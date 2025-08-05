# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog
import threading
import google.generativeai as genai

# --- 設定 ---
# ★★★ 必ずご自身のAPIキーに書き換えてください ★★★
API_KEY = "AIzaSyC3hL8KvItlaMPg1rgqiLyM-Eff1sSRz5k"  # ご自身のAPIキーに書き換えてください
AI_MODEL_NAME = "gemini-1.5-pro-latest"
AI_MODEL_NAME = 'gemini-1.5-flash'

# --- プロンプト定義 (弁護士バージョン) ---
SYSTEM_PROMPTS = {
    "case_analysis": """
#役割
あなたは、多様な訴訟分野で豊富な実務経験を持つシニアパートナー弁護士です。あなたの任務は、提示された事案の概要に基づき、法的な争点を整理し、論理的かつ戦略的な分析を提供することで、担当弁護士の思考をサポートすることです。

#指示
1.  提示された情報（当事者の主張、時系列、証拠の有無など）を慎重に分析してください。
2.  主要な法的争点を2〜4つ特定し、明確に記述してください。
3.  各争点について、以下の項目を整理してください。
    - 【請求側の主張骨子】：原告（申立人）側が主張すべき法的構成と、それを裏付ける事実。
    - 【相手方の反論予測】：被告（相手方）側から予想される反論や抗弁。
    - 【今後の立証方針】：主張を補強し、反論を覆すために収集・提出すべき証拠や行うべき調査。
4.  事案全体の解決に向けた、考えられる戦略（例：訴訟提起、交渉による和解、ADRの利用など）を簡潔に提案してください。
5.  出力の最後に、必ず以下の免責事項を追記してください。
    「*** 注意：この分析はAIによる思考支援情報です。実際の法務戦略や判断は、必ず担当弁護士の責任において、具体的な事実関係に基づき総合的に行ってください。***」
""",
    "evidence_review": """
#役割
あなたは、訴訟実務に精通し、証拠の評価能力に長けた敏腕なアソシエイト弁護士です。あなたの任務は、提示された証拠リストを精査し、その証拠価値を評価し、立証活動を効果的に進めるための助言を提供することです。

#指示
1.  提示された証拠（契約書、念書、電子メール、写真、録音など）をリストアップしてください。
2.  各証拠について、箇条書きで、以下の項目を明確に分けて記述してください。
    - 関連する法的争点: 
    - 証明力: (高・中・低などで評価)
    - 証拠としての強み: 
    - 証拠としての弱み・リスク: 
3.  現在の証拠全体を踏まえ、立証が不十分な点を指摘し、追加で収集すべき証拠（例：陳述書、専門家の意見書、公的記録など）を具体的に提案してください。
4.  出力の最後に、必ず以下の免責事項を追記してください。
    「*** 注意：この評価はAIによる参考情報です。証拠の最終的な採否や評価は、裁判所の自由心証に委ねられます。***」
""",
    "legal_research": """
#役割
あなたは、最新の判例理論と法改正に精通したリーガルリサーチャーです。あなたの任務は、弁護士からの法律に関する質問に対し、関連する法令・判例を網羅的に調査し、要点をまとめて報告することです。

#指示
1.  質問の法的な論点を正確に把握し、リサーチの範囲を明確にしてください。
2.  回答は以下の構造で構成してください。
    - 【結論】：質問に対する最も直接的な回答を1〜2文で記述。
    - 【関連法令】：根拠となる法律、施行令、規則などの条文を引用。
    - 【主要判例・学説】：結論を支持するリーディングケースや近時の重要判例、通説的な学説などを紹介（判例は事件番号と裁判年月日を可能な限り付記）。
    - 【実務上の留意点】：結論を適用する上での注意点や、下級審での判断の揺れ、法改正の動向などを補足。
3.  出力の最後に、必ず以下の免責事項を追記してください。
    「*** 注意：この情報は学術的・参考目的で提供されるものです。法改正や新たな判例の出現により内容が古くなる可能性があります。個別の事案への適用は、必ず担当弁護士の判断で行ってください。***」
""",
    "document_drafting": """
#役割
あなたは、極めて優秀で正確なパラリーガル（弁護士補助者）です。あなたの任務は、弁護士からの指示や依頼者からのヒアリングメモに基づき、各種法律文書の構造化された下書き（ドラフト）を生成することです。

#指示
1.  入力されたテキスト（弁護士の指示、メモなど）を解釈し、指定された文書の種類（例：訴状、準備書面、内容証明郵便、契約書）に応じて情報を適切に分類・整理してください。
    - 訴状の場合：「当事者」「請求の趣旨」「請求の原因」など。
    - 準備書面の場合：「相手方の主張への反論」「当方の主張の補充」など。
    - 契約書の場合：各条項（目的、契約期間、対価、解除事由など）。
2.  口述やメモの内容を、法律文書として適切な、簡潔かつ正確な表現に変換してください。
3.  情報が不足している、または弁護士の確認が必要な箇所は `[要確認]` や `[要追記]` と明記してください。
4.  出力はあくまで「下書き」であり、完成された文書ではないことを明確にしてください。
"""
}


