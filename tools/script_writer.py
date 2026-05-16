"""剧本创作工具 - 让 Agent 能够自主创作新剧本并持久化"""
import json
import re
from pathlib import Path
from agno.tools import Toolkit

SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)


class ScriptWriterTool(Toolkit):
    def __init__(self):
        super().__init__(name="script_writer")
        self.register(self.create_script)
        self.register(self.list_available_scripts)

    def create_script(
        self,
        script_name: str,
        theme: str,
        npc_role: str,
        npc_prompt: str,
        total_fund_target: float,
        plots_json: str,
    ) -> str:
        """创作一个全新的剧本并保存。当用户提出想要一个新的主题/故事时调用此工具。

        Args:
            script_name: 剧本名称（如"修仙问道：灵石传说"）
            theme: 主题标签（如"修仙逆袭"、"娱乐圈"、"商战"）
            npc_role: NPC 角色名称（如"宗门长老"、"金牌经纪人"）
            npc_prompt: NPC 的人设提示词，描述说话风格和行为逻辑
            total_fund_target: 剧本的总资金目标（元）
            plots_json: 剧情节点数组的 JSON 字符串。每个节点包含：
                - plot_id: 节点序号（从1开始）
                - plot_name: 节点名称
                - required_fund: 该节点所需资金（省钱类为0）
                - cumulative_fund: 到达该节点时的累计资金要求
                - action_type: "deposit"（存钱）或 "save_money"（省钱）
                - success_dialogue: 通关时 NPC 说的台词
                - comic_prompt: 通关漫画的生图提示词

        Returns:
            创作结果
        """
        # 生成 script_id
        script_id = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff]', '_', theme.lower())[:20].strip('_')
        if not script_id:
            script_id = "custom_script"
        # 确保不重复
        counter = 1
        base_id = script_id
        while (SCRIPTS_DIR / f"{script_id}.json").exists():
            counter += 1
            script_id = f"{base_id}_{counter:02d}"

        # 解析 plots
        try:
            plots = json.loads(plots_json)
        except json.JSONDecodeError as e:
            return json.dumps({
                "success": False,
                "message": f"plots_json 格式错误：{str(e)}，请确保是合法的 JSON 数组。"
            }, ensure_ascii=False)

        # 构建完整剧本
        script_data = {
            "script_id": script_id,
            "script_name": script_name,
            "theme": theme,
            "npc_role": npc_role,
            "npc_prompt": npc_prompt,
            "total_fund_target": total_fund_target,
            "plots": plots,
        }

        # 保存
        script_file = SCRIPTS_DIR / f"{script_id}.json"
        script_file.write_text(
            json.dumps(script_data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

        return json.dumps({
            "success": True,
            "script_id": script_id,
            "script_name": script_name,
            "total_plots": len(plots),
            "total_fund_target": total_fund_target,
            "message": f"剧本「{script_name}」创作完成！共 {len(plots)} 个剧情节点，总目标 {total_fund_target} 元。剧本 ID：{script_id}，用户可以说「开始这个剧本」来激活。"
        }, ensure_ascii=False)

    def list_available_scripts(self) -> str:
        """列出所有可用的剧本。

        Returns:
            可用剧本列表
        """
        scripts = []
        for f in SCRIPTS_DIR.glob("*.json"):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                scripts.append({
                    "script_id": data["script_id"],
                    "script_name": data["script_name"],
                    "theme": data["theme"],
                    "total_fund_target": data["total_fund_target"],
                    "total_plots": len(data["plots"]),
                })
            except (json.JSONDecodeError, KeyError):
                continue

        return json.dumps({
            "scripts": scripts,
            "message": f"当前共有 {len(scripts)} 个可用剧本。" + (
                "用户可以选择一个激活，或者让你创作新剧本。" if scripts else "暂无剧本，可以为用户创作一个！"
            )
        }, ensure_ascii=False)
