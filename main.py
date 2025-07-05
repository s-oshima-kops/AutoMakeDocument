#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ドキュメント自動要約&作成アプリ - メインエントリーポイント
"""

import sys
import os
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from src.app import AutoMakeDocumentApp

def main():
    """メイン関数"""
    try:
        app = AutoMakeDocumentApp()
        app.run()
    except Exception as e:
        print(f"アプリケーションの起動に失敗しました: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 