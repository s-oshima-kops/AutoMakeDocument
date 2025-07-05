@echo off
echo ========================================
echo ドキュメント自動要約&作成アプリ - ビルド
echo ========================================
echo.

echo PyInstallerがインストールされているか確認中...
python -m pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo PyInstallerがインストールされていません。インストールしています...
    python -m pip install pyinstaller
    if %errorlevel% neq 0 (
        echo エラー: PyInstallerのインストールに失敗しました。
        pause
        exit /b 1
    )
) else (
    echo PyInstallerは既にインストールされています。
)

echo.
echo 実行ファイルをビルドしています...
echo これには数分かかる場合があります...
echo.

pyinstaller --onefile --windowed --add-data "config;config" --add-data "templates;templates" --path src --hidden-import gui.main_window --hidden-import utils.config_manager --hidden-import utils.logger --hidden-import core.data_manager --hidden-import core.summarizer --hidden-import core.template_engine --clean --name "AutoMakeDocument" main.py

if %errorlevel% neq 0 (
    echo.
    echo エラー: ビルドに失敗しました。
    pause
    exit /b 1
)

echo.
echo ========================================
echo ビルドが完了しました！
echo ========================================
echo.
echo 実行ファイル: dist\AutoMakeDocument.exe
echo サイズ: 約93MB
echo.
echo 実行ファイルをテストしますか？ (y/n)
set /p test_choice=

if /i "%test_choice%"=="y" (
    echo.
    echo 実行ファイルを起動しています...
    start dist\AutoMakeDocument.exe
)

echo.
echo ビルドプロセスが完了しました。
echo dist\AutoMakeDocument.exe を他のPCにコピーして使用できます。
echo.
pause 