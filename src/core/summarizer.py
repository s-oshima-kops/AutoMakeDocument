# -*- coding: utf-8 -*-
"""
要約機能クラス
"""

import re
from typing import List, Dict, Any, Optional
from datetime import date
from dataclasses import dataclass

# 要約ライブラリ
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.text_rank import TextRankSummarizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

# 日本語形態素解析
try:
    from janome.tokenizer import Tokenizer as JanomeTokenizer
    JANOME_AVAILABLE = True
except ImportError:
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
    """要約機能クラス"""
    
    def __init__(self, language: str = "japanese"):
        """
        初期化
        
        Args:
            language: 言語設定
        """
        self.language = language
        self.stemmer = Stemmer(language)
        
        # ストップワード取得（エラーハンドリング付き）
        try:
            self.stop_words = get_stop_words(language)
        except Exception:
            # 日本語ストップワードが利用できない場合はデフォルトの英語を使用
            try:
                self.stop_words = get_stop_words("english")
            except Exception:
                # それでもダメな場合は空のリストを使用
                self.stop_words = []
        
        # 日本語形態素解析器（実行ファイルでは無効化）
        # PyInstallerでビルドした場合、辞書ファイルの問題を回避
        self.janome_tokenizer = None
        
        # 要約器の設定
        self.summarizers = {
            "textrank": TextRankSummarizer(self.stemmer),
            "lexrank": LexRankSummarizer(self.stemmer),
            "lsa": LsaSummarizer(self.stemmer)
        }
        
        # 各要約器のストップワード設定
        for summarizer in self.summarizers.values():
            summarizer.stop_words = self.stop_words
    
    def summarize_work_logs(self, logs: List[WorkLog], method: str = "textrank", 
                          sentences_count: int = 5) -> SummaryResult:
        """
        作業ログを要約
        
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
        
        # 要約実行
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
        テキストから要約を抽出
        
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
            
            # パーサーとトークナイザーを設定
            parser = PlaintextParser.from_string(cleaned_text, Tokenizer(self.language))
            
            # 要約器を選択
            summarizer = self.summarizers.get(method, self.summarizers["textrank"])
            
            # 要約実行
            summary = summarizer(parser.document, sentences_count)
            
            # 要約文を文字列に変換
            summary_sentences = [str(sentence) for sentence in summary]
            
            return summary_sentences if summary_sentences else ["要約の生成に失敗しました。"]
            
        except Exception as e:
            print(f"要約抽出エラー: {e}")
            return [f"要約の生成中にエラーが発生しました: {str(e)}"]
    
    def _preprocess_text(self, text: str) -> str:
        """
        テキストの前処理
        
        Args:
            text: 処理対象テキスト
            
        Returns:
            str: 前処理されたテキスト
        """
        # 不要な文字を削除
        text = re.sub(r'[【】「」（）()[\]{}]', '', text)
        
        # 複数の空白を単一の空白に変換
        text = re.sub(r'\s+', ' ', text)
        
        # 改行を適切に処理
        text = re.sub(r'\n\s*\n', '\n', text)
        
        return text.strip()
    
    def _extract_key_points(self, text: str, max_points: int = 10) -> List[str]:
        """
        キーポイントを抽出
        
        Args:
            text: 処理対象テキスト
            max_points: 最大キーポイント数
            
        Returns:
            List[str]: キーポイントリスト
        """
        key_points = []
        
        try:
            # 日本語の場合、形態素解析を使用
            if self.janome_tokenizer and self.language == "japanese":
                key_points = self._extract_key_points_japanese(text, max_points)
            else:
                key_points = self._extract_key_points_generic(text, max_points)
                
        except Exception as e:
            print(f"キーポイント抽出エラー: {e}")
            key_points = ["キーポイントの抽出に失敗しました。"]
        
        return key_points
    
    def _extract_key_points_japanese(self, text: str, max_points: int) -> List[str]:
        """
        日本語テキストからキーポイントを抽出
        
        Args:
            text: 処理対象テキスト
            max_points: 最大キーポイント数
            
        Returns:
            List[str]: キーポイントリスト
        """
        # 形態素解析器が利用できない場合は汎用的な方法を使用
        if self.janome_tokenizer is None:
            return self._extract_key_points_generic(text, max_points)
        
        # 形態素解析で名詞を抽出
        words = []
        for token in self.janome_tokenizer.tokenize(text, wakati=False):
            features = token.part_of_speech.split(',')
            if features[0] == '名詞' and len(token.surface) > 1:
                words.append(token.surface)
        
        # 単語の頻度を計算
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # 頻度の高い単語を抽出
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        # 上位の単語をキーポイントとして返す
        key_points = [word for word, freq in sorted_words[:max_points] if freq > 1]
        
        return key_points
    
    def _extract_key_points_generic(self, text: str, max_points: int) -> List[str]:
        """
        一般的なテキストからキーポイントを抽出
        
        Args:
            text: 処理対象テキスト
            max_points: 最大キーポイント数
            
        Returns:
            List[str]: キーポイントリスト
        """
        # 単語に分割
        words = re.findall(r'\b\w+\b', text.lower())
        
        # ストップワードを除去
        filtered_words = [word for word in words if word not in self.stop_words and len(word) > 2]
        
        # 単語の頻度を計算
        word_freq = {}
        for word in filtered_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # 頻度の高い単語を抽出
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        # 上位の単語をキーポイントとして返す
        key_points = [word for word, freq in sorted_words[:max_points] if freq > 1]
        
        return key_points
    
    def create_structured_summary(self, logs: List[WorkLog], template_format: str = "detailed") -> Dict[str, Any]:
        """
        構造化された要約を作成
        
        Args:
            logs: 作業ログリスト
            template_format: テンプレート形式（detailed, simple, bullet）
            
        Returns:
            Dict[str, Any]: 構造化された要約
        """
        # 基本要約を取得
        summary_result = self.summarize_work_logs(logs)
        
        # 日付別の作業内容を整理
        daily_summaries = {}
        for log in logs:
            log_date = DateUtils.parse_date(log.date)
            if log_date and log.content.strip():
                date_str = DateUtils.format_date_japanese(log_date)
                daily_summaries[date_str] = log.content.strip()
        
        # 期間情報を計算
        dates = [DateUtils.parse_date(log.date) for log in logs if log.date]
        dates = [d for d in dates if d is not None]
        
        period_info = {}
        if dates:
            period_info = {
                "start_date": DateUtils.format_date_japanese(min(dates)),
                "end_date": DateUtils.format_date_japanese(max(dates)),
                "total_days": len(dates)
            }
        
        return {
            "summary": summary_result.summary_text,
            "key_points": summary_result.key_points,
            "daily_summaries": daily_summaries,
            "period_info": period_info,
            "statistics": {
                "total_logs": len(logs),
                "original_characters": summary_result.original_count,
                "summary_characters": summary_result.word_count,
                "compression_ratio": summary_result.compression_ratio
            },
            "created_at": summary_result.created_at
        } 