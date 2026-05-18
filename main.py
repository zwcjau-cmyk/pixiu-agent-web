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
from datetime import datetime as _dt
_date_template = "\n\n---\n## 系统信息\n- 今天的日期是：{today}\n- 当用户提到\"今天\"的收支时，日期参数必须使用 {today}\n- 当用户没有明确说日期时，默认使用今天的日期 {today}\n"
# 启动时先注入一次
_today = _dt.now().strftime("%Y-%m-%d")
soul_prompt += _date_template.format(today=_today)

# 数据库路径
DB_PATH = Path(__file__).parent / "data" / "pixiu.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

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
        DiaryToLedgerTool(),
        VaultManagerTool(),
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


@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    """与貔貅学长对话"""
    # 每次请求动态更新日期，确保跨天后日期正确
    today_str = _dt.now().strftime("%Y-%m-%d")
    base_prompt = SOUL_PATH.read_text(encoding="utf-8")
    pixiu_agent.instructions = [base_prompt + _date_template.format(today=today_str)]

    response = pixiu_agent.run(
        req.message,
        user_id=req.user_id,
        session_id=req.session_id,
    )
    return ChatResponse(
        reply=response.content,
        session_id=req.session_id,
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

EXPENSES_FILE = Path(__file__).parent / "data" / "expenses.json"
VAULT_FILE = Path(__file__).parent / "data" / "vault.json"

from data.mock_data import DEFAULT_EXPENSES as _DEFAULT_EXPENSES
from data.mock_data import DEFAULT_VAULT as _DEFAULT_VAULT


def _load_json(filepath: Path) -> dict:
    if filepath.exists():
        content = filepath.read_text(encoding="utf-8").strip()
        if content:
            data = json.loads(content)
            # 如果文件存在但内容是空壳（无实际记录），返回空让 fallback 生效
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


class VaultUpdate(BaseModel):
    account: Optional[str] = None  # active_pool/fixed_deposit/fund_collection
    amount: Optional[float] = None  # 存入金额
    goal_name: Optional[str] = None  # 目标名称
    goal_amount: Optional[float] = None  # 目标新存入金额


@app.post("/api/expense/record")
async def record_expense(req: ExpenseRecord):
    """记录一笔收支"""
    import json as _json
    from datetime import datetime

    data = _load_json(EXPENSES_FILE)
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

    _save_json(EXPENSES_FILE, data)

    return {
        "success": True,
        "record": record,
        "monthly_summary": data["monthly_summary"],
        "message": f"已记录{'支出' if req.type == 'expense' else '收入'} ¥{req.amount}（{req.category}）"
    }


@app.get("/api/expense/summary")
async def get_expense_summary():
    """获取收支汇总（返回全部记录供日历使用）"""
    data = _load_json(EXPENSES_FILE)
    if not data or not data.get("records"):
        data = _DEFAULT_EXPENSES
    return {
        "records": data.get("records", []),
        "monthly_summary": data.get("monthly_summary", {"total_expense": 0, "total_income": 0}),
    }


@app.get("/api/expense/day/{date}")
async def get_expense_by_day(date: str):
    """获取某一天的收支明细，date格式：2026-05-16"""
    data = _load_json(EXPENSES_FILE)
    if not data or not data.get("records"):
        data = _DEFAULT_EXPENSES
    all_records = data.get("records", [])

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
    """更新金库资产或梦想清单进度"""
    data = _load_json(VAULT_FILE)
    if not data:
        import copy
        data = copy.deepcopy(_DEFAULT_VAULT)

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

    _save_json(VAULT_FILE, data)

    return {
        "success": True,
        "total_assets": data["total_assets"],
        "accounts": data["accounts"],
        "goals": data["goals"],
        "message": "；".join(message_parts) if message_parts else "金库数据已更新"
    }


@app.get("/api/vault/status")
async def get_vault_status():
    """获取金库完整状态"""
    data = _load_json(VAULT_FILE)
    if not data:
        data = _DEFAULT_VAULT
    return data


@app.get("/api/vault/account/{account_id}")
async def get_account_detail(account_id: str):
    """获取某个账户的详细信息（产品明细、交易记录等）"""
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


@app.post("/api/vault/withdraw")
async def request_withdraw(req: WithdrawRequest):
    """提交转出申请（需要貔貅学长审批）"""
    data = _load_json(VAULT_FILE)
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


@app.post("/api/script/chat", response_model=ScriptChatResponse)
async def script_chat_endpoint(req: ScriptChatRequest):
    """统一对话入口：所有指令（存钱/省钱/激活/创作/查进度/闲聊）都通过自然对话下达"""
    import re
    agent = create_script_agent(req.user_id)
    response = agent.run(
        req.message,
        user_id=req.user_id,
        session_id=req.session_id,
    )

    image_url = None
    reply_text = response.content or ""

    # 1. 先从 Agent 的回复/工具返回中提取图片 URL（如果 Agent 成功调了工具）
    if hasattr(response, 'messages') and response.messages:
        for msg in response.messages:
            if hasattr(msg, 'content') and msg.content and 'image_url' in str(msg.content):
                url_match = re.search(r'"image_url"\s*:\s*"(https?://[^"]+)"', str(msg.content))
                if url_match:
                    image_url = url_match.group(1)
                    break

    if not image_url:
        url_match = re.search(r'"image_url"\s*:\s*"(https?://[^"]+)"', reply_text)
        if url_match:
            image_url = url_match.group(1)

    if not image_url:
        url_match = re.search(r'(https?://[^\s"\'<>]+\.(?:png|jpg|jpeg|webp)[^\s"\'<>]*)', reply_text)
        if url_match:
            image_url = url_match.group(1)

    # 2. 如果 Agent 没调工具生成图片，但用户消息包含省钱/存钱意图，后端强制生成
    if not image_url:
        save_keywords = ['忍住', '没买', '省了', '省下', '拒绝', '存了', '入账', '往里放', '攒了']
        user_msg_lower = req.message
        is_save_or_deposit = any(kw in user_msg_lower for kw in save_keywords)

        if is_save_or_deposit and reply_text:
            # 从 Agent 回复中提取剧本世界的场景描述（取第一句有实际内容的话作为 scene）
            from tools.generate_comic import GenerateComicPlotTool
            from memory.script_state import ScriptState

            state = ScriptState(req.user_id)
            script_id = state.state.get("active_script_id")

            if script_id:
                # 从回复中提取 Agent 编造的剧本世界用途
                # Agent 回复通常包含"这笔钱用来..."的描述
                scene_hint = reply_text[:200]  # 取前200字作为场景线索

                # 用一个简单的 prompt 让 pro 模型生成 scene_description 和 episode_title
                from openai import OpenAI
                from config import MODEL_PRO
                client = OpenAI(api_key=ARK_API_KEY, base_url=ARK_BASE_URL)

                extract_resp = client.chat.completions.create(
                    model=MODEL_PRO,
                    messages=[{
                        "role": "user",
                        "content": f"根据下面这段角色对话，提取出剧本世界里发生的场景，用于生成一张插画。\n\n对话内容：{scene_hint}\n\n请直接输出JSON，格式：{{\"scene_description\": \"具体的画面描述，包含人物、动作、环境、色调\", \"episode_title\": \"情节标题，如逆袭进展之：XXX\"}}"
                    }],
                    temperature=0.7,
                )
                extract_text = extract_resp.choices[0].message.content or ""

                try:
                    # 提取 JSON
                    json_match = re.search(r'\{[^}]+\}', extract_text)
                    if json_match:
                        import json as json_mod
                        scene_data = json_mod.loads(json_match.group())
                        scene_desc = scene_data.get("scene_description", "")
                        ep_title = scene_data.get("episode_title", "剧情进展")

                        if scene_desc:
                            comic_tool = GenerateComicPlotTool()
                            result_json = comic_tool.generate_story_comic(scene_desc, ep_title)
                            result_data = json_mod.loads(result_json)
                            if result_data.get("success"):
                                image_url = result_data["image_url"]
                except Exception:
                    pass  # 图片生成失败不影响主流程

    # 清理回复文本
    if image_url:
        cleanup_patterns = [
            r'看[呐啊].*?漫画.*?[！!🤩😍✨]+',
            r'快来看.*?[！!]',
            r'双面漫画已生成.*?[！!]',
            r'剧情海报.*?已生成.*?[！!]',
            r'漫画.*?[来啦了].*?[！!🤩😍✨]+',
        ]
        for pattern in cleanup_patterns:
            reply_text = re.sub(pattern, '', reply_text)
        reply_text = re.sub(r'\{[^}]*"image_url"[^}]*\}', '', reply_text)
        reply_text = re.sub(r'"image_url"\s*:\s*"https?://[^"]*"', '', reply_text)
        reply_text = reply_text.strip()

    return ScriptChatResponse(
        reply=reply_text,
        session_id=req.session_id,
        image_url=image_url,
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
