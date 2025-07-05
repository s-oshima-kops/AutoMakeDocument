# -*- coding: utf-8 -*-
"""
テンプレート選択ウィジェット
"""

from typing import Optional, Dict, Any
from pathlib import Path
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
                             QListWidgetItem, QTextEdit, QLabel, QGroupBox,
                             QSplitter, QPushButton, QComboBox, QSpinBox,
                             QCheckBox, QScrollArea, QFormLayout, QDialog, QLineEdit)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from core.template_engine import TemplateEngine
from utils.config_manager import ConfigManager
from utils.logger import Logger

class TemplatePreviewWidget(QWidget):
    """テンプレートプレビューウィジェット"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """UI設定"""
        layout = QVBoxLayout(self)
        
        # プレビューエリア
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setFont(QFont("Consolas", 10))
        layout.addWidget(self.preview_text)
        
    def set_template_info(self, template_info: Dict[str, Any]):
        """テンプレート情報を設定"""
        if not template_info:
            self.preview_text.clear()
            return
            
        # プレビューテキストを構築
        preview_lines = []
        
        # 基本情報
        preview_lines.append("■ テンプレート情報")
        preview_lines.append(f"名前: {template_info.get('name', '')}")
        preview_lines.append(f"説明: {template_info.get('description', '')}")
        preview_lines.append(f"種別: {template_info.get('type', '')}")
        preview_lines.append("")
        
        # 出力フォーマット
        formats = template_info.get('output_formats', [])
        if formats:
            preview_lines.append("■ 対応出力フォーマット")
            for fmt in formats:
                preview_lines.append(f"  ・{fmt}")
            preview_lines.append("")
        
        # フィールド定義
        fields = template_info.get('fields', [])
        if fields:
            preview_lines.append("■ フィールド定義")
            for field in fields:
                field_name = field.get('name', '')
                field_type = field.get('type', '')
                field_desc = field.get('description', '')
                required = "必須" if field.get('required', False) else "任意"
                
                preview_lines.append(f"【{field_name}】 ({field_type}, {required})")
                if field_desc:
                    preview_lines.append(f"  {field_desc}")
                preview_lines.append("")
        
        # セクション定義
        sections = template_info.get('sections', [])
        if sections:
            preview_lines.append("■ セクション構成")
            for section in sections:
                section_name = section.get('name', '')
                section_desc = section.get('description', '')
                
                preview_lines.append(f"【{section_name}】")
                if section_desc:
                    preview_lines.append(f"  {section_desc}")
                preview_lines.append("")
        
        self.preview_text.setPlainText("\n".join(preview_lines))

class TemplateConfigWidget(QWidget):
    """テンプレート設定ウィジェット"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_template = None
        self.setup_ui()
        
    def setup_ui(self):
        """UI設定"""
        layout = QVBoxLayout(self)
        
        # スクロールエリア
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        
        # 設定ウィジェット
        self.config_widget = QWidget()
        self.config_layout = QFormLayout(self.config_widget)
        scroll_area.setWidget(self.config_widget)
        
        # 設定項目を追加
        self.add_config_items()
        
    def add_config_items(self):
        """設定項目を追加"""
        # 出力フォーマット選択
        self.format_combo = QComboBox()
        self.format_combo.addItems(["txt", "csv", "xlsx", "docx"])
        self.config_layout.addRow("出力フォーマット:", self.format_combo)
        
        # 要約レベル
        self.summary_level_spin = QSpinBox()
        self.summary_level_spin.setRange(1, 5)
        self.summary_level_spin.setValue(3)
        self.config_layout.addRow("要約レベル:", self.summary_level_spin)
        
        # 最大文字数
        self.max_chars_spin = QSpinBox()
        self.max_chars_spin.setRange(100, 10000)
        self.max_chars_spin.setValue(2000)
        self.config_layout.addRow("最大文字数:", self.max_chars_spin)
        
        # キーワード抽出
        self.extract_keywords_check = QCheckBox("キーワード抽出を実行")
        self.extract_keywords_check.setChecked(True)
        self.config_layout.addRow("", self.extract_keywords_check)
        
        # 統計情報含む
        self.include_stats_check = QCheckBox("統計情報を含める")
        self.include_stats_check.setChecked(True)
        self.config_layout.addRow("", self.include_stats_check)
        
        # LLM使用
        self.use_llm_check = QCheckBox("LLMを使用した要約")
        self.use_llm_check.setChecked(False)
        self.config_layout.addRow("", self.use_llm_check)
        
    def set_template(self, template_info: Dict[str, Any]):
        """テンプレート情報を設定"""
        self.current_template = template_info
        
        # 対応フォーマットに基づいてコンボボックスを更新
        self.format_combo.clear()
        if template_info and 'output_formats' in template_info:
            formats = template_info['output_formats']
            self.format_combo.addItems(formats)
        else:
            self.format_combo.addItems(["txt", "csv", "xlsx", "docx"])
            
    def get_config(self) -> Dict[str, Any]:
        """設定を取得"""
        return {
            'output_format': self.format_combo.currentText(),
            'summary_level': self.summary_level_spin.value(),
            'max_chars': self.max_chars_spin.value(),
            'extract_keywords': self.extract_keywords_check.isChecked(),
            'include_stats': self.include_stats_check.isChecked(),
            'use_llm': self.use_llm_check.isChecked()
        }

