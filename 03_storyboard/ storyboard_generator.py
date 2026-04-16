"""
分镜生成器
将脚本转换为详细的分镜描述和 AI 提示词
"""
import sys
import json
from pathlib import Path
from datetime import datetime
import re

sys.path.insert(0, str(Path(__file__).parent.parent))

from common.llm_client import LLMClient
from common.utils import ensure_dir, load_yaml, get_episode_id
from common.logging_config import setup_logger

logger = setup_logger()


class StoryboardGenerator:
    """分镜生成器"""

    def __init__(self, config_path: str = "config/project_config.yaml"):
        self.config = load_yaml(config_path)
        self.llm = LLMClient(
            provider=self.config.get("llm", {}).get("provider", "claude"),
            model=self.config.get("llm", {}).get("model")
        )
        self.output_dir = Path(self.config.get("paths", {}).get("storyboards", "03_storyboard/output"))
        ensure_dir(str(self.output_dir))

    def parse_script(self, script_file: str) -> dict:
        """解析脚本文件"""
        with open(script_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取 YAML front matter
        front_matter = {}
        if content.startswith('---'):
            match = re.search(r'---\n(.*?)\n---', content, re.DOTALL)
            if match:
                yaml_content = match.group(1)
                for line in yaml_content.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        front_matter[key.strip()] = value.strip().strip('"')

        # 提取分镜信息
        shots = []
        current_shot = {}

        for line in content.split('\n'):
            if 'Shot' in line or '镜头' in line:
                if current_shot:
                    shots.append(current_shot)
                current_shot = {"raw": line}
            elif current_shot:
                if '景别' in line or 'AI 提示词' in line or '时长' in line:
                    key = line.split('：')[0] if ':' in line else line.split(':')[0]
                    value = line.split('：')[-1] if ':' in line else line.split(':')[-1]
                    current_shot[key.strip()] = value.strip()

        if current_shot:
            shots.append(current_shot)

        return {
            "front_matter": front_matter,
            "shots": shots,
            "content": content
        }

    def enhance_shot_prompt(self, shot_info: str, character_refs: dict) -> dict:
        """为单个镜头生成详细的 AI 视频提示词"""
        prompt = f"""
请为以下镜头描述生成详细的 AI 视频生成提示词：

【镜头信息】
{shot_info}

【角色参考】
{json.dumps(character_refs, ensure_ascii=False)}

请生成：
1. 英文提示词（用于 AI 视频工具）：包含场景、人物外观、动作、情绪、光影、构图、镜头运动等
2. 中文描述（用于记录）
3. 建议的生成参数（时长、比例、工具推荐）

按以下 JSON 格式输出：
{{
    "prompt_en": "cinematic shot, ...",
    "prompt_cn": "中文描述...",
    "suggested_tool": "kling",
    "duration": 5,
    "ratio": "16:9",
    "negative_prompt": "blurry, distorted, ..."
}}
"""

        response = self.llm.generate(prompt, max_tokens=1024)
        try:
            return json.loads(response)
        except:
            return {
                "prompt_en": response,
                "prompt_cn": shot_info,
                "suggested_tool": "kling",
                "duration": 5,
                "ratio": "16:9"
            }

    def generate_storyboard(self, script_file: str, character_refs: dict = None) -> str:
        """生成分镜文档"""
        logger.info(f"开始生成分镜：{script_file}")

        script_data = self.parse_script(script_file)
        ep_id = script_data["front_matter"].get("episode_id", get_episode_id(1, 1))

        character_refs = character_refs or {}
        enhanced_shots = []

        # 为每个镜头生成详细提示词
        for i, shot in enumerate(script_data.get("shots", [])):
            logger.info(f"处理镜头 {i + 1}")
            enhanced = self.enhance_shot_prompt(str(shot), character_refs)
            enhanced["shot_index"] = i + 1
            enhanced_shots.append(enhanced)

        # 生成分镜文档
        output_file = self.output_dir / f"{ep_id}_storyboard.md"

        content = f"""---
episode_id: "{ep_id}"
script_source: "{script_file}"
created_at: "{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
total_shots: {len(enhanced_shots)}
---

# 分镜文档：{ep_id}

## 镜头列表

| 序号 | 工具 | 时长 | 比例 | 状态 |
|------|------|------|------|------|
"""

        for shot in enhanced_shots:
            content += f"| {shot['shot_index']} | {shot.get('suggested_tool', 'kling')} | {shot.get('duration', 5)}s | {shot.get('ratio', '16:9')} | pending |\n"

        content += "\n## 详细镜头描述\n\n"

        for shot in enhanced_shots:
            content += f"""
### Shot {shot['shot_index']}

**AI 提示词 (EN)**:
```
{shot.get('prompt_en', '')}
```

**中文描述**:
{shot.get('prompt_cn', '')}

**生成参数**:
- 推荐工具：{shot.get('suggested_tool', 'kling')}
- 时长：{shot.get('duration', 5)}s
- 比例：{shot.get('ratio', '16:9')}
- 负面提示词：{shot.get('negative_prompt', 'blurry, distorted')}

---
"""

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"分镜文档已保存：{output_file}")
        return str(output_file)


def main():
    parser = argparse.ArgumentParser(description="分镜生成器")
    parser.add_argument("--script", type=str, required=True, help="脚本文件路径")
    parser.add_argument("--config", type=str, default="config/project_config.yaml")

    args = parser.parse_args()

    generator = StoryboardGenerator(args.config)
    output_file = generator.generate_storyboard(args.script)

    print(f"\n✅ 分镜文档生成完成：{output_file}")


if __name__ == "__main__":
    main()
