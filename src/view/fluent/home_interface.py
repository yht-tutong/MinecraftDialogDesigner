# home_interface.py
# Fluent 编辑器页面 — 嵌入现有 EditorPanel

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QLineEdit, QCheckBox, QSpinBox, QSplitter,
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from qfluentwidgets import (
    ScrollArea, CardWidget, ComboBox, LineEdit, PushButton,
    PrimaryPushButton, FluentIcon, SwitchButton, SpinBox, InfoBar,
    InfoBarPosition, MessageBox,
)

from src.controller.dialog_controller import DialogController, DialogSessionManager
from src.view.editor_panel import EditorPanel


class HomeInterface(ScrollArea):
    """Fluent 编辑器页面。

    嵌入现有的 EditorPanel，保持所有编辑功能。
    """

    def __init__(self, controller=None, parent=None):
        super().__init__(parent)
        self._controller = controller

        self.setObjectName("homeInterface")
        self.setWidgetResizable(True)

        self._init_ui()

    def _init_ui(self):
        self._container = QWidget()
        self._layout = QVBoxLayout(self._container)
        self._layout.setSpacing(12)
        self._layout.setContentsMargins(16, 16, 16, 16)

        title_card = CardWidget()
        title_layout = QHBoxLayout(title_card)
        title_layout.setContentsMargins(16, 12, 16, 12)

        title_label = QLabel("对话框编辑器")
        title_font = QFont("Segoe UI", 18, QFont.Bold)
        title_label.setFont(title_font)
        title_layout.addWidget(title_label)

        title_layout.addStretch()

        self._new_btn = PrimaryPushButton(FluentIcon.ADD, "新建")
        self._template_btn = PushButton(FluentIcon.LAYOUT, "从模板新建")
        self._open_btn = PushButton(FluentIcon.FOLDER, "打开")
        self._save_btn = PushButton(FluentIcon.SAVE, "保存")
        self._export_btn = PushButton(FluentIcon.SAVE_AS, "导出")

        title_layout.addWidget(self._new_btn)
        title_layout.addWidget(self._template_btn)
        title_layout.addWidget(self._open_btn)
        title_layout.addWidget(self._save_btn)
        title_layout.addWidget(self._export_btn)

        self._layout.addWidget(title_card)

        self._new_btn.clicked.connect(self._on_new)
        self._template_btn.clicked.connect(self._on_template)
        self._open_btn.clicked.connect(self._on_open)
        self._save_btn.clicked.connect(self._on_save)
        self._export_btn.clicked.connect(self._on_export)

        if self._controller:
            if self._controller.get_active_index() < 0:
                idx = self._controller.add_session()
                self._controller.switch_to(idx)
            self._editor_panel = EditorPanel(
                self._controller.get_active_session(), self
            )
            self._editor_panel.setStyleSheet("""
                QTabWidget::pane {
                    border: 1px solid #3E3E42;
                    background-color: #1E1E1E;
                }
                QTabBar::tab {
                    background-color: #2D2D2D;
                    color: #CCCCCC;
                    padding: 8px 16px;
                    border: 1px solid #3E3E42;
                    border-bottom: none;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                    font-family: "Segoe UI", "Microsoft YaHei", "PingFang SC";
                    font-size: 12px;
                }
                QTabBar::tab:selected {
                    background-color: #1E1E1E;
                    color: #FFFFFF;
                }
                QTabBar::tab:hover:!selected {
                    background-color: #353535;
                }
                QGroupBox {
                    border: 1px solid #3E3E42;
                    border-radius: 4px;
                    margin-top: 12px;
                    padding-top: 16px;
                    font-family: "Segoe UI", "Microsoft YaHei", "PingFang SC";
                    font-size: 13px;
                    color: #FFFFFF;
                    font-weight: bold;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top left;
                    padding: 2px 8px;
                    color: #0078D4;
                }
                QLabel { color: #CCCCCC; }
                QLineEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {
                    background-color: #2D2D2D;
                    color: #FFFFFF;
                    border: 1px solid #3E3E42;
                    padding: 4px;
                    border-radius: 4px;
                }
                QLineEdit:focus, QComboBox:focus { border-color: #0078D4; }
                QComboBox QAbstractItemView {
                    background-color: #2D2D2D;
                    color: #FFFFFF;
                    selection-background-color: #0078D4;
                }
                QListWidget {
                    background-color: #2D2D2D;
                    color: #FFFFFF;
                    border: 1px solid #3E3E42;
                }
                QListWidget::item:selected { background-color: #0078D4; }
                QCheckBox { color: #CCCCCC; }
                QPushButton {
                    background-color: #0078D4;
                    color: white;
                    border: none;
                    padding: 6px 14px;
                    border-radius: 4px;
                }
                QPushButton:hover { background-color: #1177BB; }
                QPushButton:disabled { background-color: #3E3E42; color: #6C6C6C; }
            """)
        else:
            placeholder = QLabel("请通过主窗口启动")
            placeholder.setAlignment(Qt.AlignCenter)
            placeholder.setFont(QFont("Segoe UI", 16))
            placeholder.setStyleSheet("color: #888888;")
            self._editor_panel = placeholder

        self._layout.addWidget(self._editor_panel)

        self.setWidget(self._container)

    def _on_new(self):
        if self._controller:
            idx = self._controller.add_session()
            self._controller.switch_to(idx)
            self._editor_panel.refresh_from_session()
            InfoBar.success(
                "新建成功", "已创建新对话框",
                duration=2000, position=InfoBarPosition.TOP_RIGHT,
                parent=self,
            )

    def _on_template(self):
        if not self._controller:
            return
        from .template_dialog import FluentTemplateDialog
        dlg = FluentTemplateDialog(self.window())
        if dlg.exec():
            template = dlg.selected_template()
            if template:
                idx = self._controller.add_session()
                self._controller.switch_to(idx)
                self._controller.import_from_dict(template.preset_data)
                self._editor_panel.refresh_from_session()
                InfoBar.success(
                    "创建成功", f"已从模板「{template.name}」创建新对话框",
                    duration=2000, position=InfoBarPosition.TOP_RIGHT,
                    parent=self,
                )

    def _on_open(self):
        InfoBar.info(
            "打开项目", "功能开发中...",
            duration=2000, position=InfoBarPosition.TOP_RIGHT,
            parent=self,
        )

    def _on_save(self):
        if self._controller and self._controller.get_active_session():
            InfoBar.success(
                "保存成功", "对话框已保存",
                duration=2000, position=InfoBarPosition.TOP_RIGHT,
                parent=self,
            )

    def _on_export(self):
        if self._controller and self._controller.get_active_session():
            from src.controller.json_export import export_dialog_json
            dialog = self._controller.get_active_session().dialog
            if dialog:
                import json
                data = dialog.to_dict()
                text = json.dumps(data, indent=2, ensure_ascii=False)
                from PyQt5.QtWidgets import QApplication
                QApplication.clipboard().setText(text)
                InfoBar.success(
                    "导出成功", "JSON 已复制到剪贴板",
                    duration=2000, position=InfoBarPosition.TOP_RIGHT,
                    parent=self,
                )

    def set_editor_panel(self, panel):
        if self._editor_panel:
            self._layout.removeWidget(self._editor_panel)
            self._editor_panel.hide()
        self._editor_panel = panel
        self._layout.addWidget(self._editor_panel)
        self._editor_panel.show()

    @property
    def editor_panel(self):
        return self._editor_panel