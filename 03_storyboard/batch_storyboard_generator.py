"""
批量分镜提示词生成器
从脚本自动生成 AI 视频提示词
"""
import sys
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict

sys.path.insert(0, str(Path(__file__).parent.parent))

from common.llm_client import LLMClient
from common.utils import ensure_dir, load_yaml
from common.logging_config import setup_logger

logger = setup_logger()


class BatchStoryboardGenerator:
    """批量分镜提示词生成器"""

    def __init__(self, config_path: str = "config/project_config.yaml"):
        self.config = load_yaml(config_path) if Path(config_path).exists() else {}
        self.llm = LLMClient(
            provider=self.config.get("llm", {}).get("provider", "claude"),
            model=self.config.get("llm", {}).get("model")
        )
        self.output_dir = Path("03_storyboard/output")
        ensure_dir(str(self.output_dir))

    def parse_script(self, script_file: str) -> Dict:
        """解析脚本文件"""
        with open(script_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取 YAML front matter
        front_matter = {}
        fm_match = re.search(r'---\n(.*?)\n---', content, re.DOTALL)
        if fm_match:
            for line in fm_match.group(1).split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    front_matter[key.strip()] = value.strip().strip('"')

        # 提取所有镜头
        shots = []
        shot_pattern = r'####\s*Shot\s*(\d+\.\d+)\s*\n(.*?)(?=####\s*Shot|\Z)'

        for match in re.finditer(shot_pattern, content, re.DOTALL):
            shot_num = match.group(1)
            shot_content = match.group(2)

            # 提取各个字段
            shot_info = {"num": shot_num}

            # 景别
            angle_match = re.search(r'\*\*景别\*\*:\s*\[(.+?)\]', shot_content)
            if angle_match:
                shot_info["angle"] = angle_match.group(1)

            # 内容
            content_match = re.search(r'\*\*内容\*\*:\s*(.+?)(?=\n\*\*|$)', shot_content, re.DOTALL)
            if content_match:
                shot_info["content"] = content_match.group(1).strip()

            # 对白
            dialog_match = re.search(r'\*\*对白\*\*:\s*"(.+?)"', shot_content)
            if dialog_match:
                shot_info["dialog"] = dialog_match.group(1)

            # AI 提示词
            prompt_match = re.search(r'\*\*AI 视频提示词\*\*:\s*\n```\s*\n(.+?)\n```', shot_content, re.DOTALL)
            if prompt_match:
                shot_info["prompt"] = prompt_match.group(1).strip()
            else:
                # 如果没有提示词，需要生成
                shot_info["need_prompt"] = True

            shots.append(shot_info)

        return {
            "front_matter": front_matter,
            "shots": shots,
            "content": content
        }

    def enhance_prompts(self, script_data: Dict, episode_num: int) -> Dict:
        """为缺少提示词的镜头生成提示词"""
        shots_needing_prompts = [s for s in script_data["shots"] if s.get("need_prompt")]

        if not shots_needing_prompts:
            logger.info("所有镜头已有提示词")
            return script_data

        logger.info(f"为{len(shots_needing_prompts)}个镜头生成/优化提示词")

        # 提取角色信息
        role_section = re.search(r'## 角色列表\s*\n(.*?)(?=\n##|\Z)', script_data["content"], re.DOTALL)
        roles_info = role_section.group(1) if role_section else ""

        for shot in shots_needing_prompts:
            prompt = f"""
请为以下镜头描述生成 AI 视频提示词：

【镜头信息】
景别：{shot.get('angle', '中景')}
内容：{shot.get('content', '')}
对白：{shot.get('dialog', '')}

【角色信息】
{roles_info[:500]}

【剧集信息】
第{episode_num}集

【要求】
生成一段英文提示词，包含：
1. 镜头类型和构图（{shot.get('angle', 'medium shot')}）
2. 场景描述
3. 人物外观和动作
4. 情绪和氛围
5. 光影效果
6. 画质要求（cinematic, 8k, highly detailed）

直接输出英文提示词，不要其他内容。
"""

            new_prompt = self.llm.generate(prompt, max_tokens=512)
            shot["prompt"] = new_prompt.strip()
            shot["enhanced"] = True

        return script_data

    def generate_prompt_collection(self, script_files: List[str]) -> str:
        """生成提示词汇总文档"""
        logger.info(f"生成提示词汇总文档，共{len(script_files)}集")

        output_file = self.output_dir / "AI 视频提示词汇总.md"

        content = "# AI 视频提示词汇总\n\n"
        content += "**生成时间**: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n\n"
        content += "---\n\n"

        all_shots = []

        for script_file in script_files:
            script_data = self.parse_script(script_file)
            episode_num = script_data["front_matter"].get("episode", "1")

            # 增强提示词
            script_data = self.enhance_prompts(script_data, int(episode_num))

            ep_title = script_data["front_matter"].get("title", f"第{episode_num}集")

            content += f"\n## 第{episode_num}集：{ep_title}\n\n"
            content += f"**来源文件**: {Path(script_file).name}\n\n"

            for shot in script_data["shots"]:
                shot_id = f"E{episode_num}_S{shot['num']}"

                content += f"### Shot {shot_id}\n\n"

                if shot.get('angle'):
                    content += f"**景别**: {shot['angle']}\n\n"

                if shot.get('content'):
                    content += f"**内容**: {shot['content']}\n\n"

                if shot.get('prompt'):
                    content += "**AI 提示词**:\n"
                    content += "```\n"
                    content += shot['prompt'] + "\n"
                    content += "```\n\n"

                content += "---\n\n"

                all_shots.append({
                    "id": shot_id,
                    "prompt": shot.get('prompt', ''),
                    "content": shot.get('content', '')
                })

        # 添加快速复制区
        content += "\n# 快速复制区 - 纯提示词列表\n\n"
        for i, shot in enumerate(all_shots, 1):
            content += f"#### {i}. {shot['id']}\n"
            content += f"```\n{shot['prompt']}\n```\n\n"

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"提示词汇总已保存：{output_file}")

        # 同时保存为 JSON 格式，方便程序调用
        json_file = self.output_dir / "prompts_data.json"
        import json
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(all_shots, f, ensure_ascii=False, indent=2)

        return str(output_file)


def main():
    import glob as glob_module

    parser = argparse.ArgumentParser(description="批量分镜提示词生成器")
    parser.add_argument("--scripts", type=str, help="脚本文件路径，支持通配符如 'S01E*.md'")
    parser.add_argument("--dir", type=str, default="02_script_writer/output/scripts", help="脚本目录")
    parser.add_argument("--config", type=str, default="config/project_config.yaml")

    args = parser.parse_args()

    generator = BatchStoryboardGenerator(args.config)

    # 获取脚本文件列表
    if args.scripts:
        script_files = glob_module.glob(args.scripts)
    else:
        script_files = glob_module.glob(f"{args.dir}/S01E*.md")

    if not script_files:
        print("未找到脚本文件!")
        return

    print(f"找到{len(script_files)}个脚本文件")

    output_file = generator.generate_prompt_collection(script_files)

    print(f"\n✅ 提示词汇总生成完成!")
    print(f"   {output_file}")


if __name__ == "__main__":
    main()
