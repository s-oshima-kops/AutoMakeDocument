# -*- coding: utf-8 -*-
"""
要約機能クラス（簡素化版）
"""

import re
from typing import List, Dict, Any, Optional
from datetime import date
from dataclasses import dataclass

# 要約ライブラリ（無効化）
# from sumy.parsers.plaintext import PlaintextParser
# from sumy.nlp.tokenizers import Tokenizer
# from sumy.summarizers.text_rank import TextRankSummarizer
# from sumy.summarizers.lex_rank import LexRankSummarizer
# from sumy.summarizers.lsa import LsaSummarizer
# from sumy.nlp.stemmers import Stemmer
# from sumy.utils import get_stop_words

# 日本語形態素解析（無効化）
# try:
#     from janome.tokenizer import Tokenizer as JanomeTokenizer
#     JANOME_AVAILABLE = True
# except ImportError:
#     JANOME_AVAILABLE = False
JANOME_AVAILABLE = False

from core.data_manager import WorkLog
from utils.date_utils import DateUtils

@dataclass
class SummaryResult:
    """要約結果データクラス"""
    summary_text: str
    key_points: List[str]
    word_count: int
    original_count: int
    compression_ratio: float
    method: str
    created_at: str

class Summarizer:
    """要約機能クラス（簡素化版）"""
    
    def __init__(self, language: str = "japanese"):
        """
        初期化（簡素化版）
        
        Args:
            language: 言語設定
        """
        self.language = language
        # self.stemmer = Stemmer(language)
        
        # ストップワード取得（無効化）
        # try:
        #     self.stop_words = get_stop_words(language)
        # except Exception:
        #     # 日本語ストップワードが利用できない場合はデフォルトの英語を使用
        #     try:
        #         self.stop_words = get_stop_words("english")
        #     except Exception:
        #         # それでもダメな場合は空のリストを使用
        #         self.stop_words = []
        self.stop_words = []
        
        # 日本語形態素解析器（無効化）
        self.janome_tokenizer = None
        
        # 要約器の設定（無効化）
        # self.summarizers = {
        #     "textrank": TextRankSummarizer(self.stemmer),
        #     "lexrank": LexRankSummarizer(self.stemmer),
        #     "lsa": LsaSummarizer(self.stemmer)
        # }
        self.summarizers = {}
        
        # 各要約器のストップワード設定（無効化）
        # for summarizer in self.summarizers.values():
        #     summarizer.stop_words = self.stop_words
    
    def summarize_work_logs(self, logs: List[WorkLog], method: str = "textrank", 
                          sentences_count: int = 5) -> SummaryResult:
        """
        作業ログを要約（簡素化版）
        
        Args:
            logs: 作業ログリスト
            method: 要約手法（textrank, lexrank, lsa）
            sentences_count: 要約文の数
            
        Returns:
            SummaryResult: 要約結果
        """
        # テキストを結合
        combined_text = self._combine_logs(logs)
        
        if not combined_text.strip():
            return SummaryResult(
                summary_text="要約するテキストがありません。",
                key_points=[],
                word_count=0,
                original_count=0,
                compression_ratio=0.0,
                method=method,
                created_at=DateUtils.get_now().isoformat()
            )
        
        # 簡素化版：単純にテキストを分割して最初の部分を返す
        summary_sentences = self._extract_summary(combined_text, method, sentences_count)
        summary_text = "\n".join(summary_sentences)
        
        # キーポイント抽出
        key_points = self._extract_key_points(combined_text)
        
        # 統計情報計算
        original_count = len(combined_text)
        word_count = len(summary_text)
        compression_ratio = (word_count / original_count) * 100 if original_count > 0 else 0
        
        return SummaryResult(
            summary_text=summary_text,
            key_points=key_points,
            word_count=word_count,
            original_count=original_count,
            compression_ratio=compression_ratio,
            method=method,
            created_at=DateUtils.get_now().isoformat()
        )
    
    def _combine_logs(self, logs: List[WorkLog]) -> str:
        """
        作業ログを結合
        
        Args:
            logs: 作業ログリスト
            
        Returns:
            str: 結合されたテキスト
        """
        combined_parts = []
        
        for log in logs:
            if log.content.strip():
                # 日付情報を追加
                log_date = DateUtils.parse_date(log.date)
                if log_date:
                    date_str = DateUtils.format_date_japanese(log_date)
                    combined_parts.append(f"【{date_str}】")
                
                # 内容を追加
                combined_parts.append(log.content.strip())
                combined_parts.append("")  # 空行で区切り
        
        return "\n".join(combined_parts)
    
    def _extract_summary(self, text: str, method: str, sentences_count: int) -> List[str]:
        """
        テキストから要約を抽出（簡素化版）
        
        Args:
            text: 要約対象テキスト
            method: 要約手法
            sentences_count: 要約文の数
            
        Returns:
            List[str]: 要約文リスト
        """
        try:
            # テキストの前処理
            cleaned_text = self._preprocess_text(text)
            
            if not cleaned_text.strip():
                return ["要約するテキストがありません。"]
            
            # 簡素化版：単純にテキストを分割して最初の部分を返す
            sentences = cleaned_text.split('。')
            sentences = [s.strip() for s in sentences if s.strip()]
            
            # 指定された数の文を返す
            if len(sentences) <= sentences_count:
                return sentences
            else:
                return sentences[:sentences_count]
                
        except Exception as e:
            print(f"要約処理エラー: {e}")
            return ["要約処理でエラーが発生しました。"]
    
    def _preprocess_text(self, text: str) -> str:
        """
        テキストの前処理
        
        Args:
            text: 前処理対象テキスト
            
        Returns:
            str: 前処理済みテキスト
        """
        # 改行を正規化
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # 連続する空白を単一の空白に変換
        text = re.sub(r'\s+', ' ', text)
        
        # 前後の空白を削除
        text = text.strip()
        
        return text
    
    def _extract_key_points(self, text: str, max_points: int = 10) -> List[str]:
        """
        キーポイント抽出（簡素化版）
        
        Args:
            text: 抽出対象テキスト
            max_points: 最大抽出数
            
        Returns:
            List[str]: キーポイントリスト
        """
        try:
            # 簡素化版：単純にキーワードを抽出
            keywords = self._extract_key_points_generic(text, max_points)
            return keywords
        except Exception as e:
            print(f"キーポイント抽出エラー: {e}")
            return []
    
    def _extract_key_points_generic(self, text: str, max_points: int) -> List[str]:
        """
        汎用的なキーポイント抽出（簡素化版）
        
        Args:
            text: 抽出対象テキスト
            max_points: 最大抽出数
            
        Returns:
            List[str]: キーポイントリスト
        """
        try:
            # 句読点で分割
            sentences = re.split(r'[。、！？\n]', text)
            
            # 空文字列を除去
            sentences = [s.strip() for s in sentences if s.strip()]
            
            # 短い文をキーポイントとして扱う
            key_points = []
            for sentence in sentences:
                if 5 <= len(sentence) <= 50:  # 適度な長さの文
                    key_points.append(sentence)
                    if len(key_points) >= max_points:
                        break
            
            return key_points[:max_points]
            
        except Exception as e:
            print(f"汎用キーポイント抽出エラー: {e}")
            return []
    
    def create_structured_summary(self, logs: List[WorkLog], template_format: str = "detailed") -> Dict[str, Any]:
        """
        構造化された要約を作成（簡素化版）
        
        Args:
            logs: 作業ログリスト
            template_format: テンプレート形式
            
        Returns:
            Dict[str, Any]: 構造化された要約データ
        """
        summary_result = self.summarize_work_logs(logs)
        
        # 基本的な構造化データ
        structured_data = {
            "summary_text": summary_result.summary_text,
            "key_points": summary_result.key_points,
            "statistics": {
                "word_count": summary_result.word_count,
                "original_count": summary_result.original_count,
                "compression_ratio": summary_result.compression_ratio,
                "log_count": len(logs)
            },
            "generated_at": summary_result.created_at,
            "method": summary_result.method
        }
        
        return structured_data
    
    def summarize_text(self, text: str, sentences_count: int = 5, method: str = "textrank") -> str:
        """
        テキストを要約（簡素化版）
        
        Args:
            text: 要約対象テキスト
            sentences_count: 要約文の数
            method: 要約手法
            
        Returns:
            str: 要約されたテキスト
        """
        try:
            summary_sentences = self._extract_summary(text, method, sentences_count)
            return "\n".join(summary_sentences)
        except Exception as e:
            print(f"テキスト要約エラー: {e}")
            return "テキスト要約でエラーが発生しました。"
    
    def extract_keywords(self, text: str, top_k: int = 10) -> List[str]:
        """
        キーワード抽出（簡素化版）
        
        Args:
            text: 抽出対象テキスト
            top_k: 抽出数
            
        Returns:
            List[str]: キーワードリスト
        """
        try:
            return self._extract_key_points(text, top_k)
        except Exception as e:
            print(f"キーワード抽出エラー: {e}")
            return [] 