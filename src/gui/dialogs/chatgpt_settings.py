# -*- coding: utf-8 -*-
"""
ChatGPT設定ダイアログ
"""

from pathlib import Path
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLabel, QLineEdit, QPushButton, QComboBox, QTextEdit,
                             QCheckBox, QGroupBox, QProgressBar, QMessageBox,
                             QTabWidget, QWidget, QTableWidget, QTableWidgetItem)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont

from core.chatgpt_summarizer import ChatGPTSummarizer
from utils.logger import Logger


class ChatGPTTestWorker(QThread):
    """ChatGPT接続テストワーカー"""
    
    test_completed = Signal(dict)
    
    def __init__(self, chatgpt_summarizer: ChatGPTSummarizer):
        super().__init__()
        self.chatgpt_summarizer = chatgpt_summarizer
        
    def run(self):
        """接続テストを実行"""
        result = self.chatgpt_summarizer.test_connection()
        self.test_completed.emit(result)


class ChatGPTSettingsDialog(QDialog):
    """ChatGPT設定ダイアログ"""
    
    def __init__(self, config_dir: Path, logger: Logger, parent=None):
        super().__init__(parent)
        
        self.config_dir = config_dir
        self.logger = logger
        self.chatgpt_summarizer = ChatGPTSummarizer()
        
        self.setup_ui()
        self.load_settings()
        
    def setup_ui(self):
        """UI設定"""
        self.setWindowTitle("ChatGPT連携設定")
        self.setModal(True)
        self.resize(600, 500)
        
        layout = QVBoxLayout(self)
        
        # タブウィジェット
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # 設定タブ
        config_tab = self.create_config_tab()
        tab_widget.addTab(config_tab, "設定")
        
        # 使用統計タブ
        stats_tab = self.create_stats_tab()
        tab_widget.addTab(stats_tab, "使用統計")
        
        # 使用方法タブ
        help_tab = self.create_help_tab()
        tab_widget.addTab(help_tab, "使用方法")
        
        # ボタン
        button_layout = QHBoxLayout()
        
        self.test_button = QPushButton("接続テスト")
        self.test_button.clicked.connect(self.test_connection)
        button_layout.addWidget(self.test_button)
        
        button_layout.addStretch()
        
        save_button = QPushButton("保存")
        save_button.clicked.connect(self.save_settings)
        button_layout.addWidget(save_button)
        
        cancel_button = QPushButton("キャンセル")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        # プログレスバー
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
    def create_config_tab(self) -> QWidget:
        """設定タブを作成"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 基本設定
        basic_group = QGroupBox("基本設定")
        basic_layout = QFormLayout(basic_group)
        
        # ChatGPT有効/無効
        self.enable_chatgpt_check = QCheckBox("ChatGPT連携を有効にする")
        self.enable_chatgpt_check.stateChanged.connect(self.on_enable_changed)
        basic_layout.addRow("", self.enable_chatgpt_check)
        
        # APIキー
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_edit.setPlaceholderText("OpenAI APIキーを入力してください")
        basic_layout.addRow("APIキー:", self.api_key_edit)
        
        # モデル選択
        self.model_combo = QComboBox()
        self.model_combo.addItems(["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"])
        basic_layout.addRow("モデル:", self.model_combo)
        
        layout.addWidget(basic_group)
        
        # 詳細設定
        advanced_group = QGroupBox("詳細設定")
        advanced_layout = QFormLayout(advanced_group)
        
        # 最大トークン数
        self.max_tokens_combo = QComboBox()
        self.max_tokens_combo.addItems(["500", "1000", "1500", "2000"])
        self.max_tokens_combo.setCurrentText("1000")
        advanced_layout.addRow("最大トークン数:", self.max_tokens_combo)
        
        # 温度設定
        self.temperature_combo = QComboBox()
        self.temperature_combo.addItems(["0.3", "0.5", "0.7", "0.9"])
        self.temperature_combo.setCurrentText("0.7")
        advanced_layout.addRow("創造性（Temperature）:", self.temperature_combo)
        
        # 自動要約
        self.auto_summarize_check = QCheckBox("新しいログ保存時に自動要約を実行")
        advanced_layout.addRow("", self.auto_summarize_check)
        
        layout.addWidget(advanced_group)
        
        # 状態表示
        status_group = QGroupBox("接続状態")
        status_layout = QVBoxLayout(status_group)
        
        self.status_label = QLabel("未接続")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        status_layout.addWidget(self.status_label)
        
        self.last_test_label = QLabel("最後のテスト: なし")
        status_layout.addWidget(self.last_test_label)
        
        layout.addWidget(status_group)
        
        layout.addStretch()
        
        return widget
    
    def create_stats_tab(self) -> QWidget:
        """使用統計タブを作成"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 統計情報
        stats_group = QGroupBox("使用統計")
        stats_layout = QVBoxLayout(stats_group)
        
        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(2)
        self.stats_table.setHorizontalHeaderLabels(["項目", "値"])
        self.stats_table.verticalHeader().setVisible(False)
        stats_layout.addWidget(self.stats_table)
        
        # 統計更新ボタン
        update_stats_button = QPushButton("統計更新")
        update_stats_button.clicked.connect(self.update_stats)
        stats_layout.addWidget(update_stats_button)
        
        layout.addWidget(stats_group)
        
        # 料金目安
        pricing_group = QGroupBox("料金目安")
        pricing_layout = QVBoxLayout(pricing_group)
        
        pricing_text = QTextEdit()
        pricing_text.setReadOnly(True)
        pricing_text.setMaximumHeight(150)
        pricing_text.setPlainText("""
OpenAI API料金目安（2024年時点）:

GPT-3.5-turbo:
- 入力: $0.0010 / 1,000トークン
- 出力: $0.0020 / 1,000トークン

GPT-4:
- 入力: $0.0100 / 1,000トークン
- 出力: $0.0300 / 1,000トークン

※実際の料金は変動する可能性があります。
　最新情報はOpenAI公式サイトをご確認ください。
        """)
        pricing_layout.addWidget(pricing_text)
        
        layout.addWidget(pricing_group)
        
        return widget
    
    def create_help_tab(self) -> QWidget:
        """使用方法タブを作成"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setPlainText("""
