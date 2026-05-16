"""日记转账单工具 - 从用户自然语言中提取消费记录，直接读写本地数据"""
import json
from datetime import datetime
from pathlib import Path
from typing import Optional
from agno.tools import Toolkit

EXPENSES_FILE = Path(__file__).parent.parent / "data" / "expenses.json"
EXPENSES_FILE.parent.mkdir(parents=True, exist_ok=True)


def _load_expenses() -> dict:
    if EXPENSES_FILE.exists():
        return json.loads(EXPENSES_FILE.read_text(encoding="utf-8"))
    return {"records": [], "monthly_summary": {"total_expense": 0, "total_income": 0}}


def _save_expenses(data: dict):
    EXPENSES_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


class DiaryToLedgerTool(Toolkit):
    def __init__(self):
        super().__init__(name="diary_ledger")
        self.register(self.record_expense)
        self.register(self.record_income)
        self.register(self.get_daily_summary)

    def record_expense(self, category: str, amount: float, description: str = "", date: Optional[str] = None) -> str:
        """记录一笔支出。当用户说了花钱/消费/买东西等信息时调用。

        Args:
            category: 消费类别（餐饮/购物/交通/娱乐/生活用品/数码/其他）
            amount: 金额（数字）
            description: 具体描述，如"中午吃了麻辣烫"
            date: 日期，格式 YYYY-MM-DD，默认今天

        Returns:
            记录结果
        """
        data = _load_expenses()
        record = {
            "category": category,
            "amount": amount,
            "description": description,
            "type": "expense",
            "date": date or datetime.now().strftime("%Y-%m-%d"),
            "created_at": datetime.now().isoformat(),
        }
        data["records"].insert(0, record)
        data["monthly_summary"]["total_expense"] = data["monthly_summary"].get("total_expense", 0) + amount
        _save_expenses(data)

        return json.dumps({
            "success": True,
            "record": record,
            "monthly_summary": data["monthly_summary"],
            "message": f"已记录支出 ¥{amount}（{category}：{description}）"
        }, ensure_ascii=False)

    def record_income(self, category: str, amount: float, description: str = "", date: Optional[str] = None) -> str:
        """记录一笔收入。当用户说了赚钱/收到/进账/工资/生活费等信息时调用。

        Args:
            category: 收入类别（生活费/兼职/奖学金/红包/其他）
            amount: 金额（数字）
            description: 具体描述
            date: 日期，格式 YYYY-MM-DD，默认今天

        Returns:
            记录结果
        """
        data = _load_expenses()
        record = {
            "category": category,
            "amount": amount,
            "description": description,
            "type": "income",
            "date": date or datetime.now().strftime("%Y-%m-%d"),
            "created_at": datetime.now().isoformat(),
        }
        data["records"].insert(0, record)
        data["monthly_summary"]["total_income"] = data["monthly_summary"].get("total_income", 0) + amount
        _save_expenses(data)

        return json.dumps({
            "success": True,
            "record": record,
            "monthly_summary": data["monthly_summary"],
            "message": f"已记录收入 ¥{amount}（{category}：{description}）"
        }, ensure_ascii=False)

    def get_daily_summary(self, date: Optional[str] = None) -> str:
        """获取收支汇总，了解用户本月的收支情况。

        Returns:
            收支汇总数据
        """
        data = _load_expenses()
        return json.dumps({
            "records": data.get("records", [])[:20],
            "monthly_summary": data.get("monthly_summary", {"total_expense": 0, "total_income": 0}),
        }, ensure_ascii=False)
