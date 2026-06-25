# body_editor.py
# Minecraft Dialog Designer 对话框正文元素编辑器

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QListWidget, QListWidgetItem, QPushButton, QLineEdit,
    QCheckBox, QSpinBox, QComboBox, QLabel, QStackedWidget, QShortcut,
)

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QKeySequence

from ..model.body_elements import PlainMessageElement, ItemElement, BodyElement
from ..model.dialog_base import TextComponent
from .tooltips import (
    TOOLTIP_BODY_WIDTH, TOOLTIP_ITEM_ID, TOOLTIP_ITEM_SHOW_DECORATIONS,
    TOOLTIP_ITEM_SHOW_TOOLTIP, TOOLTIP_ITEM_WIDTH, TOOLTIP_ITEM_HEIGHT,
    TOOLTIP_TITLE_COLOR, TOOLTIP_TITLE_BOLD, TOOLTIP_TITLE_ITALIC,
    TOOLTIP_TITLE_UNDERLINED,
)
from .animation_utils import fade_in
# Minecraft 支持的标准文本颜色
_COLOR_NAMES = [
    "black", "dark_blue", "dark_green", "dark_aqua", "dark_red",
    "dark_purple", "gold", "gray", "dark_gray", "blue",
    "green", "aqua", "red", "light_purple", "yellow", "white",
]


class PlainMessageEditor(QGroupBox):
    """纯文本消息元素属性编辑器。"""

    changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__("纯文本消息属性", parent)
        layout = QFormLayout(self)

        self.text_edit = QLineEdit()
        layout.addRow("文本内容:", self.text_edit)

        self.color_combo = QComboBox()
        self.color_combo.setToolTip(TOOLTIP_TITLE_COLOR)
        self.color_combo.addItems(_COLOR_NAMES)
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

        self.width_spin = QSpinBox()
        self.width_spin.setToolTip(TOOLTIP_BODY_WIDTH)
        self.width_spin.setRange(-1, 500)
        self.width_spin.setSpecialValueText("自动")
        self.width_spin.setValue(-1)
        layout.addRow("宽度 (px):", self.width_spin)

        self.text_edit.textChanged.connect(self.changed)
        self.color_combo.currentTextChanged.connect(self.changed)
        self.bold_cb.stateChanged.connect(self.changed)
        self.italic_cb.stateChanged.connect(self.changed)
        self.underlined_cb.stateChanged.connect(self.changed)
        self.width_spin.valueChanged.connect(self.changed)

    def set_from_element(self, elem: PlainMessageElement):
        """从模型对象填充。"""
        if elem.text is not None:
            if isinstance(elem.text, TextComponent):
                self.text_edit.setText(elem.text.text)
                idx = self.color_combo.findText(elem.text.color)
                if idx >= 0:
                    self.color_combo.setCurrentIndex(idx)
                self.bold_cb.setChecked(elem.text.bold)
                self.italic_cb.setChecked(elem.text.italic)
                self.underlined_cb.setChecked(elem.text.underlined)
            elif isinstance(elem.text, dict):
                self.text_edit.setText(elem.text.get("text", ""))
                idx = self.color_combo.findText(elem.text.get("color", "white"))
                if idx >= 0:
                    self.color_combo.setCurrentIndex(idx)
                self.bold_cb.setChecked(elem.text.get("bold", False))
                self.italic_cb.setChecked(elem.text.get("italic", False))
                self.underlined_cb.setChecked(elem.text.get("underlined", False))

    def to_element(self) -> PlainMessageElement:
        """从控件值构建 PlainMessageElement。"""
        tc = TextComponent(
            text=self.text_edit.text(),
            color=self.color_combo.currentText(),
            bold=self.bold_cb.isChecked(),
            italic=self.italic_cb.isChecked(),
            underlined=self.underlined_cb.isChecked(),
        )
        elem = PlainMessageElement(text=tc)
        w = self.width_spin.value()
        if w > 0:
            elem.width = w
        return elem


