"""剧情漫画生成工具 - 生成剧本世界的沉浸式插画"""
import json
from openai import OpenAI
from agno.tools import Toolkit
from config import ARK_API_KEY, ARK_BASE_URL, MODEL_SEEDREAM


class GenerateComicPlotTool(Toolkit):
    def __init__(self):
        super().__init__(name="generate_comic_plot")
        self._client = None
        self.register(self.generate_story_comic)

    @property
    def client(self):
        if self._client is None:
            self._client = OpenAI(
                api_key=ARK_API_KEY or "missing",
                base_url=ARK_BASE_URL,
            )
        return self._client

    def generate_story_comic(self, scene_description: str, episode_title: str) -> str:
        """生成剧本世界的沉浸式插画。只展示剧本世界里发生的事情，不展示现实。

        每次用户存钱或省钱时都必须调用此工具。图片只画剧本世界中这笔钱的用途场景。

        Args:
            scene_description: 剧本世界的场景描述（如"闪耀的女明星站在时尚杂志拍摄现场，被摄影师和造型师簇拥"）。要具体、有画面感，包含人物动作、环境、色调。
            episode_title: 这一情节的标题（如"逆袭进展之：拍上时装杂志"）。会作为配字展示给用户。

        Returns:
            生成结果，包含图片 URL 和情节标题
        """
        full_prompt = (
            f"日系动漫插画风格，单幅竖版构图，画面华丽精致。"
            f"场景：{scene_description} "
            f"画面底部有一行白色艺术字标题：「{episode_title}」，字体有轻微发光效果。"
            f"整体色彩明亮，高光细腻，适合手机竖屏观看，像一张精美的故事卡片。"
        )

        try:
            response = self.client.images.generate(
                model=MODEL_SEEDREAM,
                prompt=full_prompt,
                size="2048x2048",
            )
            result = {
                "success": True,
                "image_url": response.data[0].url,
                "episode_title": episode_title,
                "message": "图片已生成。不要对用户提及图片生成过程，直接用角色身份继续对话。"
            }
        except Exception as e:
            result = {
                "success": False,
                "error": str(e),
                "episode_title": episode_title,
                "message": f"图片生成失败：{str(e)}，继续用角色身份对话即可。"
            }

        return json.dumps(result, ensure_ascii=False)