ChatGPT連携機能の使用方法:

1. APIキーの取得
   - OpenAI公式サイト（https://platform.openai.com/）にアクセス
   - アカウントを作成またはログイン
   - API keysページでAPIキーを生成
   - 料金プランの設定も忘れずに

2. APIキーの設定
   - 「設定」タブでAPIキーを入力
   - 「ChatGPT連携を有効にする」をチェック
   - 「接続テスト」ボタンで動作確認
   - 「保存」ボタンで設定を保存

3. 使用方法
   - 要約表示画面で「ChatGPT要約」オプションを選択
   - クイック要約（Ctrl+Enter）でも利用可能
   - 各種テンプレートに応じた要約を生成

4. 注意事項
   - APIキーは安全に管理してください
   - 使用量に応じて料金が発生します
   - インターネット接続が必要です
   - 大量のテキストは料金が高くなる可能性があります

5. トラブルシューティング
   - 接続エラー: APIキーとネット接続を確認
   - 料金エラー: OpenAIアカウントの残高を確認
   - タイムアウト: テキストサイズを小さくしてみる

6. プライバシー
   - 作業ログはOpenAI APIに送信されます
   - 機密情報を含む場合は使用を控えてください
   - OpenAIのプライバシーポリシーをご確認ください
        """)
        layout.addWidget(help_text)
        
        return widget
    
    def on_enable_changed(self, state):
        """有効/無効変更時"""
        enabled = state == Qt.CheckState.Checked
        self.api_key_edit.setEnabled(enabled)
        self.model_combo.setEnabled(enabled)
        self.max_tokens_combo.setEnabled(enabled)
        self.temperature_combo.setEnabled(enabled)
        self.auto_summarize_check.setEnabled(enabled)
        self.test_button.setEnabled(enabled)
    
    def test_connection(self):
        """接続テスト"""
        api_key = self.api_key_edit.text().strip()
        if not api_key:
            QMessageBox.warning(self, "警告", "APIキーを入力してください")
            return
        
        # ChatGPT要約器を更新
        self.chatgpt_summarizer.set_api_key(api_key)
        self.chatgpt_summarizer.model = self.model_combo.currentText()
        
        # テストを実行
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 無限プログレス
        self.test_button.setEnabled(False)
        
        self.test_worker = ChatGPTTestWorker(self.chatgpt_summarizer)
        self.test_worker.test_completed.connect(self.on_test_completed)
        self.test_worker.start()
        
    def on_test_completed(self, result):
        """テスト完了時"""
        self.progress_bar.setVisible(False)
        self.test_button.setEnabled(True)
        
        if result.get("success", False):
            self.status_label.setText("接続成功")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            
            tokens_used = result.get("tokens_used", 0)
            model = result.get("model", "")
            
            QMessageBox.information(
                self, "接続成功", 
                f"ChatGPT APIに正常に接続できました。\n\n"
                f"モデル: {model}\n"
                f"使用トークン: {tokens_used}"
            )
            
            from datetime import datetime
            self.last_test_label.setText(f"最後のテスト: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
        else:
            self.status_label.setText("接続失敗")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
            
            error_msg = result.get("error", "不明なエラー")
            QMessageBox.critical(
                self, "接続エラー", 
                f"ChatGPT APIへの接続に失敗しました。\n\n"
                f"エラー: {error_msg}\n\n"
                f"APIキーとネットワーク接続を確認してください。"
            )
    
    def update_stats(self):
        """統計情報を更新"""
        stats = self.chatgpt_summarizer.get_usage_stats()
        
        # 統計情報を表示
        stats_items = [
            ("総リクエスト数", str(stats.get("total_requests", 0))),
            ("総トークン数", str(stats.get("total_tokens", 0))),
            ("使用モデル", stats.get("model", "")),
            ("最終使用日", stats.get("last_used", "なし"))
        ]
        
        self.stats_table.setRowCount(len(stats_items))
        
        for i, (key, value) in enumerate(stats_items):
            self.stats_table.setItem(i, 0, QTableWidgetItem(key))
            self.stats_table.setItem(i, 1, QTableWidgetItem(value))
    
    def load_settings(self):
        """設定を読み込み"""
        try:
            config_file = self.config_dir / "chatgpt_config.json"
            
            if self.chatgpt_summarizer.load_api_key(config_file):
                self.enable_chatgpt_check.setChecked(True)
                self.api_key_edit.setText(self.chatgpt_summarizer.api_key)
                
                # モデルを設定
                model_index = self.model_combo.findText(self.chatgpt_summarizer.model)
                if model_index >= 0:
                    self.model_combo.setCurrentIndex(model_index)
                    
                self.status_label.setText("設定済み")
                self.status_label.setStyleSheet("color: blue; font-weight: bold;")
                
        except Exception as e:
            self.logger.log_error(e, "ChatGPT設定読み込み")
    
    def save_settings(self):
        """設定を保存"""
        try:
            if not self.enable_chatgpt_check.isChecked():
                # ChatGPT無効の場合
                config_file = self.config_dir / "chatgpt_config.json"
                if config_file.exists():
                    import json
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)
                    
                    config_data["chatgpt"]["enabled"] = False
                    
                    with open(config_file, 'w', encoding='utf-8') as f:
                        json.dump(config_data, f, ensure_ascii=False, indent=2)
                
                QMessageBox.information(self, "保存完了", "ChatGPT連携を無効にしました")
                self.accept()
                return
            
            # 設定検証
            api_key = self.api_key_edit.text().strip()
            if not api_key:
                QMessageBox.warning(self, "警告", "APIキーを入力してください")
                return
            
            # 設定を保存
            config_file = self.config_dir / "chatgpt_config.json"
            self.chatgpt_summarizer.set_api_key(api_key)
            self.chatgpt_summarizer.model = self.model_combo.currentText()
            self.chatgpt_summarizer.save_api_key(api_key, config_file)
            
            QMessageBox.information(self, "保存完了", "ChatGPT設定を保存しました")
            self.accept()
            
        except Exception as e:
            self.logger.log_error(e, "ChatGPT設定保存")
            QMessageBox.critical(self, "エラー", f"設定保存中にエラーが発生しました: {str(e)}")
    
    def get_chatgpt_summarizer(self) -> ChatGPTSummarizer:
        """ChatGPT要約器を取得"""
        return self.chatgpt_summarizer 