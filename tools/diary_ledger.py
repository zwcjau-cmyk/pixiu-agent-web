"""日记转账单工具 - 从用户自然语言中提取消费记录，按 user_id 隔离存储"""
import json
from datetime import datetime
from pathlib import Path
from typing import Optional
from agno.tools import Toolkit

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def _get_user_expenses_file(user_id: str) -> Path:
    """按 user_id 返回隔离的收支文件路径"""
    safe_id = user_id.replace("/", "_").replace("..", "_")
    return DATA_DIR / f"expenses_{safe_id}.json"


def _load_expenses_for_read(user_id: str = "default_user") -> dict:
    """加载收支数据用于查询：mock 数据 + 当前用户数据合并返回"""
    # 加载 mock 数据
    try:
        from data.mock_data import DEFAULT_EXPENSES
        mock_records = DEFAULT_EXPENSES.get("records", [])
    except ImportError:
        mock_records = []

    # 加载用户隔离文件
    user_records = []
    user_file = _get_user_expenses_file(user_id)
    if user_file.exists():
        try:
            data = json.loads(user_file.read_text(encoding="utf-8"))
            user_records = data.get("records", [])
        except (json.JSONDecodeError, KeyError):
            pass

    # 合并：用户新数据在前，mock 在后
    all_records = user_records + mock_records

    # 重新计算汇总
    total_expense = sum(r["amount"] for r in all_records if r.get("type") == "expense")
    total_income = sum(r["amount"] for r in all_records if r.get("type") == "income")

    return {
        "records": all_records,
        "monthly_summary": {"total_expense": total_expense, "total_income": total_income}
    }


def _load_expenses_for_write(user_id: str = "default_user") -> dict:
    """加载用户隔离文件用于写入，绝不加载 mock 数据"""
    user_file = _get_user_expenses_file(user_id)
    if user_file.exists():
        try:
            data = json.loads(user_file.read_text(encoding="utf-8"))
            if data.get("records") and len(data["records"]) > 0:
                return data
        except (json.JSONDecodeError, KeyError):
            pass
    return {"records": [], "monthly_summary": {"total_expense": 0, "total_income": 0}}


def _save_expenses(data: dict, user_id: str = "default_user"):
    user_file = _get_user_expenses_file(user_id)
    user_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


class DiaryToLedgerTool(Toolkit):
    def __init__(self):
        super().__init__(name="diary_ledger")
        self._current_user_id = "default_user"
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
        user_id = self._current_user_id
        data = _load_expenses_for_write(user_id)
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
        _save_expenses(data, user_id)

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
        user_id = self._current_user_id
        data = _load_expenses_for_write(user_id)
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
        _save_expenses(data, user_id)

        return json.dumps({
            "success": True,
            "record": record,
            "monthly_summary": data["monthly_summary"],
            "message": f"已记录收入 ¥{amount}（{category}：{description}）"
        }, ensure_ascii=False)

    def get_daily_summary(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> str:
        """获取收支记录。可按日期范围筛选。不传参数则返回全部记录。

        Args:
            start_date: 起始日期，格式 YYYY-MM-DD（含），如 "2026-02-18"
            end_date: 结束日期，格式 YYYY-MM-DD（含），如 "2026-05-18"

        Returns:
            符合条件的收支记录和汇总
        """
        user_id = self._current_user_id
        data = _load_expenses_for_read(user_id)
        records = data.get("records", [])

        # 按日期范围筛选
        if start_date or end_date:
            filtered = []
            for r in records:
                d = r.get("date", "")
                if start_date and d < start_date:
                    continue
                if end_date and d > end_date:
                    continue
                filtered.append(r)
            records = filtered

        # 计算筛选后的汇总
        total_expense = sum(r["amount"] for r in records if r.get("type") == "expense")
        total_income = sum(r["amount"] for r in records if r.get("type") == "income")

        return json.dumps({
            "records": records,
            "summary": {
                "total_expense": total_expense,
                "total_income": total_income,
                "net": total_income - total_expense,
                "record_count": len(records),
                "date_range": f"{start_date or '最早'} ~ {end_date or '最新'}"
            }
        }, ensure_ascii=False)
