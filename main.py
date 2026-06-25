# main.py
# Minecraft Dialog Designer 主入口 — 支持 Fluent / Classic 双模式

import sys
import os
import argparse
import traceback

# Ensure the src directory is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt
from src.config_utils import load_config


def _start_classic(config):
    """启动经典 PyQt5 原生 GUI。"""
    from src.controller.dialog_controller import DialogController
    from src.view.main_window import MainWindow

    app = QApplication(sys.argv)
    app.setApplicationName(config["app"]["name"])
    app.setApplicationVersion(config["app"]["version"])
    app.setOrganizationName("Tutong")
    app.setStyle("Fusion")
    app.setStyleSheet(CLASSIC_QSS)

    controller = DialogController()
    window = MainWindow(controller=controller)
    window.setWindowTitle("Minecraft Dialog Designer")
    window.resize(1200, 800)
    window.show()
    window.raise_()
    window.activateWindow()

    sys.exit(app.exec_())


def _start_fluent(config):
    """启动 Fluent Design GUI。"""
    from qfluentwidgets import FluentWindow, setTheme, Theme, setFont
    from src.view.fluent.main_window import FluentMainWindow
    from src.controller.dialog_controller import DialogController
    from PyQt5.QtGui import QFont

    theme = Theme.DARK if config["ui"].get("theme", "dark") == "dark" else Theme.LIGHT
    setTheme(theme)

    app = QApplication(sys.argv)
    app.setApplicationName(config["app"]["name"])
    app.setApplicationVersion(config["app"]["version"])
    app.setOrganizationName("Tutong")

    global_font = QFont("Segoe UI", 10)
    global_font.setFamilies(["Segoe UI", "Microsoft YaHei", "PingFang SC", "Arial"])
    app.setFont(global_font)

    controller = DialogController()
    window = FluentMainWindow(controller=controller)
    window.show()

    sys.exit(app.exec_())


def main():
    parser = argparse.ArgumentParser(
        description="Minecraft Dialog Designer",
        prog="python main.py",
    )
    parser.add_argument(
        "--classic", action="store_true",
        help="使用经典 PyQt5 原生 GUI（默认使用 Fluent Design）",
    )
    parser.add_argument(
        "--fluent", action="store_true",
        help="使用 Fluent Design GUI（默认）",
    )
    args = parser.parse_args()

    # 加载配置
    config = load_config()

    # 高 DPI 支持
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    try:
        if args.classic:
            _start_classic(config)
        else:
            _start_fluent(config)
    except Exception as e:
        print(f"\n[错误] 程序启动失败:", file=sys.stderr)
        traceback.print_exc()
        try:
            QMessageBox.critical(None, "启动错误", f"程序启动失败:\n{str(e)}")
        except Exception:
            pass
        sys.exit(1)


# 经典模式 QSS 样式表
CLASSIC_QSS = """
    QMainWindow { background-color: #2D2D30; }
    QWidget { background-color: #2D2D30; color: #D4D4D4; font-size: 13px; }
    QMenuBar { background-color: #2D2D30; color: #D4D4D4; border-bottom: 1px solid #3E3E42; }
    QMenuBar::item:selected { background-color: #3E3E42; }
    QMenu { background-color: #2D2D30; color: #D4D4D4; border: 1px solid #3E3E42; }
    QMenu::item:selected { background-color: #094771; }
    QToolBar { background-color: #2D2D30; border-bottom: 1px solid #3E3E42; spacing: 4px; }
    QPushButton { background-color: #0E639C; color: white; border: none; padding: 6px 14px; border-radius: 3px; min-height: 24px; }
    QPushButton:hover { background-color: #1177BB; }
    QPushButton:pressed { background-color: #094771; }
    QPushButton:disabled { background-color: #3E3E42; color: #6C6C6C; }
    QLineEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox, QComboBox { background-color: #3C3C3C; color: #D4D4D4; border: 1px solid #5A5A5A; padding: 4px; border-radius: 2px; }
    QLineEdit:focus, QPlainTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus { border-color: #0E639C; }
    QComboBox::drop-down { border: none; }
    QComboBox QAbstractItemView { background-color: #3C3C3C; color: #D4D4D4; selection-background-color: #094771; }
    QListWidget { background-color: #3C3C3C; color: #D4D4D4; border: 1px solid #5A5A5A; border-radius: 2px; }
    QListWidget::item:selected { background-color: #094771; }
    QTabWidget::pane { background-color: #2D2D30; border: 1px solid #3E3E42; }
    QTabBar::tab { background-color: #2D2D30; color: #D4D4D4; padding: 8px 16px; border: 1px solid #3E3E42; border-bottom: none; border-top-left-radius: 4px; border-top-right-radius: 4px; }
    QTabBar::tab:selected { background-color: #3E3E42; }
    QTabBar::tab:hover:!selected { background-color: #353535; }
    QCheckBox { spacing: 6px; }
    QCheckBox::indicator { width: 16px; height: 16px; }
    QGroupBox { border: 1px solid #5A5A5A; border-radius: 4px; margin-top: 12px; padding-top: 16px; font-weight: bold; }
    QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 2px 8px; color: #9C93FF; }
    QSplitter::handle { background-color: #3E3E42; width: 3px; }
    QStatusBar { background-color: #007ACC; color: white; }
    QScrollBar:vertical { background-color: #2D2D30; width: 12px; }
    QScrollBar::handle:vertical { background-color: #5A5A5A; border-radius: 4px; min-height: 24px; }
    QScrollBar::handle:vertical:hover { background-color: #7A7A7A; }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
"""


if __name__ == "__main__":
    main()