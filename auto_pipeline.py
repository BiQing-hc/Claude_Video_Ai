"""
AI 视频生成一人公司 - 一键自动化流程
从小说到脚本到提示词的全流程自动生成
"""
import sys
import argparse
from pathlib import Path
from datetime import datetime

from common.logging_config import setup_logger

logger = setup_logger()


def print_banner():
    """打印欢迎横幅"""
    print("\n" + "=" * 70)
    print("           AI 视频生成一人公司 - 自动化流程")
    print("=" * 70)
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70 + "\n")


def run_novel_generation(genre: str, title: str, brief: str, total_chapters: int, write_first_n: int = 20):
    """运行小说生成"""
    from 01_novel_generation.novel_outline_generator import NovelOutlineGenerator

    logger.info("=" * 60)
    logger.info("【阶段 1】生成长篇小说大纲和开篇")
    logger.info("=" * 60)

    generator = NovelOutlineGenerator()
    result = generator.generate_full_novel(
        genre=genre,
        title=title,
        brief=brief,
        total_chapters=total_chapters
    )

    # 返回小说文件路径
    novel_file = f"01_novel_generation/output/novels/novel_{title}_正文_第 1-{write_first_n}章.md"
    return novel_file, result


def run_script_generation(novel_file: str, num_episodes: int = 5):
    """运行脚本批量生成"""
    from 02_script_writer.batch_script_writer import BatchScriptWriter

    logger.info("=" * 60)
    logger.info("【阶段 2】批量生成短剧脚本")
    logger.info("=" * 60)

    writer = BatchScriptWriter()
    script_files = writer.generate_batch(novel_file, num_episodes)

    return script_files


def run_prompt_generation(script_files: list):
    """运行提示词汇总生成"""
    from 03_storyboard.batch_storyboard_generator import BatchStoryboardGenerator

    logger.info("=" * 60)
    logger.info("【阶段 3】生成 AI 视频提示词汇总")
    logger.info("=" * 60)

    generator = BatchStoryboardGenerator()
    output_file = generator.generate_prompt_collection(script_files)

    return output_file


def run_full_pipeline(genre: str, title: str, brief: str, total_chapters: int, episodes: int):
    """运行完整流程"""
    print_banner()

    logger.info("开始完整自动化流程")
    logger.info(f"小说题材：{genre}")
    logger.info(f"小说标题：{title}")
    logger.info(f"计划章节：{total_chapters}章")
    logger.info(f"短剧集数：{episodes}集")
    logger.info("")

    # 阶段 1：生成小说
    novel_file, novel_result = run_novel_generation(genre, title, brief, total_chapters)

    # 阶段 2：生成脚本
    script_files = run_script_generation(novel_file, episodes)

    # 阶段 3：生成提示词
    prompt_file = run_prompt_generation(script_files)

    # 完成
    print_banner()
    print("\n✅ 完整流程完成!\n")
    print("📁 生成的文件:")
    print(f"   小说世界观：01_novel_generation/output/novels/{title}_世界观设定.md")
    print(f"   小说主线：01_novel_generation/output/novels/{title}_主线剧情.md")
    print(f"   小说正文：{novel_file}")
    print(f"   短剧脚本：{len(script_files)}集")
    for sf in script_files:
        print(f"      - {sf}")
    print(f"   提示词汇总：{prompt_file}")
    print("\n" + "=" * 70)
    print("下一步：使用提示词在 AI 视频工具中生成视频")
    print("推荐工具：可灵 AI (https://klingai.kuaishou.com/)")
    print("=" * 70 + "\n")


def main():
    parser = argparse.ArgumentParser(description="AI 视频生成一人公司 - 一键自动化流程")

    # 模式选择
    parser.add_argument("--mode", type=str, choices=["full", "novel", "script", "prompt"],
                        default="full", help="运行模式")

    # 小说参数
    parser.add_argument("--genre", type=str, default="玄幻", help="小说题材")
    parser.add_argument("--title", type=str, required=True, help="小说标题")
    parser.add_argument("--brief", type=str, default="", help="核心创意简述")
    parser.add_argument("--chapters", type=int, default=2000, help="小说总章节数（计划）")

    # 短剧参数
    parser.add_argument("--episodes", type=int, default=5, help="短剧集数")

    # 文件参数
    parser.add_argument("--novel", type=str, help="小说文件路径（用于 script/prompt 模式）")
    parser.add_argument("--scripts", type=str, nargs="+", help="脚本文件列表（用于 prompt 模式）")

    # 配置
    parser.add_argument("--config", type=str, default="config/project_config.yaml", help="配置文件路径")

    args = parser.parse_args()

    # 设置日志
    setup_logger()

    try:
        if args.mode == "full":
            run_full_pipeline(
                genre=args.genre,
                title=args.title,
                brief=args.brief,
                total_chapters=args.chapters,
                episodes=args.episodes
            )

        elif args.mode == "novel":
            novel_file, _ = run_novel_generation(
                genre=args.genre,
                title=args.title,
                brief=args.brief,
                total_chapters=args.chapters
            )
            print(f"\n✅ 小说生成完成：{novel_file}")

        elif args.mode == "script":
            if not args.novel:
                print("❌ 错误：--novel 参数是必需的")
                sys.exit(1)
            script_files = run_script_generation(args.novel, args.episodes)
            print(f"\n✅ 脚本生成完成，共{len(script_files)}集")

        elif args.mode == "prompt":
            if not args.scripts:
                print("❌ 错误：--scripts 参数是必需的")
                sys.exit(1)
            prompt_file = run_prompt_generation(args.scripts)
            print(f"\n✅ 提示词汇总完成：{prompt_file}")

    except Exception as e:
        logger.error(f"流程执行失败：{e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
