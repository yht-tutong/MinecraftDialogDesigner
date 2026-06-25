# visual_preview.py
# Minecraft 对话框可视化预览面板 - 使用 QPainter + Minecraft 纹理模拟游戏内渲染效果

import os
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QRect, QRectF, QPoint
from PyQt5.QtGui import (
    QPainter, QColor, QFont, QPen, QBrush, QPixmap, QFontMetrics
)

# ── Minecraft 颜色映射 ──────────────────────────────────────────────
COLOR_MAP = {
    "black":        QColor(0, 0, 0),
    "dark_blue":    QColor(0, 0, 170),
    "dark_green":   QColor(0, 170, 0),
    "dark_aqua":    QColor(0, 170, 170),
    "dark_red":     QColor(170, 0, 0),
    "dark_purple":  QColor(170, 0, 170),
    "gold":         QColor(255, 170, 0),
    "gray":         QColor(170, 170, 170),
    "dark_gray":    QColor(85, 85, 85),
    "blue":         QColor(85, 85, 255),
    "green":        QColor(85, 255, 85),
    "aqua":         QColor(85, 255, 255),
    "red":          QColor(255, 85, 85),
    "light_purple": QColor(255, 85, 255),
    "yellow":       QColor(255, 255, 85),
    "white":        QColor(255, 255, 255),
}

# ── 常用 translate key 映射 ─────────────────────────────────────────
TRANSLATE_MAP = {
    "gui.ok":                   "确定",
    "gui.yes":                  "是",
    "gui.no":                   "否",
    "gui.done":                 "完成",
    "gui.cancel":               "取消",
    "gui.back":                 "返回",
    "gui.continue":             "继续",
    "gui.proceed":              "继续",
    "gui.quit":                 "退出",
    "gui.close":                "关闭",
    "gui.next":                 "下一步",
    "gui.prev":                 "上一步",
    "gui.accept":               "接受",
    "gui.decline":              "拒绝",
    "options.generic_value":    "值",
    "options.on":               "开",
    "options.off":              "关",
    "menu.play":                "开始游戏",
    "menu.quit":                "退出游戏",
    "menu.options":             "选项",
    "menu.returnToMenu":        "返回主菜单",
    "menu.disconnect":          "断开连接",
    "menu.shareToLan":          "对局域网开放",
    "selectServer.delete":      "删除",
    "selectServer.refresh":     "刷新",
    "selectServer.edit":        "编辑",
    "selectServer.select":      "加入服务器",
    "selectServer.add":         "添加服务器",
    "selectServer.direct":      "直接连接",
    "addServer.title":          "添加服务器",
    "editServer.title":         "编辑服务器信息",
    "directConnect.title":      "直接连接",
    "multiplayerWarning.check": "不再显示此屏幕",
    "resourcePack.title":       "资源包",
    "resourcePack.available":   "可用资源包",
    "resourcePack.selected":    "已选资源包",
    "socialInteractions.title": "社交互动",
    "controls.title":           "控制",
    "controls.reset":           "重置",
    "controls.keybinds":        "键位",
    "options.title":            "选项",
    "options.video":            "视频设置",
    "options.language":         "语言",
    "options.chat":             "聊天设置",
    "options.sounds":           "音乐和声音",
    "options.skinCustomization": "皮肤自定义",
    "options.accessibility":    "辅助功能",
    "options.resourcepack":     "资源包",
    "options.credits":          "制作人员",
    "selectWorld.title":        "选择世界",
    "selectWorld.create":       "创建新的世界",
    "selectWorld.edit":         "编辑",
    "selectWorld.delete":       "删除",
    "selectWorld.recreate":     "重建",
    "selectWorld.search":       "搜索",
    "createWorld.customize":    "自定义",
    "createWorld.reset":        "重置",
    "createWorld.moreOptions":  "更多选项",
    "datapackFailure.title":    "数据包错误",
    "datapackFailure.safeMode": "安全模式",
}


def _resolve_text_component(component, default_text=""):
    """将 TextComponent（dict 或对象）解析为纯文本字符串。

    支持:
      - {"text": "..."} 普通文本
      - {"translate": "key"} 翻译键
      - {"extra": [...]} 递归子组件
      - 对象属性访问 (obj.text / obj.translate)
    """
    if component is None:
        return default_text

    if isinstance(component, str):
        return component

    if isinstance(component, dict):
        # translate 优先
        if "translate" in component:
            key = component["translate"]
            return TRANSLATE_MAP.get(key, key)
        # text 字段
        if "text" in component:
            text = component["text"]
            if isinstance(text, str):
                return text
        # extra 数组
        if "extra" in component:
            extras = component["extra"]
            if isinstance(extras, list):
                return "".join(_resolve_text_component(e, "") for e in extras)
        return default_text

    # 对象属性访问
    if hasattr(component, "translate"):
        key = component.translate
        return TRANSLATE_MAP.get(key, key)
    if hasattr(component, "text"):
        return str(component.text)
    if hasattr(component, "extra"):
        extras = component.extra
        if isinstance(extras, list):
            return "".join(_resolve_text_component(e, "") for e in extras)

    return str(component)


