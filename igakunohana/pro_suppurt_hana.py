import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog
import threading
import google.generativeai as genai

# --- 設定 ---
# ★★★ 必ずご自身のAPIキーに書き換えてください ★★★
API_KEY = "AIzaSyC3hL8KvItlaMPg1rgqiLyM-Eff1sSRz5k"
AI_MODEL_NAME = "gemini-1.5-pro-latest"
AI_MODEL_NAME = 'gemini-1.5-flash'


# --- プロンプト定義 (前回と同じ) ---
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

# --- GUIアプリケーションのクラス ---
class HanaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("医学の華 (HANA) - Medical Intelligence Assistant")
        self.root.geometry("1600x900")

        self.current_mode = "diagnosis_assist" # 初期モード

        # メインフレームの作成
        self.main_frame = tk.Frame(root, bg="#f0f0f0")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # --- 左側のボタンパネル ---
        self.button_panel = tk.Frame(self.main_frame, width=200, bg="#d0d0e0")
        self.button_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        tk.Label(self.button_panel, text="機能選択", font=("Helvetica", 16, "bold"), bg="#d0d0e0").pack(pady=10)

        self.buttons = {}
        modes = {
            "鑑別診断アシスト": "diagnosis_assist",
            "ラボデータ分析": "lab_analysis",
            "医学情報リサーチ": "research_assist",
            "カルテ作成支援": "charting_assist"
        }
        for text, mode in modes.items():
            button = tk.Button(self.button_panel, text=text, font=("Helvetica", 12), command=lambda m=mode: self.set_mode(m))
            button.pack(fill=tk.X, pady=5, padx=10)
            self.buttons[mode] = button

        # --- 右側のコンテンツエリア ---
        self.content_panel = tk.Frame(self.main_frame, bg="#f0f0f0")
        self.content_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 入力エリア
        tk.Label(self.content_panel, text="入力情報（症状）", font=("Helvetica", 14, "bold"), bg="#f0f0f0").pack(anchor="w", padx=10)
        self.input_text = scrolledtext.ScrolledText(self.content_panel, height=15, font=("Helvetica", 11), wrap=tk.WORD)
        self.input_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 実行ボタン
        self.run_button = tk.Button(self.content_panel, text="実行", font=("Helvetica", 14, "bold"), bg="#4a90e2", fg="white", command=self.run_ai_thread)
        self.run_button.pack(pady=10)

        # 結果表示エリア
        tk.Label(self.content_panel, text="華からの回答", font=("Helvetica", 14, "bold"), bg="#f0f0f0").pack(anchor="w", padx=10)
        self.result_text = scrolledtext.ScrolledText(self.content_panel, height=20, font=("Helvetica", 11), wrap=tk.WORD, state=tk.DISABLED)
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # ステータスバー
        self.status_var = tk.StringVar()
        self.status_bar = tk.Label(root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.set_mode(self.current_mode) # 初期モードを設定

    def set_mode(self, mode):
        self.current_mode = mode
        # 選択中のボタンの見た目を変更
        for m, b in self.buttons.items():
            b.config(relief=tk.RAISED, bg="#f0f0f0")
        self.buttons[mode].config(relief=tk.SUNKEN, bg="#a0a0c0")
        
        self.status_var.set(f"現在のモード: {self.buttons[mode].cget('text')}")

    def run_ai_thread(self):
        user_input = self.input_text.get("1.0", tk.END).strip()
        if not user_input:
            messagebox.showwarning("入力エラー", "情報を入力してください。")
            return

        # AI処理は重いので別スレッドで実行し、GUIが固まるのを防ぐ
        thread = threading.Thread(target=self.call_hana_ai, args=(self.current_mode, user_input))
        thread.start()

    def call_hana_ai(self, mode, user_prompt):
        """AIを呼び出し、結果をGUIに表示する"""
        self.run_button.config(state=tk.DISABLED)
        self.status_var.set("華が思考中です...")
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, "思考中...\n")
        self.result_text.config(state=tk.DISABLED)
        
        try:
            model = genai.GenerativeModel(
                AI_MODEL_NAME,
                system_instruction=SYSTEM_PROMPTS[mode]
            )
            response = model.generate_content(user_prompt)
            result = response.text
        except Exception as e:
            result = f"API呼び出し中にエラーが発生しました:\n{e}"
        
        # GUIコンポーネントの更新はメインスレッドで行う必要がある
        self.root.after(0, self.update_ui_with_result, result)

    def update_ui_with_result(self, result):
        """AIの実行結果でUIを更新する"""
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, result)
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
    app = HanaApp(root)
    root.mainloop()

if __name__ == "__main__":
    if not API_KEY or "AIzaSyC" not in API_KEY:
        messagebox.showerror("設定エラー", "コード内の API_KEY をご自身のGemini APIキーに書き換えてください。")
    else:
        main()