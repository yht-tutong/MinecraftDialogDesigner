# template_api.py
# 模板管理 API — 提供模板列表、查询、生成功能

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.model.templates import get_builtin_templates


def list_templates() -> list[dict]:
    """列出所有内置模板。

    Returns:
        list[dict]: 每个模板包含 id, name, description, category, dialog_type。
    """
    templates = get_builtin_templates()
    return [
        {
            "id": t.id,
            "name": t.name,
            "description": t.description,
            "category": t.category,
            "dialog_type": t.dialog_type,
        }
        for t in templates
    ]


def get_template(template_id: str) -> dict | None:
    """根据 ID 获取模板的 preset_data。

    Args:
        template_id: 模板 ID，如 'welcome_notice'。

    Returns:
        dict | None: 模板的预设数据字典，不存在时返回 None。
    """
    templates = get_builtin_templates()
    for t in templates:
        if t.id == template_id:
            return dict(t.preset_data)  # 深拷贝一层
    return None


def generate_from_template(template_id: str, overrides: dict = None) -> dict | None:
    """从模板生成对话框 dict，支持字段覆盖。

    Args:
        template_id: 模板 ID。
        overrides: 可选，覆盖字段的字典。如 {"title": {"text": "自定义标题"}}。

    Returns:
        dict | None: 生成的对话框数据，模板不存在时返回 None。
    """
    data = get_template(template_id)
    if data is None:
        return None
    if overrides:
        _deep_update(data, overrides)
    return data


def _deep_update(target: dict, source: dict):
    """递归更新字典（浅合并）。"""
    for key, value in source.items():
        if isinstance(value, dict) and isinstance(target.get(key), dict):
            _deep_update(target[key], value)
        elif isinstance(value, list) and isinstance(target.get(key), list):
            # 列表直接替换
            target[key] = value
        else:
            target[key] = value