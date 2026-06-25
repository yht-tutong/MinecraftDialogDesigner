# json_export.py
# Minecraft Dialog Designer JSON 导入/导出函数 - 处理文件 I/O 与项目持久化

import json
from typing import Optional
from ..model import *


def export_to_json(dialog: Optional[DialogBase], filepath: str) -> bool:
    """Export dialog to a JSON file with indent=2.

    Args:
        dialog: The DialogBase instance to export (or None).
        filepath: Destination file path.

    Returns:
        True on success, False on any I/O error.
    """
    try:
        if dialog is None:
            data = {}
        else:
            data = dialog.to_dict()
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except (IOError, OSError, TypeError, ValueError):
        return False


def import_from_json(filepath: str) -> dict:
    """Read a JSON file and return the parsed dict.

    Args:
        filepath: Source file path.

    Returns:
        Parsed dict on success, or an empty dict on I/O or decode error.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return data
        return {}
    except (IOError, OSError, json.JSONDecodeError):
        return {}


def save_project(dialog: Optional[DialogBase], filepath: str) -> bool:
    """Save the dialog as a project file with metadata (version + dialog data).

    The project file wraps the dialog data in a container:
        {
            "version": 1,
            "dialog": <dialog.to_dict() output>
        }

    Args:
        dialog: The DialogBase instance to save (or None).
        filepath: Destination file path.

    Returns:
        True on success, False on any I/O error.
    """
    try:
        project = {
            "version": 1,
            "dialog": dialog.to_dict() if dialog else {},
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(project, f, indent=2, ensure_ascii=False)
        return True
    except (IOError, OSError, TypeError, ValueError):
        return False


def import_dialog_from_json(filepath: str) -> Optional[dict]:
    """读取 JSON 文件并返回解析后的 dict。

    Args:
        filepath: 源文件路径。

    Returns:
        解析成功返回 dict，失败返回 None。
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return data
        return None
    except (IOError, OSError, json.JSONDecodeError):
        return None


def load_project(filepath: str) -> dict:
    """Load a project file and return the dialog dict inside it.

    The expected format is:
        {
            "version": <int>,
            "dialog": { ... }
        }

    Args:
        filepath: Source file path.

    Returns:
        The inner "dialog" dict on success, or an empty dict on error.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            project = json.load(f)
        if not isinstance(project, dict):
            return {}
        dialog_data = project.get("dialog", {})
        if isinstance(dialog_data, dict):
            return dialog_data
        return {}
    except (IOError, OSError, json.JSONDecodeError):
        return {}