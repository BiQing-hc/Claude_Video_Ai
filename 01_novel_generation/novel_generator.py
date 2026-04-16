"""
小说生成器
从创意到完整小说的自动生成
"""
import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from common.llm_client import LLMClient
from common.utils import ensure_dir, load_yaml
from common.logging_config import setup_logger

logger = setup_logger()

class NovelGenerator:
    """小说生成器"""

    def __init__(self, config_path: str = "config/project_config.yaml"):
        self.config = load_yaml(config_path)
        self.llm = LLMClient(
            provider=self.config.get("llm", {}).get("provider", "claude"),
            model=self.config.get("llm", {}).get("model")
        )
        self.output_dir = Path(self.config.get("paths", {}).get("novels", "01_novel_generation/output/novels"))
        ensure_dir(str(self.output_dir))

    def generate_concept(self, genre: str, title: str, brief: str) -> dict:
        """生成小说核心概念"""
        logger.info(f"开始生成小说概念：{title} ({genre})")

        prompt = f"""
请为一部网络小说创作核心概念设定：

题材类型：{genre}
小说标题：{title}
核心创意：{brief}

请生成以下内容：
1. 世界观设定（300-500 字）
2. 故事主线概述（200-300 字）
3. 主要角色列表（3-5 个角色，每个包含：姓名、年龄、性格、背景、特征）
4. 目标受众分析
5. 核心卖点（3-5 个）
"""

        response = self.llm.generate(prompt)
        return {"concept": response, "title": title, "genre": genre}

    def generate_chapter_outline(self, concept: dict, total_chapters: int) -> list:
        """生成章节大纲"""
        logger.info(f"开始生成{total_chapters}章的章节大纲")

        prompt = f"""
根据以下小说概念，生成{total_chapters}章的章节大纲：

{concept['concept']}

请为每一章生成：
1. 章节序号
2. 章节标题
3. 主要事件（50-80 字）
4. 出场角色
5. 情绪基调

按照以下 JSON 格式输出：
[
    {{"chapter": 1, "title": "...", "summary": "...", "characters": [...], "tone": "..."}},
    ...
]
"""

        response = self.llm.generate(prompt)
        # 这里需要解析 JSON，简化处理
        return [{"raw": response, "total": total_chapters}]

    def write_chapter(self, concept: dict, chapter_num: int, chapter_outline: str) -> str:
        """撰写单章内容"""
        logger.info(f"开始撰写第{chapter_num}章")

        prompt = f"""
根据以下设定和章节大纲，撰写小说的完整章节内容：

【小说设定】
{concept['concept']}

【本章大纲】
{chapter_outline}

【本章序号】
第{chapter_num}章

要求：
1. 正文字数：1500-2000 字
2. 包含场景描写、对话、心理活动
3. 保持与设定的连贯性
4. 章节末尾设置悬念
"""

        response = self.llm.generate(prompt, max_tokens=4096)
        return response

    def generate_novel(self, genre: str, title: str, brief: str, total_chapters: int = 100) -> str:
        """生成完整小说"""
        logger.info(f"开始生成小说：{title}, 共{total_chapters}章")

        # 1. 生成概念
        concept = self.generate_concept(genre, title, brief)

        # 2. 生成章节大纲
        chapter_outline = self.generate_chapter_outline(concept, total_chapters)

        # 3. 逐章撰写
        novel_content = f"# {title}\n\n"
        novel_content += f"**题材**: {genre}\n"
        novel_content += f"**总章节**: {total_chapters}\n"
        novel_content += f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        novel_content += "---\n\n"
        novel_content += f"{concept['concept']}\n\n"
        novel_content += "---\n\n## 正文\n\n"

        for i in range(1, min(total_chapters + 1, 4)):  # 示例：只生成前 3 章
            chapter_content = self.write_chapter(concept, i, str(chapter_outline))
            novel_content += f"\n### 第{i}章\n\n{chapter_content}\n\n"

        # 4. 保存文件
        output_file = self.output_dir / f"novel_{title}.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(novel_content)

        logger.info(f"小说已保存至：{output_file}")
        return str(output_file)


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="AI 小说生成器")
    parser.add_argument("--genre", type=str, default="玄幻", help="小说题材")
    parser.add_argument("--title", type=str, required=True, help="小说标题")
    parser.add_argument("--brief", type=str, default="", help="核心创意简述")
    parser.add_argument("--chapters", type=int, default=100, help="总章节数")
    parser.add_argument("--config", type=str, default="config/project_config.yaml", help="配置文件路径")

    args = parser.parse_args()

    generator = NovelGenerator(args.config)
    output_file = generator.generate_novel(
        genre=args.genre,
        title=args.title,
        brief=args.brief,
        total_chapters=args.chapters
    )

    print(f"\n✅ 小说生成完成：{output_file}")


if __name__ == "__main__":
    main()
