"""图片生成工具 - 使用 Seedream 模型生成虚拟贴纸和场景图"""
import json
from typing import Optional
from openai import OpenAI
from config import ARK_API_KEY, ARK_BASE_URL, MODEL_SEEDREAM
from agno.tools import Toolkit


class ImageGeneratorTool(Toolkit):
    def __init__(self):
        super().__init__(name="image_generator")
        self.client = OpenAI(
            api_key=ARK_API_KEY,
            base_url=ARK_BASE_URL,
        )
        self.register(self.generate_sticker)
        self.register(self.generate_scenario_image)

    def generate_sticker(self, item_description: str, style: str = "2.5D cute") -> str:
        """为用户忍住没买的物品生成虚拟贴纸。
        
        Args:
            item_description: 物品描述（如"一个粉色的可爱包包"）
            style: 贴纸风格，默认 2.5D cute
        
        Returns:
            生成结果，包含图片 URL
        """
        prompt = f"生成一张{style}风格的贴纸图片，主体是：{item_description}。要求：白色背景、物品居中、边缘有轻微发光效果、整体可爱精致。"
        
        try:
            response = self.client.images.generate(
                model=MODEL_SEEDREAM,
                prompt=prompt,
                size="2048x2048",
                response_format="url",
            )
            result = {
                "success": True,
                "image_url": response.data[0].url,
                "item_description": item_description,
                "message": f"已为「{item_description}」生成虚拟贴纸！已存入你的虚拟储物架~"
            }
        except Exception as e:
            result = {
                "success": False,
                "error": str(e),
                "message": "贴纸生成失败，请稍后再试。"
            }
        
        return json.dumps(result, ensure_ascii=False)

    def generate_scenario_image(self, scenario: str, progress: Optional[float] = None) -> str:
        """为主题存钱剧本生成场景进度图。
        
        Args:
            scenario: 场景描述（如"修仙宗门建设第三层"）
            progress: 当前进度百分比 (0-100)
        
        Returns:
            生成结果，包含图片 URL
        """
        progress_text = f"，当前进度{progress}%" if progress else ""
        prompt = f"生成一张精美的游戏场景插画：{scenario}{progress_text}。风格：2.5D插画风、温暖配色、有层次感。"
        
        try:
            response = self.client.images.generate(
                model=MODEL_SEEDREAM,
                prompt=prompt,
                size="2048x1152",
                response_format="url",
            )
            result = {
                "success": True,
                "image_url": response.data[0].url,
                "scenario": scenario,
                "message": f"剧本场景图已生成：{scenario}"
            }
        except Exception as e:
            result = {
                "success": False,
                "error": str(e),
                "message": "场景图生成失败，请稍后再试。"
            }
        
        return json.dumps(result, ensure_ascii=False)
