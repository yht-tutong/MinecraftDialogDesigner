# main_window.py
# Fluent Design 主窗口

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont
from qfluentwidgets import (
    FluentWindow, FluentIcon, NavigationItemPosition,
    MessageBox, InfoBar, InfoBarPosition, ScrollArea,
)

from .home_interface import HomeInterface
from .settings_interface import SettingsInterface


class FluentMainWindow(FluentWindow):
    """Fluent Design 主窗口。

    左侧导航栏，右侧内容区，支持页面切换。
    """

    def __init__(self, controller=None, parent=None):
        super().__init__(parent)
        self._controller = controller

        self.setWindowTitle("Minecraft Dialog Designer")
        self.resize(1280, 800)
        self.setMinimumSize(900, 600)

        self._home_interface = HomeInterface(controller, self)
        self._settings_interface = SettingsInterface(self)

        self._init_navigation()
        self._init_styles()

    def _init_navigation(self):
        """初始化导航栏。"""
        self.addSubInterface(
            self._home_interface,
            FluentIcon.EDIT,
            "编辑器",
            position=NavigationItemPosition.TOP,
        )

        self.addSubInterface(
            self._settings_interface,
            FluentIcon.SETTING,
            "设置",
            position=NavigationItemPosition.BOTTOM,
        )

        about_widget = ScrollArea()
        about_widget.setObjectName("aboutInterface")
        about_layout = QVBoxLayout(about_widget)
        about_layout.setAlignment(Qt.AlignCenter)
        
        about_label = QLabel("Minecraft Dialog Designer v1.1.0\n\n"
                             "基于 PyQt-Fluent-Widgets 构建\n"
                             "作者: Tutong\n"
                             "B站: https://space.bilibili.com/630095673")
        about_label.setAlignment(Qt.AlignCenter)
        about_label.setFont(QFont("Segoe UI", 14))
        about_label.setStyleSheet("color: #888888;")
        about_layout.addWidget(about_label)

        self.addSubInterface(
            about_widget,
            FluentIcon.INFO,
            "关于",
            position=NavigationItemPosition.BOTTOM,
        )

    def _init_styles(self):
        """初始化样式 - 统一导航栏和菜单颜色。"""
        self.navigationInterface.setStyleSheet("""
            NavigationBar {
                background-color: #1E1E1E;
                border-right: 1px solid #3E3E42;
            }
            NavigationItem {
                color: #CCCCCC;
                font-family: "Segoe UI", "Microsoft YaHei", "PingFang SC";
                font-size: 13px;
            }
            NavigationItem:hover {
                background-color: #2D2D2D;
            }
            NavigationItem:selected {
                color: #FFFFFF;
                background-color: #0078D4;
            }
        """)

    def switch_to_editor(self):
        """切换到编辑器页面。"""
        self.switchTo(self._home_interface)

    @property
    def home_interface(self):
        return self._home_interface

    @property
    def settings_interface(self):
        return self._settings_interface