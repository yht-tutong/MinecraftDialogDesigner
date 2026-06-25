# import_dialog.py
# Minecraft Dialog Designer 导入预览确认对话框

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPlainTextEdit, QDialogButtonBox,
)
import json


class ImportPreviewDialog(QDialog):
    """导入预览确认对话框。

    显示待导入的 JSON 数据预览，让用户确认后再导入。
    """

    def __init__(self, data: dict, has_unsaved: bool = False, parent=None):
        super().__init__(parent)
        self.setWindowTitle("导入预览")
        self.resize(600, 500)
        self._confirmed = False

        layout = QVBoxLayout(self)

        # 标题
        title_label = QLabel("导入预览")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(title_label)

        # JSON 预览（只读）
        self._text_edit = QPlainTextEdit()
        self._text_edit.setReadOnly(True)
        json_text = json.dumps(data, indent=2, ensure_ascii=False)
        self._text_edit.setPlainText(json_text)
        layout.addWidget(self._text_edit)

        # 警告文本（如果有未保存更改）
        if has_unsaved:
            warning_label = QLabel("⚠ 当前对话框有未保存的更改，导入将覆盖当前内容。")
            warning_label.setStyleSheet("color: #ff9800; font-weight: bold;")
            layout.addWidget(warning_label)

        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.button(QDialogButtonBox.Ok).setText("确认导入")
        button_box.button(QDialogButtonBox.Cancel).setText("取消")
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _on_accept(self):
        self._confirmed = True
        self.accept()

    def is_confirmed(self) -> bool:
        return self._confirmed