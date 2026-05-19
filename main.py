"""
貔貅学长 - Web API 版本
基于 Agno 框架 + FastAPI 提供 HTTP 接口
"""
import json
import os
import uuid
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from agno.agent import Agent
from agno.models.openai.like import OpenAILike
from agno.db.sqlite import SqliteDb

from config import ARK_API_KEY, ARK_BASE_URL, MODEL_CHARACTER
from tools.diary_ledger import DiaryToLedgerTool
from tools.vault_manager import VaultManagerTool
from tools.ui_control import UIControlTool
from tools.image_generator import ImageGeneratorTool
from tools.speech_recognizer import SpeechRecognizerTool
from tools.sticker_maker import StickerMakerTool
from script_agent import create_script_agent

# 读取人设文件
SOUL_PATH = Path(__file__).parent / "soul.md"
soul_prompt = SOUL_PATH.read_text(encoding="utf-8")

# 注入当前日期的模板（每次请求时动态替换）
from datetime import datetime as _dt, timezone as _tz, timedelta as _td
_CN_TZ = _tz(_td(hours=8))  # 东八区
_date_template = "\n\n---\n## 系统信息\n- 今天的日期是：{today}\n- 当用户提到\"今天\"的收支时，日期参数必须使用 {today}\n- 当用户没有明确说日期时，默认使用今天的日期 {today}\n"
# 启动时先注入一次
_today = _dt.now(_CN_TZ).strftime("%Y-%m-%d")
soul_prompt += _date_template.format(today=_today)

# 数据库路径
DB_PATH = Path(__file__).parent / "data" / "pixiu.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# 初始化工具实例（需要在请求时动态设置 user_id）
_diary_tool = DiaryToLedgerTool()
_vault_tool = VaultManagerTool()

# 初始化 SOLO Agent
pixiu_agent = Agent(
    name="貔貅学长",
    model=OpenAILike(
        id=MODEL_CHARACTER,
        api_key=ARK_API_KEY,
        base_url=ARK_BASE_URL,
    ),
    description="貔貅学长 - 你的赛博理财引路人",
    instructions=[soul_prompt],
    tools=[
        _diary_tool,
        _vault_tool,
        UIControlTool(),
        ImageGeneratorTool(),
        SpeechRecognizerTool(),
        StickerMakerTool(),
    ],
    db=SqliteDb(
        db_file=str(DB_PATH),
        session_table="pixiu_sessions",
    ),
    add_history_to_context=True,
    num_history_runs=10,
    markdown=True,
)

# FastAPI 应用
app = FastAPI(title="貔貅学长 API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载贴纸静态文件目录
STICKER_DIR = Path(__file__).parent / "stickers"
STICKER_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/api/stickers", StaticFiles(directory=str(STICKER_DIR)), name="stickers")


class ChatRequest(BaseModel):
    message: str
    user_id: str = "default_user"
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))


class ChatResponse(BaseModel):
    reply: str
    session_id: str


@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    """与貔貅学长对话 - SSE 流式输出"""
    # 每次请求动态更新日期，确保跨天后日期正确（东八区）
    today_str = _dt.now(_CN_TZ).strftime("%Y-%m-%d")
    base_prompt = SOUL_PATH.read_text(encoding="utf-8")
    pixiu_agent.instructions = [base_prompt + _date_template.format(today=today_str)]

    # 自动注入 user_id 到工具实例，不依赖 LLM 传参
    _diary_tool._current_user_id = req.user_id
    _vault_tool._current_user_id = req.user_id

    def event_stream():
        response_stream = pixiu_agent.run(
            req.message,
            user_id=req.user_id,
            session_id=req.session_id,
            stream=True,
        )
        for chunk in response_stream:
            if hasattr(chunk, 'content') and chunk.content:
                yield f"data: {json.dumps({'token': chunk.content}, ensure_ascii=False)}\n\n"
        # 结束标记
        yield f"data: {json.dumps({'done': True, 'session_id': req.session_id})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/api/health")
async def health():
    return {"status": "ok", "agent": "貔貅学长"}


# ============ 贴纸制作 Agent API ============

sticker_tool = StickerMakerTool()


class StickerRequest(BaseModel):
    image_base64: str  # 商品图片的 base64 编码
    product_name: Optional[str] = None  # 可选，用户手动输入的名称
    product_price: Optional[float] = None  # 可选，用户手动输入的价格
    user_id: str = "default_user"  # 用户标识，用于数据隔离


