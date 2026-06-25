# cards.py
# Fluent 风格可复用卡片组件

from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from qfluentwidgets import FluentIcon, CardWidget, IconWidget


class TemplateCard(CardWidget):
    """Fluent 风格模板选择卡片。

    点击选中，蓝色边框高亮，单选模式。
    """

    clicked = None  # 外部设置的回调: (template_id: str) -> None

    def __init__(self, template_id: str, name: str, description: str,
                 dialog_type: str, parent=None):
        super().__init__(parent)
        self._template_id = template_id
        self._selected = False
        self.setCursor(Qt.PointingHandCursor)
        self.setBorderRadius(8)
        self._build_ui(name, description, dialog_type)
        self.set_selected(False)

    def _build_ui(self, name: str, description: str, dialog_type: str):
        layout = QVBoxLayout(self)
        layout.setSpacing(6)
        layout.setContentsMargins(16, 14, 16, 14)

        title_layout = QHBoxLayout()
        title_layout.setSpacing(8)

        icon = IconWidget(FluentIcon.DOCUMENT)
        icon.setFixedSize(24, 24)
        title_layout.addWidget(icon)

        name_label = QLabel(name)
        name_font = QFont("Segoe UI", 14, QFont.Bold)
        name_label.setFont(name_font)
        title_layout.addWidget(name_label)
        title_layout.addStretch()

        layout.addLayout(title_layout)

        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setFont(QFont("Segoe UI", 12))
        desc_label.setStyleSheet("color: #B0B0B0;")
        layout.addWidget(desc_label)

        type_label = QLabel(f"类型: {dialog_type}")
        type_label.setFont(QFont("Segoe UI", 11))
        type_label.setStyleSheet("color: #0078D4;")
        layout.addWidget(type_label)

    def mousePressEvent(self, event):
        if self.clicked:
            self.clicked(self._template_id)
        super().mousePressEvent(event)

    def set_selected(self, selected: bool):
        self._selected = selected
        if selected:
            self.setStyleSheet("""
                QFrame {
                    border: 2px solid #0078D4;
                    border-radius: 8px;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    border: 1px solid #3E3E42;
                    border-radius: 8px;
                }
            """)

    def is_selected(self) -> bool:
        return self._selected


class DialogInfoCard(CardWidget):
    """对话框信息卡片，用于展示已保存的对话框信息。"""

    def __init__(self, title: str, dialog_type: str, body_count: int,
                 input_count: int, action_count: int, parent=None):
        super().__init__(parent)
        self.setBorderRadius(8)
        self.clickable = True
        self._build_ui(title, dialog_type, body_count, input_count, action_count)

    def _build_ui(self, title: str, dialog_type: str, body_count: int,
                  input_count: int, action_count: int):
        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        layout.setContentsMargins(16, 12, 16, 12)

        name_label = QLabel(title or "未命名")
        name_font = QFont("Segoe UI", 13, QFont.Bold)
        name_label.setFont(name_font)
        layout.addWidget(name_label)

        type_label = QLabel(dialog_type)
        type_label.setFont(QFont("Segoe UI", 11))
        type_label.setStyleSheet("color: #0078D4;")
        layout.addWidget(type_label)

        stats = f"正文 {body_count} | 输入 {input_count} | 操作 {action_count}"
        stats_label = QLabel(stats)
        stats_label.setFont(QFont("Segoe UI", 11))
        stats_label.setStyleSheet("color: #888888;")
        layout.addWidget(stats_label)