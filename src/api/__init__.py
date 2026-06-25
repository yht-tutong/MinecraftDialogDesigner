# __init__.py
# 纯 Python API 模块 — 不依赖 PyQt5，可被 CLI 和其他脚本导入

from .template_api import list_templates, get_template, generate_from_template
from .dialog_api import (
    load_dialog_json, save_dialog_json,
    load_project, save_project,
    convert_project_to_dialog, convert_dialog_to_project,
    validate_dialog,
)
from .batch_api import (
    batch_convert_projects,
    batch_generate_from_template,
    batch_validate,
)

__all__ = [
    # template
    'list_templates', 'get_template', 'generate_from_template',
    # dialog
    'load_dialog_json', 'save_dialog_json',
    'load_project', 'save_project',
    'convert_project_to_dialog', 'convert_dialog_to_project',
    'validate_dialog',
    # batch
    'batch_convert_projects', 'batch_generate_from_template', 'batch_validate',
]