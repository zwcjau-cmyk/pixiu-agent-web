"""剧情状态管理 - 存储用户当前剧本进度、累计资金、已解锁节点"""
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"


class ScriptState:
    """剧情状态管理器，负责持久化用户的剧本进度"""

    def __init__(self, user_id: str = "default_user"):
        self.user_id = user_id
        self.state_file = DATA_DIR / f"{user_id}_script_state.json"
        self.state = self._load_state()

    def _load_state(self) -> dict:
        if self.state_file.exists():
            return json.loads(self.state_file.read_text(encoding="utf-8"))
        return self._default_state()

    def _default_state(self) -> dict:
        return {
            "active_script_id": None,
            "total_deposited": 0,
            "total_saved_count": 0,
            "current_plot_id": 1,
            "unlocked_plots": [],
            "comic_gallery": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

    def save(self):
        self.state["updated_at"] = datetime.now().isoformat()
        self.state_file.write_text(
            json.dumps(self.state, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    def load_script(self, script_id: str) -> Optional[dict]:
        """加载指定剧本的 JSON 配置"""
        script_file = SCRIPTS_DIR / f"{script_id}.json"
        if not script_file.exists():
            return None
        return json.loads(script_file.read_text(encoding="utf-8"))

    def activate_script(self, script_id: str):
        """激活一个剧本"""
        self.state["active_script_id"] = script_id
        self.state["current_plot_id"] = 1
        self.state["total_deposited"] = 0
        self.state["total_saved_count"] = 0
        self.state["unlocked_plots"] = []
        self.state["comic_gallery"] = []
        self.save()

    def add_deposit(self, amount: float):
        """记录一笔存款"""
        self.state["total_deposited"] += amount
        self.save()

    def add_save_action(self):
        """记录一次省钱行为"""
        self.state["total_saved_count"] += 1
        self.save()

    def unlock_plot(self, plot_id: int, comic_url: str = ""):
        """解锁一个剧情节点"""
        if plot_id not in self.state["unlocked_plots"]:
            self.state["unlocked_plots"].append(plot_id)
        self.state["current_plot_id"] = plot_id + 1
        if comic_url:
            self.state["comic_gallery"].append({
                "plot_id": plot_id,
                "comic_url": comic_url,
                "unlocked_at": datetime.now().isoformat(),
            })
        self.save()

    def get_current_plot(self) -> Optional[dict]:
        """获取当前待完成的剧情节点"""
        script_id = self.state.get("active_script_id")
        if not script_id:
            return None
        script = self.load_script(script_id)
        if not script:
            return None
        current_id = self.state["current_plot_id"]
        for plot in script["plots"]:
            if plot["plot_id"] == current_id:
                return plot
        return None

    def get_progress_summary(self) -> dict:
        """获取完整进度摘要"""
        script_id = self.state.get("active_script_id")
        script = self.load_script(script_id) if script_id else None
        return {
            "active_script_id": script_id,
            "script_name": script["script_name"] if script else None,
            "total_deposited": self.state["total_deposited"],
            "total_saved_count": self.state["total_saved_count"],
            "current_plot_id": self.state["current_plot_id"],
            "total_plots": len(script["plots"]) if script else 0,
            "unlocked_plots": self.state["unlocked_plots"],
            "total_target": script["total_fund_target"] if script else 0,
            "progress_percent": round(
                self.state["total_deposited"] / script["total_fund_target"] * 100, 1
            ) if script and script["total_fund_target"] > 0 else 0,
        }

    def get_state(self) -> dict:
        return self.state
