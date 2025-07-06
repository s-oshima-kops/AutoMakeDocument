# 📄 ドキュメント自動作成アプリ

## 📚 ドキュメント一覧

詳細なドキュメントは`docs`ディレクトリに格納されています：

- **[操作手順書](docs/操作手順書.md)** - 詳細な操作マニュアル
- **[クイックスタートガイド](docs/クイックスタートガイド.md)** - 初心者向けガイド  
- **[要件定義書](docs/要件定義書_ドキュメント自動要約アプリ.md)** - 機能仕様と開発状況
- **[ビルド手順](docs/ビルド手順.md)** - 実行ファイル作成方法

## 概要

このアプリケーションは、日々の業務における作業ログを記録・集積し、それらを週報・月報などのドキュメント形式に整形するための**ローカルアプリケーション**です。オフラインで動作し、Windows環境向けに`.exe`形式で配布することを前提としています。

## 🚀 クイックスタート

### 実行ファイル版（推奨）
1. [Releases](https://github.com/s-oshima-kops/AutoMakeDocument/releases)から最新版の`AutoMakeDocument.zip`をダウンロード
2. ダウンロードした`AutoMakeDocument.zip`を任意のフォルダに展開
3. 展開したフォルダ内の`AutoMakeDocument.exe`をダブルクリック

### Python版
```bash
git clone https://github.com/s-oshima-kops/AutoMakeDocument.git
cd AutoMakeDocument
pip install -r requirements.txt
python main.py
```

## 主な機能

### 📝 作業ログ入力機能
- 日ごとの作業内容をプレーンテキストで貼り付け、保存可能
- 直感的なGUIでの入力操作
- 日付単位でのローカル保存（JSON形式）
- 自動保存機能とショートカットキー対応

### 📋 テンプレート選択機能
- あらかじめ用意されたテンプレートから形式を選択可能
  - 日報／週報／月報／業務報告書／進捗報告書
- YAML形式でのユーザー定義テンプレート対応
- リアルタイムプレビュー機能

### 📤 出力機能
- 複数フォーマットでの出力対応：
  - `.txt`（プレーンテキスト）
  - `.csv`（表形式）
  - `.xlsx`（Excel帳票）
  - `.docx`（Word文書）
- 出力前プレビュー機能
- 出力先ディレクトリのGUI指定

## システム要件

| 項目 | 内容 |
|------|------|
| 対応OS | Windows 10 / 11 |
| 実行形式 | ポータブル版（ZIP展開）|
| ネットワーク | オフライン動作（完全ローカル） |
| 外部依存 | なし（オープンソースライブラリのみ使用） |
| 言語 | 日本語対応 |

## インストール方法

### 実行ファイル版（推奨）

1. **ZIPファイルのダウンロード**
   - [Releases](https://github.com/s-oshima-kops/AutoMakeDocument/releases)から最新版の`AutoMakeDocument.zip`をダウンロード
   
2. **ZIPファイルの展開**
   - ダウンロードした`AutoMakeDocument.zip`を任意のフォルダに展開
   
3. **アプリケーションの起動**
   ```
   AutoMakeDocument.exe をダブルクリック
   ```

### 開発環境でのセットアップ

1. **リポジトリのクローン**
   ```bash
   git clone https://github.com/s-oshima-kops/AutoMakeDocument.git
   cd AutoMakeDocument
   ```

2. **Python環境の準備**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   ```

3. **依存関係のインストール**
   ```bash
   pip install -r requirements.txt
   ```

4. **アプリケーションの起動**
   ```bash
   python main.py
   ```

### 実行ファイルのビルド

```bash
python build.py
```
または
```bash
build.bat
```

ビルド完了後、以下のファイルが生成されます：
- `dist/AutoMakeDocument.exe` - 実行ファイル
- `dist/AutoMakeDocument.zip` - 配布用ZIPファイル
- `dist/AutoMakeDocument/` - ポータブル版フォルダ

## 配布方法

### ポータブル版の特徴
- **設定ファイル・テンプレートが同梱** - 追加ファイルのダウンロード不要
- **フォルダ内で完結** - 展開したフォルダ内にすべてのデータが保存
- **複数PC対応** - フォルダごとコピーして他のPCでも使用可能
- **権限問題なし** - 書き込み権限の心配が不要

### 配布用ZIPファイルの内容
```
AutoMakeDocument/
├── AutoMakeDocument.exe    # 実行ファイル
├── README.md              # 使用方法
├── templates/             # レポートテンプレート
│   ├── daily_report.yaml
│   ├── weekly_report.yaml
│   └── ...
├── config/                # 設定ファイル
│   ├── app_config.yaml
│   └── ...
└── data/                  # データ保存フォルダ（実行時に作成）
    └── logs/
```

## 使用方法

### 1. 作業ログの入力
1. 「📝 ログ入力」タブを開く
2. 日付を選択（前日・今日・翌日ボタンまたはカレンダー）
3. 作業内容をテキストエリアに入力
4. タグを追加（任意）
5. 「💾 保存」ボタンをクリック

### 2. テンプレートの選択
1. 「📋 テンプレート選択」タブを開く
2. 出力したいレポート形式を選択
3. 右側でテンプレートのプレビューを確認
4. 「このテンプレートを選択」ボタンをクリック

### 3. レポートの生成と出力
1. 「📤 出力設定」タブを開く
2. 出力対象期間を設定（開始日・終了日）
3. 「プレビュー」ボタンで生成内容を確認
4. 出力形式を選択（txt/csv/xlsx/docx）
5. 「出力実行」ボタンをクリック

### ショートカットキー

| キー | 機能 |
|------|------|
| Ctrl+C | コピー |
| Ctrl+V | ペースト |
| Ctrl+S | ログ保存 |
| Ctrl+N | 新規ログ作成 |
| F11 | フルスクリーン切り替え |

## 技術仕様

### 使用ライブラリ

| 分類 | ライブラリ | 用途 |
|------|-------------|------|
| GUI | PySide6 | ユーザーインターフェース |
| 出力 | openpyxl, python-docx, csv | 各種ファイル出力処理 |
| 実行ファイル化 | PyInstaller | 単体アプリ作成 |

### アーキテクチャ

```
AutoMakeDocument/
├── src/
│   ├── gui/          # GUI コンポーネント
│   ├── core/         # コア機能（テンプレート処理）
│   ├── utils/        # ユーティリティ関数
│   └── output/       # ファイル出力処理
├── data/
│   └── logs/         # 作業ログ（JSON形式）
├── templates/        # レポートテンプレート（YAML形式）
├── config/          # 設定ファイル
└── assets/          # リソースファイル
```

## 設定ファイル

### アプリケーション設定（config/app_config.yaml）
```yaml
app_name: "ドキュメント自動作成アプリ"
version: "1.0.0"
language: "ja"
window:
  width: 1200
  height: 800
```

### ユーザー設定（config/user_settings.json）
```json
{
  "last_template": "daily_report",
  "output_format": "docx",
  "output_directory": "",
  "auto_save": true
}
```

## テンプレートのカスタマイズ

新しいテンプレートを作成するには、`templates/`ディレクトリに新しいYAMLファイルを追加します：

```yaml
id: custom_report
name: カスタムレポート
description: カスタムレポートテンプレート
sections:
  - name: header
    title: 基本情報
    fields:
      - name: title
        type: text
        required: true
```

## トラブルシューティング

### よくある問題

1. **アプリケーションが起動しない**
   - **実行ファイル版**: ウイルス対策ソフトでブロックされていないか確認
   - **Python版**: Python 3.8以上がインストールされているか確認

2. **ファイル出力ができない**
   - 出力先ディレクトリの書き込み権限を確認
   - ディスクの空き容量を確認
   - 同名ファイルが開かれていないか確認

3. **プレビューが表示されない**
   - 作業ログが保存されているか確認
   - 対象期間にデータが存在するか確認
   - ログの内容が十分な長さか確認

### ログの確認

アプリケーションのログは `data/app.log` に記録されます。問題が発生した場合は、このファイルを確認してください。

## 開発情報

### バージョン履歴

- v1.0.0 (2024-01-01): 初回リリース
  - 基本的な出力機能の実装
  - 5種類のテンプレート対応
  - 完全オフライン動作
  - ショートカットキー対応

### 出力ファイル例

生成されるファイル名の例：
```
日報_2024-01-15_2024-01-15.docx
週報_2024-01-08_2024-01-14.xlsx
月報_2024-01-01_2024-01-31.txt
```

### サポート情報

- 完全オフライン動作
- データはすべてローカルに保存
- インターネット接続不要
- 日本語フォント対応

## サポート

質問や問題がある場合は、以下の方法でお問い合わせください：

- GitHub Issues: プロジェクトページで新しいIssueを作成
- メール: [support@example.com](mailto:support@example.com)

---

**Auto Make Document Team**  
© 2024 All Rights Reserved 