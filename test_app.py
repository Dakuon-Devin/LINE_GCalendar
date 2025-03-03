"""
テスト用アプリケーション
モックデータを使用してシステムの動作をテストします
"""
import logging
import datetime
import pytz
from mock_google_calendar import get_mock_events, get_mock_notification_events, format_mock_event
from mock_line_notify import MockLineNotifier
import config

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_day_before_notification():
    """
    1日前の通知をテストします
    """
    logger.info("1日前の通知テストを実行します")
    
    # モックデータを取得
    day_before_events, _ = get_mock_notification_events()
    
    # LINE通知クライアントを初期化
    line_notifier = MockLineNotifier()
    
    if day_before_events:
        # 複数の予定をまとめて通知
        response = line_notifier.send_multiple_events_notification(
            events=day_before_events,
            is_day_before=True
        )
        
        logger.info(f"1日前の通知テスト結果: {response}")
        
        # 個別の予定も通知
        for event in day_before_events:
            summary = event.get('summary', '(タイトルなし)')
            
            # 開始時刻を取得
            start = event.get('start', {})
            if 'dateTime' in start:
                start_time = datetime.datetime.fromisoformat(start['dateTime'])
                start_str = start_time.strftime('%Y年%m月%d日 %H:%M')
            else:
                start_date = datetime.datetime.fromisoformat(start.get('date'))
                start_str = start_date.strftime('%Y年%m月%d日') + ' 終日'
            
            # 場所と詳細を取得
            location = event.get('location', '')
            description = event.get('description', '')
            
            # 個別通知を送信
            response = line_notifier.send_calendar_notification(
                event_title=summary,
                event_datetime=start_str,
                location=location,
                description=description,
                is_day_before=True
            )
            
            logger.info(f"個別予定通知テスト結果: {response}")
    else:
        logger.info("1日前に通知する予定はありませんでした")

def test_hours_before_notification():
    """
    2時間前の通知をテストします
    """
    logger.info("2時間前の通知テストを実行します")
    
    # モックデータを取得
    _, hours_before_events = get_mock_notification_events()
    
    # LINE通知クライアントを初期化
    line_notifier = MockLineNotifier()
    
    if hours_before_events:
        # 複数の予定をまとめて通知
        response = line_notifier.send_multiple_events_notification(
            events=hours_before_events,
            is_day_before=False
        )
        
        logger.info(f"2時間前の通知テスト結果: {response}")
        
        # 個別の予定も通知
        for event in hours_before_events:
            summary = event.get('summary', '(タイトルなし)')
            
            # 開始時刻を取得
            start = event.get('start', {})
            if 'dateTime' in start:
                start_time = datetime.datetime.fromisoformat(start['dateTime'])
                start_str = start_time.strftime('%Y年%m月%d日 %H:%M')
            else:
                start_date = datetime.datetime.fromisoformat(start.get('date'))
                start_str = start_date.strftime('%Y年%m月%d日') + ' 終日'
            
            # 場所と詳細を取得
            location = event.get('location', '')
            description = event.get('description', '')
            
            # 個別通知を送信
            response = line_notifier.send_calendar_notification(
                event_title=summary,
                event_datetime=start_str,
                location=location,
                description=description,
                is_day_before=False
            )
            
            logger.info(f"個別予定通知テスト結果: {response}")
    else:
        logger.info("2時間前に通知する予定はありませんでした")

def test_all_events():
    """
    すべての予定を表示します
    """
    logger.info("すべての予定を表示します")
    
    # モックデータを取得
    events = get_mock_events()
    
    if not events:
        logger.info("予定はありません")
        return
    
    for i, event in enumerate(events, 1):
        formatted_event = format_mock_event(event)
        print(f"\n=== 予定 {i} ===\n{formatted_event}\n===========")

def main():
    """
    テストを実行します
    """
    logger.info("テストアプリケーションを開始します")
    
    # すべての予定を表示
    test_all_events()
    
    # 1日前の通知テスト
    test_day_before_notification()
    
    # 2時間前の通知テスト
    test_hours_before_notification()
    
    logger.info("テストアプリケーションを終了します")

if __name__ == "__main__":
    main()
