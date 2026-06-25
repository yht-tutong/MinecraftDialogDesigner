# preview_panel.py
# Minecraft Dialog Designer JSON 实时预览面板

from PyQt5.QtWidgets import QPlainTextEdit, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtGui import QFont, QColor, QTextCharFormat, QSyntaxHighlighter, QFontDatabase
from PyQt5.QtCore import QRegularExpression, pyqtSignal, QTimer
import json


class JsonHighlighter(QSyntaxHighlighter):
    """Basic JSON syntax highlighter."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._rules = []
        # Keys
        key_fmt = QTextCharFormat()
        key_fmt.setForeground(QColor("#9C93FF"))
        key_fmt.setFontWeight(QFont.Bold)
        self._rules.append((QRegularExpression(r'"[^"]*"\s*:'), key_fmt))
        # Strings
        str_fmt = QTextCharFormat()
        str_fmt.setForeground(QColor("#CE9178"))
        self._rules.append((QRegularExpression(r'"[^"]*"'), str_fmt))
        # Numbers
        num_fmt = QTextCharFormat()
        num_fmt.setForeground(QColor("#B5CEA8"))
        self._rules.append((QRegularExpression(r'\b\d+\.?\d*\b'), num_fmt))
        # Booleans
        bool_fmt = QTextCharFormat()
        bool_fmt.setForeground(QColor("#569CD6"))
        self._rules.append((QRegularExpression(r'\b(true|false)\b'), bool_fmt))
        # Null
        null_fmt = QTextCharFormat()
        null_fmt.setForeground(QColor("#569CD6"))
        self._rules.append((QRegularExpression(r'\bnull\b'), null_fmt))

    def highlightBlock(self, text):
        for pattern, fmt in self._rules:
            it = pattern.globalMatch(text)
            while it.hasNext():
                match = it.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)


class PreviewPanel(QWidget):
    """实时 JSON 预览面板，支持双向编辑——修改 JSON 文本会同步更新模型。"""

    json_edited = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # 顶部栏：标题 + 格式化按钮
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(0, 0, 0, 0)
        label = QLabel("JSON 预览")
        label.setStyleSheet("font-weight: bold; padding: 4px;")
        top_bar.addWidget(label)
        top_bar.addStretch()
        self._format_btn = QPushButton("Format JSON")
        self._format_btn.setFixedHeight(24)
        self._format_btn.clicked.connect(self._format_json)
        top_bar.addWidget(self._format_btn)
        layout.addLayout(top_bar)

        # 编辑器（可编辑）
        self._editor = QPlainTextEdit()
        self._editor.setReadOnly(False)
        self._editor.setFont(QFontDatabase.systemFont(QFontDatabase.FixedFont))
        font = QFont("Consolas", 10)
        if not font.exactMatch():
            font = QFont("Courier New", 10)
        self._editor.setFont(font)
        self._editor.setStyleSheet("background-color: #1E1E1E; color: #D4D4D4;")
        self._highlighter = JsonHighlighter(self._editor.document())
        self._editor.textChanged.connect(self._on_text_changed)
        layout.addWidget(self._editor)

        # 错误标签（初始隐藏）
        self._error_label = QLabel()
        self._error_label.setStyleSheet(
            "color: #F44747; background-color: #1E1E1E; "
            "padding: 4px; font-size: 11px;"
        )
        self._error_label.setWordWrap(True)
        self._error_label.setVisible(False)
        layout.addWidget(self._error_label)

        # 防抖定时器（300ms）
        self._debounce_timer = QTimer()
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.timeout.connect(self._parse_and_emit)

        self._suppress_signals = False

    def _on_text_changed(self):
        """文本变更时启动防抖定时器。"""
        if self._suppress_signals:
            return
        self._debounce_timer.start(300)

    def _parse_and_emit(self):
        """解析当前 JSON 文本，有效则发出 json_edited 信号，无效则显示错误。"""
        text = self._editor.toPlainText()
        if not text.strip():
            self._error_label.setVisible(False)
            return
        try:
            data = json.loads(text)
            self._error_label.setVisible(False)
            self.json_edited.emit(data)
        except json.JSONDecodeError as e:
            self._error_label.setText(f"JSON 解析错误: {e}")
            self._error_label.setVisible(True)

    def _format_json(self):
        """格式化当前 JSON 文本（2 空格缩进）。"""
        text = self._editor.toPlainText()
        try:
            data = json.loads(text)
            formatted = json.dumps(data, indent=2, ensure_ascii=False)
            self._suppress_signals = True
            self._editor.setPlainText(formatted)
            self._suppress_signals = False
            self._error_label.setVisible(False)
        except json.JSONDecodeError as e:
            self._error_label.setText(f"JSON 解析错误: {e}")
            self._error_label.setVisible(True)

    def set_text(self, text: str):
        """设置文本区域内容，不触发变更信号（防止循环更新）。"""
        self._suppress_signals = True
        self._editor.setPlainText(text)
        self._suppress_signals = False
        self._error_label.setVisible(False)

    def update_json(self, data: dict):
        """Update the preview with formatted JSON."""
        try:
            text = json.dumps(data, indent=2, ensure_ascii=False)
            self.set_text(text)
        except Exception:
            self.set_text("{}")