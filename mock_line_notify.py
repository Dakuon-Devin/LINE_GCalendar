"""
LINE通知のモックモジュール
テスト用にLINE Messaging APIの動作をシミュレートします
"""
from typing import Dict, Any, List, Optional
from test_config import TEST_LINE_RESPONSE

class MockLineNotifier:
    """
    LINE通知のモッククラス
    実際のAPIを呼び出さずに通知をシミュレートします
    """
    
    def __init__(self, channel_access_token=None, user_id=None):
        """
        初期化
        
        Args:
            channel_access_token: 未使用（互換性のため）
            user_id: 未使用（互換性のため）
        """
        self.messages = []  # 送信されたメッセージを記録
    
    def send_text_message(self, text: str) -> Dict[str, Any]:
        """
        テキストメッセージの送信をシミュレートします
        
        Args:
            text: 送信するテキスト
        
        Returns:
            モックAPIレスポンス
        """
        print(f"\n===== LINE通知（モック）=====\n{text}\n===========================\n")
        self.messages.append(text)
        return TEST_LINE_RESPONSE
    
    def send_calendar_notification(self, event_title: str, event_datetime: str, 
                                  location: Optional[str] = None, 
                                  description: Optional[str] = None,
                                  is_day_before: bool = False) -> Dict[str, Any]:
        """
        カレンダー予定の通知をシミュレートします
        
        Args:
            event_title: 予定のタイトル
            event_datetime: 予定の日時（フォーマット済み文字列）
            location: 場所（オプション）
            description: 詳細（オプション）
            is_day_before: 1日前の通知かどうか
        
        Returns:
            モックAPIレスポンス
        """
        # 通知タイプに応じたメッセージを作成
        if is_day_before:
            notification_type = "【明日の予定】"
        else:
            notification_type = "【まもなくの予定】"
        
        # 基本メッセージ
        message = f"{notification_type}\n{event_title}\n日時: {event_datetime}"
        
        # 場所があれば追加
        if location:
            message += f"\n場所: {location}"
        
        # 詳細があれば追加（長すぎる場合は省略）
        if description:
            # 詳細が長い場合は省略
            if len(description) > 100:
                description = description[:97] + "..."
            message += f"\n詳細: {description}"
        
        # メッセージ送信
        return self.send_text_message(message)
    
    def send_multiple_events_notification(self, events: List[Dict[str, Any]], 
                                         is_day_before: bool = False) -> Dict[str, Any]:
        """
        複数の予定をまとめて通知します
        
        Args:
            events: 予定のリスト
            is_day_before: 1日前の通知かどうか
        
        Returns:
            モックAPIレスポンス
        """
        if not events:
            return {"status": "no_events"}
        
        # 通知タイプに応じたヘッダーを作成
        if is_day_before:
            header = "【明日の予定】"
        else:
            header = "【まもなくの予定】"
        
        # 各予定の情報を整形
        event_messages = []
        for i, event in enumerate(events, 1):
            title = event.get('summary', '(タイトルなし)')
            
            # 開始時刻を取得
            start = event.get('start', {})
            if 'dateTime' in start:
                from datetime import datetime
                start_time = datetime.fromisoformat(start['dateTime'])
                start_str = start_time.strftime('%H:%M')
            else:
                start_str = '終日'
            
            # 場所を取得
            location = event.get('location', '')
            location_str = f" @ {location}" if location else ""
            
            # 予定の情報を追加
            event_messages.append(f"{i}. {start_str} {title}{location_str}")
        
        # 全体のメッセージを作成
        message = header + "\n\n" + "\n".join(event_messages)
        
        # メッセージ送信
        return self.send_text_message(message)
