"""语音识别工具 - 使用豆包 ASR 模型将语音转为文本"""
import json
import base64
from typing import Optional
from openai import OpenAI
from config import ARK_API_KEY, ARK_BASE_URL, MODEL_ASR
from agno.tools import Toolkit


class SpeechRecognizerTool(Toolkit):
    def __init__(self):
        super().__init__(name="speech_recognizer")
        self.client = OpenAI(
            api_key=ARK_API_KEY,
            base_url=ARK_BASE_URL,
        )
        self.register(self.transcribe_audio)

    def transcribe_audio(self, audio_path: Optional[str] = None, audio_base64: Optional[str] = None) -> str:
        """将语音文件转录为文本。
        
        Args:
            audio_path: 音频文件路径（支持 mp3, wav, ogg 格式）
            audio_base64: Base64 编码的音频数据（二选一）
        
        Returns:
            转录结果文本
        """
        if not audio_path and not audio_base64:
            return json.dumps({
                "success": False,
                "message": "请提供音频文件路径或 Base64 编码的音频数据。"
            }, ensure_ascii=False)

        try:
            if audio_path:
                with open(audio_path, "rb") as f:
                    audio_data = f.read()
            else:
                audio_data = base64.b64decode(audio_base64)

            # 使用 OpenAI 兼容的 audio transcription 接口
            transcription = self.client.audio.transcriptions.create(
                model=MODEL_ASR,
                file=("audio.wav", audio_data, "audio/wav"),
            )

            result = {
                "success": True,
                "text": transcription.text,
                "message": "语音识别成功"
            }
        except Exception as e:
            result = {
                "success": False,
                "error": str(e),
                "message": "语音识别失败，请确保音频文件格式正确。"
            }

        return json.dumps(result, ensure_ascii=False)
