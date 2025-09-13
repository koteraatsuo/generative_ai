# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
import threading
import google.generativeai as genai
import configparser
import os
import sys

# --- 設定 ---
AI_MODEL_NAME = 'gemini-1.5-flash'

# --- プロンプト定義 (変更なし) ---
SYSTEM_PROMPTS = {
    "diagnosis_assist": """
#役割
あなたは、豊富な臨床経験を持つ総合診療医です。あなたの任務は、提示された患者情報に基づき、論理的かつ網羅的な鑑別診断のリストを作成し、医師の臨床的思考をサポートすることです。
#指示
1.  提示された情報（主訴、現病歴、身体所見、検査データ等）を慎重に分析してください。
2.  鑑別疾患リストを、可能性の高い順、または緊急性の高い順に3〜5つ挙げてください。
3.  各疾患について、以下の項目を明確に記述してください。
    - 【支持する所見】：提示された情報のうち、その疾患を示唆する根拠。
    - 【矛盾する所見】：その疾患らしくない、または否定的な根拠。
    - 【次に行うべき検査/質問】：診断を確定または除外するために必要な追加のアクション。
4.  出力の最後に、必ず以下の免責事項を追記してください。
    「*** 注意：このリストはAIによる思考支援情報です。実際の診断・治療は、必ず担当医師の責任において総合的に判断してください。***」
""",
    "lab_analysis": """
#役割
あなたは、臨床病理学と臨床検査医学の専門家です。あなたの任務は、提示された臨床検査データ（ラボデータ）を解釈し、考えられる病態生理学的な考察を提供することです。
#指示
1.  提示されたデータの中から、基準値を逸脱している可能性のある項目を特定してください。
2.  複数の異常値を関連付け、統合的なアセスメント（考えられる病態や疾患）を記述してください。
3.  診断の精度を高めるために推奨される追加検査項目を提案してください。
4.  出力の最後に、必ず以下の免責事項を追記してください。
    「*** 注意：この分析はAIによる参考情報です。臨床診断は、他の所見と合わせて総合的に判断してください。***」
""",
    "research_assist": """
#役割
あなたは、最新の医学研究と主要な診療ガイドラインに精通したメディカルサイエンス・リエゾンです。あなたの任務は、医師からの質問に対し、エビデンスに基づいた正確かつ簡潔な情報を提供することです。
#指示
1.  質問の意図を正確に理解し、最も関連性の高い情報を抽出してください。
2.  回答は以下の構造で構成してください。
    - 【結論】：質問に対する最も直接的な回答を1〜2文で記述。
    - 【解説】：結論に至る背景、メカニズム、臨床的意義などを詳細に説明。
    - 【主要な根拠 (Evidence)】：回答の裏付けとなる主要な診療ガイドライン、大規模臨床試験、システマティックレビューなどを具体的に引用（例: JCS 2023 Guideline on Pharmacotherapy of Cardiovascular Disease, NEJM 2021, DAPA-CKD trialなど）。
3.  出力の最後に、必ず以下の免責事項を追記してください。
    「*** 注意：この情報は学術的な参考情報です。個々の患者への適用は、必ず担当医師の判断で行ってください。***」
""",
    "charting_assist": """
#役割
あなたは、極めて優秀な医療クラーク（医師事務作業補助者）です。あなたの任務は、医師の口述記録を基に、構造化されたSOAP形式のカルテ下書きを生成することです。
#指示
1.  入力されたテキスト（医師の口述内容）を解釈し、情報をSOAPの各項目に正確に分類してください。
    - S (Subjective): 患者の訴え、主観的な情報。
    - O (Objective): 客観的な所見、バイタルサイン、検査結果。
    - A (Assessment): SとOに基づく評価、考察、診断。
    - P (Plan): 治療、検査、処方、指導などの計画。
2.  口述内容を医療用語に適切に変換し、簡潔かつ明瞭な文章で記述してください。
3.  情報が不足している、または不明瞭な箇所は `[要確認]` と明記してください。
"""
}

# --- APIキー読み込み関数 (変更なし) ---
def load_api_key():
    # ... (変更なし) ...
    try:
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(__file__)
        config_path = os.path.join(base_path, 'apikey.ini')
        if not os.path.exists(config_path):
            return None
        config = configparser.ConfigParser()
        config.read(config_path, 'utf-8')
        api_key = config.get('GEMINI', 'api_key')
        if not api_key or 'YOUR_API_KEY' in api_key:
            return None
        return api_key
    except Exception as e:
        print(f"APIキーの読み込み中にエラーが発生しました: {e}")
        return None


