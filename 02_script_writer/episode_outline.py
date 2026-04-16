"""
分集大纲生成器
将小说改编为分集大纲
"""
import sys
from pathlib import Path
from datetime import datetime
import re

sys.path.insert(0, str(Path(__file__).parent.parent))

from common.llm_client import LLMClient
from common.utils import ensure_dir, load_yaml, get_episode_id
from common.logging_config import setup_logger

logger = setup_logger()


class EpisodeOutlineGenerator:
    """分集大纲生成器"""

    def __init__(self, config_path: str = "config/project_config.yaml"):
        self.config = load_yaml(config_path)
        self.llm = LLMClient(
            provider=self.config.get("llm", {}).get("provider", "claude"),
            model=self.config.get("llm", {}).get("model")
        )
        self.output_dir = Path(self.config.get("paths", {}).get("scripts", "02_script_writer/output"))
        ensure_dir(str(self.output_dir))

    def analyze_novel(self, novel_content: str) -> dict:
        """分析小说结构"""
        logger.info("开始分析小说结构")

        prompt = f"""
请分析以下小说内容，提取关键信息：

{novel_content[:8000]}  # 只取前 8000 字

请输出：
1. 故事主线概述（200 字）
2. 主要角色列表
3. 重要情节点（至少 10 个）
4. 故事节奏分析
"""

        response = self.llm.generate(prompt)
        return {"analysis": response}

    def generate_episode_outline(self, novel_content: str, total_episodes: int = 20) -> list:
        """生成分集大纲"""
        logger.info(f"开始生成{total_episodes}集的分集大纲")

        prompt = f"""
请将以下小说内容改编为{total_episodes}集的短剧分集大纲：

{novel_content[:8000]}

每集时长约 90 秒，请为每一集生成：
1. 集数序号（S01E01 格式）
2. 本集标题
3. 核心事件（100 字以内）
4. 出场角色
5. 本集悬念/高潮点
6. 对应小说章节

按照以下格式输出：
S01E01 | 第一集标题 | 核心事件 | 角色 A,B | 悬念点 | 第 1-2 章
...
"""

        response = self.llm.generate(prompt)
        return self._parse_outline(response, total_episodes)

    def _parse_outline(self, response: str, total_episodes: int) -> list:
        """解析大纲文本为结构化数据"""
        episodes = []
        lines = response.strip().split('\n')

        for i, line in enumerate(lines[:total_episodes]):
            parts = line.split('|')
            if len(parts) >= 5:
                episodes.append({
                    "episode_id": parts[0].strip() or get_episode_id(1, i + 1),
                    "title": parts[1].strip(),
                    "summary": parts[2].strip(),
                    "characters": parts[3].strip(),
                    "hook": parts[4].strip(),
                    "novel_chapters": parts[5].strip() if len(parts) > 5 else ""
                })

        return episodes

    def save_outline(self, episodes: list, novel_title: str) -> str:
        """保存分集大纲"""
        output_file = self.output_dir / f"episode_outline_{novel_title}_S01.md"

        content = f"""---
season: 1
total_episodes: {len(episodes)}
novel_source: "{novel_title}"
created_at: "{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
---

# 分集大纲

"""

        for ep in episodes:
            content += f"""
## {ep['episode_id']}：{ep['title']}

- **核心事件**：{ep['summary']}
- **出场角色**：{ep['characters']}
- **悬念点**：{ep['hook']}
- **对应小说**：{ep.get('novel_chapters', 'N/A')}

---
"""

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"分集大纲已保存：{output_file}")
        return str(output_file)

    def generate(self, novel_file: str, total_episodes: int = 20) -> str:
        """主流程：从小说生成分集大纲"""
        # 读取小说
        with open(novel_file, 'r', encoding='utf-8') as f:
            novel_content = f.read()

        # 提取小说标题
        novel_title = Path(novel_file).stem.replace("novel_", "")

        # 分析小说
        self.analyze_novel(novel_content)

        # 生成大纲
        episodes = self.generate_episode_outline(novel_content, total_episodes)

        # 保存
        return self.save_outline(episodes, novel_title)


def main():
    parser = argparse.ArgumentParser(description="分集大纲生成器")
    parser.add_argument("--novel", type=str, required=True, help="小说文件路径")
    parser.add_argument("--episodes", type=int, default=20, help="总集数")
    parser.add_argument("--config", type=str, default="config/project_config.yaml")

    args = parser.parse_args()

    generator = EpisodeOutlineGenerator(args.config)
    output_file = generator.generate(args.novel, args.episodes)

    print(f"\n✅ 分集大纲生成完成：{output_file}")


if __name__ == "__main__":
    import argparse
    main()
