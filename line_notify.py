"""
LINE通知モジュール
LINE Messaging APIを使用してメッセージを送信する機能を提供します
"""
import json
import requests
from typing import Dict, Any, List, Optional

import config

class LineNotifier:
    """
    LINE Messaging APIを使用して通知を送信するクラス
    """
    
    def __init__(self, channel_access_token: str = None, user_id: str = None):
        """
        初期化
        
        Args:
            channel_access_token: LINEチャネルアクセストークン
            user_id: 通知先のLINEユーザーID
        """
        self.channel_access_token = channel_access_token or config.LINE_CHANNEL_ACCESS_TOKEN
        self.user_id = user_id or config.LINE_USER_ID
        self.api_url = "https://api.line.me/v2/bot/message/push"
        
        if not self.channel_access_token:
            raise ValueError("LINE_CHANNEL_ACCESS_TOKENが設定されていません")
        
        if not self.user_id:
            raise ValueError("LINE_USER_IDが設定されていません")
    
    def send_text_message(self, text: str) -> Dict[str, Any]:
        """
        テキストメッセージを送信します
        
        Args:
            text: 送信するテキスト
        
        Returns:
            APIレスポンス
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.channel_access_token}"
        }
        
        data = {
            "to": self.user_id,
            "messages": [
                {
                    "type": "text",
                    "text": text
                }
            ]
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                data=json.dumps(data)
            )
            response.raise_for_status()
            return response.json() if response.text else {"status": "success"}
        
        except requests.exceptions.RequestException as e:
            print(f"LINE通知の送信に失敗しました: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"エラーレスポンス: {e.response.text}")
            return {"status": "error", "message": str(e)}
    
    def send_calendar_notification(self, event_title: str, event_datetime: str, 
                                  location: Optional[str] = None, 
                                  description: Optional[str] = None,
                                  is_day_before: bool = False) -> Dict[str, Any]:
        """
        カレンダー予定の通知を送信します
        
        Args:
            event_title: 予定のタイトル
            event_datetime: 予定の日時（フォーマット済み文字列）
            location: 場所（オプション）
            description: 詳細（オプション）
            is_day_before: 1日前の通知かどうか
        
        Returns:
            APIレスポンス
        """
        # 通知タイプに応じたメッセージを作成
        if is_day_before:
            notification_type = "【明日の予定】"
        else:
            notification_type = f"【まもなく（{config.NOTIFICATION_HOURS_BEFORE}時間後）】"
        
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
            APIレスポンス
        """
        if not events:
            return {"status": "no_events"}
        
        # 通知タイプに応じたヘッダーを作成
        if is_day_before:
            header = "【明日の予定】"
        else:
            header = f"【まもなく（{config.NOTIFICATION_HOURS_BEFORE}時間後）の予定】"
        
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


if __name__ == "__main__":
    # テスト用コード
    try:
        notifier = LineNotifier()
        
        # 単一の予定通知のテスト
        response = notifier.send_calendar_notification(
            event_title="テスト予定",
            event_datetime="2023年4月1日 15:00",
            location="会議室A",
            description="これはテスト通知です",
            is_day_before=True
        )
        print(f"単一予定通知のレスポンス: {response}")
        
        # 複数予定通知のテスト
        test_events = [
            {
                'summary': 'ミーティング',
                'start': {'dateTime': '2023-04-01T10:00:00+09:00'},
                'location': '会議室B'
            },
            {
                'summary': 'ランチ',
                'start': {'dateTime': '2023-04-01T12:30:00+09:00'}
            },
            {
                'summary': '資料作成',
                'start': {'dateTime': '2023-04-01T14:00:00+09:00'}
            }
        ]
        
        response = notifier.send_multiple_events_notification(
            events=test_events,
            is_day_before=False
        )
        print(f"複数予定通知のレスポンス: {response}")
        
    except Exception as e:
        print(f"テスト実行中にエラーが発生しました: {e}")
