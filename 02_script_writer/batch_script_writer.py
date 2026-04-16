"""
批量脚本生成器
从小说自动生成多集短剧脚本
"""
import sys
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict

sys.path.insert(0, str(Path(__file__).parent.parent))

from common.llm_client import LLMClient
from common.utils import ensure_dir, load_yaml, get_episode_id
from common.logging_config import setup_logger

logger = setup_logger()


class BatchScriptWriter:
    """批量脚本生成器"""

    def __init__(self, config_path: str = "config/project_config.yaml"):
        self.config = load_yaml(config_path) if Path(config_path).exists() else {}
        self.llm = LLMClient(
            provider=self.config.get("llm", {}).get("provider", "claude"),
            model=self.config.get("llm", {}).get("model")
        )
        self.output_dir = Path("02_script_writer/output/scripts")
        ensure_dir(str(self.output_dir))

    def extract_novel_content(self, novel_file: str) -> Dict:
        """提取小说内容"""
        with open(novel_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取标题
        title_match = re.search(r'#\s*(.+)', content)
        title = title_match.group(1).strip() if title_match else "未知"

        # 提取章节
        chapters = []
        chapter_pattern = r'##\s*第 (\d+) 章\s*(.+?)\n(.*?)(?=\n##\s*第|\Z)'
        for match in re.finditer(chapter_pattern, content, re.DOTALL):
            chapters.append({
                "num": int(match.group(1)),
                "title": match.group(2).strip(),
                "content": match.group(3).strip()
            })

        return {"title": title, "chapters": chapters}

    def adapt_chapter_to_episode(self, novel_title: str, chapters: List[Dict], episode_num: int) -> Dict:
        """将小说章节改编为单集脚本"""
        # 每集短剧约涵盖 2-4 章小说内容
        start_chapter = (episode_num - 1) * 2 + 1
        end_chapter = min(start_chapter + 1, len(chapters))

        if start_chapter > len(chapters):
            logger.warning(f"第{episode_num}集超出小说范围")
            return None

        episode_chapters = chapters[start_chapter-1:end_chapter]

        logger.info(f"改编第{episode_num}集：使用小说第{start_chapter}-{end_chapter}章")

        # 合并章节内容
        combined_content = "\n\n".join([ch["content"] for ch in episode_chapters])
        chapter_titles = "、".join([f"第{ch['num']}章{ch['title']}" for ch in episode_chapters])

        prompt = f"""
请将以下小说内容改编为一集 90 秒的短剧脚本：

【小说信息】
小说标题：{novel_title}
改编来源：{chapter_titles}

【小说内容】
{combined_content[:6000]}  # 限制长度

【改编要求】
1. 时长约 90 秒，15-25 个镜头
2. 保留核心剧情和高潮
3. 每个镜头包含：
   - 景别（特写/中景/全景等）
   - 画面描述（详细、可视化、适合 AI 视频生成）
   - 对白（精简有力）
   - 音效
   - 时长（秒）
4. 为每个镜头生成 AI 视频提示词（英文，包含场景、人物、动作、情绪、光影、构图）
5. 开头设置钩子吸引观众（前 3 秒）
6. 结尾设置悬念

【输出格式】
请严格按照以下 Markdown 格式输出：

---
season: 1
episode: {episode_num}
title: "本集标题"
duration: "90s"
status: "script_ready"
created_at: "{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
---

# S01E{episode_num:02d}：本集标题

## 故事梗概
（100 字以内）

## 角色列表
- 角色 A：描述
- 角色 B：描述

## 场景列表
| 场号 | 场景 | 时间 | 人物 | 情绪 | 时长 |
|------|------|------|------|------|------|
| 1    | ...  | ...  | ...  | ...  | ...  |

## 分镜详情

### Scene 1 - 场景名

#### Shot 1.1
- **景别**: [特写/中景/全景]
- **内容**: 详细描述
- **对白**: "..."
- **音效**: ...
- **时长**: Xs
- **AI 视频提示词**:
```
英文提示词内容
```
**中文**: 提示词中文翻译

（继续更多镜头...）

## 本集悬念
...

## 制作备注
...
"""

        response = self.llm.generate(prompt, max_tokens=8192)
        return {
            "episode_num": episode_num,
            "script": response,
            "source_chapters": f"{start_chapter}-{end_chapter}"
        }

    def generate_batch(self, novel_file: str, num_episodes: int = 5) -> List[str]:
        """批量生成多集脚本"""
        logger.info(f"开始批量生成{num_episodes}集脚本")

        # 提取小说内容
        novel_data = self.extract_novel_content(novel_file)
        novel_title = novel_data["title"]
        chapters = novel_data["chapters"]

        logger.info(f"小说：{novel_title}，共{len(chapters)}章")

        if len(chapters) < num_episodes * 2:
            logger.warning(f"小说章节不足，最多只能生成{len(chapters)//2}集")
            num_episodes = len(chapters) // 2

        output_files = []

        for i in range(1, num_episodes + 1):
            logger.info(f"\n{'='*40}")
            logger.info(f"生成第{i}集")
            logger.info(f"{'='*40}")

            result = self.adapt_chapter_to_episode(novel_title, chapters, i)

            if result and result["script"]:
                # 提取标题
                title_match = re.search(r'title:\s*"(.+?)"', result["script"])
                ep_title = title_match.group(1) if title_match else f"第{i}集"

                # 保存文件
                output_file = self.output_dir / f"S01E{i:02d}_{ep_title}.md"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(result["script"])

                output_files.append(str(output_file))
                logger.info(f"已保存：{output_file}")

        logger.info(f"\n{'='*40}")
        logger.info(f"批量生成完成！共{len(output_files)}集")
        logger.info(f"{'='*40}")

        return output_files


def main():
    parser = argparse.ArgumentParser(description="批量脚本生成器")
    parser.add_argument("--novel", type=str, required=True, help="小说文件路径")
    parser.add_argument("--episodes", type=int, default=5, help="生成集数")
    parser.add_argument("--config", type=str, default="config/project_config.yaml")

    args = parser.parse_args()

    writer = BatchScriptWriter(args.config)
    output_files = writer.generate_batch(args.novel, args.episodes)

    print(f"\n✅ 脚本批量生成完成!")
    for f in output_files:
        print(f"  - {f}")


if __name__ == "__main__":
    main()
