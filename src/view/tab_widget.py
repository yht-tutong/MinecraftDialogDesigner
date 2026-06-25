# tab_widget.py
# Minecraft Dialog Designer 文档标签页组件 - 支持拖拽排序、关闭按钮和右键菜单

from PyQt5.QtWidgets import QTabWidget, QMenu, QAction, QMessageBox
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QKeySequence


class DocumentTabWidget(QTabWidget):
    """文档标签页组件。

    支持拖拽排序、关闭按钮、右键菜单和快捷键切换。
    """

    tab_context_menu_requested = pyqtSignal(int, object)  # index, QPoint

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMovable(True)
        self.setTabsClosable(True)
        self.setDocumentMode(True)
        self.setUsesScrollButtons(True)
        self.setElideMode(Qt.ElideRight)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_context_menu)

        self.tabCloseRequested.connect(self._on_tab_close_requested)

        self._on_close_tab = None  # 外部注入的回调
        self._on_close_others = None
        self._on_close_all = None

    def set_close_callback(self, callback):
        """设置关闭标签页的回调函数。callback(index) -> bool（返回 True 表示允许关闭）。"""
        self._on_close_tab = callback

    def set_close_others_callback(self, callback):
        """设置关闭其他标签页的回调函数。"""
        self._on_close_others = callback

    def set_close_all_callback(self, callback):
        """设置关闭所有标签页的回调函数。"""
        self._on_close_all = callback

    def _on_tab_close_requested(self, index: int):
        """标签页关闭按钮被点击。"""
        if self._on_close_tab:
            self._on_close_tab(index)

    def _on_context_menu(self, pos):
        """右键菜单。"""
        tab_index = self.tabBar().tabAt(pos)
        if tab_index < 0:
            return

        menu = QMenu(self)

        close_action = QAction("关闭", self)
        close_action.setShortcut(QKeySequence("Ctrl+W"))
        close_action.triggered.connect(lambda: self._on_tab_close_requested(tab_index))
        menu.addAction(close_action)

        close_others_action = QAction("关闭其他", self)
        close_others_action.triggered.connect(lambda: self._close_others(tab_index))
        menu.addAction(close_others_action)

        close_all_action = QAction("关闭所有", self)
        close_all_action.triggered.connect(lambda: self._close_all())
        menu.addAction(close_all_action)

        menu.exec_(self.mapToGlobal(pos))

    def _close_others(self, keep_index: int):
        """关闭除指定索引外的所有标签页。"""
        if self._on_close_others:
            self._on_close_others(keep_index)

    def _close_all(self):
        """关闭所有标签页。"""
        if self._on_close_all:
            self._on_close_all()

    def keyPressEvent(self, event):
        """处理 Ctrl+Tab 和 Ctrl+Shift+Tab 快捷键。"""
        if event.modifiers() == Qt.ControlModifier:
            if event.key() == Qt.Key_Tab:
                # 切换到下一个标签页
                if self.count() > 1:
                    next_idx = (self.currentIndex() + 1) % self.count()
                    self.setCurrentIndex(next_idx)
                return
        super().keyPressEvent(event)