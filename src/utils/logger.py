# -*- coding: utf-8 -*-
"""
ログ機能クラス
"""

import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
from typing import Optional

class Logger:
    """アプリケーションログ管理クラス"""
    
    def __init__(self, log_file: Optional[Path] = None, level: str = "INFO"):
        """
        初期化
        
        Args:
            log_file: ログファイルパス
            level: ログレベル
        """
        self.log_file = log_file
        self.level = level
        self.logger = logging.getLogger("AutoMakeDocument")
        
        # ログレベルを設定
        numeric_level = getattr(logging, level.upper(), logging.INFO)
        self.logger.setLevel(numeric_level)
        
        # 既存のハンドラーをクリア
        self.logger.handlers.clear()
        
        # フォーマッターを設定
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # コンソールハンドラーを追加
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # ファイルハンドラーを追加（指定されている場合）
        if log_file:
            self._setup_file_handler(log_file, formatter)
    
    def _setup_file_handler(self, log_file: Path, formatter: logging.Formatter):
        """ファイルハンドラーを設定"""
        try:
            # ログディレクトリを作成
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            # ローテーションファイルハンドラーを設定
            # 最大10MB、バックアップ5個
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
            
        except Exception as e:
            self.logger.error(f"ファイルハンドラーの設定に失敗しました: {e}")
    
    def debug(self, message: str):
        """デバッグメッセージを出力"""
        self.logger.debug(message)
    
    def info(self, message: str):
        """情報メッセージを出力"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """警告メッセージを出力"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """エラーメッセージを出力"""
        self.logger.error(message)
    
    def critical(self, message: str):
        """クリティカルメッセージを出力"""
        self.logger.critical(message)
    
    def log_operation(self, operation: str, details: str = ""):
        """操作ログを出力"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"[{timestamp}] {operation}"
        if details:
            message += f" - {details}"
        self.info(message)
    
    def log_error(self, error: Exception, context: str = ""):
        """エラーログを出力"""
        error_message = f"エラーが発生しました: {type(error).__name__}: {str(error)}"
        if context:
            error_message = f"{context} - {error_message}"
        self.error(error_message)
    
    def log_performance(self, operation: str, duration: float):
        """パフォーマンスログを出力"""
        self.info(f"パフォーマンス - {operation}: {duration:.2f}秒")
    
    def set_level(self, level: str):
        """ログレベルを変更"""
        numeric_level = getattr(logging, level.upper(), logging.INFO)
        self.logger.setLevel(numeric_level)
        self.level = level 