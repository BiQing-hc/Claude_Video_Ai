"""
剧集记录生成器
为每集生成详细的元数据记录文件
"""
import sys
from pathlib import Path
from datetime import datetime
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent))

from common.utils import ensure_dir, load_yaml, get_episode_id, parse_episode_id
from common.logging_config import setup_logger

logger = setup_logger()


class RecordGenerator:
    """记录生成器"""

    def __init__(self, config_path: str = "config/project_config.yaml"):
        self.config = load_yaml(config_path)
        self.output_dir = Path(self.config.get("paths", {}).get("records", "06_metadata/records"))
        ensure_dir(str(self.output_dir))

    def collect_generation_info(self, episode_id: str, generation_log_file: str = None) -> dict:
        """收集生成信息"""
        info = {
            "episode_id": episode_id,
            "season": parse_episode_id(episode_id)[0],
            "episode_number": parse_episode_id(episode_id)[1],
            "timestamp": datetime.now().isoformat(),
            "shots": []
        }

        # 如果有生成日志，读取详细信息
        if generation_log_file and Path(generation_log_file).exists():
            with open(generation_log_file, 'r', encoding='utf-8') as f:
                logs = yaml.safe_load(f)

            for log in logs:
                if log.get("episode_id") == episode_id:
                    info["generation_summary"] = log
                    info["shots"] = log.get("results", [])
                    break

        # 收集视频文件信息
        raw_videos_dir = Path("04_video_generation/output/raw_videos") / episode_id
        if raw_videos_dir.exists():
            video_files = sorted(raw_videos_dir.glob("shot_*.mp4"))
            for i, vf in enumerate(video_files):
                stat = vf.stat()
                info["shots"].append({
                    "shot_index": i + 1,
                    "file": str(vf),
                    "size_bytes": stat.st_size,
                    "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat()
                })

        # 检查最终视频
        final_video = Path("05_post_production/output/final_videos") / f"{episode_id}_final.mp4"
        info["final_video"] = {
            "exists": final_video.exists(),
            "file": str(final_video) if final_video.exists() else None
        }

        return info

    def generate_record(self, episode_id: str, script_file: str = None, generation_log: str = None) -> str:
        """生成记录文件"""
        logger.info(f"生成记录：{episode_id}")

        info = self.collect_generation_info(episode_id, generation_log)

        # 从脚本文件提取标题等信息
        title = episode_id
        summary = ""

        if script_file and Path(script_file).exists():
            with open(script_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # 提取标题
                if 'title:' in content:
                    for line in content.split('\n'):
                        if 'title:' in line:
                            title = line.split('：')[-1].strip().strip('"')
                            break
                # 提取梗概
                if '故事梗概' in content:
                    in_summary = False
                    for line in content.split('\n'):
                        if '故事梗概' in line:
                            in_summary = True
                            continue
                        if in_summary and line.strip() and not line.startswith('#'):
                            summary += line + " "
                        elif in_summary and line.startswith('#'):
                            break

        # 计算统计信息
        shots = info.get("shots", [])
        success_count = len([s for s in shots if s.get("status") != "failed"])
        total_cost = len(shots) * 0.1  # 假设每个镜头 0.1 元

        # 生成记录内容
        record_content = f"""---
episode: {episode_id}
title: "{title}"
season: {info['season']}
episode_number: {info['episode_number']}

# 制作状态
script_status: completed
storyboard_status: completed
video_status: {"completed" if info.get('final_video', {}).get('exists') else "in_progress"}
post_production_status: {"completed" if info.get('final_video', {}).get('exists') else "pending"}
publish_status: pending

# 视频生成记录
shots:
"""

        for shot in shots:
            record_content += f"""  shot_{shot.get('shot_index', 0):02d}:
    status: {shot.get('status', 'unknown')}
    file: {shot.get('file', 'N/A')}
    size_bytes: {shot.get('size_bytes', 'N/A')}

"""

        record_content += f"""
# 成本统计
estimated_cost: {total_cost:.2f}
total_shots: {len(shots)}
success_rate: {(success_count / len(shots) * 100) if shots else 0:.1f}%

# 制作时间线
created_at: "{info['timestamp']}"

# 备注
{summary[:200] if summary else '无'}

---

## 生成日志
- [{info['timestamp']}] 记录文件生成
"""

        # 保存文件
        season_dir = self.output_dir / f"S{info['season']:02d}"
        ensure_dir(str(season_dir))

        output_file = season_dir / f"{episode_id}_record.md"

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(record_content)

        logger.info(f"记录文件已保存：{output_file}")
        return str(output_file)


def main():
    parser = argparse.ArgumentParser(description="记录生成器")
    parser.add_argument("--episode", type=str, required=True, help="剧集 ID")
    parser.add_argument("--script", type=str, help="脚本文件路径")
    parser.add_argument("--log", type=str, help="生成日志文件路径")
    parser.add_argument("--config", type=str, default="config/project_config.yaml")

    args = parser.parse_args()

    generator = RecordGenerator(args.config)
    output_file = generator.generate_record(args.episode, args.script, args.log)

    print(f"\n✅ 记录文件生成完成：{output_file}")


if __name__ == "__main__":
    main()
