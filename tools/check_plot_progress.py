"""剧情进度检查工具 - 根据资金变动计算剧情推进状态"""
import json
from agno.tools import Toolkit
from memory.script_state import ScriptState


class CheckPlotProgressTool(Toolkit):
    def __init__(self):
        super().__init__(name="check_plot_progress")
        self.register(self.get_current_quest)
        self.register(self.record_deposit)
        self.register(self.record_save_action)
        self.register(self.get_full_progress)
        self.register(self.activate_script)

    def activate_script(self, script_id: str, user_id: str = "default_user") -> str:
        """激活一个剧本，开始新的剧情冒险。

        Args:
            script_id: 剧本 ID（如 "super_star_01"）
            user_id: 用户 ID

        Returns:
            激活结果
        """
        state = ScriptState(user_id)
        script = state.load_script(script_id)
        if not script:
            return json.dumps({"success": False, "message": f"剧本 {script_id} 不存在"}, ensure_ascii=False)

        state.activate_script(script_id)
        first_plot = script["plots"][0]
        return json.dumps({
            "success": True,
            "script_name": script["script_name"],
            "npc_role": script["npc_role"],
            "first_quest": first_plot["plot_name"],
            "first_quest_target": first_plot["required_fund"],
            "first_quest_type": first_plot["action_type"],
            "message": f"剧本「{script['script_name']}」已激活！你的角色：{script['npc_role']}。第一个任务：{first_plot['plot_name']}"
        }, ensure_ascii=False)

    def get_current_quest(self, user_id: str = "default_user") -> str:
        """获取用户当前正在进行的剧情任务。

        Args:
            user_id: 用户 ID

        Returns:
            当前任务信息
        """
        state = ScriptState(user_id)
        plot = state.get_current_plot()
        if not plot:
            return json.dumps({
                "has_active_quest": False,
                "message": "当前没有进行中的剧本。可用剧本：super_star_01（顶流诞生：大明星爽文图鉴）"
            }, ensure_ascii=False)

        progress = state.get_progress_summary()
        # 计算当前节点还需多少资金
        if plot["action_type"] == "deposit":
            remaining = plot["cumulative_fund"] - progress["total_deposited"]
            remaining = max(0, remaining)
        else:
            remaining = 0

        return json.dumps({
            "has_active_quest": True,
            "script_name": progress["script_name"],
            "current_plot": plot["plot_name"],
            "plot_id": plot["plot_id"],
            "action_type": plot["action_type"],
            "required_fund": plot["required_fund"],
            "remaining_fund": remaining,
            "total_deposited": progress["total_deposited"],
            "total_progress_percent": progress["progress_percent"],
            "message": f"当前任务：{plot['plot_name']}。" + (
                f"还需投入 {remaining} 元即可推进剧情！" if plot["action_type"] == "deposit" and remaining > 0
                else "完成一次省钱行为即可推进剧情！" if plot["action_type"] == "save_money"
                else "任务条件已满足，可以推进！"
            )
        }, ensure_ascii=False)

    def record_deposit(self, amount: float, user_id: str = "default_user") -> str:
        """记录用户的一笔存款，并检查是否触发剧情推进。

        Args:
            amount: 存款金额（元）
            user_id: 用户 ID

        Returns:
            存款记录结果，以及是否触发了剧情节点
        """
        state = ScriptState(user_id)
        state.add_deposit(amount)

        plot = state.get_current_plot()
        if not plot:
            return json.dumps({
                "deposited": amount,
                "plot_triggered": False,
                "message": "已记录存款，但当前无活跃剧本。"
            }, ensure_ascii=False)

        progress = state.get_progress_summary()
        triggered = False

        if plot["action_type"] == "deposit" and progress["total_deposited"] >= plot["cumulative_fund"]:
            triggered = True
            state.unlock_plot(plot["plot_id"])

        return json.dumps({
            "deposited": amount,
            "total_deposited": progress["total_deposited"],
            "plot_triggered": triggered,
            "triggered_plot": plot if triggered else None,
            "message": (
                f"存入 {amount} 元！剧情节点「{plot['plot_name']}」已解锁！请立即生成奖励漫画并给出激励台词！"
                if triggered else
                f"存入 {amount} 元，距离下一个剧情节点还需 {max(0, plot['cumulative_fund'] - progress['total_deposited'])} 元。"
            )
        }, ensure_ascii=False)

    def record_save_action(self, description: str, saved_amount: float = 0, user_id: str = "default_user") -> str:
        """记录用户的一次省钱/克制消费行为，并检查是否触发剧情推进。

        Args:
            description: 用户省钱行为的描述（如"今天没去吃日料，吃了食堂"）
            saved_amount: 省下的金额（用于展示，不计入累计存款）
            user_id: 用户 ID

        Returns:
            记录结果，以及是否触发了剧情节点
        """
        state = ScriptState(user_id)
        state.add_save_action()

        plot = state.get_current_plot()
        if not plot:
            return json.dumps({
                "saved": True,
                "plot_triggered": False,
                "message": "已记录省钱行为，但当前无活跃剧本。"
            }, ensure_ascii=False)

        triggered = False
        if plot["action_type"] == "save_money":
            triggered = True
            state.unlock_plot(plot["plot_id"])

        return json.dumps({
            "saved": True,
            "description": description,
            "saved_amount": saved_amount,
            "plot_triggered": triggered,
            "triggered_plot": plot if triggered else None,
            "message": (
                f"省钱行为触发剧情推进！节点「{plot['plot_name']}」已解锁！请立即生成奖励漫画并给出激励台词！"
                if triggered else
                f"已记录省钱行为：{description}。当前节点需要存款 {plot['required_fund']} 元才能推进。"
            )
        }, ensure_ascii=False)

    def get_full_progress(self, user_id: str = "default_user") -> str:
        """获取用户的完整剧情进度。

        Args:
            user_id: 用户 ID

        Returns:
            完整进度信息
        """
        state = ScriptState(user_id)
        progress = state.get_progress_summary()
        return json.dumps(progress, ensure_ascii=False)