class TemplateSelectorWidget(QWidget):
    """テンプレート選択ウィジェット"""
    
    # シグナル定義
    template_selected = Signal(str, dict)  # template_id, config
    
    def __init__(self, template_engine: TemplateEngine, config_manager: ConfigManager, 
                 logger: Logger, parent=None):
        super().__init__(parent)
        
        self.template_engine = template_engine
        self.config_manager = config_manager
        self.logger = logger
        
        self.templates = {}
        self.current_template_id = None
        
        self.setup_ui()
        self.load_templates()
        
    def setup_ui(self):
        """UI設定"""
        layout = QVBoxLayout(self)
        
        # ヘッダー
        header_label = QLabel("テンプレート選択")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(header_label)
        
        # メインスプリッター
        main_splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(main_splitter)
        
        # 左側: テンプレート一覧
        left_group = QGroupBox("テンプレート一覧")
        left_layout = QVBoxLayout(left_group)
        
        self.template_list = QListWidget()
        self.template_list.currentItemChanged.connect(self.on_template_selected)
        left_layout.addWidget(self.template_list)
        
        main_splitter.addWidget(left_group)
        
        # 右側: プレビューと設定
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # プレビュー
        preview_group = QGroupBox("プレビュー")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_widget = TemplatePreviewWidget()
        preview_layout.addWidget(self.preview_widget)
        
        right_layout.addWidget(preview_group)
        
        # 設定
        config_group = QGroupBox("設定")
        config_layout = QVBoxLayout(config_group)
        
        self.config_widget = TemplateConfigWidget()
        config_layout.addWidget(self.config_widget)
        
        right_layout.addWidget(config_group)
        
        main_splitter.addWidget(right_widget)
        
        # 分割比率設定
        main_splitter.setSizes([300, 500])
        
        # ボタン
        button_layout = QHBoxLayout()
        
        self.select_button = QPushButton("このテンプレートを選択")
        self.select_button.clicked.connect(self.select_template)
        self.select_button.setEnabled(False)
        button_layout.addWidget(self.select_button)
        
        button_layout.addStretch()
        
        self.refresh_button = QPushButton("再読み込み")
        self.refresh_button.clicked.connect(self.load_templates)
        button_layout.addWidget(self.refresh_button)
        
        layout.addLayout(button_layout)
        
    def load_templates(self):
        """テンプレートを読み込み"""
        try:
            template_list = self.template_engine.get_available_templates()
            self.templates = {}
            self.template_list.clear()
            
            for template_info in template_list:
                template_id = template_info.get('id')
                if template_id:
                    self.templates[template_id] = template_info
                    
                    item = QListWidgetItem(f"{template_info.get('name', template_id)}")
                    item.setData(Qt.UserRole, template_id)
                    
                    # 説明を設定
                    description = template_info.get('description', '')
                    if description:
                        item.setToolTip(description)
                    
                    self.template_list.addItem(item)
                
            self.logger.log_operation(f"テンプレート読み込み完了: {len(self.templates)}件")
            
        except Exception as e:
            self.logger.log_error(f"テンプレート読み込みエラー: {e}")
            
    def on_template_selected(self, current_item, previous_item):
        """テンプレート選択時"""
        if current_item is None:
            self.current_template_id = None
            self.preview_widget.set_template_info({})
            self.config_widget.set_template({})
            self.select_button.setEnabled(False)
            return
            
        template_id = current_item.data(Qt.UserRole)
        self.current_template_id = template_id
        
        if template_id in self.templates:
            template_info = self.templates[template_id]
            self.preview_widget.set_template_info(template_info)
            self.config_widget.set_template(template_info)
            self.select_button.setEnabled(True)
            
    def select_template(self):
        """テンプレートを選択"""
        if self.current_template_id is None:
            return
            
        config = self.config_widget.get_config()
        
        # 選択をシグナルで通知
        self.template_selected.emit(self.current_template_id, config)
        
        # ログに記録
        self.logger.log_operation(f"テンプレート選択: {self.current_template_id}")
        
        # 設定を保存
        self.save_selection(self.current_template_id, config)
        
    def save_selection(self, template_id: str, config: Dict[str, Any]):
        """選択内容を保存"""
        try:
            app_config = self.config_manager.get_app_config()
            
            if 'template_selection' not in app_config:
                app_config['template_selection'] = {}
                
            app_config['template_selection']['last_selected'] = template_id
            app_config['template_selection']['config'] = config
            
            self.config_manager.save_app_config(app_config)
            
        except Exception as e:
            self.logger.log_error(f"選択内容保存エラー: {e}")
            
    def load_last_selection(self):
        """最後の選択内容を読み込み"""
        try:
            app_config = self.config_manager.get_app_config()
            selection = app_config.get('template_selection', {})
            
            last_selected = selection.get('last_selected')
            if last_selected:
                # リストから該当項目を選択
                for i in range(self.template_list.count()):
                    item = self.template_list.item(i)
                    if item.data(Qt.UserRole) == last_selected:
                        self.template_list.setCurrentItem(item)
                        break
                        
                # 設定を復元
                config = selection.get('config', {})
                if config:
                    self.restore_config(config)
                    
        except Exception as e:
            self.logger.log_error(f"選択内容読み込みエラー: {e}")
            
    def restore_config(self, config: Dict[str, Any]):
        """設定を復元"""
        try:
            if 'output_format' in config:
                index = self.config_widget.format_combo.findText(config['output_format'])
                if index >= 0:
                    self.config_widget.format_combo.setCurrentIndex(index)
                    
            if 'summary_level' in config:
                self.config_widget.summary_level_spin.setValue(config['summary_level'])
                
            if 'max_chars' in config:
                self.config_widget.max_chars_spin.setValue(config['max_chars'])
                
            if 'extract_keywords' in config:
                self.config_widget.extract_keywords_check.setChecked(config['extract_keywords'])
                
            if 'include_stats' in config:
                self.config_widget.include_stats_check.setChecked(config['include_stats'])
                
            if 'use_llm' in config:
                self.config_widget.use_llm_check.setChecked(config['use_llm'])
                
        except Exception as e:
            self.logger.log_error(f"設定復元エラー: {e}")
            
    def select_template_by_id(self, template_id: str):
        """指定されたテンプレートIDを選択"""
        for i in range(self.template_list.count()):
            item = self.template_list.item(i)
            if item.data(Qt.UserRole) == template_id:
                self.template_list.setCurrentItem(item)
                break
    
    def get_selected_template(self) -> Optional[str]:
        """選択されたテンプレートIDを取得"""
        return self.current_template_id
    
    def get_current_selection(self) -> tuple[Optional[str], Optional[Dict[str, Any]]]:
        """現在の選択内容を取得"""
        if self.current_template_id is None:
            return None, None
            
        config = self.config_widget.get_config()
        return self.current_template_id, config
    
    # キーボードショートカット対応メソッド
    def refresh_templates(self):
        """テンプレートを更新"""
        try:
            # 現在の選択を保存
            current_selection = self.current_template_id
            
            # テンプレートを再読み込み
            self.load_templates()
            
            # 選択を復元
            if current_selection:
                self.select_template_by_id(current_selection)
                
            self.logger.log_operation("テンプレート更新完了")
            
        except Exception as e:
            self.logger.log_error(e, "テンプレート更新")
    
    def open_template_editor(self):
        """テンプレート編集ダイアログを開く"""
        try:
            # テンプレート編集ダイアログ
            dialog = QDialog(self)
            dialog.setWindowTitle("テンプレート編集")
            dialog.setModal(True)
            dialog.resize(800, 600)
            
            layout = QVBoxLayout(dialog)
            
            # 新規テンプレート作成用フィールド
            form_layout = QHBoxLayout()
            form_layout.addWidget(QLabel("テンプレート名:"))
            name_edit = QLineEdit()
            name_edit.setPlaceholderText("新規テンプレート名を入力")
            form_layout.addWidget(name_edit)
            layout.addLayout(form_layout)
            
            # 説明入力
            desc_layout = QHBoxLayout()
            desc_layout.addWidget(QLabel("説明:"))
            desc_edit = QLineEdit()
            desc_edit.setPlaceholderText("テンプレートの説明を入力")
            desc_layout.addWidget(desc_edit)
            layout.addLayout(desc_layout)
            
            # YAML編集エリア
            yaml_edit = QTextEdit()
            yaml_edit.setPlaceholderText("""
# テンプレート定義例
name: "カスタムテンプレート"
description: "カスタム作成のテンプレート"
type: "custom"
output_formats:
  - "txt"
  - "docx"
fields:
  - name: "summary_text"
    type: "text"
    description: "要約テキスト"
    required: true
  - name: "creation_date"
    type: "date"
    description: "作成日"
    required: true
sections:
  - name: "概要"
    fields:
      - "summary_text"
      - "creation_date"
""")
            layout.addWidget(yaml_edit)
            
            # ボタン
            button_layout = QHBoxLayout()
            
            save_button = QPushButton("保存")
            def save_template():
                name = name_edit.text().strip()
                description = desc_edit.text().strip()
                yaml_content = yaml_edit.toPlainText().strip()
                
                if not name:
                    from PySide6.QtWidgets import QMessageBox
                    QMessageBox.warning(dialog, "警告", "テンプレート名を入力してください")
                    return
                    
                if not yaml_content:
                    from PySide6.QtWidgets import QMessageBox
                    QMessageBox.warning(dialog, "警告", "YAML定義を入力してください")
                    return
                
                # カスタムテンプレートを保存
                try:
                    custom_template_path = self.template_engine.get_template_dir() / "custom" / f"{name}.yaml"
                    custom_template_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(custom_template_path, 'w', encoding='utf-8') as f:
                        f.write(yaml_content)
                    
                    self.logger.log_operation(f"カスタムテンプレート保存: {name}")
                    
                    # テンプレートを再読み込み
                    self.refresh_templates()
                    
                    dialog.accept()
                    
                except Exception as e:
                    from PySide6.QtWidgets import QMessageBox
                    QMessageBox.critical(dialog, "エラー", f"テンプレートの保存に失敗しました: {str(e)}")
                    
            save_button.clicked.connect(save_template)
            button_layout.addWidget(save_button)
            
            cancel_button = QPushButton("キャンセル")
            cancel_button.clicked.connect(dialog.reject)
            button_layout.addWidget(cancel_button)
            
            layout.addLayout(button_layout)
            
            # 既存テンプレートの編集
            if self.current_template_id:
                template_info = self.templates.get(self.current_template_id)
                if template_info:
                    name_edit.setText(template_info.get('name', ''))
                    desc_edit.setText(template_info.get('description', ''))
                    
                    # YAML形式でテンプレート情報を表示
                    import yaml
                    yaml_content = yaml.dump(template_info, default_flow_style=False, allow_unicode=True)
                    yaml_edit.setPlainText(yaml_content)
            
            dialog.exec()
            
        except Exception as e:
            self.logger.log_error(e, "テンプレート編集")
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "エラー", f"テンプレート編集中にエラーが発生しました: {str(e)}") 