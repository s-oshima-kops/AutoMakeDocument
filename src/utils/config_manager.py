# -*- coding: utf-8 -*-
"""
設定管理クラス
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigManager:
    """アプリケーション設定管理クラス"""
    
    def __init__(self, config_dir: Path):
        """
        初期化
        
        Args:
            config_dir: 設定ファイルディレクトリ
        """
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # 設定ファイルパス
        self.app_config_path = self.config_dir / "app_config.yaml"
        self.user_settings_path = self.config_dir / "user_settings.json"
        self.templates_config_path = self.config_dir / "templates_config.yaml"
        self.output_config_path = self.config_dir / "output_config.yaml"
        
        # デフォルト設定
        self.default_app_config = {
            "app_name": "ドキュメント自動要約&作成アプリ",
            "version": "1.0.0",
            "language": "ja",
            "theme": "default",
            "window": {
                "width": 1200,
                "height": 800,
                "resizable": True
            },
            "logging": {
                "level": "INFO",
                "max_size": "10MB",
                "backup_count": 5
            }
        }
        
        self.default_user_settings = {
            "last_template": "weekly_report",
            "output_format": "docx",
            "output_directory": "",
            "auto_save": True,
            "recent_files": []
        }
        
        self.default_templates_config = {
            "templates": [
                {
                    "id": "daily_report",
                    "name": "日報",
                    "file": "daily_report.yaml",
                    "description": "日次の作業報告書"
                },
                {
                    "id": "weekly_report",
                    "name": "週報",
                    "file": "weekly_report.yaml",
                    "description": "週次の作業報告書"
                },
                {
                    "id": "monthly_report",
                    "name": "月報",
                    "file": "monthly_report.yaml",
                    "description": "月次の作業報告書"
                },
                {
                    "id": "business_report",
                    "name": "業務報告書",
                    "file": "business_report.yaml",
                    "description": "業務報告書"
                },
                {
                    "id": "progress_report",
                    "name": "進捗報告書",
                    "file": "progress_report.yaml",
                    "description": "進捗報告書"
                }
            ]
        }
        
        self.default_output_config = {
            "formats": {
                "txt": {
                    "extension": ".txt",
                    "encoding": "utf-8",
                    "enabled": True
                },
                "csv": {
                    "extension": ".csv",
                    "encoding": "utf-8",
                    "delimiter": ",",
                    "enabled": True
                },
                "xlsx": {
                    "extension": ".xlsx",
                    "sheet_name": "要約レポート",
                    "enabled": True
                },
                "docx": {
                    "extension": ".docx",
                    "font_name": "游ゴシック",
                    "font_size": 11,
                    "enabled": True
                }
            }
        }
        
        # 設定ファイルを初期化
        self._initialize_configs()
    
    def _initialize_configs(self):
        """設定ファイルを初期化"""
        # アプリケーション設定
        if not self.app_config_path.exists():
            self.save_yaml(self.app_config_path, self.default_app_config)
        
        # ユーザー設定
        if not self.user_settings_path.exists():
            self.save_json(self.user_settings_path, self.default_user_settings)
        
        # テンプレート設定
        if not self.templates_config_path.exists():
            self.save_yaml(self.templates_config_path, self.default_templates_config)
        
        # 出力設定
        if not self.output_config_path.exists():
            self.save_yaml(self.output_config_path, self.default_output_config)
    
    def get_app_config(self) -> Dict[str, Any]:
        """アプリケーション設定を取得"""
        return self.load_yaml(self.app_config_path)
    
    def get_user_settings(self) -> Dict[str, Any]:
        """ユーザー設定を取得"""
        return self.load_json(self.user_settings_path)
    
    def get_templates_config(self) -> Dict[str, Any]:
        """テンプレート設定を取得"""
        return self.load_yaml(self.templates_config_path)
    
    def get_output_config(self) -> Dict[str, Any]:
        """出力設定を取得"""
        return self.load_yaml(self.output_config_path)
    
    def save_user_settings(self, settings: Dict[str, Any]):
        """ユーザー設定を保存"""
        self.save_json(self.user_settings_path, settings)
    
    def update_user_setting(self, key: str, value: Any):
        """ユーザー設定を更新"""
        settings = self.get_user_settings()
        settings[key] = value
        self.save_user_settings(settings)
    
    def load_yaml(self, file_path: Path) -> Dict[str, Any]:
        """YAMLファイルを読み込み"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file) or {}
        except Exception as e:
            print(f"YAML読み込みエラー ({file_path}): {e}")
            return {}
    
    def save_yaml(self, file_path: Path, data: Dict[str, Any]):
        """YAMLファイルに保存"""
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                yaml.dump(data, file, default_flow_style=False, 
                         allow_unicode=True, sort_keys=False)
        except Exception as e:
            print(f"YAML保存エラー ({file_path}): {e}")
    
    def load_json(self, file_path: Path) -> Dict[str, Any]:
        """JSONファイルを読み込み"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception as e:
            print(f"JSON読み込みエラー ({file_path}): {e}")
            return {}
    
    def save_json(self, file_path: Path, data: Dict[str, Any]):
        """JSONファイルに保存"""
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"JSON保存エラー ({file_path}): {e}")
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """設定値を取得"""
        settings = self.get_user_settings()
        return settings.get(key, default) 