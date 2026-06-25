# submit_methods.py
# Minecraft Dialog Designer SubmitMethod 提交方法模型

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class SubmitMethod:
    """提交方法抽象基类"""
    type: str = ""

    def to_dict(self) -> dict:
        raise NotImplementedError


@dataclass
class CommandTemplateSubmitMethod(SubmitMethod):
    """动态命令模板提交 - type: minecraft:command_template"""
    type: str = "minecraft:command_template"
    template: str = ""

    def to_dict(self) -> dict:
        return {"type": self.type, "template": self.template}


@dataclass
class CustomFormSubmitMethod(SubmitMethod):
    """自定义表单提交 - type: minecraft:custom_form"""
    type: str = "minecraft:custom_form"
    id: str = ""

    def to_dict(self) -> dict:
        return {"type": self.type, "id": self.id}


@dataclass
class CustomTemplateSubmitMethod(SubmitMethod):
    """自定义模板提交 - type: minecraft:custom_template"""
    type: str = "minecraft:custom_template"
    id: str = ""
    additions: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        result = {"type": self.type, "id": self.id}
        if self.additions:
            result["additions"] = self.additions
        return result