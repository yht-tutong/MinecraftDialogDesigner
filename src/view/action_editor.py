# action_editor.py
# Minecraft Dialog Designer 对话框操作按钮/动作编辑器

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QListWidget, QListWidgetItem, QPushButton, QLineEdit,
    QCheckBox, QSpinBox, QComboBox, QLabel, QStackedWidget,
    QPlainTextEdit, QShortcut,
)
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QKeySequence
import json

from ..model.action_models import (
    Action, StaticAction, DynamicRunCommandAction, DynamicCustomAction,
)
from .animation_utils import fade_in
from .tooltips import (
    TOOLTIP_ACTION_LABEL, TOOLTIP_ACTION_COLOR, TOOLTIP_ACTION_BOLD,
    TOOLTIP_ACTION_WIDTH, TOOLTIP_ACTION_TYPE, TOOLTIP_ACTION_URL,
    TOOLTIP_ACTION_COMMAND, TOOLTIP_ACTION_DIALOG, TOOLTIP_ACTION_VALUE,
    TOOLTIP_ACTION_PAGE, TOOLTIP_ACTION_CUSTOM_ID, TOOLTIP_ACTION_PAYLOAD,
    TOOLTIP_ACTION_TEMPLATE, TOOLTIP_ACTION_ADDITIONS,
    TOOLTIP_ACTION_INLINE_DIALOG, TOOLTIP_EXIT_ACTION_ENABLE,
)

# 所有支持的 action_type
ACTION_TYPES = [
    "minecraft:open_url",
    "minecraft:run_command",
    "minecraft:suggest_command",
    "minecraft:change_page",
    "minecraft:copy_to_clipboard",
    "minecraft:show_dialog",
    "minecraft:custom",
    "minecraft:dynamic/run_command",
    "minecraft:dynamic/custom",
]

# 哪些类型使用 StaticAction（有独立直接编辑的 params）
_STATIC_DIRECT_TYPES = {
    "minecraft:open_url",
    "minecraft:suggest_command",
}

# 哪些类型需要使用 params JSON 编辑器
_STATIC_JSON_PARAM_TYPES = {
    "minecraft:run_command",
    "minecraft:change_page",
    "minecraft:copy_to_clipboard",
    "minecraft:custom",
}


class _ActionCommonForm(QGroupBox):
    """动作公共属性：标签文本、颜色、粗体、宽度。"""

    changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__("通用属性", parent)
        layout = QFormLayout(self)

        self.label_edit = QLineEdit()
        self.label_edit.setToolTip(TOOLTIP_ACTION_LABEL)
        layout.addRow("标签文本:", self.label_edit)

        self.color_edit = QLineEdit()
        self.color_edit.setToolTip(TOOLTIP_ACTION_COLOR)
        self.color_edit.setPlaceholderText("white, yellow, red, ...")
        layout.addRow("标签颜色:", self.color_edit)

        self.bold_cb = QCheckBox("粗体")
        self.bold_cb.setToolTip(TOOLTIP_ACTION_BOLD)
        layout.addRow("样式:", self.bold_cb)

        self.width_spin = QSpinBox()
        self.width_spin.setToolTip(TOOLTIP_ACTION_WIDTH)
        self.width_spin.setRange(-1, 500)
        self.width_spin.setSpecialValueText("自动")
        self.width_spin.setValue(-1)
        layout.addRow("宽度 (px):", self.width_spin)

        self.label_edit.textChanged.connect(self.changed)
        self.color_edit.textChanged.connect(self.changed)
        self.bold_cb.stateChanged.connect(self.changed)
        self.width_spin.valueChanged.connect(self.changed)


class _StaticDirectEditor(QGroupBox):
    """直接参数编辑器：用于 open_url / suggest_command。"""

    changed = pyqtSignal()

    def __init__(self, action_type: str, parent=None):
        super().__init__("参数", parent)
        self._action_type = action_type
        layout = QFormLayout(self)

        if action_type == "minecraft:open_url":
            self.param_edit = QLineEdit()
            self.param_edit.setToolTip(TOOLTIP_ACTION_URL)
            self.param_edit.setPlaceholderText("https://example.com")
            layout.addRow("URL:", self.param_edit)
        elif action_type == "minecraft:suggest_command":
            self.param_edit = QLineEdit()
            self.param_edit.setToolTip(TOOLTIP_ACTION_COMMAND)
            self.param_edit.setPlaceholderText("/say Hello")
            layout.addRow("建议命令:", self.param_edit)
        else:
            self.param_edit = QLineEdit()
            layout.addRow("值:", self.param_edit)

        self.param_edit.textChanged.connect(self.changed)

    def get_param_value(self) -> str:
        return self.param_edit.text()

    def set_param_value(self, val: str):
        self.param_edit.setText(val)


