# batch_api.py
# 批量处理 API — 提供目录遍历、批量转换、批量生成功能

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from .dialog_api import (
    load_project, save_dialog_json,
    load_dialog_json, save_project,
    validate_dialog,
)
from .template_api import generate_from_template


def _ensure_dir(path: str):
    """确保目录存在。"""
    os.makedirs(path, exist_ok=True)


def batch_convert_projects(input_dir: str, output_dir: str) -> dict:
    """批量将项目文件转换为纯 JSON 对话框文件。

    遍历 input_dir 中所有 .json 文件，提取 dialog 数据并输出到 output_dir。

    Args:
        input_dir: 输入目录，包含 .json 项目文件。
        output_dir: 输出目录，生成的纯 JSON 文件保存于此。

    Returns:
        dict: {"success": int, "failed": int, "details": [{"file": str, "status": str, "error": str|None}]}
    """
    result = {"success": 0, "failed": 0, "details": []}
    _ensure_dir(output_dir)

    if not os.path.isdir(input_dir):
        result["details"].append({"file": input_dir, "status": "failed", "error": f"输入目录不存在: {input_dir}"})
        result["failed"] += 1
        return result

    for filename in sorted(os.listdir(input_dir)):
        if not filename.endswith(".json"):
            continue
        src = os.path.join(input_dir, filename)
        dst = os.path.join(output_dir, filename)

        data = load_project(src)
        if data is None:
            result["failed"] += 1
            result["details"].append({"file": filename, "status": "failed", "error": "读取失败"})
            continue

        if save_dialog_json(data, dst):
            result["success"] += 1
            result["details"].append({"file": filename, "status": "success", "error": None})
        else:
            result["failed"] += 1
            result["details"].append({"file": filename, "status": "failed", "error": "写入失败"})

    return result


def batch_generate_from_template(template_id: str, count: int, output_dir: str) -> dict:
    """批量从模板生成对话框文件。

    Args:
        template_id: 模板 ID。
        count: 生成数量。
        output_dir: 输出目录。

    Returns:
        dict: {"success": int, "failed": int, "details": [...]}
    """
    result = {"success": 0, "failed": 0, "details": []}
    _ensure_dir(output_dir)

    template = generate_from_template(template_id)
    if template is None:
        result["failed"] = count
        result["details"].append({"file": template_id, "status": "failed", "error": f"模板不存在: {template_id}"})
        return result

    for i in range(1, count + 1):
        filename = f"{template_id}_{i:03d}.json"
        filepath = os.path.join(output_dir, filename)
        if save_dialog_json(template, filepath):
            result["success"] += 1
            result["details"].append({"file": filename, "status": "success", "error": None})
        else:
            result["failed"] += 1
            result["details"].append({"file": filename, "status": "failed", "error": "写入失败"})

    return result


def batch_validate(input_dir: str) -> dict:
    """批量验证目录中的 JSON 文件。

    Args:
        input_dir: 输入目录，包含 .json 文件。

    Returns:
        dict: {"success": int, "failed": int, "details": [{"file": str, "status": str, "errors": list}]}
    """
    result = {"success": 0, "failed": 0, "details": []}

    if not os.path.isdir(input_dir):
        result["details"].append({"file": input_dir, "status": "failed", "errors": [f"目录不存在: {input_dir}"]})
        result["failed"] += 1
        return result

    for filename in sorted(os.listdir(input_dir)):
        if not filename.endswith(".json"):
            continue
        filepath = os.path.join(input_dir, filename)
        data = load_dialog_json(filepath)
        if data is None:
            result["failed"] += 1
            result["details"].append({"file": filename, "status": "failed", "errors": ["无法读取 JSON"]})
            continue

        passed, errors = validate_dialog(data)
        if passed:
            result["success"] += 1
            result["details"].append({"file": filename, "status": "success", "errors": []})
        else:
            result["failed"] += 1
            result["details"].append({"file": filename, "status": "failed", "errors": errors})

    return result