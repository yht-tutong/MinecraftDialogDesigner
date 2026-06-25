# dialog_types.py
# Minecraft Dialog Designer 具体对话框类型 - 5种标准对话框

from dataclasses import dataclass, field
from typing import Any, List, Optional

from .dialog_base import DialogBase
from .action_models import Action


@dataclass
class ConfirmationDialog(DialogBase):
    """确认对话框，提供"是/否"两个操作按钮。

    type: "minecraft:confirm"
    yes: 点击"是"时执行的动作
    no: 点击"否"时执行的动作
    """
    type: str = "minecraft:confirmation"
    yes: Optional[Action] = None
    no: Optional[Action] = None

    def to_dict(self) -> dict:
        result = super().to_dict()
        if self.yes:
            result["yes"] = (
                self.yes.to_dict()
                if hasattr(self.yes, 'to_dict')
                else self.yes
            )
        if self.no:
            result["no"] = (
                self.no.to_dict()
                if hasattr(self.no, 'to_dict')
                else self.no
            )
        return result


@dataclass
class DialogListDialog(DialogBase):
    """对话框列表对话框，展示多个子对话框供玩家选择。

    type: "minecraft:dialog_list"
    dialogs: 子对话框列表（DialogBase 实例列表）
    columns: 列数（默认 2）
    button_width: 按钮宽度像素（默认 150）
    exit_action: 退出时执行的可选动作
    """
    type: str = "minecraft:dialog_list"
    dialogs: List[DialogBase] = field(default_factory=list)
    columns: int = 2
    button_width: int = 150
    exit_action: Optional[Action] = None

    def to_dict(self) -> dict:
        result = super().to_dict()
        if self.dialogs:
            result["dialogs"] = [
                d.to_dict() if hasattr(d, 'to_dict') else d
                for d in self.dialogs
            ]
        result["columns"] = self.columns
        result["button_width"] = self.button_width
        if self.exit_action:
            result["exit_action"] = (
                self.exit_action.to_dict()
                if hasattr(self.exit_action, 'to_dict')
                else self.exit_action
            )
        return result


@dataclass
class MultiActionDialog(DialogBase):
    """多动作对话框，展示多个操作按钮供玩家选择。

    type: "minecraft:multi_action"
    actions: 动作列表（Action 实例列表）
    columns: 列数（默认 2）
    exit_action: 退出时执行的可选动作
    """
    type: str = "minecraft:multi_action"
    actions: List[Action] = field(default_factory=list)
    columns: int = 2
    exit_action: Optional[Action] = None

    def to_dict(self) -> dict:
        result = super().to_dict()
        if self.actions:
            result["actions"] = [
                a.to_dict() if hasattr(a, 'to_dict') else a
                for a in self.actions
            ]
        result["columns"] = self.columns
        if self.exit_action:
            result["exit_action"] = (
                self.exit_action.to_dict()
                if hasattr(self.exit_action, 'to_dict')
                else self.exit_action
            )
        return result


@dataclass
class NoticeDialog(DialogBase):
    """通知对话框，显示一条信息并提供一个确认动作。

    type: "minecraft:notice"
    action: 点击确认时执行的动作
    """
    type: str = "minecraft:notice"
    action: Optional[Action] = None

    def to_dict(self) -> dict:
        result = super().to_dict()
        if self.action:
            result["action"] = (
                self.action.to_dict()
                if hasattr(self.action, 'to_dict')
                else self.action
            )
        return result


@dataclass
class ServerLinksDialog(DialogBase):
    """服务器链接对话框，展示服务器链接按钮列表。

    type: "minecraft:server_links"
    columns: 列数（默认 2）
    button_width: 按钮宽度像素（默认 150）
    exit_action: 退出时执行的可选动作
    """
    type: str = "minecraft:server_links"
    columns: int = 2
    button_width: int = 150
    exit_action: Optional[Action] = None

    def to_dict(self) -> dict:
        result = super().to_dict()
        result["columns"] = self.columns
        result["button_width"] = self.button_width
        if self.exit_action:
            result["exit_action"] = (
                self.exit_action.to_dict()
                if hasattr(self.exit_action, 'to_dict')
                else self.exit_action
            )
        return result


@dataclass
class SimpleInputFormDialog(DialogBase):
    """简单输入表单 - type: minecraft:simple_input_form"""
    type: str = "minecraft:simple_input_form"
    action: Any = None  # SubmitMethod

    def to_dict(self) -> dict:
        result = super().to_dict()
        if self.action:
            result["action"] = self.action.to_dict() if hasattr(self.action, 'to_dict') else self.action
        return result


@dataclass
class MultiActionInputDialog(DialogBase):
    """多操作输入表单 - type: minecraft:multi_action_input_form"""
    type: str = "minecraft:multi_action_input_form"
    actions: list = field(default_factory=list)
    columns: int = 2

    def to_dict(self) -> dict:
        result = super().to_dict()
        if self.actions:
            result["actions"] = [a.to_dict() if hasattr(a, 'to_dict') else a for a in self.actions]
        result["columns"] = self.columns
        return result