# input_editor.py
# Minecraft Dialog Designer 输入控件编辑器

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QListWidget, QListWidgetItem, QPushButton, QLineEdit,
    QCheckBox, QSpinBox, QDoubleSpinBox, QComboBox, QLabel,
    QStackedWidget, QDialog, QDialogButtonBox, QInputDialog,
    QMessageBox, QShortcut,
)
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QKeySequence

from ..model.input_controls import (
    BooleanInput, NumberRangeInput, SingleOptionInput,
    TextInput, Option, InputControl, MultilineConfig,
)
from ..model.dialog_base import TextComponent
from .animation_utils import fade_in
from .tooltips import (
    TOOLTIP_INPUT_KEY, TOOLTIP_INPUT_LABEL, TOOLTIP_TITLE_COLOR,
    TOOLTIP_BOOLEAN_INITIAL, TOOLTIP_BOOLEAN_ON_TRUE, TOOLTIP_BOOLEAN_ON_FALSE,
    TOOLTIP_NUMBER_START, TOOLTIP_NUMBER_END, TOOLTIP_NUMBER_STEP,
    TOOLTIP_NUMBER_INITIAL, TOOLTIP_SINGLE_OPTION_WIDTH,
    TOOLTIP_TEXT_MAX_LENGTH, TOOLTIP_TEXT_WIDTH, TOOLTIP_TEXT_MULTILINE,
    TOOLTIP_TEXT_MULTILINE_MAX_LINES, TOOLTIP_TEXT_MULTILINE_HEIGHT,
)

_COLOR_NAMES = [
    "black", "dark_blue", "dark_green", "dark_aqua", "dark_red",
    "dark_purple", "gold", "gray", "dark_gray", "blue",
    "green", "aqua", "red", "light_purple", "yellow", "white",
]


class _CommonInputForm(QGroupBox):
    """输入控件公共属性：key、label 文本、颜色。"""

    changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__("通用属性", parent)
        layout = QFormLayout(self)

        self.key_edit = QLineEdit()
        self.key_edit.setToolTip(TOOLTIP_INPUT_KEY)
        self.key_edit.setPlaceholderText("输入控件唯一标识")
        layout.addRow("Key:", self.key_edit)

        self.label_edit = QLineEdit()
        self.label_edit.setToolTip(TOOLTIP_INPUT_LABEL)
        layout.addRow("标签文本:", self.label_edit)

        self.color_combo = QComboBox()
        self.color_combo.setToolTip(TOOLTIP_TITLE_COLOR)
        self.color_combo.addItems(_COLOR_NAMES)
        layout.addRow("标签颜色:", self.color_combo)

        self.key_edit.textChanged.connect(self.changed)
        self.label_edit.textChanged.connect(self.changed)
        self.color_combo.currentTextChanged.connect(self.changed)


class _BooleanEditor(QGroupBox):
    """布尔输入控件属性编辑器。"""

    changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__("布尔属性", parent)
        layout = QFormLayout(self)

        self.initial_cb = QCheckBox("默认选中")
        self.initial_cb.setToolTip(TOOLTIP_BOOLEAN_INITIAL)
        layout.addRow("初始值:", self.initial_cb)

        self.on_true_edit = QLineEdit()
        self.on_true_edit.setToolTip(TOOLTIP_BOOLEAN_ON_TRUE)
        self.on_true_edit.setPlaceholderText("选中时执行的命令")
        layout.addRow("on_true:", self.on_true_edit)

        self.on_false_edit = QLineEdit()
        self.on_false_edit.setToolTip(TOOLTIP_BOOLEAN_ON_FALSE)
        self.on_false_edit.setPlaceholderText("取消时执行的命令")
        layout.addRow("on_false:", self.on_false_edit)

        self.initial_cb.stateChanged.connect(self.changed)
        self.on_true_edit.textChanged.connect(self.changed)
        self.on_false_edit.textChanged.connect(self.changed)


