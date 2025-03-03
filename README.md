# LINE_GCalendar

Googleカレンダーの予定を、1日前の19:00と当日の2時間前にLINE Messaging APIを使って通知するシステムです。LINE Notifyサービス終了に伴う代替ソリューションとして開発されました。

## 機能

- Googleカレンダーから予定を取得
- 予定の1日前の19:00に通知
- 予定の当日の2時間前に通知
- LINE Messaging APIを使用したメッセージ送信

## セットアップ

### 前提条件

- Python 3.12以上
- Google Cloud Platformのプロジェクト（Google Calendar API有効化済み）
- LINE Developersアカウント（Messaging API有効化済み）

### インストール

1. リポジトリをクローン

```bash
git clone https://github.com/Dakuon-Devin/LINE_GCalendar.git
cd LINE_GCalendar
```

2. 仮想環境を作成してアクティベート

```bash
uv venv
source .venv/bin/activate  # Linuxの場合
```

3. 依存パッケージをインストール

```bash
uv pip install -e .
```

### 設定

1. `.env.example`を`.env`にコピーして編集

```bash
cp .env.example .env
```

2. `.env`ファイルに以下の情報を設定

- `GOOGLE_CREDENTIALS_FILE`: Google Cloud Platformから取得した認証情報ファイルのパス
- `GOOGLE_TOKEN_FILE`: Googleの認証トークンを保存するファイルのパス
- `GOOGLE_CALENDAR_ID`: 通知対象のGoogleカレンダーID（デフォルトは`primary`）
- `LINE_CHANNEL_ACCESS_TOKEN`: LINE Messaging APIのチャネルアクセストークン
- `LINE_USER_ID`: 通知を送信するLINEユーザーID
- `TIMEZONE`: タイムゾーン（デフォルトは`Asia/Tokyo`）

3. Google Calendar APIの認証情報を取得

- [Google Cloud Console](https://console.cloud.google.com/)でプロジェクトを作成
- Google Calendar APIを有効化
- OAuth 2.0クライアントIDを作成し、認証情報をダウンロード
- ダウンロードしたJSONファイルを`credentials.json`として保存

4. LINE Messaging APIの設定

- [LINE Developers Console](https://developers.line.biz/console/)でプロバイダーとチャネルを作成
- Messaging APIを有効化
- チャネルアクセストークンを発行
- ユーザーIDを取得

## 使用方法

### 通常実行（スケジューラーモード）

```bash
python main.py
```

### テストモード

```bash
python main.py --test
```

特定の日数分の予定を取得してテストする場合：

```bash
python main.py --test --days 14
```

## 動作の仕組み

1. Googleカレンダーから予定を定期的に取得
2. 予定の日時から通知タイミングを計算
3. 1日前の19:00と当日の2時間前に通知を送信
4. LINE Messaging APIを使用してメッセージを配信

## ファイル構成

- `config.py`: 設定管理
- `google_calendar.py`: Googleカレンダー連携
- `line_notify.py`: LINE通知機能
- `scheduler.py`: 通知スケジューリング
- `main.py`: メインアプリケーション
