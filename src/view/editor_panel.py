# editor_panel.py
# Minecraft Dialog Designer 编辑器面板 - 封装单个标签页的编辑器+预览布局

from PyQt5.QtWidgets import (
    QWidget, QTabWidget, QSplitter, QVBoxLayout,
)
from PyQt5.QtCore import Qt, pyqtSignal
import json

from .dialog_editor import DialogEditor
from .body_editor import BodyEditor
from .input_editor import InputEditor
from .action_editor import ActionEditor
from .preview_panel import PreviewPanel
from .visual_preview import VisualPreview
from .animation_utils import fade_in
from ..controller.dialog_session import DialogSession
from ..model.dialog_base import TextComponent


class EditorPanel(QWidget):
    """单个标签页的编辑器面板。

    包含左侧编辑器标签页（通用设置、主体元素、输入控件、操作按钮）
    和右侧预览标签页（JSON 预览、可视化预览）。

    每个标签页持有独立的 EditorPanel 实例，互不影响。
    """

    changed = pyqtSignal()        # 编辑器内容变更
    json_edited = pyqtSignal(dict)  # JSON 预览编辑后
    copy_requested = pyqtSignal(str, dict)   # (type, data) 请求复制
    paste_requested = pyqtSignal(str)        # type 请求粘贴

    def __init__(self, session: DialogSession, parent=None):
        super().__init__(parent)
        self._session = session

        self._build_ui()
        self._connect_signals()
        self.refresh_from_session()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Horizontal)

        # 左侧：编辑器选项卡
        self.tab_widget = QTabWidget()
        self.tab_widget.setContentsMargins(0, 0, 0, 0)

        self.dialog_editor = DialogEditor()
        self.tab_widget.addTab(self.dialog_editor, "通用设置")

        self.body_editor = BodyEditor()
        self.tab_widget.addTab(self.body_editor, "主体元素")

        self.input_editor = InputEditor()
        self.tab_widget.addTab(self.input_editor, "输入控件")

        self.action_editor = ActionEditor()
        self.tab_widget.addTab(self.action_editor, "操作按钮")

        splitter.addWidget(self.tab_widget)

        # 标签页切换动画
        self.tab_widget.currentChanged.connect(self._on_tab_changed)

        # 右侧：预览选项卡
        self.preview_tabs = QTabWidget()

        self.preview_panel = PreviewPanel()
        self.preview_panel.json_edited.connect(self._on_json_edited)
        self.preview_tabs.addTab(self.preview_panel, "JSON 预览")

        self.visual_preview = VisualPreview()
        self.preview_tabs.addTab(self.visual_preview, "可视化预览")

        splitter.addWidget(self.preview_tabs)

        splitter.setSizes([800, 400])
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)

        layout.addWidget(splitter)

    def _connect_signals(self):
        """连接编辑器信号。"""
        self.dialog_editor.changed.connect(self._on_editor_changed)
        self.body_editor.changed.connect(self._on_editor_changed)
        self.input_editor.changed.connect(self._on_editor_changed)
        self.action_editor.changed.connect(self._on_editor_changed)

        # 跨标签页复制粘贴信号转发
        self.body_editor.copy_requested.connect(
            lambda data: self.copy_requested.emit('body', data))
        self.body_editor.paste_requested.connect(
            lambda: self.paste_requested.emit('body'))
        self.input_editor.copy_requested.connect(
            lambda data: self.copy_requested.emit('input', data))
        self.input_editor.paste_requested.connect(
            lambda: self.paste_requested.emit('input'))
        self.action_editor.copy_requested.connect(
            lambda data: self.copy_requested.emit('action', data))
        self.action_editor.paste_requested.connect(
            lambda: self.paste_requested.emit('action'))

    def _on_editor_changed(self):
        """编辑器内容变更时标记会话并触发信号。"""
        self._session.modified = True
        self.changed.emit()

    def _on_tab_changed(self, index):
        """编辑器标签页切换动画。"""
        widget = self.tab_widget.widget(index)
        if widget:
            fade_in(widget, 250)

    def _on_json_edited(self, data: dict):
        """JSON 预览编辑后转发信号。"""
        self.json_edited.emit(data)

    # ---- 会话同步 ----

    def sync_to_session(self):
        """将 UI 数据同步到会话的对话框模型。"""
        dialog = self._session.dialog

        new_type = self.dialog_editor.get_type()
        if dialog.type != new_type:
            # 类型切换需要通过控制器处理
            self._session.dialog = self._create_dialog_of_type(new_type, dialog)

        dialog = self._session.dialog

        dialog.title = self.dialog_editor.get_title()
        dialog.pause = self.dialog_editor.get_pause()
        dialog.can_close_with_escape = self.dialog_editor.get_can_close_with_escape()
        dialog.after_action = self.dialog_editor.get_after_action()
        dialog.external_title = self.dialog_editor.get_external_title()

        dialog.body = self.body_editor.get_elements()
        dialog.inputs = self.input_editor.get_inputs()

        if hasattr(dialog, 'actions'):
            dialog.actions = self.action_editor.get_actions()
        if hasattr(dialog, 'exit_action'):
            dialog.exit_action = self.action_editor.get_exit_action()

    def _create_dialog_of_type(self, new_type: str, old_dialog):
        """根据类型字符串创建对应的对话框实例，保留公共字段。"""
        from ..model import (
            MultiActionDialog, ConfirmationDialog, DialogListDialog,
            NoticeDialog, ServerLinksDialog, SimpleInputFormDialog,
            MultiActionInputDialog,
        )
        common = {
            "title": old_dialog.title,
            "body": list(old_dialog.body),
            "inputs": list(old_dialog.inputs),
            "pause": old_dialog.pause,
            "can_close_with_escape": old_dialog.can_close_with_escape,
            "after_action": old_dialog.after_action,
            "external_title": old_dialog.external_title,
        }
        type_map = {
            "minecraft:multi_action": MultiActionDialog,
            "minecraft:confirmation": ConfirmationDialog,
            "minecraft:dialog_list": DialogListDialog,
            "minecraft:notice": NoticeDialog,
            "minecraft:server_links": ServerLinksDialog,
            "minecraft:simple_input_form": SimpleInputFormDialog,
            "minecraft:multi_action_input_form": MultiActionInputDialog,
        }
        cls = type_map.get(new_type, MultiActionDialog)
        return cls(**common)

    def refresh_from_session(self):
        """从会话加载数据到 UI。"""
        dialog = self._session.dialog

        self.dialog_editor.set_from_dialog(dialog)
        self.body_editor.set_elements(getattr(dialog, 'body', []))
        self.input_editor.set_inputs(getattr(dialog, 'inputs', []))

        if hasattr(dialog, 'actions'):
            self.action_editor.set_actions(dialog.actions)
        if hasattr(dialog, 'exit_action'):
            self.action_editor.set_exit_action(
                dialog.exit_action,
                label=getattr(dialog.exit_action, 'label', ''),
            )

        # 更新预览
        data = dialog.to_dict()
        text = json.dumps(data, indent=2, ensure_ascii=False)
        self.preview_panel.set_text(text)
        self.visual_preview.update_dialog(data)

    def get_session(self) -> DialogSession:
        """返回关联的会话。"""
        return self._session

    def set_session(self, session: DialogSession):
        """更换关联的会话。"""
        self._session = session
        self.refresh_from_session()

    def apply_locked_fields(self):
        """根据会话的锁定字段禁用编辑器按钮。"""
        locked = self._session.locked_fields
        if "body" in locked:
            self.body_editor.add_plain_btn.setEnabled(False)
            self.body_editor.add_item_btn.setEnabled(False)
        if "inputs" in locked:
            self.input_editor.add_btn.setEnabled(False)
        if "actions" in locked:
            self.action_editor.add_btn.setEnabled(False)

    def unlock_all(self):
        """解锁所有编辑器按钮。"""
        self.body_editor.add_plain_btn.setEnabled(True)
        self.body_editor.add_item_btn.setEnabled(True)
        self.input_editor.add_btn.setEnabled(True)
        self.action_editor.add_btn.setEnabled(True)

    def paste_from_clipboard(self, item_type: str, data: dict):
        """从剪贴板粘贴数据到对应编辑器。

        Args:
            item_type: 'body' | 'input' | 'action'
            data: 剪贴板中的 dict 数据
        """
        if item_type == 'body':
            from ..model.body_elements import PlainMessageElement, ItemElement
            btype = data.get('type', '')
            if btype == 'minecraft:plain_message':
                contents = data.get('contents', {})
                tc = TextComponent(
                    text=contents.get('text', ''),
                    color=contents.get('color', 'white'),
                    bold=contents.get('bold', False),
                    italic=contents.get('italic', False),
                    underlined=contents.get('underlined', False),
                )
                elem = PlainMessageElement(text=tc)
                if 'width' in data:
                    elem.width = data['width']
            elif btype == 'minecraft:item':
                desc = None
                if 'description' in data:
                    desc_data = data['description']
                    if isinstance(desc_data, dict):
                        desc = PlainMessageElement(text=TextComponent(
                            text=desc_data.get('contents', {}).get('text', ''),
                            color=desc_data.get('contents', {}).get('color', 'white'),
                        ))
                elem = ItemElement(
                    item=data.get('item', 'minecraft:stone'),
                    description=desc,
                )
            else:
                return
            self.body_editor.add_element_from_clipboard(elem)

        elif item_type == 'input':
            from ..model.input_controls import (
                BooleanInput, NumberRangeInput, SingleOptionInput,
                TextInput, Option, MultilineConfig,
            )
            itype = data.get('type', '')
            label = data.get('label', '')
            if isinstance(label, dict):
                label_tc = TextComponent(
                    text=label.get('text', str(label)),
                    color=label.get('color', 'white'),
                )
            else:
                label_tc = TextComponent(text=str(label))

            if itype == 'minecraft:boolean':
                ctrl = BooleanInput(label=label_tc, initial=data.get('initial', False))
            elif itype == 'minecraft:number_range':
                ctrl = NumberRangeInput(
                    label=label_tc, initial=data.get('initial', 0.0),
                    start=data.get('start', 0.0), end=data.get('end', 100.0),
                    step=data.get('step', 1.0),
                )
            elif itype == 'minecraft:single_option':
                options = []
                for opt in data.get('options', []):
                    if isinstance(opt, str):
                        options.append(Option(label=TextComponent(text=opt), value=opt))
                    elif isinstance(opt, dict):
                        opt_label = opt.get('label', {})
                        if isinstance(opt_label, dict):
                            opt_label_tc = TextComponent(text=opt_label.get('text', opt.get('value', '')))
                        else:
                            opt_label_tc = TextComponent(text=str(opt_label))
                        options.append(Option(label=opt_label_tc, value=opt.get('value', '')))
                ctrl = SingleOptionInput(label=label_tc, options=options)
            elif itype == 'minecraft:text':
                multiline = None
                if 'multiline' in data:
                    ml = data['multiline']
                    if isinstance(ml, dict):
                        multiline = MultilineConfig(enabled=True, max_lines=ml.get('max_lines', 5))
                    else:
                        multiline = MultilineConfig(enabled=bool(ml))
                ctrl = TextInput(
                    label=label_tc, initial=data.get('initial', ''),
                    placeholder=data.get('placeholder', ''),
                    multiline=multiline or MultilineConfig(),
                )
            else:
                return
            self.input_editor.add_input_from_clipboard(ctrl)

        elif item_type == 'action':
            self.action_editor.add_action_from_clipboard(data)