"""
メインアプリケーション
Googleカレンダー予定通知システムのエントリーポイント
"""
import logging
import argparse
from scheduler import run_scheduler
from google_calendar import get_events, format_event
from line_notify import LineNotifier

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """
    メイン関数
    コマンドライン引数に基づいて処理を実行します
    """
    parser = argparse.ArgumentParser(description='Googleカレンダー予定通知システム')
    parser.add_argument('--test', action='store_true', help='テストモード（予定の取得と通知のテスト）')
    parser.add_argument('--days', type=int, default=7, help='取得する予定の日数（デフォルト: 7日）')
    args = parser.parse_args()
    
    if args.test:
        # テストモード
        logger.info("テストモードで実行します")
        test_notifications(days=args.days)
    else:
        # 通常モード（スケジューラー実行）
        logger.info("通知スケジューラーを開始します")
        run_scheduler()

def test_notifications(days=7):
    """
    通知機能のテストを実行します
    
    Args:
        days: 取得する予定の日数
    """
    try:
        # 予定を取得
        events = get_events(days=days)
        
        if not events:
            logger.info(f"今後{days}日間の予定はありません")
            return
        
        logger.info(f"今後{days}日間の予定: {len(events)}件")
        
        # LINE通知クライアントを初期化
        line_notifier = LineNotifier()
        
        # 最初の予定をテスト通知
        if events:
            event = events[0]
            summary = event.get('summary', '(タイトルなし)')
            
            # 開始時刻を取得
            start = event.get('start', {})
            if 'dateTime' in start:
                from datetime import datetime
                start_time = datetime.fromisoformat(start['dateTime'])
                start_str = start_time.strftime('%Y年%m月%d日 %H:%M')
            else:
                start_date = datetime.fromisoformat(start.get('date'))
                start_str = start_date.strftime('%Y年%m月%d日') + ' 終日'
            
            # 場所と詳細を取得
            location = event.get('location', '')
            description = event.get('description', '')
            
            # テスト通知を送信
            logger.info(f"テスト通知を送信します: {summary}")
            response = line_notifier.send_calendar_notification(
                event_title=summary,
                event_datetime=start_str,
                location=location,
                description=description,
                is_day_before=True
            )
            
            logger.info(f"テスト通知の結果: {response}")
            
            # 複数予定の通知テスト
            if len(events) > 1:
                logger.info("複数予定の通知テストを送信します")
                response = line_notifier.send_multiple_events_notification(
                    events=events[:3],  # 最大3件まで
                    is_day_before=False
                )
                logger.info(f"複数予定通知の結果: {response}")
        
    except Exception as e:
        logger.error(f"テスト実行中にエラーが発生しました: {e}")

if __name__ == "__main__":
    main()
