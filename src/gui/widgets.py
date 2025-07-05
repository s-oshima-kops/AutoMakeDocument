# -*- coding: utf-8 -*-
"""
カスタムウィジェット
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QTextEdit, QComboBox,
                             QDateEdit, QSpinBox, QCheckBox, QListWidget,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QProgressBar, QGroupBox, QFrame)
from PySide6.QtCore import Qt, QDate, Signal, QTimer
from PySide6.QtGui import QFont, QPalette, QColor

class DateRangeWidget(QWidget):
    """日付範囲選択ウィジェット"""
    
    date_changed = Signal(QDate, QDate)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """UI設定"""
        layout = QHBoxLayout(self)
        
        # 開始日
        layout.addWidget(QLabel("開始日:"))
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setDate(QDate.currentDate().addDays(-7))
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.dateChanged.connect(self.on_date_changed)
        layout.addWidget(self.start_date_edit)
        
        layout.addWidget(QLabel("〜"))
        
        # 終了日
        layout.addWidget(QLabel("終了日:"))
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setDate(QDate.currentDate())
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.dateChanged.connect(self.on_date_changed)
        layout.addWidget(self.end_date_edit)
        
        layout.addStretch()
    
    def on_date_changed(self):
        """日付変更時の処理"""
        start_date = self.start_date_edit.date()
        end_date = self.end_date_edit.date()
        
        # 開始日が終了日より後の場合は調整
        if start_date > end_date:
            if self.sender() == self.start_date_edit:
                self.end_date_edit.setDate(start_date)
            else:
                self.start_date_edit.setDate(end_date)
        
        self.date_changed.emit(self.start_date_edit.date(), self.end_date_edit.date())
    
    def get_date_range(self):
        """日付範囲を取得"""
        return self.start_date_edit.date(), self.end_date_edit.date()
    
    def set_date_range(self, start_date, end_date):
        """日付範囲を設定"""
        self.start_date_edit.setDate(start_date)
        self.end_date_edit.setDate(end_date)

class LogStatisticsWidget(QWidget):
    """ログ統計表示ウィジェット"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """UI設定"""
        layout = QVBoxLayout(self)
        
        # グループボックス
        group_box = QGroupBox("ログ統計")
        group_layout = QVBoxLayout(group_box)
        
        # 統計情報テーブル
        self.stats_table = QTableWidget(0, 2)
        self.stats_table.setHorizontalHeaderLabels(["項目", "値"])
        header = self.stats_table.horizontalHeader()
        header.setStretchLastSection(True)
        self.stats_table.setAlternatingRowColors(True)
        
        group_layout.addWidget(self.stats_table)
        layout.addWidget(group_box)
    
    def update_statistics(self, stats):
        """統計情報を更新"""
        self.stats_table.setRowCount(len(stats))
        
        for row, (key, value) in enumerate(stats.items()):
            # 項目名
            item_name = QTableWidgetItem(str(key))
            self.stats_table.setItem(row, 0, item_name)
            
            # 値
            item_value = QTableWidgetItem(str(value))
            self.stats_table.setItem(row, 1, item_value)

class ProgressWidget(QWidget):
    """プログレス表示ウィジェット"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """UI設定"""
        layout = QVBoxLayout(self)
        
        # プログレスバー
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)
        
        # ステータスラベル
        self.status_label = QLabel("準備完了")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        # 詳細ラベル
        self.detail_label = QLabel("")
        self.detail_label.setAlignment(Qt.AlignCenter)
        self.detail_label.setWordWrap(True)
        layout.addWidget(self.detail_label)
        
        # 初期状態は非表示
        self.hide()
    
    def start_progress(self, message="処理中..."):
        """プログレス開始"""
        self.progress_bar.setRange(0, 0)  # 不確定プログレス
        self.status_label.setText(message)
        self.detail_label.setText("")
        self.show()
    
    def update_progress(self, value, maximum=100, message="", detail=""):
        """プログレス更新"""
        self.progress_bar.setRange(0, maximum)
        self.progress_bar.setValue(value)
        
        if message:
            self.status_label.setText(message)
        
        if detail:
            self.detail_label.setText(detail)
    
    def finish_progress(self, message="完了"):
        """プログレス完了"""
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        self.status_label.setText(message)
        self.detail_label.setText("")
        
        # 2秒後に非表示にする
        QTimer.singleShot(2000, self.hide)

class KeywordListWidget(QWidget):
    """キーワードリスト表示ウィジェット"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """UI設定"""
        layout = QVBoxLayout(self)
        
        # タイトル
        title_label = QLabel("キーワード")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title_label)
        
        # キーワードリスト
        self.keyword_list = QListWidget()
        self.keyword_list.setMaximumHeight(150)
        layout.addWidget(self.keyword_list)
    
    def set_keywords(self, keywords):
        """キーワードを設定"""
        self.keyword_list.clear()
        for keyword in keywords:
            self.keyword_list.addItem(keyword)

class SummaryStatsWidget(QWidget):
    """要約統計表示ウィジェット"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """UI設定"""
        layout = QVBoxLayout(self)
        
        # グループボックス
        group_box = QGroupBox("要約統計")
        group_layout = QVBoxLayout(group_box)
        
        # 統計情報のレイアウト
        stats_layout = QHBoxLayout()
        
        # 元文字数
        original_layout = QVBoxLayout()
        original_layout.addWidget(QLabel("元文字数"))
        self.original_count_label = QLabel("0")
        self.original_count_label.setAlignment(Qt.AlignCenter)
        self.original_count_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        original_layout.addWidget(self.original_count_label)
        stats_layout.addLayout(original_layout)
        
        # 要約文字数
        summary_layout = QVBoxLayout()
        summary_layout.addWidget(QLabel("要約文字数"))
        self.summary_count_label = QLabel("0")
        self.summary_count_label.setAlignment(Qt.AlignCenter)
        self.summary_count_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        summary_layout.addWidget(self.summary_count_label)
        stats_layout.addLayout(summary_layout)
        
        # 圧縮率
        ratio_layout = QVBoxLayout()
        ratio_layout.addWidget(QLabel("圧縮率"))
        self.ratio_label = QLabel("0%")
        self.ratio_label.setAlignment(Qt.AlignCenter)
        self.ratio_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2E7D32;")
        ratio_layout.addWidget(self.ratio_label)
        stats_layout.addLayout(ratio_layout)
        
        group_layout.addLayout(stats_layout)
        layout.addWidget(group_box)
    
    def update_stats(self, original_count, summary_count, compression_ratio):
        """統計情報を更新"""
        self.original_count_label.setText(f"{original_count:,}")
        self.summary_count_label.setText(f"{summary_count:,}")
        self.ratio_label.setText(f"{compression_ratio:.1f}%")

class OutputFormatWidget(QWidget):
    """出力形式選択ウィジェット"""
    
    format_changed = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """UI設定"""
        layout = QVBoxLayout(self)
        
        # グループボックス
        group_box = QGroupBox("出力形式")
        group_layout = QVBoxLayout(group_box)
        
        # 出力形式チェックボックス
        self.format_checkboxes = {}
        formats = [
            ("txt", "テキスト形式 (.txt)"),
            ("csv", "CSV形式 (.csv)"),
            ("xlsx", "Excel形式 (.xlsx)"),
            ("docx", "Word形式 (.docx)")
        ]
        
        for format_id, format_name in formats:
            checkbox = QCheckBox(format_name)
            checkbox.stateChanged.connect(lambda state, fmt=format_id: self.on_format_changed(fmt, state))
            self.format_checkboxes[format_id] = checkbox
            group_layout.addWidget(checkbox)
        
        layout.addWidget(group_box)
    
    def on_format_changed(self, format_id, state):
        """出力形式変更時の処理"""
        if state == Qt.Checked:
            self.format_changed.emit(format_id)
    
    def get_selected_formats(self):
        """選択された形式を取得"""
        selected = []
        for format_id, checkbox in self.format_checkboxes.items():
            if checkbox.isChecked():
                selected.append(format_id)
        return selected
    
    def set_selected_formats(self, formats):
        """選択された形式を設定"""
        for format_id, checkbox in self.format_checkboxes.items():
            checkbox.setChecked(format_id in formats)

class LogPreviewWidget(QWidget):
    """ログプレビューウィジェット"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """UI設定"""
        layout = QVBoxLayout(self)
        
        # タイトル
        title_label = QLabel("ログプレビュー")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title_label)
        
        # プレビューエリア
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMaximumHeight(200)
        layout.addWidget(self.preview_text)
    
    def set_preview_text(self, text):
        """プレビューテキストを設定"""
        self.preview_text.setPlainText(text)
    
    def clear_preview(self):
        """プレビューをクリア"""
        self.preview_text.clear() 