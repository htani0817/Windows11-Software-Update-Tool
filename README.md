# 🔄 Windows 11 Software Update Tool

<p align="center">
  <img src="https://img.shields.io/badge/Platform-Windows%2011-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="Windows 11">
  <img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
</p>

<p align="center">
  <b>Windows 11 Pro用のモダンなGUIソフトウェアアップデート管理ツール</b>
</p>

<p align="center">
  インストール済みソフトウェアを検出し、アップデートの有無を確認、ワンクリックで更新できます。
</p>

---

## ✨ 特徴

- 🔍 **自動検出** - wingetを使用してインストール済みソフトウェアを自動スキャン
- 📡 **アップデート確認** - 各ソフトウェアの最新バージョンをチェック
- 🔎 **検索・フィルター** - ソフトウェア名やIDで検索、状態でフィルタリング
- ⬆️ **ワンクリック更新** - 選択したソフトウェアまたは全てを一括更新
- 📄 **ログ機能** - 全操作を自動でログファイルに記録
- 🎨 **モダンUI** - ダークテーマの美しいインターフェース
- 🚀 **軽量** - 標準ライブラリのみ使用、追加インストール不要

## 📸 スクリーンショット

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  🔄 ソフトウェア アップデートチェッカー    Windows 11 Pro                   │
├─────────────────────────────────────────────────────────────────────────────┤
│  🔍 [検索...]   ○すべて ○更新あり ○最新   [再スキャン][確認][更新][ログ]   │
├─────────────────────────────────────────────────────────────────────────────┤
│  ソフトウェア名      │ パッケージID      │ 現在    │ 利用可能 │ 状態     │
│  ─────────────────────────────────────────────────────────────────────────  │
│  Google Chrome       │ Google.Chrome     │ 120.0   │ 121.0    │🔄更新あり│
│  Visual Studio Code  │ Microsoft.VSCode  │ 1.85    │ 1.85     │✅ 最新   │
│  Node.js             │ OpenJS.NodeJS     │ 20.10   │ 20.11    │🔄更新あり│
│  ...                 │ ...               │ ...     │ ...      │ ...      │
├─────────────────────────────────────────────────────────────────────────────┤
│  準備完了                                       合計: 156件 │ 更新: 8件  │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 🚀 インストール

### 方法1: リポジトリをクローン

```bash
git clone https://github.com/htani0817/Windows11-Software-Update-Tool.git
cd Windows11-Software-Update-Tool
```

### 方法2: ZIPダウンロード

[Releases](https://github.com/htani0817/Windows11-Software-Update-Tool/releases) から最新版をダウンロード

## 📖 使い方

### 起動方法

**方法A: バッチファイル（推奨）**
```
run.bat をダブルクリック
```

**方法B: コマンドライン**
```bash
python update_checker.py
```

### 基本操作

| ボタン | 説明 |
|--------|------|
| 🔄 再スキャン | インストール済みソフトウェアを再検出 |
| 📡 アップデート確認 | 各ソフトウェアの最新バージョンをチェック |
| ⬆️ 選択を更新 | リストで選択したソフトウェアを更新 |
| ⬆️ すべて更新 | 更新可能なすべてのソフトウェアを一括更新 |
| 📄 ログを開く | ログフォルダを開く |

### フィルター

- **すべて** - 全ソフトウェアを表示
- **更新あり** - アップデート可能なもののみ
- **最新** - 最新バージョンのもののみ

## 📄 ログ機能

すべての操作は自動的にログファイルに記録されます。

### ログの保存場所

```
[実行フォルダ]/logs/update_checker_YYYYMMDD_HHMMSS.log
```

### ログの内容

- アプリケーションの起動・終了
- 検出されたソフトウェア一覧
- 利用可能なアップデート一覧
- アップデートの実行結果（成功/失敗）
- セッションサマリー（終了時）

### ログ出力例

```
2025-01-01 12:34:56 | INFO     | ============================================================
2025-01-01 12:34:56 | INFO     | Software Update Checker Started
2025-01-01 12:34:56 | INFO     | Log file: C:\tools\logs\update_checker_20250101_123456.log
2025-01-01 12:34:56 | INFO     | ============================================================
2025-01-01 12:34:57 | INFO     | Starting software scan...
2025-01-01 12:34:58 | INFO     | Detected 156 installed software
2025-01-01 12:35:00 | INFO     | Checking for updates...
2025-01-01 12:35:02 | INFO     | Updates available: 8
2025-01-01 12:35:02 | INFO     |   UPDATE: Google Chrome
2025-01-01 12:35:02 | INFO     |           120.0.0.0 -> 121.0.0.0
2025-01-01 12:35:10 | INFO     | Starting update: 1 packages
2025-01-01 12:35:10 | INFO     |   - Google.Chrome
2025-01-01 12:35:30 | INFO     |   SUCCESS: Google.Chrome
2025-01-01 12:36:00 | INFO     | ============================================================
2025-01-01 12:36:00 | INFO     | SESSION SUMMARY
2025-01-01 12:36:00 | INFO     |   Total software detected: 156
2025-01-01 12:36:00 | INFO     |   Updates available: 8
2025-01-01 12:36:00 | INFO     |   Updates applied: 1
2025-01-01 12:36:00 | INFO     | ============================================================
2025-01-01 12:36:00 | INFO     | Application closed
```

## ⚙️ 必要条件

| 項目 | 要件 |
|------|------|
| OS | Windows 10 (1809以降) / Windows 11 |
| Python | 3.8 以上 |
| winget | Windows標準搭載（App Installerに含まれる） |

### wingetの確認

```powershell
winget --version
```

見つからない場合は、Microsoft Storeから「アプリ インストーラー」を更新してください。

## 🔧 トラブルシューティング

<details>
<summary><b>wingetが見つからない</b></summary>

Microsoft Store → 「アプリ インストーラー」を検索 → 更新

または PowerShell で:
```powershell
Add-AppxPackage -RegisterByFamilyName -MainPackage Microsoft.DesktopAppInstaller_8wekyb3d8bbwe
```
</details>

<details>
<summary><b>アップデートが検出されない</b></summary>

wingetのソースを更新:
```powershell
winget source update
```
</details>

<details>
<summary><b>更新時にエラーが出る</b></summary>

管理者権限が必要な場合があります:
- `run.bat` を右クリック → 「管理者として実行」
</details>

<details>
<summary><b>ログファイルが作成されない</b></summary>

実行フォルダへの書き込み権限を確認してください。
管理者として実行するか、書き込み可能なフォルダに移動してください。
</details>

## 📁 ファイル構成

```
Windows11-Software-Update-Tool/
├── update_checker.py   # メインアプリケーション
├── run.bat             # 起動用バッチファイル
├── README.md           # このファイル
├── LICENSE             # MITライセンス
├── .gitignore          # Git除外設定
├── requirements.txt    # 依存パッケージ（標準ライブラリのみ）
└── logs/               # ログ出力フォルダ（自動作成）
    └── update_checker_YYYYMMDD_HHMMSS.log
```

## 🤝 コントリビューション

1. このリポジトリをFork
2. 新しいブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチをPush (`git push origin feature/amazing-feature`)
5. Pull Requestを作成

## 📜 ライセンス

MIT License - 詳細は [LICENSE](LICENSE) を参照

## 🙏 謝辞

- [winget](https://github.com/microsoft/winget-cli) - Microsoft Windows Package Manager
- [tkinter](https://docs.python.org/3/library/tkinter.html) - Python標準GUIライブラリ

---

<p align="center">
  Made with ❤️ for Windows Users
</p>
