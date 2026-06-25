# input_controls.py
# Minecraft Dialog Designer 输入控件模型 - 定义对话框中的用户输入控件

from dataclasses import dataclass, field
from typing import Any, List, Optional


@dataclass
class InputControl:
    """所有输入控件的抽象基类。"""

    type: str = ""

    def to_dict(self) -> dict:
        raise NotImplementedError("子类必须实现 to_dict 方法")


@dataclass
class BooleanInput(InputControl):
    """布尔输入控件，提供是/否切换开关。

    type: "minecraft:boolean"
    label: 控件标签（TextComponent 或兼容 to_dict 的对象）
    default: 默认值
    """
    type: str = "minecraft:boolean"
    label: Any = None  # TextComponent
    initial: bool = False

    def to_dict(self) -> dict:
        result: dict = {"type": self.type}
        if self.label is not None:
            result["label"] = (
                self.label.to_dict()
                if hasattr(self.label, 'to_dict')
                else self.label
            )
        result["initial"] = self.initial
        return result


@dataclass
class NumberRangeInput(InputControl):
    """数值范围输入控件，提供滑块或数值输入。

    type: "minecraft:number_range"
    label: 控件标签（TextComponent 或兼容 to_dict 的对象）
    default: 默认值
    min: 最小值
    max: 最大值
    step: 步进值
    """
    type: str = "minecraft:number_range"
    label: Any = None  # TextComponent
    initial: float = 0.0
    start: float = 0.0
    end: float = 100.0
    step: float = 1.0

    def to_dict(self) -> dict:
        result: dict = {"type": self.type}
        if self.label is not None:
            result["label"] = (
                self.label.to_dict()
                if hasattr(self.label, 'to_dict')
                else self.label
            )
        result["initial"] = self.initial
        result["start"] = self.start
        result["end"] = self.end
        result["step"] = self.step
        return result


@dataclass
class Option:
    """单选项中的单个选项。"""
    label: Any = None  # TextComponent
    value: str = ""

    def to_dict(self) -> dict:
        result: dict = {}
        if self.label is not None:
            result["label"] = (
                self.label.to_dict()
                if hasattr(self.label, 'to_dict')
                else self.label
            )
        if self.value:
            result["value"] = self.value
        return result


@dataclass
class SingleOptionInput(InputControl):
    """单选输入控件，从多个选项中选择一个。

    type: "minecraft:single_option"
    label: 控件标签（TextComponent 或兼容 to_dict 的对象）
    options: 选项列表
    default: 默认选项值
    """
    type: str = "minecraft:single_option"
    label: Any = None  # TextComponent
    options: List[Option] = field(default_factory=list)
    default: str = ""

    def to_dict(self) -> dict:
        result: dict = {"type": self.type}
        if self.label is not None:
            result["label"] = (
                self.label.to_dict()
                if hasattr(self.label, 'to_dict')
                else self.label
            )
        if self.options:
            result["options"] = [o.to_dict() for o in self.options]
        if self.default:
            result["default"] = self.default
        return result


@dataclass
class MultilineConfig:
    """多行文本输入的配置。"""
    enabled: bool = False
    max_lines: int = 5

    def to_dict(self) -> dict:
        result: dict = {"enabled": self.enabled}
        if self.enabled:
            result["max_lines"] = self.max_lines
        return result


@dataclass
class TextInput(InputControl):
    """文本输入控件，提供单行或多行文本输入。

    type: "minecraft:text"
    label: 控件标签（TextComponent 或兼容 to_dict 的对象）
    default: 默认文本
    placeholder: 占位文本
    multiline: 多行配置
    """
    type: str = "minecraft:text"
    label: Any = None  # TextComponent
    initial: str = ""
    placeholder: str = ""
    multiline: MultilineConfig = field(default_factory=MultilineConfig)

    def to_dict(self) -> dict:
        result: dict = {"type": self.type}
        if self.label is not None:
            result["label"] = (
                self.label.to_dict()
                if hasattr(self.label, 'to_dict')
                else self.label
            )
        if self.initial:
            result["initial"] = self.initial
        if self.placeholder:
            result["placeholder"] = self.placeholder
        if self.multiline:
            result["multiline"] = self.multiline.to_dict()
        return result