# cli.py
# Minecraft Dialog Designer CLI 入口 — 命令行接口，不依赖 PyQt5

"""Minecraft Dialog Designer CLI

Usage:
    python cli.py <command> [options]

Commands:
    generate   从模板生成对话框
    convert    格式转换（项目文件 ↔ 纯 JSON）
    batch      批量处理
    validate   验证对话框 JSON

Global Options:
    --quiet    静默模式，仅输出错误
    --version  显示版本号
"""

import argparse
import os
import sys

# 确保项目根目录在 sys.path 中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.api.template_api import list_templates, generate_from_template
from src.api.dialog_api import (
    load_dialog_json, save_dialog_json,
    convert_project_to_dialog, convert_dialog_to_project,
    validate_dialog,
)
from src.api.batch_api import (
    batch_convert_projects,
    batch_generate_from_template,
    batch_validate,
)

__version__ = "1.0.0"

# ANSI 颜色码
_GREEN = "\033[92m"
_RED = "\033[91m"
_YELLOW = "\033[93m"
_BOLD = "\033[1m"
_RESET = "\033[0m"


def _ok(msg: str):
    return f"{_GREEN}{msg}{_RESET}"


def _err(msg: str):
    return f"{_RED}{msg}{_RESET}"


def _warn(msg: str):
    return f"{_YELLOW}{msg}{_RESET}"


def _print_ok(msg: str):
    print(_ok(msg))


def _print_err(msg: str):
    print(_err(msg), file=sys.stderr)


def _print_warn(msg: str):
    print(_warn(msg))


# ── generate 子命令 ──

def cmd_generate(args):
    if args.list_templates:
        templates = list_templates()
        print(f"{_BOLD}内置模板列表:{_RESET}")
        print()
        for t in templates:
            print(f"  {_BOLD}{t['id']}{_RESET} — {t['name']}")
            print(f"    类型: {t['dialog_type']}, 分类: {t['category']}")
            print(f"    描述: {t['description']}")
            print()
        return

    if args.from_file:
        data = load_dialog_json(args.from_file)
        if data is None:
            _print_err(f"错误: 无法读取文件 '{args.from_file}'")
            sys.exit(1)
    elif args.template:
        data = generate_from_template(args.template)
        if data is None:
            _print_err(f"错误: 模板 '{args.template}' 不存在")
            if not args.quiet:
                _print_warn("提示: 使用 --list-templates 查看所有可用模板")
            sys.exit(1)
    else:
        _print_err("错误: 必须指定 --template 或 --from-file")
        sys.exit(1)

    if args.output:
        if save_dialog_json(data, args.output):
            if not args.quiet:
                _print_ok(f"成功: 已生成对话框到 '{args.output}'")
        else:
            _print_err(f"错误: 无法写入文件 '{args.output}'")
            sys.exit(1)
    else:
        # 输出到 stdout
        import json
        print(json.dumps(data, indent=2, ensure_ascii=False))


# ── convert 子命令 ──

def cmd_convert(args):
    if args.from_project and args.to_dialog:
        if convert_project_to_dialog(args.from_project, args.to_dialog):
            if not args.quiet:
                _print_ok(f"成功: 项目文件 '{args.from_project}' → 对话框 JSON '{args.to_dialog}'")
        else:
            _print_err(f"错误: 转换失败，请检查输入文件 '{args.from_project}'")
            sys.exit(1)

    elif args.from_dialog and args.to_project:
        if convert_dialog_to_project(args.from_dialog, args.to_project):
            if not args.quiet:
                _print_ok(f"成功: 对话框 JSON '{args.from_dialog}' → 项目文件 '{args.to_project}'")
        else:
            _print_err(f"错误: 转换失败，请检查输入文件 '{args.from_dialog}'")
            sys.exit(1)

    else:
        _print_err("错误: 必须指定 --from-project + --to-dialog 或 --from-dialog + --to-project")
        sys.exit(1)


# ── batch 子命令 ──

