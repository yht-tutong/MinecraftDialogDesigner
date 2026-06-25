# template_dialog.py
# Fluent 风格模板选择对话框

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QLabel, QSplitter,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from qfluentwidgets import (
    Dialog, PrimaryPushButton, PushButton, FluentIcon,
    MessageBox, ListWidget,
)

from src.model.templates import TemplateData, get_builtin_templates
from .cards import TemplateCard


class FluentTemplateDialog(Dialog):
    """Fluent 风格模板选择对话框。

    左侧分类列表，右侧模板卡片（点击选中），底部确认/取消按钮。
    """

    def __init__(self, parent=None):
        super().__init__("从模板新建", "", parent)
        self._templates = get_builtin_templates()
        self._selected_template = None
        self._cards = {}

        self._build_ui()
        self._select_first()

    def _build_ui(self):
        title_label = QLabel("从模板新建")
        title_font = QFont("Segoe UI", 18, QFont.Bold)
        title_label.setFont(title_font)
        self.textLayout.addWidget(title_label)

        desc_label = QLabel("选择一个模板开始创建对话框")
        desc_label.setFont(QFont("Segoe UI", 12))
        desc_label.setStyleSheet("color: #888888;")
        self.textLayout.addWidget(desc_label)

        self.textLayout.addSpacing(12)

        splitter = QSplitter(Qt.Horizontal)

        self._category_list = ListWidget()
        categories = ["🎉 欢迎/通知", "📋 任务/确认", "✏️ 输入/表单", "⚙️ 系统/设置"]
        for cat in categories:
            self._category_list.addItem(cat)
        self._category_list.setFixedWidth(150)
        self._category_list.setFont(QFont("Segoe UI", 13))
        self._category_list.setStyleSheet("""
            QListWidget {
                background-color: #2D2D2D;
                color: #CCCCCC;
                border: 1px solid #3E3E42;
                border-radius: 4px;
            }
            QListWidget::item:selected {
                background-color: #0078D4;
                color: #FFFFFF;
            }
        """)
        self._category_list.currentRowChanged.connect(self._on_category_changed)
        splitter.addWidget(self._category_list)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        cards_widget = QWidget()
        cards_widget.setStyleSheet("background-color: #1E1E1E;")
        cards_layout = QVBoxLayout(cards_widget)
        cards_layout.setSpacing(8)
        cards_layout.setContentsMargins(8, 8, 8, 8)

        for template in self._templates:
            card = TemplateCard(
                template.id, template.name, template.description,
                template.dialog_type,
            )
            card.clicked = self._on_card_clicked
            card.setProperty("category", template.category)
            cards_layout.addWidget(card)
            self._cards[template.id] = card

        cards_layout.addStretch()
        scroll.setWidget(cards_widget)
        splitter.addWidget(scroll)

        splitter.setSizes([150, 450])
        self.textLayout.addWidget(splitter)

        self.textLayout.addSpacing(12)

        self.yesButton.setText("使用模板")
        self.yesButton.setFont(QFont("Segoe UI", 12))
        self.yesButton.setEnabled(False)
        self.cancelButton.setText("取消")
        self.cancelButton.setFont(QFont("Segoe UI", 12))

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
        for tid, card in self._cards.items():
            card.set_selected(tid == template_id)

        for t in self._templates:
            if t.id == template_id:
                self._selected_template = t
                break
        self.yesButton.setEnabled(True)

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