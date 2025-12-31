#!/usr/bin/env python3
"""
Windows Software Update Checker
インストール済みソフトウェアのアップデートを検出するGUIアプリケーション
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import threading
import json
import re
from datetime import datetime
import os
import logging
from pathlib import Path


# ログ設定
class Logger:
    """ログ管理クラス"""
    def __init__(self):
        # ログディレクトリの作成（実行ファイルと同じ場所にlogsフォルダを作成）
        script_dir = Path(__file__).parent.resolve()
        self.log_dir = script_dir / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # ログファイル名（日付ベース）
        self.log_file = self.log_dir / f"update_checker_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        # ロガーの設定
        self.logger = logging.getLogger('UpdateChecker')
        self.logger.setLevel(logging.DEBUG)
        
        # ファイルハンドラー
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # フォーマット
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        
        # 起動ログ
        self.info("=" * 60)
        self.info("Software Update Checker Started")
        self.info(f"Log file: {self.log_file}")
        self.info("=" * 60)
    
    def debug(self, message):
        self.logger.debug(message)
    
    def info(self, message):
        self.logger.info(message)
    
    def warning(self, message):
        self.logger.warning(message)
    
    def error(self, message):
        self.logger.error(message)
    
    def log_software_list(self, software_list):
        """ソフトウェアリストをログに記録"""
        self.info(f"Detected {len(software_list)} installed software")
        self.info("-" * 50)
        for sw in software_list:
            self.debug(f"  {sw.name} | {sw.id} | v{sw.version}")
    
    def log_updates_available(self, software_list):
        """利用可能なアップデートをログに記録"""
        updates = [sw for sw in software_list if sw.has_update]
        self.info(f"Updates available: {len(updates)}")
        self.info("-" * 50)
        for sw in updates:
            self.info(f"  UPDATE: {sw.name}")
            self.info(f"          {sw.version} -> {sw.available_version}")
    
    def log_update_started(self, package_ids, all_updates=False):
        """アップデート開始をログに記録"""
        if all_updates:
            self.info("Starting update: ALL PACKAGES")
        else:
            self.info(f"Starting update: {len(package_ids)} packages")
            for pkg_id in package_ids:
                self.info(f"  - {pkg_id}")
    
    def log_update_result(self, package_id, success, error_msg=None):
        """アップデート結果をログに記録"""
        if success:
            self.info(f"  SUCCESS: {package_id}")
        else:
            self.error(f"  FAILED: {package_id}")
            if error_msg:
                self.error(f"    Error: {error_msg}")
    
    def log_session_summary(self, total_software, updates_available, updates_applied):
        """セッションサマリーをログに記録"""
        self.info("=" * 60)
        self.info("SESSION SUMMARY")
        self.info(f"  Total software detected: {total_software}")
        self.info(f"  Updates available: {updates_available}")
        self.info(f"  Updates applied: {updates_applied}")
        self.info("=" * 60)
    
    def get_log_path(self):
        """ログファイルのパスを返す"""
        return self.log_file
    
    def get_log_dir(self):
        """ログディレクトリのパスを返す"""
        return self.log_dir


class ModernStyle:
    """モダンなUIスタイル定義"""
    # カラーパレット
    BG_DARK = "#1a1b26"
    BG_MEDIUM = "#24283b"
    BG_LIGHT = "#414868"
    ACCENT = "#7aa2f7"
    ACCENT_HOVER = "#89b4fa"
    SUCCESS = "#9ece6a"
    WARNING = "#e0af68"
    ERROR = "#f7768e"
    TEXT = "#c0caf5"
    TEXT_DIM = "#565f89"
    
    # フォント
    FONT_FAMILY = "Segoe UI"
    FONT_SIZE = 10
    FONT_SIZE_LARGE = 12
    FONT_SIZE_TITLE = 16


class SoftwareItem:
    """ソフトウェア情報を保持するクラス"""
    def __init__(self, name, id_str, version, available_version=None, source="winget"):
        self.name = name
        self.id = id_str
        self.version = version
        self.available_version = available_version
        self.source = source
        self.has_update = available_version is not None and available_version != version


class UpdateCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ソフトウェア アップデートチェッカー")
        self.root.geometry("1000x700")
        self.root.minsize(800, 500)
        
        # ロガー初期化
        self.logger = Logger()
        
        # スタイル設定
        self.style = ModernStyle()
        self.root.configure(bg=self.style.BG_DARK)
        
        # データ
        self.all_software = []
        self.filtered_software = []
        self.is_scanning = False
        self.updates_applied = 0
        
        # UI構築
        self._setup_styles()
        self._create_ui()
        
        # 終了時の処理
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # 初期スキャン
        self.root.after(500, self.scan_installed)
    
    def _on_closing(self):
        """アプリ終了時の処理"""
        updates_available = sum(1 for s in self.all_software if s.has_update)
        self.logger.log_session_summary(
            len(self.all_software),
            updates_available,
            self.updates_applied
        )
        self.logger.info("Application closed")
        self.root.destroy()
    
    def _setup_styles(self):
        """ttkスタイルの設定"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Treeview スタイル
        style.configure("Custom.Treeview",
                       background=self.style.BG_MEDIUM,
                       foreground=self.style.TEXT,
                       fieldbackground=self.style.BG_MEDIUM,
                       borderwidth=0,
                       font=(self.style.FONT_FAMILY, self.style.FONT_SIZE))
        
        style.configure("Custom.Treeview.Heading",
                       background=self.style.BG_LIGHT,
                       foreground=self.style.TEXT,
                       borderwidth=0,
                       font=(self.style.FONT_FAMILY, self.style.FONT_SIZE, 'bold'))
        
        style.map("Custom.Treeview",
                 background=[('selected', self.style.ACCENT)],
                 foreground=[('selected', self.style.BG_DARK)])
        
        # スクロールバー
        style.configure("Custom.Vertical.TScrollbar",
                       background=self.style.BG_LIGHT,
                       troughcolor=self.style.BG_MEDIUM,
                       borderwidth=0,
                       arrowsize=0)
    
    def _create_ui(self):
        """UI要素の作成"""
        # ヘッダー
        self._create_header()
        
        # ツールバー
        self._create_toolbar()
        
        # メインコンテンツ
        self._create_main_content()
        
        # ステータスバー
        self._create_statusbar()
    
    def _create_header(self):
        """ヘッダー部分の作成"""
        header_frame = tk.Frame(self.root, bg=self.style.BG_DARK, pady=15)
        header_frame.pack(fill=tk.X, padx=20)
        
        # タイトル
        title_label = tk.Label(header_frame,
                              text="🔄 ソフトウェア アップデートチェッカー",
                              font=(self.style.FONT_FAMILY, self.style.FONT_SIZE_TITLE, 'bold'),
                              fg=self.style.ACCENT,
                              bg=self.style.BG_DARK)
        title_label.pack(side=tk.LEFT)
        
        # サブタイトル
        subtitle_label = tk.Label(header_frame,
                                 text="Windows 11 Pro",
                                 font=(self.style.FONT_FAMILY, self.style.FONT_SIZE),
                                 fg=self.style.TEXT_DIM,
                                 bg=self.style.BG_DARK)
        subtitle_label.pack(side=tk.LEFT, padx=(10, 0))
    
    def _create_toolbar(self):
        """ツールバーの作成"""
        toolbar_frame = tk.Frame(self.root, bg=self.style.BG_DARK, pady=10)
        toolbar_frame.pack(fill=tk.X, padx=20)
        
        # 検索ボックス
        search_frame = tk.Frame(toolbar_frame, bg=self.style.BG_MEDIUM, padx=10, pady=5)
        search_frame.pack(side=tk.LEFT)
        
        search_label = tk.Label(search_frame, text="🔍",
                               bg=self.style.BG_MEDIUM, fg=self.style.TEXT_DIM)
        search_label.pack(side=tk.LEFT)
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self._on_search_change)
        self.search_entry = tk.Entry(search_frame,
                                    textvariable=self.search_var,
                                    font=(self.style.FONT_FAMILY, self.style.FONT_SIZE),
                                    bg=self.style.BG_MEDIUM,
                                    fg=self.style.TEXT,
                                    insertbackground=self.style.TEXT,
                                    relief=tk.FLAT,
                                    width=30)
        self.search_entry.pack(side=tk.LEFT, padx=(5, 0))
        
        # フィルターボタン
        filter_frame = tk.Frame(toolbar_frame, bg=self.style.BG_DARK)
        filter_frame.pack(side=tk.LEFT, padx=(15, 0))
        
        self.filter_var = tk.StringVar(value="all")
        
        filters = [
            ("すべて", "all"),
            ("更新あり", "updates"),
            ("最新", "uptodate")
        ]
        
        for text, value in filters:
            btn = tk.Radiobutton(filter_frame,
                               text=text,
                               variable=self.filter_var,
                               value=value,
                               command=self._apply_filter,
                               font=(self.style.FONT_FAMILY, self.style.FONT_SIZE),
                               bg=self.style.BG_DARK,
                               fg=self.style.TEXT,
                               selectcolor=self.style.BG_MEDIUM,
                               activebackground=self.style.BG_DARK,
                               activeforeground=self.style.ACCENT)
            btn.pack(side=tk.LEFT, padx=5)
        
        # アクションボタン
        btn_frame = tk.Frame(toolbar_frame, bg=self.style.BG_DARK)
        btn_frame.pack(side=tk.RIGHT)
        
        self.scan_btn = self._create_button(btn_frame, "🔄 再スキャン", self.scan_installed)
        self.scan_btn.pack(side=tk.LEFT, padx=5)
        
        self.check_btn = self._create_button(btn_frame, "📡 アップデート確認", self.check_updates)
        self.check_btn.pack(side=tk.LEFT, padx=5)
        
        self.update_btn = self._create_button(btn_frame, "⬆️ 選択を更新", self.update_selected,
                                             bg=self.style.SUCCESS)
        self.update_btn.pack(side=tk.LEFT, padx=5)
        
        self.update_all_btn = self._create_button(btn_frame, "⬆️ すべて更新", self.update_all,
                                                  bg=self.style.WARNING)
        self.update_all_btn.pack(side=tk.LEFT, padx=5)
        
        # ログを開くボタン
        self.log_btn = self._create_button(btn_frame, "📄 ログを開く", self.open_log_folder,
                                          bg=self.style.BG_LIGHT)
        self.log_btn.pack(side=tk.LEFT, padx=5)
    
    def _create_button(self, parent, text, command, bg=None):
        """カスタムボタンの作成"""
        if bg is None:
            bg = self.style.ACCENT
        
        btn = tk.Button(parent,
                       text=text,
                       command=command,
                       font=(self.style.FONT_FAMILY, self.style.FONT_SIZE),
                       bg=bg,
                       fg=self.style.BG_DARK,
                       activebackground=self.style.ACCENT_HOVER,
                       activeforeground=self.style.BG_DARK,
                       relief=tk.FLAT,
                       padx=15,
                       pady=5,
                       cursor="hand2")
        
        original_bg = bg
        
        def on_enter(e):
            btn.config(bg=self.style.ACCENT_HOVER)
        
        def on_leave(e):
            btn.config(bg=original_bg)
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn
    
    def _create_main_content(self):
        """メインコンテンツエリアの作成"""
        main_frame = tk.Frame(self.root, bg=self.style.BG_DARK)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Treeview
        columns = ("name", "id", "version", "available", "status")
        self.tree = ttk.Treeview(main_frame, columns=columns, show="headings",
                                style="Custom.Treeview", selectmode="extended")
        
        # カラム設定
        self.tree.heading("name", text="ソフトウェア名", anchor=tk.W)
        self.tree.heading("id", text="パッケージID", anchor=tk.W)
        self.tree.heading("version", text="現在のバージョン", anchor=tk.W)
        self.tree.heading("available", text="利用可能", anchor=tk.W)
        self.tree.heading("status", text="状態", anchor=tk.CENTER)
        
        self.tree.column("name", width=250, minwidth=150)
        self.tree.column("id", width=250, minwidth=150)
        self.tree.column("version", width=150, minwidth=100)
        self.tree.column("available", width=150, minwidth=100)
        self.tree.column("status", width=100, minwidth=80)
        
        # スクロールバー
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview,
                                 style="Custom.Vertical.TScrollbar")
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # 配置
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 行タグの設定
        self.tree.tag_configure("update", background="#2d4a3e", foreground=self.style.SUCCESS)
        self.tree.tag_configure("uptodate", background=self.style.BG_MEDIUM, foreground=self.style.TEXT)
        self.tree.tag_configure("unknown", background=self.style.BG_MEDIUM, foreground=self.style.TEXT_DIM)
        
        # ダブルクリックで詳細表示
        self.tree.bind("<Double-1>", self._on_double_click)
    
    def _create_statusbar(self):
        """ステータスバーの作成"""
        statusbar_frame = tk.Frame(self.root, bg=self.style.BG_MEDIUM, pady=8)
        statusbar_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = tk.Label(statusbar_frame,
                                    text="準備完了",
                                    font=(self.style.FONT_FAMILY, self.style.FONT_SIZE),
                                    fg=self.style.TEXT,
                                    bg=self.style.BG_MEDIUM)
        self.status_label.pack(side=tk.LEFT, padx=20)
        
        self.count_label = tk.Label(statusbar_frame,
                                   text="",
                                   font=(self.style.FONT_FAMILY, self.style.FONT_SIZE),
                                   fg=self.style.TEXT_DIM,
                                   bg=self.style.BG_MEDIUM)
        self.count_label.pack(side=tk.RIGHT, padx=20)
        
        # プログレスバー（非表示で初期化）
        self.progress = ttk.Progressbar(statusbar_frame, mode='indeterminate', length=200)
    
    def _set_status(self, message, color=None):
        """ステータスメッセージの更新"""
        if color is None:
            color = self.style.TEXT
        self.status_label.config(text=message, fg=color)
        self.logger.info(f"Status: {message}")
    
    def _update_count(self):
        """カウント表示の更新"""
        total = len(self.all_software)
        updates = sum(1 for s in self.all_software if s.has_update)
        self.count_label.config(text=f"合計: {total} 件 | 更新可能: {updates} 件")
    
    def _show_progress(self, show=True):
        """プログレスバーの表示/非表示"""
        if show:
            self.progress.pack(side=tk.LEFT, padx=20)
            self.progress.start(10)
        else:
            self.progress.stop()
            self.progress.pack_forget()
    
    def _on_search_change(self, *args):
        """検索文字列変更時の処理"""
        self._apply_filter()
    
    def _apply_filter(self):
        """フィルターの適用"""
        search_text = self.search_var.get().lower()
        filter_type = self.filter_var.get()
        
        self.filtered_software = []
        for software in self.all_software:
            # 検索フィルター
            if search_text:
                if search_text not in software.name.lower() and search_text not in software.id.lower():
                    continue
            
            # タイプフィルター
            if filter_type == "updates" and not software.has_update:
                continue
            elif filter_type == "uptodate" and software.has_update:
                continue
            
            self.filtered_software.append(software)
        
        self._refresh_tree()
    
    def _refresh_tree(self):
        """Treeviewの更新"""
        # 既存アイテムをクリア
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 新しいアイテムを追加
        for software in self.filtered_software:
            if software.has_update:
                status = "🔄 更新あり"
                tag = "update"
            elif software.available_version is None:
                status = "❓ 不明"
                tag = "unknown"
            else:
                status = "✅ 最新"
                tag = "uptodate"
            
            available = software.available_version or "-"
            
            self.tree.insert("", tk.END, values=(
                software.name,
                software.id,
                software.version,
                available,
                status
            ), tags=(tag,))
    
    def _on_double_click(self, event):
        """ダブルクリック時の処理"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            values = item['values']
            
            detail_window = tk.Toplevel(self.root)
            detail_window.title(f"詳細: {values[0]}")
            detail_window.geometry("400x250")
            detail_window.configure(bg=self.style.BG_DARK)
            
            info_text = f"""
