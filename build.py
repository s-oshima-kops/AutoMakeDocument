#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ドキュメント自動要約&作成アプリ - ビルドスクリプト
"""

import os
import sys
import shutil
from pathlib import Path
import PyInstaller.__main__

def build_app():
    """アプリケーションをビルドする"""
    
    # プロジェクトルート
    project_root = Path(__file__).parent
    
    # ビルド設定
    build_args = [
        'main.py',
        '--onefile',
        '--windowed',
        '--name=AutoMakeDocument',
        '--icon=assets/icon.ico',
        '--distpath=dist',
        '--workpath=build',
        '--specpath=build',
        '--add-data=templates;templates',
        '--add-data=config;config',
        '--add-data=assets;assets',
        '--hidden-import=PySide6.QtWidgets',
        '--hidden-import=PySide6.QtCore',
        '--hidden-import=PySide6.QtGui',
        '--hidden-import=sumy',
        '--hidden-import=janome',
        '--hidden-import=openpyxl',
        '--hidden-import=docx',
        '--hidden-import=yaml',
        '--hidden-import=pandas',
        '--hidden-import=numpy',
        '--collect-all=sumy',
        '--collect-all=janome',
        '--collect-all=nltk',
        '--noupx',
        '--clean'
    ]
    
    # アイコンファイルが存在しない場合は削除
    icon_path = project_root / "assets" / "icon.ico"
    if not icon_path.exists():
        build_args = [arg for arg in build_args if not arg.startswith('--icon=')]
    
    # PyInstallerを実行
    try:
        print("アプリケーションのビルドを開始します...")
        PyInstaller.__main__.run(build_args)
        print("ビルドが完了しました！")
        
        # 配布用フォルダを作成
        create_distribution_folder()
        
    except Exception as e:
        print(f"ビルドエラー: {e}")
        sys.exit(1)

def create_distribution_folder():
    """配布用フォルダを作成"""
    project_root = Path(__file__).parent
    dist_dir = project_root / "dist"
    portable_dir = dist_dir / "portable"
    
    # ポータブル版フォルダを作成
    if portable_dir.exists():
        shutil.rmtree(portable_dir)
    
    portable_dir.mkdir(parents=True, exist_ok=True)
    
    # 必要なファイルをコピー
    files_to_copy = [
        ("dist/AutoMakeDocument.exe", "portable/AutoMakeDocument.exe"),
        ("README.md", "portable/README.md"),
        ("templates", "portable/templates"),
        ("config", "portable/config"),
        ("assets", "portable/assets")
    ]
    
    for src, dst in files_to_copy:
        src_path = project_root / src
        dst_path = project_root / dst
        
        if src_path.exists():
            if src_path.is_file():
                shutil.copy2(src_path, dst_path)
            else:
                shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
    
    print(f"配布用フォルダを作成しました: {portable_dir}")

if __name__ == "__main__":
    build_app() 