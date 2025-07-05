# -*- coding: utf-8 -*-
"""
ChatGPT連携要約機能
"""

import json
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path


class ChatGPTSummarizer:
    """ChatGPT連携要約クラス"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """
        初期化
        
        Args:
            api_key: OpenAI APIキー
            model: 使用するモデル（gpt-3.5-turbo または gpt-4）
        """
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.openai.com/v1"
        
        # プロンプトテンプレート
        self.prompts = {
            "daily_report": """
以下の作業ログを日報形式で要約してください。
・本日の作業内容を簡潔にまとめる
・完了した作業、進行中の作業、課題を明確に分ける
・明日の予定があれば含める
・読みやすい箇条書き形式で出力

作業ログ:
{content}
""",
            "weekly_report": """
以下の作業ログを週報形式で要約してください。
・今週の主要な成果と活動を要約
・完了したタスク、進行中のタスク、課題を整理
・来週の計画や重要な予定を含める
・数値的な実績があれば含める

作業ログ:
{content}
""",
            "monthly_report": """
以下の作業ログを月報形式で要約してください。
・今月の主要な成果と活動を要約
・完了したプロジェクト、進行中のプロジェクト、課題を整理
・来月の計画や重要な目標を含める
・スキル開発や改善点があれば含める

作業ログ:
{content}
""",
            "quick_summary": """
以下の作業ログを簡潔に要約してください。
・重要なポイントを3-5個の箇条書きで
・専門用語は分かりやすく説明
・数値や具体的な成果があれば含める

作業ログ:
{content}
""",
            "extract_keywords": """
以下の作業ログから重要なキーワードを抽出してください。
・技術名、プロジェクト名、作業内容のキーワード
・重要度順に並べる
・カンマ区切りで出力

作業ログ:
{content}
""",
            "analyze_tasks": """
以下の作業ログを分析して、以下の形式で出力してください。
・完了したタスク
・進行中のタスク
・課題・問題点
・今後の予定

作業ログ:
{content}
"""
        }
    
    def set_api_key(self, api_key: str):
        """APIキーを設定"""
        self.api_key = api_key
    
    def is_configured(self) -> bool:
        """設定が完了しているかチェック"""
        return self.api_key is not None and len(self.api_key.strip()) > 0
    
    def summarize_text(self, text: str, summary_type: str = "quick_summary", 
                      max_tokens: int = 1000) -> Dict[str, Any]:
        """
        テキストを要約
        
        Args:
            text: 要約対象のテキスト
            summary_type: 要約タイプ（daily_report, weekly_report, monthly_report, quick_summary）
            max_tokens: 最大トークン数
            
        Returns:
            要約結果の辞書
        """
        if not self.is_configured():
            raise ValueError("APIキーが設定されていません")
        
        if summary_type not in self.prompts:
            summary_type = "quick_summary"
        
        # プロンプトを構築
        prompt = self.prompts[summary_type].format(content=text)
        
        try:
            # API呼び出し
            response = self._call_openai_api(prompt, max_tokens)
            
            # 結果を構築
            result = {
                "summary_text": response.get("choices", [{}])[0].get("message", {}).get("content", ""),
                "original_text": text,
                "summary_type": summary_type,
                "model": self.model,
                "tokens_used": response.get("usage", {}).get("total_tokens", 0),
                "generated_at": datetime.now().isoformat(),
                "method": "chatgpt"
            }
            
            return result
            
        except Exception as e:
            raise Exception(f"ChatGPT要約エラー: {str(e)}")
    
    def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """
        キーワードを抽出
        
        Args:
            text: 対象テキスト
            max_keywords: 最大キーワード数
            
        Returns:
            キーワードリスト
        """
        if not self.is_configured():
            raise ValueError("APIキーが設定されていません")
        
        # プロンプトを構築
        prompt = self.prompts["extract_keywords"].format(content=text)
        
        try:
            # API呼び出し
            response = self._call_openai_api(prompt, max_tokens=200)
            
            # キーワードを抽出
            keywords_text = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            keywords = [kw.strip() for kw in keywords_text.split(",") if kw.strip()]
            
            return keywords[:max_keywords]
            
        except Exception as e:
            raise Exception(f"キーワード抽出エラー: {str(e)}")
    
    def analyze_tasks(self, text: str) -> Dict[str, List[str]]:
        """
        タスクを分析
        
        Args:
            text: 対象テキスト
            
        Returns:
            タスク分析結果
        """
        if not self.is_configured():
            raise ValueError("APIキーが設定されていません")
        
        # プロンプトを構築
        prompt = self.prompts["analyze_tasks"].format(content=text)
        
        try:
            # API呼び出し
            response = self._call_openai_api(prompt, max_tokens=800)
            
            # 分析結果を解析
            analysis_text = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # 簡単な解析（実際の実装では、より詳細な解析が必要）
            analysis = {
                "completed_tasks": [],
                "in_progress_tasks": [],
                "issues": [],
                "future_plans": []
            }
            
            # 分析結果をテキストとして返す
            analysis["raw_analysis"] = analysis_text
            
            return analysis
            
        except Exception as e:
            raise Exception(f"タスク分析エラー: {str(e)}")
    
    def _call_openai_api(self, prompt: str, max_tokens: int = 1000) -> Dict[str, Any]:
        """
        OpenAI APIを呼び出し
        
        Args:
            prompt: プロンプト
            max_tokens: 最大トークン数
            
        Returns:
            API応答
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "あなたは優秀な文書作成アシスタントです。日本語で分かりやすく要約を作成してください。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code != 200:
            error_detail = response.json().get("error", {}).get("message", "不明なエラー")
            raise Exception(f"API呼び出しエラー ({response.status_code}): {error_detail}")
        
        return response.json()
    
    def test_connection(self) -> Dict[str, Any]:
        """
        接続テスト
        
        Returns:
            テスト結果
        """
        if not self.is_configured():
            return {
                "success": False,
                "error": "APIキーが設定されていません"
            }
        
        try:
            # 簡単なテスト用プロンプト
            test_prompt = "こんにちは！接続テストです。"
            
            response = self._call_openai_api(test_prompt, max_tokens=10)
            
            return {
                "success": True,
                "model": self.model,
                "tokens_used": response.get("usage", {}).get("total_tokens", 0)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """
        使用統計を取得（簡易版）
        
        Returns:
            使用統計
        """
        # 実際の実装では、使用状況をローカルファイルに保存して管理
        return {
            "total_requests": 0,
            "total_tokens": 0,
            "last_used": None,
            "model": self.model
        }
    
    def save_api_key(self, api_key: str, config_file: Path):
        """
        APIキーを安全に保存
        
        Args:
            api_key: APIキー
            config_file: 設定ファイルパス
        """
        try:
            config_data = {}
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
            
            config_data["chatgpt"] = {
                "api_key": api_key,
                "model": self.model,
                "enabled": True
            }
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
            
            self.api_key = api_key
            
        except Exception as e:
            raise Exception(f"APIキー保存エラー: {str(e)}")
    
    def load_api_key(self, config_file: Path) -> bool:
        """
        APIキーを読み込み
        
        Args:
            config_file: 設定ファイルパス
            
        Returns:
            読み込み成功フラグ
        """
        try:
            if not config_file.exists():
                return False
            
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            chatgpt_config = config_data.get("chatgpt", {})
            
            if chatgpt_config.get("enabled", False):
                self.api_key = chatgpt_config.get("api_key")
                self.model = chatgpt_config.get("model", "gpt-3.5-turbo")
                return True
            
            return False
            
        except Exception:
            return False 