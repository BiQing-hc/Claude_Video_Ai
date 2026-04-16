"""
即梦 (Jimeng) 视频生成器
"""
import time
import requests
from pathlib import Path
from typing import Optional
from common.logging_config import setup_logger

logger = setup_logger()


class JimengGenerator:
    """即梦视频生成器"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.jimeng.ai/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def submit_task(self, prompt: str, duration: int = 5, ratio: str = "16:9") -> Optional[str]:
        """提交视频生成任务"""
        logger.info(f"提交即梦生成任务：{prompt[:50]}...")

        payload = {
            "prompt": prompt,
            "duration": duration,
            "aspect_ratio": ratio
        }

        try:
            response = requests.post(
                f"{self.base_url}/video/generate",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()

            task_id = result.get("data", {}).get("task_id")
            if task_id:
                logger.info(f"任务提交成功：{task_id}")
                return task_id
            else:
                logger.error(f"任务提交失败：{result}")
                return None

        except Exception as e:
            logger.error(f"提交任务失败：{e}")
            return None

    def check_status(self, task_id: str) -> dict:
        """查询任务状态"""
        try:
            response = requests.get(
                f"{self.base_url}/video/status/{task_id}",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"查询状态失败：{e}")
            return {"status": "error", "error": str(e)}

    def wait_for_completion(self, task_id: str, timeout: int = 600, poll_interval: int = 10) -> Optional[str]:
        """等待任务完成"""
        logger.info(f"等待任务完成：{task_id}")

        start_time = time.time()

        while time.time() - start_time < timeout:
            result = self.check_status(task_id)
            status = result.get("data", {}).get("status", "unknown")

            if status == "completed":
                video_url = result.get("data", {}).get("video_url")
                logger.info(f"任务完成：{video_url}")
                return video_url
            elif status in ["failed", "error"]:
                logger.error(f"任务失败：{result}")
                return None
            elif status in ["processing", "queued"]:
                logger.info(f"任务进行中：{status}")
                time.sleep(poll_interval)
            else:
                time.sleep(poll_interval)

        logger.error(f"任务超时：{task_id}")
        return None

    def download_video(self, video_url: str, save_path: str) -> str:
        """下载视频"""
        logger.info(f"下载视频：{save_path}")

        try:
            response = requests.get(video_url, stream=True, timeout=60)
            response.raise_for_status()

            Path(save_path).parent.mkdir(parents=True, exist_ok=True)

            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            logger.info(f"视频已下载：{save_path}")
            return save_path

        except Exception as e:
            logger.error(f"下载失败：{e}")
            return None

    def generate(self, prompt: str, save_path: str, duration: int = 5, ratio: str = "16:9") -> Optional[str]:
        """完整生成流程"""
        task_id = self.submit_task(prompt, duration, ratio)
        if not task_id:
            return None

        video_url = self.wait_for_completion(task_id)
        if not video_url:
            return None

        return self.download_video(video_url, save_path)
