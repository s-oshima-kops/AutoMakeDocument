# -*- coding: utf-8 -*-
"""
ファイル操作ユーティリティ
"""

import os
import shutil
import chardet
from pathlib import Path
from typing import Optional, List, Dict, Any

class FileUtils:
    """ファイル操作ユーティリティクラス"""
    
    @staticmethod
    def read_text_file(file_path: Path, encoding: Optional[str] = None) -> str:
        """
        テキストファイルを読み込み
        
        Args:
            file_path: ファイルパス
            encoding: エンコーディング（指定しない場合は自動検出）
            
        Returns:
            str: ファイル内容
        """
        try:
            if encoding is None:
                # エンコーディングを自動検出
                encoding = FileUtils.detect_encoding(file_path)
            
            with open(file_path, 'r', encoding=encoding) as file:
                return file.read()
                
        except Exception as e:
            raise FileNotFoundError(f"ファイルの読み込みに失敗しました: {e}")
    
    @staticmethod
    def write_text_file(file_path: Path, content: str, encoding: str = 'utf-8'):
        """
        テキストファイルに書き込み
        
        Args:
            file_path: ファイルパス
            content: 書き込み内容
            encoding: エンコーディング
        """
        try:
            # ディレクトリが存在しない場合は作成
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding=encoding) as file:
                file.write(content)
                
        except Exception as e:
            raise IOError(f"ファイルの書き込みに失敗しました: {e}")
    
    @staticmethod
    def detect_encoding(file_path: Path) -> str:
        """
        ファイルのエンコーディングを検出
        
        Args:
            file_path: ファイルパス
            
        Returns:
            str: エンコーディング名
        """
        try:
            with open(file_path, 'rb') as file:
                raw_data = file.read()
                result = chardet.detect(raw_data)
                return result['encoding'] or 'utf-8'
                
        except Exception:
            return 'utf-8'
    
    @staticmethod
    def copy_file(src: Path, dst: Path) -> bool:
        """
        ファイルをコピー
        
        Args:
            src: コピー元パス
            dst: コピー先パス
            
        Returns:
            bool: 成功したかどうか
        """
        try:
            # コピー先のディレクトリを作成
            dst.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(src, dst)
            return True
            
        except Exception as e:
            print(f"ファイルコピーエラー: {e}")
            return False
    
    @staticmethod
    def move_file(src: Path, dst: Path) -> bool:
        """
        ファイルを移動
        
        Args:
            src: 移動元パス
            dst: 移動先パス
            
        Returns:
            bool: 成功したかどうか
        """
        try:
            # 移動先のディレクトリを作成
            dst.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.move(src, dst)
            return True
            
        except Exception as e:
            print(f"ファイル移動エラー: {e}")
            return False
    
    @staticmethod
    def delete_file(file_path: Path) -> bool:
        """
        ファイルを削除
        
        Args:
            file_path: ファイルパス
            
        Returns:
            bool: 成功したかどうか
        """
        try:
            if file_path.exists():
                os.remove(file_path)
            return True
            
        except Exception as e:
            print(f"ファイル削除エラー: {e}")
            return False
    
    @staticmethod
    def get_file_size(file_path: Path) -> int:
        """
        ファイルサイズを取得
        
        Args:
            file_path: ファイルパス
            
        Returns:
            int: ファイルサイズ（バイト）
        """
        try:
            return os.path.getsize(file_path)
        except Exception:
            return 0
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """
        ファイルサイズを人間が読みやすい形式に変換
        
        Args:
            size_bytes: ファイルサイズ（バイト）
            
        Returns:
            str: フォーマットされたサイズ
        """
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    @staticmethod
    def list_files(directory: Path, pattern: str = "*") -> List[Path]:
        """
        ディレクトリ内のファイルをリスト
        
        Args:
            directory: ディレクトリパス
            pattern: ファイルパターン
            
        Returns:
            List[Path]: ファイルリスト
        """
        try:
            return list(directory.glob(pattern))
        except Exception:
            return []
    
    @staticmethod
    def ensure_directory(directory: Path):
        """
        ディレクトリの存在を確認し、存在しない場合は作成
        
        Args:
            directory: ディレクトリパス
        """
        directory.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def get_safe_filename(filename: str) -> str:
        """
        ファイル名として安全な文字列に変換
        
        Args:
            filename: 元のファイル名
            
        Returns:
            str: 安全なファイル名
        """
        # 使用できない文字を置換
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # 長すぎる場合は切り詰める
        if len(filename) > 200:
            filename = filename[:200]
        
        return filename.strip() 