def _get_text_style(component):
    """从 TextComponent 中提取颜色和样式属性。"""
    if component is None:
        return "white", False, False, False

    if isinstance(component, dict):
        return (
            component.get("color", "white"),
            component.get("bold", False),
            component.get("italic", False),
            component.get("underlined", False),
        )
    if hasattr(component, "color"):
        return (
            getattr(component, "color", "white"),
            getattr(component, "bold", False),
            getattr(component, "italic", False),
            getattr(component, "underlined", False),
        )
    return "white", False, False, False


# ── 按钮区域记录（用于 hover 检测）─────────────────────────────────
class _ButtonRect:
    """记录一个按钮的绘制区域和关联数据。"""
    __slots__ = ("rect", "label", "is_warning", "action_data")
    def __init__(self, rect, label, is_warning=False, action_data=None):
        self.rect = rect
        self.label = label
        self.is_warning = is_warning
        self.action_data = action_data


# ── VisualPreview ───────────────────────────────────────────────────
class VisualPreview(QWidget):
    """Minecraft 对话框可视化预览面板，使用 QPainter 模拟游戏内渲染效果。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(300, 200)
        self.setMouseTracking(True)

        self._dialog_data = {}
        self._bg_color = QColor(72, 60, 50)

        # 按钮区域记录
        self._buttons: list[_ButtonRect] = []
        self._hovered_index = -1

        # ── 加载纹理 ──────────────────────────────────────────────
        self._textures = {}
        self._load_textures()

    # ── 纹理加载 ────────────────────────────────────────────────────
    def _load_textures(self):
        """加载 Minecraft 对话框纹理，若文件不存在则设为 None。"""
        asset_dir = os.path.join(os.path.dirname(__file__), "assets", "dialog")
        texture_files = {
            "background":              "background.webp",
            "button":                  "button.png",
            "button_highlighted":      "button_highlighted.png",
            "warning_button":          "warning_button.png",
            "warning_button_highlighted": "warning_button_highlighted.png",
            "checkbox":                "checkbox.png",
            "checkbox_selected":       "checkbox_selected.png",
            "slider":                  "slider.png",
            "slider_handle":           "slider_handle.png",
            "text_field":              "text_field.png",
        }
        for key, filename in texture_files.items():
            path = os.path.join(asset_dir, filename)
            if os.path.isfile(path):
                self._textures[key] = QPixmap(path)
            else:
                self._textures[key] = None

    # ── 公共接口 ────────────────────────────────────────────────────
    def update_dialog(self, data: dict):
        """更新对话框数据并重绘。"""
        self._dialog_data = data
        self.update()

    # ── 鼠标事件 ────────────────────────────────────────────────────
    def mouseMoveEvent(self, event):
        """检测鼠标悬停在按钮上的状态。"""
        pos = event.pos()
        new_hover = -1
        for i, btn in enumerate(self._buttons):
            if btn.rect.contains(pos):
                new_hover = i
                break
        if new_hover != self._hovered_index:
            self._hovered_index = new_hover
            self.update()

    def mousePressEvent(self, event):
        """鼠标点击按钮时触发（预留接口，当前无实际动作）。"""
        if event.button() == Qt.LeftButton:
            pos = event.pos()
            for btn in self._buttons:
                if btn.rect.contains(pos):
                    # 预留：未来可在此处发射信号
                    break

    def leaveEvent(self, event):
        """鼠标离开控件时清除 hover 状态。"""
        if self._hovered_index != -1:
            self._hovered_index = -1
            self.update()

    # ── 主绘制入口 ──────────────────────────────────────────────────
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 清除按钮记录
        self._buttons.clear()

        # 背景
        painter.fillRect(self.rect(), self._bg_color)

        if not self._dialog_data:
            painter.setPen(QColor(255, 255, 255))
            painter.setFont(QFont("Microsoft YaHei", 14))
            painter.drawText(self.rect(), Qt.AlignCenter, "暂无对话框数据")
            painter.end()
            return

        # ── 计算缩放与布局 ─────────────────────────────────────────
        w = self.width()
        h = self.height()

        # 对话框宽度：容器宽度的 80%
        dialog_w = int(w * 0.8)
        # 16:10 宽高比 → 高度 = 宽度 / 1.6
        dialog_h = int(dialog_w / 1.6)
        if dialog_h > h - 20:
            dialog_h = h - 20
            dialog_w = int(dialog_h * 1.6)

        dialog_x = (w - dialog_w) // 2
        dialog_y = (h - dialog_h) // 2

        # dialog_px 比例因子（以 400px 宽为基准）
        dialog_px = dialog_w / 400.0

        # ── 绘制对话框背景 ─────────────────────────────────────────
        bg_tex = self._textures.get("background")
        if bg_tex and not bg_tex.isNull():
            painter.drawPixmap(QRect(dialog_x, dialog_y, dialog_w, dialog_h), bg_tex)
        else:
            painter.setPen(QPen(QColor(55, 55, 55), 2))
            painter.setBrush(QBrush(QColor(198, 198, 198)))
            painter.drawRoundedRect(dialog_x, dialog_y, dialog_w, dialog_h, 4, 4)

        # ── 布局常量 ───────────────────────────────────────────────
        margin = int(12 * dialog_px)
        title_h = int(28 * dialog_px)
        footer_h = int(50 * dialog_px)
        body_top = dialog_y + title_h + int(8 * dialog_px)
        footer_top = dialog_y + dialog_h - footer_h

        body_available_h = footer_top - body_top
        input_area_h = int(80 * dialog_px)
        body_area_h = body_available_h - input_area_h
        if body_area_h < 20:
            body_area_h = body_available_h // 2
            input_area_h = body_available_h - body_area_h

        input_top = body_top + body_area_h

        # ── 绘制标题 ───────────────────────────────────────────────
        self._draw_title(painter, dialog_x, dialog_y, dialog_w, title_h, dialog_px)

        # ── 绘制分隔线 ─────────────────────────────────────────────
        sep_y = dialog_y + title_h + int(2 * dialog_px)
        painter.setPen(QPen(QColor(55, 55, 55), max(1, int(1 * dialog_px))))
        painter.drawLine(
            dialog_x + margin, sep_y,
            dialog_x + dialog_w - margin, sep_y
        )

        # ── 绘制正文 ───────────────────────────────────────────────
        self._draw_body(painter, dialog_x, body_top, dialog_w, body_area_h, margin, dialog_px)

        # ── 绘制输入控件 ───────────────────────────────────────────
        self._draw_inputs(painter, dialog_x, input_top, dialog_w, input_area_h, margin, dialog_px)

        # ── 绘制底部按钮 ───────────────────────────────────────────
        self._draw_actions(painter, dialog_x, footer_top, dialog_w, footer_h, margin, dialog_px)

        painter.end()

    # ── 标题绘制 ────────────────────────────────────────────────────
    def _draw_title(self, painter, x, y, w, title_h, dp):
        title_data = self._dialog_data.get("title", {})
        title_text = _resolve_text_component(title_data, "")
        title_color, title_bold, title_italic, title_underline = _get_text_style(title_data)

        font_size = max(8, int(11 * dp))
        font = QFont("Microsoft YaHei", font_size)
        font.setBold(title_bold)
        font.setItalic(title_italic)
        font.setUnderline(title_underline)
        painter.setFont(font)
        painter.setPen(COLOR_MAP.get(title_color, QColor(255, 255, 255)))
        painter.drawText(QRect(x, y, w, title_h), Qt.AlignCenter, title_text)

    # ── 正文绘制 ────────────────────────────────────────────────────
    def _draw_body(self, painter, x, y, w, body_h, margin, dp):
        body = self._dialog_data.get("body", [])
        if isinstance(body, dict):
            body = [body]
        if not body:
            return

        font_size = max(7, int(9 * dp))
        body_font = QFont("Microsoft YaHei", font_size)
        line_h = max(14, int(22 * dp))
        cur_y = y + int(4 * dp)

        for elem in body:
            if not isinstance(elem, dict):
                continue

            elem_type = elem.get("type", "")

            if elem_type == "minecraft:plain_message":
                # 内容可能在 "contents" 或 "text" 字段中
                contents = elem.get("contents", elem.get("text", ""))
                text = _resolve_text_component(contents, "")
                color, bold, italic, underline = _get_text_style(contents)

                font = QFont("Microsoft YaHei", font_size)
                font.setBold(bold)
                font.setItalic(italic)
                font.setUnderline(underline)
                painter.setFont(font)
                painter.setPen(COLOR_MAP.get(color, QColor(255, 255, 255)))
                painter.drawText(
                    QRect(x + margin, cur_y, w - 2 * margin, line_h),
                    Qt.AlignLeft | Qt.AlignVCenter, text
                )
                cur_y += line_h

            elif elem_type == "minecraft:item":
                item_id = elem.get("item", "?")
                self._draw_item(painter, x + margin, cur_y, dp, item_id)
                # 如果有 description，显示在旁边
                desc = elem.get("description")
                if desc:
                    desc_text = _resolve_text_component(desc, "")
                    desc_color, desc_bold, desc_italic, desc_underline = _get_text_style(desc)
                    font = QFont("Microsoft YaHei", font_size)
                    font.setBold(desc_bold)
                    font.setItalic(desc_italic)
                    font.setUnderline(desc_underline)
                    painter.setFont(font)
                    painter.setPen(COLOR_MAP.get(desc_color, QColor(255, 255, 255)))
                    icon_w = int(20 * dp)
                    painter.drawText(
                        QRect(x + margin + icon_w + int(4 * dp), cur_y, w - 2 * margin - icon_w - int(4 * dp), line_h),
                        Qt.AlignLeft | Qt.AlignVCenter, desc_text
                    )
                cur_y += line_h

            if cur_y > y + body_h - line_h:
                break

    # ── 物品绘制 ────────────────────────────────────────────────────
    def _draw_item(self, painter, ix, iy, dp, item_id):
        icon_size = int(20 * dp)
        # Level 1: 彩色矩形 + 缩写
        try:
            abbr = self._item_abbreviation(item_id)
            rect = QRect(ix, iy + int(1 * dp), icon_size, icon_size)
            painter.setPen(QPen(QColor(100, 100, 100), 1))
            painter.setBrush(QBrush(QColor(139, 139, 139)))
            painter.drawRect(rect)

            font = QFont("Microsoft YaHei", max(5, int(7 * dp)))
            painter.setFont(font)
            painter.setPen(QColor(255, 255, 255))
            painter.drawText(rect, Qt.AlignCenter, abbr)
            return
        except Exception:
            pass

        # Level 2: 显示 item ID
        try:
            font = QFont("Microsoft YaHei", max(5, int(7 * dp)))
            painter.setFont(font)
            painter.setPen(QColor(200, 200, 200))
            painter.drawText(QRect(ix, iy, icon_size, icon_size), Qt.AlignCenter, item_id[:4])
            return
        except Exception:
            pass

        # Level 3: "?"
        painter.setPen(QPen(QColor(100, 100, 100), 1))
        painter.setBrush(QBrush(QColor(139, 139, 139)))
        painter.drawRect(QRect(ix, iy, icon_size, icon_size))
        font = QFont("Microsoft YaHei", max(5, int(7 * dp)))
        painter.setFont(font)
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(QRect(ix, iy, icon_size, icon_size), Qt.AlignCenter, "?")

    @staticmethod
    def _item_abbreviation(item_id):
        """从 item ID 提取缩写，如 'minecraft:diamond' → 'Di'。"""
        name = item_id.split(":")[-1] if ":" in item_id else item_id
        if not name:
            return "?"
        parts = name.split("_")
        if len(parts) >= 2:
            return (parts[0][:1] + parts[1][:1]).upper()
        return name[:2].upper()

    # ── 输入控件绘制 ────────────────────────────────────────────────
    def _draw_inputs(self, painter, x, y, w, area_h, margin, dp):
        inputs = self._dialog_data.get("inputs", [])
        if not inputs:
            return

        font_size = max(7, int(9 * dp))
        input_font = QFont("Microsoft YaHei", font_size)
        line_h = max(14, int(22 * dp))
        cur_y = y + int(2 * dp)

        for inp in inputs:
            if not isinstance(inp, dict):
                continue

            inp_type = inp.get("type", "")
            label_data = inp.get("label", {})
            label_text = _resolve_text_component(label_data, "")

            if inp_type == "minecraft:boolean":
                self._draw_boolean_input(painter, x + margin, cur_y, dp, label_text, inp)
            elif inp_type == "minecraft:number_range":
                self._draw_number_range_input(painter, x + margin, cur_y, w - 2 * margin, dp, label_text, inp)
            elif inp_type == "minecraft:single_option":
                self._draw_single_option_input(painter, x + margin, cur_y, w - 2 * margin, dp, label_text, inp)
            elif inp_type == "minecraft:text":
                self._draw_text_input(painter, x + margin, cur_y, w - 2 * margin, dp, label_text, inp)

            cur_y += line_h
            if cur_y > y + area_h - line_h:
                break

    def _draw_boolean_input(self, painter, ix, iy, dp, label_text, inp):
        """绘制布尔复选框控件。"""
        checkbox_size = int(16 * dp)
        initial = inp.get("initial", False)

        tex = self._textures.get("checkbox_selected" if initial else "checkbox")
        if tex and not tex.isNull():
            scaled = tex.scaled(
                checkbox_size, checkbox_size,
                Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            painter.drawPixmap(ix, iy, scaled)
        else:
            # Fallback: 绘制矩形
            painter.setPen(QPen(QColor(100, 100, 100), 1))
            painter.setBrush(QBrush(QColor(200, 200, 200)))
            painter.drawRect(QRect(ix, iy + int(1 * dp), checkbox_size - 2, checkbox_size - 2))
            if initial:
                painter.setPen(QPen(QColor(60, 60, 60), 2))
                painter.drawLine(ix + 2, iy + checkbox_size // 2, ix + checkbox_size // 2, iy + checkbox_size - 4)
                painter.drawLine(ix + checkbox_size // 2, iy + checkbox_size - 4, ix + checkbox_size - 3, iy + 2)

        # 标签文本
        label_color, label_bold, label_italic, label_underline = _get_text_style(inp.get("label"))
        font_size = max(7, int(9 * dp))
        font = QFont("Microsoft YaHei", font_size)
        font.setBold(label_bold)
        font.setItalic(label_italic)
        font.setUnderline(label_underline)
        painter.setFont(font)
        painter.setPen(COLOR_MAP.get(label_color, QColor(64, 64, 64)))
        text_x = ix + checkbox_size + int(6 * dp)
        painter.drawText(QRect(text_x, iy, 200, checkbox_size), Qt.AlignLeft | Qt.AlignVCenter, label_text)

    def _draw_number_range_input(self, painter, ix, iy, w, dp, label_text, inp):
        """绘制数值范围滑块控件。"""
        start = inp.get("start", 0)
        end = inp.get("end", 100)
        initial = inp.get("initial", start)

        slider_w = int(120 * dp)
        slider_h = int(20 * dp)

        # 标签
        label_color, label_bold, label_italic, label_underline = _get_text_style(inp.get("label"))
        font_size = max(7, int(9 * dp))
        font = QFont("Microsoft YaHei", font_size)
        font.setBold(label_bold)
        font.setItalic(label_italic)
        font.setUnderline(label_underline)
        painter.setFont(font)
        painter.setPen(COLOR_MAP.get(label_color, QColor(64, 64, 64)))
        painter.drawText(QRect(ix, iy, int(80 * dp), slider_h), Qt.AlignLeft | Qt.AlignVCenter, label_text)

        slider_x = ix + int(85 * dp)

        # 滑块背景
        slider_tex = self._textures.get("slider")
        if slider_tex and not slider_tex.isNull():
            scaled = slider_tex.scaled(slider_w, int(6 * dp), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
            painter.drawPixmap(slider_x, iy + int(7 * dp), scaled)
        else:
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor(100, 100, 100)))
            painter.drawRoundedRect(QRect(slider_x, iy + int(7 * dp), slider_w, int(6 * dp)), 3, 3)

        # 滑块手柄位置
        if end != start:
            ratio = (initial - start) / (end - start)
        else:
            ratio = 0.5
        ratio = max(0.0, min(1.0, ratio))
        handle_x = slider_x + int((slider_w - int(8 * dp)) * ratio)

        # 滑块手柄
        handle_tex = self._textures.get("slider_handle")
        handle_size = int(12 * dp)
        if handle_tex and not handle_tex.isNull():
            scaled = handle_tex.scaled(handle_size, handle_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            painter.drawPixmap(handle_x, iy + int(4 * dp), scaled)
        else:
            painter.setPen(QPen(QColor(60, 60, 60), 1))
            painter.setBrush(QBrush(QColor(180, 180, 180)))
            painter.drawRoundedRect(QRect(handle_x, iy + int(4 * dp), handle_size, handle_size), 3, 3)

        # 当前值显示
        painter.setPen(QColor(64, 64, 64))
        val_str = str(int(initial)) if isinstance(initial, float) and initial == int(initial) else str(initial)
        painter.drawText(
            QRect(slider_x + slider_w + int(4 * dp), iy, int(40 * dp), slider_h),
            Qt.AlignLeft | Qt.AlignVCenter, val_str
        )

    def _draw_single_option_input(self, painter, ix, iy, w, dp, label_text, inp):
        """绘制单选按钮控件。"""
        options = inp.get("options", [])
        default_val = inp.get("default", "")

        # 标签
        label_color, label_bold, label_italic, label_underline = _get_text_style(inp.get("label"))
        font_size = max(7, int(9 * dp))
        font = QFont("Microsoft YaHei", font_size)
        font.setBold(label_bold)
        font.setItalic(label_italic)
        font.setUnderline(label_underline)
        painter.setFont(font)
        painter.setPen(COLOR_MAP.get(label_color, QColor(64, 64, 64)))
        painter.drawText(QRect(ix, iy, int(80 * dp), int(20 * dp)), Qt.AlignLeft | Qt.AlignVCenter, label_text)

        opt_x = ix + int(85 * dp)
        for opt in options:
            if not isinstance(opt, dict):
                continue
            opt_label = _resolve_text_component(opt.get("label"), "")
            opt_value = opt.get("value", "")
            is_selected = (opt_value == default_val)

            # Radio circle
            radio_size = int(10 * dp)
            painter.setPen(QPen(QColor(100, 100, 100), 1))
            painter.setBrush(QBrush(QColor(200, 200, 200) if not is_selected else QColor(100, 100, 100)))
            painter.drawEllipse(QRect(opt_x, iy + int(5 * dp), radio_size, radio_size))

            # Option text
            painter.setPen(QColor(64, 64, 64))
            fm = QFontMetrics(font)
            opt_text_w = fm.horizontalAdvance(opt_label) + int(16 * dp)
            painter.drawText(
                QRect(opt_x + radio_size + int(4 * dp), iy, opt_text_w, int(20 * dp)),
                Qt.AlignLeft | Qt.AlignVCenter, opt_label
            )
            opt_x += radio_size + int(4 * dp) + opt_text_w

    def _draw_text_input(self, painter, ix, iy, w, dp, label_text, inp):
        """绘制文本输入控件。"""
        placeholder = inp.get("placeholder", "")
        initial = inp.get("initial", "")

        field_w = int(160 * dp)
        field_h = int(22 * dp)

        # 标签
        label_color, label_bold, label_italic, label_underline = _get_text_style(inp.get("label"))
        font_size = max(7, int(9 * dp))
        font = QFont("Microsoft YaHei", font_size)
        font.setBold(label_bold)
        font.setItalic(label_italic)
        font.setUnderline(label_underline)
        painter.setFont(font)
        painter.setPen(COLOR_MAP.get(label_color, QColor(64, 64, 64)))
        painter.drawText(QRect(ix, iy, int(80 * dp), field_h), Qt.AlignLeft | Qt.AlignVCenter, label_text)

        field_x = ix + int(85 * dp)

        # 文本框背景
        tex = self._textures.get("text_field")
        if tex and not tex.isNull():
            scaled = tex.scaled(field_w, field_h, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
            painter.drawPixmap(field_x, iy, scaled)
        else:
            painter.setPen(QPen(QColor(100, 100, 100), 1))
            painter.setBrush(QBrush(QColor(60, 60, 60)))
            painter.drawRect(QRect(field_x, iy, field_w, field_h))

        # 占位文本或初始值
        display_text = initial if initial else placeholder
        if display_text:
            painter.setPen(QColor(160, 160, 160) if not initial else QColor(220, 220, 220))
            painter.drawText(
                QRect(field_x + int(4 * dp), iy, field_w - int(8 * dp), field_h),
                Qt.AlignLeft | Qt.AlignVCenter, display_text
            )

    # ── 底部按钮绘制 ────────────────────────────────────────────────
    def _draw_actions(self, painter, x, y, w, footer_h, margin, dp):
        dlg_type = self._dialog_data.get("type", "")

        if dlg_type == "minecraft:confirmation":
            self._draw_confirm_buttons(painter, x, y, w, footer_h, margin, dp)
        elif dlg_type in ("minecraft:notice", "minecraft:simple_input_form"):
            self._draw_single_action_button(painter, x, y, w, footer_h, margin, dp)
        elif dlg_type in ("minecraft:multi_action", "minecraft:multi_action_input_form"):
            self._draw_multi_action_buttons(painter, x, y, w, footer_h, margin, dp)
        elif dlg_type == "minecraft:dialog_list":
            self._draw_dialog_list_buttons(painter, x, y, w, footer_h, margin, dp)
        elif dlg_type == "minecraft:server_links":
            self._draw_server_links_buttons(painter, x, y, w, footer_h, margin, dp)
        else:
            # Fallback: 如果有 actions 列表，按多按钮渲染
            actions = self._dialog_data.get("actions", [])
            if actions:
                self._draw_multi_action_buttons(painter, x, y, w, footer_h, margin, dp)

    # ── 确认按钮（是/否）────────────────────────────────────────────
    def _draw_confirm_buttons(self, painter, x, y, w, footer_h, margin, dp):
        yes_data = self._dialog_data.get("yes", {})
        no_data = self._dialog_data.get("no", {})

        yes_label = yes_data.get("label", {}) if isinstance(yes_data, dict) else {}
        no_label = no_data.get("label", {}) if isinstance(no_data, dict) else {}

        yes_text = _resolve_text_component(yes_label, "是")
        no_text = _resolve_text_component(no_label, "否")

        btn_w = int(100 * dp)
        btn_h = int(24 * dp)
        spacing = int(12 * dp)
        total_w = btn_w * 2 + spacing
        start_x = x + (w - total_w) // 2
        btn_y = y + (footer_h - btn_h) // 2

        # 否按钮（warning 样式）
        self._draw_button(painter, start_x, btn_y, btn_w, btn_h, dp, no_text, is_warning=True)
        # 是按钮
        self._draw_button(painter, start_x + btn_w + spacing, btn_y, btn_w, btn_h, dp, yes_text, is_warning=False)

    # ── 单按钮（通知 / 简单表单）────────────────────────────────────
    def _draw_single_action_button(self, painter, x, y, w, footer_h, margin, dp):
        action = self._dialog_data.get("action", {})
        label_data = action.get("label", {}) if isinstance(action, dict) else {}
        text = _resolve_text_component(label_data, "确定")

        btn_w = int(120 * dp)
        btn_h = int(24 * dp)
        btn_x = x + (w - btn_w) // 2
        btn_y = y + (footer_h - btn_h) // 2

        self._draw_button(painter, btn_x, btn_y, btn_w, btn_h, dp, text)

    # ── 多动作按钮 ──────────────────────────────────────────────────
    def _draw_multi_action_buttons(self, painter, x, y, w, footer_h, margin, dp):
        actions = self._dialog_data.get("actions", [])
        if not actions:
            return

        columns = self._dialog_data.get("columns", 2)
        columns = max(1, min(columns, len(actions)))

        btn_w = int(100 * dp)
        btn_h = int(24 * dp)
        spacing = int(5 * dp)
        total_grid_w = columns * btn_w + (columns - 1) * spacing
        start_x = x + (w - total_grid_w) // 2

        rows = (len(actions) + columns - 1) // columns
        total_grid_h = rows * btn_h + (rows - 1) * spacing
        btn_y = y + (footer_h - total_grid_h) // 2

        for i, act in enumerate(actions):
            if not isinstance(act, dict):
                continue
            label_data = act.get("label", {})
            text = _resolve_text_component(label_data, f"按钮{i + 1}")

            col = i % columns
            row = i // columns
            bx = start_x + col * (btn_w + spacing)
            by = btn_y + row * (btn_h + spacing)

            self._draw_button(painter, bx, by, btn_w, btn_h, dp, text)

    # ── 对话框列表按钮 ──────────────────────────────────────────────
    def _draw_dialog_list_buttons(self, painter, x, y, w, footer_h, margin, dp):
        dialogs = self._dialog_data.get("dialogs", [])
        columns = self._dialog_data.get("columns", 2)
        columns = max(1, min(columns, 4))

        btn_w = int(100 * dp)
        btn_h = int(24 * dp)
        spacing = int(5 * dp)

        # 子对话框按钮
        total_grid_w = columns * btn_w + (columns - 1) * spacing
        start_x = x + (w - total_grid_w) // 2

        rows = (len(dialogs) + columns - 1) // columns if dialogs else 0
        # 为 exit 按钮预留空间
        exit_btn_h = int(20 * dp)
        total_btns_h = rows * btn_h + (rows - 1) * spacing + exit_btn_h + spacing
        btn_y = y + (footer_h - total_btns_h) // 2

        for i, dlg in enumerate(dialogs):
            if not isinstance(dlg, dict):
                continue
            title_data = dlg.get("title", {})
            text = _resolve_text_component(title_data, f"对话框{i + 1}")

            col = i % columns
            row = i // columns
            bx = start_x + col * (btn_w + spacing)
            by = btn_y + row * (btn_h + spacing)

            self._draw_button(painter, bx, by, btn_w, btn_h, dp, text)

        # Exit 按钮
        exit_action = self._dialog_data.get("exit_action", {})
        exit_label = exit_action.get("label", {}) if isinstance(exit_action, dict) else {}
        exit_text = _resolve_text_component(exit_label, "退出")

        exit_btn_w = int(80 * dp)
        exit_x = x + (w - exit_btn_w) // 2
        exit_y = btn_y + (rows * (btn_h + spacing)) if rows > 0 else btn_y

        self._draw_button(painter, exit_x, exit_y, exit_btn_w, exit_btn_h, dp, exit_text, is_warning=True)

    # ── 服务器链接按钮 ──────────────────────────────────────────────
    def _draw_server_links_buttons(self, painter, x, y, w, footer_h, margin, dp):
        columns = self._dialog_data.get("columns", 2)
        columns = max(1, min(columns, 4))

        btn_w = int(100 * dp)
        btn_h = int(24 * dp)
        spacing = int(5 * dp)

        total_grid_w = columns * btn_w + (columns - 1) * spacing
        start_x = x + (w - total_grid_w) // 2

        # 服务器链接按钮（模拟 4 个链接按钮）
        link_buttons = [
            {"label": {"text": "官网"}, "url": "https://minecraft.net"},
            {"label": {"text": "反馈"}, "url": "https://feedback.minecraft.net"},
            {"label": {"text": "社区"}, "url": "https://discord.gg/minecraft"},
            {"label": {"text": "Bug"}, "url": "https://bugs.mojang.com"},
        ]

        rows = (len(link_buttons) + columns - 1) // columns
        exit_btn_h = int(20 * dp)
        total_btns_h = rows * btn_h + (rows - 1) * spacing + exit_btn_h + spacing
        btn_y = y + (footer_h - total_btns_h) // 2

        for i, link in enumerate(link_buttons):
            label_data = link.get("label", {})
            text = _resolve_text_component(label_data, f"链接{i + 1}")

            col = i % columns
            row = i // columns
            bx = start_x + col * (btn_w + spacing)
            by = btn_y + row * (btn_h + spacing)

            self._draw_button(painter, bx, by, btn_w, btn_h, dp, text)

        # Exit 按钮
        exit_action = self._dialog_data.get("exit_action", {})
        exit_label = exit_action.get("label", {}) if isinstance(exit_action, dict) else {}
        exit_text = _resolve_text_component(exit_label, "退出")

        exit_btn_w = int(80 * dp)
        exit_x = x + (w - exit_btn_w) // 2
        exit_y = btn_y + (rows * (btn_h + spacing)) if rows > 0 else btn_y

        self._draw_button(painter, exit_x, exit_y, exit_btn_w, exit_btn_h, dp, exit_text, is_warning=True)

    # ── 通用按钮绘制 ────────────────────────────────────────────────
    def _draw_button(self, painter, bx, by, bw, bh, dp, label, is_warning=False):
        """绘制一个按钮，记录其区域用于 hover 检测。"""
        btn_idx = len(self._buttons)

        # 确定按钮是否 hover
        is_hover = (btn_idx == self._hovered_index)

        # 选择纹理
        if is_warning:
            tex_key = "warning_button_highlighted" if is_hover else "warning_button"
        else:
            tex_key = "button_highlighted" if is_hover else "button"

        tex = self._textures.get(tex_key)
        if tex and not tex.isNull():
            scaled = tex.scaled(bw, bh, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
            painter.drawPixmap(bx, by, scaled)
        else:
            # Fallback: 绘制圆角矩形
            if is_warning:
                bg = QColor(180, 80, 80) if is_hover else QColor(160, 60, 60)
            else:
                bg = QColor(120, 120, 120) if is_hover else QColor(100, 100, 100)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(bg))
            painter.drawRoundedRect(QRect(bx, by, bw, bh), 3, 3)

        # 绘制标签文本
        label_data = label if isinstance(label, dict) else {"text": str(label)}
        text = _resolve_text_component(label_data, "")
        color, bold, italic, underline = _get_text_style(label_data)

        font_size = max(7, int(9 * dp))
        font = QFont("Microsoft YaHei", font_size)
        font.setBold(bold)
        font.setItalic(italic)
        font.setUnderline(underline)
        painter.setFont(font)
        painter.setPen(COLOR_MAP.get(color, QColor(255, 255, 255)))
        painter.drawText(QRect(bx, by, bw, bh), Qt.AlignCenter, text)

        # 记录按钮区域
        self._buttons.append(_ButtonRect(
            QRect(bx, by, bw, bh),
            label,
            is_warning=is_warning,
        ))