class _StaticJsonEditor(QGroupBox):
    """JSON 参数编辑器：用于 run_command / change_page / copy_to_clipboard / custom。"""

    changed = pyqtSignal()

    def __init__(self, action_type: str, parent=None):
        super().__init__(f"参数 (JSON)", parent)
        self._action_type = action_type
        layout = QVBoxLayout(self)

        hint_text = {
            "minecraft:run_command": '{"command": "/say hello"}',
            "minecraft:change_page": '{"page": 1}',
            "minecraft:copy_to_clipboard": '{"value": "text to copy"}',
            "minecraft:custom": '{"id": "my_action", ...}',
        }.get(action_type, "{}")

        param_tooltips = {
            "minecraft:run_command": TOOLTIP_ACTION_COMMAND,
            "minecraft:change_page": TOOLTIP_ACTION_PAGE,
            "minecraft:copy_to_clipboard": TOOLTIP_ACTION_VALUE,
            "minecraft:custom": TOOLTIP_ACTION_PAYLOAD,
        }

        hint = QLabel(f"JSON 格式 (例如: {hint_text})")
        hint.setStyleSheet("color: gray; font-size: 11px;")
        layout.addWidget(hint)

        self.json_edit = QPlainTextEdit()
        self.json_edit.setToolTip(param_tooltips.get(action_type, ""))
        self.json_edit.setPlaceholderText(hint_text)
        self.json_edit.setMaximumBlockCount(20)
        layout.addWidget(self.json_edit)

        self.json_edit.textChanged.connect(self.changed)


class _ShowDialogEditor(QGroupBox):
    """show_dialog 参数编辑器，支持对话框 ID 引用和内联 JSON 定义。"""

    changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__("显示对话框参数", parent)
        layout = QVBoxLayout(self)

        # 对话框 ID 行
        id_row = QHBoxLayout()
        self.dialog_id_label = QLabel("对话框 ID:")
        self.dialog_id_edit = QLineEdit()
        self.dialog_id_edit.setToolTip(TOOLTIP_ACTION_DIALOG)
        self.dialog_id_edit.setPlaceholderText("namespace:dialog_id")
        id_row.addWidget(self.dialog_id_label)
        id_row.addWidget(self.dialog_id_edit)
        layout.addLayout(id_row)

        self.inline_cb = QCheckBox("使用内联对话框")
        self.inline_cb.setToolTip(TOOLTIP_ACTION_INLINE_DIALOG)
        layout.addWidget(self.inline_cb)

        # 内联 JSON 编辑器（默认隐藏）
        self.inline_edit = QPlainTextEdit()
        self.inline_edit.setToolTip("直接输入 JSON 格式的对话框定义")
        self.inline_edit.setPlaceholderText(
            '{\n  "type": "dialog_list",\n  "title": "对话框标题",\n  ...\n}'
        )
        self.inline_edit.setMaximumBlockCount(30)
        self.inline_edit.setVisible(False)
        layout.addWidget(self.inline_edit)

        self.inline_cb.stateChanged.connect(self._on_inline_toggled)
        self.dialog_id_edit.textChanged.connect(self.changed)
        self.inline_edit.textChanged.connect(self.changed)

    def _on_inline_toggled(self):
        is_inline = self.inline_cb.isChecked()
        self.dialog_id_label.setVisible(not is_inline)
        self.dialog_id_edit.setVisible(not is_inline)
        self.inline_edit.setVisible(is_inline)
        self.changed.emit()


class _DynamicRunCommandEditor(QGroupBox):
    """动态运行命令编辑器。"""

    changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__("动态命令模板", parent)
        layout = QVBoxLayout(self)

        hint = QLabel("使用 {{key}} 引用输入控件的值")
        hint.setStyleSheet("color: gray; font-size: 11px;")
        layout.addWidget(hint)

        self.template_edit = QPlainTextEdit()
        self.template_edit.setToolTip(TOOLTIP_ACTION_TEMPLATE)
        self.template_edit.setPlaceholderText(
            'say 你选择了 {{option_key}}\n'
            'give @s {{item_key}}'
        )
        self.template_edit.setMaximumBlockCount(20)
        layout.addWidget(self.template_edit)

        self.template_edit.textChanged.connect(self.changed)


