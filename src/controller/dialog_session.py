# dialog_session.py
# Minecraft Dialog Designer 会话数据类 - 管理单个打开的对话框状态

from dataclasses import dataclass, field
import os
from ..model.dialog_base import DialogBase


@dataclass
class DialogSession:
    """单个对话框会话，对应一个标签页。

    包含对话框模型、文件路径、修改状态和锁定字段。
    """
    dialog: DialogBase
    file_path: str | None = None
    modified: bool = False
    locked_fields: list = field(default_factory=list)
    _tab_title: str = ""

    def display_title(self) -> str:
        """返回标签页显示标题。

        - 有文件路径时显示文件名
        - 无文件路径时显示"未命名"（由管理器分配序号）
        - 有未保存修改时末尾显示 *
        """
        if self.file_path:
            base = os.path.basename(self.file_path)
        elif self._tab_title:
            base = self._tab_title
        else:
            base = "未命名"
        marker = " *" if self.modified else ""
        return f"{base}{marker}"

    def set_tab_title(self, title: str):
        """设置标签页标题（用于未命名标签页的序号）。"""
        self._tab_title = title