"""
视频生成统一管理器
调度多个视频生成工具，处理批量生成任务
"""
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent))

from common.utils import ensure_dir, load_yaml, get_episode_id
from common.logging_config import setup_logger
from generators.kling_generator import KlingGenerator
from generators.jimeng_generator import JimengGenerator

logger = setup_logger()


class VideoManager:
    """视频生成管理器"""

    def __init__(self, config_path: str = "config/project_config.yaml"):
        self.config = load_yaml(config_path)
        self.tools_config = self.config.get("video_tools", {})

        # 初始化工具
        self.generators = {}

        if self.tools_config.get("kling", {}).get("enabled"):
            api_key = self._get_api_key("kling")
            if api_key:
                self.generators["kling"] = KlingGenerator(api_key)

        if self.tools_config.get("jimeng", {}).get("enabled"):
            api_key = self._get_api_key("jimeng")
            if api_key:
                self.generators["jimeng"] = JimengGenerator(api_key)

        self.output_dir = Path(self.config.get("paths", {}).get("raw_videos", "04_video_generation/output/raw_videos"))
        ensure_dir(str(self.output_dir))

        # 生成记录
        self.generation_log = []

    def _get_api_key(self, tool: str) -> Optional[str]:
        """获取 API 密钥"""
        import os

        env_keys = {
            "kling": "KLING_API_KEY",
            "jimeng": "JIMENG_API_KEY",
            "runway": "RUNWAY_API_KEY"
        }

        key = os.getenv(env_keys.get(tool, ""))
        if key:
            return key

        # 尝试从配置文件读取
        config_path = Path("config/api_keys.yaml")
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                return config.get("video", {}).get(f"{tool}_api_key")

        return None

    def parse_storyboard(self, storyboard_file: str) -> List[Dict]:
        """解析分镜文档"""
        with open(storyboard_file, 'r', encoding='utf-8') as f:
            content = f.read()

        shots = []
        current_shot = {}

        for line in content.split('\n'):
            if '### Shot' in line:
                if current_shot:
                    shots.append(current_shot)
                current_shot = {"shot_index": len(shots) + 1}
            elif '**AI 提示词 (EN)**' in line:
                pass  # 下一行开始是提示词
            elif line.strip().startswith('```'):
                if 'prompt_en' not in current_shot:
                    current_shot['prompt_en'] = ""
                elif not current_shot.get('prompt_en_complete'):
                    current_shot['prompt_en_complete'] = True
            elif current_shot and not line.startswith('**') and not line.startswith('---'):
                if 'prompt_en' in current_shot and not current_shot.get('prompt_en_complete'):
                    current_shot['prompt_en'] += line + " "
                elif '推荐工具' in line:
                    current_shot['tool'] = line.split('：')[-1].strip()
                elif '时长' in line and '比例' not in line:
                    current_shot['duration'] = int(line.split('：')[-1].strip().replace('s', ''))

        if current_shot:
            shots.append(current_shot)

        return shots

    def select_generator(self, preferred_tool: str = None):
        """选择可用的生成器"""
        if preferred_tool and preferred_tool in self.generators:
            return self.generators[preferred_tool]

        # 返回第一个可用的生成器
        for tool in ["kling", "jimeng"]:
            if tool in self.generators:
                return self.generators[tool]

        raise RuntimeError("没有可用的视频生成工具")

    def generate_shot(self, shot: Dict, episode_id: str) -> Dict:
        """生成单个镜头"""
        shot_index = shot.get("shot_index", 1)
        prompt = shot.get("prompt_en", "").strip()
        tool = shot.get("tool", "kling")
        duration = shot.get("duration", 5)

        if not prompt:
            logger.warning(f"镜头{shot_index}提示词为空，跳过")
            return {"status": "skipped", "reason": "empty_prompt"}

        # 选择生成器
        try:
            generator = self.select_generator(tool)
        except RuntimeError:
            logger.error("没有可用的生成器")
            return {"status": "failed", "reason": "no_generator"}

        # 生成文件路径
        save_dir = self.output_dir / episode_id
        save_path = save_dir / f"shot_{shot_index:02d}.mp4"

        logger.info(f"生成镜头{shot_index}: {prompt[:50]}...")

        # 执行生成
        result_path = generator.generate(
            prompt=prompt,
            save_path=str(save_path),
            duration=duration
        )

        if result_path:
            logger.info(f"镜头{shot_index}生成成功：{result_path}")
            return {
                "status": "success",
                "file": result_path,
                "tool": tool
            }
        else:
            logger.error(f"镜头{shot_index}生成失败")
            return {"status": "failed", "reason": "generation_failed"}

    def generate_episode(self, storyboard_file: str, episode_id: str) -> Dict:
        """生成整集视频"""
        logger.info(f"开始生成剧集：{episode_id}")

        shots = self.parse_storyboard(storyboard_file)
        logger.info(f"共{len(shots)}个镜头")

        results = []
        success_count = 0

        for i, shot in enumerate(shots):
            logger.info(f"进度：{i + 1}/{len(shots)}")

            result = self.generate_shot(shot, episode_id)
            result["shot_index"] = shot.get("shot_index", i + 1)
            results.append(result)

            if result["status"] == "success":
                success_count += 1

        # 生成记录
        summary = {
            "episode_id": episode_id,
            "storyboard": storyboard_file,
            "timestamp": datetime.now().isoformat(),
            "total_shots": len(shots),
            "success_count": success_count,
            "failed_count": len(shots) - success_count,
            "results": results
        }

        self.generation_log.append(summary)
        return summary

    def save_log(self, log_file: Optional[str] = None):
        """保存生成记录"""
        if not log_file:
            log_file = f"logs/video_generation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"

        Path(log_file).parent.mkdir(parents=True, exist_ok=True)

        with open(log_file, 'w', encoding='utf-8') as f:
            yaml.dump(self.generation_log, f, allow_unicode=True, default_flow_style=False)

        logger.info(f"生成记录已保存：{log_file}")


def main():
    parser = argparse.ArgumentParser(description="视频生成管理器")
    parser.add_argument("--storyboard", type=str, required=True, help="分镜文件路径")
    parser.add_argument("--episode", type=str, required=True, help="剧集 ID (如 S01E01)")
    parser.add_argument("--config", type=str, default="config/project_config.yaml")

    args = parser.parse_args()

    manager = VideoManager(args.config)
    result = manager.generate_episode(args.storyboard, args.episode)

    print(f"\n生成完成:")
    print(f"  总镜头数：{result['total_shots']}")
    print(f"  成功：{result['success_count']}")
    print(f"  失败：{result['failed_count']}")

    manager.save_log()


if __name__ == "__main__":
    main()