class _CustomActionEditor(QWidget):
    """自定义动作编辑器：id + additions JSON。"""

    changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        form = QFormLayout()
        self.id_edit = QLineEdit()
        self.id_edit.setToolTip(TOOLTIP_ACTION_CUSTOM_ID)
        self.id_edit.setPlaceholderText("my_custom_action")
        form.addRow("ID:", self.id_edit)
        layout.addLayout(form)

        additions_label = QLabel("附加字段 (JSON):")
        layout.addWidget(additions_label)

        self.additions_edit = QPlainTextEdit()
        self.additions_edit.setToolTip(TOOLTIP_ACTION_ADDITIONS)
        self.additions_edit.setPlaceholderText('{\n  "some_key": "some_value"\n}')
        self.additions_edit.setMaximumBlockCount(15)
        layout.addWidget(self.additions_edit)

        self.id_edit.textChanged.connect(self.changed)
        self.additions_edit.textChanged.connect(self.changed)


class _ActionProperties(QStackedWidget):
    """动作属性栈，根据 action_type 切换不同的参数编辑器。"""

    changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # 页面 0: 空
        self.addWidget(QLabel("请选择动作类型"))

        # 页面 1: open_url (StaticAction, direct)
        self.open_url_editor = _StaticDirectEditor("minecraft:open_url")
        self.open_url_editor.changed.connect(self._relay)
        self.addWidget(self.open_url_editor)

        # 页面 2: run_command (StaticAction, JSON)
        self.run_cmd_editor = _StaticJsonEditor("minecraft:run_command")
        self.run_cmd_editor.changed.connect(self._relay)
        self.addWidget(self.run_cmd_editor)

        # 页面 3: suggest_command (StaticAction, direct)
        self.suggest_cmd_editor = _StaticDirectEditor("minecraft:suggest_command")
        self.suggest_cmd_editor.changed.connect(self._relay)
        self.addWidget(self.suggest_cmd_editor)

        # 页面 4: change_page (StaticAction, JSON)
        self.change_page_editor = _StaticJsonEditor("minecraft:change_page")
        self.change_page_editor.changed.connect(self._relay)
        self.addWidget(self.change_page_editor)

        # 页面 5: copy_to_clipboard (StaticAction, JSON)
        self.copy_editor = _StaticJsonEditor("minecraft:copy_to_clipboard")
        self.copy_editor.changed.connect(self._relay)
        self.addWidget(self.copy_editor)

        # 页面 6: show_dialog
        self.show_dialog_editor = _ShowDialogEditor()
        self.show_dialog_editor.changed.connect(self._relay)
        self.addWidget(self.show_dialog_editor)

        # 页面 7: custom (StaticAction, JSON)
        self.custom_editor = _StaticJsonEditor("minecraft:custom")
        self.custom_editor.changed.connect(self._relay)
        self.addWidget(self.custom_editor)

        # 页面 8: dynamic/run_command
        self.dynamic_run_editor = _DynamicRunCommandEditor()
        self.dynamic_run_editor.changed.connect(self._relay)
        self.addWidget(self.dynamic_run_editor)

        # 页面 9: dynamic/custom (custom-like but dynamic)
        self.dynamic_custom_editor = _CustomActionEditor()
        self.dynamic_custom_editor.changed.connect(self._relay)
        self.addWidget(self.dynamic_custom_editor)

        self.setCurrentIndex(0)

    def _relay(self):
        self.changed.emit()

    def show_for_type(self, action_type: str):
        """根据 action_type 切换到对应属性页面。"""
        mapping = {
            "minecraft:open_url": 1,
            "minecraft:run_command": 2,
            "minecraft:suggest_command": 3,
            "minecraft:change_page": 4,
            "minecraft:copy_to_clipboard": 5,
            "minecraft:show_dialog": 6,
            "minecraft:custom": 7,
            "minecraft:dynamic/run_command": 8,
            "minecraft:dynamic/custom": 9,
        }
        idx = mapping.get(action_type, 0)
        self.setCurrentIndex(idx)

    def populate_from_action(self, action: Action):
        """从 Action 对象填充属性。"""
        if isinstance(action, StaticAction):
            if action.action_type == "minecraft:open_url":
                self.show_for_type(action.action_type)
                self.open_url_editor.set_param_value(
                    action.params.get("url", "")
                )
            elif action.action_type == "minecraft:suggest_command":
                self.show_for_type(action.action_type)
                self.suggest_cmd_editor.set_param_value(
                    action.params.get("command", "")
                )
            elif action.action_type in _STATIC_JSON_PARAM_TYPES:
                self.show_for_type(action.action_type)
                json_text = json.dumps(action.params, indent=2, ensure_ascii=False)
                if action.action_type == "minecraft:run_command":
                    self.run_cmd_editor.json_edit.setPlainText(json_text)
                elif action.action_type == "minecraft:change_page":
                    self.change_page_editor.json_edit.setPlainText(json_text)
                elif action.action_type == "minecraft:copy_to_clipboard":
                    self.copy_editor.json_edit.setPlainText(json_text)
                elif action.action_type == "minecraft:custom":
                    self.custom_editor.json_edit.setPlainText(json_text)
            elif action.action_type == "minecraft:show_dialog":
                self.show_for_type(action.action_type)
                inline_dialog = action.params.get("inline_dialog", None)
                if isinstance(inline_dialog, dict):
                    self.show_dialog_editor.inline_cb.setChecked(True)
                    self.show_dialog_editor.inline_edit.setPlainText(
                        json.dumps(inline_dialog, indent=2, ensure_ascii=False)
                    )
                else:
                    self.show_dialog_editor.inline_cb.setChecked(False)
                    self.show_dialog_editor.dialog_id_edit.setText(
                        action.params.get("dialog", "")
                    )
            else:
                self.show_for_type(action.action_type)
        elif isinstance(action, DynamicRunCommandAction):
            self.show_for_type("minecraft:dynamic/run_command")
            self.dynamic_run_editor.template_edit.setPlainText(action.command)
        elif isinstance(action, DynamicCustomAction):
            self.show_for_type("minecraft:dynamic/custom")
            try:
                params = json.loads(action.command) if action.command else {}
            except json.JSONDecodeError:
                params = {}
            self.dynamic_custom_editor.id_edit.setText(
                params.get("id", "")
            )
            additions = {k: v for k, v in params.items() if k != "id"}
            self.dynamic_custom_editor.additions_edit.setPlainText(
                json.dumps(additions, indent=2, ensure_ascii=False)
                if additions else ""
            )
        else:
            self.show_for_type("")

    def to_action(self, action_type: str) -> Action:
        """从当前属性构建 Action 对象。"""
        if action_type in ("minecraft:dynamic/run_command",):
            return DynamicRunCommandAction(
                command=self.dynamic_run_editor.template_edit.toPlainText()
            )
        elif action_type == "minecraft:dynamic/custom":
            additions_text = self.dynamic_custom_editor.additions_edit.toPlainText()
            additions = {}
            try:
                additions = json.loads(additions_text) if additions_text.strip() else {}
            except json.JSONDecodeError:
                pass
            command_dict = {"id": self.dynamic_custom_editor.id_edit.text()}
            command_dict.update(additions)
            return DynamicCustomAction(
                command=json.dumps(command_dict, ensure_ascii=False)
            )
        elif action_type == "minecraft:open_url":
            return StaticAction(
                action_type=action_type,
                params={"url": self.open_url_editor.get_param_value()}
            )
        elif action_type == "minecraft:suggest_command":
            return StaticAction(
                action_type=action_type,
                params={"command": self.suggest_cmd_editor.get_param_value()}
            )
        elif action_type == "minecraft:show_dialog":
            params = {}
            if self.show_dialog_editor.inline_cb.isChecked():
                inline_text = self.show_dialog_editor.inline_edit.toPlainText()
                try:
                    inline_dialog = json.loads(inline_text) if inline_text.strip() else {}
                    params["inline_dialog"] = inline_dialog
                except json.JSONDecodeError:
                    params["inline_dialog"] = {}
            else:
                params["dialog"] = self.show_dialog_editor.dialog_id_edit.text()
            return StaticAction(action_type=action_type, params=params)
        elif action_type in _STATIC_JSON_PARAM_TYPES:
            json_text = ""
            if action_type == "minecraft:run_command":
                json_text = self.run_cmd_editor.json_edit.toPlainText()
            elif action_type == "minecraft:change_page":
                json_text = self.change_page_editor.json_edit.toPlainText()
            elif action_type == "minecraft:copy_to_clipboard":
                json_text = self.copy_editor.json_edit.toPlainText()
            elif action_type == "minecraft:custom":
                json_text = self.custom_editor.json_edit.toPlainText()

            params = {}
            try:
                params = json.loads(json_text) if json_text.strip() else {}
            except json.JSONDecodeError:
                pass
            return StaticAction(action_type=action_type, params=params)
        else:
            return StaticAction(action_type=action_type)


