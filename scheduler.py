"""
通知スケジューリングモジュール
予定の通知タイミングを管理し、スケジュールに従って通知を送信します
"""
import datetime
import logging
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

import config
from google_calendar import get_notification_events, format_event
from line_notify import LineNotifier

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NotificationScheduler:
    """
    通知スケジューリングを管理するクラス
    """
    
    def __init__(self):
        """
        初期化
        """
        self.scheduler = BackgroundScheduler()
        self.line_notifier = LineNotifier()
        self.timezone = pytz.timezone(config.TIMEZONE)
    
    def start(self):
        """
        スケジューラーを開始します
        """
        # 1日前の19:00に通知するジョブを追加
        self.scheduler.add_job(
            self.send_day_before_notifications,
            CronTrigger(hour=19, minute=0, timezone=self.timezone),
            id='day_before_notifications',
            name='1日前の通知'
        )
        
        # 2時間前の通知をチェックするジョブを追加（10分ごとに実行）
        self.scheduler.add_job(
            self.check_hours_before_notifications,
            IntervalTrigger(minutes=10, timezone=self.timezone),
            id='hours_before_check',
            name='2時間前の通知チェック'
        )
        
        # スケジューラーを開始
        self.scheduler.start()
        logger.info("通知スケジューラーを開始しました")
    
    def stop(self):
        """
        スケジューラーを停止します
        """
        self.scheduler.shutdown()
        logger.info("通知スケジューラーを停止しました")
    
    def send_day_before_notifications(self):
        """
        1日前の19:00に通知を送信します
        """
        logger.info("1日前の通知処理を実行します")
        try:
            # 通知対象の予定を取得
            day_before_events, _ = get_notification_events()
            
            if day_before_events:
                # 複数の予定をまとめて通知
                response = self.line_notifier.send_multiple_events_notification(
                    events=day_before_events,
                    is_day_before=True
                )
                
                logger.info(f"1日前の通知を送信しました: {len(day_before_events)}件の予定")
                logger.debug(f"通知レスポンス: {response}")
            else:
                logger.info("1日前に通知する予定はありませんでした")
        
        except Exception as e:
            logger.error(f"1日前の通知処理中にエラーが発生しました: {e}")
    
    def check_hours_before_notifications(self):
        """
        2時間前の通知をチェックし、該当する予定があれば通知を送信します
        """
        logger.info("2時間前の通知チェックを実行します")
        try:
            # 通知対象の予定を取得
            _, hours_before_events = get_notification_events()
            
            if hours_before_events:
                # 複数の予定をまとめて通知
                response = self.line_notifier.send_multiple_events_notification(
                    events=hours_before_events,
                    is_day_before=False
                )
                
                logger.info(f"2時間前の通知を送信しました: {len(hours_before_events)}件の予定")
                logger.debug(f"通知レスポンス: {response}")
            else:
                logger.info("2時間前に通知する予定はありませんでした")
        
        except Exception as e:
            logger.error(f"2時間前の通知処理中にエラーが発生しました: {e}")

def run_scheduler():
    """
    スケジューラーを実行します
    """
    scheduler = NotificationScheduler()
    try:
        scheduler.start()
        
        # スケジューラーを実行し続ける（Ctrl+Cで終了）
        print("通知スケジューラーを実行中... (Ctrl+Cで終了)")
        print(f"タイムゾーン: {config.TIMEZONE}")
        print(f"1日前の通知時刻: 毎日 {config.NOTIFICATION_TIME_DAY_BEFORE}")
        print(f"当日の通知: 予定開始の{config.NOTIFICATION_HOURS_BEFORE}時間前")
        
        # メインスレッドを維持
        import time
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("スケジューラーを停止します...")
    finally:
        scheduler.stop()
        print("スケジューラーを停止しました")

if __name__ == "__main__":
    run_scheduler()
