# -*- coding: utf-8 -*-
"""
ログ入力ウィジェット
"""

from datetime import date, timedelta
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTextEdit, QPushButton, QDateEdit, QLineEdit,
                             QComboBox, QListWidget, QListWidgetItem,
                             QMessageBox, QSplitter, QGroupBox, QFrame, QCheckBox)
from PySide6.QtCore import Qt, QDate, Signal, QTimer
from PySide6.QtGui import QTextCharFormat, QColor

from core.data_manager import DataManager
from utils.config_manager import ConfigManager
from utils.logger import Logger
from utils.date_utils import DateUtils
from gui.widgets import LogPreviewWidget, LogStatisticsWidget, ProgressWidget

class LogInputWidget(QWidget):
    """ログ入力ウィジェット"""
    
    log_saved = Signal(str, bool)  # 日付, 成功フラグ
    
    def __init__(self, data_manager: DataManager, config_manager: ConfigManager, logger: Logger):
        """
        初期化
        
        Args:
            data_manager: データ管理
            config_manager: 設定管理
            logger: ログ機能
        """
        super().__init__()
        
        self.data_manager = data_manager
        self.config_manager = config_manager
        self.logger = logger
        
        self.current_date = date.today()
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.auto_save)
        
        self.setup_ui()
        self.setup_connections()
        self.load_current_log()
    
    def setup_ui(self):
        """UI設定"""
        layout = QHBoxLayout(self)
        
        # スプリッター
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # 左側：入力エリア
        self.create_input_area(splitter)
        
        # 右側：プレビューと統計
        self.create_preview_area(splitter)
        
        # スプリッターの初期サイズ
        splitter.setSizes([600, 400])
    
    def create_input_area(self, parent):
        """入力エリアを作成"""
        input_widget = QWidget()
        layout = QVBoxLayout(input_widget)
        
        # ヘッダー部分
        header_group = QGroupBox("ログ入力")
        header_layout = QVBoxLayout(header_group)
        
        # 日付選択
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("日付:"))
        
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.fromString(DateUtils.format_date(self.current_date), "yyyy-MM-dd"))
        self.date_edit.setCalendarPopup(True)
        self.date_edit.dateChanged.connect(self.on_date_changed)
        date_layout.addWidget(self.date_edit)
        
        # 日付ナビゲーション
        prev_button = QPushButton("前日")
        prev_button.clicked.connect(self.go_previous_day)
        date_layout.addWidget(prev_button)
        
        today_button = QPushButton("今日")
        today_button.clicked.connect(self.go_today)
        date_layout.addWidget(today_button)
        
        next_button = QPushButton("翌日")
        next_button.clicked.connect(self.go_next_day)
        date_layout.addWidget(next_button)
        
        date_layout.addStretch()
        header_layout.addLayout(date_layout)
        
        # タグ入力
        tag_layout = QHBoxLayout()
        tag_layout.addWidget(QLabel("タグ:"))
        
        self.tag_input = QLineEdit()
        self.tag_input.setPlaceholderText("タグをカンマ区切りで入力（例：会議,開発,レビュー）")
        tag_layout.addWidget(self.tag_input)
        
        header_layout.addLayout(tag_layout)
        layout.addWidget(header_group)
        
        # メイン入力エリア
        content_group = QGroupBox("作業内容")
        content_layout = QVBoxLayout(content_group)
        
        # 作業内容入力
        self.content_edit = QTextEdit()
        self.content_edit.setPlaceholderText(
            "今日の作業内容を入力してください...\n\n"
            "例：\n"
            "- プロジェクトAの要件定義書を作成\n"
            "- チームミーティングに参加\n"
            "- バグ修正: ログイン機能の不具合を解決\n"
            "- コードレビュー: 新機能の実装をチェック"
        )
        self.content_edit.textChanged.connect(self.on_content_changed)
        content_layout.addWidget(self.content_edit)
        
        # 文字数表示
        self.char_count_label = QLabel("文字数: 0")
        self.char_count_label.setStyleSheet("color: #666; font-size: 12px;")
        content_layout.addWidget(self.char_count_label)
        
        layout.addWidget(content_group)
        
        # ボタンエリア
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("💾 保存")
        self.save_button.clicked.connect(self.save_log)
        self.save_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; padding: 10px 20px; }")
        button_layout.addWidget(self.save_button)
        
        self.clear_button = QPushButton("🗑️ クリア")
        self.clear_button.clicked.connect(self.clear_content)
        button_layout.addWidget(self.clear_button)
        
        self.copy_previous_button = QPushButton("📋 前日をコピー")
        self.copy_previous_button.clicked.connect(self.copy_previous_log)
        button_layout.addWidget(self.copy_previous_button)
        
        button_layout.addStretch()
        
        # 自動保存設定
        auto_save_checkbox = QCheckBox("自動保存")
        auto_save_checkbox.setChecked(True)
        auto_save_checkbox.stateChanged.connect(self.toggle_auto_save)
        button_layout.addWidget(auto_save_checkbox)
        
        layout.addLayout(button_layout)
        
        # プログレスウィジェット
        self.progress_widget = ProgressWidget()
        layout.addWidget(self.progress_widget)
        
        parent.addWidget(input_widget)
    
    def create_preview_area(self, parent):
        """プレビューエリアを作成"""
        preview_widget = QWidget()
        layout = QVBoxLayout(preview_widget)
        
        # ログ履歴
        history_group = QGroupBox("最近のログ")
        history_layout = QVBoxLayout(history_group)
        
        self.log_history = QListWidget()
        self.log_history.itemClicked.connect(self.on_history_selected)
        history_layout.addWidget(self.log_history)
        
        layout.addWidget(history_group)
        
        # プレビュー
        self.preview_widget = LogPreviewWidget()
        layout.addWidget(self.preview_widget)
        
        # 統計情報
        self.statistics_widget = LogStatisticsWidget()
        layout.addWidget(self.statistics_widget)
        
        parent.addWidget(preview_widget)
        
        # 初期データを読み込み
        self.update_log_history()
        self.update_statistics()
    
    def setup_connections(self):
        """シグナル・スロット接続"""
        # 自動保存タイマー設定
        self.toggle_auto_save(Qt.Checked)
    
    def on_date_changed(self, q_date):
        """日付変更時の処理"""
        new_date = q_date.toPython()
        if new_date != self.current_date:
            # 現在のログを保存確認
            if self.content_edit.toPlainText().strip() and self.has_unsaved_changes():
                reply = QMessageBox.question(
                    self, 
                    "未保存の変更",
                    "現在のログに未保存の変更があります。保存しますか？",
                    QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
                )
                
                if reply == QMessageBox.Yes:
                    self.save_log()
                elif reply == QMessageBox.Cancel:
                    # 日付変更をキャンセル
                    self.date_edit.setDate(QDate.fromString(DateUtils.format_date(self.current_date), "yyyy-MM-dd"))
                    return
            
            self.current_date = new_date
            self.load_current_log()
            self.update_log_history()
    
    def on_content_changed(self):
        """コンテンツ変更時の処理"""
        content = self.content_edit.toPlainText()
        char_count = len(content)
        self.char_count_label.setText(f"文字数: {char_count:,}")
        
        # プレビュー更新
        self.preview_widget.set_preview_text(content[:500] + ("..." if len(content) > 500 else ""))
        
        # 自動保存タイマーリセット
        if self.auto_save_timer.isActive():
            self.auto_save_timer.start(30000)  # 30秒後に自動保存
    
    def on_history_selected(self, item):
        """履歴選択時の処理"""
        date_str = item.data(Qt.UserRole)
        if date_str:
            selected_date = DateUtils.parse_date(date_str)
            if selected_date:
                self.current_date = selected_date
                self.date_edit.setDate(QDate.fromString(date_str, "yyyy-MM-dd"))
                self.load_current_log()
    
    def load_current_log(self):
        """現在の日付のログを読み込み"""
        log = self.data_manager.load_work_log(self.current_date)
        
        if log:
            self.content_edit.setPlainText(log.content)
            self.tag_input.setText(", ".join(log.tags))
            self.logger.log_operation(f"ログ読み込み: {self.current_date}")
        else:
            self.content_edit.clear()
            self.tag_input.clear()
            self.logger.log_operation(f"新規ログ作成: {self.current_date}")
        
        # プレビューを更新
        self.preview_widget.set_preview_text(self.content_edit.toPlainText())
    
    def save_log(self):
        """ログを保存"""
        content = self.content_edit.toPlainText().strip()
        tags = [tag.strip() for tag in self.tag_input.text().split(",") if tag.strip()]
        
        if not content:
            QMessageBox.warning(self, "警告", "作業内容が入力されていません。")
            return
        
        try:
            self.progress_widget.start_progress("保存中...")
            
            success = self.data_manager.save_work_log(self.current_date, content, tags)
            
            if success:
                self.progress_widget.finish_progress("保存完了")
                self.log_saved.emit(DateUtils.format_date(self.current_date), True)
                self.update_log_history()
                self.update_statistics()
                QMessageBox.information(self, "成功", "ログが正常に保存されました。")
            else:
                self.progress_widget.finish_progress("保存失敗")
                self.log_saved.emit(DateUtils.format_date(self.current_date), False)
                QMessageBox.critical(self, "エラー", "ログの保存に失敗しました。")
                
        except Exception as e:
            self.progress_widget.finish_progress("保存失敗")
            self.logger.log_error(e, "ログ保存")
            QMessageBox.critical(self, "エラー", f"保存中にエラーが発生しました: {str(e)}")
    
    def auto_save(self):
        """自動保存"""
        content = self.content_edit.toPlainText().strip()
        if content and self.has_unsaved_changes():
            tags = [tag.strip() for tag in self.tag_input.text().split(",") if tag.strip()]
            success = self.data_manager.save_work_log(self.current_date, content, tags)
            
            if success:
                self.logger.log_operation(f"自動保存: {self.current_date}")
                # ステータス表示（控えめに）
                self.char_count_label.setText(f"文字数: {len(content):,} (自動保存済み)")
                QTimer.singleShot(2000, lambda: self.char_count_label.setText(f"文字数: {len(content):,}"))
    
    def clear_content(self):
        """コンテンツをクリア"""
        if self.content_edit.toPlainText().strip():
            reply = QMessageBox.question(
                self,
                "確認",
                "作業内容をクリアしますか？未保存の内容は失われます。",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.content_edit.clear()
                self.tag_input.clear()
                self.preview_widget.clear_preview()
    
    def copy_previous_log(self):
        """前日のログをコピー"""
        previous_date = DateUtils.get_previous_business_day(self.current_date)
        previous_log = self.data_manager.load_work_log(previous_date)
        
        if previous_log:
            reply = QMessageBox.question(
                self,
                "確認",
                f"{DateUtils.format_date_japanese(previous_date)}のログをコピーしますか？\n"
                f"現在の内容は上書きされます。",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.content_edit.setPlainText(previous_log.content)
                self.tag_input.setText(", ".join(previous_log.tags))
                self.logger.log_operation(f"前日ログコピー: {previous_date} -> {self.current_date}")
        else:
            QMessageBox.information(
                self,
                "情報",
                f"{DateUtils.format_date_japanese(previous_date)}のログが見つかりません。"
            )
    
    def go_previous_day(self):
        """前日に移動"""
        previous_date = self.current_date - timedelta(days=1)
        self.date_edit.setDate(QDate.fromString(DateUtils.format_date(previous_date), "yyyy-MM-dd"))
    
    def go_today(self):
        """今日に移動"""
        today = date.today()
        self.date_edit.setDate(QDate.fromString(DateUtils.format_date(today), "yyyy-MM-dd"))
    
    def go_next_day(self):
        """翌日に移動"""
        next_date = self.current_date + timedelta(days=1)
        self.date_edit.setDate(QDate.fromString(DateUtils.format_date(next_date), "yyyy-MM-dd"))
    
    def toggle_auto_save(self, state):
        """自動保存の切り替え"""
        if state == Qt.Checked:
            self.auto_save_timer.start(30000)  # 30秒間隔
        else:
            self.auto_save_timer.stop()
    
    def update_log_history(self):
        """ログ履歴を更新"""
        self.log_history.clear()
        
        # 最近のログ日付を取得
        recent_dates = self.data_manager.get_all_log_dates()[-10:]  # 最新10件
        recent_dates.reverse()  # 新しい順に並べ替え
        
        for log_date in recent_dates:
            log = self.data_manager.load_work_log(log_date)
            if log:
                date_str = DateUtils.format_date_japanese(log_date)
                preview = log.content[:50] + ("..." if len(log.content) > 50 else "")
                
                item = QListWidgetItem(f"{date_str}\n{preview}")
                item.setData(Qt.UserRole, DateUtils.format_date(log_date))
                
                # 現在の日付は強調表示
                if log_date == self.current_date:
                    item.setBackground(QColor("#E3F2FD"))
                
                self.log_history.addItem(item)
    
    def update_statistics(self):
        """統計情報を更新"""
        stats = self.data_manager.get_statistics()
        
        # 表示用に整形
        display_stats = {
            "総ログ数": f"{stats['total_logs']}件",
            "総文字数": f"{stats['total_characters']:,}文字",
            "平均文字数": f"{stats['average_characters_per_log']:,}文字/日",
            "最初のログ": DateUtils.format_date_japanese(stats['first_log_date']) if stats['first_log_date'] else "なし",
            "最新のログ": DateUtils.format_date_japanese(stats['last_log_date']) if stats['last_log_date'] else "なし"
        }
        
        self.statistics_widget.update_statistics(display_stats)
    
    def has_unsaved_changes(self):
        """未保存の変更があるかチェック"""
        current_log = self.data_manager.load_work_log(self.current_date)
        current_content = self.content_edit.toPlainText().strip()
        current_tags = [tag.strip() for tag in self.tag_input.text().split(",") if tag.strip()]
        
        if current_log:
            return (current_content != current_log.content.strip() or 
                   current_tags != current_log.tags)
        else:
            return bool(current_content)
    
    def new_log(self):
        """新規ログ作成"""
        self.go_today()
        self.content_edit.setFocus()
    
    # キーボードショートカット対応メソッド
    def get_current_content(self):
        """現在のログ内容を取得"""
        return self.content_edit.toPlainText().strip()
    
    def refresh_data(self):
        """データを更新"""
        try:
            # 現在のログを再読み込み
            self.load_current_log()
            
            # 履歴と統計を更新
            self.update_log_history()
            self.update_statistics()
            
            self.logger.log_operation("データ更新完了")
            
        except Exception as e:
            self.logger.log_error(e, "データ更新")
            QMessageBox.critical(self, "エラー", f"データ更新中にエラーが発生しました: {str(e)}")
    
    def duplicate_current_log(self):
        """現在のログを複製"""
        try:
            current_content = self.content_edit.toPlainText().strip()
            current_tags = [tag.strip() for tag in self.tag_input.text().split(",") if tag.strip()]
            
            if not current_content:
                return False
            
            # 明日の日付で複製
            tomorrow = self.current_date + timedelta(days=1)
            existing_log = self.data_manager.load_work_log(tomorrow)
            
            if existing_log:
                reply = QMessageBox.question(
                    self,
                    "確認",
                    f"{DateUtils.format_date_japanese(tomorrow)}のログが既に存在します。\n"
                    f"上書きしますか？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply != QMessageBox.StandardButton.Yes:
                    return False
            
            # 複製実行
            success = self.data_manager.save_work_log(tomorrow, current_content, current_tags)
            
            if success:
                self.logger.log_operation(f"ログ複製: {self.current_date} -> {tomorrow}")
                self.update_log_history()
                return True
            else:
                return False
                
        except Exception as e:
            self.logger.log_error(e, "ログ複製")
            return False
    
    def delete_current_log(self):
        """現在のログを削除"""
        try:
            existing_log = self.data_manager.load_work_log(self.current_date)
            
            if not existing_log:
                return False
            
            # 削除実行
            success = self.data_manager.delete_work_log(self.current_date)
            
            if success:
                self.content_edit.clear()
                self.tag_input.clear()
                self.preview_widget.clear_preview()
                self.update_log_history()
                self.update_statistics()
                self.logger.log_operation(f"ログ削除: {self.current_date}")
                return True
            else:
                return False
                
        except Exception as e:
            self.logger.log_error(e, "ログ削除")
            return False
    
    def open_snippet_manager(self):
        """定型文管理ダイアログを開く"""
        try:
            # 簡単な定型文管理ダイアログを実装
            from gui.dialogs.snippet_manager import SnippetManagerDialog
            
            dialog = SnippetManagerDialog(self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                selected_snippet = dialog.get_selected_snippet()
                if selected_snippet:
                    # 選択された定型文を現在のカーソル位置に挿入
                    cursor = self.content_edit.textCursor()
                    cursor.insertText(selected_snippet)
                    self.content_edit.setTextCursor(cursor)
                    
        except ImportError:
            # 定型文管理ダイアログが未実装の場合の簡易版
            snippets = [
                "本日の作業内容:",
                "- 会議参加: ",
                "- 開発作業: ",
                "- レビュー: ",
                "- 問題・課題: ",
                "- 明日の予定: "
            ]
            
            from PySide6.QtWidgets import QInputDialog
            snippet, ok = QInputDialog.getItem(
                self, "定型文挿入", "挿入する定型文を選択:", 
                snippets, 0, False
            )
            
            if ok and snippet:
                cursor = self.content_edit.textCursor()
                cursor.insertText(snippet)
                self.content_edit.setTextCursor(cursor)
                
        except Exception as e:
            self.logger.log_error(e, "定型文管理")
            QMessageBox.critical(self, "エラー", f"定型文管理中にエラーが発生しました: {str(e)}") 