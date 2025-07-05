# -*- coding: utf-8 -*-
"""
日付処理ユーティリティ
"""

from datetime import datetime, date, timedelta
from typing import List, Tuple, Optional
import calendar

class DateUtils:
    """日付処理ユーティリティクラス"""
    
    # 日本語の曜日名
    WEEKDAY_NAMES_JA = ['月', '火', '水', '木', '金', '土', '日']
    
    # 月名
    MONTH_NAMES_JA = [
        '1月', '2月', '3月', '4月', '5月', '6月',
        '7月', '8月', '9月', '10月', '11月', '12月'
    ]
    
    @staticmethod
    def get_today() -> date:
        """今日の日付を取得"""
        return date.today()
    
    @staticmethod
    def get_now() -> datetime:
        """現在の日時を取得"""
        return datetime.now()
    
    @staticmethod
    def format_date(target_date: date, format_str: str = "%Y-%m-%d") -> str:
        """
        日付をフォーマット
        
        Args:
            target_date: 対象日付
            format_str: フォーマット文字列
            
        Returns:
            str: フォーマットされた日付
        """
        return target_date.strftime(format_str)
    
    @staticmethod
    def parse_date(date_str: str, format_str: str = "%Y-%m-%d") -> Optional[date]:
        """
        文字列から日付を解析
        
        Args:
            date_str: 日付文字列
            format_str: フォーマット文字列
            
        Returns:
            date: 解析された日付（失敗した場合はNone）
        """
        try:
            return datetime.strptime(date_str, format_str).date()
        except ValueError:
            return None
    
    @staticmethod
    def get_weekday_name(target_date: date, japanese: bool = True) -> str:
        """
        曜日名を取得
        
        Args:
            target_date: 対象日付
            japanese: 日本語で取得するかどうか
            
        Returns:
            str: 曜日名
        """
        if japanese:
            return DateUtils.WEEKDAY_NAMES_JA[target_date.weekday()]
        else:
            return target_date.strftime("%A")
    
    @staticmethod
    def get_month_name(target_date: date, japanese: bool = True) -> str:
        """
        月名を取得
        
        Args:
            target_date: 対象日付
            japanese: 日本語で取得するかどうか
            
        Returns:
            str: 月名
        """
        if japanese:
            return DateUtils.MONTH_NAMES_JA[target_date.month - 1]
        else:
            return target_date.strftime("%B")
    
    @staticmethod
    def get_week_range(target_date: date) -> Tuple[date, date]:
        """
        指定日を含む週の範囲を取得（月曜日開始）
        
        Args:
            target_date: 対象日付
            
        Returns:
            Tuple[date, date]: 週の開始日と終了日
        """
        # 月曜日を週の開始とする
        days_since_monday = target_date.weekday()
        week_start = target_date - timedelta(days=days_since_monday)
        week_end = week_start + timedelta(days=6)
        
        return week_start, week_end
    
    @staticmethod
    def get_month_range(target_date: date) -> Tuple[date, date]:
        """
        指定日を含む月の範囲を取得
        
        Args:
            target_date: 対象日付
            
        Returns:
            Tuple[date, date]: 月の開始日と終了日
        """
        # 月の最初の日
        month_start = target_date.replace(day=1)
        
        # 月の最後の日
        last_day = calendar.monthrange(target_date.year, target_date.month)[1]
        month_end = target_date.replace(day=last_day)
        
        return month_start, month_end
    
    @staticmethod
    def get_date_range(start_date: date, end_date: date) -> List[date]:
        """
        指定された範囲の日付リストを取得
        
        Args:
            start_date: 開始日
            end_date: 終了日
            
        Returns:
            List[date]: 日付リスト
        """
        date_list = []
        current_date = start_date
        
        while current_date <= end_date:
            date_list.append(current_date)
            current_date += timedelta(days=1)
        
        return date_list
    
    @staticmethod
    def get_business_days(start_date: date, end_date: date) -> List[date]:
        """
        指定された範囲の営業日（平日）リストを取得
        
        Args:
            start_date: 開始日
            end_date: 終了日
            
        Returns:
            List[date]: 営業日リスト
        """
        all_dates = DateUtils.get_date_range(start_date, end_date)
        # 平日のみを抽出（月曜日=0, 日曜日=6）
        business_days = [d for d in all_dates if d.weekday() < 5]
        
        return business_days
    
    @staticmethod
    def format_date_japanese(target_date: date) -> str:
        """
        日本語形式で日付をフォーマット
        
        Args:
            target_date: 対象日付
            
        Returns:
            str: 日本語形式の日付
        """
        year = target_date.year
        month = target_date.month
        day = target_date.day
        weekday = DateUtils.get_weekday_name(target_date)
        
        return f"{year}年{month}月{day}日（{weekday}）"
    
    @staticmethod
    def get_relative_date_string(target_date: date) -> str:
        """
        相対的な日付文字列を取得
        
        Args:
            target_date: 対象日付
            
        Returns:
            str: 相対的な日付文字列
        """
        today = DateUtils.get_today()
        diff = (target_date - today).days
        
        if diff == 0:
            return "今日"
        elif diff == 1:
            return "明日"
        elif diff == -1:
            return "昨日"
        elif diff > 0:
            return f"{diff}日後"
        else:
            return f"{abs(diff)}日前"
    
    @staticmethod
    def is_weekend(target_date: date) -> bool:
        """
        週末かどうかを判定
        
        Args:
            target_date: 対象日付
            
        Returns:
            bool: 週末の場合True
        """
        return target_date.weekday() >= 5  # 土曜日=5, 日曜日=6
    
    @staticmethod
    def get_previous_business_day(target_date: date) -> date:
        """
        前営業日を取得
        
        Args:
            target_date: 対象日付
            
        Returns:
            date: 前営業日
        """
        previous_day = target_date - timedelta(days=1)
        
        while DateUtils.is_weekend(previous_day):
            previous_day -= timedelta(days=1)
        
        return previous_day
    
    @staticmethod
    def get_next_business_day(target_date: date) -> date:
        """
        次営業日を取得
        
        Args:
            target_date: 対象日付
            
        Returns:
            date: 次営業日
        """
        next_day = target_date + timedelta(days=1)
        
        while DateUtils.is_weekend(next_day):
            next_day += timedelta(days=1)
        
        return next_day 