class StickerResponse(BaseModel):
    success: bool
    product_name: str = ""
    product_price: float = 0
    product_category: str = ""
    sticker_url: str = ""
    total_saved: float = 0
    total_items: int = 0
    message: str = ""


@app.post("/api/sticker/create", response_model=StickerResponse)
async def create_sticker(req: StickerRequest):
    """一键流程：识别商品 → 抠图制作贴纸 → 添加到藏宝阁"""
    import json as _json

    # 步骤1：识别商品（如果用户没手动输入名称和价格）
    product_name = req.product_name
    product_price = req.product_price
    product_category = "其他"

    if not product_name or not product_price:
        recognize_result = _json.loads(sticker_tool.recognize_product(req.image_base64))
        if recognize_result["success"]:
            product = recognize_result["product"]
            product_name = product_name or product.get("name", "未知商品")
            product_price = product_price or product.get("price", 0)
            product_category = product.get("category", "其他")
        else:
            return StickerResponse(
                success=False,
                message=recognize_result["message"],
            )

    # 步骤2：抠图制作贴纸
    sticker_result = _json.loads(
        sticker_tool.create_sticker_from_image(req.image_base64, product_name)
    )
    if not sticker_result["success"]:
        return StickerResponse(
            success=False,
            product_name=product_name,
            product_price=product_price,
            message=sticker_result["message"],
        )

    sticker_url = sticker_result["sticker_url"]

    # 步骤3：添加到藏宝阁
    shelf_result = _json.loads(
        sticker_tool.add_to_treasure_shelf(
            name=product_name,
            price=product_price,
            sticker_url=sticker_url,
            category=product_category,
            user_id=req.user_id,
        )
    )

    return StickerResponse(
        success=shelf_result["success"],
        product_name=product_name,
        product_price=product_price,
        product_category=product_category,
        sticker_url=sticker_url,
        total_saved=shelf_result.get("total_saved", 0),
        total_items=shelf_result.get("total_items", 0),
        message=shelf_result["message"],
    )


@app.get("/api/sticker/shelf")
async def get_shelf(user_id: str = "default_user"):
    """获取藏宝阁储物架数据"""
    import json as _json
    return _json.loads(sticker_tool.get_treasure_shelf(user_id=user_id))


# ============ 收支记录 API ============

DATA_DIR = Path(__file__).parent / "data"
VAULT_FILE = DATA_DIR / "vault.json"

from data.mock_data import DEFAULT_EXPENSES as _DEFAULT_EXPENSES
from data.mock_data import DEFAULT_VAULT as _DEFAULT_VAULT
from tools.vault_manager import _get_user_vault_file, _load_vault as _load_user_vault, DEFAULT_VAULT as _VAULT_DEFAULT


def _get_user_expenses_file(user_id: str) -> Path:
    """按 user_id 返回隔离的收支文件路径"""
    safe_id = user_id.replace("/", "_").replace("..", "_")
    return DATA_DIR / f"expenses_{safe_id}.json"


def _load_json(filepath: Path) -> dict:
    if filepath.exists():
        content = filepath.read_text(encoding="utf-8").strip()
        if content:
            data = json.loads(content)
            if data:
                return data
    return {}


def _save_json(filepath: Path, data: dict):
    filepath.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


class ExpenseRecord(BaseModel):
    category: str  # 类别：餐饮/购物/交通等
    amount: float  # 金额
    description: str = ""  # 描述
    type: str = "expense"  # expense 或 income
    date: Optional[str] = None  # 日期，默认今天
    user_id: str = "default_user"  # 用户标识


class VaultUpdate(BaseModel):
    account: Optional[str] = None  # active_pool/fixed_deposit/fund_collection
    amount: Optional[float] = None  # 存入金额
    goal_name: Optional[str] = None  # 目标名称
    goal_amount: Optional[float] = None  # 目标新存入金额
    user_id: str = "default_user"  # 用户标识


