"""貔貅学长 Agent 配置模块"""
import os
from dotenv import load_dotenv

load_dotenv()

# API 配置
ARK_API_KEY = os.getenv("ARK_API_KEY")
ARK_BASE_URL = os.getenv("ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")

# 模型配置
MODEL_PRO = os.getenv("ARK_MODEL_PRO", "doubao-1-5-pro-32k-250115")
MODEL_CHARACTER = os.getenv("ARK_MODEL_CHARACTER", "doubao-1-5-pro-32k-character-0228")
MODEL_VISION = os.getenv("ARK_MODEL_VISION", "doubao-1-5-vision-pro-32k-250115")
MODEL_SEEDREAM = os.getenv("ARK_MODEL_SEEDREAM", "doubao-seedream-4-5-251128")
MODEL_ASR = os.getenv("ARK_MODEL_ASR", "doubao-seed-asr-1-0")
