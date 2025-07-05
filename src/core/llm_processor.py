# -*- coding: utf-8 -*-
"""
LLMプロセッサークラス
"""

from typing import List, Dict, Any, Optional, Callable
from pathlib import Path
import json
from dataclasses import dataclass
from datetime import datetime

# オプション：ローカルLLM対応
try:
    from llama_cpp import Llama
    LLAMA_CPP_AVAILABLE = True
except ImportError:
    LLAMA_CPP_AVAILABLE = False

from core.data_manager import WorkLog
from utils.date_utils import DateUtils

@dataclass
class LLMConfig:
    """LLM設定クラス"""
    model_path: str
    context_length: int = 2048
    max_tokens: int = 512
    temperature: float = 0.7
    top_p: float = 0.95
    repeat_penalty: float = 1.1
    threads: int = 4

@dataclass
class LLMResponse:
    """LLM応答クラス"""
    text: str
    tokens_used: int
    processing_time: float
    model_name: str
    created_at: str

class LLMProcessor:
    """LLMプロセッサークラス"""
    
    def __init__(self, config: Optional[LLMConfig] = None):
        """
        初期化
        
        Args:
            config: LLM設定
        """
        self.config = config
        self.llm = None
        self.is_available = False
        
        # LLMが利用可能かチェック
        if LLAMA_CPP_AVAILABLE and config and Path(config.model_path).exists():
            self._initialize_llm()
    
    def _initialize_llm(self):
        """LLMを初期化"""
        try:
            if not self.config:
                return
            
            self.llm = Llama(
                model_path=self.config.model_path,
                n_ctx=self.config.context_length,
                n_threads=self.config.threads,
                verbose=False
            )
            
            self.is_available = True
            print(f"LLMが初期化されました: {self.config.model_path}")
            
        except Exception as e:
            print(f"LLM初期化エラー: {e}")
            self.is_available = False
    
    def generate_summary(self, logs: List[WorkLog], 
                        prompt_template: str = None,
                        max_tokens: int = None) -> Optional[LLMResponse]:
        """
        作業ログから要約を生成
        
        Args:
            logs: 作業ログリスト
            prompt_template: プロンプトテンプレート
            max_tokens: 最大トークン数
            
        Returns:
            Optional[LLMResponse]: LLM応答（利用不可の場合はNone）
        """
        if not self.is_available:
            return None
        
        try:
            # プロンプトを作成
            prompt = self._create_summary_prompt(logs, prompt_template)
            
            # 生成実行
            start_time = datetime.now()
            
            response = self.llm(
                prompt,
                max_tokens=max_tokens or self.config.max_tokens,
                temperature=self.config.temperature,
                top_p=self.config.top_p,
                repeat_penalty=self.config.repeat_penalty,
                stop=["</s>", "Human:", "Assistant:"]
            )
            
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            # 応答を整形
            generated_text = response["choices"][0]["text"].strip()
            tokens_used = response["usage"]["total_tokens"]
            
            return LLMResponse(
                text=generated_text,
                tokens_used=tokens_used,
                processing_time=processing_time,
                model_name=str(self.config.model_path),
                created_at=datetime.now().isoformat()
            )
            
        except Exception as e:
            print(f"LLM要約生成エラー: {e}")
            return None
    
    def _create_summary_prompt(self, logs: List[WorkLog], 
                              template: str = None) -> str:
        """
        要約用プロンプトを作成
        
        Args:
            logs: 作業ログリスト
            template: プロンプトテンプレート
            
        Returns:
            str: 作成されたプロンプト
        """
        if template is None:
            template = self._get_default_summary_template()
        
        # ログをテキストに変換
        log_text = self._format_logs_for_llm(logs)
        
        # プロンプトを組み立て
        prompt = template.format(
            logs=log_text,
            log_count=len(logs),
            date_range=self._get_date_range_string(logs)
        )
        
        return prompt
    
    def _get_default_summary_template(self) -> str:
        """デフォルトの要約テンプレートを取得"""
        return """以下の作業ログを簡潔に要約してください。重要なポイントと主な成果を含めてください。

作業期間: {date_range}
ログ件数: {log_count}件

作業ログ:
{logs}

要約:"""
    
    def _format_logs_for_llm(self, logs: List[WorkLog]) -> str:
        """LLM用にログを整形"""
        formatted_logs = []
        
        for log in logs:
            if log.content.strip():
                log_date = DateUtils.parse_date(log.date)
                if log_date:
                    date_str = DateUtils.format_date_japanese(log_date)
                    formatted_logs.append(f"[{date_str}]")
                    formatted_logs.append(log.content.strip())
                    formatted_logs.append("")
        
        return "\n".join(formatted_logs)
    
    def _get_date_range_string(self, logs: List[WorkLog]) -> str:
        """日付範囲の文字列を取得"""
        if not logs:
            return "不明"
        
        dates = []
        for log in logs:
            log_date = DateUtils.parse_date(log.date)
            if log_date:
                dates.append(log_date)
        
        if not dates:
            return "不明"
        
        dates.sort()
        start_date = DateUtils.format_date_japanese(dates[0])
        end_date = DateUtils.format_date_japanese(dates[-1])
        
        if start_date == end_date:
            return start_date
        else:
            return f"{start_date} 〜 {end_date}"
    
    def generate_structured_summary(self, logs: List[WorkLog], 
                                  summary_type: str = "weekly") -> Optional[Dict[str, Any]]:
        """
        構造化された要約を生成
        
        Args:
            logs: 作業ログリスト
            summary_type: 要約タイプ（daily, weekly, monthly）
            
        Returns:
            Optional[Dict[str, Any]]: 構造化された要約
        """
        if not self.is_available:
            return None
        
        try:
            # 要約タイプに応じたプロンプトを作成
            prompt = self._create_structured_prompt(logs, summary_type)
            
            # 生成実行
            response = self.llm(
                prompt,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                top_p=self.config.top_p,
                repeat_penalty=self.config.repeat_penalty,
                stop=["</s>", "Human:", "Assistant:"]
            )
            
            # 応答を解析
            generated_text = response["choices"][0]["text"].strip()
            
            # 構造化された形式で返す
            return self._parse_structured_response(generated_text, summary_type)
            
        except Exception as e:
            print(f"構造化要約生成エラー: {e}")
            return None
    
    def _create_structured_prompt(self, logs: List[WorkLog], 
                                 summary_type: str) -> str:
        """構造化プロンプトを作成"""
        log_text = self._format_logs_for_llm(logs)
        date_range = self._get_date_range_string(logs)
        
        prompts = {
            "daily": f"""以下の日報を要約してください。

日付: {date_range}
作業内容:
{log_text}

以下の形式で要約してください：
## 主な成果
- 

## 課題・問題点
- 

## 明日の予定
- 

要約:""",
            
            "weekly": f"""以下の週間作業ログを要約してください。

期間: {date_range}
作業内容:
{log_text}

以下の形式で要約してください：
## 今週の主な成果
- 

## 完了したタスク
- 

## 進行中のタスク
- 

## 課題・問題点
- 

## 来週の予定
- 

要約:""",
            
            "monthly": f"""以下の月間作業ログを要約してください。

期間: {date_range}
作業内容:
{log_text}

以下の形式で要約してください：
## 今月の主な成果
- 

## 完了したプロジェクト
- 

## 進行中のプロジェクト
- 

## 課題・改善点
- 

## 来月の計画
- 

要約:"""
        }
        
        return prompts.get(summary_type, prompts["weekly"])
    
    def _parse_structured_response(self, response_text: str, 
                                  summary_type: str) -> Dict[str, Any]:
        """構造化された応答を解析"""
        # 簡単な解析（実装は省略）
        sections = {}
        current_section = None
        current_items = []
        
        for line in response_text.split('\n'):
            line = line.strip()
            
            if line.startswith('## '):
                # 前のセクションを保存
                if current_section and current_items:
                    sections[current_section] = current_items
                
                # 新しいセクション開始
                current_section = line[3:].strip()
                current_items = []
                
            elif line.startswith('- ') and current_section:
                current_items.append(line[2:].strip())
        
        # 最後のセクションを保存
        if current_section and current_items:
            sections[current_section] = current_items
        
        return {
            "summary_type": summary_type,
            "sections": sections,
            "raw_response": response_text,
            "generated_at": datetime.now().isoformat()
        }
    
    def is_llm_available(self) -> bool:
        """LLMが利用可能かチェック"""
        return self.is_available
    
    def get_model_info(self) -> Dict[str, Any]:
        """モデル情報を取得"""
        if not self.is_available or not self.config:
            return {"available": False}
        
        return {
            "available": True,
            "model_path": self.config.model_path,
            "context_length": self.config.context_length,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature
        }
    
    def test_connection(self) -> bool:
        """接続テスト"""
        if not self.is_available:
            return False
        
        try:
            test_response = self.llm(
                "これはテストです。",
                max_tokens=10,
                temperature=0.1
            )
            return test_response is not None
            
        except Exception as e:
            print(f"LLM接続テストエラー: {e}")
            return False
    
    def summarize_text(self, text: str, max_length: int = 2000) -> str:
        """
        テキストを要約
        
        Args:
            text: 要約対象テキスト
            max_length: 最大文字数
            
        Returns:
            str: 要約されたテキスト
        """
        if not self.is_available:
            return "LLMが利用できません。統計的要約を使用してください。"
        
        try:
            # シンプルな要約プロンプト
            prompt = f"""以下のテキストを{max_length}文字以内で要約してください。

テキスト:
{text}

要約:"""
            
            response = self.llm(
                prompt,
                max_tokens=max_length // 2,  # 概算でトークン数を設定
                temperature=self.config.temperature,
                top_p=self.config.top_p,
                repeat_penalty=self.config.repeat_penalty,
                stop=["</s>", "Human:", "Assistant:"]
            )
            
            return response["choices"][0]["text"].strip()
            
        except Exception as e:
            return f"LLM要約エラー: {str(e)}" 