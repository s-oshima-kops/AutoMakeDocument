# -*- coding: utf-8 -*-
"""
要約表示ウィジェット
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, date
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
                             QLabel, QGroupBox, QSplitter, QPushButton,
                             QComboBox, QDateEdit, QSpinBox, QCheckBox,
                             QTabWidget, QTableWidget, QTableWidgetItem,
                             QProgressBar, QScrollArea, QListWidget,
                             QListWidgetItem, QDialog, QDialogButtonBox)
from PySide6.QtCore import Qt, QDate, QThread, Signal, QTimer
from PySide6.QtGui import QFont, QTextCharFormat, QColor

from core.data_manager import DataManager
from core.summarizer import Summarizer
from core.llm_processor import LLMProcessor
from utils.config_manager import ConfigManager
from utils.logger import Logger
from utils.date_utils import DateUtils

class SummaryWorker(QThread):
    """要約処理ワーカー"""
    
    progress_updated = Signal(int)
    summary_completed = Signal(dict)
    error_occurred = Signal(str)
    
    def __init__(self, data_manager: DataManager, summarizer: Summarizer,
                 llm_processor: LLMProcessor, logs: List[Dict], config: Dict[str, Any]):
        super().__init__()
        self.data_manager = data_manager
        self.summarizer = summarizer
        self.llm_processor = llm_processor
        self.logs = logs
        self.config = config
        
    def run(self):
        """要約処理を実行"""
        try:
            # 進捗更新
            self.progress_updated.emit(10)
            
            # テキストを統合
            combined_text = self.combine_logs()
            self.progress_updated.emit(30)
            
            # 要約実行
            summary_result = self.generate_summary(combined_text)
            self.progress_updated.emit(80)
            
            # キーワード抽出
            if self.config.get('extract_keywords', True):
                keywords = self.extract_keywords(combined_text)
                summary_result['keywords'] = keywords
                
            self.progress_updated.emit(100)
            
            # 結果を返す
            self.summary_completed.emit(summary_result)
            
        except Exception as e:
            self.error_occurred.emit(str(e))
            
    def combine_logs(self) -> str:
        """ログを統合"""
        combined_lines = []
        
        for log in self.logs:
            date_str = log.get('date', '')
            content = log.get('content', '')
            tags = log.get('tags', [])
            
            # 日付とタグを含めて統合
            combined_lines.append(f"【{date_str}】")
            if tags:
                combined_lines.append(f"タグ: {', '.join(tags)}")
            combined_lines.append(content)
            combined_lines.append("")
            
        return "\n".join(combined_lines)
        
    def generate_summary(self, text: str) -> Dict[str, Any]:
        """要約を生成"""
        summary_result = {
            'original_text': text,
            'summary_text': '',
            'stats': {},
            'generated_at': datetime.now().isoformat()
        }
        
        # 基本要約
        if self.config.get('use_llm', False):
            # LLM要約
            summary_result['summary_text'] = self.llm_processor.summarize_text(
                text, 
                max_length=self.config.get('max_chars', 2000)
            )
            summary_result['method'] = 'llm'
        else:
            # 統計的要約
            summary_result['summary_text'] = self.summarizer.summarize_text(
                text,
                sentences_count=self.config.get('summary_level', 3),
                method='textrank'
            )
            summary_result['method'] = 'textrank'
            
        # 統計情報を含める
        if self.config.get('include_stats', True):
            summary_result['stats'] = self.calculate_stats(text)
            
        return summary_result
        
    def extract_keywords(self, text: str) -> List[str]:
        """キーワードを抽出"""
        return self.summarizer.extract_keywords(text, top_k=10)
        
    def calculate_stats(self, text: str) -> Dict[str, Any]:
        """統計情報を計算"""
        lines = text.split('\n')
        words = text.split()
        
        return {
            'total_chars': len(text),
            'total_lines': len(lines),
            'total_words': len(words),
            'avg_line_length': sum(len(line) for line in lines) / max(len(lines), 1),
            'non_empty_lines': len([line for line in lines if line.strip()])
        }

class SummaryEditDialog(QDialog):
    """要約編集ダイアログ"""
    
    def __init__(self, summary_text: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("要約編集")
        self.setModal(True)
        self.resize(600, 400)
        
        self.setup_ui(summary_text)
        
    def setup_ui(self, summary_text: str):
        """UI設定"""
        layout = QVBoxLayout(self)
        
        # 編集エリア
        self.edit_text = QTextEdit()
        self.edit_text.setPlainText(summary_text)
        self.edit_text.setFont(QFont("Meiryo", 10))
        layout.addWidget(self.edit_text)
        
        # 文字数表示
        self.char_count_label = QLabel()
        self.update_char_count()
        self.edit_text.textChanged.connect(self.update_char_count)
        layout.addWidget(self.char_count_label)
        
        # ボタン
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def update_char_count(self):
        """文字数を更新"""
        text = self.edit_text.toPlainText()
        char_count = len(text)
        self.char_count_label.setText(f"文字数: {char_count}")
        
    def get_edited_text(self) -> str:
        """編集されたテキストを取得"""
        return self.edit_text.toPlainText()

class SummaryStatsWidget(QWidget):
    """要約統計ウィジェット"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """UI設定"""
        layout = QVBoxLayout(self)
        
        # 統計テーブル
        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(2)
        self.stats_table.setHorizontalHeaderLabels(["項目", "値"])
        self.stats_table.verticalHeader().setVisible(False)
        layout.addWidget(self.stats_table)
        
    def set_stats(self, stats: Dict[str, Any]):
        """統計情報を設定"""
        self.stats_table.setRowCount(len(stats))
        
        for row, (key, value) in enumerate(stats.items()):
            # 項目名の日本語化
            item_names = {
                'total_chars': '総文字数',
                'total_lines': '総行数',
                'total_words': '総単語数',
                'avg_line_length': '平均行長',
                'non_empty_lines': '非空行数'
            }
            
            item_name = item_names.get(key, key)
            
            # 値のフォーマット
            if isinstance(value, float):
                formatted_value = f"{value:.1f}"
            else:
                formatted_value = str(value)
                
            self.stats_table.setItem(row, 0, QTableWidgetItem(item_name))
            self.stats_table.setItem(row, 1, QTableWidgetItem(formatted_value))
            
        self.stats_table.resizeColumnsToContents()

class SummaryViewWidget(QWidget):
    """要約表示ウィジェット"""
    
    # シグナル定義
    summary_generated = Signal(dict)
    
    def __init__(self, data_manager: DataManager, summarizer: Summarizer,
                 llm_processor: LLMProcessor, config_manager: ConfigManager,
                 logger: Logger, parent=None):
        super().__init__(parent)
        
        self.data_manager = data_manager
        self.summarizer = summarizer
        self.llm_processor = llm_processor
        self.config_manager = config_manager
        self.logger = logger
        
        self.current_summary = None
        self.current_logs = []
        self.worker = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """UI設定"""
        layout = QVBoxLayout(self)
        
        # ヘッダー
        header_label = QLabel("要約表示")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(header_label)
        
        # 制御パネル
        control_group = QGroupBox("制御パネル")
        control_layout = QHBoxLayout(control_group)
        
        # 期間選択
        control_layout.addWidget(QLabel("期間:"))
        
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setDate(QDate.currentDate().addDays(-7))
        self.start_date_edit.setCalendarPopup(True)
        control_layout.addWidget(self.start_date_edit)
        
        control_layout.addWidget(QLabel("〜"))
        
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setDate(QDate.currentDate())
        self.end_date_edit.setCalendarPopup(True)
        control_layout.addWidget(self.end_date_edit)
        
        # 要約設定
        control_layout.addWidget(QLabel("要約レベル:"))
        self.summary_level_combo = QComboBox()
        self.summary_level_combo.addItems(["1 (簡潔)", "2 (標準)", "3 (詳細)", "4 (冗長)", "5 (完全)"])
        self.summary_level_combo.setCurrentIndex(2)
        control_layout.addWidget(self.summary_level_combo)
        
        # LLM使用
        self.use_llm_check = QCheckBox("LLM使用")
        control_layout.addWidget(self.use_llm_check)
        
        # 要約実行ボタン
        self.generate_button = QPushButton("要約生成")
        self.generate_button.clicked.connect(self.generate_summary)
        control_layout.addWidget(self.generate_button)
        
        control_layout.addStretch()
        layout.addWidget(control_group)
        
        # 進捗バー
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # メインコンテンツ
        main_splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(main_splitter)
        
        # 左側: 要約結果
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # 要約タブ
        self.summary_tabs = QTabWidget()
        
        # 要約テキストタブ
        self.summary_text_edit = QTextEdit()
        self.summary_text_edit.setReadOnly(True)
        self.summary_text_edit.setFont(QFont("Meiryo", 10))
        self.summary_tabs.addTab(self.summary_text_edit, "要約テキスト")
        
        # 元テキストタブ
        self.original_text_edit = QTextEdit()
        self.original_text_edit.setReadOnly(True)
        self.original_text_edit.setFont(QFont("Meiryo", 9))
        self.summary_tabs.addTab(self.original_text_edit, "元テキスト")
        
        left_layout.addWidget(self.summary_tabs)
        
        # 要約操作ボタン
        summary_button_layout = QHBoxLayout()
        
        self.edit_button = QPushButton("編集")
        self.edit_button.clicked.connect(self.edit_summary)
        self.edit_button.setEnabled(False)
        summary_button_layout.addWidget(self.edit_button)
        
        self.copy_button = QPushButton("コピー")
        self.copy_button.clicked.connect(self.copy_summary)
        self.copy_button.setEnabled(False)
        summary_button_layout.addWidget(self.copy_button)
        
        summary_button_layout.addStretch()
        
        self.regenerate_button = QPushButton("再生成")
        self.regenerate_button.clicked.connect(self.regenerate_summary)
        self.regenerate_button.setEnabled(False)
        summary_button_layout.addWidget(self.regenerate_button)
        
        left_layout.addLayout(summary_button_layout)
        
        main_splitter.addWidget(left_widget)
        
        # 右側: 統計とキーワード
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # 統計情報
        stats_group = QGroupBox("統計情報")
        stats_layout = QVBoxLayout(stats_group)
        
        self.stats_widget = SummaryStatsWidget()
        stats_layout.addWidget(self.stats_widget)
        
        right_layout.addWidget(stats_group)
        
        # キーワード
        keywords_group = QGroupBox("キーワード")
        keywords_layout = QVBoxLayout(keywords_group)
        
        self.keywords_list = QListWidget()
        keywords_layout.addWidget(self.keywords_list)
        
        right_layout.addWidget(keywords_group)
        
        main_splitter.addWidget(right_widget)
        
        # 分割比率設定
        main_splitter.setSizes([600, 300])
        
    def generate_summary(self):
        """要約を生成"""
        try:
            # 期間を取得
            start_date = self.start_date_edit.date().toPython()
            end_date = self.end_date_edit.date().toPython()
            
            # ログを取得
            self.current_logs = self.data_manager.get_work_logs_by_date_range(start_date, end_date)
            
            if not self.current_logs:
                self.logger.log_warning("指定期間にログが見つかりません")
                return
                
            # 設定を構築
            config = {
                'summary_level': self.summary_level_combo.currentIndex() + 1,
                'max_chars': 2000,
                'extract_keywords': True,
                'include_stats': True,
                'use_llm': self.use_llm_check.isChecked()
            }
            
            # ワーカーを開始
            self.start_summary_worker(config)
            
        except Exception as e:
            self.logger.log_error(f"要約生成エラー: {e}")
            
    def start_summary_worker(self, config: Dict[str, Any]):
        """要約ワーカーを開始"""
        # UI状態を更新
        self.generate_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # ワーカーを作成
        self.worker = SummaryWorker(
            self.data_manager,
            self.summarizer,
            self.llm_processor,
            self.current_logs,
            config
        )
        
        # シグナル接続
        self.worker.progress_updated.connect(self.progress_bar.setValue)
        self.worker.summary_completed.connect(self.on_summary_completed)
        self.worker.error_occurred.connect(self.on_summary_error)
        
        # ワーカー開始
        self.worker.start()
        
    def on_summary_completed(self, result: Dict[str, Any]):
        """要約完了時"""
        self.current_summary = result
        
        # 要約テキストを表示
        self.summary_text_edit.setPlainText(result.get('summary_text', ''))
        
        # 元テキストを表示
        self.original_text_edit.setPlainText(result.get('original_text', ''))
        
        # 統計情報を表示
        if 'stats' in result:
            self.stats_widget.set_stats(result['stats'])
            
        # キーワードを表示
        if 'keywords' in result:
            self.keywords_list.clear()
            for keyword in result['keywords']:
                self.keywords_list.addItem(keyword)
                
        # ボタンを有効化
        self.edit_button.setEnabled(True)
        self.copy_button.setEnabled(True)
        self.regenerate_button.setEnabled(True)
        
        # UI状態を復元
        self.generate_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        # シグナルを発行
        self.summary_generated.emit(result)
        
        # ログに記録
        self.logger.log_operation(f"要約生成完了: {result.get('method', 'unknown')}方式")
        
    def on_summary_error(self, error_message: str):
        """要約エラー時"""
        self.logger.log_error(f"要約生成エラー: {error_message}")
        
        # UI状態を復元
        self.generate_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        
    def edit_summary(self):
        """要約を編集"""
        if not self.current_summary:
            return
            
        dialog = SummaryEditDialog(self.current_summary.get('summary_text', ''), self)
        if dialog.exec() == QDialog.Accepted:
            edited_text = dialog.get_edited_text()
            
            # 要約を更新
            self.current_summary['summary_text'] = edited_text
            self.current_summary['edited'] = True
            self.current_summary['edited_at'] = datetime.now().isoformat()
            
            # 表示を更新
            self.summary_text_edit.setPlainText(edited_text)
            
            # ログに記録
            self.logger.log_operation("要約編集完了")
            
    def copy_summary(self):
        """要約をコピー"""
        if self.current_summary:
            text = self.current_summary.get('summary_text', '')
            if text:
                clipboard = self.parent().clipboard()
                clipboard.setText(text)
                self.logger.log_operation("要約をクリップボードにコピー")
                
    def regenerate_summary(self):
        """要約を再生成"""
        if self.current_logs:
            self.generate_summary()
            
    def get_current_summary(self) -> Optional[Dict[str, Any]]:
        """現在の要約を取得"""
        return self.current_summary
        
    def set_date_range(self, start_date: date, end_date: date):
        """日付範囲を設定"""
        self.start_date_edit.setDate(QDate(start_date.year, start_date.month, start_date.day))
        self.end_date_edit.setDate(QDate(end_date.year, end_date.month, end_date.day))
        
    def run_summarization(self):
        """要約を実行（エイリアス）"""
        self.generate_summary() 