def cmd_batch(args):
    subcmd = args.batch_subcommand

    if subcmd == "convert":
        result = batch_convert_projects(args.input_dir, args.output_dir)
        if not args.quiet:
            _print_ok(f"批量转换完成: 成功 {result['success']}, 失败 {result['failed']}")
            for d in result["details"]:
                if d["status"] == "failed":
                    _print_err(f"  [失败] {d['file']}: {d.get('error', '未知错误')}")

    elif subcmd == "generate":
        result = batch_generate_from_template(args.template, args.count, args.output_dir)
        if not args.quiet:
            _print_ok(f"批量生成完成: 成功 {result['success']}, 失败 {result['failed']}")
            for d in result["details"]:
                if d["status"] == "failed":
                    _print_err(f"  [失败] {d['file']}: {d.get('error', '未知错误')}")

    else:
        _print_err(f"未知的批量子命令: {subcmd}")
        sys.exit(1)


# ── validate 子命令 ──

def cmd_validate(args):
    if args.dir:
        result = batch_validate(args.dir)
        if not args.quiet:
            for d in result["details"]:
                if d["status"] == "success":
                    _print_ok(f"  [通过] {d['file']}")
                else:
                    _print_err(f"  [失败] {d['file']}")
                    for e in d.get("errors", []):
                        _print_err(f"    - {e}")
            print()
            _print_ok(f"验证完成: 通过 {result['success']}, 失败 {result['failed']}")
    elif args.file:
        data = load_dialog_json(args.file)
        if data is None:
            _print_err(f"错误: 无法读取文件 '{args.file}'")
            sys.exit(1)

        passed, errors = validate_dialog(data)
        if passed:
            _print_ok(f"验证通过: {args.file}")
        else:
            _print_err(f"验证失败: {args.file}")
            for e in errors:
                _print_err(f"  - {e}")
            sys.exit(1)
    else:
        _print_err("错误: 必须指定文件路径或 --dir")
        sys.exit(1)


# ── 主入口 ──

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Minecraft Dialog Designer CLI — 命令行对话框生成工具",
        prog="python cli.py",
    )
    parser.add_argument("--quiet", action="store_true", help="静默模式，仅输出错误")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="可用子命令")

    # generate
    gen = subparsers.add_parser("generate", help="从模板生成对话框",
        description="从内置模板或 JSON 文件生成对话框")
    gen.add_argument("--template", "-t", help="模板 ID（如 welcome_notice）")
    gen.add_argument("--from-file", "-f", help="从 JSON 文件读取对话框数据")
    gen.add_argument("--output", "-o", help="输出文件路径（不指定则输出到 stdout）")
    gen.add_argument("--list-templates", "-l", action="store_true", help="列出所有模板")

    # convert
    conv = subparsers.add_parser("convert", help="格式转换（项目文件 ↔ 纯 JSON）",
        description="在项目文件（.mcdialog）和纯 JSON 对话框文件之间转换")
    conv.add_argument("--from-project", help="源项目文件路径")
    conv.add_argument("--to-dialog", help="目标纯 JSON 对话框文件路径")
    conv.add_argument("--from-dialog", help="源纯 JSON 对话框文件路径")
    conv.add_argument("--to-project", help="目标项目文件路径")

    # batch
    bat = subparsers.add_parser("batch", help="批量处理",
        description="对目录中的 JSON 文件批量执行操作")
    bat_sub = bat.add_subparsers(dest="batch_subcommand", help="批量子命令")

    bat_conv = bat_sub.add_parser("convert", help="批量转换项目文件")
    bat_conv.add_argument("--input-dir", "-i", required=True, help="输入目录")
    bat_conv.add_argument("--output-dir", "-o", required=True, help="输出目录")

    bat_gen = bat_sub.add_parser("generate", help="批量从模板生成")
    bat_gen.add_argument("--template", "-t", required=True, help="模板 ID")
    bat_gen.add_argument("--count", "-n", type=int, required=True, help="生成数量")
    bat_gen.add_argument("--output-dir", "-o", required=True, help="输出目录")

    # validate
    val = subparsers.add_parser("validate", help="验证对话框 JSON",
        description="验证 JSON 文件是否符合对话框格式")
    val.add_argument("file", nargs="?", help="要验证的 JSON 文件路径")
    val.add_argument("--dir", "-d", help="验证目录中的所有 JSON 文件")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    if args.command == "generate":
        cmd_generate(args)
    elif args.command == "convert":
        cmd_convert(args)
    elif args.command == "batch":
        cmd_batch(args)
    elif args.command == "validate":
        cmd_validate(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()