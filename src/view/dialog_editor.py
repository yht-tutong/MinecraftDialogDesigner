# dialog_editor.py
# Minecraft Dialog Designer 通用对话框设置编辑器

from PyQt5.QtWidgets import (
    QWidget, QFormLayout, QHBoxLayout, QVBoxLayout, QGroupBox,
    QLineEdit, QComboBox, QCheckBox, QLabel,
)
from PyQt5.QtCore import pyqtSignal

from ..model.dialog_base import DialogBase, TextComponent
from .tooltips import (
    TOOLTIP_TITLE, TOOLTIP_TITLE_COLOR, TOOLTIP_TITLE_BOLD,
    TOOLTIP_TITLE_ITALIC, TOOLTIP_TITLE_UNDERLINED, TOOLTIP_DIALOG_TYPE,
    TOOLTIP_PAUSE, TOOLTIP_CAN_CLOSE_WITH_ESCAPE, TOOLTIP_AFTER_ACTION,
    TOOLTIP_EXTERNAL_TITLE,
)

# Minecraft 支持的标准文本颜色
COLOR_NAMES = [
    "black", "dark_blue", "dark_green", "dark_aqua", "dark_red",
    "dark_purple", "gold", "gray", "dark_gray", "blue",
    "green", "aqua", "red", "light_purple", "yellow", "white",
]

# 5 种标准对话框类型
DIALOG_TYPES = [
    "minecraft:multi_action",
    "minecraft:confirmation",
    "minecraft:dialog_list",
    "minecraft:notice",
    "minecraft:server_links",
    "minecraft:simple_input_form",
    "minecraft:multi_action_input_form",
]

AFTER_ACTIONS = ["close", "none", "wait_for_response"]


class _TextStyleGroup(QGroupBox):
    """可复用的文本样式组件：文本 + 颜色 + 粗体/斜体/下划线"""

    changed = pyqtSignal()

    def __init__(self, title: str, parent=None):
        super().__init__(title, parent)
        layout = QFormLayout(self)
        layout.setSpacing(6)
        layout.setContentsMargins(6, 6, 6, 6)

        self.text_edit = QLineEdit()
        self.text_edit.setToolTip(TOOLTIP_TITLE)
        layout.addRow("文本:", self.text_edit)

        self.color_combo = QComboBox()
        self.color_combo.setToolTip(TOOLTIP_TITLE_COLOR)
        self.color_combo.addItems(COLOR_NAMES)
        layout.addRow("颜色:", self.color_combo)

        style_layout = QHBoxLayout()
        self.bold_cb = QCheckBox("粗体")
        self.bold_cb.setToolTip(TOOLTIP_TITLE_BOLD)
        self.italic_cb = QCheckBox("斜体")
        self.italic_cb.setToolTip(TOOLTIP_TITLE_ITALIC)
        self.underlined_cb = QCheckBox("下划线")
        self.underlined_cb.setToolTip(TOOLTIP_TITLE_UNDERLINED)
        style_layout.addWidget(self.bold_cb)
        style_layout.addWidget(self.italic_cb)
        style_layout.addWidget(self.underlined_cb)
        layout.addRow("样式:", style_layout)

        self.text_edit.textChanged.connect(self.changed)
        self.color_combo.currentTextChanged.connect(self.changed)
        self.bold_cb.stateChanged.connect(self.changed)
        self.italic_cb.stateChanged.connect(self.changed)
        self.underlined_cb.stateChanged.connect(self.changed)

    def set_from_text_component(self, tc: TextComponent):
        """从 TextComponent 填充控件值。"""
        self.text_edit.setText(tc.text)
        idx = self.color_combo.findText(tc.color)
        if idx >= 0:
            self.color_combo.setCurrentIndex(idx)
        self.bold_cb.setChecked(tc.bold)
        self.italic_cb.setChecked(tc.italic)
        self.underlined_cb.setChecked(tc.underlined)

    def to_text_component(self) -> TextComponent:
        """从当前控件值构建 TextComponent。"""
        return TextComponent(
            text=self.text_edit.text(),
            color=self.color_combo.currentText(),
            bold=self.bold_cb.isChecked(),
            italic=self.italic_cb.isChecked(),
            underlined=self.underlined_cb.isChecked(),
        )


