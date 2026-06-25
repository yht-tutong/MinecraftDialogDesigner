# dialog_base.py
# Minecraft Dialog Designer 对话框基础模型 - 通用对话框基类与文本组件

from dataclasses import dataclass, field, asdict
from typing import Any, Optional


@dataclass
class TextComponent:
    """Minecraft 文本组件，用于构建 JSON 格式的文本显示。

    支持基本的文本样式属性：颜色、粗体、斜体、下划线。
    序列化为 Minecraft 文本组件 JSON 字典格式。
    """
    text: str = ""
    color: str = "white"
    bold: bool = False
    italic: bool = False
    underlined: bool = False

    def to_dict(self) -> dict:
        """序列化为 Minecraft 文本组件 JSON 字典。"""
        result: dict = {"text": self.text}
        if self.color and self.color != "white":
            result["color"] = self.color
        if self.bold:
            result["bold"] = True
        if self.italic:
            result["italic"] = True
        if self.underlined:
            result["underlined"] = True
        return result


@dataclass
class DialogBase:
    """对话框基类，包含所有对话框类型的公共字段。

    字段说明：
        title - 对话框标题（TextComponent 或兼容 to_dict 的对象）
        type - 对话框类型 ID（默认 "minecraft:multi_action"）
        body - 对话框正文元素列表（BodyElement 对象列表）
        inputs - 对话框输入控件列表（InputControl 对象列表）
        pause - 打开对话框时是否暂停游戏
        can_close_with_escape - 是否允许按 ESC 关闭
        after_action - 对话框关闭后的行为（"close" 或 "none"）
        external_title - 外部标题（可选 TextComponent）
    """
    title: Any  # TextComponent 或兼容对象
    type: str = "minecraft:multi_action"
    body: list = field(default_factory=list)
    inputs: list = field(default_factory=list)
    pause: bool = True
    can_close_with_escape: bool = True
    after_action: str = "close"
    external_title: Optional[Any] = None  # 可选 TextComponent

    def to_dict(self) -> dict:
        """序列化为 Minecraft 对话框 JSON 字典。"""
        result: dict = {
            "type": self.type,
            "title": self.title.to_dict() if hasattr(self.title, 'to_dict') else self.title,
        }
        if self.body:
            result["body"] = [
                b.to_dict() if hasattr(b, 'to_dict') else b
                for b in self.body
            ]
        if self.inputs:
            result["inputs"] = [
                i.to_dict() if hasattr(i, 'to_dict') else i
                for i in self.inputs
            ]
        result["pause"] = self.pause
        result["can_close_with_escape"] = self.can_close_with_escape
        if self.after_action != "close":
            result["after_action"] = self.after_action
        if self.external_title:
            result["external_title"] = (
                self.external_title.to_dict()
                if hasattr(self.external_title, 'to_dict')
                else self.external_title
            )
        return result