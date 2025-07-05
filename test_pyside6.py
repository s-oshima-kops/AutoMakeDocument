#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PySide6テストスクリプト
"""

import sys
print("Python version:", sys.version)

try:
    print("PySide6をインポート中...")
    from PySide6.QtWidgets import QApplication, QMainWindow, QLabel
    from PySide6.QtCore import Qt
    print("PySide6インポート成功")
    
    print("アプリケーションを作成中...")
    app = QApplication(sys.argv)
    print("アプリケーション作成成功")
    
    print("ウィンドウを作成中...")
    window = QMainWindow()
    window.setWindowTitle("PySide6テスト")
    window.resize(400, 300)
    
    label = QLabel("Hello, PySide6!")
    label.setAlignment(Qt.AlignCenter)
    window.setCentralWidget(label)
    
    window.show()
    print("ウィンドウ表示成功")
    
    print("アプリケーション実行中...")
    sys.exit(app.exec())
    
except Exception as e:
    print(f"エラーが発生しました: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1) 