"""
工具函数模块
"""
import yaml
from pathlib import Path
from typing import Any, Optional

def load_yaml(file_path: str) -> dict:
    """加载 YAML 文件"""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"配置文件不存在：{file_path}")

    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def save_yaml(data: dict, file_path: str):
    """保存 YAML 文件"""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False)

def ensure_dir(dir_path: str):
    """确保目录存在"""
    Path(dir_path).mkdir(parents=True, exist_ok=True)

def get_episode_id(season: int, episode: int) -> str:
    """生成集数 ID，如 S01E01"""
    return f"S{season:02d}E{episode:02d}"

def parse_episode_id(episode_id: str) -> tuple[int, int]:
    """解析集数 ID"""
    # 支持 S01E01 或 S01_E01 格式
    episode_id = episode_id.upper().replace("_", "")
    season = int(episode_id[1:3])
    episode = int(episode_id[4:6])
    return season, episode
