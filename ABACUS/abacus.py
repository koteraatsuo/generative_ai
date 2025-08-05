# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog
import threading
import google.generativeai as genai

# --- 設定 ---
# ★★★ 必ずご自身のAPIキーに書き換えてください ★★★
API_KEY = "AIzaSyC3hL8KvItlaMPg1rgqiLyM-Eff1sSRz5k"  # ご自身のAPIキーに書き換えてください
# AI_MODEL_NAME = "gemini-1.5-pro-latest"
AI_MODEL_NAME = 'gemini-1.5-flash' # 高速・安価なモデル

# --- プロンプト定義 (会計士・税理士バージョン) ---
SYSTEM_PROMPTS = {
    "tax_consulting": """
# 役割
あなたは、国税庁OBで、現在は事業承継やM&Aなどの資産税・組織再編税務を専門とするベテラン税理士です。あなたの任務は、複雑な取引の概要に基づき、税務上の論点を網羅的に洗い出し、実務的な対応策を提示することです。

# 指示
1.  提示された取引の概要（登場人物、取引スキーム、金額など）を正確に把握してください。
2.  税務上の主要な論点を2〜4つ特定し、明確に記述してください。
3.  各論点について、以下の項目を整理してください。
    - 【関連法令・通達】：根拠となる法律（法人税法、所得税法、相続税法など）の条文や、重要な基本通達を引用してください。
    - 【考えられる申告・節税スキーム】：適用可能な特例や、税負担を軽減するための具体的な方法を提案してください。
    - 【税務リスク】：提案したスキームに伴う否認リスク、税務調査で指摘されやすいポイント、将来的な税務問題の可能性などを具体的に解説してください。
4.  事案全体の解決に向けた、総合的なアドバイスを簡潔に付記してください。
5.  出力の最後に、必ず以下の免責事項を追記してください。
    「*** 注意：この回答はAIによる思考支援情報です。実際の税務判断や申告は、必ず担当税理士・会計士の責任において、個別具体的な事実関係に基づき総合的に行ってください。***」
""",
    "audit_support": """
# 役割
あなたは、不正調査（フォレンジック）に長けた経験豊富な公認会計士です。あなたの任務は、提示された財務データや勘定科目の内訳から、不正や誤謬のリスクを示唆する兆候をいち早く見抜くことです。

# 指示
1.  提示された財務データ（B/S, P/L, 勘定科目内訳書、前期比較など）を分析してください。
2.  異常値や特異な変動（例：売上高が横ばいなのに売上債権だけが急増している）を検知し、リストアップしてください。
3.  各異常点について、箇条書きで、以下の項目を明確に記述してください。
    - 【リスクの指摘】：考えられる粉飾決算のパターン（架空売上、費用隠蔽など）や、業務上横領などの不正行為の可能性を具体的に指摘してください。
    - 【追加で実施すべき監査手続】：リスクを検証するために有効な監査手続を具体的に提案してください。（例：「売上計上基準の再検討」「特定取引先の期後入金テスト」「棚卸資産の実在性確認の強化」など）
4.  全体的な分析に基づき、内部統制上の弱点の可能性についても言及してください。
5.  出力の最後に、必ず以下の免責事項を追記してください。
    「*** 注意：この分析はAIによるリスク識別のための参考情報です。不正の有無を断定するものではありません。監査計画の策定と監査手続の実施は、監査人の専門的判断に依拠します。***」
""",
    "ruling_research": """
# 役割
あなたは、税務専門のリーガルリサーチャーです。あなたの任務は、税理士からの質問に対し、関連する法令、通達、裁決例、判例を網羅的に調査し、要点をまとめて報告することです。

# 指示
1.  質問の税務上の論点を正確に把握し、リサーチの範囲を明確にしてください。
2.  回答は以下の構造で構成してください。
    - 【結論】：質問に対する最も直接的な回答を1〜2文で記述してください。
    - 【関連法令・通達】：根拠となる法律の条文（例：法人税法第XX条）や、法人税法基本通達などを正確に引用してください。
    - 【関連裁決・判例】：結論を支持、または覆す可能性のある、直近の重要裁決やリーディングケースとなる判例を紹介してください（裁決・判決年月日、事件番号を可能な限り付記）。
    - 【実務上のポイント】：結論を実務に適用する上での注意点、税務調査での想定問答、見解が分かれている論点などを補足してください。
3.  出力の最後に、必ず以下の免責事項を追記してください。
    「*** 注意：この情報はリサーチ時点での法令・裁決に基づく参考情報です。法改正や新たな裁決により内容が変更される可能性があります。個別の事案への適用は、必ず担当専門家の判断で行ってください。***」
""",
    "tax_form_drafting": """
# 役割
あなたは、大手税理士法人での実務経験が豊富な、極めて正確かつ効率的なスタッフです。あなたの任務は、決算データやヒアリングメモに基づき、法人税申告書別表等の下書きを生成することです。

# 指示
1.  入力されたテキスト（決算書数値、勘定科目内訳、クライアントからのメモなど）を解釈し、指定された文書（例：法人税申告書 別表四、別表五(一)、各種届出書）の作成に必要な情報を整理してください。
2.  法人税申告書別表四（所得の金額の計算に関する明細書）を作成する場合、会計上の利益を起点とし、加算・減算項目を適切に配置して、所得金額を計算するプロセスを明示してください。
3.  法人税申告書別表五(一)（利益積立金額及び資本金等の額の計算に関する明細書）を作成する場合、期首残高、当期中の増減、期末残高を分かりやすく示してください。
4.  情報が不足している、またはクライアントへの確認が必要な箇所は `[要確認：クライアントに〇〇について確認]` のように明記してください。
5.  出力はあくまで「下書き（ドラフト）」であり、検算や税理士による最終確認が必須であることを明確にしてください。
"""
}


