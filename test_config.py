"""
テスト用設定モジュール
テスト実行時に使用する設定値を提供します
"""
import os
import datetime
import pytz
from config import TIMEZONE

# テスト用のモックデータ
TEST_EVENTS = [
    {
        'summary': 'テスト予定1',
        'start': {
            'dateTime': (datetime.datetime.now(pytz.timezone(TIMEZONE)) + 
                         datetime.timedelta(days=1)).isoformat()
        },
        'location': 'テスト会議室A',
        'description': 'これはテスト用の予定1です'
    },
    {
        'summary': 'テスト予定2',
        'start': {
            'dateTime': (datetime.datetime.now(pytz.timezone(TIMEZONE)) + 
                         datetime.timedelta(hours=3)).isoformat()
        },
        'description': 'これはテスト用の予定2です'
    },
    {
        'summary': 'テスト終日予定',
        'start': {
            'date': (datetime.datetime.now(pytz.timezone(TIMEZONE)).date() + 
                    datetime.timedelta(days=2)).isoformat()
        },
        'description': 'これはテスト用の終日予定です'
    }
]

# テスト用の通知タイミング
TEST_DAY_BEFORE_TIME = datetime.time(19, 0)  # 1日前の19:00
TEST_HOURS_BEFORE = 2  # 当日の2時間前

# テスト用のLINE設定
TEST_LINE_RESPONSE = {
    "status": "success"
}
