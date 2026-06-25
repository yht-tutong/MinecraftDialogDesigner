# settings_interface.py
# Fluent 设置页面

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from qfluentwidgets import (
    ScrollArea, SettingCardGroup, SwitchSettingCard,
    ComboBox, PushButton, FluentIcon,
    CardWidget, InfoBar, InfoBarPosition, setTheme, Theme,
    SettingCard,
)

from src.config_utils import load_config, save_config, DEFAULT_CONFIG


class _ComboSettingCard(SettingCard):
    """简化版下拉设置卡片，不依赖 qconfig。"""

    def __init__(self, icon, title, content, texts, current_index, parent=None):
        super().__init__(icon, title, content, parent)
        self.comboBox = ComboBox()
        self.comboBox.addItems(texts)
        self.comboBox.setCurrentIndex(current_index)
        self.comboBox.setMinimumWidth(120)
        self.comboBox.setFont(QFont("Segoe UI", 12))
        self.hBoxLayout.addWidget(self.comboBox)
        self.hBoxLayout.addSpacing(16)


class SettingsInterface(ScrollArea):
    """Fluent 设置页面。

    提供主题、编辑器、导出等配置项的修改。
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("settingsInterface")
        self.setWidgetResizable(True)

        self._config = load_config()
        self._init_ui()

    def _init_ui(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(16)
        layout.setContentsMargins(16, 16, 16, 16)

        title_label = QLabel("设置")
        title_font = QFont("Segoe UI", 18, QFont.Bold)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        appearance_group = SettingCardGroup("外观", self)

        self._theme_card = _ComboSettingCard(
            FluentIcon.BRUSH,
            "主题",
            "选择界面主题",
            texts=["暗色", "亮色"],
            current_index=0 if self._config["ui"].get("theme", "dark") == "dark" else 1,
            parent=appearance_group,
        )
        self._theme_card.comboBox.currentIndexChanged.connect(self._on_theme_changed)
        appearance_group.addSettingCard(self._theme_card)

        self._animation_card = SwitchSettingCard(
            FluentIcon.VIDEO,
            "动画效果",
            "启用界面过渡动画",
            parent=appearance_group,
        )
        self._animation_card.switchButton.setChecked(
            self._config["ui"].get("animation_enabled", True)
        )
        appearance_group.addSettingCard(self._animation_card)

        self._tooltip_card = SwitchSettingCard(
            FluentIcon.HELP,
            "显示提示",
            "鼠标悬停时显示字段说明",
            parent=appearance_group,
        )
        self._tooltip_card.switchButton.setChecked(
            self._config["ui"].get("show_tooltips", True)
        )
        appearance_group.addSettingCard(self._tooltip_card)
        layout.addWidget(appearance_group)

        editor_group = SettingCardGroup("编辑器", self)

        interval_texts = ["关闭", "1分钟", "3分钟", "5分钟", "10分钟"]
        interval_map = {0: 0, 60: 1, 180: 2, 300: 3, 600: 4}
        current_interval = self._config["editor"].get("auto_save_interval", 300)
        self._autosave_card = _ComboSettingCard(
            FluentIcon.SAVE,
            "自动保存间隔",
            "设置自动保存的时间间隔",
            texts=interval_texts,
            current_index=interval_map.get(current_interval, 3),
            parent=editor_group,
        )
        editor_group.addSettingCard(self._autosave_card)
        layout.addWidget(editor_group)

        export_group = SettingCardGroup("导出", self)

        self._autovalidate_card = SwitchSettingCard(
            FluentIcon.COMPLETED,
            "自动验证",
            "导出时自动验证 JSON 格式",
            parent=export_group,
        )
        self._autovalidate_card.switchButton.setChecked(
            self._config["export"].get("auto_validate", True)
        )
        export_group.addSettingCard(self._autovalidate_card)
        layout.addWidget(export_group)

        save_btn = PushButton(FluentIcon.SAVE, "保存设置")
        save_btn.setFont(QFont("Segoe UI", 12))
        save_btn.clicked.connect(self._save_settings)
        layout.addWidget(save_btn)

        layout.addStretch()
        self.setWidget(container)

    def _on_theme_changed(self, index: int):
        """切换主题。"""
        theme = Theme.DARK if index == 0 else Theme.LIGHT
        setTheme(theme)

    def _save_settings(self):
        """保存设置到 config.json。"""
        self._config["ui"]["theme"] = "dark" if self._theme_card.comboBox.currentIndex() == 0 else "light"

        self._config["ui"]["animation_enabled"] = self._animation_card.switchButton.isChecked()
        self._config["ui"]["show_tooltips"] = self._tooltip_card.switchButton.isChecked()

        interval_map = {0: 0, 1: 60, 2: 180, 3: 300, 4: 600}
        self._config["editor"]["auto_save_interval"] = interval_map.get(
            self._autosave_card.comboBox.currentIndex(), 300
        )

        self._config["export"]["auto_validate"] = self._autovalidate_card.switchButton.isChecked()

        if save_config(self._config):
            InfoBar.success(
                "保存成功",
                "设置已保存到 config.json",
                duration=2000,
                position=InfoBarPosition.TOP_RIGHT,
                parent=self,
            )
        else:
            InfoBar.error(
                "保存失败",
                "无法写入 config.json",
                duration=2000,
                position=InfoBarPosition.TOP_RIGHT,
                parent=self,
            )