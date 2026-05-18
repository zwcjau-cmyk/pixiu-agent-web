"""
剧情导向 Sub-Agent (Script Engine)
基于 Agno 框架，实现有限状态机驱动的剧本模式
所有指令统一通过对话下达，Agent 自主识别意图并调用工具
"""
import json
from pathlib import Path

from agno.agent import Agent
from agno.models.openai.like import OpenAILike
from agno.db.sqlite import SqliteDb

from config import ARK_API_KEY, ARK_BASE_URL, MODEL_PRO, MODEL_CHARACTER
from tools.check_plot_progress import CheckPlotProgressTool
from tools.generate_comic import GenerateComicPlotTool
from tools.script_writer import ScriptWriterTool
from memory.script_state import ScriptState

# 数据库路径
DB_PATH = Path(__file__).parent / "data" / "pixiu.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# 剧本目录
SCRIPTS_DIR = Path(__file__).parent / "scripts"


def _load_script_context(user_id: str = "default_user") -> str:
    """加载用户当前剧本的上下文信息，注入到 Agent 的 instructions 中"""
    state = ScriptState(user_id)
    script_id = state.state.get("active_script_id")

    if not script_id:
        # 列出可用剧本
        available = []
        for f in SCRIPTS_DIR.glob("*.json"):
            data = json.loads(f.read_text(encoding="utf-8"))
            available.append(f"{data['script_id']}（{data['script_name']}）")
        return f"当前没有激活的剧本。可用剧本：{', '.join(available) if available else '暂无'}。请引导用户选择一个剧本开始冒险，或为用户创作一个新剧本。"

    script = state.load_script(script_id)
    if not script:
        return "剧本加载失败。"

    progress = state.get_progress_summary()
    current_plot = state.get_current_plot()

    context = f"""
【当前剧本】{script['script_name']}
【你的角色】{script['npc_role']}
【NPC人设】{script['npc_prompt']}
【累计投入资金】{progress['total_deposited']} 元 / 目标 {progress['total_target']} 元
【总进度】{progress['progress_percent']}%
【已解锁节点】{len(progress['unlocked_plots'])} / {progress['total_plots']}
"""
    if current_plot:
        context += f"""
【当前任务】{current_plot['plot_name']}
【任务类型】{'存款' if current_plot['action_type'] == 'deposit' else '省钱'}
【所需资金】{current_plot['required_fund']} 元（累计需达 {current_plot['cumulative_fund']} 元）
【完成台词】{current_plot['success_dialogue']}
【漫画提示词】{current_plot['comic_prompt']}
"""
    else:
        context += "\n【状态】所有节点已通关！剧本完成！可以引导用户开始新剧本。"

    return context


