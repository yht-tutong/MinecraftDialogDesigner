# dialog_api.py
# 对话框 CRUD API — 提供加载、保存、转换、验证功能

import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.controller.json_export import (
    export_to_json, import_from_json,
    save_project as _save_project, load_project as _load_project,
)


# ── 文件 I/O ──

def load_dialog_json(filepath: str) -> dict | None:
    """从 JSON 文件加载对话框数据。

    Args:
        filepath: JSON 文件路径。

    Returns:
        dict | None: 解析后的对话框数据，失败返回 None。
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return data
        return None
    except (IOError, OSError, json.JSONDecodeError):
        return None


def save_dialog_json(data: dict, filepath: str) -> bool:
    """保存对话框数据到 JSON 文件。

    Args:
        data: 对话框数据字典。
        filepath: 目标文件路径。

    Returns:
        bool: 成功返回 True。
    """
    try:
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except (IOError, OSError, TypeError):
        return False


# ── 项目文件 ──

def load_project(filepath: str) -> dict | None:
    """加载项目文件（.mcdialog），提取 dialog 数据。

    Args:
        filepath: 项目文件路径。

    Returns:
        dict | None: 内层的 dialog 数据，失败返回 None。
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            project = json.load(f)
        if not isinstance(project, dict):
            return None
        dialog_data = project.get("dialog", {})
        if isinstance(dialog_data, dict):
            return dialog_data
        return None
    except (IOError, OSError, json.JSONDecodeError):
        return None


def save_project(data: dict, filepath: str) -> bool:
    """保存对话框数据为项目文件格式。

    Args:
        data: 对话框数据字典。
        filepath: 目标文件路径。

    Returns:
        bool: 成功返回 True。
    """
    try:
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        project = {"version": 1, "dialog": data}
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(project, f, indent=2, ensure_ascii=False)
        return True
    except (IOError, OSError, TypeError):
        return False


# ── 格式转换 ──

def convert_project_to_dialog(project_path: str, dialog_path: str) -> bool:
    """项目文件转纯 JSON 对话框文件。

    Args:
        project_path: 源项目文件路径。
        dialog_path: 目标对话框 JSON 文件路径。

    Returns:
        bool: 成功返回 True。
    """
    data = load_project(project_path)
    if data is None:
        return False
    return save_dialog_json(data, dialog_path)


def convert_dialog_to_project(dialog_path: str, project_path: str) -> bool:
    """纯 JSON 对话框文件转项目文件。

    Args:
        dialog_path: 源对话框 JSON 文件路径。
        project_path: 目标项目文件路径。

    Returns:
        bool: 成功返回 True。
    """
    data = load_dialog_json(dialog_path)
    if data is None:
        return False
    return save_project(data, project_path)


# ── 验证 ──

_VALID_TYPES = [
    "minecraft:confirmation",
    "minecraft:dialog_list",
    "minecraft:multi_action",
    "minecraft:notice",
    "minecraft:server_links",
    "minecraft:simple_input_form",
    "minecraft:multi_action_input_form",
]

_VALID_AFTER_ACTIONS = ["close", "none", "wait_for_response"]


def validate_dialog(data: dict) -> tuple[bool, list[str]]:
    """验证 dict 是否为有效对话框格式。

    检查项：
    - 顶层必须是 dict
    - 必须包含 type 字段
    - type 必须是已知的对话框类型
    - 如果存在 after_action，必须是合法值
    - 如果存在 inputs，必须是 list
    - 如果存在 actions，必须是 list

    Args:
        data: 待验证的对话框数据。

    Returns:
        tuple[bool, list[str]]: (是否通过, 错误信息列表)。
    """
    errors = []

    if not isinstance(data, dict):
        errors.append("数据必须是字典类型")
        return False, errors

    if "type" not in data:
        errors.append("缺少必填字段 'type'")
        return False, errors

    dtype = data.get("type")
    if dtype not in _VALID_TYPES:
        errors.append(f"未知的对话框类型: '{dtype}'，有效类型: {', '.join(_VALID_TYPES)}")

    if "after_action" in data:
        if data["after_action"] not in _VALID_AFTER_ACTIONS:
            errors.append(f"无效的 after_action: '{data['after_action']}'")

    if "inputs" in data:
        if not isinstance(data["inputs"], list):
            errors.append("'inputs' 字段必须是数组")

    if "actions" in data:
        if not isinstance(data["actions"], list):
            errors.append("'actions' 字段必须是数组")

    if "body" in data:
        body = data["body"]
        if isinstance(body, list):
            for i, elem in enumerate(body):
                if isinstance(elem, dict):
                    etype = elem.get("type", "")
                    if etype not in ("minecraft:plain_message", "plain_message", "minecraft:item", "item", ""):
                        errors.append(f"body[{i}]: 未知的元素类型 '{etype}'")

    return len(errors) == 0, errors