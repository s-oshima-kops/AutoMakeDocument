#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ドキュメント自動要約&作成アプリ - メインアプリケーション
"""

import sys
import os
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

from gui.main_window import MainWindow
from utils.config_manager import ConfigManager
from utils.logger import Logger

class AutoMakeDocumentApp:
    """メインアプリケーションクラス"""
    
    def __init__(self):
        """初期化"""
        self.app = None
        self.main_window = None
        self.config_manager = None
        self.logger = None
        
        # アプリケーションディレクトリを設定
        self.app_dir = Path(__file__).parent.parent
        self.data_dir = self.app_dir / "data"
        self.config_dir = self.app_dir / "config"
        self.templates_dir = self.app_dir / "templates"
        
        # ディレクトリが存在しない場合は作成
        self._create_directories()
        
        # 設定とログを初期化
        self._initialize_config()
        self._initialize_logger()
        
    def _create_directories(self):
        """必要なディレクトリを作成"""
        dirs_to_create = [
            self.data_dir,
            self.data_dir / "logs",
            self.config_dir,
            self.templates_dir,
            self.app_dir / "assets",
            self.app_dir / "dist",
            self.app_dir / "tests"
        ]
        
        for directory in dirs_to_create:
            directory.mkdir(parents=True, exist_ok=True)
            
    def _initialize_config(self):
        """設定管理を初期化"""
        self.config_manager = ConfigManager(self.config_dir)
        
    def _initialize_logger(self):
        """ログ機能を初期化"""
        self.logger = Logger(self.data_dir / "app.log")
        
    def run(self):
        """アプリケーションを実行"""
        try:
            # Qt アプリケーションを作成
            self.app = QApplication(sys.argv)
            
            # 日本語フォントの設定
            self.app.setApplicationName("ドキュメント自動要約&作成アプリ")
            self.app.setApplicationVersion("1.0.0")
            
            # アイコンを設定
            icon_path = self.app_dir / "assets" / "icon.ico"
            if icon_path.exists():
                self.app.setWindowIcon(QIcon(str(icon_path)))
                
            # メインウィンドウを作成
            self.main_window = MainWindow(
                config_manager=self.config_manager,
                logger=self.logger,
                app_dir=self.app_dir
            )
            
            # メインウィンドウを表示
            self.main_window.show()
            
            # イベントループを開始
            return self.app.exec()
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"アプリケーション実行中にエラーが発生しました: {e}")
            raise
            
    def quit(self):
        """アプリケーションを終了"""
        if self.app:
            self.app.quit() 