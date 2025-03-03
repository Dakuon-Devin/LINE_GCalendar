"""
Googleカレンダー連携モジュール
Googleカレンダーから予定を取得する機能を提供します
"""
import os
import datetime
import pytz
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import config

def get_credentials():
    """
    Google Calendar APIの認証情報を取得します
    初回実行時はユーザー認証が必要です
    """
    creds = None
    # トークンファイルが存在する場合は読み込む
    if os.path.exists(config.GOOGLE_TOKEN_FILE):
        creds = Credentials.from_authorized_user_info(
            info=eval(open(config.GOOGLE_TOKEN_FILE).read()), 
            scopes=config.GOOGLE_API_SCOPES
        )
    
    # 認証情報が無効または存在しない場合は新規取得
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                config.GOOGLE_CREDENTIALS_FILE, config.GOOGLE_API_SCOPES)
            creds = flow.run_local_server(port=0)
        
        # 認証情報を保存
        with open(config.GOOGLE_TOKEN_FILE, 'w') as token:
            token.write(str(creds.to_json()))
    
    return creds

def get_calendar_service():
    """
    Google Calendar APIのサービスオブジェクトを取得します
    """
    try:
        creds = get_credentials()
        service = build('calendar', 'v3', credentials=creds)
        return service
    except Exception as e:
        print(f"カレンダーサービスの取得に失敗しました: {e}")
        return None

def get_events(days=7):
    """
    指定した日数分の予定を取得します
    
    Args:
        days: 何日分の予定を取得するか（デフォルト: 7日）
    
    Returns:
        取得した予定のリスト
    """
    try:
        service = get_calendar_service()
        if not service:
            return []
        
        # 現在時刻と終了時刻を設定
        timezone = pytz.timezone(config.TIMEZONE)
        now = datetime.datetime.now(timezone)
        end_time = now + datetime.timedelta(days=days)
        
        # APIリクエストパラメータ
        events_result = service.events().list(
            calendarId=config.GOOGLE_CALENDAR_ID,
            timeMin=now.isoformat(),
            timeMax=end_time.isoformat(),
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        return events
    
    except HttpError as error:
        print(f"Google Calendar APIエラー: {error}")
        return []
    except Exception as e:
        print(f"予定の取得中にエラーが発生しました: {e}")
        return []

def get_notification_events():
    """
    通知対象の予定を取得します
    1日前の19:00に通知する予定と当日の2時間前に通知する予定を識別します
    
    Returns:
        day_before_events: 1日前の19:00に通知する予定のリスト
        hours_before_events: 当日の2時間前に通知する予定のリスト
    """
    # 7日分の予定を取得
    all_events = get_events(days=7)
    
    timezone = pytz.timezone(config.TIMEZONE)
    now = datetime.datetime.now(timezone)
    
    # 1日前の19:00に通知する予定
    day_before_events = []
    # 当日の2時間前に通知する予定
    hours_before_events = []
    
    for event in all_events:
        # 予定の開始時刻を取得
        start = event.get('start', {})
        
        # 終日の予定の場合
        if 'date' in start:
            event_date = datetime.datetime.fromisoformat(start['date'])
            event_datetime = timezone.localize(datetime.datetime.combine(
                event_date, datetime.time(0, 0, 0)))
        # 時間指定の予定の場合
        elif 'dateTime' in start:
            event_datetime = datetime.datetime.fromisoformat(start['dateTime'])
        else:
            continue
        
        # 1日前の予定を抽出
        one_day_before = event_datetime - datetime.timedelta(days=1)
        notification_time_day_before = datetime.datetime.strptime(
            config.NOTIFICATION_TIME_DAY_BEFORE, "%H:%M").time()
        
        one_day_before_notification = timezone.localize(datetime.datetime.combine(
            one_day_before.date(), notification_time_day_before))
        
        # 現在時刻から1時間以内に1日前の通知を送るべき予定
        if now <= one_day_before_notification <= now + datetime.timedelta(hours=1):
            day_before_events.append(event)
        
        # 当日の予定で、現在時刻から1時間以内に2時間前の通知を送るべき予定
        hours_before_notification = event_datetime - datetime.timedelta(
            hours=config.NOTIFICATION_HOURS_BEFORE)
        
        if now <= hours_before_notification <= now + datetime.timedelta(hours=1):
            hours_before_events.append(event)
    
    return day_before_events, hours_before_events

def format_event(event):
    """
    予定を通知用にフォーマットします
    
    Args:
        event: Google Calendar APIから取得した予定
    
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

if __name__ == "__main__":
    # テスト用コード
    print("今後の予定:")
    events = get_events(days=7)
    for event in events:
        print(format_event(event))
        print("-" * 30)
    
    print("\n通知対象の予定:")
    day_before, hours_before = get_notification_events()
    
    print("\n1日前に通知する予定:")
    for event in day_before:
        print(format_event(event))
        print("-" * 30)
    
    print("\n2時間前に通知する予定:")
    for event in hours_before:
        print(format_event(event))
        print("-" * 30)
