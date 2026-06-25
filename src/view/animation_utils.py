# animation_utils.py
# Minecraft Dialog Designer 动画工具函数

from PyQt5.QtWidgets import QGraphicsOpacityEffect, QWidget
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QSequentialAnimationGroup


def fade_in(widget: QWidget, duration: int = 300):
    """淡入动画：opacity 0 → 1"""
    effect = QGraphicsOpacityEffect(widget)
    widget.setGraphicsEffect(effect)
    anim = QPropertyAnimation(effect, b"opacity")
    anim.setDuration(duration)
    anim.setStartValue(0.0)
    anim.setEndValue(1.0)
    anim.setEasingCurve(QEasingCurve.OutCubic)
    anim.start()
    anim.finished.connect(lambda: widget.setGraphicsEffect(None))
    return anim


def fade_out(widget: QWidget, duration: int = 300):
    """淡出动画：opacity 1 → 0"""
    effect = QGraphicsOpacityEffect(widget)
    widget.setGraphicsEffect(effect)
    anim = QPropertyAnimation(effect, b"opacity")
    anim.setDuration(duration)
    anim.setStartValue(1.0)
    anim.setEndValue(0.0)
    anim.setEasingCurve(QEasingCurve.InCubic)
    anim.start()
    return anim


def fade_in_widget(widget: QWidget, duration: int = 250):
    """在 widget 上应用淡入效果（简写）"""
    widget.hide()
    effect = QGraphicsOpacityEffect(widget)
    widget.setGraphicsEffect(effect)
    anim = QPropertyAnimation(effect, b"opacity")
    anim.setDuration(duration)
    anim.setStartValue(0.0)
    anim.setEndValue(1.0)
    anim.setEasingCurve(QEasingCurve.OutCubic)
    widget.show()
    anim.start()
    return anim