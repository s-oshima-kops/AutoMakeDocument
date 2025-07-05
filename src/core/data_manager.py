# -*- coding: utf-8 -*-
"""
データ管理クラス
"""

import json
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

from utils.file_utils import FileUtils
from utils.date_utils import DateUtils

@dataclass
class WorkLog:
    """作業ログデータクラス"""
    date: str
    content: str
    created_at: str
    updated_at: str
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []

class DataManager:
    """データ管理クラス"""
    
    def __init__(self, data_dir: Path):
        """
        初期化
        
        Args:
            data_dir: データディレクトリパス
        """
        self.data_dir = Path(data_dir)
        self.logs_dir = self.data_dir / "logs"
        
        # ディレクトリを作成
        self.logs_dir.mkdir(parents=True, exist_ok=True)
    
    def save_work_log(self, log_date: date, content: str, tags: List[str] = None) -> bool:
        """
        作業ログを保存
        
        Args:
            log_date: ログの日付
            content: 作業内容
            tags: タグリスト
            
        Returns:
            bool: 成功したかどうか
        """
        try:
            date_str = DateUtils.format_date(log_date)
            file_path = self.logs_dir / f"{date_str}.json"
            
            now = datetime.now().isoformat()
            
            # 既存のログがあるかチェック
            if file_path.exists():
                existing_log = self.load_work_log(log_date)
                if existing_log:
                    # 更新
                    work_log = WorkLog(
                        date=date_str,
                        content=content,
                        created_at=existing_log.created_at,
                        updated_at=now,
                        tags=tags or []
                    )
                else:
                    # 新規作成
                    work_log = WorkLog(
                        date=date_str,
                        content=content,
                        created_at=now,
                        updated_at=now,
                        tags=tags or []
                    )
            else:
                # 新規作成
                work_log = WorkLog(
                    date=date_str,
                    content=content,
                    created_at=now,
                    updated_at=now,
                    tags=tags or []
                )
            
            # ファイルに保存
            log_data = asdict(work_log)
            FileUtils.write_text_file(file_path, json.dumps(log_data, ensure_ascii=False, indent=2))
            
            return True
            
        except Exception as e:
            print(f"作業ログ保存エラー: {e}")
            return False
    
    def load_work_log(self, log_date: date) -> Optional[WorkLog]:
        """
        作業ログを読み込み
        
        Args:
            log_date: ログの日付
            
        Returns:
            Optional[WorkLog]: 作業ログ（存在しない場合はNone）
        """
        try:
            date_str = DateUtils.format_date(log_date)
            file_path = self.logs_dir / f"{date_str}.json"
            
            if not file_path.exists():
                return None
            
            content = FileUtils.read_text_file(file_path)
            log_data = json.loads(content)
            
            return WorkLog(**log_data)
            
        except Exception as e:
            print(f"作業ログ読み込みエラー: {e}")
            return None
    
    def get_work_logs_by_date_range(self, start_date: date, end_date: date) -> List[WorkLog]:
        """
        指定された期間の作業ログを取得
        
        Args:
            start_date: 開始日
            end_date: 終了日
            
        Returns:
            List[WorkLog]: 作業ログリスト
        """
        logs = []
        date_range = DateUtils.get_date_range(start_date, end_date)
        
        for target_date in date_range:
            log = self.load_work_log(target_date)
            if log and log.content.strip():
                logs.append(log)
        
        return logs
    
    def get_weekly_logs(self, target_date: date) -> List[WorkLog]:
        """
        指定された日を含む週の作業ログを取得
        
        Args:
            target_date: 対象日付
            
        Returns:
            List[WorkLog]: 週の作業ログリスト
        """
        week_start, week_end = DateUtils.get_week_range(target_date)
        return self.get_work_logs_by_date_range(week_start, week_end)
    
    def get_monthly_logs(self, target_date: date) -> List[WorkLog]:
        """
        指定された日を含む月の作業ログを取得
        
        Args:
            target_date: 対象日付
            
        Returns:
            List[WorkLog]: 月の作業ログリスト
        """
        month_start, month_end = DateUtils.get_month_range(target_date)
        return self.get_work_logs_by_date_range(month_start, month_end)
    
    def get_all_log_dates(self) -> List[date]:
        """
        すべてのログファイルの日付を取得
        
        Returns:
            List[date]: ログファイルの日付リスト
        """
        dates = []
        
        try:
            for file_path in self.logs_dir.glob("*.json"):
                date_str = file_path.stem
                parsed_date = DateUtils.parse_date(date_str)
                if parsed_date:
                    dates.append(parsed_date)
        except Exception as e:
            print(f"ログ日付取得エラー: {e}")
        
        return sorted(dates)
    
    def delete_work_log(self, log_date: date) -> bool:
        """
        作業ログを削除
        
        Args:
            log_date: ログの日付
            
        Returns:
            bool: 成功したかどうか
        """
        try:
            date_str = DateUtils.format_date(log_date)
            file_path = self.logs_dir / f"{date_str}.json"
            
            return FileUtils.delete_file(file_path)
            
        except Exception as e:
            print(f"作業ログ削除エラー: {e}")
            return False
    
    def search_logs(self, keyword: str, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[WorkLog]:
        """
        キーワードで作業ログを検索
        
        Args:
            keyword: 検索キーワード
            start_date: 検索開始日（指定しない場合は全期間）
            end_date: 検索終了日（指定しない場合は全期間）
            
        Returns:
            List[WorkLog]: 検索結果
        """
        if not keyword:
            return []
        
        # 検索範囲を設定
        if start_date and end_date:
            logs = self.get_work_logs_by_date_range(start_date, end_date)
        else:
            # 全期間から検索
            all_dates = self.get_all_log_dates()
            logs = []
            for log_date in all_dates:
                log = self.load_work_log(log_date)
                if log and log.content.strip():
                    logs.append(log)
        
        # キーワードで絞り込み
        keyword_lower = keyword.lower()
        filtered_logs = []
        
        for log in logs:
            # 内容とタグを検索
            if (keyword_lower in log.content.lower() or
                any(keyword_lower in tag.lower() for tag in log.tags)):
                filtered_logs.append(log)
        
        return filtered_logs
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        統計情報を取得
        
        Returns:
            Dict[str, Any]: 統計情報
        """
        all_dates = self.get_all_log_dates()
        
        if not all_dates:
            return {
                "total_logs": 0,
                "first_log_date": None,
                "last_log_date": None,
                "total_characters": 0,
                "average_characters_per_log": 0
            }
        
        total_characters = 0
        
        for log_date in all_dates:
            log = self.load_work_log(log_date)
            if log and log.content:
                total_characters += len(log.content)
        
        return {
            "total_logs": len(all_dates),
            "first_log_date": all_dates[0],
            "last_log_date": all_dates[-1],
            "total_characters": total_characters,
            "average_characters_per_log": total_characters // len(all_dates) if all_dates else 0
        }
    
    def export_logs_to_json(self, start_date: date, end_date: date, output_file: Path) -> bool:
        """
        指定期間のログをJSONファイルにエクスポート
        
        Args:
            start_date: 開始日
            end_date: 終了日
            output_file: 出力ファイルパス
            
        Returns:
            bool: 成功したかどうか
        """
        try:
            logs = self.get_work_logs_by_date_range(start_date, end_date)
            logs_data = [asdict(log) for log in logs]
            
            export_data = {
                "export_date": datetime.now().isoformat(),
                "period": {
                    "start_date": DateUtils.format_date(start_date),
                    "end_date": DateUtils.format_date(end_date)
                },
                "logs": logs_data
            }
            
            FileUtils.write_text_file(output_file, json.dumps(export_data, ensure_ascii=False, indent=2))
            return True
            
        except Exception as e:
            print(f"ログエクスポートエラー: {e}")
            return False 