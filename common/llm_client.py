"""
大模型客户端模块
支持 Claude、DeepSeek、OpenAI 等模型
"""
import os
from typing import Optional, List
from pathlib import Path
import yaml

class LLMClient:
    """大模型客户端基类"""

    def __init__(self, provider: str = "bailian", model: Optional[str] = None, base_url: Optional[str] = None):
        self.provider = provider
        self.model = model or self._get_default_model(provider)
        self.base_url = base_url
        self.api_key = self._load_api_key(provider)

    def _get_default_model(self, provider: str) -> str:
        """获取默认模型"""
        models = {
            "bailian": "qwen-plus",
            "claude": "claude-sonnet-4-6",
            "deepseek": "deepseek-chat",
            "openai": "gpt-4-turbo"
        }
        return models.get(provider, "qwen-plus")

    def _load_api_key(self, provider: str) -> str:
        """加载 API 密钥"""
        # 先从环境变量读取
        env_keys = {
            "bailian": "BAILIAN_API_KEY",
            "claude": "ANTHROPIC_API_KEY",
            "deepseek": "DEEPSEEK_API_KEY",
            "openai": "OPENAI_API_KEY"
        }

        key = os.getenv(env_keys.get(provider, ""))
        if key:
            return key

        # 尝试从配置文件读取
        config_path = Path("config/api_keys.yaml")
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

                # 如果是 bailian，直接从 llm 配置读取
                if provider == "bailian":
                    llm_config = config.get("llm", {})
                    if llm_config.get("provider") == "bailian":
                        self.base_url = llm_config.get("base_url", "https://dashscope.aliyuncs.com/v1")
                        self.model = llm_config.get("model", "qwen-plus")
                        return llm_config.get("bailian_api_key", "")

                key_paths = {
                    "claude": ["llm", "claude_api_key"],
                    "deepseek": ["llm", "deepseek_api_key"],
                    "openai": ["llm", "openai_api_key"]
                }
                keys = key_paths.get(provider, [])
                value = config
                for k in keys:
                    value = value.get(k, {}) if isinstance(value, dict) else None
                if value:
                    return value

        raise ValueError(f"未找到 {provider} 的 API 密钥，请配置环境变量或 config/api_keys.yaml")

    def generate(self, prompt: str, system: Optional[str] = None, **kwargs) -> str:
        """生成文本内容"""
        if self.provider == "bailian":
            return self._generate_bailian(prompt, system, **kwargs)
        elif self.provider == "claude":
            return self._generate_claude(prompt, system, **kwargs)
        elif self.provider == "deepseek":
            return self._generate_deepseek(prompt, system, **kwargs)
        else:
            return self._generate_openai(prompt, system, **kwargs)

    def _generate_bailian(self, prompt: str, system: Optional[str], **kwargs) -> str:
        """使用阿里云百炼（通义千问）生成"""
        try:
            from openai import OpenAI
            # 阿里云百炼兼容 OpenAI 接口
            client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url or "https://dashscope.aliyuncs.com/v1"
            )

            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(
                model=self.model or "qwen-plus",
                messages=messages,
                max_tokens=kwargs.get("max_tokens", 8192)
            )
            return response.choices[0].message.content
        except ImportError:
            raise ImportError("请安装 openai 库：pip install openai")

    def _generate_claude(self, prompt: str, system: Optional[str], **kwargs) -> str:
        """使用 Claude 生成"""
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=self.api_key)

            response = client.messages.create(
                model=self.model,
                max_tokens=kwargs.get("max_tokens", 8192),
                system=system or "你是一个专业的创意写作助手。",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except ImportError:
            raise ImportError("请安装 anthropic 库：pip install anthropic")

    def _generate_deepseek(self, prompt: str, system: Optional[str], **kwargs) -> str:
        """使用 DeepSeek 生成"""
        try:
            from openai import OpenAI
            client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.deepseek.com"
            )

            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=kwargs.get("max_tokens", 4096)
            )
            return response.choices[0].message.content
        except ImportError:
            raise ImportError("请安装 openai 库：pip install openai")

    def _generate_openai(self, prompt: str, system: Optional[str], **kwargs) -> str:
        """使用 OpenAI 生成"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)

            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=kwargs.get("max_tokens", 4096)
            )
            return response.choices[0].message.content
        except ImportError:
            raise ImportError("请安装 openai 库：pip install openai")