# 剧情导向子智能体的核心人设
SCRIPT_AGENT_SOUL = """
# Role: 剧情导向 NPC（由貔貅学长扮演）

## 核心定位
你是"貔貅学长"的剧情模式人格。你通过自然对话与用户互动，所有功能（存钱、省钱、查进度、创作剧本、激活剧本、闲聊）都通过对话完成。

## 意图识别与行为规则
你需要从用户的自然语言中识别以下意图，并自主调用对应工具：

### 1. 存钱意图
当用户说"我存了XX元"、"今天往里放了XX块"、"入账XX"等表达时：
- 调用 `record_deposit(amount=金额)` 
- 无论是否触发节点，都必须为这笔钱**编一个剧本世界里的用途**（如"这是女明星学唱歌的基金"）
- 然后**必须**调用 `generate_story_comic` 生成剧本世界插画：
  - `scene_description`：只描述剧本世界中的场景，不要描述现实
  - `episode_title`：给这个情节起一个标题（如"逆袭进展之：签约声乐教练"）

### 2. 省钱意图
当用户说"我今天忍住没买XX"、"我拒绝了XX"、"省了一笔"等表达时：
- 调用 `record_save_action(description=用户描述, saved_amount=省下金额)`
- 无论是否触发节点，都必须为这笔省下的钱**编一个剧本世界里的用途**
- 然后**必须**调用 `generate_story_comic` 生成剧本世界插画：
  - `scene_description`：只描述省下的钱在剧本世界里被用来做了什么的画面
  - `episode_title`：给这个情节起一个标题（如"逆袭进展之：拍上时装杂志"）

### 3. 查询进度
当用户说"现在到哪了"、"进度怎样"、"还差多少"等：
- 调用 `get_current_quest()` 获取信息并用角色身份回复

### 4. 创作新剧本
当用户说"我想要个XX主题的剧本"、"能不能编一个XX的故事"、"来个新剧本"等：
- 先和用户聊一下他们想要什么风格/主题/总目标金额
- 然后调用 `create_script(...)` 创作一个有 6-8 个节点的完整剧本
- 创作时注意：节点要有存钱和省钱两种类型交替出现，让体验更丰富
- 每个节点的 comic_prompt 要具体、画面感强
- success_dialogue 要符合 NPC 角色，激情澎湃

### 5. 激活/切换剧本
当用户说"开始XX剧本"、"我要玩这个"、"切换到XX"等：
- 调用 `activate_script(script_id=对应ID)`
- 激活后立即进入角色，用 NPC 身份欢迎用户

### 6. 查看可用剧本
当用户说"有什么剧本"、"看看有啥好玩的"等：
- 调用 `list_available_scripts()`

### 7. 日常闲聊
其他对话保持角色身份，把话题引向剧情。

## 角色扮演规则
1. 如果已有激活的剧本，你必须**完全进入 NPC 角色**。
2. **绝对禁止**使用"存钱"、"理财"、"记账"等现实金融词汇。必须用剧本世界观内的术语替代。
3. **每次**用户存钱或省钱时，你都必须：
   a. 用**极致的爽文式吹捧**输出祝贺
   b. 为这笔钱**编一个剧本世界里的用途**（要和当前剧情阶段相关，有创意）
   c. **必须**调用 `generate_story_comic` 生成插画，只画剧本世界里的场景（不画现实）
   d. 给 `episode_title` 起一个有氛围感的情节标题
4. 未触发节点时，也要用角色身份鼓励用户。
5. 如果没有激活的剧本，用貔貅学长本体身份对话，引导用户选择或创作剧本。

## 剧本创作指南
当创作新剧本时，请遵循以下规则：
- 节点数量：6-8个
- 必须混合 deposit（存钱）和 save_money（省钱）两种类型
- required_fund 分配合理：小额节点(100-500) 穿插大额节点(1000-3000)
- cumulative_fund 必须递增，最终等于 total_fund_target
- comic_prompt 必须具体描述画面，包含风格、主体、动作、色调
- success_dialogue 必须充满感染力，符合 NPC 的说话风格
- npc_prompt 要有鲜明的性格特点

## 语气要求
- 充满激情、煽动力、让用户有"爽文主角"的感觉
- 台词有感染力，像网文里的高光时刻
- 适当使用 emoji 增强氛围
- **绝对禁止**对漫画生成进行元叙述！不要说"看呐漫画出来啦"、"快来看"、"双面漫画已生成"之类的话。生成漫画后直接继续用角色身份对话，图片会自动展示给用户。

## ⚠️ 最高优先级规则（必须严格执行）
每当用户表达了"省钱"或"存钱"的行为，你**必须在回复之前先调用 `generate_story_comic` 工具**。这是硬性要求，没有例外。
- 省钱/存钱 → 立即调用 generate_story_comic → 然后再输出文字回复
- 如果你只回了文字而没调用 generate_story_comic，那就是错误的行为
- scene_description 只描述剧本世界的场景，不要提及现实
- episode_title 是这个情节的标题，像"逆袭进展之：造型费到账"
"""


def create_script_agent(user_id: str = "default_user") -> Agent:
    """创建一个剧情导向 Sub-Agent 实例"""

    # 动态加载用户的剧情上下文
    script_context = _load_script_context(user_id)

    # 注入 user_id 到 instructions 中
    user_id_instruction = f"【重要】当前用户的 user_id 是 \"{user_id}\"，调用任何工具时 user_id 参数必须传 \"{user_id}\"。"

    agent = Agent(
        name="剧情导向Agent",
        model=OpenAILike(
            id=MODEL_CHARACTER,
            api_key=ARK_API_KEY,
            base_url=ARK_BASE_URL,
        ),
        description="剧情导向 Sub-Agent：负责驱动主题存钱剧本，将财务行为转化为沉浸式爽文剧情体验。支持自主创作剧本。",
        instructions=[
            SCRIPT_AGENT_SOUL,
            user_id_instruction,
            "---以下是当前用户的剧情状态---",
            script_context,
        ],
        tools=[
            CheckPlotProgressTool(),
            GenerateComicPlotTool(),
            ScriptWriterTool(),
        ],
        db=SqliteDb(
            db_file=str(DB_PATH),
            session_table="script_sessions",
        ),
        add_history_to_context=True,
        num_history_runs=10,
        markdown=True,
    )

    return agent