class DialogEditor(QWidget):
    """通用对话框设置编辑器。

    包含标题、类型、游戏暂停/ESC 关闭、关闭后行为、外部标题等字段。
    所有变更通过 changed 信号通知外部。
    """

    changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        # 标题
        self.title_group = _TextStyleGroup("标题")
        layout.addWidget(self.title_group)

        # 对话框类型
        type_group = QGroupBox("对话框类型")
        type_group_layout = QVBoxLayout(type_group)
        type_group_layout.setSpacing(6)
        type_group_layout.setContentsMargins(6, 6, 6, 6)

        type_layout = QFormLayout()
        self.type_combo = QComboBox()
        self.type_combo.setToolTip(TOOLTIP_DIALOG_TYPE)
        self.type_combo.addItems(DIALOG_TYPES)
        type_layout.addRow("对话框类型:", self.type_combo)
        type_group_layout.addLayout(type_layout)

        option_layout = QHBoxLayout()
        self.pause_cb = QCheckBox("暂停游戏 (pause)")
        self.pause_cb.setToolTip(TOOLTIP_PAUSE)
        self.pause_cb.setChecked(True)
        self.escape_cb = QCheckBox("允许 ESC 关闭 (can_close_with_escape)")
        self.escape_cb.setToolTip(TOOLTIP_CAN_CLOSE_WITH_ESCAPE)
        self.escape_cb.setChecked(True)
        option_layout.addWidget(self.pause_cb)
        option_layout.addWidget(self.escape_cb)
        type_group_layout.addLayout(option_layout)

        after_layout = QFormLayout()
        self.after_combo = QComboBox()
        self.after_combo.setToolTip(TOOLTIP_AFTER_ACTION)
        self.after_combo.addItems(AFTER_ACTIONS)
        after_layout.addRow("关闭后行为 (after_action):", self.after_combo)
        type_group_layout.addLayout(after_layout)

        layout.addWidget(type_group)

        # 外部标题
        self.ext_title_group = _TextStyleGroup("外部标题 (external_title, 可选)")
        self.ext_title_group.text_edit.setToolTip(TOOLTIP_EXTERNAL_TITLE)
        layout.addWidget(self.ext_title_group)

        layout.addStretch()

        # 连接信号
        self.title_group.changed.connect(self.changed)
        self.type_combo.currentTextChanged.connect(self.changed)
        self.pause_cb.stateChanged.connect(self.changed)
        self.escape_cb.stateChanged.connect(self.changed)
        self.after_combo.currentTextChanged.connect(self.changed)
        self.ext_title_group.changed.connect(self.changed)

    # ---- 获取器 ----

    def get_title(self) -> TextComponent:
        return self.title_group.to_text_component()

    def get_type(self) -> str:
        return self.type_combo.currentText()

    def get_pause(self) -> bool:
        return self.pause_cb.isChecked()

    def get_can_close_with_escape(self) -> bool:
        return self.escape_cb.isChecked()

    def get_after_action(self) -> str:
        return self.after_combo.currentText()

    def get_external_title(self):
        """如果外部标题有文本则返回 TextComponent，否则返回 None。"""
        tc = self.ext_title_group.to_text_component()
        return tc if tc.text else None

    # ---- 设置器 ----

    def set_from_dialog(self, dialog: DialogBase):
        """从 DialogBase 对象填充所有字段。"""
        if hasattr(dialog, 'title') and dialog.title is not None:
            title = dialog.title
            if isinstance(title, TextComponent):
                self.title_group.set_from_text_component(title)
            elif isinstance(title, dict):
                self.title_group.set_from_text_component(
                    TextComponent(**title)
                )

        if hasattr(dialog, 'type') and dialog.type:
            idx = self.type_combo.findText(dialog.type)
            if idx >= 0:
                self.type_combo.setCurrentIndex(idx)

        self.pause_cb.setChecked(getattr(dialog, 'pause', True))
        self.escape_cb.setChecked(
            getattr(dialog, 'can_close_with_escape', True)
        )

        after = getattr(dialog, 'after_action', 'close')
        idx = self.after_combo.findText(after)
        if idx >= 0:
            self.after_combo.setCurrentIndex(idx)

        ext = getattr(dialog, 'external_title', None)
        if ext is not None:
            if isinstance(ext, TextComponent):
                self.ext_title_group.set_from_text_component(ext)
            elif isinstance(ext, dict):
                self.ext_title_group.set_from_text_component(
                    TextComponent(**ext)
                )