"""
视频合成器
将多个视频片段合成为完整剧集
"""
import sys
from pathlib import Path
from typing import List, Optional
import subprocess

sys.path.insert(0, str(Path(__file__).parent.parent))

from common.utils import ensure_dir, load_yaml
from common.logging_config import setup_logger

logger = setup_logger()


class VideoCompositor:
    """视频合成器"""

    def __init__(self, config_path: str = "config/project_config.yaml"):
        self.config = load_yaml(config_path)
        self.output_dir = Path(self.config.get("paths", {}).get("final_videos", "05_post_production/output/final_videos"))
        ensure_dir(str(self.output_dir))

    def merge_videos(self, video_files: List[str], output_file: str, transition: bool = False) -> Optional[str]:
        """合并多个视频文件"""
        logger.info(f"开始合并{len(video_files)}个视频文件")

        # 创建临时文件列表
        temp_list_file = Path("temp_video_list.txt")
        with open(temp_list_file, 'w', encoding='utf-8') as f:
            for video_file in video_files:
                f.write(f"file '{Path(video_file).absolute()}'\n")

        try:
            # 使用 ffmpeg 合并
            cmd = [
                "ffmpeg", "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", str(temp_list_file),
                "-c", "copy",
                output_file
            ]

            subprocess.run(cmd, check=True, capture_output=True)
            logger.info(f"视频合并完成：{output_file}")
            return output_file

        except subprocess.CalledProcessError as e:
            logger.error(f"合并失败：{e}")
            return None
        finally:
            # 清理临时文件
            if temp_list_file.exists():
                temp_list_file.unlink()

    def add_audio(self, video_file: str, audio_file: str, output_file: str) -> Optional[str]:
        """添加音频到视频"""
        logger.info(f"添加音频：{audio_file}")

        cmd = [
            "ffmpeg", "-y",
            "-i", video_file,
            "-i", audio_file,
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            output_file
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info(f"音频添加完成：{output_file}")
            return output_file
        except subprocess.CalledProcessError as e:
            logger.error(f"添加音频失败：{e}")
            return None

    def add_subtitles(self, video_file: str, subtitle_file: str, output_file: str) -> Optional[str]:
        """添加字幕到视频"""
        logger.info(f"添加字幕：{subtitle_file}")

        cmd = [
            "ffmpeg", "-y",
            "-i", video_file,
            "-vf", f"subtitles={subtitle_file}",
            "-c:a", "copy",
            output_file
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info(f"字幕添加完成：{output_file}")
            return output_file
        except subprocess.CalledProcessError as e:
            logger.error(f"添加字幕失败：{e}")
            return None

    def composite_episode(self, episode_id: str, raw_videos_dir: str) -> Optional[str]:
        """合成整集视频"""
        logger.info(f"开始合成剧集：{episode_id}")

        raw_dir = Path(raw_videos_dir) / episode_id
        if not raw_dir.exists():
            logger.error(f"原始视频目录不存在：{raw_dir}")
            return None

        # 获取所有视频文件，按名称排序
        video_files = sorted(raw_dir.glob("shot_*.mp4"))

        if not video_files:
            logger.error(f"未找到视频文件：{raw_dir}")
            return None

        # 合并视频
        output_file = self.output_dir / f"{episode_id}_final.mp4"
        video_files = [str(f) for f in video_files]

        return self.merge_videos(video_files, str(output_file))


def main():
    parser = argparse.ArgumentParser(description="视频合成器")
    parser.add_argument("--episode", type=str, required=True, help="剧集 ID")
    parser.add_argument("--input", type=str, required=True, help="原始视频目录")
    parser.add_argument("--config", type=str, default="config/project_config.yaml")

    args = parser.parse_args()

    compositor = VideoCompositor(args.config)
    output_file = compositor.composite_episode(args.episode, args.input)

    if output_file:
        print(f"\n✅ 合成完成：{output_file}")
    else:
        print("\n❌ 合成失败")


if __name__ == "__main__":
    import argparse
    main()
