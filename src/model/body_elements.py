# body_elements.py
# Minecraft Dialog Designer 对话框正文元素模型 - 定义对话框内容展示元素

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class BodyElement:
    """所有正文元素的抽象基类。"""

    type: str = ""

    def to_dict(self) -> dict:
        raise NotImplementedError("子类必须实现 to_dict 方法")


@dataclass
class PlainMessageElement(BodyElement):
    """纯文本消息元素，用于在对话框中显示文本内容。

    type: "minecraft:plain_message"
    contents: TextComponent 或兼容 to_dict 的对象
    width: 宽度像素
    """
    type: str = "minecraft:plain_message"
    text: Any = None  # TextComponent 实例
    width: int = 200

    def to_dict(self) -> dict:
        result: dict = {"type": self.type}
        if self.text is not None:
            result["contents"] = (
                self.text.to_dict()
                if hasattr(self.text, 'to_dict')
                else self.text
            )
        result["width"] = self.width
        return result


@dataclass
class ItemElement(BodyElement):
    """物品元素，用于在对话框中展示一个 Minecraft 物品。

    type: "minecraft:item"
    item: 物品标识符（如 "minecraft:diamond"）
    count: 物品数量（可选，默认 1）
    description: 可选的描述文本（PlainMessageElement）
    components: 物品组件（如 enchantments 等）
    """
    type: str = "minecraft:item"
    item: str = "minecraft:stone"
    count: int = 1
    description: Any = None  # Optional[PlainMessageElement] - description text next to item
    components: dict = field(default_factory=dict)  # item components (e.g. enchantments)

    def to_dict(self) -> dict:
        result: dict = {"type": self.type, "item": self.item}
        if self.count != 1:
            result["count"] = self.count
        if self.description is not None:
            result["description"] = (
                self.description.to_dict()
                if hasattr(self.description, 'to_dict')
                else self.description
            )
        if self.components:
            result["components"] = self.components
        return result