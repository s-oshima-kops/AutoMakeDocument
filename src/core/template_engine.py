# -*- coding: utf-8 -*-
"""
テンプレートエンジンクラス
"""

import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

from utils.file_utils import FileUtils
from utils.date_utils import DateUtils

@dataclass
class TemplateField:
    """テンプレートフィールドクラス"""
    name: str
    type: str
    required: bool = False
    default: Any = None
    description: str = ""

@dataclass
class TemplateSection:
    """テンプレートセクションクラス"""
    name: str
    title: str
    fields: List[TemplateField]
    order: int = 0
    visible: bool = True

@dataclass
class Template:
    """テンプレートクラス"""
    id: str
    name: str
    description: str
    sections: List[TemplateSection]
    output_format: str
    created_at: str
    updated_at: str

class TemplateEngine:
    """テンプレートエンジンクラス"""
    
    def __init__(self, templates_dir: Path):
        """
        初期化
        
        Args:
            templates_dir: テンプレートディレクトリパス
        """
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # テンプレートキャッシュ
        self.template_cache = {}
        
        # デフォルトテンプレートを作成
        self._create_default_templates()
    
    def _create_default_templates(self):
        """デフォルトテンプレートを作成"""
        default_templates = [
            "daily_report.yaml",
            "weekly_report.yaml", 
            "monthly_report.yaml",
            "business_report.yaml",
            "progress_report.yaml"
        ]
        
        for template_file in default_templates:
            template_path = self.templates_dir / template_file
            if not template_path.exists():
                self._create_template_file(template_file)
    
    def _create_template_file(self, template_file: str):
        """テンプレートファイルを作成"""
        # テンプレートファイルの作成は別途実装
        pass
    
    def load_template(self, template_id: str) -> Optional[Template]:
        """
        テンプレートを読み込み
        
        Args:
            template_id: テンプレートID
            
        Returns:
            Optional[Template]: テンプレート（存在しない場合はNone）
        """
        # キャッシュから確認
        if template_id in self.template_cache:
            return self.template_cache[template_id]
        
        # ファイルから読み込み
        template_file = self.templates_dir / f"{template_id}.yaml"
        if not template_file.exists():
            return None
        
        try:
            template_data = FileUtils.read_text_file(template_file)
            template_config = yaml.safe_load(template_data)
            
            # テンプレートオブジェクトに変換
            template = self._parse_template_config(template_config)
            
            # キャッシュに保存
            self.template_cache[template_id] = template
            
            return template
            
        except Exception as e:
            print(f"テンプレート読み込みエラー ({template_id}): {e}")
            return None
    
    def _parse_template_config(self, config: Dict[str, Any]) -> Template:
        """
        テンプレート設定を解析
        
        Args:
            config: 設定辞書
            
        Returns:
            Template: テンプレートオブジェクト
        """
        # セクションを解析
        sections = []
        for section_config in config.get("sections", []):
            # フィールドを解析
            fields = []
            for field_config in section_config.get("fields", []):
                field = TemplateField(
                    name=field_config["name"],
                    type=field_config.get("type", "text"),
                    required=field_config.get("required", False),
                    default=field_config.get("default"),
                    description=field_config.get("description", "")
                )
                fields.append(field)
            
            section = TemplateSection(
                name=section_config["name"],
                title=section_config.get("title", section_config["name"]),
                fields=fields,
                order=section_config.get("order", 0),
                visible=section_config.get("visible", True)
            )
            sections.append(section)
        
        # セクションを順序でソート
        sections.sort(key=lambda x: x.order)
        
        return Template(
            id=config["id"],
            name=config["name"],
            description=config.get("description", ""),
            sections=sections,
            output_format=config.get("output_format", "text"),
            created_at=config.get("created_at", datetime.now().isoformat()),
            updated_at=config.get("updated_at", datetime.now().isoformat())
        )
    
    def get_available_templates(self) -> List[Dict[str, str]]:
        """
        利用可能なテンプレートのリストを取得
        
        Returns:
            List[Dict[str, str]]: テンプレート情報リスト
        """
        templates = []
        
        for template_file in self.templates_dir.glob("*.yaml"):
            template_id = template_file.stem
            template = self.load_template(template_id)
            
            if template:
                templates.append({
                    "id": template.id,
                    "name": template.name,
                    "description": template.description,
                    "output_format": template.output_format
                })
        
        return templates
    
    def apply_template(self, template_id: str, data: Dict[str, Any], output_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        テンプレートにデータを適用
        
        Args:
            template_id: テンプレートID
            data: 適用するデータ
            output_config: 出力設定（オプション）
            
        Returns:
            Dict[str, Any]: 適用結果
        """
        if output_config is None:
            output_config = {}
        template = self.load_template(template_id)
        if not template:
            return {"error": f"テンプレート '{template_id}' が見つかりません"}
        
        try:
            # テンプレートの各セクションにデータを適用
            result = {
                "template_id": template_id,
                "template_name": template.name,
                "generated_at": datetime.now().isoformat(),
                "sections": []
            }
            
            for section in template.sections:
                if not section.visible:
                    continue
                
                section_data = {
                    "name": section.name,
                    "title": section.title,
                    "content": {}
                }
                
                # フィールドにデータを適用
                for field in section.fields:
                    field_value = self._get_field_value(field, data)
                    section_data["content"][field.name] = field_value
                
                result["sections"].append(section_data)
            
            return result
            
        except Exception as e:
            return {"error": f"テンプレート適用エラー: {str(e)}"}
    
    def _get_field_value(self, field: TemplateField, data: Dict[str, Any]) -> Any:
        """
        フィールドの値を取得
        
        Args:
            field: テンプレートフィールド
            data: データ辞書
            
        Returns:
            Any: フィールドの値
        """
        # フィールドマッピング: テンプレートフィールド名 → 要約データフィールド名
        field_mapping = {
            'weekly_summary': 'summary_text',
            'summary_text': 'summary_text',
            'keywords': 'keywords',
            'generated_at': 'generated_at',
            'creation_date': 'generated_at',
            'report_date': 'generated_at',
            'daily_summary': 'summary_text',
            'monthly_summary': 'summary_text',
            'key_achievements': 'summary_text',
            'completed_tasks': 'summary_text',
            'ongoing_tasks': 'summary_text',
            'project_summary': 'summary_text',
            'activity_summary': 'summary_text',
            'progress_summary': 'summary_text',
            'achievement_summary': 'summary_text'
        }
        
        # マッピングがあれば使用、なければ元のフィールド名を使用
        mapped_field = field_mapping.get(field.name, field.name)
        
        # データから値を取得
        value = data.get(mapped_field, field.default)
        
        # 必須フィールドで値がない場合、デフォルト値を設定
        if field.required and (value is None or value == ""):
            # 特定のフィールドにはデフォルト値を設定
            if field.name in ['week_start_date', 'week_end_date']:
                return "指定なし"
            elif field.name == 'reporter_name':
                return "報告者名未設定"
            elif field.name == 'department':
                return "部署未設定"
            else:
                return f"[必須フィールド '{field.name}' が未入力です]"
        
        # 型に応じた処理
        if field.type == "date":
            if isinstance(value, str):
                parsed_date = DateUtils.parse_date(value)
                if parsed_date:
                    return DateUtils.format_date_japanese(parsed_date)
            return value
        
        elif field.type == "datetime":
            if isinstance(value, str):
                try:
                    dt = datetime.fromisoformat(value)
                    return dt.strftime("%Y年%m月%d日 %H:%M")
                except ValueError:
                    pass
            return value
        
        elif field.type == "list":
            if isinstance(value, list):
                return "\n".join(f"• {item}" for item in value if item)
            return value
        
        elif field.type == "summary":
            # 要約データの特別処理
            if isinstance(value, dict):
                if "summary_text" in value:
                    return value["summary_text"]
                elif "summary" in value:
                    return value["summary"]
            return value
        
        return value
    
    def format_output(self, template_result: Dict[str, Any], output_format: str = "text") -> str:
        """
        テンプレート結果を指定形式で出力
        
        Args:
            template_result: テンプレート適用結果
            output_format: 出力形式（text, markdown, html）
            
        Returns:
            str: フォーマットされた出力
        """
        if output_format == "markdown":
            return self._format_markdown(template_result)
        elif output_format == "html":
            return self._format_html(template_result)
        else:
            return self._format_text(template_result)
    
    def _format_text(self, template_result: Dict[str, Any]) -> str:
        """テキスト形式で出力"""
        lines = []
        
        # ヘッダー
        lines.append(f"# {template_result.get('template_name', 'レポート')}")
        lines.append(f"作成日時: {template_result.get('generated_at', '')}")
        lines.append("")
        
        # セクション
        for section in template_result.get("sections", []):
            lines.append(f"## {section['title']}")
            lines.append("")
            
            for field_name, field_value in section["content"].items():
                if field_value is not None and field_value != "":
                    lines.append(f"{field_name}: {field_value}")
                    lines.append("")
        
        return "\n".join(lines)
    
    def _format_markdown(self, template_result: Dict[str, Any]) -> str:
        """Markdown形式で出力"""
        lines = []
        
        # ヘッダー
        lines.append(f"# {template_result.get('template_name', 'レポート')}")
        lines.append(f"**作成日時**: {template_result.get('generated_at', '')}")
        lines.append("")
        
        # セクション
        for section in template_result.get("sections", []):
            lines.append(f"## {section['title']}")
            lines.append("")
            
            for field_name, field_value in section["content"].items():
                if field_value is not None and field_value != "":
                    lines.append(f"**{field_name}**:")
                    lines.append(f"{field_value}")
                    lines.append("")
        
        return "\n".join(lines)
    
    def _format_html(self, template_result: Dict[str, Any]) -> str:
        """HTML形式で出力"""
        lines = []
        
        lines.append("<html><head><meta charset='utf-8'></head><body>")
        lines.append(f"<h1>{template_result.get('template_name', 'レポート')}</h1>")
        lines.append(f"<p><strong>作成日時</strong>: {template_result.get('generated_at', '')}</p>")
        
        # セクション
        for section in template_result.get("sections", []):
            lines.append(f"<h2>{section['title']}</h2>")
            
            for field_name, field_value in section["content"].items():
                if field_value is not None and field_value != "":
                    lines.append(f"<p><strong>{field_name}</strong>: {field_value}</p>")
        
        lines.append("</body></html>")
        
        return "\n".join(lines)
    
    def save_template(self, template: Template) -> bool:
        """
        テンプレートを保存
        
        Args:
            template: 保存するテンプレート
            
        Returns:
            bool: 成功したかどうか
        """
        try:
            # テンプレートを辞書に変換
            template_dict = {
                "id": template.id,
                "name": template.name,
                "description": template.description,
                "output_format": template.output_format,
                "created_at": template.created_at,
                "updated_at": datetime.now().isoformat(),
                "sections": []
            }
            
            for section in template.sections:
                section_dict = {
                    "name": section.name,
                    "title": section.title,
                    "order": section.order,
                    "visible": section.visible,
                    "fields": []
                }
                
                for field in section.fields:
                    field_dict = {
                        "name": field.name,
                        "type": field.type,
                        "required": field.required,
                        "default": field.default,
                        "description": field.description
                    }
                    section_dict["fields"].append(field_dict)
                
                template_dict["sections"].append(section_dict)
            
            # ファイルに保存
            template_file = self.templates_dir / f"{template.id}.yaml"
            yaml_content = yaml.dump(template_dict, default_flow_style=False,
                                   allow_unicode=True, sort_keys=False)
            FileUtils.write_text_file(template_file, yaml_content)
            
            # キャッシュを更新
            self.template_cache[template.id] = template
            
            return True
            
        except Exception as e:
            print(f"テンプレート保存エラー: {e}")
            return False 