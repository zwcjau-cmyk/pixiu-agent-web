"""前端 UI 控制工具 - 触发前端界面的各种干预动作"""
import json
from typing import Optional
from agno.tools import Toolkit


class UIControlTool(Toolkit):
    def __init__(self):
        super().__init__(name="ui_control")
        self.register(self.trigger_thank_you_letter)
        self.register(self.highlight_button)
        self.register(self.show_budget_chart)
        self.register(self.trigger_streak_celebration)

    def trigger_thank_you_letter(self, min_words: int = 50) -> str:
        """触发"感谢信结界"——当用户冲动提现时，强制要求写感谢信才能解锁。
        
        Args:
            min_words: 最少字数要求，默认50字
        
        Returns:
            UI 指令 JSON
        """
        command = {
            "action": "thank_you_letter",
            "params": {
                "min_words": min_words,
                "prompt": f"应急取款确认：请写一封不少于 {min_words} 字的信，感谢过去努力攒钱的自己。写完即刻放款。",
                "style": "fullscreen_typewriter"
            },
            "status": "triggered",
            "message": "感谢信结界已启动，用户需完成书写才能继续提现。"
        }
        return json.dumps(command, ensure_ascii=False)

    def highlight_button(self, button_id: str, tip: Optional[str] = None) -> str:
        """高亮指定按钮并附加提示气泡。
        
        Args:
            button_id: 需要高亮的按钮标识
            tip: 学长批注内容
        
        Returns:
            UI 指令 JSON
        """
        command = {
            "action": "highlight_button",
            "params": {
                "button_id": button_id,
                "tip": tip or "",
                "animation": "breathing_glow"
            },
            "status": "triggered"
        }
        return json.dumps(command, ensure_ascii=False)

    def show_budget_chart(self, chart_type: str = "pie", data: Optional[dict] = None) -> str:
        """在对话框中渲染动态预算图表。
        
        Args:
            chart_type: 图表类型，默认饼图 (pie/bar/line)
            data: 图表数据
        
        Returns:
            UI 指令 JSON
        """
        command = {
            "action": "render_chart",
            "params": {
                "chart_type": chart_type,
                "data": data or {},
                "interactive": True
            },
            "status": "triggered",
            "message": "预算图表已渲染。"
        }
        return json.dumps(command, ensure_ascii=False)

    def trigger_streak_celebration(self, streak_days: int, streak_type: str) -> str:
        """触发连胜庆祝动画。
        
        Args:
            streak_days: 连胜天数
            streak_type: 连胜类型（攒钱/记账/理财）
        
        Returns:
            UI 指令 JSON
        """
        command = {
            "action": "streak_celebration",
            "params": {
                "streak_days": streak_days,
                "streak_type": streak_type,
                "animation": "fireworks"
            },
            "status": "triggered"
        }
        return json.dumps(command, ensure_ascii=False)
