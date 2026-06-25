# action_models.py
# Minecraft Dialog Designer 动作模型层 - 定义对话框交互动作

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, Optional


@dataclass
class Action:
    """所有动作的抽象基类。"""

    def to_dict(self) -> dict:
        raise NotImplementedError("子类必须实现 to_dict 方法")


@dataclass
class StaticAction(Action):
    """静态动作，拥有固定的 action_type 和可选参数字典。

    支持的 action_type 值（完整命名空间 ID）：
        - minecraft:open_url
        - minecraft:run_command
        - minecraft:suggest_command
        - minecraft:change_page
        - minecraft:copy_to_clipboard
        - minecraft:show_dialog
        - minecraft:custom
    """
    action_type: str = "minecraft:run_command"
    params: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        result: dict = {"type": self.action_type}
        if self.params:
            p = dict(self.params)

            # 内联对话框：将 inline_dialog dict 直接嵌套为 dialog 的值
            if self.action_type == "minecraft:show_dialog" and "inline_dialog" in p:
                inline_dialog = p.pop("inline_dialog")
                if isinstance(inline_dialog, dict):
                    p["dialog"] = inline_dialog

            # on_cancel：将字符串命令转换为 ClickEvent 格式
            if "on_cancel" in p:
                cmd = p.pop("on_cancel")
                if isinstance(cmd, str) and cmd:
                    p["on_cancel"] = {"action": "run_command", "command": cmd}
                elif isinstance(cmd, dict):
                    p["on_cancel"] = cmd

            result.update(p)
        return result


@dataclass
class DynamicRunCommandAction(Action):
    """动态运行命令动作，允许在运行时通过命令生成动态行为。"""
    action_type: str = "minecraft:dynamic/run_command"
    command: str = ""

    def to_dict(self) -> dict:
        result: dict = {"type": self.action_type}
        if self.command:
            result["command"] = self.command
        return result


@dataclass
class DynamicCustomAction(Action):
    """动态自定义动作，允许在运行时通过命令定义完全自定义的行为。"""
    action_type: str = "minecraft:dynamic/custom"
    command: str = ""

    def to_dict(self) -> dict:
        result: dict = {"type": self.action_type}
        if self.command:
            result["command"] = self.command
        return result