class ItemElementEditor(QGroupBox):
    """物品元素属性编辑器。"""

    changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__("物品属性", parent)
        layout = QFormLayout(self)

        self.item_edit = QLineEdit()
        self.item_edit.setToolTip(TOOLTIP_ITEM_ID)
        self.item_edit.setPlaceholderText("minecraft:diamond")
        layout.addRow("物品 ID:", self.item_edit)

        self.desc_edit = QLineEdit()
        self.desc_edit.setPlaceholderText("物品描述（可选）")
        layout.addRow("描述:", self.desc_edit)

        self.decorations_cb = QCheckBox("显示装饰 (show_decorations)")
        self.decorations_cb.setToolTip(TOOLTIP_ITEM_SHOW_DECORATIONS)
        self.decorations_cb.setChecked(True)
        layout.addRow("", self.decorations_cb)

        self.tooltip_cb = QCheckBox("显示提示 (show_tooltip)")
        self.tooltip_cb.setToolTip(TOOLTIP_ITEM_SHOW_TOOLTIP)
        self.tooltip_cb.setChecked(True)
        layout.addRow("", self.tooltip_cb)

        self.width_spin = QSpinBox()
        self.width_spin.setToolTip(TOOLTIP_ITEM_WIDTH)
        self.width_spin.setRange(-1, 500)
        self.width_spin.setSpecialValueText("自动")
        self.width_spin.setValue(-1)
        layout.addRow("宽度 (px):", self.width_spin)

        self.height_spin = QSpinBox()
        self.height_spin.setToolTip(TOOLTIP_ITEM_HEIGHT)
        self.height_spin.setRange(-1, 500)
        self.height_spin.setSpecialValueText("自动")
        self.height_spin.setValue(-1)
        layout.addRow("高度 (px):", self.height_spin)

        self.item_edit.textChanged.connect(self.changed)
        self.desc_edit.textChanged.connect(self.changed)
        self.decorations_cb.stateChanged.connect(self.changed)
        self.tooltip_cb.stateChanged.connect(self.changed)
        self.width_spin.valueChanged.connect(self.changed)
        self.height_spin.valueChanged.connect(self.changed)

    def set_from_element(self, elem: ItemElement):
        """从模型对象填充。"""
        self.item_edit.setText(elem.item)
        if elem.description is not None and hasattr(elem.description, 'text'):
            self.desc_edit.setText(elem.description.text)

    def to_element(self) -> ItemElement:
        """从控件值构建 ItemElement。"""
        desc = None
        if self.desc_edit.text():
            desc = PlainMessageElement(text=TextComponent(text=self.desc_edit.text(), color="white"))
        elem = ItemElement(item=self.item_edit.text() or "minecraft:stone", description=desc)
        w = self.width_spin.value()
        h = self.height_spin.value()
        if w > 0:
            elem.width = w
        if h > 0:
            elem.height = h
        return elem


