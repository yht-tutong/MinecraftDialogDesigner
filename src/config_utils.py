# config_utils.py
# 配置文件加载工具 — 首次运行自动创建 config.json 默认配置

import json
import os
import sys

# 项目根目录
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 默认配置
DEFAULT_CONFIG = {
    "app": {
        "name": "Minecraft Dialog Designer",
        "version": "1.1.0",
        "language": "zh_CN",
    },
    "editor": {
        "default_dialog_type": "minecraft:multi_action",
        "auto_save_interval": 300,
        "default_width": 200,
        "default_button_width": 150,
        "default_columns": 2,
    },
    "export": {
        "indent": 2,
        "ensure_ascii": False,
        "default_output_dir": "./output",
        "auto_validate": True,
    },
    "ui": {
        "theme": "dark",
        "font_size": 13,
        "animation_enabled": True,
        "show_tooltips": True,
    },
    "cli": {
        "quiet": False,
        "color_output": True,
    },
    "paths": {
        "template_dir": "",
        "project_dir": "",
        "export_dir": "",
    },
}


def _config_path() -> str:
    """返回 config.json 的完整路径。"""
    return os.path.join(_PROJECT_ROOT, "config.json")


def load_config() -> dict:
    """加载配置文件。如果 config.json 不存在，自动创建默认配置。

    Returns:
        dict: 配置字典。
    """
    path = _config_path()
    if not os.path.exists(path):
        _create_default_config(path)
        return dict(DEFAULT_CONFIG)

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return dict(DEFAULT_CONFIG)
        # 合并默认值，确保缺失的键有默认值
        return _merge_defaults(data)
    except (json.JSONDecodeError, IOError):
        return dict(DEFAULT_CONFIG)


def _merge_defaults(user_config: dict) -> dict:
    """深度合并用户配置与默认配置，确保缺失字段有默认值。"""
    result = {}
    for section, defaults in DEFAULT_CONFIG.items():
        if section in user_config and isinstance(user_config[section], dict):
            result[section] = {**defaults, **user_config[section]}
        else:
            result[section] = dict(defaults)
    return result


def _create_default_config(path: str):
    """创建默认 config.json 文件。"""
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2, ensure_ascii=False)
        print(f"[Config] 已创建默认配置文件: {path}")
        print(f"[Config] 请编辑此文件以自定义设置，或参考 config.json.example")
    except IOError:
        print(f"[Config] 警告: 无法创建配置文件 {path}")


def save_config(config: dict) -> bool:
    """保存配置到 config.json。

    Args:
        config: 配置字典。

    Returns:
        bool: 成功返回 True。
    """
    try:
        with open(_config_path(), "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except IOError:
        return False