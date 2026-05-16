"""金库资金管理工具 - 管理活期池、定期舱、基金图鉴和梦想清单，直接读写本地数据"""
import json
from pathlib import Path
from typing import Optional
from agno.tools import Toolkit

VAULT_FILE = Path(__file__).parent.parent / "data" / "vault.json"
VAULT_FILE.parent.mkdir(parents=True, exist_ok=True)

DEFAULT_VAULT = {
    "total_assets": 13579.30,
    "monthly_growth": 856,
    "accounts": {
        "active_pool": {"label": "活期池", "balance": 3428.50, "rate": "1.8%"},
        "fixed_deposit": {"label": "定期舱", "balance": 8000.00, "rate": "3.2%", "term": "90天"},
        "fund_collection": {"label": "基金图鉴", "balance": 2150.80, "rate": "+2.3%"}
    },
    "goals": [
        {"name": "AirPods Pro", "target": 1799, "current": 1295, "emoji": "🎧"},
        {"name": "毕业旅行基金", "target": 5000, "current": 2250, "emoji": "✈️"},
        {"name": "新款iPad", "target": 3499, "current": 980, "emoji": "📱"}
    ]
}


def _load_vault() -> dict:
    if VAULT_FILE.exists():
        return json.loads(VAULT_FILE.read_text(encoding="utf-8"))
    return DEFAULT_VAULT.copy()


def _save_vault(data: dict):
    VAULT_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


class VaultManagerTool(Toolkit):
    def __init__(self):
        super().__init__(name="vault_manager")
        self.register(self.get_vault_status)
        self.register(self.deposit_to_account)
        self.register(self.update_goal_progress)

    def get_vault_status(self) -> str:
        """获取用户金库的整体状态，包括总资产、活期池、定期舱、基金图鉴的余额以及梦想清单进度。

        Returns:
            金库完整状态 JSON
        """
        data = _load_vault()
        return json.dumps(data, ensure_ascii=False)

    def deposit_to_account(self, account: str, amount: float) -> str:
        """存钱到指定账户。当用户说存了钱/转入/充值到某个账户时调用。

        Args:
            account: 账户类型，可选值：
                - "active_pool"（活期池）
                - "fixed_deposit"（定期舱）
                - "fund_collection"（基金图鉴）
            amount: 存入金额（正数表示存入，负数表示取出）

        Returns:
            更新结果，包含新的总资产和账户余额
        """
        data = _load_vault()
        if account not in data.get("accounts", {}):
            return json.dumps({"success": False, "message": f"未知账户: {account}"}, ensure_ascii=False)

        data["accounts"][account]["balance"] += amount
        data["total_assets"] = sum(acc["balance"] for acc in data["accounts"].values())
        data["monthly_growth"] = data.get("monthly_growth", 0) + amount
        _save_vault(data)

        return json.dumps({
            "success": True,
            "total_assets": data["total_assets"],
            "account_label": data["accounts"][account]["label"],
            "new_balance": data["accounts"][account]["balance"],
            "message": f"{data['accounts'][account]['label']}已存入 ¥{amount}，当前余额 ¥{data['accounts'][account]['balance']:.2f}，总资产 ¥{data['total_assets']:.2f}"
        }, ensure_ascii=False)

    def update_goal_progress(self, goal_name: str, amount: float) -> str:
        """更新梦想清单中某个目标的进度。当用户说为某个目标存了钱时调用。

        Args:
            goal_name: 目标名称，如 "AirPods Pro"、"毕业旅行基金"、"新款iPad"
            amount: 本次新存入的金额

        Returns:
            更新结果，包含目标最新进度
        """
        data = _load_vault()
        goals = data.get("goals", [])

        for goal in goals:
            if goal["name"] == goal_name:
                goal["current"] = min(goal["current"] + amount, goal["target"])
                progress = int(goal["current"] / goal["target"] * 100)
                _save_vault(data)
                return json.dumps({
                    "success": True,
                    "goal": goal,
                    "progress": progress,
                    "message": f"「{goal_name}」进度更新：¥{goal['current']:.0f}/¥{goal['target']} ({progress}%)"
                }, ensure_ascii=False)

        # 没找到，新建目标
        new_goal = {"name": goal_name, "target": amount, "current": 0, "emoji": "🎯"}
        goals.append(new_goal)
        data["goals"] = goals
        _save_vault(data)
        return json.dumps({
            "success": True,
            "goal": new_goal,
            "message": f"新目标「{goal_name}」已创建，目标金额 ¥{amount}"
        }, ensure_ascii=False)
