"""
语音服务模块
集成语音识别(ASR)和语音合成(TTS)
"""

import os
import base64
import requests
from typing import Optional, Dict
from dotenv import load_dotenv

load_dotenv()


class VoiceService:
    """
    语音服务类
    使用百度语音API
    """
    
    def __init__(self):
        self.app_id = os.getenv("BAIDU_APP_ID")
        self.api_key = os.getenv("BAIDU_API_KEY")
        self.secret_key = os.getenv("BAIDU_SECRET_KEY")
        self.access_token = self._get_access_token()
    
    def _get_access_token(self) -> str:
        """获取百度API访问令牌"""
        url = f"https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.secret_key
        }
        
        try:
            response = requests.post(url, params=params)
            result = response.json()
            return result.get("access_token", "")
        except Exception as e:
            print(f"获取access_token失败: {e}")
            return ""
    
    def speech_to_text(self, audio_data: bytes, format: str = "wav", rate: int = 16000) -> Dict:
        """
        语音识别（ASR）
        将语音转换为文字
        
        Args:
            audio_data: 音频数据（bytes）
            format: 音频格式（wav, pcm, amr等）
            rate: 采样率
            
        Returns:
            {"success": bool, "text": str, "error": str}
        """
        if not self.access_token:
            return {"success": False, "text": "", "error": "未获取到access_token"}
        
        url = f"https://vop.baidu.com/server_api"
        
        # Base64编码音频数据
        speech = base64.b64encode(audio_data).decode('utf-8')
        
        headers = {
            "Content-Type": "application/json"
        }
        
        payload = {
            "format": format,
            "rate": rate,
            "channel": 1,
            "cuid": "emotional_agent_user",
            "token": self.access_token,
            "speech": speech,
            "len": len(audio_data)
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            result = response.json()
            
            if result.get("err_no") == 0:
                return {
                    "success": True,
                    "text": result.get("result", [""])[0],
                    "error": ""
                }
            else:
                return {
                    "success": False,
                    "text": "",
                    "error": result.get("err_msg", "识别失败")
                }
        except Exception as e:
            return {"success": False, "text": "", "error": str(e)}
    
    def text_to_speech(self, text: str, spd: int = 5, pit: int = 5, vol: int = 5, per: int = 0) -> Dict:
        """
        语音合成（TTS）
        将文字转换为语音
        
        Args:
            text: 要合成的文字
            spd: 语速（0-15）
            pit: 音调（0-15）
            vol: 音量（0-15）
            per: 发音人（0:女声，1:男声，3:度逍遥，4:度丫丫）
            
        Returns:
            {"success": bool, "audio_data": bytes, "error": str}
        """
        if not self.access_token:
            return {"success": False, "audio_data": None, "error": "未获取到access_token"}
        
        url = f"https://tsn.baidu.com/text2audio"
        
        params = {
            "tex": text,
            "tok": self.access_token,
            "cuid": "emotional_agent_user",
            "ctp": 1,
            "lan": "zh",
            "spd": spd,
            "pit": pit,
            "vol": vol,
            "per": per,
            "aue": 3  # mp3格式
        }
        
        try:
            response = requests.post(url, data=params)
            
            # 检查Content-Type
            content_type = response.headers.get("Content-Type", "")
            
            if "audio" in content_type:
                return {
                    "success": True,
                    "audio_data": response.content,
                    "error": ""
                }
            else:
                # 返回的是错误信息（JSON格式）
                try:
                    error_result = response.json()
                    return {
                        "success": False,
                        "audio_data": None,
                        "error": error_result.get("err_msg", "合成失败")
                    }
                except:
                    return {
                        "success": False,
                        "audio_data": None,
                        "error": "合成失败"
                    }
        except Exception as e:
            return {"success": False, "audio_data": None, "error": str(e)}


# 全局语音服务实例
voice_service = VoiceService()


def speech_to_text(audio_data: bytes, format: str = "wav", rate: int = 16000) -> Dict:
    """语音识别接口"""
    return voice_service.speech_to_text(audio_data, format, rate)


def text_to_speech(text: str, spd: int = 5, pit: int = 5, vol: int = 5, per: int = 0) -> Dict:
    """语音合成接口"""
    return voice_service.text_to_speech(text, spd, pit, vol, per)


# 测试
if __name__ == "__main__":
    # 测试语音合成
    result = text_to_speech("你好，我是情感陪伴AI，很高兴为你服务！")
    if result["success"]:
        print("语音合成成功")
        # 保存音频文件
        with open("test_output.mp3", "wb") as f:
            f.write(result["audio_data"])
        print("音频已保存到 test_output.mp3")
    else:
        print(f"语音合成失败: {result['error']}")