@app.post("/api/expense/record")
async def record_expense(req: ExpenseRecord):
    """记录一笔收支（按 user_id 隔离存储）"""
    import json as _json
    from datetime import datetime

    expenses_file = _get_user_expenses_file(req.user_id)
    data = _load_json(expenses_file)
    if "records" not in data:
        data["records"] = []
    if "monthly_summary" not in data:
        data["monthly_summary"] = {"total_expense": 0, "total_income": 0}

    record = {
        "category": req.category,
        "amount": req.amount,
        "description": req.description,
        "type": req.type,
        "date": req.date or datetime.now().strftime("%Y-%m-%d"),
        "created_at": datetime.now().isoformat(),
    }
    data["records"].insert(0, record)

    # 更新月度汇总
    if req.type == "expense":
        data["monthly_summary"]["total_expense"] = data["monthly_summary"].get("total_expense", 0) + req.amount
    else:
        data["monthly_summary"]["total_income"] = data["monthly_summary"].get("total_income", 0) + req.amount

    _save_json(expenses_file, data)

    return {
        "success": True,
        "record": record,
        "monthly_summary": data["monthly_summary"],
        "message": f"已记录{'支出' if req.type == 'expense' else '收入'} ¥{req.amount}（{req.category}）"
    }


@app.get("/api/expense/summary")
async def get_expense_summary(user_id: Optional[str] = None):
    """获取收支汇总 —— 只返回 Mock 数据（用户数据隔离，不混入公共展示）"""
    mock_records = _DEFAULT_EXPENSES.get("records", [])

    # 如果有 user_id，合并该用户的私有数据
    user_records = []
    if user_id:
        user_file = _get_user_expenses_file(user_id)
        user_data = _load_json(user_file)
        user_records = user_data.get("records", []) if user_data else []

    all_records = user_records + mock_records

    total_expense = sum(r["amount"] for r in all_records if r.get("type") == "expense")
    total_income = sum(r["amount"] for r in all_records if r.get("type") == "income")
    return {
        "records": all_records,
        "monthly_summary": {"total_expense": total_expense, "total_income": total_income},
    }


@app.get("/api/expense/day/{date}")
async def get_expense_by_day(date: str, user_id: Optional[str] = None):
    """获取某一天的收支明细，date格式：2026-05-16"""
    mock_records = _DEFAULT_EXPENSES.get("records", [])

    user_records = []
    if user_id:
        user_file = _get_user_expenses_file(user_id)
        user_data = _load_json(user_file)
        user_records = user_data.get("records", []) if user_data else []

    all_records = user_records + mock_records

    # 筛选当天记录
    day_records = [r for r in all_records if r.get("date") == date]

    # 计算当天汇总
    day_income = sum(r["amount"] for r in day_records if r["type"] == "income")
    day_expense = sum(r["amount"] for r in day_records if r["type"] == "expense")
    day_balance = day_income - day_expense

    # 计算截至当天的累计结余（从月初开始）
    month_prefix = date[:7]  # "2026-05"
    month_records = [r for r in all_records if r.get("date", "").startswith(month_prefix) and r.get("date", "") <= date]
    cumulative_income = sum(r["amount"] for r in month_records if r["type"] == "income")
    cumulative_expense = sum(r["amount"] for r in month_records if r["type"] == "expense")
    cumulative_balance = cumulative_income - cumulative_expense

    return {
        "date": date,
        "records": day_records,
        "day_income": day_income,
        "day_expense": day_expense,
        "day_balance": day_balance,
        "cumulative_income": cumulative_income,
        "cumulative_expense": cumulative_expense,
        "cumulative_balance": cumulative_balance,
    }


@app.post("/api/vault/update")
async def update_vault(req: VaultUpdate):
    """更新金库资产或梦想清单进度（按 user_id 隔离）"""
    data = _load_user_vault(req.user_id)

    message_parts = []

    # 更新账户余额
    if req.account and req.amount is not None:
        if req.account in data.get("accounts", {}):
            old_balance = data["accounts"][req.account]["balance"]
            data["accounts"][req.account]["balance"] = old_balance + req.amount
            # 重新计算总资产
            data["total_assets"] = sum(
                acc["balance"] for acc in data["accounts"].values()
            )
            data["monthly_growth"] = data.get("monthly_growth", 0) + req.amount
            message_parts.append(
                f"{data['accounts'][req.account]['label']}已存入 ¥{req.amount}，"
                f"当前余额 ¥{data['accounts'][req.account]['balance']:.2f}"
            )

    # 更新梦想清单
    if req.goal_name and req.goal_amount is not None:
        goals = data.get("goals", [])
        found = False
        for goal in goals:
            if goal["name"] == req.goal_name:
                goal["current"] = goal["current"] + req.goal_amount
                if goal["current"] > goal["target"]:
                    goal["current"] = goal["target"]
                progress = int(goal["current"] / goal["target"] * 100)
                message_parts.append(
                    f"「{goal['name']}」进度更新：¥{goal['current']}/{goal['target']} ({progress}%)"
                )
                found = True
                break
        if not found:
            # 新建目标
            goals.append({
                "name": req.goal_name,
                "target": req.goal_amount,
                "current": 0,
                "emoji": "🎯"
            })
            message_parts.append(f"新目标「{req.goal_name}」已创建，目标金额 ¥{req.goal_amount}")
        data["goals"] = goals

    from tools.vault_manager import _save_vault as _save_user_vault
    _save_user_vault(data, req.user_id)

    return {
        "success": True,
        "total_assets": data["total_assets"],
        "accounts": data["accounts"],
        "goals": data["goals"],
        "message": "；".join(message_parts) if message_parts else "金库数据已更新"
    }


