"""
长篇小说大纲生成器
生成几千章小说的完整大纲和开篇内容
"""
import sys
from pathlib import Path
from datetime import datetime
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from common.llm_client import LLMClient
from common.utils import ensure_dir, load_yaml
from common.logging_config import setup_logger

logger = setup_logger()


class NovelOutlineGenerator:
    """长篇小说大纲生成器"""

    def __init__(self, config_path: str = "config/project_config.yaml"):
        self.config = load_yaml(config_path) if Path(config_path).exists() else {}
        self.llm = LLMClient(
            provider=self.config.get("llm", {}).get("provider", "claude"),
            model=self.config.get("llm", {}).get("model")
        )
        self.output_dir = Path("01_novel_generation/output/novels")
        ensure_dir(str(self.output_dir))

    def generate_world_building(self, genre: str, title: str, brief: str) -> dict:
        """生成世界观设定"""
        logger.info(f"开始生成世界观：{title} ({genre})")

        prompt = f"""
请为一部{genre}类型的长篇小说创作详细的世界观设定：

小说标题：{title}
核心创意：{brief}

请生成以下内容（总计 3000-5000 字）：

1. 【世界背景】（800-1000 字）
   - 世界名称和地理格局
   - 历史沿革（远古时代、上古大战、当前时代）
   - 世界规则（灵气、法则、禁忌）

2. 【修炼体系】（800-1000 字）
   - 详细境界划分（至少 7 个大境界，每个境界 3-9 个小境界）
   - 每个境界的特征和能力
   - 修炼方法和资源

3. 【势力分布】（600-800 字）
   - 主要宗门/家族（至少 5 个正派、5 个反派）
   - 各势力的位置、实力、特点
   - 势力之间的关系

4. 【特殊设定】（600-800 字）
   - 宝物/神器体系
   - 特殊职业（炼丹师、炼器师等）
   - 特殊地点（秘境、禁地等）
   - 异族/妖兽体系

请用 JSON 格式输出，键名为：world_background, cultivation_system, factions, special_settings
"""

        response = self.llm.generate(prompt, max_tokens=8192)

        # 尝试解析 JSON
        try:
            # 提取 JSON 部分
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass

        return {"raw": response}

    def generate_main_storyline(self, world: dict, total_chapters: int) -> dict:
        """生成主线剧情大纲"""
        logger.info(f"生成长达{total_chapters}章的主线剧情")

        prompt = f"""
根据以下世界观，生成一部长篇小说的主线剧情大纲：

【世界观概要】
{str(world)[:3000]}

【小说规模】
总章节数：{total_chapters}章

请生成主线剧情大纲（总计 3000-5000 字）：

1. 【故事主线】（500 字）
   - 主角的核心目标
   - 主要冲突和反派
   - 故事主题

2. 【卷/篇划分】（2000-3000 字）
   将{total_chapters}章划分为 8-12 个大卷，每卷包含：
   - 卷名
   - 章节范围（如第 1-100 章）
   - 本卷主线剧情概述（300-500 字）
   - 本卷高潮事件
   - 主角成长目标

3. 【角色成长线】（500-800 字）
   - 主角从弱到强的成长阶段
   - 各阶段对应的境界
   - 重要转折点

请用 JSON 格式输出，键名为：main_story, volumes, character_growth
"""

        response = self.llm.generate(prompt, max_tokens=8192)

        try:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass

        return {"raw": response}

    def generate_volume_outlines(self, world: dict, main_story: dict, volume_num: int, chapters_in_volume: int) -> dict:
        """生成单卷详细大纲"""
        logger.info(f"生成第{volume_num}卷详细大纲（{chapters_in_volume}章）")

        prompt = f"""
根据以下设定，生成第{volume_num}卷的详细章节大纲：

【世界观】
{str(world)[:2000]}

【主线剧情】
{str(main_story)[:2000]}

【本卷信息】
卷序号：{volume_num}
本卷章节数：{chapters_in_volume}章

请为每一章生成简要概述（每章 50-100 字），包括：
- 章节序号（从 1 开始）
- 章节标题（4-8 字，有吸引力）
- 主要事件
- 出场重要角色
- 情绪基调（轻松/紧张/悲伤/热血等）
- 是否有重要伏笔

请按以下 JSON 格式输出：
{{
    "chapters": [
        {{"chapter": 1, "title": "...", "summary": "...", "characters": [...], "tone": "...", "foreshadowing": "..."}},
        ...
    ]
}}
"""

        response = self.llm.generate(prompt, max_tokens=16384)

        try:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass

        return {"raw": response}

    def write_chapter(self, world: dict, volume_outlines: dict, chapter_num: int, chapter_info: dict) -> str:
        """撰写单章内容"""
        logger.info(f"撰写第{chapter_num}章：{chapter_info.get('title', '未知')}")

        prompt = f"""
根据以下设定和章节大纲，撰写小说的完整章节内容：

【世界观设定】
{str(world)[:2000]}

【本章大纲】
章节序号：第{chapter_num}章
章节标题：{chapter_info.get('title', '未知')}
主要事件：{chapter_info.get('summary', '未知')}
出场角色：{', '.join(chapter_info.get('characters', []))}
情绪基调：{chapter_info.get('tone', '未知')}

【写作要求】
1. 正文字数：2000-2500 字
2. 包含：场景描写、人物对话、心理活动、动作描写
3. 保持与世界观的一致性
4. 章节末尾设置悬念或转折
5. 文风：{chapter_info.get('tone', '精彩刺激')}
6. 第三人称叙述

请直接输出正文内容，不需要额外说明。
"""

        response = self.llm.generate(prompt, max_tokens=4096)
        return response

    def generate_full_novel(self, genre: str, title: str, brief: str, total_chapters: int = 2000) -> dict:
        """完整生成流程"""
        logger.info("=" * 60)
        logger.info(f"开始生成长篇小说：{title}")
        logger.info(f"题材：{genre} | 总章节：{total_chapters}")
        logger.info("=" * 60)

        result = {
            "title": title,
            "genre": genre,
            "brief": brief,
            "total_chapters": total_chapters,
            "created_at": datetime.now().isoformat()
        }

        # 1. 生成世界观
        world = self.generate_world_building(genre, title, brief)
        result["world"] = world

        # 2. 生成主线
        main_story = self.generate_main_storyline(world, total_chapters)
        result["main_story"] = main_story

        # 3. 计算卷数和每卷章数
        volumes = main_story.get("volumes", [])
        if not volumes:
            # 默认分 10 卷
            chapters_per_volume = total_chapters // 10
            volumes = [{"num": i+1, "chapters": chapters_per_volume} for i in range(10)]

        logger.info(f"小说分为{len(volumes)}卷")

        # 4. 只生成第 1 卷的详细大纲和前 20 章内容（用于制作前 5 集短剧）
        result["volumes"] = []
        result["chapters"] = []

        # 生成第 1 卷大纲
        vol1_chapters = volumes[0].get("chapters", 200) if volumes else 200
        volume1_outline = self.generate_volume_outlines(world, main_story, 1, vol1_chapters)
        result["volumes"].append({"num": 1, "outline": volume1_outline})

        # 生成前 20 章正文
        chapters_to_write = min(20, len(volume1_outline.get("chapters", [])))
        for i in range(chapters_to_write):
            chapter_info = volume1_outline.get("chapters", [{}])[i]
            chapter_content = self.write_chapter(world, volume1_outline, i+1, chapter_info)
            result["chapters"].append({
                "num": i+1,
                "title": chapter_info.get("title", ""),
                "content": chapter_content
            })

        # 保存结果
        self.save_result(result)

        logger.info("=" * 60)
        logger.info(f"小说生成完成！已保存至：{self.output_dir}")
        logger.info("=" * 60)

        return result

    def save_result(self, result: dict):
        """保存结果为多个文件"""
        title = result["title"]

        # 1. 保存世界观设定
        world_file = self.output_dir / f"{title}_世界观设定.md"
        with open(world_file, 'w', encoding='utf-8') as f:
            f.write(f"# {result['title']} - 世界观设定\n\n")
            f.write(f"**题材**: {result['genre']}\n")
            f.write(f"**生成时间**: {result['created_at']}\n\n")
            f.write("---\n\n")

            world = result.get("world", {})
            if "raw" in world:
                f.write(world["raw"])
            else:
                for key, value in world.items():
                    f.write(f"## {key}\n\n")
                    if isinstance(value, str):
                        f.write(value + "\n\n")
                    else:
                        f.write(str(value) + "\n\n")

        # 2. 保存主线剧情
        story_file = self.output_dir / f"{title}_主线剧情.md"
        with open(story_file, 'w', encoding='utf-8') as f:
            f.write(f"# {result['title']} - 主线剧情大纲\n\n")
            main_story = result.get("main_story", {})
            if "raw" in main_story:
                f.write(main_story["raw"])
            else:
                f.write(str(main_story))

        # 3. 保存第 1 卷大纲
        if result.get("volumes"):
            vol1 = result["volumes"][0]
            vol1_file = self.output_dir / f"{title}_第 1 卷大纲.md"
            with open(vol1_file, 'w', encoding='utf-8') as f:
                f.write(f"# {result['title']} - 第 1 卷详细大纲\n\n")
                outline = vol1.get("outline", {})
                chapters = outline.get("chapters", [])
                for ch in chapters:
                    f.write(f"### 第{ch.get('chapter', 0)}章 {ch.get('title', '')}\n")
                    f.write(f"- 事件：{ch.get('summary', '')}\n")
                    f.write(f"- 角色：{', '.join(ch.get('characters', []))}\n")
                    f.write(f"- 基调：{ch.get('tone', '')}\n\n")

        # 4. 保存前 20 章正文
        novel_file = self.output_dir / f"novel_{title}_正文_第 1-20 章.md"
        with open(novel_file, 'w', encoding='utf-8') as f:
            f.write(f"# {result['title']}\n\n")
            f.write(f"**题材**: {result['genre']}\n")
            f.write(f"**总章节**: {result['total_chapters']}章（计划）\n")
            f.write(f"**当前进度**: 第 1-20 章\n")
            f.write(f"**生成时间**: {result['created_at']}\n\n")
            f.write("---\n\n")

            for chapter in result.get("chapters", []):
                f.write(f"## 第{chapter['num']}章 {chapter['title']}\n\n")
                f.write(chapter['content'])
                f.write("\n\n---\n\n")

        # 5. 保存完整 JSON 数据
        json_file = self.output_dir / f"{title}_data.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            # 简化 JSON，只保留结构化数据
            simplified = {
                "title": result["title"],
                "genre": result["genre"],
                "total_chapters": result["total_chapters"],
                "world_summary": str(result.get("world", {}))[:2000],
                "main_story_summary": str(result.get("main_story", {}))[:2000],
                "volume1_chapters": result.get("volumes", [{}])[0].get("outline", {}).get("chapters", [])[:20],
                "chapter_titles": [{"num": ch["num"], "title": ch["title"]} for ch in result.get("chapters", [])]
            }
            json.dump(simplified, f, ensure_ascii=False, indent=2)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="长篇小说大纲生成器")
    parser.add_argument("--genre", type=str, default="玄幻", help="小说题材")
    parser.add_argument("--title", type=str, required=True, help="小说标题")
    parser.add_argument("--brief", type=str, default="", help="核心创意简述")
    parser.add_argument("--chapters", type=int, default=2000, help="总章节数")
    parser.add_argument("--config", type=str, default="config/project_config.yaml")

    args = parser.parse_args()

    generator = NovelOutlineGenerator(args.config)
    result = generator.generate_full_novel(
        genre=args.genre,
        title=args.title,
        brief=args.brief,
        total_chapters=args.chapters
    )

    print(f"\n✅ 小说大纲生成完成!")
    print(f"   世界观设定：01_novel_generation/output/novels/{args.title}_世界观设定.md")
    print(f"   主线剧情：01_novel_generation/output/novels/{args.title}_主线剧情.md")
    print(f"   第 1 卷大纲：01_novel_generation/output/novels/{args.title}_第 1 卷大纲.md")
    print(f"   前 20 章正文：01_novel_generation/output/novels/novel_{args.title}_正文_第 1-20 章.md")


if __name__ == "__main__":
    main()