class BodyEditor(QWidget):
    """对话框正文元素编辑器。

    管理 body 元素列表，支持添加 PlainMessage / Item 两种类型，
    并提供选中后的属性编辑。
    """

    changed = pyqtSignal()
    copy_requested = pyqtSignal(dict)   # 请求复制选中的 body 元素
    paste_requested = pyqtSignal()       # 请求粘贴 body 元素

    def __init__(self, parent=None):
        super().__init__(parent)
        self._locked = False
        layout = QVBoxLayout(self)
        layout.setSpacing(6)
        layout.setContentsMargins(6, 6, 6, 6)

        # ---- 正文元素列表 ----
        elements_group = QGroupBox("正文元素")
        elements_layout = QVBoxLayout(elements_group)
        elements_layout.setSpacing(6)
        elements_layout.setContentsMargins(6, 6, 6, 6)

        toolbar = QHBoxLayout()
        toolbar.setSpacing(6)
        self.add_plain_btn = QPushButton("+ 添加纯文本")
        self.add_item_btn = QPushButton("+ 添加物品")
        toolbar.addWidget(self.add_plain_btn)
        toolbar.addWidget(self.add_item_btn)
        toolbar.addStretch()
        elements_layout.addLayout(toolbar)

        self.list_widget = QListWidget()
        elements_layout.addWidget(self.list_widget)

        layout.addWidget(elements_group)

        # ---- 元素属性编辑区 ----
        props_group = QGroupBox("元素属性")
        props_layout = QVBoxLayout(props_group)
        props_layout.setSpacing(6)
        props_layout.setContentsMargins(6, 6, 6, 6)

        self.prop_stack = QStackedWidget()

        # 页面 0：空提示
        empty_label = QLabel("请选择一个元素进行编辑")
        empty_label.setStyleSheet("color: gray; padding: 16px;")
        self.prop_stack.addWidget(empty_label)

        # 页面 1：PlainMessage
        self.plain_editor = PlainMessageEditor()
        self.plain_editor.changed.connect(self._on_prop_changed)
        self.prop_stack.addWidget(self.plain_editor)

        # 页面 2：Item
        self.item_editor = ItemElementEditor()
        self.item_editor.changed.connect(self._on_prop_changed)
        self.prop_stack.addWidget(self.item_editor)

        props_layout.addWidget(self.prop_stack)
        layout.addWidget(props_group)

        # ---- 信号连接 ----
        self.add_plain_btn.clicked.connect(self._add_plain_message)
        self.add_item_btn.clicked.connect(self._add_item)
        self.list_widget.currentRowChanged.connect(self._on_selection_changed)

        # Delete 键删除选中元素
        QShortcut(QKeySequence.Delete, self.list_widget, self._remove_element)

        # Ctrl+C / Ctrl+V 复制粘贴
        QShortcut(QKeySequence.Copy, self.list_widget, self._copy_selected)
        QShortcut(QKeySequence.Paste, self.list_widget, self._paste_request)

    # ---- 内部数据 ----

    def _elements(self) -> list:
        """获取当前列表中的所有元素。"""
        items = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            items.append(item.data(32))  # type: ignore  # Qt.UserRole
        return items

    def _make_summary(self, elem: BodyElement) -> str:
        """生成元素摘要文本。"""
        if isinstance(elem, PlainMessageElement):
            text = ""
            if elem.text is not None:
                if isinstance(elem.text, TextComponent):
                    text = elem.text.text
                elif isinstance(elem.text, dict):
                    text = elem.text.get("text", "")
            return f"[文本] {text[:30]}"
        elif isinstance(elem, ItemElement):
            return f"[物品] {elem.item}"
        return f"[未知] {elem.type}"

    def _set_item_widget(self, item: QListWidgetItem):
        """为单个列表项创建内联按钮 widget。"""
        elem = item.data(32)
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(4)

        label = QLabel(self._make_summary(elem))
        layout.addWidget(label, 1)

        up_btn = QPushButton("↑")
        up_btn.setFixedSize(24, 24)
        up_btn.clicked.connect(lambda checked=False, it=item: self._move_item_up(it))
        layout.addWidget(up_btn)

        down_btn = QPushButton("↓")
        down_btn.setFixedSize(24, 24)
        down_btn.clicked.connect(lambda checked=False, it=item: self._move_item_down(it))
        layout.addWidget(down_btn)

        del_btn = QPushButton("✕")
        del_btn.setFixedSize(24, 24)
        del_btn.setEnabled(not self._locked)
        del_btn.clicked.connect(lambda checked=False, it=item: self._remove_item(it))
        layout.addWidget(del_btn)

        item.setSizeHint(widget.sizeHint())
        self.list_widget.setItemWidget(item, widget)

    def _refresh_item_widgets(self):
        """遍历所有列表项重新设置 item widget。"""
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            self._set_item_widget(item)

    # ---- 增删改 ----

    def _add_plain_message(self):
        elem = PlainMessageElement(
            text=TextComponent(text="", color="white")
        )
        self._add_element(elem)

    def _add_item(self):
        elem = ItemElement(item="minecraft:stone")
        self._add_element(elem)

    def _add_element(self, elem: BodyElement):
        item = QListWidgetItem(self._make_summary(elem))
        item.setData(32, elem)
        self.list_widget.addItem(item)
        self._set_item_widget(item)
        self.list_widget.setCurrentItem(item)
        self.changed.emit()
        fade_in(self.list_widget, 150)

    def _remove_element(self):
        row = self.list_widget.currentRow()
        if row < 0:
            return
        self.list_widget.takeItem(row)
        self._refresh_item_widgets()
        self.changed.emit()
        fade_in(self.list_widget, 150)

    def _copy_selected(self):
        """复制选中的 body 元素到内部剪贴板。"""
        row = self.list_widget.currentRow()
        if row < 0:
            return
        item = self.list_widget.item(row)
        elem = item.data(32)
        if elem and hasattr(elem, 'to_dict'):
            data = elem.to_dict()
            self.copy_requested.emit(data)

    def _paste_request(self):
        """请求粘贴 body 元素。"""
        self.paste_requested.emit()

    def add_element_from_clipboard(self, elem):
        """从剪贴板添加 body 元素（直接传入模型对象）。"""
        if isinstance(elem, BodyElement):
            self._add_element(elem)

    def _remove_item(self, item: QListWidgetItem):
        """通过引用删除指定项。"""
        row = self.list_widget.row(item)
        if row < 0:
            return
        self.list_widget.takeItem(row)
        self._refresh_item_widgets()
        self.changed.emit()
        fade_in(self.list_widget, 150)

    def _move_up(self):
        row = self.list_widget.currentRow()
        if row <= 0:
            return
        item = self.list_widget.takeItem(row)
        self.list_widget.insertItem(row - 1, item)
        self.list_widget.setCurrentRow(row - 1)
        self._refresh_item_widgets()
        self.changed.emit()
        fade_in(self.list_widget, 150)

    def _move_item_up(self, item: QListWidgetItem):
        """通过引用上移指定项。"""
        row = self.list_widget.row(item)
        if row <= 0:
            return
        item = self.list_widget.takeItem(row)
        self.list_widget.insertItem(row - 1, item)
        self.list_widget.setCurrentRow(row - 1)
        self._refresh_item_widgets()
        self.changed.emit()
        fade_in(self.list_widget, 150)

    def _move_down(self):
        row = self.list_widget.currentRow()
        if row < 0 or row >= self.list_widget.count() - 1:
            return
        item = self.list_widget.takeItem(row)
        self.list_widget.insertItem(row + 1, item)
        self.list_widget.setCurrentRow(row + 1)
        self._refresh_item_widgets()
        self.changed.emit()
        fade_in(self.list_widget, 150)

    def _move_item_down(self, item: QListWidgetItem):
        """通过引用下移指定项。"""
        row = self.list_widget.row(item)
        if row < 0 or row >= self.list_widget.count() - 1:
            return
        item = self.list_widget.takeItem(row)
        self.list_widget.insertItem(row + 1, item)
        self.list_widget.setCurrentRow(row + 1)
        self._refresh_item_widgets()
        self.changed.emit()
        fade_in(self.list_widget, 150)

    # ---- 选择与属性编辑 ----

    def _on_selection_changed(self, row: int):
        if row < 0:
            self.prop_stack.setCurrentIndex(0)
            return

        item = self.list_widget.item(row)
        elem = item.data(32)

        if isinstance(elem, PlainMessageElement):
            self.plain_editor.set_from_element(elem)
            self.prop_stack.setCurrentIndex(1)
        elif isinstance(elem, ItemElement):
            self.item_editor.set_from_element(elem)
            self.prop_stack.setCurrentIndex(2)
        else:
            self.prop_stack.setCurrentIndex(0)

    def _on_prop_changed(self):
        """属性编辑变更时更新列表项和数据。"""
        row = self.list_widget.currentRow()
        if row < 0:
            return

        item = self.list_widget.item(row)
        elem = item.data(32)

        if isinstance(elem, PlainMessageElement):
            new_elem = self.plain_editor.to_element()
        elif isinstance(elem, ItemElement):
            new_elem = self.item_editor.to_element()
        else:
            return

        # 保留原始引用中的额外属性
        new_elem.type = elem.type
        item.setData(32, new_elem)
        item.setText(self._make_summary(new_elem))

        # 更新 item widget 中的标签文本
        widget = self.list_widget.itemWidget(item)
        if widget is not None:
            label = widget.findChild(QLabel)
            if label is not None:
                label.setText(self._make_summary(new_elem))

        self.changed.emit()

    # ---- 批量设置 / 导出 ----

    def set_elements(self, elements: list):
        """用外部元素列表替换当前列表。"""
        self.list_widget.blockSignals(True)
        self.list_widget.clear()
        for elem in elements:
            item = QListWidgetItem(self._make_summary(elem))
            item.setData(32, elem)
            self.list_widget.addItem(item)
        self.list_widget.blockSignals(False)
        self._refresh_item_widgets()
        self.prop_stack.setCurrentIndex(0)

    def get_elements(self) -> list:
        """获取当前编辑后的元素列表。"""
        return self._elements()

    def set_locked(self, locked: bool):
        """锁定/解锁编辑器，禁用/启用添加和删除按钮。"""
        self._locked = locked
        self.add_plain_btn.setEnabled(not locked)
        self.add_item_btn.setEnabled(not locked)
        self._refresh_item_widgets()