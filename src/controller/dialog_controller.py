# dialog_controller.py
# Minecraft Dialog Designer 会话管理器 - 管理多个对话框会话

from PyQt5.QtCore import QObject, pyqtSignal
from typing import Optional, Any
from ..model import *
from .dialog_session import DialogSession


class DialogSessionManager(QObject):
    """管理多个对话框会话（每个会话对应一个标签页）。

    维护有序会话列表，追踪活跃会话，提供向后兼容的代理方法。
    """

    # 信号
    session_added = pyqtSignal(int)        # index
    session_removed = pyqtSignal(int)       # index
    session_switched = pyqtSignal(int)      # new_index
    model_changed = pyqtSignal()            # 活跃会话的模型变更

    def __init__(self, parent=None):
        super().__init__(parent)
        self._sessions: list[DialogSession] = []
        self._active_index: int = -1
        self._unnamed_counter: int = 0

    # ---- 会话管理 ----

    def add_session(self, dialog: Optional[DialogBase] = None, file_path: str = None,
                    locked_fields: list = None) -> int:
        """创建新会话并添加到列表末尾。

        Args:
            dialog: 对话框模型，None 时创建默认 MultiActionDialog
            file_path: 文件路径，None 表示新文档
            locked_fields: 锁定字段列表

        Returns:
            新会话的索引
        """
        if dialog is None:
            dialog = MultiActionDialog(
                title=TextComponent("新对话框", color="aqua", bold=True)
            )

        self._unnamed_counter += 1
        session = DialogSession(
            dialog=dialog,
            file_path=file_path,
            modified=False,
            locked_fields=locked_fields or [],
        )
        session.set_tab_title(f"未命名-{self._unnamed_counter}")

        self._sessions.append(session)
        idx = len(self._sessions) - 1
        self.session_added.emit(idx)
        return idx

    def remove_session(self, index: int):
        """移除指定索引的会话。"""
        if 0 <= index < len(self._sessions):
            del self._sessions[index]
            self.session_removed.emit(index)
            # 调整活跃索引
            if self._sessions:
                if index == self._active_index:
                    new_idx = min(index, len(self._sessions) - 1)
                    self.switch_to(new_idx)
                elif index < self._active_index:
                    self._active_index -= 1
            else:
                self._active_index = -1

    def switch_to(self, index: int):
        """切换到指定索引的会话。"""
        if 0 <= index < len(self._sessions):
            self._active_index = index
            self.session_switched.emit(index)
            self.model_changed.emit()

    def get_active_session(self) -> Optional[DialogSession]:
        """返回当前活跃会话。"""
        if 0 <= self._active_index < len(self._sessions):
            return self._sessions[self._active_index]
        return None

    def get_session(self, index: int) -> Optional[DialogSession]:
        """返回指定索引的会话。"""
        if 0 <= index < len(self._sessions):
            return self._sessions[index]
        return None

    def get_sessions(self) -> list[DialogSession]:
        """返回所有会话的副本。"""
        return list(self._sessions)

    def get_active_index(self) -> int:
        """返回活跃会话索引。"""
        return self._active_index

    def session_count(self) -> int:
        """返回会话数量。"""
        return len(self._sessions)

    def reorder_sessions(self, from_index: int, to_index: int):
        """重新排序会话（标签页拖拽后调用）。"""
        if 0 <= from_index < len(self._sessions) and 0 <= to_index < len(self._sessions):
            session = self._sessions.pop(from_index)
            self._sessions.insert(to_index, session)
            # 调整活跃索引
            if from_index == self._active_index:
                self._active_index = to_index
            elif from_index < self._active_index <= to_index:
                self._active_index -= 1
            elif to_index <= self._active_index < from_index:
                self._active_index += 1

    # ---- 向后兼容的代理方法（操作活跃会话） ----

    def get_current(self) -> Optional[DialogBase]:
        """返回活跃会话的对话框模型。"""
        session = self.get_active_session()
        return session.dialog if session else None

    def set_type(self, dialog_type: str):
        """切换活跃会话的对话框类型，保留公共字段。"""
        session = self.get_active_session()
        if not session:
            return
        common = self._get_common_fields(session.dialog)
        type_map = {
            "minecraft:multi_action": MultiActionDialog,
            "minecraft:confirmation": ConfirmationDialog,
            "minecraft:dialog_list": DialogListDialog,
            "minecraft:notice": NoticeDialog,
            "minecraft:server_links": ServerLinksDialog,
            "minecraft:simple_input_form": SimpleInputFormDialog,
            "minecraft:multi_action_input_form": MultiActionInputDialog,
        }
        cls = type_map.get(dialog_type)
        if cls:
            session.dialog = cls(**common)
            session.modified = True
            self.model_changed.emit()

    def import_from_dict(self, data: dict):
        """从 dict 导入到活跃会话的对话框。"""
        session = self.get_active_session()
        if not session:
            return
        dlg_type = data.get("type", "minecraft:multi_action")

        title = data.get("title", {})
        if isinstance(title, dict):
            title = TextComponent(
                text=title.get("text", ""),
                color=title.get("color", "white"),
                bold=title.get("bold", False),
                italic=title.get("italic", False),
                underlined=title.get("underlined", False),
            )

        body = []
        raw_body = data.get("body", [])
        if isinstance(raw_body, list):
            for elem in raw_body:
                be = self._parse_body_element(elem)
                if be:
                    body.append(be)
        elif isinstance(raw_body, dict):
            be = self._parse_body_element(raw_body)
            if be:
                body.append(be)

        inputs = []
        for inp in data.get("inputs", []):
            ic = self._parse_input_control(inp)
            if ic:
                inputs.append(ic)

        actions = []
        for act in data.get("actions", []):
            a = self._parse_action_wrapper(act)
            if a:
                actions.append(a)

        exit_action = None
        if "exit_action" in data:
            ea = data["exit_action"]
            if isinstance(ea, dict):
                exit_action = self._parse_action(ea)

        yes_action = None
        if "yes" in data:
            yes_action = self._parse_action_wrapper(data["yes"])

        no_action = None
        if "no" in data:
            no_action = self._parse_action_wrapper(data["no"])

        notice_action = None
        if "action" in data and dlg_type == "minecraft:notice":
            notice_action = self._parse_action_wrapper(data["action"])

        external_title = None
        if "external_title" in data:
            et = data["external_title"]
            if isinstance(et, dict):
                external_title = TextComponent(
                    text=et.get("text", ""),
                    color=et.get("color", "white"),
                    bold=et.get("bold", False),
                    italic=et.get("italic", False),
                    underlined=et.get("underlined", False),
                )
            else:
                external_title = TextComponent(text=str(et))

        common = {
            "title": title,
            "body": body,
            "inputs": inputs,
            "pause": data.get("pause", True),
            "can_close_with_escape": data.get("can_close_with_escape", True),
            "after_action": data.get("after_action", "close"),
            "external_title": external_title,
        }

        if dlg_type == "minecraft:multi_action":
            session.dialog = MultiActionDialog(
                **common, actions=actions,
                columns=data.get("columns", 2), exit_action=exit_action,
            )
        elif dlg_type == "minecraft:confirmation":
            session.dialog = ConfirmationDialog(
                **common, yes=yes_action, no=no_action,
            )
        elif dlg_type == "minecraft:dialog_list":
            session.dialog = DialogListDialog(
                **common, dialogs=data.get("dialogs", []),
                columns=data.get("columns", 2), button_width=data.get("button_width", 150),
                exit_action=exit_action,
            )
        elif dlg_type == "minecraft:notice":
            session.dialog = NoticeDialog(**common, action=notice_action)
        elif dlg_type == "minecraft:server_links":
            session.dialog = ServerLinksDialog(
                **common, columns=data.get("columns", 2),
                button_width=data.get("button_width", 150), exit_action=exit_action,
            )
        elif dlg_type == "minecraft:simple_input_form":
            simple_action = None
            if "action" in data:
                simple_action = self._parse_submit_method(data["action"])
            session.dialog = SimpleInputFormDialog(**common, action=simple_action)
        elif dlg_type == "minecraft:multi_action_input_form":
            submit_actions = []
            for act in data.get("actions", []):
                sm = self._parse_submit_method(act)
                if sm:
                    submit_actions.append(sm)
            session.dialog = MultiActionInputDialog(
                **common, actions=submit_actions,
                columns=data.get("columns", 2),
            )
        else:
            session.dialog = MultiActionDialog(
                **common, actions=actions,
                columns=data.get("columns", 2), exit_action=exit_action,
            )

        session.modified = True
        self.model_changed.emit()

    def new_dialog(self):
        """重置活跃会话为默认对话框。"""
        session = self.get_active_session()
        if session:
            session.dialog = MultiActionDialog(
                title=TextComponent("新对话框", color="aqua", bold=True)
            )
            session.file_path = None
            session.modified = False
            session.locked_fields = []
            self._unnamed_counter += 1
            session.set_tab_title(f"未命名-{self._unnamed_counter}")
            self.model_changed.emit()

    def set_dialog(self, data: dict):
        """从 dict 加载到活跃会话。"""
        if isinstance(data, dict):
            self.import_from_dict(data)
        else:
            self.new_dialog()

    def export_to_dict(self) -> dict:
        """导出活跃会话的对话框为 dict。"""
        session = self.get_active_session()
        if session and session.dialog:
            return session.dialog.to_dict()
        return {}

    # ---- 内部辅助方法 ----

    def _get_common_fields(self, dialog: DialogBase) -> dict:
        if not dialog:
            return {}
        return {
            "title": dialog.title,
            "body": list(dialog.body),
            "inputs": list(dialog.inputs),
            "pause": dialog.pause,
            "can_close_with_escape": dialog.can_close_with_escape,
            "after_action": dialog.after_action,
            "external_title": dialog.external_title,
        }

    def _parse_body_element(self, elem: dict):
        btype = elem.get("type", "")
        if btype == "minecraft:plain_message":
            contents = elem.get("contents", {})
            if isinstance(contents, dict):
                tc = TextComponent(
                    text=contents.get("text", ""),
                    color=contents.get("color", "white"),
                    bold=contents.get("bold", False),
                    italic=contents.get("italic", False),
                    underlined=contents.get("underlined", False),
                )
            else:
                tc = TextComponent(text=str(contents))
            return PlainMessageElement(text=tc)
        elif btype == "minecraft:item":
            desc = None
            if "description" in elem:
                desc_data = elem["description"]
                if isinstance(desc_data, dict):
                    desc = PlainMessageElement(text=TextComponent(
                        text=desc_data.get("contents", {}).get("text", ""),
                        color=desc_data.get("contents", {}).get("color", "white"),
                    ))
            return ItemElement(
                item=elem.get("item", "minecraft:stone"),
                count=elem.get("count", 1),
                description=desc,
                components=elem.get("components", {}),
            )
        return None

    def _parse_input_control(self, inp: dict):
        itype = inp.get("type", "")
        label = inp.get("label", "")
        if isinstance(label, dict):
            label_tc = TextComponent(
                text=label.get("text", str(label)),
                color=label.get("color", "white"),
                bold=label.get("bold", False),
                italic=label.get("italic", False),
                underlined=label.get("underlined", False),
            )
        else:
            label_tc = TextComponent(text=str(label))

        if itype == "minecraft:boolean":
            return BooleanInput(label=label_tc, initial=inp.get("initial", False))
        elif itype == "minecraft:number_range":
            return NumberRangeInput(
                label=label_tc, initial=inp.get("initial", 0.0),
                start=inp.get("start", 0.0), end=inp.get("end", 100.0),
                step=inp.get("step", 1.0),
            )
        elif itype == "minecraft:single_option":
            options = []
            for opt in inp.get("options", []):
                if isinstance(opt, str):
                    options.append(Option(label=TextComponent(text=opt), value=opt))
                elif isinstance(opt, dict):
                    opt_label = opt.get("label", {})
                    if isinstance(opt_label, dict):
                        opt_label_tc = TextComponent(text=opt_label.get("text", opt.get("value", "")))
                    else:
                        opt_label_tc = TextComponent(text=str(opt_label))
                    options.append(Option(label=opt_label_tc, value=opt.get("value", "")))
            return SingleOptionInput(
                label=label_tc, options=options,
                default=inp.get("initial", ""),
            )
        elif itype == "minecraft:text":
            multiline = None
            if "multiline" in inp:
                ml = inp["multiline"]
                if isinstance(ml, dict):
                    multiline = MultilineConfig(enabled=True, max_lines=ml.get("max_lines", 5))
                else:
                    multiline = MultilineConfig(enabled=bool(ml))
            return TextInput(
                label=label_tc, default=inp.get("initial", ""),
                placeholder=inp.get("placeholder", ""),
                multiline=multiline or MultilineConfig(),
            )
        return None

    def _parse_action(self, act: dict) -> Optional[Action]:
        if not act:
            return None
        atype = act.get("type", "")
        if atype == "minecraft:dynamic/run_command":
            return DynamicRunCommandAction(command=act.get("command", ""))
        elif atype == "minecraft:dynamic/custom":
            return DynamicCustomAction(command=act.get("command", ""))
        else:
            params = dict(act)
            params.pop("type", None)
            return StaticAction(action_type=atype, params=params)

    def _parse_action_wrapper(self, wrapper: dict) -> Optional[Action]:
        if not wrapper:
            return None
        inner = wrapper.get("action", {})
        if not inner:
            return None
        return self._parse_action(inner)

    def _parse_submit_method(self, data: dict):
        stype = data.get("type", "")
        if stype == "minecraft:command_template":
            return CommandTemplateSubmitMethod(template=data.get("template", ""))
        elif stype == "minecraft:custom_form":
            return CustomFormSubmitMethod(id=data.get("id", ""))
        elif stype == "minecraft:custom_template":
            return CustomTemplateSubmitMethod(
                id=data.get("id", ""), additions=data.get("additions", {}),
            )
        return None


# 向后兼容别名
DialogController = DialogSessionManager