"""用户状态管理 - 存储用户财务状态、目标进度等长期记忆"""
import json
from pathlib import Path
from datetime import datetime
from typing import Optional


DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


class UserState:
    """用户状态管理器，负责持久化用户的财务信息和目标进度"""

    def __init__(self, user_id: str = "default_user"):
        self.user_id = user_id
        self.state_file = DATA_DIR / f"{user_id}_state.json"
        self.state = self._load_state()

    def _load_state(self) -> dict:
        """加载用户状态"""
        if self.state_file.exists():
            return json.loads(self.state_file.read_text(encoding="utf-8"))
        return self._default_state()

    def _default_state(self) -> dict:
        """默认用户状态模板"""
        return {
            "user_profile": {
                "current_stage": "未设置",
                "primary_goal": None,
                "current_progress": 0,
                "usage_goal": None,  # 攒钱 / 梳理支出 / 理财
            },
            "financial_structure": {
                "monthly_income": 0,
                "fixed_expenses": 0,
                "discretionary_budget": 0,
                "investment_budget": 0,
            },
            "calibration_cycle": {
                "last_calibration_date": None,
                "next_calibration_date": None,
                "current_rules": None,
            },
            "streak_status": {
                "type": None,
                "current_streak_days": 0,
                "last_check_date": None,
            },
            "virtual_shelf": [],
            "goals": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

    def save(self):
        """保存用户状态"""
        self.state["updated_at"] = datetime.now().isoformat()
        self.state_file.write_text(
            json.dumps(self.state, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    def update_profile(self, **kwargs):
        """更新用户档案"""
        self.state["user_profile"].update(kwargs)
        self.save()

    def update_financial_structure(self, **kwargs):
        """更新财务结构"""
        self.state["financial_structure"].update(kwargs)
        self.save()

    def add_to_shelf(self, item_name: str, saved_amount: float, sticker_url: str = ""):
        """添加虚拟物品到储物架"""
        self.state["virtual_shelf"].append({
            "item_name": item_name,
            "saved_amount": saved_amount,
            "sticker_url": sticker_url,
            "date": datetime.now().isoformat(),
        })
        self.save()

    def increment_streak(self):
        """增加连胜天数"""
        today = datetime.now().strftime("%Y-%m-%d")
        if self.state["streak_status"]["last_check_date"] != today:
            self.state["streak_status"]["current_streak_days"] += 1
            self.state["streak_status"]["last_check_date"] = today
            self.save()

    def reset_streak(self):
        """重置连胜"""
        self.state["streak_status"]["current_streak_days"] = 0
        self.save()

    def get_state(self) -> dict:
        """获取完整状态"""
        return self.state