# --- GUIアプリケーションのクラス ---
class AbacusApp:
    def __init__(self, root):
        self.root = root
        self.root.title("算盤 (ABACUS) - Accounting & Tax AI Assistant")
        self.root.geometry("1600x900")

        # --- ダークモード用カラーパレット ---
        self.colors = {
            "bg_main": "#2E2E2E",          # メイン背景色
            "bg_panel": "#3C3C3C",         # パネル背景色
            "bg_entry": "#4A4A4A",         # テキスト入力エリア背景色
            "text": "#E0E0E0",             # 通常テキスト色
            "accent": "#4A90E2",           # アクセントカラー (実行ボタン, 青系)
            "accent_fg": "#FFFFFF",        # アクセントカラーの文字色
            "button_selected": "#6E6E6E",   # 選択中ボタンの背景色
            "cursor": "#FFFFFF"            # テキストカーソル色
        }

        self.root.config(bg=self.colors["bg_main"])
        self.current_mode = "tax_consulting" # 初期モード

        # メインフレーム
        self.main_frame = tk.Frame(root, bg=self.colors["bg_main"])
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # --- 左側ボタンパネル ---
        self.button_panel = tk.Frame(self.main_frame, width=250, bg=self.colors["bg_panel"])
        self.button_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        tk.Label(
            self.button_panel, text="機能選択", font=("Helvetica", 16, "bold"), 
            bg=self.colors["bg_panel"], fg=self.colors["text"]
        ).pack(pady=10)

        self.buttons = {}
        modes = {
            "税務相談アシスト": "tax_consulting",
            "会計監査支援": "audit_support",
            "法令・裁決リサーチ": "ruling_research",
            "申告書作成支援": "tax_form_drafting"
        }
        for text, mode in modes.items():
            button = tk.Button(
                self.button_panel, text=text, font=("Helvetica", 12),
                command=lambda m=mode: self.set_mode(m),
                bg=self.colors["bg_panel"], fg=self.colors["text"],
                activebackground=self.colors["button_selected"], activeforeground=self.colors["text"],
                bd=2, relief=tk.RAISED, wraplength=200, justify=tk.LEFT
            )
            button.pack(fill=tk.X, pady=5, padx=10)
            self.buttons[mode] = button

        # --- 右側コンテンツエリア ---
        self.content_panel = tk.Frame(self.main_frame, bg=self.colors["bg_main"])
        self.content_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 入力エリア
        tk.Label(
            self.content_panel, text="入力情報（取引概要、財務データ、質問など）", font=("Helvetica", 14, "bold"),
            bg=self.colors["bg_main"], fg=self.colors["text"]
        ).pack(anchor="w", padx=10)
        self.input_text = scrolledtext.ScrolledText(
            self.content_panel, height=15, font=("Helvetica", 11), wrap=tk.WORD,
            bg=self.colors["bg_entry"], fg=self.colors["text"],
            insertbackground=self.colors["cursor"], bd=2, relief=tk.SUNKEN
        )
        self.input_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 実行ボタン
        self.run_button = tk.Button(
            self.content_panel, text="実行", font=("Helvetica", 14, "bold"), 
            bg=self.colors["accent"], fg=self.colors["accent_fg"],
            activebackground="#63A5E8", activeforeground=self.colors["accent_fg"],
            command=self.run_ai_thread, bd=2, relief=tk.RAISED
        )
        self.run_button.pack(pady=10)

        # 結果表示エリア
        tk.Label(
            self.content_panel, text="ABACUSからの回答", font=("Helvetica", 14, "bold"),
            bg=self.colors["bg_main"], fg=self.colors["text"]
        ).pack(anchor="w", padx=10)
        self.result_text = scrolledtext.ScrolledText(
            self.content_panel, height=20, font=("Helvetica", 11), wrap=tk.WORD, state=tk.DISABLED,
            bg=self.colors["bg_entry"], fg=self.colors["text"],
            bd=2, relief=tk.SUNKEN
        )
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # ステータスバー
        self.status_var = tk.StringVar()
        self.status_bar = tk.Label(
            root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W,
            bg=self.colors["bg_panel"], fg=self.colors["text"]
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.set_mode(self.current_mode) # 初期モードを設定

    def set_mode(self, mode):
        self.current_mode = mode
        for m, b in self.buttons.items():
            b.config(relief=tk.RAISED, bg=self.colors["bg_panel"])
        self.buttons[mode].config(relief=tk.SUNKEN, bg=self.colors["button_selected"])
        
        self.status_var.set(f"現在のモード: {self.buttons[mode].cget('text')}")

    def run_ai_thread(self):
        user_input = self.input_text.get("1.0", tk.END).strip()
        if not user_input:
            messagebox.showwarning("入力エラー", "情報を入力してください。")
            return
        thread = threading.Thread(target=self.call_abacus_ai, args=(self.current_mode, user_input))
        thread.start()

    def call_abacus_ai(self, mode, user_prompt):
        self.run_button.config(state=tk.DISABLED)
        self.status_var.set("ABACUSが分析中です...")
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, "分析中...\n")
        self.result_text.config(state=tk.DISABLED)
        
        try:
            model = genai.GenerativeModel(AI_MODEL_NAME, system_instruction=SYSTEM_PROMPTS[mode])
            response = model.generate_content(user_prompt)
            result = response.text
        except Exception as e:
            result = f"API呼び出し中にエラーが発生しました:\n{e}"
        
        self.root.after(0, self.update_ui_with_result, result)

    def update_ui_with_result(self, result):
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, result)
        self.result_text.config(state=tk.DISABLED)
        
        self.run_button.config(state=tk.NORMAL)
        self.status_var.set(f"現在のモード: {self.buttons[self.current_mode].cget('text')} | 完了")

# --- メイン実行部 ---
def main():
    try:
        # APIキーがプレースホルダーのままではないかチェック
        if "YOUR_GEMINI_API_KEY_HERE" in API_KEY or not API_KEY:
            messagebox.showerror("APIキー未設定", "コード内の `API_KEY` をご自身のGemini APIキーに書き換えてください。")
            return
        genai.configure(api_key=API_KEY)
    except Exception as e:
        messagebox.showerror("APIキー設定エラー", f"APIキーの設定に失敗しました。\n{e}")
        return

    root = tk.Tk()
    app = AbacusApp(root)
    root.mainloop()
    
if __name__ == "__main__":
    main()