class _NumberRangeEditor(QGroupBox):
    """数值范围输入控件属性编辑器。"""

    changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__("数值范围属性", parent)
        layout = QFormLayout(self)

        self.start_spin = QDoubleSpinBox()
        self.start_spin.setRange(-1000000, 1000000)
        self.start_spin.setValue(0.0)
        layout.addRow("最小值 (start):", self.start_spin)

        self.end_spin = QDoubleSpinBox()
        self.end_spin.setRange(-1000000, 1000000)
        self.end_spin.setValue(100.0)
        layout.addRow("最大值 (end):", self.end_spin)

        self.step_spin = QDoubleSpinBox()
        self.step_spin.setRange(0.01, 1000000)
        self.step_spin.setValue(1.0)
        layout.addRow("步进 (step):", self.step_spin)

        self.initial_spin = QDoubleSpinBox()
        self.initial_spin.setRange(-1000000, 1000000)
        layout.addRow("初始值 (default):", self.initial_spin)

        self.width_spin = QSpinBox()
        self.width_spin.setRange(-1, 500)
        self.width_spin.setSpecialValueText("自动")
        self.width_spin.setValue(-1)
        layout.addRow("宽度 (px):", self.width_spin)

        self.start_spin.valueChanged.connect(self.changed)
        self.end_spin.valueChanged.connect(self.changed)
        self.step_spin.valueChanged.connect(self.changed)
        self.initial_spin.valueChanged.connect(self.changed)
        self.width_spin.valueChanged.connect(self.changed)


