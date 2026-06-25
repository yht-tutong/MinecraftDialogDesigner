# template_dialog.py
# Minecraft Dialog Designer 模板选择对话框

from PyQt5.QtWidgets import (
    QDialog, QSplitter, QListWidget, QListWidgetItem, QScrollArea,
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QDialogButtonBox, QFrame,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from ..model.templates import TemplateData, get_builtin_templates

# 选中/未选中卡片样式
_CARD_NORMAL = """
    QFrame {
        border: 2px solid #5A5A5A;
        border-radius: 6px;
        background-color: #3C3C3C;
        padding: 12px;
    }
    QFrame:hover {
        border-color: #0E639C;
        background-color: #404040;
    }
"""
_CARD_SELECTED = """
    QFrame {
        border: 2px solid #0E639C;
        border-radius: 6px;
        background-color: #1A3A5C;
        padding: 12px;
    }
"""


class TemplateCard(QFrame):
    """可点击选中的模板卡片。"""

    clicked = None  # 外部设置的回调

    def __init__(self, template: TemplateData, parent=None):
        super().__init__(parent)
        self._template = template
        self._selected = False
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setCursor(Qt.PointingHandCursor)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        layout.setContentsMargins(0, 0, 0, 0)

        bold_font = QFont()
        bold_font.setPointSize(14)
        bold_font.setBold(True)

        desc_font = QFont()
        desc_font.setPointSize(12)

        name_label = QLabel(self._template.name)
        name_label.setFont(bold_font)
        layout.addWidget(name_label)

        desc_label = QLabel(self._template.description)
        desc_label.setFont(desc_font)
        desc_label.setStyleSheet("color: gray;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        type_label = QLabel(f"类型: {self._template.dialog_type}")
        type_label.setStyleSheet("color: #1976d2;")
        layout.addWidget(type_label)

    def mousePressEvent(self, event):
        """点击卡片时选中。"""
        if self.clicked:
            self.clicked(self._template.id)
        super().mousePressEvent(event)

    def set_selected(self, selected: bool):
        """设置选中状态并更新样式。"""
        self._selected = selected
        self.setStyleSheet(_CARD_SELECTED if selected else _CARD_NORMAL)

    def is_selected(self) -> bool:
        return self._selected

    @property
    def template(self) -> TemplateData:
        return self._template


class TemplateSelectDialog(QDialog):
    """模板选择对话框。

    左侧分类列表，右侧模板卡片（点击选中），底部确认/取消按钮。
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("从模板新建")
        self.resize(750, 520)

        self._templates = get_builtin_templates()
        self._selected_template = None
        self._cards = {}  # template_id -> TemplateCard

        self._build_ui()
        self._select_first()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # ---- 左右分栏 ----
        splitter = QSplitter(Qt.Horizontal)

        # 左侧：分类列表
        self._category_list = QListWidget()
        self._category_list.addItem("🎉 欢迎/通知")
        self._category_list.addItem("📋 任务/确认")
        self._category_list.addItem("✏️ 输入/表单")
        self._category_list.addItem("⚙️ 系统/设置")
        self._category_list.setFixedWidth(160)
        self._category_list.currentRowChanged.connect(self._on_category_changed)
        splitter.addWidget(self._category_list)

        # 右侧：模板卡片区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self._cards_widget = QWidget()
        self._cards_layout = QVBoxLayout(self._cards_widget)
        self._cards_layout.setSpacing(8)
        self._cards_layout.setContentsMargins(8, 8, 8, 8)
        self._cards_layout.addStretch()

        for template in self._templates:
            card = TemplateCard(template)
            card.clicked = self._on_card_clicked
            card.setProperty("category", template.category)
            self._cards_layout.insertWidget(self._cards_layout.count() - 1, card)
            self._cards[template.id] = card

        scroll.setWidget(self._cards_widget)
        splitter.addWidget(scroll)

        # 设置分割比例
        splitter.setSizes([160, 570])
        layout.addWidget(splitter)

        # ---- 底部按钮 ----
        button_box = QDialogButtonBox()
        self._use_btn = button_box.addButton("使用模板", QDialogButtonBox.AcceptRole)
        self._use_btn.setEnabled(False)
        cancel_btn = button_box.addButton("取消", QDialogButtonBox.RejectRole)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _on_category_changed(self, row: int):
        """左侧分类切换时筛选右侧模板卡片。"""
        category_keys = ["welcome", "quest", "input", "system"]
        if row < 0 or row >= len(category_keys):
            return
        selected_category = category_keys[row]
        for template in self._templates:
            card = self._cards.get(template.id)
            if card:
                card.setVisible(template.category == selected_category)

    def _on_card_clicked(self, template_id: str):
        """点击卡片时选中，取消其他卡片。"""
        # 取消所有卡片选中
        for tid, card in self._cards.items():
            card.set_selected(tid == template_id)

        # 更新选中模板
        for t in self._templates:
            if t.id == template_id:
                self._selected_template = t
                break
        self._use_btn.setEnabled(True)

    def _select_first(self):
        """默认选中第一个分类和第一个可见模板。"""
        self._category_list.setCurrentRow(0)
        self._on_category_changed(0)

        first_visible = None
        for t in self._templates:
            card = self._cards.get(t.id)
            if card and not card.isHidden():
                first_visible = t
                break
        if first_visible:
            self._on_card_clicked(first_visible.id)

    def selected_template(self) -> TemplateData:
        """返回当前选中的 TemplateData 对象。"""
        return self._selected_template