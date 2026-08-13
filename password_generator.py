#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
随机密码生成器 - 密码学安全的Windows小工具
使用 secrets 模块（CSPRNG）生成密码
"""

import sys
import secrets
import string
import base64
import platform
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSlider, QCheckBox, QLineEdit, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, QByteArray
from PyQt6.QtGui import QIcon, QPixmap

# Windows API 支持（用于剪贴板历史操作）
if platform.system() == 'Windows':
    import ctypes
    from ctypes import wintypes

    CF_UNICODETEXT = 13
    GMEM_MOVEABLE = 0x0002

    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32

    user32.OpenClipboard.argtypes = [wintypes.HWND]
    user32.OpenClipboard.restype = wintypes.BOOL
    user32.EmptyClipboard.restype = wintypes.BOOL
    user32.SetClipboardData.argtypes = [wintypes.UINT, wintypes.HANDLE]
    user32.SetClipboardData.restype = wintypes.HANDLE
    user32.CloseClipboard.restype = wintypes.BOOL

    kernel32.GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
    kernel32.GlobalAlloc.restype = wintypes.HANDLE
    kernel32.GlobalLock.argtypes = [wintypes.HANDLE]
    kernel32.GlobalLock.restype = wintypes.LPVOID
    kernel32.GlobalUnlock.argtypes = [wintypes.HANDLE]
    kernel32.GlobalUnlock.restype = wintypes.BOOL

    try:
        CF_EXCLUDE = user32.RegisterClipboardFormatW("ExcludeClipboardContentFromMonitorProcessing")
        CF_NO_HISTORY = user32.RegisterClipboardFormatW("CanIncludeInClipboardHistory")
        WINDOWS_CLIPBOARD_HISTORY_SUPPORTED = True
    except Exception:
        WINDOWS_CLIPBOARD_HISTORY_SUPPORTED = False
else:
    WINDOWS_CLIPBOARD_HISTORY_SUPPORTED = False


# 应用图标（钥匙，暖橙棕色，256x256 PNG）
APP_ICON_BASE64 = "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"

# 创作者印记（纸箱人，透明背景，40x40 PNG）
BOX_MASCOT_BASE64 = "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"


class PasswordGenerator(QMainWindow):
    """密码生成器主窗口"""

    def __init__(self):
        super().__init__()
        self.current_password = ""
        self.clipboard_timer = QTimer()
        self.clipboard_timer.timeout.connect(self._auto_clear_clipboard)

        app_icon = self._load_pixmap(APP_ICON_BASE64)
        if app_icon:
            self.setWindowIcon(QIcon(app_icon))

        self.init_ui()
        self.generate_password()

    def _load_pixmap(self, b64):
        try:
            data = base64.b64decode(b64)
            pix = QPixmap()
            pix.loadFromData(QByteArray(data))
            return pix
        except Exception:
            return None

    def init_ui(self):
        self.setWindowTitle("随机密码生成器")
        self.setFixedSize(440, 460)

        central = QWidget()
        self.setCentralWidget(central)
        main = QVBoxLayout(central)
        main.setContentsMargins(22, 22, 22, 22)
        main.setSpacing(14)

        # ===== 密码显示区 =====
        pw_label = QLabel("生成的密码:")
        pw_label.setStyleSheet("font-size: 14px;")
        main.addWidget(pw_label)

        pw_row = QHBoxLayout()
        self.password_display = QLineEdit()
        self.password_display.setReadOnly(True)
        self.password_display.setMinimumHeight(44)
        self.password_display.setStyleSheet("font-size: 16px; padding: 6px;")
        pw_row.addWidget(self.password_display)

        self.copy_btn = QPushButton("复制")
        self.copy_btn.setFixedSize(64, 44)
        self.copy_btn.setStyleSheet("font-size: 14px;")
        self.copy_btn.clicked.connect(self.copy_password)
        pw_row.addWidget(self.copy_btn)
        main.addLayout(pw_row)

        # 强度指示（增加与密码框的间距）
        main.addSpacing(6)
        self.strength_label = QLabel("强度: ")
        self.strength_label.setStyleSheet("font-size: 13px;")
        main.addWidget(self.strength_label)

        line1 = QFrame()
        line1.setFrameShape(QFrame.Shape.HLine)
        line1.setFrameShadow(QFrame.Shadow.Sunken)
        main.addWidget(line1)

        # ===== 密码长度 =====
        self.length_label = QLabel("密码长度: 16")
        self.length_label.setStyleSheet("font-size: 14px;")
        main.addWidget(self.length_label)

        len_row = QHBoxLayout()
        minus_btn = QPushButton("-")
        minus_btn.setFixedSize(34, 34)
        minus_btn.setStyleSheet("font-size: 20px; font-weight: bold;")
        minus_btn.clicked.connect(lambda: self.adjust_length(-1))
        len_row.addWidget(minus_btn)

        self.length_slider = QSlider(Qt.Orientation.Horizontal)
        self.length_slider.setMinimum(4)
        self.length_slider.setMaximum(64)
        self.length_slider.setValue(16)
        self.length_slider.valueChanged.connect(self.update_length_label)
        len_row.addWidget(self.length_slider)

        plus_btn = QPushButton("+")
        plus_btn.setFixedSize(34, 34)
        plus_btn.setStyleSheet("font-size: 20px; font-weight: bold;")
        plus_btn.clicked.connect(lambda: self.adjust_length(1))
        len_row.addWidget(plus_btn)
        main.addLayout(len_row)

        # ===== 字符集选择 + 纸箱人印记 =====
        cs_label = QLabel("已使用的字符:")
        cs_label.setStyleSheet("font-size: 14px;")
        main.addWidget(cs_label)

        cs_row = QHBoxLayout()
        self.cb_upper = QCheckBox("ABC")
        self.cb_upper.setChecked(True)
        self.cb_upper.setStyleSheet("font-size: 14px;")
        self.cb_upper.stateChanged.connect(self.on_charset_changed)
        cs_row.addWidget(self.cb_upper)

        self.cb_lower = QCheckBox("abc")
        self.cb_lower.setChecked(True)
        self.cb_lower.setStyleSheet("font-size: 14px;")
        self.cb_lower.stateChanged.connect(self.on_charset_changed)
        cs_row.addWidget(self.cb_lower)

        self.cb_digits = QCheckBox("123")
        self.cb_digits.setChecked(True)
        self.cb_digits.setStyleSheet("font-size: 14px;")
        self.cb_digits.stateChanged.connect(self.on_charset_changed)
        cs_row.addWidget(self.cb_digits)

        self.cb_symbols = QCheckBox("!@#$%^*")
        self.cb_symbols.setChecked(False)
        self.cb_symbols.setStyleSheet("font-size: 14px;")
        self.cb_symbols.stateChanged.connect(self.on_charset_changed)
        cs_row.addWidget(self.cb_symbols)

        cs_row.addStretch()

        # 纸箱人印记（放在特殊字符右边）
        box_label = QLabel()
        box_pix = self._load_pixmap(BOX_MASCOT_BASE64)
        if box_pix:
            box_label.setPixmap(box_pix)
            box_label.setFixedSize(40, 40)
            box_label.setScaledContents(True)
            box_label.setToolTip("Made with love")
        cs_row.addWidget(box_label)
        main.addLayout(cs_row)

        # 排除易混淆字符
        self.cb_exclude = QCheckBox("排除易混淆字符 (0OIl1)")
        self.cb_exclude.setChecked(False)
        self.cb_exclude.setStyleSheet("font-size: 14px;")
        self.cb_exclude.stateChanged.connect(self.on_charset_changed)
        main.addWidget(self.cb_exclude)

        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setFrameShadow(QFrame.Shadow.Sunken)
        main.addWidget(line2)

        # ===== 生成按钮 =====
        self.generate_btn = QPushButton("生成密码")
        self.generate_btn.setMinimumHeight(48)
        self.generate_btn.setStyleSheet("font-size: 15px; font-weight: bold;")
        self.generate_btn.clicked.connect(self.generate_password)
        main.addWidget(self.generate_btn)

        # 自动清空选项（增加与生成按钮的间距）
        main.addSpacing(10)
        self.cb_auto_clear = QCheckBox("20秒后自动清空剪贴板")
        self.cb_auto_clear.setChecked(True)
        self.cb_auto_clear.setStyleSheet("font-size: 14px;")
        main.addWidget(self.cb_auto_clear)

        # ===== 两个清空按钮 =====
        clear_row = QHBoxLayout()
        self.clear_pw_btn = QPushButton("清空当前密码")
        self.clear_pw_btn.setStyleSheet("font-size: 13px;")
        self.clear_pw_btn.setMinimumHeight(36)
        self.clear_pw_btn.clicked.connect(self.clear_current_password)
        clear_row.addWidget(self.clear_pw_btn)

        self.clear_all_btn = QPushButton("清空所有历史记录")
        self.clear_all_btn.setStyleSheet("font-size: 13px;")
        self.clear_all_btn.setMinimumHeight(36)
        self.clear_all_btn.clicked.connect(self.clear_all_history)
        clear_row.addWidget(self.clear_all_btn)
        main.addLayout(clear_row)

    def adjust_length(self, delta):
        v = self.length_slider.value() + delta
        if self.length_slider.minimum() <= v <= self.length_slider.maximum():
            self.length_slider.setValue(v)

    def update_length_label(self, value):
        self.length_label.setText(f"密码长度: {value}")

    def get_charset(self):
        cs = ""
        if self.cb_upper.isChecked():
            cs += string.ascii_uppercase
        if self.cb_lower.isChecked():
            cs += string.ascii_lowercase
        if self.cb_digits.isChecked():
            cs += string.digits
        if self.cb_symbols.isChecked():
            cs += "!@#$%^*"
        if self.cb_exclude.isChecked():
            for ch in "0OIl1":
                cs = cs.replace(ch, "")
        return cs

    def on_charset_changed(self):
        has = any([
            self.cb_upper.isChecked(), self.cb_lower.isChecked(),
            self.cb_digits.isChecked(), self.cb_symbols.isChecked()
        ])
        self.generate_btn.setEnabled(has)
        self.generate_btn.setText("生成密码" if has else "至少选择一种字符")

    def generate_password(self):
        cs = self.get_charset()
        if not cs:
            return
        length = self.length_slider.value()
        self.current_password = "".join(secrets.choice(cs) for _ in range(length))
        self.password_display.setText(self.current_password)
        self.update_strength()

    def update_strength(self):
        pw = self.current_password
        length = len(pw)
        div = sum([
            any(c.isupper() for c in pw), any(c.islower() for c in pw),
            any(c.isdigit() for c in pw), any(not c.isalnum() for c in pw)
        ])
        if length < 8:
            s, color, dots = "弱", "#ff4444", "*----"
        elif length < 12 and div < 3:
            s, color, dots = "中等", "#ffaa00", "***--"
        elif length < 16 or div < 3:
            s, color, dots = "强", "#88cc00", "****-"
        else:
            s, color, dots = "很强", "#00cc44", "*****"
        self.strength_label.setText(f"强度: {dots} {s}")
        self.strength_label.setStyleSheet(f"font-size: 13px; color: {color};")

    def copy_password(self):
        if not self.current_password:
            return
        if WINDOWS_CLIPBOARD_HISTORY_SUPPORTED:
            if not self._copy_windows(self.current_password):
                QApplication.clipboard().setText(self.current_password)
        else:
            QApplication.clipboard().setText(self.current_password)
        self.copy_btn.setText("已复制")
        QTimer.singleShot(2000, lambda: self.copy_btn.setText("复制"))
        if self.cb_auto_clear.isChecked():
            self.clipboard_timer.stop()
            self.clipboard_timer.start(20000)

    def _copy_windows(self, text):
        try:
            if not user32.OpenClipboard(None):
                return False
            user32.EmptyClipboard()
            enc = (text + "\0").encode("utf-16le")
            h = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(enc))
            if not h:
                user32.CloseClipboard()
                return False
            p = kernel32.GlobalLock(h)
            if not p:
                user32.CloseClipboard()
                return False
            ctypes.memmove(p, enc, len(enc))
            kernel32.GlobalUnlock(h)
            if not user32.SetClipboardData(CF_UNICODETEXT, h):
                user32.CloseClipboard()
                return False
            hm = kernel32.GlobalAlloc(GMEM_MOVEABLE, 1)
            if hm:
                user32.SetClipboardData(CF_EXCLUDE, hm)
            hn = kernel32.GlobalAlloc(GMEM_MOVEABLE, 1)
            if hn:
                user32.SetClipboardData(CF_NO_HISTORY, hn)
            user32.CloseClipboard()
            return True
        except Exception:
            try:
                user32.CloseClipboard()
            except Exception:
                pass
            return False

    def _auto_clear_clipboard(self):
        cb = QApplication.clipboard()
        if cb.text() == self.current_password:
            cb.clear()
        self.clipboard_timer.stop()

    def clear_current_password(self):
        """清空当前密码（仅清掉本工具生成的那条）"""
        cb = QApplication.clipboard()
        if cb.text() == self.current_password:
            cb.clear()
            self.clipboard_timer.stop()
        self.clear_pw_btn.setText("已清空")
        QTimer.singleShot(2000, lambda: self.clear_pw_btn.setText("清空当前密码"))

    def clear_all_history(self):
        """清空系统所有剪贴板历史记录（Win+V），需确认"""
        reply = QMessageBox.question(
            self, "确认清空",
            "这将删除系统中所有的剪贴板历史记录 (Win+V)，\n"
            "包括你复制过的其他文字、网址、图片等，无法恢复。\n\n确定要清空吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        ok = False
        if platform.system() == 'Windows':
            ok = self._clear_windows_history()
        else:
            QApplication.clipboard().clear()
            ok = True

        self.clear_all_btn.setText("已清空历史" if ok else "清空失败")
        QTimer.singleShot(2500, lambda: self.clear_all_btn.setText("清空所有历史记录"))

    def _clear_windows_history(self):
        """调用 Windows API / PowerShell 清空剪贴板历史"""
        try:
            if user32.OpenClipboard(None):
                user32.EmptyClipboard()
                user32.CloseClipboard()
            import subprocess
            subprocess.run(
                ["powershell", "-Command",
                 "[Windows.ApplicationModel.DataTransfer.Clipboard,"
                 "Windows.ApplicationModel.DataTransfer,ContentType=WindowsRuntime]"
                 " | Out-Null; "
                 "[Windows.ApplicationModel.DataTransfer.Clipboard]::ClearHistory()"],
                capture_output=True, timeout=5,
                creationflags=0x08000000  # CREATE_NO_WINDOW
            )
            return True
        except Exception:
            return False

    def closeEvent(self, event):
        cb = QApplication.clipboard()
        if cb.text() == self.current_password:
            cb.clear()
        if self.current_password:
            self.current_password = "X" * len(self.current_password)
        self.current_password = ""
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    try:
        data = base64.b64decode(APP_ICON_BASE64)
        pix = QPixmap()
        pix.loadFromData(QByteArray(data))
        app.setWindowIcon(QIcon(pix))
    except Exception:
        pass
    w = PasswordGenerator()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