# --- GUIアプリケーションのクラス ---
class HanaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("医学の華 (HANA) - Medical Intelligence Assistant (チャットモード)")
        self.root.geometry("1600x900")

        self.colors = {
            "bg_main": "#1E2B38", "bg_panel": "#2C3E50", "bg_entry": "#283543",
            "text": "#E0E0E0", "accent": "#5E81AC", "accent_fg": "#FFFFFF",
            "button_normal": "#3B4252", "button_selected": "#5E81AC", "button_hover": "#4C566A",
            "user_fg": "#88C0D0", "hana_fg": "#A3BE8C", "error_fg": "#BF616A",
            "cursor": "#FFFFFF", "thinking_fg": "#81909e",
            "clear_button": "#D08770" # クリアボタン用の色を追加
        }

        self.root.config(bg=self.colors["bg_main"])
        self.current_mode = "diagnosis_assist"
        self.chat_session = None

        self.main_frame = tk.Frame(root, bg=self.colors["bg_main"])
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.button_panel = tk.Frame(self.main_frame, width=250, bg=self.colors["bg_panel"])
        self.button_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        
        tk.Label(self.button_panel, text="機能選択", font=("Yu Gothic UI", 16, "bold"), bg=self.colors["bg_panel"], fg=self.colors["text"]).pack(pady=15, padx=10)

        self.buttons = {}
        modes = {
            "鑑別診断アシスト": "diagnosis_assist",
            "ラボデータ分析": "lab_analysis",
            "医学情報リサーチ": "research_assist",
            "カルテ作成支援": "charting_assist"
        }
        for text, mode in modes.items():
            button = tk.Button(self.button_panel, text=text, font=("Yu Gothic UI", 12),
                               command=lambda m=mode: self.set_mode(m),
                               bg=self.colors["button_normal"], fg=self.colors["text"],
                               activebackground=self.colors["button_hover"], activeforeground=self.colors["text"],
                               bd=0, relief=tk.FLAT, anchor="w", padx=20)
            button.pack(fill=tk.X, pady=2, padx=10)
            self.buttons[mode] = button

        # ★★★ 新機能: 会話クリアボタンを追加 ★★★
        tk.Frame(self.button_panel, height=2, bg=self.colors["bg_main"]).pack(fill=tk.X, pady=20, padx=10) # セパレーター
        self.clear_button = tk.Button(self.button_panel, text="会話をクリア", font=("Yu Gothic UI", 12, "bold"),
                                      command=self.clear_chat,
                                      bg=self.colors["clear_button"], fg=self.colors["accent_fg"],
                                      activebackground=self.colors["button_hover"], activeforeground=self.colors["accent_fg"],
                                      bd=0, relief=tk.FLAT, anchor="center")
        self.clear_button.pack(fill=tk.X, pady=5, padx=10)


        self.content_panel = tk.Frame(self.main_frame, bg=self.colors["bg_main"])
        self.content_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        tk.Label(self.content_panel, text="医学の「華」 - Clinical Chat", font=("Yu Gothic UI", 14, "bold"), bg=self.colors["bg_main"], fg=self.colors["text"]).pack(anchor="w", padx=10, pady=(5,0))
        
        self.result_text = scrolledtext.ScrolledText(self.content_panel, font=("Yu Gothic UI", 11), wrap=tk.WORD, state=tk.DISABLED,
                                                    bg=self.colors["bg_entry"], fg=self.colors["text"], bd=0, relief=tk.FLAT, padx=10, pady=10)
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.result_text.tag_config("user", font=("Yu Gothic UI", 11, "bold"), foreground=self.colors["user_fg"])
        self.result_text.tag_config("hana", font=("Yu Gothic UI", 11, "bold"), foreground=self.colors["hana_fg"])
        self.result_text.tag_config("error", font=("Yu Gothic UI", 11, "bold"), foreground=self.colors["error_fg"])
        self.result_text.tag_config("info", font=("Yu Gothic UI", 11, "italic"), foreground=self.colors["text"])
        self.result_text.tag_config("thinking_tag", font=("Yu Gothic UI", 11, "italic"), foreground=self.colors["thinking_fg"])

        self.input_text = scrolledtext.ScrolledText(self.content_panel, height=10, font=("Yu Gothic UI", 11), wrap=tk.WORD,
                                                   bg=self.colors["bg_entry"], fg=self.colors["text"], insertbackground=self.colors["cursor"],
                                                   bd=0, relief=tk.FLAT, padx=10, pady=10)
        self.input_text.pack(fill=tk.X, padx=10, pady=5)

        self.run_button = tk.Button(self.content_panel, text="送信", font=("Yu Gothic UI", 14, "bold"),
                                   bg=self.colors["accent"], fg=self.colors["accent_fg"],
                                   activebackground=self.colors["button_hover"], activeforeground=self.colors["accent_fg"],
                                   command=self.run_ai_thread, bd=0, relief=tk.FLAT)
        self.run_button.pack(fill=tk.X, padx=10, pady=5)

        self.io_button_frame = tk.Frame(self.content_panel, bg=self.colors["bg_main"])
        self.io_button_frame.pack(fill=tk.X, padx=10, pady=(0, 5))

        self.save_button = tk.Button(self.io_button_frame, text="会話を保存", font=("Yu Gothic UI", 11),
                                     bg=self.colors["button_normal"], fg=self.colors["text"],
                                     activebackground=self.colors["button_hover"], activeforeground=self.colors["text"],
                                     command=self.save_chat, bd=0, relief=tk.FLAT)
        self.save_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))

        self.load_button = tk.Button(self.io_button_frame, text="テキスト読込", font=("Yu Gothic UI", 11),
                                     bg=self.colors["button_normal"], fg=self.colors["text"],
                                     activebackground=self.colors["button_hover"], activeforeground=self.colors["text"],
                                     command=self.load_text, bd=0, relief=tk.FLAT)
        self.load_button.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(2, 0))

        self.status_var = tk.StringVar()
        self.status_bar = tk.Label(root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W,
                                   bg=self.colors["bg_panel"], fg=self.colors["text"], font=("Yu Gothic UI", 9))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.initialize_chat()

    def initialize_chat(self):
        """チャット画面を初期状態にする"""
        self.set_mode(self.current_mode, is_initialization=True)

    # ★★★ 新機能: 会話をクリアするメソッド ★★★
    def clear_chat(self):
        """チャット履歴と入力欄をクリアし、セッションをリセットする"""
        if messagebox.askyesno("確認", "現在の会話履歴をすべてクリアしますか？"):
            self.input_text.delete("1.0", tk.END)
            self.chat_session = None
            self.initialize_chat()

    # (save_chat, load_textメソッドは変更なし)
    def save_chat(self):
        # ... (変更なし) ...
        chat_content = self.result_text.get("1.0", tk.END)
        if not chat_content.strip():
            messagebox.showwarning("保存エラー", "保存する内容がありません。")
            return
        filepath = filedialog.asksaveasfilename(
            title="会話履歴を保存",
            defaultextension=".txt",
            filetypes=[("テキストファイル", "*.txt"), ("すべてのファイル", "*.*")]
        )
        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(chat_content)
                self.status_var.set(f"ファイルを保存しました: {os.path.basename(filepath)}")
            except Exception as e:
                messagebox.showerror("保存エラー", f"ファイルの保存中にエラーが発生しました:\n{e}")
                self.status_var.set("ファイルの保存に失敗しました")
                
    def load_text(self):
        # ... (変更なし) ...
        filepath = filedialog.askopenfilename(
            title="テキストファイルを読み込む",
            filetypes=[("テキストファイル", "*.txt"), ("すべてのファイル", "*.*")]
        )
        if filepath:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.input_text.delete("1.0", tk.END)
                self.input_text.insert("1.0", content)
                self.status_var.set(f"ファイルを読み込みました: {os.path.basename(filepath)}")
            except Exception as e:
                messagebox.showerror("読込エラー", f"ファイルの読み込み中にエラーが発生しました:\n{e}")
                self.status_var.set("ファイルの読み込みに失敗しました")


    # ★★★ 変更点: set_modeメソッドを修正 ★★★
    def set_mode(self, mode, is_initialization=False):
        """
        AIのモードを設定する。
        is_initializationがTrueの場合のみ、チャット履歴をクリアする。
        """
        self.current_mode = mode
        self.chat_session = None 
        
        for m, b in self.buttons.items():
            b.config(bg=self.colors["button_normal"])
        self.buttons[mode].config(bg=self.colors["button_selected"])
        
        mode_text = self.buttons[mode].cget('text')
        self.status_var.set(f"モード: {mode_text} | 準備完了")
        
        self.result_text.config(state=tk.NORMAL)
        if is_initialization:
            # アプリ起動時やクリア時にのみ履歴を消去
            self.result_text.delete("1.0", tk.END)
            self.result_text.insert(tk.END, f"華: 『{mode_text}』モードを起動しました。ご用件をどうぞ。\n", ("info",))
        else:
            # モード変更時はメッセージを追記
            self.result_text.insert(tk.END, f"\n--- 『{mode_text}』モードに切り替えました ---\n", ("info",))
            self.result_text.see(tk.END)
        self.result_text.config(state=tk.DISABLED)

    def run_ai_thread(self):
        # ... (変更なし) ...
        user_input = self.input_text.get("1.0", tk.END).strip()
        if not user_input:
            return
        self.result_text.config(state=tk.NORMAL)
        self.result_text.insert(tk.END, f"\nあなた:\n", ("user",))
        self.result_text.insert(tk.END, f"{user_input}\n")
        self.result_text.insert(tk.END, "\n「華」が思考中です...\n", ("thinking_tag",))
        self.result_text.see(tk.END) 
        self.result_text.config(state=tk.DISABLED)
        self.input_text.delete("1.0", tk.END)
        thread = threading.Thread(target=self.call_hana_ai, args=(self.current_mode, user_input))
        thread.start()

    def call_hana_ai(self, mode, user_prompt):
        # ... (変更なし) ...
        mode_text = self.buttons[mode].cget('text')
        self.run_button.config(state=tk.DISABLED)
        self.save_button.config(state=tk.DISABLED)
        self.load_button.config(state=tk.DISABLED)
        self.clear_button.config(state=tk.DISABLED) # クリアボタンも無効化
        self.status_var.set(f"モード: {mode_text} | HANAが思考中...")
        try:
            if self.chat_session is None:
                model = genai.GenerativeModel(
                    AI_MODEL_NAME,
                    system_instruction=SYSTEM_PROMPTS[mode]
                )
                self.chat_session = model.start_chat(history=[])
            response = self.chat_session.send_message(user_prompt)
            result = response.text
        except Exception as e:
            result = f"API呼び出し中にエラーが発生しました:\n{e}"
            self.chat_session = None
        self.root.after(0, self.update_chat_display, result)

    def update_chat_display(self, result):
        # ... (変更なし) ...
        self.result_text.config(state=tk.NORMAL)
        tag_ranges = self.result_text.tag_ranges("thinking_tag")
        if tag_ranges:
            self.result_text.delete(tag_ranges[0], tag_ranges[1])
        if "API呼び出し中にエラーが発生しました" in result:
             self.result_text.insert(tk.END, f"\nシステムエラー:\n", ("error",))
        else:
            self.result_text.insert(tk.END, f"\nHANA:\n", ("hana",))
        self.result_text.insert(tk.END, f"{result}\n")
        self.result_text.see(tk.END)
        self.result_text.config(state=tk.DISABLED)
        mode_text = self.buttons[self.current_mode].cget('text')
        self.run_button.config(state=tk.NORMAL)
        self.save_button.config(state=tk.NORMAL)
        self.load_button.config(state=tk.NORMAL)
        self.clear_button.config(state=tk.NORMAL) # クリアボタンも有効化
        self.status_var.set(f"モード: {mode_text} | 入力待機中")

# --- メイン実行部 (変更なし) ---
def main():
    API_KEY = load_api_key()
    
    if not API_KEY:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "APIキー設定エラー",
            "「apikey.ini」ファイルが見つからないか、内容が正しくありません。\n\n"
            "実行ファイルと同じフォルダに「apikey.ini」を作成し、以下の形式でAPIキーを設定してください。\n\n"
            "[GEMINI]\n"
            "api_key = YOUR_API_KEY_GOES_HERE"
        )
        return

    try:
        genai.configure(api_key=API_KEY)
    except Exception as e:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("API設定エラー", f"APIキーの設定に失敗しました。\n{e}")
        return

    root = tk.Tk()
    app = HanaApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()