# --- GUIアプリケーションのクラス ---
class LibraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("法の天秤 (LIBRA) - Legal Intelligence Assistant")
        self.root.geometry("1600x900")

        # --- ダークモード用カラーパレット ---
        self.colors = {
            "bg_main": "#2E2E2E",          # メイン背景色
            "bg_panel": "#3C3C3C",         # パネル背景色
            "bg_entry": "#4A4A4A",         # テキスト入力エリア背景色
            "text": "#E0E0E0",             # 通常テキスト色
            "accent": "#5E81AC",           # アクセントカラー (実行ボタン)
            "accent_fg": "#FFFFFF",        # アクセントカラーの文字色
            "button_selected": "#6E6E6E",   # 選択中ボタンの背景色
            "cursor": "#FFFFFF"            # テキストカーソル色
        }

        self.root.config(bg=self.colors["bg_main"])
        self.current_mode = "case_analysis"

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
            "事案分析支援": "case_analysis",
            "証拠レビュー": "evidence_review",
            "法令・判例リサーチ": "legal_research",
            "書面作成支援": "document_drafting"
        }
        for text, mode in modes.items():
            button = tk.Button(
                self.button_panel, text=text, font=("Helvetica", 12),
                command=lambda m=mode: self.set_mode(m),
                bg=self.colors["bg_panel"], fg=self.colors["text"],
                activebackground=self.colors["button_selected"], activeforeground=self.colors["text"],
                bd=2, relief=tk.RAISED
            )
            button.pack(fill=tk.X, pady=5, padx=10)
            self.buttons[mode] = button

        # --- 右側コンテンツエリア ---
        self.content_panel = tk.Frame(self.main_frame, bg=self.colors["bg_main"])
        self.content_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 入力エリア
        tk.Label(
            self.content_panel, text="入力情報（事案の概要、質問など）", font=("Helvetica", 14, "bold"),
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
            activebackground="#7899C6", activeforeground=self.colors["accent_fg"],
            command=self.run_ai_thread, bd=2, relief=tk.RAISED
        )
        self.run_button.pack(pady=10)

        # 結果表示エリア
        tk.Label(
            self.content_panel, text="LIBRAからの回答", font=("Helvetica", 14, "bold"),
            bg=self.colors["bg_main"], fg=self.colors["text"]
        ).pack(anchor="w", padx=10)
        self.result_text = scrolledtext.ScrolledText(
            self.content_panel, height=20, font=("Helvetica", 11), wrap=tk.WORD, state=tk.DISABLED,
            bg=self.colors["bg_entry"], fg=self.colors["text"],
            bd=2, relief=tk.SUNKEN
            # ★★★ 修正点：↓の行を削除しました ★★★
            # disabledforeground=self.colors["text_disabled"],
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
        thread = threading.Thread(target=self.call_libra_ai, args=(self.current_mode, user_input))
        thread.start()

    def call_libra_ai(self, mode, user_prompt):
        self.run_button.config(state=tk.DISABLED)
        self.status_var.set("LIBRAが検討中です...")
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, "検討中...\n")
        # ★★★ 修正点：↓の行から 'disabledforeground' を削除しました ★★★
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
        # ★★★ 修正点：↓の行から 'disabledforeground' を削除しました ★★★
        self.result_text.config(state=tk.DISABLED)
        
        self.run_button.config(state=tk.NORMAL)
        self.status_var.set(f"現在のモード: {self.buttons[self.current_mode].cget('text')} | 完了")

# --- メイン実行部 ---
def main():
    try:
        genai.configure(api_key=API_KEY)
    except Exception as e:
        messagebox.showerror("APIキー設定エラー", f"APIキーの設定に失敗しました。\n{e}")
        return

    root = tk.Tk()
    app = LibraApp(root)
    root.mainloop()
    
if __name__ == "__main__":
    if not API_KEY :
        messagebox.showerror("設定エラー", "コード内の API_KEY をご自身のGemini APIキーに書き換えてください。")
    else:
        main()