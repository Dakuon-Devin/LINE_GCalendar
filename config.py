"""
設定管理モジュール
環境変数や設定値を管理します
"""
import os
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# Google Calendar API設定
GOOGLE_CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
GOOGLE_TOKEN_FILE = os.getenv('GOOGLE_TOKEN_FILE', 'token.json')
GOOGLE_CALENDAR_ID = os.getenv('GOOGLE_CALENDAR_ID', 'primary')
GOOGLE_API_SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

# LINE Messaging API設定
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_USER_ID = os.getenv('LINE_USER_ID')  # 通知先のLINEユーザーID

# 通知設定
NOTIFICATION_TIME_DAY_BEFORE = "19:00"  # 1日前の通知時刻
NOTIFICATION_HOURS_BEFORE = 2  # 当日の通知時間（何時間前か）

# タイムゾーン設定
TIMEZONE = os.getenv('TIMEZONE', 'Asia/Tokyo')
