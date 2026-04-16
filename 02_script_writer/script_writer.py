"""
单集脚本生成器
为每一集生成详细的视频脚本
"""
import sys
from pathlib import Path
from datetime import datetime
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent))

from common.llm_client import LLMClient
from common.utils import ensure_dir, load_yaml, get_episode_id, parse_episode_id
from common.logging_config import setup_logger

logger = setup_logger()


class ScriptWriter:
    """单集脚本生成器"""

    def __init__(self, config_path: str = "config/project_config.yaml"):
        self.config = load_yaml(config_path)
        self.llm = LLMClient(
            provider=self.config.get("llm", {}).get("provider", "claude"),
            model=self.config.get("llm", {}).get("model")
        )
        self.output_dir = Path(self.config.get("paths", {}).get("scripts", "02_script_writer/output/scripts"))
        ensure_dir(str(self.output_dir))

    def generate_episode_script(self, episode_info: dict, prev_episode_context: str = "") -> str:
        """生成单集详细脚本"""
        ep_id = episode_info.get("episode_id", "S01E01")
        title = episode_info.get("title", "无题")
        summary = episode_info.get("summary", "")
        characters = episode_info.get("characters", "")
        hook = episode_info.get("hook", "")

        logger.info(f"开始生成脚本：{ep_id} {title}")

        prompt = f"""
请为以下短剧生成详细的视频脚本：

【剧集信息】
集数：{ep_id}
标题：{title}
核心事件：{summary}
出场角色：{characters}
悬念点：{hook}

【上一集回顾】
{prev_episode_context[:500] if prev_episode_context else "无"}

【要求】
1. 时长约 90 秒，约 15-25 个镜头
2. 每个镜头包含：
   - 景别（特写/中景/全景等）
   - 画面描述（详细、可视化、适合 AI 视频生成）
   - 对白（如有）
   - 音效
   - 时长（秒）
3. 为每个镜头生成 AI 视频提示词（英文，包含场景、人物、动作、情绪、光影等）
4. 开头设置钩子吸引观众
5. 结尾设置悬念

请按照以下 Markdown 格式输出：
"""

        response = self.llm.generate(prompt, max_tokens=4096)
        return self._format_script(response, episode_info)

    def _format_script(self, response: str, episode_info: dict) -> str:
        """格式化脚本为标准格式"""
        ep_id = episode_info.get("episode_id", "S01E01")
        season, episode = parse_episode_id(ep_id)

        script = f"""---
season: {season}
episode: {episode}
title: "{episode_info.get('title', '无题')}"
duration: "90s"
status: "script_ready"
created_at: "{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
---

# {ep_id}：{episode_info.get('title', '无题')}

## 故事梗概
{episode_info.get('summary', '')}

## 角色列表
{episode_info.get('characters', '')}

## 场景列表
（根据脚本内容自动生成）

## 分镜详情

"""
        # 追加生成的分镜内容
        script += response

        return script

    def parse_outline(self, outline_file: str) -> list:
        """解析分集大纲文件"""
        with open(outline_file, 'r', encoding='utf-8') as f:
            content = f.read()

        episodes = []
        current_ep = {}

        for line in content.split('\n'):
            if line.startswith('## S0'):
                if current_ep:
                    episodes.append(current_ep)
                # 解析：## S01E01：标题
                parts = line.replace('## ', '').split('：')
                current_ep = {
                    "episode_id": parts[0].strip(),
                    "title": parts[1].strip() if len(parts) > 1 else "",
                    "summary": "",
                    "characters": "",
                    "hook": ""
                }
            elif '**核心事件**' in line:
                current_ep['summary'] = line.split('：')[-1].strip()
            elif '**出场角色**' in line:
                current_ep['characters'] = line.split('：')[-1].strip()
            elif '**悬念点**' in line:
                current_ep['hook'] = line.split('：')[-1].strip()

        if current_ep:
            episodes.append(current_ep)

        return episodes

    def generate_from_outline(self, outline_file: str, target_episode: int = None) -> list:
        """从分集大纲生成单集脚本"""
        episodes = self.parse_outline(outline_file)

        if target_episode:
            episodes = [ep for ep in episodes if f"E{target_episode:02d}" in ep.get('episode_id', '')]

        output_files = []
        prev_context = ""

        for ep in episodes:
            script_content = self.generate_episode_script(ep, prev_context)

            # 保存脚本
            ep_id = ep.get('episode_id', 'S01E01')
            title = ep.get('title', 'episode')
            output_file = self.output_dir / f"{ep_id}_{title}.md"

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(script_content)

            logger.info(f"脚本已保存：{output_file}")
            output_files.append(str(output_file))

            # 更新上下文
            prev_context = ep.get('summary', '')

        return output_files


def main():
    parser = argparse.ArgumentParser(description="单集脚本生成器")
    parser.add_argument("--outline", type=str, required=True, help="分集大纲文件路径")
    parser.add_argument("--episode", type=int, default=None, help="目标集数（可选）")
    parser.add_argument("--config", type=str, default="config/project_config.yaml")

    args = parser.parse_args()

    writer = ScriptWriter(args.config)
    output_files = writer.generate_from_outline(args.outline, args.episode)

    print(f"\n✅ 脚本生成完成，共{len(output_files)}集:")
    for f in output_files:
        print(f"  - {f}")


if __name__ == "__main__":
    main()