class _ActionItemData:
    """存储在 QListWidgetItem 中的动作数据包装类。"""

    def __init__(self, action: Action, label: str = "",
                 label_color: str = "white", bold: bool = False,
                 width: int = -1):
        self.action = action
        self.label = label
        self.label_color = label_color
        self.bold = bold
        self.width = width

    @property
    def action_type(self) -> str:
        if isinstance(self.action, StaticAction):
            return self.action.action_type
        return self.action.action_type


class ActionEditor(QWidget):
    """操作按钮编辑器。

    管理 actions 列表，支持 9 种动作类型，以及退出动作编辑。
    """

    changed = pyqtSignal()
    copy_requested = pyqtSignal(dict)   # 请求复制选中的 action
    paste_requested = pyqtSignal()       # 请求粘贴 action

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setSpacing(6)
        layout.setContentsMargins(6, 6, 6, 6)

        # ======== 常规动作列表 ========
        main_group = QGroupBox("操作按钮 (actions)")
        main_layout = QVBoxLayout(main_group)
        main_layout.setSpacing(6)
        main_layout.setContentsMargins(6, 6, 6, 6)

        # 工具栏
        toolbar = QHBoxLayout()
        toolbar.setSpacing(6)
        self.add_btn = QPushButton("+ 添加")

        self.action_type_combo = QComboBox()
        self.action_type_combo.setToolTip(TOOLTIP_ACTION_TYPE)
        self.action_type_combo.addItems(ACTION_TYPES)

        toolbar.addWidget(QLabel("类型:"))
        toolbar.addWidget(self.action_type_combo)
        toolbar.addWidget(self.add_btn)
        toolbar.addStretch()
        main_layout.addLayout(toolbar)

        # 列表
        self.list_widget = QListWidget()
        main_layout.addWidget(self.list_widget)

        # 公共属性
        self.common_form = _ActionCommonForm()
        self.common_form.changed.connect(self._on_common_changed)
        main_layout.addWidget(self.common_form)

        # 类型选择
        type_layout = QFormLayout()
        self.type_combo = QComboBox()
        self.type_combo.setToolTip(TOOLTIP_ACTION_TYPE)
        self.type_combo.addItems(ACTION_TYPES)
        self.type_combo.currentTextChanged.connect(self._on_type_changed)
        type_layout.addRow("动作类型:", self.type_combo)
        main_layout.addLayout(type_layout)

        # 类型特定属性
        self.prop_stack = _ActionProperties()
        self.prop_stack.changed.connect(self._on_prop_changed)
        main_layout.addWidget(self.prop_stack)

        layout.addWidget(main_group)

        # ======== 退出动作 ========
        exit_group = QGroupBox("退出动作 (exit_action, 可选)")
        exit_layout = QVBoxLayout(exit_group)
        exit_layout.setSpacing(6)
        exit_layout.setContentsMargins(6, 6, 6, 6)

        self.enable_exit_cb = QCheckBox("启用退出动作")
        self.enable_exit_cb.setToolTip(TOOLTIP_EXIT_ACTION_ENABLE)
        exit_layout.addWidget(self.enable_exit_cb)

        # 退出动作的属性编辑（复用上面的组件）
        exit_form_layout = QFormLayout()
        self.exit_label_edit = QLineEdit()
        self.exit_label_edit.setToolTip(TOOLTIP_ACTION_LABEL)
        exit_form_layout.addRow("标签文本:", self.exit_label_edit)
        self.exit_color_edit = QLineEdit()
        self.exit_color_edit.setToolTip(TOOLTIP_ACTION_COLOR)
        self.exit_color_edit.setPlaceholderText("white")
        exit_form_layout.addRow("标签颜色:", self.exit_color_edit)
        exit_layout.addLayout(exit_form_layout)

        self.exit_type_combo = QComboBox()
        self.exit_type_combo.setToolTip(TOOLTIP_ACTION_TYPE)
        self.exit_type_combo.addItems(ACTION_TYPES)
        exit_layout.addWidget(QLabel("退出动作类型:"))
        exit_layout.addWidget(self.exit_type_combo)

        self.exit_prop_stack = _ActionProperties()
        exit_layout.addWidget(self.exit_prop_stack)

        layout.addWidget(exit_group)

        # ======== 取消回调 (on_cancel) ========
        on_cancel_group = QGroupBox("取消回调 (on_cancel)")
        on_cancel_layout = QVBoxLayout(on_cancel_group)
        on_cancel_layout.setSpacing(6)
        on_cancel_layout.setContentsMargins(6, 6, 6, 6)

        self.on_cancel_enable_cb = QCheckBox("启用 on_cancel")
        on_cancel_layout.addWidget(self.on_cancel_enable_cb)

        on_cancel_form = QFormLayout()
        self.on_cancel_command_edit = QLineEdit()
        self.on_cancel_command_edit.setPlaceholderText("say cancelled")
        on_cancel_form.addRow("取消命令:", self.on_cancel_command_edit)
        on_cancel_layout.addLayout(on_cancel_form)

        layout.addWidget(on_cancel_group)

        # ---- 信号 ----
        self.add_btn.clicked.connect(self._add_action)
        self.list_widget.currentRowChanged.connect(self._on_selection_changed)
        self.enable_exit_cb.stateChanged.connect(self.changed)

        # Delete 键删除选中动作
        QShortcut(QKeySequence.Delete, self.list_widget, self._remove_action)

        # Ctrl+C / Ctrl+V 复制粘贴
        QShortcut(QKeySequence.Copy, self.list_widget, self._copy_selected)
        QShortcut(QKeySequence.Paste, self.list_widget, self._paste_request)
        self.exit_label_edit.textChanged.connect(self.changed)
        self.exit_color_edit.textChanged.connect(self.changed)
        self.exit_type_combo.currentTextChanged.connect(
            self._on_exit_type_changed
        )
        self.on_cancel_enable_cb.stateChanged.connect(self.changed)
        self.on_cancel_command_edit.textChanged.connect(self.changed)

    def _make_summary(self, data: _ActionItemData) -> str:
        """生成动作摘要。"""
        at = data.action_type.split(":")[-1] if ":" in data.action_type else data.action_type
        lbl = data.label or at
        return f"[{at}] {lbl[:30]}"

    # ---- 增删改 ----

    def _add_action(self):
        at = self.action_type_combo.currentText()
        action = StaticAction(action_type=at)
        data = _ActionItemData(action=action, label=at)
        item = QListWidgetItem(self._make_summary(data))
        item.setData(32, data)
        self.list_widget.addItem(item)
        self.list_widget.setCurrentItem(item)
        self._refresh_item_widgets()
        self.changed.emit()
        fade_in(self.list_widget, 150)

    def _remove_action(self):
        row = self.list_widget.currentRow()
        if row < 0:
            return
        self.list_widget.takeItem(row)
        self._refresh_item_widgets()
        self.changed.emit()
        fade_in(self.list_widget, 150)

    def _copy_selected(self):
        """复制选中的 action 到内部剪贴板。"""
        row = self.list_widget.currentRow()
        if row < 0:
            return
        item = self.list_widget.item(row)
        data: _ActionItemData = item.data(32)
        if data and data.action:
            action_dict = data.action.to_dict()
            action_dict["_label"] = data.label
            action_dict["_label_color"] = data.label_color
            action_dict["_bold"] = data.bold
            action_dict["_width"] = data.width
            self.copy_requested.emit(action_dict)

    def _paste_request(self):
        """请求粘贴 action。"""
        self.paste_requested.emit()

    def add_action_from_clipboard(self, action_data: dict):
        """从剪贴板添加 action（从 dict 重建）。"""
        from ..model.action_models import StaticAction, DynamicRunCommandAction, DynamicCustomAction
        atype = action_data.get("action_type", action_data.get("type", "minecraft:open_url"))
        params = {k: v for k, v in action_data.items()
                  if k not in ("action_type", "type", "_label", "_label_color", "_bold", "_width")}
        if atype == "minecraft:dynamic/run_command":
            action = DynamicRunCommandAction(command=action_data.get("command", ""))
        elif atype == "minecraft:dynamic/custom":
            action = DynamicCustomAction(command=action_data.get("command", ""))
        else:
            action = StaticAction(action_type=atype, params=params)
        data = _ActionItemData(
            action=action,
            label=action_data.get("_label", ""),
            label_color=action_data.get("_label_color", "white"),
            bold=action_data.get("_bold", False),
            width=action_data.get("_width", -1),
        )
        item = QListWidgetItem(self._make_summary(data))
        item.setData(32, data)
        self.list_widget.addItem(item)
        self.list_widget.setCurrentItem(item)
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

    # ---- 内联按钮操作 ----

    def _get_row_from_button(self, button):
        """从按钮找到其所属列表项的行号。"""
        for i in range(self.list_widget.count()):
            w = self.list_widget.itemWidget(self.list_widget.item(i))
            if w is not None and w is button.parent():
                return i
        return -1

    def _inline_move_up(self):
        btn = self.sender()
        row = self._get_row_from_button(btn)
        if row <= 0:
            return
        self.list_widget.setCurrentRow(row)
        self._move_up()

    def _inline_move_down(self):
        btn = self.sender()
        row = self._get_row_from_button(btn)
        if row < 0 or row >= self.list_widget.count() - 1:
            return
        self.list_widget.setCurrentRow(row)
        self._move_down()

    def _inline_remove(self):
        btn = self.sender()
        row = self._get_row_from_button(btn)
        if row < 0:
            return
        self.list_widget.setCurrentRow(row)
        self._remove_action()

    def _refresh_item_widgets(self):
        """为所有列表项设置内联按钮 widget。"""
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            data: _ActionItemData = item.data(32)
            item.setText(self._make_summary(data))

            w = QWidget()
            row_layout = QHBoxLayout(w)
            row_layout.setContentsMargins(4, 2, 4, 2)
            row_layout.setSpacing(4)

            summary = QLabel(self._make_summary(data))
            row_layout.addWidget(summary, 1)

            up_btn = QPushButton("↑")
            up_btn.setFixedSize(24, 24)
            up_btn.setToolTip("上移")
            up_btn.clicked.connect(self._inline_move_up)
            row_layout.addWidget(up_btn)

            down_btn = QPushButton("↓")
            down_btn.setFixedSize(24, 24)
            down_btn.setToolTip("下移")
            down_btn.clicked.connect(self._inline_move_down)
            row_layout.addWidget(down_btn)

            del_btn = QPushButton("✕")
            del_btn.setFixedSize(24, 24)
            del_btn.setToolTip("删除")
            del_btn.clicked.connect(self._inline_remove)
            row_layout.addWidget(del_btn)

            self.list_widget.setItemWidget(item, w)

    def _update_item_summary(self, item, data):
        """更新单个列表项内联 widget 中的摘要标签。"""
        w = self.list_widget.itemWidget(item)
        if w is not None:
            label = w.layout().itemAt(0).widget()
            if isinstance(label, QLabel):
                label.setText(self._make_summary(data))

    # ---- 选择与编辑 ----

    def _on_selection_changed(self, row: int):
        if row < 0:
            self.common_form.setEnabled(False)
            self.type_combo.setEnabled(False)
            self.prop_stack.setEnabled(False)
            return

        self.common_form.setEnabled(True)
        self.type_combo.setEnabled(True)
        self.prop_stack.setEnabled(True)

        item = self.list_widget.item(row)
        data: _ActionItemData = item.data(32)

        # 公共属性
        self.common_form.label_edit.setText(data.label)
        self.common_form.color_edit.setText(data.label_color)
        self.common_form.bold_cb.setChecked(data.bold)
        self.common_form.width_spin.setValue(data.width)

        # 动作类型
        idx = self.type_combo.findText(data.action_type)
        if idx >= 0:
            self.type_combo.blockSignals(True)
            self.type_combo.setCurrentIndex(idx)
            self.type_combo.blockSignals(False)

        # 属性
        self.prop_stack.populate_from_action(data.action)

    def _on_type_changed(self, action_type: str):
        """切换动作类型时切换属性编辑器。"""
        if not action_type:
            return
        self.prop_stack.show_for_type(action_type)
        row = self.list_widget.currentRow()
        if row >= 0:
            item = self.list_widget.item(row)
            data: _ActionItemData = item.data(32)
            # 重建 Action
            new_action = self.prop_stack.to_action(action_type)
            data.action = new_action
            item.setText(self._make_summary(data))
            self._update_item_summary(item, data)
            self.changed.emit()

    def _on_common_changed(self):
        """公共属性变更。"""
        row = self.list_widget.currentRow()
        if row < 0:
            return
        item = self.list_widget.item(row)
        data: _ActionItemData = item.data(32)
        data.label = self.common_form.label_edit.text()
        data.label_color = self.common_form.color_edit.text()
        data.bold = self.common_form.bold_cb.isChecked()
        data.width = self.common_form.width_spin.value()
        item.setText(self._make_summary(data))
        self._update_item_summary(item, data)
        self.changed.emit()

    def _on_prop_changed(self):
        """类型特定属性变更。"""
        row = self.list_widget.currentRow()
        if row < 0:
            return
        item = self.list_widget.item(row)
        data: _ActionItemData = item.data(32)
        action_type = self.type_combo.currentText()
        data.action = self.prop_stack.to_action(action_type)
        item.setText(self._make_summary(data))
        self._update_item_summary(item, data)
        self.changed.emit()

    # ---- 退出动作 ----

    def _on_exit_type_changed(self, action_type: str):
        """退出动作类型切换。"""
        self.exit_prop_stack.show_for_type(action_type)
        self.changed.emit()

    # ---- 批量设置 / 导出 ----

    def set_actions(self, actions: list):
        """用外部动作列表替换当前列表。"""
        self.list_widget.blockSignals(True)
        self.list_widget.clear()
        for action in actions:
            data = _ActionItemData(action=action)
            # 尝试从 StaticAction params 中提取 label
            if isinstance(action, StaticAction):
                data.label = action.params.get("label", "")
                data.label_color = action.params.get("label_color", "white")
                data.bold = action.params.get("bold", False)
                data.width = action.params.get("width", -1)
            item = QListWidgetItem(self._make_summary(data))
            item.setData(32, data)
            self.list_widget.addItem(item)
        self.list_widget.blockSignals(False)
        self._refresh_item_widgets()

    def get_actions(self) -> list:
        """获取当前编辑后的动作列表。"""
        actions = []
        for i in range(self.list_widget.count()):
            data: _ActionItemData = self.list_widget.item(i).data(32)
            # 将 UI 标签等信息注入到 params 中
            action = data.action
            if isinstance(action, StaticAction):
                if data.label:
                    action.params["label"] = data.label
                if data.label_color != "white":
                    action.params["label_color"] = data.label_color
                if data.bold:
                    action.params["bold"] = True
                if data.width > 0:
                    action.params["width"] = data.width
            actions.append(action)
        return actions

    def set_exit_action(self, action, label="", color="white"):
        """设置退出动作。"""
        if action is None:
            self.enable_exit_cb.setChecked(False)
            return
        self.enable_exit_cb.setChecked(True)
        self.exit_label_edit.setText(label)
        self.exit_color_edit.setText(color)
        at = action.action_type if isinstance(action, StaticAction) else action.action_type
        idx = self.exit_type_combo.findText(at)
        if idx >= 0:
            self.exit_type_combo.setCurrentIndex(idx)
        self.exit_prop_stack.populate_from_action(action)

    def get_exit_action(self):
        """获取退出动作，如果未启用则返回 None。"""
        if not self.enable_exit_cb.isChecked():
            return None
        at = self.exit_type_combo.currentText()
        action = self.exit_prop_stack.to_action(at)
        if isinstance(action, StaticAction):
            lbl = self.exit_label_edit.text()
            color = self.exit_color_edit.text()
            if lbl:
                action.params["label"] = lbl
            if color and color != "white":
                action.params["label_color"] = color
        return action

    def set_on_cancel(self, command: str = "", enabled: bool = False):
        """设置 on_cancel 回调。"""
        self.on_cancel_enable_cb.setChecked(enabled)
        self.on_cancel_command_edit.setText(command)

    def get_on_cancel(self):
        """获取 on_cancel ClickEvent，如果未启用则返回 None。"""
        if not self.on_cancel_enable_cb.isChecked():
            return None
        cmd = self.on_cancel_command_edit.text().strip()
        if not cmd:
            return None
        return {"action": "run_command", "command": cmd}