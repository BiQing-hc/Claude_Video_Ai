"""
AI 视频生成一人公司 - 主入口
统一管理和执行整个生产流程
"""
import sys
import argparse
from pathlib import Path
from datetime import datetime

from common.logging_config import setup_logger
from common.utils import load_yaml, ensure_dir

logger = setup_logger()


def run_novel_generation(genre: str, title: str, brief: str, chapters: int):
    """运行小说生成"""
    from 01_novel_generation.novel_generator import NovelGenerator

    generator = NovelGenerator()
    return generator.generate_novel(genre, title, brief, chapters)


def run_episode_outline(novel_file: str, episodes: int):
    """运行分集大纲生成"""
    from 02_script_writer.episode_outline import EpisodeOutlineGenerator

    generator = EpisodeOutlineGenerator()
    return generator.generate(novel_file, episodes)


def run_scripts(outline_file: str, episode: int = None):
    """运行脚本生成"""
    from 02_script_writer.script_writer import ScriptWriter

    writer = ScriptWriter()
    return writer.generate_from_outline(outline_file, episode)


def run_storyboard(script_file: str):
    """运行分镜生成"""
    from 03_storyboard.storyboard_generator import StoryboardGenerator

    generator = StoryboardGenerator()
    return generator.generate_storyboard(script_file)


def run_video_generation(storyboard_file: str, episode_id: str):
    """运行视频生成"""
    from 04_video_generation.video_manager import VideoManager

    manager = VideoManager()
    return manager.generate_episode(storyboard_file, episode_id)


def run_compositing(episode_id: str):
    """运行后期合成"""
    from 05_post_production.compositor import VideoCompositor

    compositor = VideoCompositor()
    raw_dir = "04_video_generation/output/raw_videos"
    return compositor.composite_episode(episode_id, raw_dir)


def run_record(episode_id: str, script_file: str = None):
    """运行记录生成"""
    from 06_metadata.record_generator import RecordGenerator

    generator = RecordGenerator()
    return generator.generate_record(episode_id, script_file)


def run_full_pipeline(config: dict):
    """运行完整流程"""
    logger.info("=" * 50)
    logger.info("开始完整流程")
    logger.info("=" * 50)

    # 1. 生成小说
    logger.info("\n【阶段 1】生成小说")
    novel_file = run_novel_generation(
        genre=config.get("genre", "玄幻"),
        title=config.get("title", "我的小说"),
        brief=config.get("brief", ""),
        chapters=config.get("chapters", 100)
    )

    # 2. 生成大纲
    logger.info("\n【阶段 2】生成分集大纲")
    outline_file = run_episode_outline(novel_file, config.get("episodes", 20))

    # 3. 生成脚本
    logger.info("\n【阶段 3】生成单集脚本")
    script_files = run_scripts(outline_file)

    # 4. 生成分镜
    logger.info("\n【阶段 4】生成分镜")
    storyboard_files = []
    for script_file in script_files:
        sb = run_storyboard(script_file)
        storyboard_files.append(sb)

    # 5. 生成视频
    logger.info("\n【阶段 5】生成视频")
    for i, sb_file in enumerate(storyboard_files, 1):
        episode_id = f"S01E{i:02d}"
        run_video_generation(sb_file, episode_id)

    # 6. 后期合成
    logger.info("\n【阶段 6】后期合成")
    for i in range(1, len(storyboard_files) + 1):
        episode_id = f"S01E{i:02d}"
        run_compositing(episode_id)

    # 7. 生成记录
    logger.info("\n【阶段 7】生成记录")
    for i, script_file in enumerate(script_files, 1):
        episode_id = f"S01E{i:02d}"
        run_record(episode_id, script_file)

    logger.info("\n" + "=" * 50)
    logger.info("流程完成!")
    logger.info("=" * 50)


def main():
    parser = argparse.ArgumentParser(description="AI 视频生成一人公司")
    parser.add_argument("--stage", type=str, choices=[
        "novel", "outline", "script", "storyboard",
        "video", "composite", "record", "full"
    ], default="full", help="执行阶段")

    parser.add_argument("--genre", type=str, default="玄幻", help="小说题材")
    parser.add_argument("--title", type=str, required=True, help="小说/剧集标题")
    parser.add_argument("--brief", type=str, default="", help="核心创意简述")
    parser.add_argument("--chapters", type=int, default=100, help="小说章节数")
    parser.add_argument("--episodes", type=int, default=20, help="剧集数")
    parser.add_argument("--episode", type=int, help="指定集数")
    parser.add_argument("--config", type=str, default="config/project_config.yaml")
    parser.add_argument("--novel", type=str, help="小说文件路径")
    parser.add_argument("--outline", type=str, help="大纲文件路径")
    parser.add_argument("--script", type=str, help="脚本文件路径")
    parser.add_argument("--storyboard", type=str, help="分镜文件路径")

    args = parser.parse_args()
    config = vars(args)

    # 设置日志
    setup_logger()

    logger.info(f"开始执行：{args.stage}")
    logger.info(f"标题：{args.title}")

    try:
        if args.stage == "full":
            run_full_pipeline(config)
        elif args.stage == "novel":
            run_novel_generation(args.genre, args.title, args.brief, args.chapters)
        elif args.stage == "outline":
            run_episode_outline(args.novel, args.episodes)
        elif args.stage == "script":
            run_scripts(args.outline, args.episode)
        elif args.stage == "storyboard":
            run_storyboard(args.script)
        elif args.stage == "video":
            run_video_generation(args.storyboard, f"S01E{args.episode:02d}")
        elif args.stage == "composite":
            run_compositing(f"S01E{args.episode:02d}")
        elif args.stage == "record":
            run_record(f"S01E{args.episode:02d}", args.script)

        logger.info("\n✅ 执行完成!")

    except Exception as e:
        logger.error(f"执行失败：{e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
