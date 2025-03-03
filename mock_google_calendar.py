"""
Googleカレンダーのモックモジュール
テスト用にGoogleカレンダーAPIの動作をシミュレートします
"""
import datetime
import pytz
from test_config import TEST_EVENTS
import config

def get_mock_events(days=7):
    """
    モックの予定データを返します
    
    Args:
        days: 取得する日数（使用されませんが互換性のために残しています）
    
    Returns:
        テスト用の予定リスト
    """
    return TEST_EVENTS

def get_mock_notification_events():
    """
    通知対象のモック予定を返します
    
    Returns:
        day_before_events: 1日前の19:00に通知する予定のリスト
        hours_before_events: 当日の2時間前に通知する予定のリスト
    """
    # 1日前の予定（テスト予定1）
    day_before_events = [TEST_EVENTS[0]]
    
    # 2時間前の予定（テスト予定2）
    hours_before_events = [TEST_EVENTS[1]]
    
    return day_before_events, hours_before_events

def format_mock_event(event):
    """
    モック予定を通知用にフォーマットします
    
    Args:
        event: モックイベントデータ
    
    Returns:
        フォーマットされた予定の文字列
    """
    summary = event.get('summary', '(タイトルなし)')
    
    # 開始時刻を取得
    start = event.get('start', {})
    if 'dateTime' in start:
        # 時間指定の予定
        start_time = datetime.datetime.fromisoformat(start['dateTime'])
        start_str = start_time.strftime('%Y年%m月%d日 %H:%M')
    else:
        # 終日の予定
        start_date = datetime.datetime.fromisoformat(start.get('date'))
        start_str = start_date.strftime('%Y年%m月%d日') + ' 終日'
    
    # 場所を取得
    location = event.get('location', '')
    location_str = f"\n場所: {location}" if location else ""
    
    # 説明を取得（最初の100文字まで）
    description = event.get('description', '')
    if description:
        description = description[:100] + ('...' if len(description) > 100 else '')
        description_str = f"\n詳細: {description}"
    else:
        description_str = ""
    
    # フォーマットされた文字列を返す
    return f"予定: {summary}\n日時: {start_str}{location_str}{description_str}"