@app.get("/api/vault/status")
async def get_vault_status(user_id: Optional[str] = None):
    """获取金库完整状态（按 user_id 隔离）"""
    if user_id:
        data = _load_user_vault(user_id)
    else:
        data = _load_json(VAULT_FILE)
        if not data:
            data = _DEFAULT_VAULT
    return data


@app.get("/api/vault/account/{account_id}")
async def get_account_detail(account_id: str, user_id: Optional[str] = None):
    """获取某个账户的详细信息（按 user_id 隔离）"""
    if user_id:
        data = _load_user_vault(user_id)
    else:
        data = _load_json(VAULT_FILE)
        if not data:
            data = _DEFAULT_VAULT
    accounts = data.get("accounts", {})
    if account_id not in accounts:
        return {"success": False, "message": f"账户 {account_id} 不存在"}

    account = accounts[account_id]
    return {
        "success": True,
        "account_id": account_id,
        "label": account.get("label", ""),
        "balance": account.get("balance", 0),
        "rate": account.get("rate", ""),
        "term": account.get("term", ""),
        "principal": account.get("principal", 0),
        "monthly_profit": account.get("monthly_profit", 0),
        "products": account.get("products", []),
        "transactions": account.get("transactions", []),
    }


class WithdrawRequest(BaseModel):
    account_id: str
    amount: float
    reason: str = ""
    user_id: str = "default_user"


@app.post("/api/vault/withdraw")
async def request_withdraw(req: WithdrawRequest):
    """提交转出申请（需要貔貅学长审批）"""
    data = _load_user_vault(req.user_id)
    accounts = data.get("accounts", {})
    if req.account_id not in accounts:
        return {"success": False, "message": "账户不存在"}

    account = accounts[req.account_id]
    if req.amount > account.get("balance", 0):
        return {"success": False, "message": f"余额不足，当前余额 ¥{account['balance']:.2f}"}

    # 生成转出申请消息，返回给前端跳转到貔貅空间发送
    apply_message = f"学长，我想从{account['label']}转出¥{req.amount}{'，' + req.reason if req.reason else ''}。可以吗？"

    return {
        "success": True,
        "apply_message": apply_message,
        "account_label": account["label"],
        "amount": req.amount,
    }


# ============ 剧情导向 Agent API ============

class ScriptChatRequest(BaseModel):
    message: str
    user_id: str = "default_user"
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))


class ScriptChatResponse(BaseModel):
    reply: str
    session_id: str
    image_url: Optional[str] = None


