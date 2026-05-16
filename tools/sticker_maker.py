"""贴纸制作工具 - 接收商品图片，识别商品信息，抠图制作贴纸，添加到藏宝阁"""
import json
import base64
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional
from openai import OpenAI
from agno.tools import Toolkit
from config import ARK_API_KEY, ARK_BASE_URL, MODEL_VISION

# 贴纸输出目录
STICKER_OUTPUT_DIR = Path(__file__).parent.parent / "stickers"
STICKER_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 藏宝阁数据文件
TREASURE_DATA_FILE = Path(__file__).parent.parent / "data" / "treasure_shelf.json"
TREASURE_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)


class StickerMakerTool(Toolkit):
    """商品贴纸制作工具
    
    流程：
    1. 接收商品图片（base64）
    2. 调用视觉模型识别商品名称和估价
    3. 抠图去除背景
    4. 添加贴纸边框
    5. 保存贴纸并添加到藏宝阁数据
    """

    def __init__(self):
        super().__init__(name="sticker_maker")
        self._client = None
        self.register(self.recognize_product)
        self.register(self.create_sticker_from_image)
        self.register(self.add_to_treasure_shelf)
        self.register(self.get_treasure_shelf)

    @property
    def client(self):
        if self._client is None:
            self._client = OpenAI(
                api_key=ARK_API_KEY or "missing",
                base_url=ARK_BASE_URL,
            )
        return self._client

    def recognize_product(self, image_base64: str) -> str:
        """通过视觉模型识别商品图片中的商品名称和价格。
        
        Args:
            image_base64: 商品图片的 base64 编码字符串
        
        Returns:
            JSON 字符串，包含识别出的商品名称和估价
        """
        try:
            response = self.client.chat.completions.create(
                model=MODEL_VISION,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "请识别这张图片中的商品。返回JSON格式，包含以下字段：\n"
                                        "- name: 商品名称（简短，如'星巴克拿铁'、'Nike运动鞋'）\n"
                                        "- price: 估计价格（数字，单位元，根据商品类型合理估价）\n"
                                        "- category: 商品类别（如餐饮、服装、数码、美妆、生活用品等）\n"
                                        "只返回JSON，不要其他文字。"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=200,
            )
            
            content = response.choices[0].message.content.strip()
            # 尝试提取 JSON
            if "```" in content:
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            
            product_info = json.loads(content)
            return json.dumps({
                "success": True,
                "product": product_info,
                "message": f"识别成功：{product_info.get('name', '未知商品')}，估价 ¥{product_info.get('price', '?')}"
            }, ensure_ascii=False)
            
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e),
                "message": "商品识别失败，请重试或手动输入商品信息"
            }, ensure_ascii=False)

    def create_sticker_from_image(self, image_base64: str, product_name: str) -> str:
        """将商品图片抠图并制作成贴纸（去背景 + 加边框）。
        
        Args:
            image_base64: 商品图片的 base64 编码
            product_name: 商品名称，用于文件命名
        
        Returns:
            JSON 字符串，包含贴纸文件路径
        """
        try:
            from PIL import Image, ImageDraw, ImageFilter
            import io
            
            # 解码图片
            img_data = base64.b64decode(image_base64)
            img = Image.open(io.BytesIO(img_data)).convert("RGBA")
            
            # 抠图：去除白色/浅色背景
            datas = img.getdata()
            new_data = []
            for item in datas:
                # 白色/接近白色的像素变透明
                if item[0] > 235 and item[1] > 235 and item[2] > 235:
                    new_data.append((255, 255, 255, 0))
                else:
                    new_data.append(item)
            img.putdata(new_data)
            
            # 裁剪到内容区域（去除多余透明边距）
            bbox = img.getbbox()
            if bbox:
                img = img.crop(bbox)
            
            # 调整大小，保持比例，最大 512px
            max_size = 512
            ratio = min(max_size / img.width, max_size / img.height)
            if ratio < 1:
                new_size = (int(img.width * ratio), int(img.height * ratio))
                img = img.resize(new_size, Image.LANCZOS)
            
            # 制作贴纸：添加白色描边边框效果
            padding = 20
            sticker_size = (img.width + padding * 2, img.height + padding * 2)
            sticker = Image.new("RGBA", sticker_size, (0, 0, 0, 0))
            
            # 创建白色描边（通过扩展 alpha 通道）
            alpha = img.split()[3]
            # 膨胀 alpha 来创建边框
            border_width = 6
            border_alpha = alpha.copy()
            for _ in range(border_width):
                border_alpha = border_alpha.filter(ImageFilter.MaxFilter(3))
            
            # 白色边框层
            border_layer = Image.new("RGBA", img.size, (255, 255, 255, 0))
            border_pixels = border_layer.load()
            alpha_pixels = border_alpha.load()
            orig_alpha_pixels = alpha.load()
            for y in range(img.height):
                for x in range(img.width):
                    if alpha_pixels[x, y] > 0:
                        border_pixels[x, y] = (255, 255, 255, 255)
            
            # 合成：先贴边框，再贴原图
            sticker.paste(border_layer, (padding, padding), border_alpha)
            sticker.paste(img, (padding, padding), img)
            
            # 保存贴纸（纯英文文件名，避免中文路径问题）
            sticker_id = str(uuid.uuid4())[:8]
            filename = f"sticker_{sticker_id}.png"
            filepath = STICKER_OUTPUT_DIR / filename
            sticker.save(str(filepath), "PNG")
            
            return json.dumps({
                "success": True,
                "sticker_path": str(filepath),
                "sticker_filename": filename,
                "sticker_url": f"/api/stickers/{filename}",
                "message": f"贴纸制作完成！「{product_name}」已变成你的虚拟藏品~"
            }, ensure_ascii=False)
            
        except ImportError:
            return json.dumps({
                "success": False,
                "error": "Pillow 库未安装",
                "message": "贴纸制作功能需要 Pillow 库，请安装后重试"
            }, ensure_ascii=False)
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e),
                "message": "贴纸制作失败，请重试"
            }, ensure_ascii=False)

    def add_to_treasure_shelf(
        self,
        name: str,
        price: float,
        sticker_url: str,
        category: str = "其他",
    ) -> str:
        """将新宝物添加到藏宝阁的虚拟储物架。
        
        Args:
            name: 商品名称
            price: 商品价格
            sticker_url: 贴纸图片 URL 路径
            category: 商品类别
        
        Returns:
            JSON 字符串，包含添加结果和当前已省金额
        """
        try:
            # 读取现有数据
            shelf_data = self._load_shelf()
            
            # 新增宝物
            new_item = {
                "id": str(uuid.uuid4())[:8],
                "name": name,
                "price": price,
                "category": category,
                "sticker_url": sticker_url,
                "date": datetime.now().strftime("%m月%d日"),
                "created_at": datetime.now().isoformat(),
            }
            shelf_data["items"].insert(0, new_item)  # 最新的放最前
            shelf_data["total_saved"] = sum(item["price"] for item in shelf_data["items"])
            
            # 保存
            self._save_shelf(shelf_data)
            
            return json.dumps({
                "success": True,
                "item": new_item,
                "total_saved": shelf_data["total_saved"],
                "total_items": len(shelf_data["items"]),
                "message": f"🎉 「{name}」(¥{price}) 已加入你的虚拟储物架！\n"
                           f"累计已省下 ¥{shelf_data['total_saved']:.0f}，共 {len(shelf_data['items'])} 件宝物！"
            }, ensure_ascii=False)
            
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e),
                "message": "添加宝物失败，请重试"
            }, ensure_ascii=False)

    def get_treasure_shelf(self) -> str:
        """获取当前虚拟储物架的所有宝物列表。
        
        Returns:
            JSON 字符串，包含所有宝物和总省金额
        """
        shelf_data = self._load_shelf()
        return json.dumps({
            "success": True,
            "items": shelf_data["items"],
            "total_saved": shelf_data["total_saved"],
            "total_items": len(shelf_data["items"]),
        }, ensure_ascii=False)

    def _load_shelf(self) -> dict:
        """加载储物架数据"""
        if TREASURE_DATA_FILE.exists():
            return json.loads(TREASURE_DATA_FILE.read_text(encoding="utf-8"))
        return {"items": [], "total_saved": 0}

    def _save_shelf(self, data: dict):
        """保存储物架数据"""
        TREASURE_DATA_FILE.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
