# -*- coding: utf-8 -*-
"""
メインウィンドウ
"""

from pathlib import Path
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTabWidget, QMenuBar, QStatusBar, QMessageBox,
                             QProgressBar, QLabel, QSplitter, QTextEdit)
from PySide6.QtCore import Qt, QTimer, QThread, Signal
from PySide6.QtGui import QAction, QIcon, QKeySequence

from gui.log_input import LogInputWidget
from gui.template_selector import TemplateSelectorWidget
from gui.summary_view import SummaryViewWidget
from gui.output_config import OutputConfigWidget
from core.data_manager import DataManager
from core.summarizer import Summarizer
from core.template_engine import TemplateEngine
from core.llm_processor import LLMProcessor
from utils.config_manager import ConfigManager
from utils.logger import Logger

class MainWindow(QMainWindow):
    """メインウィンドウクラス"""
    
    def __init__(self, config_manager: ConfigManager, logger: Logger, app_dir: Path):
        """
        初期化
        
        Args:
            config_manager: 設定管理
            logger: ログ機能
            app_dir: アプリケーションディレクトリ
        """
        super().__init__()
        
        self.config_manager = config_manager
        self.logger = logger
        self.app_dir = app_dir
        
        # コアコンポーネントを初期化
        self.data_manager = DataManager(app_dir / "data")
        self.summarizer = Summarizer()
        self.template_engine = TemplateEngine(app_dir / "templates")
        self.llm_processor = LLMProcessor()
        
        # UI設定
        self.setup_ui()
        self.setup_menu()
        self.setup_statusbar()
        self.setup_connections()
        
        # 設定を読み込み
        self.load_settings()
        
        # 初期化完了をログに記録
        self.logger.log_operation("アプリケーション起動完了")
    
    def setup_ui(self):
        """UI設定"""
        self.setWindowTitle("ドキュメント自動要約&作成アプリ")
        
        # 中央ウィジェット
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # メインレイアウト
        main_layout = QVBoxLayout(central_widget)
        
        # タブウィジェット
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # 各タブのウィジェットを作成
        self.create_tabs()
        
        # ウィンドウサイズ設定
        app_config = self.config_manager.get_app_config()
        window_config = app_config.get("window", {})
        self.resize(window_config.get("width", 1200), window_config.get("height", 800))
    
    def create_tabs(self):
        """タブを作成"""
        # 1. ログ入力タブ
        self.log_input_widget = LogInputWidget(
            self.data_manager,
            self.config_manager,
            self.logger
        )
        self.tab_widget.addTab(self.log_input_widget, "📝 ログ入力")
        
        # 2. テンプレート選択タブ
        self.template_selector_widget = TemplateSelectorWidget(
            self.template_engine,
            self.config_manager,
            self.logger
        )
        self.tab_widget.addTab(self.template_selector_widget, "📋 テンプレート選択")
        
        # 3. 要約表示タブ
        self.summary_view_widget = SummaryViewWidget(
            self.data_manager,
            self.summarizer,
            self.llm_processor,
            self.config_manager,
            self.logger
        )
        self.tab_widget.addTab(self.summary_view_widget, "📊 要約表示")
        
        # 4. 出力設定タブ
        self.output_config_widget = OutputConfigWidget(
            self.template_engine,
            self.config_manager,
            self.logger,
            self.app_dir
        )
        self.tab_widget.addTab(self.output_config_widget, "📤 出力設定")
    
    def setup_menu(self):
        """メニューを設定"""
        menubar = self.menuBar()
        
        # ファイルメニュー
        file_menu = menubar.addMenu("ファイル(&F)")
        
        # 新規作成
        new_action = QAction("新規作成(&N)", self)
        new_action.setShortcut(QKeySequence.New)
        new_action.triggered.connect(self.new_log)
        file_menu.addAction(new_action)
        
        # 保存
        save_action = QAction("保存(&S)", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.save_log)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        # 設定
        settings_action = QAction("設定(&P)", self)
        settings_action.triggered.connect(self.open_settings)
        file_menu.addAction(settings_action)
        
        file_menu.addSeparator()
        
        # 終了
        exit_action = QAction("終了(&X)", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 編集メニュー
        edit_menu = menubar.addMenu("編集(&E)")
        
        # 元に戻す
        undo_action = QAction("元に戻す(&U)", self)
        undo_action.setShortcut(QKeySequence.Undo)
        edit_menu.addAction(undo_action)
        
        # やり直し
        redo_action = QAction("やり直し(&R)", self)
        redo_action.setShortcut(QKeySequence.Redo)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        # コピー
        copy_action = QAction("コピー(&C)", self)
        copy_action.setShortcut(QKeySequence.Copy)
        edit_menu.addAction(copy_action)
        
        # 貼り付け
        paste_action = QAction("貼り付け(&P)", self)
        paste_action.setShortcut(QKeySequence.Paste)
        edit_menu.addAction(paste_action)
        
        # 表示メニュー
        view_menu = menubar.addMenu("表示(&V)")
        
        # フルスクリーン
        fullscreen_action = QAction("フルスクリーン(&F)", self)
        fullscreen_action.setShortcut(QKeySequence.FullScreen)
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(fullscreen_action)
        
        # ツールメニュー
        tools_menu = menubar.addMenu("ツール(&T)")
        
        # 要約実行
        summarize_action = QAction("要約実行(&S)", self)
        summarize_action.setShortcut(QKeySequence("Ctrl+R"))
        summarize_action.triggered.connect(self.run_summarization)
        tools_menu.addAction(summarize_action)
        
        # 出力実行
        export_action = QAction("出力実行(&E)", self)
        export_action.setShortcut(QKeySequence("Ctrl+E"))
        export_action.triggered.connect(self.run_export)
        tools_menu.addAction(export_action)
        
        # ヘルプメニュー
        help_menu = menubar.addMenu("ヘルプ(&H)")
        
        # バージョン情報
        about_action = QAction("バージョン情報(&A)", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_statusbar(self):
        """ステータスバーを設定"""
        self.statusbar = self.statusBar()
        
        # ステータスラベル
        self.status_label = QLabel("準備完了")
        self.statusbar.addWidget(self.status_label)
        
        # プログレスバー
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.statusbar.addPermanentWidget(self.progress_bar)
        
        # 情報ラベル
        self.info_label = QLabel("")
        self.statusbar.addPermanentWidget(self.info_label)
    
    def setup_connections(self):
        """シグナル・スロット接続"""
        # タブ変更時のイベント
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
        # ログ入力ウィジェットのシグナル
        self.log_input_widget.log_saved.connect(self.on_log_saved)
        
        # テンプレート選択ウィジェットのシグナル
        self.template_selector_widget.template_selected.connect(self.on_template_selected)
        
        # 要約表示ウィジェットのシグナル
        self.summary_view_widget.summary_generated.connect(self.on_summary_generated)
        
        # 出力設定ウィジェットのシグナル
        self.output_config_widget.output_completed.connect(self.on_output_completed)
        
        # ウィジェット間のデータ連携
        self.template_selector_widget.template_selected.connect(self.on_template_selected_for_output)
        self.summary_view_widget.summary_generated.connect(self.on_summary_generated_for_output)
    
    def load_settings(self):
        """設定を読み込み"""
        try:
            user_settings = self.config_manager.get_user_settings()
            
            # 最後に使用したテンプレートを復元
            last_template = user_settings.get("last_template")
            if last_template:
                try:
                    # テンプレートリストから該当項目を選択
                    self.template_selector_widget.select_template_by_id(last_template)
                except Exception as template_error:
                    self.logger.log_error(template_error, "テンプレート選択")
            
            # 出力設定を復元
            try:
                output_format = user_settings.get("output_format", "docx")
                self.output_config_widget.set_output_format(output_format)
                
                output_dir = user_settings.get("output_directory")
                if output_dir:
                    self.output_config_widget.set_output_directory(output_dir)
            except Exception as output_error:
                self.logger.log_error(output_error, "出力設定復元")
            
            self.logger.log_operation("設定読み込み完了")
            
        except Exception as e:
            self.logger.log_error(e, "設定読み込み")
            # エラーが発生してもアプリケーションを起動させる
            self.logger.log_operation("設定読み込みでエラーが発生しましたが、デフォルト設定で起動します")
    
    def save_settings(self):
        """設定を保存"""
        try:
            user_settings = self.config_manager.get_user_settings()
            
            # 現在の設定を保存
            user_settings["last_template"] = self.template_selector_widget.get_selected_template()
            user_settings["output_format"] = self.output_config_widget.get_output_format()
            user_settings["output_directory"] = self.output_config_widget.get_output_directory()
            
            # ウィンドウサイズを保存
            app_config = self.config_manager.get_app_config()
            app_config["window"]["width"] = self.width()
            app_config["window"]["height"] = self.height()
            
            self.config_manager.save_user_settings(user_settings)
            self.logger.log_operation("設定保存完了")
            
        except Exception as e:
            self.logger.log_error(e, "設定保存")
    
    def new_log(self):
        """新規ログ作成"""
        self.log_input_widget.new_log()
        self.tab_widget.setCurrentIndex(0)  # ログ入力タブに切り替え
    
    def save_log(self):
        """ログ保存"""
        self.log_input_widget.save_log()
    
    def open_settings(self):
        """設定ダイアログを開く"""
        # 設定ダイアログの実装（省略）
        QMessageBox.information(self, "設定", "設定機能は未実装です。")
    
    def toggle_fullscreen(self):
        """フルスクリーン切り替え"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    def run_summarization(self):
        """要約実行"""
        self.summary_view_widget.run_summarization()
        self.tab_widget.setCurrentIndex(2)  # 要約表示タブに切り替え
    
    def run_export(self):
        """出力実行"""
        self.output_config_widget.run_export()
        self.tab_widget.setCurrentIndex(3)  # 出力設定タブに切り替え
    
    def show_about(self):
        """バージョン情報表示"""
        app_config = self.config_manager.get_app_config()
        about_text = f"""
        {app_config.get('app_name', 'ドキュメント自動要約&作成アプリ')}
        
        バージョン: {app_config.get('version', '1.0.0')}
        
        このアプリケーションは作業ログを自動的に要約し、
        各種レポート形式で出力することができます。
        
        © 2024 Auto Make Document Team
        """
        QMessageBox.about(self, "バージョン情報", about_text)
    
    def on_tab_changed(self, index):
        """タブ変更時の処理"""
        tab_names = ["ログ入力", "テンプレート選択", "要約表示", "出力設定"]
        if 0 <= index < len(tab_names):
            self.status_label.setText(f"現在のタブ: {tab_names[index]}")
            self.logger.log_operation(f"タブ切り替え: {tab_names[index]}")
    
    def on_log_saved(self, log_date, success):
        """ログ保存完了時の処理"""
        if success:
            self.status_label.setText(f"ログ保存完了: {log_date}")
            self.logger.log_operation(f"ログ保存: {log_date}")
        else:
            self.show_error("ログ保存エラー", "ログの保存に失敗しました")
    
    def on_template_selected(self, template_id, config):
        """テンプレート選択時の処理"""
        self.status_label.setText(f"テンプレート選択: {template_id}")
        self.logger.log_operation(f"テンプレート選択: {template_id}")
    
    def on_template_selected_for_output(self, template_id, config):
        """テンプレート選択時の出力設定への連携"""
        self.output_config_widget.set_template_id(template_id)
    
    def on_summary_generated(self, summary_data):
        """要約生成完了時の処理"""
        self.status_label.setText("要約生成完了")
        self.logger.log_operation("要約生成完了")
    
    def on_summary_generated_for_output(self, summary_data):
        """要約生成完了時の出力設定への連携"""
        self.output_config_widget.set_summary_data(summary_data)
    
    def on_output_completed(self, file_path):
        """出力完了時の処理"""
        self.status_label.setText(f"出力完了: {file_path}")
        self.logger.log_operation(f"出力完了: {file_path}")
    
    def show_error(self, title, message):
        """エラーメッセージ表示"""
        QMessageBox.critical(self, title, message)
    
    def show_info(self, title, message):
        """情報メッセージ表示"""
        QMessageBox.information(self, title, message)
    
    def set_progress(self, value, maximum=100):
        """プログレスバー設定"""
        self.progress_bar.setMaximum(maximum)
        self.progress_bar.setValue(value)
        self.progress_bar.setVisible(value < maximum)
    
    def closeEvent(self, event):
        """ウィンドウクローズイベント"""
        # 設定を保存
        self.save_settings()
        
        # ログに記録
        self.logger.log_operation("アプリケーション終了")
        
        event.accept() 