@app.post("/api/script/chat")
async def script_chat_endpoint(req: ScriptChatRequest):
    """统一对话入口 - SSE 流式输出"""
    import re
    agent = create_script_agent(req.user_id)

    def event_stream():
        # 流式获取 Agent 回复
        full_text = ""
        tool_outputs = []
        response_stream = agent.run(
            req.message,
            user_id=req.user_id,
            session_id=req.session_id,
            stream=True,
        )
        for chunk in response_stream:
            if hasattr(chunk, 'content') and chunk.content:
                full_text += chunk.content
                yield f"data: {json.dumps({'token': chunk.content}, ensure_ascii=False)}\n\n"
            # 捕获工具调用结果
            if hasattr(chunk, 'tool_call_content') and chunk.tool_call_content:
                tool_outputs.append(str(chunk.tool_call_content))
            if hasattr(chunk, 'messages') and chunk.messages:
                for msg in chunk.messages:
                    if hasattr(msg, 'content') and msg.content:
                        tool_outputs.append(str(msg.content))

        # 流结束后，尝试从完整回复和工具输出中提取图片 URL
        image_url = None

        # 先从工具输出中找
        for output in tool_outputs:
            if 'image_url' in output:
                url_match = re.search(r'"image_url"\s*:\s*"(https?://[^"]+)"', output)
                if url_match:
                    image_url = url_match.group(1)
                    break

        # 从 response_stream 的 response 属性找
        if not image_url:
            if hasattr(response_stream, 'response') and response_stream.response:
                resp = response_stream.response
                if hasattr(resp, 'messages') and resp.messages:
                    for msg in resp.messages:
                        if hasattr(msg, 'content') and msg.content and 'image_url' in str(msg.content):
                            url_match = re.search(r'"image_url"\s*:\s*"(https?://[^"]+)"', str(msg.content))
                            if url_match:
                                image_url = url_match.group(1)
                                break

        # 从完整文本中找
        if not image_url:
            url_match = re.search(r'"image_url"\s*:\s*"(https?://[^"]+)"', full_text)
            if url_match:
                image_url = url_match.group(1)

        if not image_url:
            url_match = re.search(r'(https?://[^\s"\'<>]+\.(?:png|jpg|jpeg|webp)[^\s"\'<>]*)', full_text)
            if url_match:
                image_url = url_match.group(1)

        # 后端强制补图逻辑：只要有正常对话内容就生成漫画
        if not image_url and full_text and len(full_text.strip()) > 20:
            # 通知前端正在生成图片
            yield f"data: {json.dumps({'generating_image': True}, ensure_ascii=False)}\n\n"
            from tools.generate_comic import GenerateComicPlotTool
            from memory.script_state import ScriptState

            state = ScriptState(req.user_id)
            script_id = state.state.get("active_script_id")

            if script_id:
                scene_hint = full_text[:200]
                from openai import OpenAI
                from config import MODEL_PRO
                client = OpenAI(api_key=ARK_API_KEY, base_url=ARK_BASE_URL)

                try:
                    extract_resp = client.chat.completions.create(
                        model=MODEL_PRO,
                        messages=[{
                            "role": "user",
                            "content": f"根据下面这段角色对话，提取出剧本世界里发生的场景，用于生成一张插画。\n\n对话内容：{scene_hint}\n\n请直接输出JSON，格式：{{\"scene_description\": \"具体的画面描述，包含人物、动作、环境、色调\", \"episode_title\": \"情节标题，如逆袭进展之：XXX\"}}"
                        }],
                        temperature=0.7,
                    )
                    extract_text = extract_resp.choices[0].message.content or ""
                    json_match = re.search(r'\{[^}]+\}', extract_text)
                    if json_match:
                        scene_data = json.loads(json_match.group())
                        scene_desc = scene_data.get("scene_description", "")
                        ep_title = scene_data.get("episode_title", "剧情进展")
                        if scene_desc:
                            comic_tool = GenerateComicPlotTool()
                            result_json = comic_tool.generate_story_comic(scene_desc, ep_title)
                            result_data = json.loads(result_json)
                            if result_data.get("success"):
                                image_url = result_data["image_url"]
                except Exception:
                    pass

        # 发送结束事件（包含 image_url）
        yield f"data: {json.dumps({'done': True, 'session_id': req.session_id, 'image_url': image_url}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/api/script/progress/{user_id}")
async def script_progress_endpoint(user_id: str = "default_user"):
    """获取用户的剧情进度（供前端 UI 展示用）"""
    from memory.script_state import ScriptState
    state = ScriptState(user_id)
    return state.get_progress_summary()


@app.get("/api/script/available")
async def available_scripts():
    """获取可用剧本列表（供前端 UI 展示用）"""
    import json
    scripts_dir = Path(__file__).parent / "scripts"
    scripts = []
    for f in scripts_dir.glob("*.json"):
        data = json.loads(f.read_text(encoding="utf-8"))
        scripts.append({
            "script_id": data["script_id"],
            "script_name": data["script_name"],
            "theme": data["theme"],
            "total_fund_target": data["total_fund_target"],
            "total_plots": len(data["plots"]),
        })
    return {"scripts": scripts}


# CLI 仍然保留
def main():
    """交互式命令行对话"""
    print("=" * 50)
    print("  🐉 貔貅学长 - 你的赛博理财引路人")
    print("  输入 'quit' 退出对话")
    print("=" * 50)
    print()

    session_id = str(uuid.uuid4())
    while True:
        user_input = input("你: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            print("\n貔貅学长: 下次见啦，记得记账哦~ (｡•̀ᴗ-)✧")
            break

        response = pixiu_agent.run(user_input, user_id="cli_user", session_id=session_id)
        print(f"\n貔貅学长: {response.content}\n")


if __name__ == "__main__":
    import sys
    if "--serve" in sys.argv:
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)
    else:
        main()