ソフトウェア名: {values[0]}

パッケージID: {values[1]}

現在のバージョン: {values[2]}

利用可能なバージョン: {values[3]}

状態: {values[4]}
"""
            
            label = tk.Label(detail_window,
                           text=info_text,
                           font=(self.style.FONT_FAMILY, self.style.FONT_SIZE_LARGE),
                           fg=self.style.TEXT,
                           bg=self.style.BG_DARK,
                           justify=tk.LEFT)
            label.pack(padx=20, pady=20, anchor=tk.W)
    
    def open_log_folder(self):
        """ログフォルダを開く"""
        log_dir = self.logger.get_log_dir()
        self.logger.info(f"Opening log folder: {log_dir}")
        
        if os.name == 'nt':
            os.startfile(log_dir)
        else:
            subprocess.run(['xdg-open', str(log_dir)])
    
    def scan_installed(self):
        """インストール済みソフトウェアのスキャン"""
        if self.is_scanning:
            return
        
        self.is_scanning = True
        self.logger.info("Starting software scan...")
        self._set_status("インストール済みソフトウェアをスキャン中...", self.style.ACCENT)
        self._show_progress(True)
        self._disable_buttons()
        
        thread = threading.Thread(target=self._scan_installed_thread)
        thread.daemon = True
        thread.start()
    
    def _scan_installed_thread(self):
        """スキャン処理（別スレッド）"""
        try:
            # winget list コマンドを実行
            self.logger.debug("Executing: winget list --disable-interactivity")
            result = subprocess.run(
                ["winget", "list", "--disable-interactivity"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            self.logger.debug(f"winget list returned code: {result.returncode}")
            software_list = self._parse_winget_list(result.stdout)
            
            self.root.after(0, lambda: self._on_scan_complete(software_list))
            
        except FileNotFoundError:
            self.logger.error("winget not found")
            self.root.after(0, lambda: self._on_scan_error(
                "wingetが見つかりません。Windows 10/11の最新版をご利用ください。"))
        except Exception as e:
            self.logger.error(f"Scan error: {str(e)}")
            self.root.after(0, lambda: self._on_scan_error(str(e)))
    
    def _parse_winget_list(self, output):
        """winget list の出力をパース"""
        software_list = []
        lines = output.strip().split('\n')
        
        # ヘッダー行を見つける
        header_index = -1
        for i, line in enumerate(lines):
            if '名前' in line or 'Name' in line:
                header_index = i
                break
        
        if header_index == -1 or header_index + 1 >= len(lines):
            return software_list
        
        # 区切り線をスキップ
        data_start = header_index + 1
        if data_start < len(lines) and lines[data_start].startswith('-'):
            data_start += 1
        
        # ヘッダーから列位置を特定
        header = lines[header_index]
        
        # データ行をパース
        for line in lines[data_start:]:
            if not line.strip() or line.startswith('-'):
                continue
            
            # 簡易パース（固定幅のテーブル形式）
            parts = line.split()
            if len(parts) >= 2:
                # 最後の要素がバージョン番号らしければ
                name_parts = []
                version = ""
                id_str = ""
                
                for i, part in enumerate(parts):
                    if self._looks_like_version(part):
                        version = part
                        # IDは通常バージョンの前にある
                        if i > 0:
                            id_str = parts[i-1]
                            name_parts = parts[:i-1]
                        break
                    name_parts.append(part)
                
                if name_parts:
                    name = ' '.join(name_parts)
                    if not id_str:
                        id_str = name_parts[-1] if name_parts else ""
                    
                    software_list.append(SoftwareItem(
                        name=name,
                        id_str=id_str,
                        version=version
                    ))
        
        return software_list
    
    def _looks_like_version(self, text):
        """バージョン番号らしいかどうかを判定"""
        # バージョン番号のパターン: 数字.数字 または 数字.数字.数字 など
        return bool(re.match(r'^\d+\.[\d.]+', text))
    
    def _on_scan_complete(self, software_list):
        """スキャン完了時の処理"""
        self.all_software = software_list
        self.logger.log_software_list(software_list)
        self._apply_filter()
        self._update_count()
        self._set_status(f"スキャン完了 - {len(software_list)} 件のソフトウェアを検出", 
                        self.style.SUCCESS)
        self._show_progress(False)
        self._enable_buttons()
        self.is_scanning = False
    
    def _on_scan_error(self, error_message):
        """スキャンエラー時の処理"""
        self.logger.error(f"Scan error: {error_message}")
        self._set_status(f"エラー: {error_message}", self.style.ERROR)
        self._show_progress(False)
        self._enable_buttons()
        self.is_scanning = False
        messagebox.showerror("エラー", error_message)
    
    def check_updates(self):
        """アップデートの確認"""
        if self.is_scanning:
            return
        
        self.is_scanning = True
        self.logger.info("Checking for updates...")
        self._set_status("アップデートを確認中...", self.style.ACCENT)
        self._show_progress(True)
        self._disable_buttons()
        
        thread = threading.Thread(target=self._check_updates_thread)
        thread.daemon = True
        thread.start()
    
    def _check_updates_thread(self):
        """アップデート確認処理（別スレッド）"""
        try:
            self.logger.debug("Executing: winget upgrade --disable-interactivity")
            result = subprocess.run(
                ["winget", "upgrade", "--disable-interactivity"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            self.logger.debug(f"winget upgrade returned code: {result.returncode}")
            updates = self._parse_winget_upgrade(result.stdout)
            self.root.after(0, lambda: self._on_updates_checked(updates))
            
        except Exception as e:
            self.logger.error(f"Update check error: {str(e)}")
            self.root.after(0, lambda: self._on_scan_error(str(e)))
    
    def _parse_winget_upgrade(self, output):
        """winget upgrade の出力をパース"""
        updates = {}
        lines = output.strip().split('\n')
        
        # ヘッダー行を見つける
        header_index = -1
        for i, line in enumerate(lines):
            if '名前' in line or 'Name' in line:
                header_index = i
                break
        
        if header_index == -1:
            return updates
        
        data_start = header_index + 1
        if data_start < len(lines) and lines[data_start].startswith('-'):
            data_start += 1
        
        for line in lines[data_start:]:
            if not line.strip() or line.startswith('-'):
                continue
            if 'アップグレード' in line or 'upgrade' in line.lower():
                continue
            
            parts = line.split()
            if len(parts) >= 3:
                # バージョン番号を探す
                versions = []
                id_str = ""
                for i, part in enumerate(parts):
                    if self._looks_like_version(part):
                        versions.append((i, part))
                
                # 2つのバージョン番号があれば、現在と利用可能なバージョン
                if len(versions) >= 2:
                    id_idx = versions[0][0] - 1
                    if id_idx >= 0:
                        id_str = parts[id_idx]
                        available_version = versions[1][1]
                        updates[id_str] = available_version
        
        return updates
    
    def _on_updates_checked(self, updates):
        """アップデート確認完了時の処理"""
        update_count = 0
        
        for software in self.all_software:
            # IDまたは名前でマッチング
            if software.id in updates:
                software.available_version = updates[software.id]
                software.has_update = True
                update_count += 1
            elif software.name in updates:
                software.available_version = updates[software.name]
                software.has_update = True
                update_count += 1
            else:
                # アップデートリストにない = 最新
                if software.available_version is None:
                    software.available_version = software.version
                    software.has_update = False
        
        self.logger.log_updates_available(self.all_software)
        self._apply_filter()
        self._update_count()
        
        if update_count > 0:
            self._set_status(f"✨ {update_count} 件のアップデートが利用可能です", 
                           self.style.WARNING)
        else:
            self._set_status("✅ すべてのソフトウェアが最新です", self.style.SUCCESS)
        
        self._show_progress(False)
        self._enable_buttons()
        self.is_scanning = False
    
    def update_selected(self):
        """選択したソフトウェアを更新"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("情報", "更新するソフトウェアを選択してください。")
            return
        
        items_to_update = []
        for item in selection:
            values = self.tree.item(item)['values']
            if "更新あり" in str(values[4]):
                items_to_update.append(values[1])  # パッケージID
        
        if not items_to_update:
            messagebox.showinfo("情報", "選択したソフトウェアに更新はありません。")
            return
        
        if messagebox.askyesno("確認", 
                              f"{len(items_to_update)} 件のソフトウェアを更新しますか？\n\n" + 
                              "\n".join(items_to_update[:5]) +
                              ("..." if len(items_to_update) > 5 else "")):
            self._run_updates(items_to_update)
    
    def update_all(self):
        """すべてのアップデートを適用"""
        items_to_update = [s.id for s in self.all_software if s.has_update]
        
        if not items_to_update:
            messagebox.showinfo("情報", "更新可能なソフトウェアはありません。")
            return
        
        if messagebox.askyesno("確認",
                              f"{len(items_to_update)} 件すべてのソフトウェアを更新しますか？"):
            self._run_updates(items_to_update, all_updates=True)
    
    def _run_updates(self, package_ids, all_updates=False):
        """アップデートの実行"""
        self.logger.log_update_started(package_ids, all_updates)
        self._set_status("アップデートを実行中...", self.style.ACCENT)
        self._show_progress(True)
        self._disable_buttons()
        
        def update_thread():
            success_count = 0
            try:
                if all_updates:
                    # すべて更新
                    self.logger.info("Executing: winget upgrade --all")
                    result = subprocess.run(
                        ["winget", "upgrade", "--all", "--silent", "--accept-package-agreements", 
                         "--accept-source-agreements"],
                        capture_output=True,
                        text=True,
                        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                    )
                    if result.returncode == 0:
                        success_count = len(package_ids)
                        self.logger.info("All updates completed successfully")
                    else:
                        self.logger.warning(f"Some updates may have failed: {result.stderr}")
                else:
                    # 個別に更新
                    for pkg_id in package_ids:
                        self.logger.info(f"Updating: {pkg_id}")
                        result = subprocess.run(
                            ["winget", "upgrade", pkg_id, "--silent", 
                             "--accept-package-agreements", "--accept-source-agreements"],
                            capture_output=True,
                            text=True,
                            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                        )
                        if result.returncode == 0:
                            self.logger.log_update_result(pkg_id, True)
                            success_count += 1
                        else:
                            self.logger.log_update_result(pkg_id, False, result.stderr)
                
                self.updates_applied += success_count
                self.root.after(0, lambda: self._on_update_complete(success_count, len(package_ids)))
                
            except Exception as e:
                self.logger.error(f"Update error: {str(e)}")
                self.root.after(0, lambda: self._on_update_error(str(e)))
        
        thread = threading.Thread(target=update_thread)
        thread.daemon = True
        thread.start()
    
    def _on_update_complete(self, success_count, total_count):
        """アップデート完了時の処理"""
        self._show_progress(False)
        self._enable_buttons()
        
        if success_count == total_count:
            self.logger.info(f"All {total_count} updates completed successfully")
            self._set_status("✅ アップデートが完了しました", self.style.SUCCESS)
            messagebox.showinfo("完了", f"アップデートが完了しました。\n成功: {success_count}/{total_count}")
        else:
            self.logger.warning(f"Updates completed with some failures: {success_count}/{total_count}")
            self._set_status(f"⚠️ 一部のアップデートが失敗しました ({success_count}/{total_count})", 
                           self.style.WARNING)
            messagebox.showwarning("完了", 
                                  f"一部のアップデートが失敗しました。\n成功: {success_count}/{total_count}\n\n詳細はログを確認してください。")
        
        self.scan_installed()
    
    def _on_update_error(self, error_message):
        """アップデートエラー時の処理"""
        self.logger.error(f"Update error: {error_message}")
        self._show_progress(False)
        self._enable_buttons()
        self._set_status(f"エラー: {error_message}", self.style.ERROR)
        messagebox.showerror("エラー", f"アップデート中にエラーが発生しました:\n{error_message}")
    
    def _disable_buttons(self):
        """ボタンを無効化"""
        self.scan_btn.config(state=tk.DISABLED)
        self.check_btn.config(state=tk.DISABLED)
        self.update_btn.config(state=tk.DISABLED)
        self.update_all_btn.config(state=tk.DISABLED)
    
    def _enable_buttons(self):
        """ボタンを有効化"""
        self.scan_btn.config(state=tk.NORMAL)
        self.check_btn.config(state=tk.NORMAL)
        self.update_btn.config(state=tk.NORMAL)
        self.update_all_btn.config(state=tk.NORMAL)


def main():
    root = tk.Tk()
    
    # DPI対応
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
    
    app = UpdateCheckerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
