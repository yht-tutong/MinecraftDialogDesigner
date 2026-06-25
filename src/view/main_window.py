# main_window.py
# Minecraft Dialog Designer 主窗口 - 多标签页编辑

from PyQt5.QtWidgets import (
    QMainWindow, QTabWidget, QSplitter, QStatusBar, QMenuBar,
    QToolBar, QAction, QFileDialog, QMessageBox, QWidget, QVBoxLayout,
    QApplication, QLabel, QComboBox, QDialog, QShortcut,
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QKeySequence
import json
import os

from .dialog_editor import DialogEditor
from .body_editor import BodyEditor
from .input_editor import InputEditor
from .action_editor import ActionEditor
from .preview_panel import PreviewPanel
from .visual_preview import VisualPreview
from .import_dialog import ImportPreviewDialog
from .template_dialog import TemplateSelectDialog
from .editor_panel import EditorPanel
from .tab_widget import DocumentTabWidget
from .animation_utils import fade_in

from ..controller.dialog_controller import DialogSessionManager, DialogController
from ..controller.json_export import export_to_json, import_from_json, import_dialog_from_json, save_project, load_project
from ..model import *
from ..model.templates import TemplateData, get_builtin_templates


class MainWindow(QMainWindow):
    """Minecraft Dialog Designer 主窗口。

    支持多标签页编辑，每个标签页对应一个独立的对话框文档。
    包含菜单栏、工具栏、文档标签栏、编辑器面板和状态栏。
    """

    def __init__(self, controller: DialogSessionManager, parent=None):
        super().__init__(parent)
        self._controller = controller
        self._internal_clipboard = None  # {"type": "body"|"input"|"action", "data": {...}}

        self.setWindowTitle("Minecraft Dialog Designer")
        self.resize(1280, 860)
        self.setAcceptDrops(True)

        self._build_menu_bar()
        self._build_toolbar()
        self._build_central()
        self._build_status_bar()

        # 连接控制器信号
        controller.model_changed.connect(self._on_model_changed)
        controller.session_switched.connect(self._on_session_switched)

        # 创建初始标签页
        self._add_initial_tab()

    # ---- 菜单栏 ----

    def _build_menu_bar(self):
        menu_bar = self.menuBar()

        # 文件菜单
        file_menu = menu_bar.addMenu("文件(&F)")

        new_action = QAction("新建(&N)", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self._new_file)
        file_menu.addAction(new_action)

        open_action = QAction("打开(&O)...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._open_file)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        save_action = QAction("保存(&S)", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self._save_file)
        file_menu.addAction(save_action)

        save_as_action = QAction("另存为(&A)...", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self._save_as_file)
        file_menu.addAction(save_as_action)

        save_all_action = QAction("全部保存(&L)", self)
        save_all_action.setShortcut("Ctrl+Shift+L")
        save_all_action.triggered.connect(self._save_all)
        file_menu.addAction(save_all_action)

        file_menu.addSeparator()

        export_action = QAction("导出 JSON(&E)...", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self._export_json)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        import_action = QAction("导入 JSON(&I)...", self)
        import_action.setShortcut("Ctrl+I")
        import_action.triggered.connect(self._import_json)
        file_menu.addAction(import_action)

        clipboard_import_action = QAction("从剪贴板导入(&V)", self)
        clipboard_import_action.setShortcut("Ctrl+Shift+V")
        clipboard_import_action.triggered.connect(self._import_from_clipboard)
        file_menu.addAction(clipboard_import_action)

        file_menu.addSeparator()

        close_tab_action = QAction("关闭标签页(&W)", self)
        close_tab_action.setShortcut("Ctrl+W")
        close_tab_action.triggered.connect(self._close_active_tab)
        file_menu.addAction(close_tab_action)

        file_menu.addSeparator()

        exit_action = QAction("退出(&X)", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 模板菜单
        template_menu = menu_bar.addMenu("模板(&T)")

        new_from_template_action = QAction("从模板新建(&N)...", self)
        new_from_template_action.setShortcut("Ctrl+T")
        new_from_template_action.triggered.connect(self._new_from_template)
        template_menu.addAction(new_from_template_action)

    # ---- 工具栏 ----

    def _build_toolbar(self):
        toolbar = QToolBar("主工具栏")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        new_btn = QAction("新建", self)
        new_btn.triggered.connect(self._new_file)
        toolbar.addAction(new_btn)

        open_btn = QAction("打开", self)
        open_btn.triggered.connect(self._open_file)
        toolbar.addAction(open_btn)

        save_btn = QAction("保存", self)
        save_btn.triggered.connect(self._save_file)
        toolbar.addAction(save_btn)

        toolbar.addSeparator()

        export_btn = QAction("导出 JSON", self)
        export_btn.triggered.connect(self._export_json)
        toolbar.addAction(export_btn)

        import_btn = QAction("导入 JSON", self)
        import_btn.triggered.connect(self._import_json)
        toolbar.addAction(import_btn)

        toolbar.addSeparator()

        # 对话框类型快速切换
        toolbar.addWidget(QLabel(" 类型: "))
        self._toolbar_type_combo = QComboBox()
        self._toolbar_type_combo.setToolTip("快速切换对话框类型，保留公共字段")
        self._toolbar_type_combo.addItems([
            "multi_action",
            "confirmation",
            "dialog_list",
            "notice",
            "server_links",
            "simple_input_form",
            "multi_action_input_form",
        ])
        self._toolbar_type_combo.currentTextChanged.connect(self._on_toolbar_type_changed)
        toolbar.addWidget(self._toolbar_type_combo)

        toolbar.addSeparator()

        template_btn = QAction("从模板新建", self)
        template_btn.triggered.connect(self._new_from_template)
        toolbar.addAction(template_btn)

        self._unlock_btn = QAction("解锁模板", self)
        self._unlock_btn.triggered.connect(self._unlock_template)
        self._unlock_btn.setVisible(False)
        toolbar.addAction(self._unlock_btn)

        toolbar.addSeparator()

        close_tab_btn = QAction("关闭标签页", self)
        close_tab_btn.triggered.connect(self._close_active_tab)
        toolbar.addAction(close_tab_btn)

    # ---- 中央控件 ----

    def _build_central(self):
        """创建文档标签栏 + 编辑器面板的布局。"""
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 文档标签栏
        self.doc_tabs = DocumentTabWidget()
        self.doc_tabs.set_close_callback(self._close_tab)
        self.doc_tabs.set_close_others_callback(self._close_other_tabs)
        self.doc_tabs.set_close_all_callback(self._close_all_tabs)
        self.doc_tabs.currentChanged.connect(self._on_doc_tab_changed)
        self.doc_tabs.tabBar().tabMoved.connect(self._on_tab_moved)
        layout.addWidget(self.doc_tabs)

        self.setCentralWidget(central_widget)

    def _add_initial_tab(self):
        """创建初始标签页。"""
        idx = self._controller.add_session()
        self._controller.switch_to(idx)
        self._add_editor_tab(idx)

    def _add_editor_tab(self, session_index: int):
        """为指定会话索引创建编辑器面板标签页。"""
        session = self._controller.get_session(session_index)
        if not session:
            return

        panel = EditorPanel(session)
        panel.changed.connect(self._on_panel_changed)
        panel.json_edited.connect(self._on_json_edited)
        panel.copy_requested.connect(self._on_copy_requested)
        panel.paste_requested.connect(self._on_paste_requested)

        title = session.display_title()
        self.doc_tabs.addTab(panel, title)
        self.doc_tabs.setCurrentWidget(panel)
        # 存储 panel 引用以便后续查找
        self.doc_tabs.widget(session_index).setProperty("session_index", session_index)

    def _get_active_panel(self) -> EditorPanel:
        """获取当前活跃的编辑器面板。"""
        widget = self.doc_tabs.currentWidget()
        if isinstance(widget, EditorPanel):
            return widget
        return None

    def _get_panel_for_index(self, index: int) -> EditorPanel:
        """获取指定索引的编辑器面板。"""
        for i in range(self.doc_tabs.count()):
            widget = self.doc_tabs.widget(i)
            if isinstance(widget, EditorPanel) and widget.get_session() == self._controller.get_session(index):
                return widget
        return None

    # ---- 状态栏 ----

    def _build_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel("就绪")
        self.status_bar.addPermanentWidget(self.status_label)

    # ---- 信号处理 ----

    def _on_panel_changed(self):
        """编辑器面板内容变更。"""
        session = self._controller.get_active_session()
        if session:
            session.modified = True
        self._update_tab_title()
        self._on_model_changed()

    def _on_json_edited(self, data: dict):
        """JSON 预览编辑后同步到会话。"""
        self._controller.import_from_dict(data)
        panel = self._get_active_panel()
        if panel:
            panel.refresh_from_session()
        session = self._controller.get_active_session()
        if session:
            session.modified = True
        self._update_tab_title()

    def _on_model_changed(self):
        """控制器模型变更时更新窗口标题。"""
        session = self._controller.get_active_session()
        if session:
            file_path = session.file_path
            modified = session.modified
            if file_path:
                marker = " *" if modified else ""
                title = f"{os.path.basename(file_path)}{marker} - Minecraft Dialog Designer"
            else:
                marker = " *" if modified else ""
                title = f"{session.display_title().replace(' *', '')}{marker} - Minecraft Dialog Designer"
            self.setWindowTitle(title)

    def _on_session_switched(self, index: int):
        """会话切换时同步工具栏。"""
        session = self._controller.get_session(index)
        if not session:
            return

        # 同步类型下拉框
        dialog = session.dialog
        short_type = dialog.type.replace("minecraft:", "") if dialog.type else "multi_action"
        idx = self._toolbar_type_combo.findText(short_type)
        if idx >= 0:
            self._toolbar_type_combo.blockSignals(True)
            self._toolbar_type_combo.setCurrentIndex(idx)
            self._toolbar_type_combo.blockSignals(False)

        # 同步解锁按钮
        if session.locked_fields:
            self._unlock_btn.setVisible(True)
        else:
            self._unlock_btn.setVisible(False)

    def _on_doc_tab_changed(self, index: int):
        """文档标签页切换。"""
        if index < 0:
            return
        # 切换到对应会话
        self._controller.switch_to(index)
        # 更新窗口标题
        self._on_model_changed()
        # 淡入动画
        widget = self.doc_tabs.widget(index)
        if widget:
            fade_in(widget, 250)

    def _on_tab_moved(self, from_index: int, to_index: int):
        """标签页拖拽排序后同步会话顺序。"""
        self._controller.reorder_sessions(from_index, to_index)

    def _on_toolbar_type_changed(self, short_type: str):
        """工具栏类型下拉框切换。"""
        if not short_type:
            return
        full_type = f"minecraft:{short_type}"
        self._controller.set_type(full_type)
        panel = self._get_active_panel()
        if panel:
            panel.refresh_from_session()
        self._update_tab_title()

    # ---- 标签页标题更新 ----

    def _update_tab_title(self):
        """更新活跃标签页的标题。"""
        idx = self.doc_tabs.currentIndex()
        session = self._controller.get_active_session()
        if session and idx >= 0:
            self.doc_tabs.setTabText(idx, session.display_title())

    # ---- 文件操作 ----

    def _new_file(self):
        """创建新标签页。"""
        idx = self._controller.add_session()
        self._controller.switch_to(idx)
        self._add_editor_tab(idx)
        self._unlock_btn.setVisible(False)
        self.status_label.setText("新建对话框")

    def _open_file(self):
        """打开文件到新标签页。"""
        path, _ = QFileDialog.getOpenFileName(
            self, "打开项目", "", "Dialog 项目 (*.json);;所有文件 (*)"
        )
        if not path:
            return
        try:
            dialog_data = load_project(path)
            if not dialog_data:
                QMessageBox.critical(self, "打开失败", "无法读取项目文件。")
                return

            idx = self._controller.add_session(file_path=path)
            self._controller.switch_to(idx)
            self._controller.import_from_dict(dialog_data)
            session = self._controller.get_active_session()
            session.modified = False
            self._add_editor_tab(idx)
            self._update_tab_title()
            self._unlock_btn.setVisible(False)
            self.status_label.setText(f"已打开: {path}")
        except Exception as e:
            QMessageBox.critical(self, "打开失败", f"无法打开文件:\n{e}")

    def _save_file(self):
        """保存当前活跃标签页。"""
        session = self._controller.get_active_session()
        if not session:
            return

        panel = self._get_active_panel()
        if panel:
            panel.sync_to_session()

        if session.file_path:
            try:
                save_project(session.dialog, session.file_path)
                session.modified = False
                self._update_tab_title()
                self._on_model_changed()
                self.status_label.setText(f"已保存: {session.file_path}")
            except Exception as e:
                QMessageBox.critical(self, "保存失败", f"无法保存文件:\n{e}")
        else:
            self._save_as_file()

    def _save_as_file(self):
        """另存为当前活跃标签页。"""
        session = self._controller.get_active_session()
        if not session:
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "另存为", "", "Dialog 项目 (*.json);;所有文件 (*)"
        )
        if not path:
            return

        panel = self._get_active_panel()
        if panel:
            panel.sync_to_session()

        try:
            save_project(session.dialog, path)
            session.file_path = path
            session.modified = False
            self._update_tab_title()
            self._on_model_changed()
            self.status_label.setText(f"已保存: {path}")
        except Exception as e:
            QMessageBox.critical(self, "保存失败", f"无法保存文件:\n{e}")

    def _save_all(self):
        """保存所有未保存的标签页。"""
        for i in range(self.doc_tabs.count()):
            widget = self.doc_tabs.widget(i)
            if isinstance(widget, EditorPanel):
                session = widget.get_session()
                if session.modified and session.file_path:
                    widget.sync_to_session()
                    try:
                        save_project(session.dialog, session.file_path)
                        session.modified = False
                    except Exception:
                        pass
        self._update_tab_title()
        self._on_model_changed()
        self.status_label.setText("已全部保存")

    def _export_json(self):
        """导出当前活跃标签页的对话框。"""
        session = self._controller.get_active_session()
        if not session:
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "导出 JSON", "", "JSON 文件 (*.json);;所有文件 (*)"
        )
        if not path:
            return

        panel = self._get_active_panel()
        if panel:
            panel.sync_to_session()

        try:
            export_to_json(session.dialog, path)
            self.status_label.setText(f"已导出: {path}")
        except Exception as e:
            QMessageBox.critical(self, "导出失败", f"无法导出 JSON:\n{e}")

    def _import_json(self):
        """从 JSON 文件导入到新标签页。"""
        path, _ = QFileDialog.getOpenFileName(
            self, "导入 JSON", "", "JSON 文件 (*.json);;所有文件 (*)"
        )
        if not path:
            return
        data = import_dialog_from_json(path)
        if data is None:
            QMessageBox.critical(self, "导入失败", "无法读取 JSON 文件，请检查文件格式。")
            return

        preview = ImportPreviewDialog(data, has_unsaved=False, parent=self)
        if preview.exec_() != QDialog.Accepted or not preview.is_confirmed():
            return

        idx = self._controller.add_session()
        self._controller.switch_to(idx)
        self._controller.import_from_dict(data)
        self._add_editor_tab(idx)
        self._unlock_btn.setVisible(False)
        self.status_label.setText(f"已导入: {path}")

    def _import_from_clipboard(self):
        """从剪贴板导入到新标签页。"""
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        if not text:
            QMessageBox.warning(self, "导入失败", "剪贴板为空。")
            return

        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            QMessageBox.warning(self, "导入失败", "剪贴板内容不是有效的 JSON。")
            return

        if not isinstance(data, dict):
            QMessageBox.warning(self, "导入失败", "剪贴板内容不是有效的对话框 JSON 对象。")
            return

        preview = ImportPreviewDialog(data, has_unsaved=False, parent=self)
        if preview.exec_() != QDialog.Accepted or not preview.is_confirmed():
            return

        idx = self._controller.add_session()
        self._controller.switch_to(idx)
        self._controller.import_from_dict(data)
        self._add_editor_tab(idx)
        self._unlock_btn.setVisible(False)
        self.status_label.setText("已从剪贴板导入")

    def _maybe_save(self) -> bool:
        """检查活跃标签页是否有未保存更改。"""
        session = self._controller.get_active_session()
        if not session or not session.modified:
            return True
        ret = QMessageBox.warning(
            self, "未保存的更改",
            f"当前对话框有未保存的更改，是否保存？",
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
        )
        if ret == QMessageBox.Save:
            self._save_file()
            return True
        elif ret == QMessageBox.Discard:
            return True
        else:
            return False

    # ---- 标签页关闭 ----

    def _close_active_tab(self):
        """关闭当前活跃标签页。"""
        idx = self.doc_tabs.currentIndex()
        if idx >= 0:
            self._close_tab(idx)

    def _close_tab(self, index: int):
        """关闭指定索引的标签页。"""
        if not self._maybe_save_tab(index):
            return

        self.doc_tabs.removeTab(index)
        self._controller.remove_session(index)

        if self._controller.session_count() == 0:
            # 没有标签页了，创建一个默认的
            self._add_initial_tab()

    def _close_other_tabs(self, keep_index: int):
        """关闭除指定索引外的所有标签页。"""
        # 需要从后往前关闭，避免索引变化
        for i in range(self.doc_tabs.count() - 1, -1, -1):
            if i != keep_index:
                if self._maybe_save_tab(i):
                    self.doc_tabs.removeTab(i)
                    self._controller.remove_session(i)

    def _close_all_tabs(self):
        """关闭所有标签页。"""
        for i in range(self.doc_tabs.count() - 1, -1, -1):
            if self._maybe_save_tab(i):
                self.doc_tabs.removeTab(i)
                self._controller.remove_session(i)

        if self._controller.session_count() == 0:
            self._add_initial_tab()

    def _maybe_save_tab(self, index: int) -> bool:
        """检查指定标签页是否有未保存更改。"""
        session = self._controller.get_session(index)
        if not session or not session.modified:
            return True
        ret = QMessageBox.warning(
            self, "未保存的更改",
            f"\"{session.display_title().replace(' *', '')}\" 有未保存的更改，是否保存？",
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
        )
        if ret == QMessageBox.Save:
            if session.file_path:
                try:
                    save_project(session.dialog, session.file_path)
                    session.modified = False
                except Exception:
                    QMessageBox.critical(self, "保存失败", "无法保存文件。")
                    return False
            else:
                # 需要另存为
                self._save_as_file()
                if session.modified:
                    return False
            return True
        elif ret == QMessageBox.Discard:
            return True
        else:
            return False

    # ---- 窗口事件 ----

    def closeEvent(self, event):
        """关闭窗口时检查所有标签页。"""
        for i in range(self.doc_tabs.count() - 1, -1, -1):
            if not self._maybe_save_tab(i):
                event.ignore()
                return
        event.accept()

    # ---- 拖拽导入 ----

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.toLocalFile().endswith('.json'):
                    event.accept()
                    return
        event.ignore()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            filepath = url.toLocalFile()
            if filepath.endswith('.json'):
                data = import_dialog_from_json(filepath)
                if data is None:
                    QMessageBox.critical(self, "导入失败", f"无法读取 JSON 文件:\n{filepath}")
                    return

                preview = ImportPreviewDialog(data, has_unsaved=False, parent=self)
                if preview.exec_() != QDialog.Accepted or not preview.is_confirmed():
                    return

                idx = self._controller.add_session()
                self._controller.switch_to(idx)
                self._controller.import_from_dict(data)
                self._add_editor_tab(idx)
                self._unlock_btn.setVisible(False)
                self.status_label.setText(f"已导入: {filepath}")
                return

    # ---- 模板功能 ----

    def _new_from_template(self):
        """从模板创建新标签页。"""
        dlg = TemplateSelectDialog(self)
        if dlg.exec_() != QDialog.Accepted:
            return

        template = dlg.selected_template()
        if template is None:
            return

        idx = self._controller.add_session(locked_fields=list(template.locked_fields))
        self._controller.switch_to(idx)
        self._controller.import_from_dict(template.preset_data)
        session = self._controller.get_active_session()
        session.modified = False
        self._add_editor_tab(idx)

        panel = self._get_active_panel()
        if panel:
            panel.apply_locked_fields()
        self._unlock_btn.setVisible(True)
        self.status_label.setText(f"已从模板创建: {template.name}")

    def _unlock_template(self):
        """解锁当前模板。"""
        session = self._controller.get_active_session()
        if session:
            session.locked_fields = []
        panel = self._get_active_panel()
        if panel:
            panel.unlock_all()
        self._unlock_btn.setVisible(False)
        self.status_label.setText("模板已解锁，可自由编辑")

    # ---- 跨标签页复制粘贴 ----

    def _on_copy_requested(self, item_type: str, data: dict):
        """处理编辑器复制请求，存入内部剪贴板。"""
        self._internal_clipboard = {"type": item_type, "data": data}
        type_names = {"body": "正文元素", "input": "输入控件", "action": "动作"}
        self.status_label.setText(f"已复制 {type_names.get(item_type, item_type)} 到剪贴板")

    def _on_paste_requested(self, item_type: str):
        """处理编辑器粘贴请求，从内部剪贴板读取并粘贴。"""
        if not self._internal_clipboard:
            self.status_label.setText("剪贴板为空，无法粘贴")
            return
        if self._internal_clipboard["type"] != item_type:
            self.status_label.setText(f"剪贴板类型不匹配（剪贴板: {self._internal_clipboard['type']}, 当前: {item_type}）")
            return
        panel = self._get_active_panel()
        if panel:
            panel.paste_from_clipboard(item_type, self._internal_clipboard["data"])
            type_names = {"body": "正文元素", "input": "输入控件", "action": "动作"}
            self.status_label.setText(f"已粘贴 {type_names.get(item_type, item_type)}")

    def copy_to_internal_clipboard(self, item_type: str, data: dict):
        """复制到内部剪贴板（直接调用）。"""
        self._internal_clipboard = {"type": item_type, "data": data}
        self.status_label.setText(f"已复制 {item_type} 到剪贴板")

    def paste_from_internal_clipboard(self, target_type: str) -> dict:
        """从内部剪贴板粘贴。返回数据 dict 或 None。"""
        if self._internal_clipboard and self._internal_clipboard["type"] == target_type:
            return self._internal_clipboard["data"]
        return None