class _OptionEditDialog(QDialog):
    """选项编辑对话框，用于编辑单个选项的 label 和 value。"""

    def __init__(self, label_text="", value="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("编辑选项")
        layout = QFormLayout(self)

        self.label_edit = QLineEdit(label_text)
        layout.addRow("标签:", self.label_edit)

        self.value_edit = QLineEdit(value)
        layout.addRow("值:", self.value_edit)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_label(self):
        return self.label_edit.text()

    def get_value(self):
        return self.value_edit.text()


class _SingleOptionEditor(QGroupBox):
    """单选输入控件属性编辑器。"""

    changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__("单选属性", parent)
        layout = QVBoxLayout(self)

        # 选项列表
        opt_layout = QHBoxLayout()
        opt_layout.addWidget(QLabel("选项列表:"))
        opt_layout.addStretch()
        self.add_opt_btn = QPushButton("+ 添加")
        self.edit_opt_btn = QPushButton("编辑")
        self.remove_opt_btn = QPushButton("− 删除")
        opt_layout.addWidget(self.add_opt_btn)
        opt_layout.addWidget(self.edit_opt_btn)
        opt_layout.addWidget(self.remove_opt_btn)
        layout.addLayout(opt_layout)

        self.option_list = QListWidget()
        layout.addWidget(self.option_list)

        # 宽度
        width_layout = QFormLayout()
        self.width_spin = QSpinBox()
        self.width_spin.setToolTip(TOOLTIP_SINGLE_OPTION_WIDTH)
        self.width_spin.setRange(-1, 500)
        self.width_spin.setSpecialValueText("自动")
        self.width_spin.setValue(-1)
        width_layout.addRow("宽度 (px):", self.width_spin)
        layout.addLayout(width_layout)

        self.add_opt_btn.clicked.connect(self._add_option)
        self.edit_opt_btn.clicked.connect(self._edit_option)
        self.remove_opt_btn.clicked.connect(self._remove_option)
        self.width_spin.valueChanged.connect(self.changed)

    def _add_option(self):
        dlg = _OptionEditDialog(parent=self)
        if dlg.exec_() == QDialog.Accepted:
            lbl = dlg.get_label()
            val = dlg.get_value()
            opt = Option(
                label=TextComponent(text=lbl, color="white"),
                value=val,
            )
            item = QListWidgetItem(f"{lbl} ({val})" if val else lbl)
            item.setData(32, opt)
            self.option_list.addItem(item)
            self.changed.emit()

    def _edit_option(self):
        row = self.option_list.currentRow()
        if row < 0:
            return
        item = self.option_list.item(row)
        opt: Option = item.data(32)
        lbl = opt.label.text if isinstance(opt.label, TextComponent) else ""
        dlg = _OptionEditDialog(label_text=lbl, value=opt.value, parent=self)
        if dlg.exec_() == QDialog.Accepted:
            new_lbl = dlg.get_label()
            new_val = dlg.get_value()
            opt.label = TextComponent(text=new_lbl, color="white")
            opt.value = new_val
            item.setText(f"{new_lbl} ({new_val})" if new_val else new_lbl)
            self.changed.emit()

    def _remove_option(self):
        row = self.option_list.currentRow()
        if row < 0:
            return
        self.option_list.takeItem(row)
        self.changed.emit()

    def set_options(self, options: list):
        self.option_list.blockSignals(True)
        self.option_list.clear()
        for opt in options:
            lbl = opt.label.text if isinstance(opt.label, TextComponent) else ""
            item = QListWidgetItem(f"{lbl} ({opt.value})" if opt.value else lbl)
            item.setData(32, opt)
            self.option_list.addItem(item)
        self.option_list.blockSignals(False)

    def get_options(self) -> list:
        opts = []
        for i in range(self.option_list.count()):
            opts.append(self.option_list.item(i).data(32))
        return opts


class _TextEditor(QGroupBox):
    """文本输入控件属性编辑器。"""

    changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__("文本输入属性", parent)
        layout = QFormLayout(self)

        self.initial_edit = QLineEdit()
        layout.addRow("初始文本 (default):", self.initial_edit)

        self.placeholder_edit = QLineEdit()
        layout.addRow("占位文本:", self.placeholder_edit)

        self.max_length_spin = QSpinBox()
        self.max_length_spin.setToolTip(TOOLTIP_TEXT_MAX_LENGTH)
        self.max_length_spin.setRange(0, 32767)
        self.max_length_spin.setSpecialValueText("不限")
        self.max_length_spin.setValue(0)
        layout.addRow("最大长度:", self.max_length_spin)

        self.width_spin = QSpinBox()
        self.width_spin.setToolTip(TOOLTIP_TEXT_WIDTH)
        self.width_spin.setRange(-1, 500)
        self.width_spin.setSpecialValueText("自动")
        self.width_spin.setValue(-1)
        layout.addRow("宽度 (px):", self.width_spin)

        self.multiline_cb = QCheckBox("启用多行")
        self.multiline_cb.setToolTip(TOOLTIP_TEXT_MULTILINE)
        layout.addRow("", self.multiline_cb)

        self.max_lines_spin = QSpinBox()
        self.max_lines_spin.setToolTip(TOOLTIP_TEXT_MULTILINE_MAX_LINES)
        self.max_lines_spin.setRange(1, 100)
        self.max_lines_spin.setValue(5)
        layout.addRow("最大行数:", self.max_lines_spin)

        self.height_spin = QSpinBox()
        self.height_spin.setToolTip(TOOLTIP_TEXT_MULTILINE_HEIGHT)
        self.height_spin.setRange(-1, 500)
        self.height_spin.setSpecialValueText("自动")
        self.height_spin.setValue(-1)
        layout.addRow("高度 (px):", self.height_spin)

        self.initial_edit.textChanged.connect(self.changed)
        self.placeholder_edit.textChanged.connect(self.changed)
        self.max_length_spin.valueChanged.connect(self.changed)
        self.width_spin.valueChanged.connect(self.changed)
        self.multiline_cb.stateChanged.connect(self.changed)
        self.max_lines_spin.valueChanged.connect(self.changed)
        self.height_spin.valueChanged.connect(self.changed)


class InputEditor(QWidget):
    """输入控件编辑器。

    管理 inputs 列表，支持 4 种输入类型：
    Boolean, NumberRange, SingleOption, Text。
    """

    changed = pyqtSignal()
    copy_requested = pyqtSignal(dict)   # 请求复制选中的 input 控件
    paste_requested = pyqtSignal()       # 请求粘贴 input 控件

    # 输入类型到索引的映射
    TYPE_INDEX = {
        "minecraft:boolean": 0,
        "minecraft:number_range": 1,
        "minecraft:single_option": 2,
        "minecraft:text": 3,
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setSpacing(6)
        layout.setContentsMargins(6, 6, 6, 6)

        input_group = QGroupBox("输入控件")
        input_group_layout = QVBoxLayout(input_group)
        input_group_layout.setSpacing(6)
        input_group_layout.setContentsMargins(6, 6, 6, 6)

        # ---- 列表工具栏 ----
        toolbar = QHBoxLayout()
        toolbar.setSpacing(6)
        self.add_btn = QPushButton("+ 添加输入")

        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "minecraft:boolean",
            "minecraft:number_range",
            "minecraft:single_option",
            "minecraft:text",
        ])

        toolbar.addWidget(QLabel("类型:"))
        toolbar.addWidget(self.type_combo)
        toolbar.addWidget(self.add_btn)
        toolbar.addStretch()
        input_group_layout.addLayout(toolbar)

        # ---- 列表 ----
        self.list_widget = QListWidget()
        input_group_layout.addWidget(self.list_widget)

        # ---- 属性编辑区 (QStackedWidget) ----
        self.prop_stack = QStackedWidget()

        # 页面 0：空提示
        empty_label = QLabel("请选择一个输入控件进行编辑")
        empty_label.setStyleSheet("color: gray; padding: 16px;")
        self.prop_stack.addWidget(empty_label)

        # 页面 1：Boolean
        self.boolean_widget = QWidget()
        bw_layout = QVBoxLayout(self.boolean_widget)
        self.bool_common = _CommonInputForm()
        bw_layout.addWidget(self.bool_common)
        self.bool_editor = _BooleanEditor()
        bw_layout.addWidget(self.bool_editor)
        bw_layout.addStretch()
        self.prop_stack.addWidget(self.boolean_widget)

        # 页面 2：NumberRange
        self.number_widget = QWidget()
        nw_layout = QVBoxLayout(self.number_widget)
        self.num_common = _CommonInputForm()
        nw_layout.addWidget(self.num_common)
        self.num_editor = _NumberRangeEditor()
        nw_layout.addWidget(self.num_editor)
        nw_layout.addStretch()
        self.prop_stack.addWidget(self.number_widget)

        # 页面 3：SingleOption
        self.option_widget = QWidget()
        ow_layout = QVBoxLayout(self.option_widget)
        self.opt_common = _CommonInputForm()
        ow_layout.addWidget(self.opt_common)
        self.opt_editor = _SingleOptionEditor()
        ow_layout.addWidget(self.opt_editor)
        ow_layout.addStretch()
        self.prop_stack.addWidget(self.option_widget)

        # 页面 4：Text
        self.text_widget = QWidget()
        tw_layout = QVBoxLayout(self.text_widget)
        self.txt_common = _CommonInputForm()
        tw_layout.addWidget(self.txt_common)
        self.txt_editor = _TextEditor()
        tw_layout.addWidget(self.txt_editor)
        tw_layout.addStretch()
        self.prop_stack.addWidget(self.text_widget)

        input_group_layout.addWidget(self.prop_stack)
        layout.addWidget(input_group)

        # ---- 信号连接 ----
        self.add_btn.clicked.connect(self._add_input)
        self.list_widget.currentRowChanged.connect(self._on_selection_changed)

        # Delete 键删除选中输入控件
        QShortcut(QKeySequence.Delete, self.list_widget, self._remove_input)

        # Ctrl+C / Ctrl+V 复制粘贴
        QShortcut(QKeySequence.Copy, self.list_widget, self._copy_selected)
        QShortcut(QKeySequence.Paste, self.list_widget, self._paste_request)

        # 连接所有子编辑器的 changed 信号
        for w in [self.bool_common, self.bool_editor,
                  self.num_common, self.num_editor,
                  self.opt_common, self.opt_editor,
                  self.txt_common, self.txt_editor]:
            if hasattr(w, 'changed'):
                w.changed.connect(self._on_prop_changed)

    # ---- 摘要 ----

    def _make_summary(self, ctrl: InputControl) -> str:
        """生成输入控件摘要。"""
        label = ""
        if hasattr(ctrl, 'label') and ctrl.label is not None:
            if isinstance(ctrl.label, TextComponent):
                label = ctrl.label.text
            elif isinstance(ctrl.label, dict):
                label = ctrl.label.get("text", "")

        type_name = ctrl.type.split(":")[-1] if ":" in ctrl.type else ctrl.type
        return f"[{type_name}] {label[:30]}"

    # ---- 列表项内联按钮 ----

    def _refresh_item_widgets(self):
        """为每个列表项设置内联操作按钮（上移/下移/删除）。"""
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            ctrl = item.data(32)

            widget = QWidget()
            layout = QHBoxLayout(widget)
            layout.setContentsMargins(4, 2, 4, 2)
            layout.setSpacing(2)

            summary = QLabel(self._make_summary(ctrl))
            layout.addWidget(summary)
            layout.addStretch()

            up_btn = QPushButton("↑")
            up_btn.setFixedSize(24, 24)
            up_btn.clicked.connect(lambda checked, it=item: self._move_up(it))
            layout.addWidget(up_btn)

            down_btn = QPushButton("↓")
            down_btn.setFixedSize(24, 24)
            down_btn.clicked.connect(lambda checked, it=item: self._move_down(it))
            layout.addWidget(down_btn)

            remove_btn = QPushButton("✕")
            remove_btn.setFixedSize(24, 24)
            remove_btn.clicked.connect(lambda checked, it=item: self._remove_input(it))
            layout.addWidget(remove_btn)

            item.setSizeHint(widget.sizeHint())
            self.list_widget.setItemWidget(item, widget)

    # ---- 增删改 ----

    def _add_input(self):
        """根据当前 type_combo 选择创建对应类型的输入控件。"""
        typ = self.type_combo.currentText()
        if typ == "minecraft:boolean":
            ctrl = BooleanInput(label=TextComponent(text="", color="white"))
        elif typ == "minecraft:number_range":
            ctrl = NumberRangeInput(label=TextComponent(text="", color="white"))
        elif typ == "minecraft:single_option":
            ctrl = SingleOptionInput(label=TextComponent(text="", color="white"))
        elif typ == "minecraft:text":
            ctrl = TextInput(label=TextComponent(text="", color="white"))
        else:
            return

        item = QListWidgetItem(self._make_summary(ctrl))
        item.setData(32, ctrl)
        self.list_widget.addItem(item)
        self.list_widget.setCurrentItem(item)
        self._refresh_item_widgets()
        self.changed.emit()
        fade_in(self.list_widget, 150)

    def _remove_input(self, item=None):
        if item is not None:
            row = self.list_widget.row(item)
        else:
            row = self.list_widget.currentRow()
        if row < 0:
            return
        self.list_widget.takeItem(row)
        self._refresh_item_widgets()
        self.changed.emit()
        fade_in(self.list_widget, 150)

    def _copy_selected(self):
        """复制选中的 input 控件到内部剪贴板。"""
        row = self.list_widget.currentRow()
        if row < 0:
            return
        item = self.list_widget.item(row)
        ctrl = item.data(32)
        if ctrl and hasattr(ctrl, 'to_dict'):
            data = ctrl.to_dict()
            self.copy_requested.emit(data)

    def _paste_request(self):
        """请求粘贴 input 控件。"""
        self.paste_requested.emit()

    def add_input_from_clipboard(self, ctrl):
        """从剪贴板添加 input 控件（直接传入模型对象）。"""
        if isinstance(ctrl, InputControl):
            item = QListWidgetItem(self._make_summary(ctrl))
            item.setData(32, ctrl)
            self.list_widget.addItem(item)
            self.list_widget.setCurrentItem(item)
            self._refresh_item_widgets()
            self.changed.emit()
            fade_in(self.list_widget, 150)

    def _move_up(self, item=None):
        if item is not None:
            row = self.list_widget.row(item)
        else:
            row = self.list_widget.currentRow()
        if row <= 0:
            return
        taken = self.list_widget.takeItem(row)
        self.list_widget.insertItem(row - 1, taken)
        self.list_widget.setCurrentRow(row - 1)
        self._refresh_item_widgets()
        self.changed.emit()
        fade_in(self.list_widget, 150)

    def _move_down(self, item=None):
        if item is not None:
            row = self.list_widget.row(item)
        else:
            row = self.list_widget.currentRow()
        if row < 0 or row >= self.list_widget.count() - 1:
            return
        taken = self.list_widget.takeItem(row)
        self.list_widget.insertItem(row + 1, taken)
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
        ctrl = item.data(32)

        # 根据类型切换页面
        if isinstance(ctrl, BooleanInput):
            self._populate_common(self.bool_common, ctrl)
            self.bool_editor.initial_cb.setChecked(ctrl.initial)
            self.prop_stack.setCurrentIndex(1)
        elif isinstance(ctrl, NumberRangeInput):
            self._populate_common(self.num_common, ctrl)
            self.num_editor.start_spin.setValue(ctrl.start)
            self.num_editor.end_spin.setValue(ctrl.end)
            self.num_editor.step_spin.setValue(ctrl.step)
            self.num_editor.initial_spin.setValue(ctrl.initial)
            self.prop_stack.setCurrentIndex(2)
        elif isinstance(ctrl, SingleOptionInput):
            self._populate_common(self.opt_common, ctrl)
            self.opt_editor.set_options(ctrl.options)
            self.prop_stack.setCurrentIndex(3)
        elif isinstance(ctrl, TextInput):
            self._populate_common(self.txt_common, ctrl)
            self.txt_editor.initial_edit.setText(ctrl.initial)
            self.txt_editor.placeholder_edit.setText(ctrl.placeholder)
            if ctrl.multiline:
                self.txt_editor.multiline_cb.setChecked(ctrl.multiline.enabled)
                self.txt_editor.max_lines_spin.setValue(ctrl.multiline.max_lines)
            self.prop_stack.setCurrentIndex(4)
        else:
            self.prop_stack.setCurrentIndex(0)

    def _populate_common(self, form: _CommonInputForm, ctrl: InputControl):
        """填充公共表单。"""
        label = ""
        color = "white"
        if hasattr(ctrl, 'label') and ctrl.label is not None:
            if isinstance(ctrl.label, TextComponent):
                label = ctrl.label.text
                color = ctrl.label.color
            elif isinstance(ctrl.label, dict):
                label = ctrl.label.get("text", "")
                color = ctrl.label.get("color", "white")

        form.label_edit.setText(label)
        idx = form.color_combo.findText(color)
        if idx >= 0:
            form.color_combo.setCurrentIndex(idx)
        # key 保留在控件的自定义属性中

    def _on_prop_changed(self):
        """属性变更时更新列表项。"""
        row = self.list_widget.currentRow()
        if row < 0:
            return

        item = self.list_widget.item(row)
        old_ctrl = item.data(32)

        if isinstance(old_ctrl, BooleanInput):
            tc = TextComponent(
                text=self.bool_common.label_edit.text(),
                color=self.bool_common.color_combo.currentText(),
            )
            new_ctrl = BooleanInput(
                label=tc,
                initial=self.bool_editor.initial_cb.isChecked(),
            )
        elif isinstance(old_ctrl, NumberRangeInput):
            tc = TextComponent(
                text=self.num_common.label_edit.text(),
                color=self.num_common.color_combo.currentText(),
            )
            new_ctrl = NumberRangeInput(
                label=tc,
                start=self.num_editor.start_spin.value(),
                end=self.num_editor.end_spin.value(),
                step=self.num_editor.step_spin.value(),
                initial=self.num_editor.initial_spin.value(),
            )
        elif isinstance(old_ctrl, SingleOptionInput):
            tc = TextComponent(
                text=self.opt_common.label_edit.text(),
                color=self.opt_common.color_combo.currentText(),
            )
            new_ctrl = SingleOptionInput(
                label=tc,
                options=self.opt_editor.get_options(),
            )
        elif isinstance(old_ctrl, TextInput):
            tc = TextComponent(
                text=self.txt_common.label_edit.text(),
                color=self.txt_common.color_combo.currentText(),
            )
            ml = MultilineConfig(
                enabled=self.txt_editor.multiline_cb.isChecked(),
                max_lines=self.txt_editor.max_lines_spin.value(),
            )
            new_ctrl = TextInput(
                label=tc,
                initial=self.txt_editor.initial_edit.text(),
                placeholder=self.txt_editor.placeholder_edit.text(),
                multiline=ml,
            )
        else:
            return

        # 保留 type
        new_ctrl.type = old_ctrl.type
        item.setData(32, new_ctrl)
        item.setText(self._make_summary(new_ctrl))
        self._refresh_item_widgets()
        self.changed.emit()

    # ---- 批量设置 / 导出 ----

    def set_inputs(self, controls: list):
        """用外部控件列表替换当前列表。"""
        self.list_widget.blockSignals(True)
        self.list_widget.clear()
        for ctrl in controls:
            item = QListWidgetItem(self._make_summary(ctrl))
            item.setData(32, ctrl)
            self.list_widget.addItem(item)
        self.list_widget.blockSignals(False)
        self._refresh_item_widgets()
        self.prop_stack.setCurrentIndex(0)

    def get_inputs(self) -> list:
        """获取当前编辑后的控件列表。"""
        controls = []
        for i in range(self.list_widget.count()):
            controls.append(self.list_widget.item(i).data(32))
        return controls