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
