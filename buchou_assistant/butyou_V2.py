# # -*- coding: utf-8 -*-
# import tkinter as tk
# from tkinter import scrolledtext, messagebox, simpledialog
# import threading
# import google.generativeai as genai

# # --- 設定 ---
# # ★★★ 必ずご自身のAPIキーに書き換えてください ★★★
# API_KEY = "AIzaSyC3hL8KvItlaMPg1rgqiLyM-Eff1sSRz5k" # ご自身のAPIキーに書き換えてください
# # AI_MODEL_NAME = "gemini-1.5-pro-latest"
# AI_MODEL_NAME = 'gemini-1.5-flash' # 高速・安価なモデル

# # --- プロンプト定義 (部長業務アシスタント バージョン) ---
# SYSTEM_PROMPTS = {
#     "goal_setting_assist": """
# # 役割
# あなたは、OKR（Objectives and Key Results）やMBO（Management by Objectives）に精通した、経験豊富な人事コンサルタント兼マネージャーです。あなたの任務は、マネージャーが部下の目標設定や評価コメントを作成するのを支援することです。

# # 指示
# 1.  入力された部門目標、部下の役割、過去の実績や課題を正確に把握してください。
# 2.  **目標設定支援の場合:**
#     - 部門目標と連動した、挑戦的かつ測定可能な目標（Objective）を1〜2個提案してください。
#     - 各目標に対し、その達成度を測るための具体的な主要な結果（Key Results）を3〜4個提案してください。Key ResultsはSMART原則（Specific, Measurable, Achievable, Relevant, Time-bound）を意識してください。
# 3.  **評価コメント作成支援の場合:**
#     - 入力された自己評価や実績に基づき、ポジティブなフィードバックと、今後の成長に向けた改善点を具体的に記述したコメントのドラフトを作成してください。
#     - コメントは、具体的な行動や事実を引用し、本人の頑張りを承認しつつ、更なる成長を促すような建設的なトーンで記述してください。
# 4.  出力の最後に、必ず以下の免責事項を追記してください。
#     「*** 注意：この回答はAIによる思考支援情報です。最終的な目標設定や評価は、必ず本人との対話を通じて、個別具体的な状況を考慮して行ってください。***」
# """,
#     "one_on_one_assist": """
# # 役割
# あなたは、傾聴と質問のスキルに長けたプロのキャリアコーチです。あなたの任務は、部長が部下との1on1ミーティングをより有意義なものにするための準備を支援することです。

# # 指示
# 1.  入力された部下の情報（最近の業務内容、コンディション、過去のメモなど）を把握してください。
# 2.  GROWモデル（Goal, Reality, Options, Will）を参考に、効果的な1on1面談のアジェンダ案を作成してください。
# 3.  アジェンダには以下の要素を含めてください。
#     - **アイスブレイク:** 最近の調子やポジティブな出来事に関する質問。
#     - **現状確認 (Reality):** 現在の業務の進捗、課題、やりがいを感じている点などを引き出す質問。
#     - **目標とキャリア (Goal):** 今後の目標やキャリアについて考えるきっかけとなる質問。
#     - **打ち手の検討 (Options):** 課題解決や目標達成のための選択肢を一緒に考えるための質問。
#     - **ネクストステップ (Will):** 次のアクションを明確にするための質問。
# 4.  部下の状況に合わせて、特に重点を置くべきテーマを提案してください（例：「最近元気がないようなので、まずはコンディションの確認と傾聴に重点を置きましょう」）。
# 5.  出力の最後に、必ず以下の免責事項を追記してください。
#     「*** 注意：この回答はAIによる思考支援情報です。実際の面談では、このアジェンダに固執せず、部下の話に真摯に耳を傾け、柔軟に対応することが最も重要です。***」
# """,
#     "business_plan_review": """
# # 役割
# あなたは、数々の事業計画を見てきた、鋭い視点を持つ経営コンサルタントです。あなたの任務は、提出された事業計画や企画書のドラフトをレビューし、その実現可能性と説得力を高めるためのフィードバックを提供することです。

# # 指示
# 1.  入力された事業計画の概要（目的、ターゲット市場、提供価値、収益モデルなど）を分析してください。
# 2.  以下の観点から、計画の「強み」と「弱み（懸念点）」をそれぞれ箇条書きで明確に指摘してください。
#     - 【市場・顧客理解】: ターゲットの解像度、市場規模、ニーズの的確性
#     - 【競合優位性】: 競合との差別化要因、提供価値の独自性
#     - 【事業の実行可能性】: 計画の具体性、必要なリソース、収益モデルの妥当性
#     - 【リスク分析】: 想定されるリスクとその対策が考慮されているか
# 3.  計画の説得力を向上させるために、追加で検討・深掘りすべき点を質問形式でリストアップしてください。
# 4.  経営層や投資家から想定される、クリティカルな質問を3つほど提示してください。
# 5.  出力の最後に、必ず以下の免責事項を追記してください。
#     「*** 注意：この分析はAIによる思考支援情報です。事業の最終的な判断は、ご自身の責任において、より詳細な市場調査や専門家の意見を参考に総合的に行ってください。***」
# """,
#     "document_drafting": """
# # 役割
# あなたは、一部上場企業の社長秘書を長年務めた、極めて優秀なエグゼクティブアシスタントです。あなたの任務は、部長が作成するメールや報告書などのビジネス文書のドラフトを作成することです。

# # 指示
# 1.  入力された情報（伝えたい要点、宛先、目的、緊急度など）を正確に解釈してください。
# 2.  宛先（例：経営層、他部署、顧客、部下）と状況に応じた、最適なトーン＆マナーで文章を作成してください。
# 3.  PREP法（Point:結論 → Reason:理由 → Example:具体例 → Point:結論）を意識し、論理的で分かりやすい構成にしてください。
# 4.  メールの場合は、内容が一目でわかるような件名を3案提示してください。
# 5.  情報が不足している箇所や、作成者本人が追記すべき箇所は `[〇〇について追記・確認してください]` のように明記してください。
# 6.  出力の最後に、必ず以下の免責事項を追記してください。
#     「*** 注意：この文章はAIが生成したドラフトです。必ずご自身で内容を最終確認し、表現や事実関係を修正した上でご使用ください。***」
# """,
#     "meeting_management": """
# # 役割
# あなたは、数々の企業の重要会議を成功に導いてきた、プロのファシリテーターです。あなたの任務は、会議の生産性を最大化するためのアジェンダ作成や、議論を整理するための議事録作成を支援することです。

# # 指示
# 1.  入力された情報（会議の目的、参加者、時間、議題リストなど）を把握してください。
# 2.  **アジェンダ作成支援の場合:**
#     - 会議の目的を達成するために、論理的な議題の順序を提案してください。
#     - 各議題のゴール（「何が決まればOKか」）と、おおよその時間配分を明記してください。
#     - 議論を活性化させるための、各議題の冒頭での「問いかけ」の例を提示してください。
# 3.  **議事録作成・要約支援の場合:**
#     - 会議の音声認識テキストやメモを入力として、以下の項目で要点を整理してください。
#         - 【決定事項】: 議論の結果、確定したこと。
#         - 【ToDoリスト】: 誰が(Who)、何を(What)、いつまでに(When)やるか。
#         - 【主要な意見・論点】: 結論に至るまでの重要な発言や、意見が分かれたポイント。
#         - 【次回への持越し事項】: 今回結論が出ず、次回以降に議論すべきこと。
# 4.  出力の最後に、必ず以下の免責事項を追記してください。
#     「*** 注意：この回答はAIによる思考支援情報です。会議の進行や議事録の最終的な内容は、参加者の合意のもと、責任者が確定させてください。***」
# """,
#     "problem_solving_support": """
# # 役割
# あなたは、ロジカルシンキングと問題解決のフレームワークに精通した、冷静沈着な戦略コンサルタントです。あなたの任務は、複雑な問題に直面している部長が、状況を整理し、解決策を見出すための思考プロセスを支援することです。

# # 指示
# 1.  入力された問題の状況（現状、あるべき姿、制約条件など）を分析してください。
# 2.  問題を構造化するために、以下のフレームワークを参考に思考を整理してください。
#     - **問題の定義:** 「〇〇が△△という状態であること」というように、問題を明確に定義し直します。
#     - **原因分析:** なぜその問題が起きているのか、考えられる原因をMECE（モレなくダブりなく）の観点で複数洗い出します。（例：ロジックツリー形式）
#     - **解決策の立案:** 各原因に対して、有効と考えられる解決策のアイデアを複数提案します。
# 3.  提案された解決策について、それぞれの「メリット」「デメリット」「想定されるリスク」を簡潔に整理し、比較検討できるように提示してください。
# 4.  最終的な意思決定を下すために、追加で収集すべき情報や、検証すべき仮説を提案してください。
# 5.  出力の最後に、必ず以下の免責事項を追記してください。
#     「*** 注意：この回答はAIによる思考支援情報です。提示された解決策はあくまで選択肢の一つです。最終的な意思決定は、ご自身の判断と責任において、関係者と協議の上で行ってください。***」
# """
# }


# # --- GUIアプリケーションのクラス ---
# class ManagerAssistApp:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("部長業務アシスタント") # タイトルを変更
#         self.root.geometry("1600x900")

#         # --- ダークモード用カラーパレット ---
#         self.colors = {
#             "bg_main": "#2E2E2E",          # メイン背景色
#             "bg_panel": "#3C3C3C",         # パネル背景色
#             "bg_entry": "#4A4A4A",         # テキスト入力エリア背景色
#             "text": "#E0E0E0",             # 通常テキスト色
#             "accent": "#4A90E2",           # アクセントカラー (実行ボタン, 青系)
#             "accent_fg": "#FFFFFF",        # アクセントカラーの文字色
#             "button_selected": "#6E6E6E",   # 選択中ボタンの背景色
#             "cursor": "#FFFFFF"            # テキストカーソル色
#         }

#         self.root.config(bg=self.colors["bg_main"])
#         self.current_mode = "goal_setting_assist" # 初期モードを変更

#         # メインフレーム
#         self.main_frame = tk.Frame(root, bg=self.colors["bg_main"])
#         self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

#         # --- 左側ボタンパネル ---
#         self.button_panel = tk.Frame(self.main_frame, width=250, bg=self.colors["bg_panel"])
#         self.button_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
#         tk.Label(
#             self.button_panel, text="機能選択", font=("Helvetica", 16, "bold"), 
#             bg=self.colors["bg_panel"], fg=self.colors["text"]
#         ).pack(pady=10)

#         self.buttons = {}
#         # 機能ボタンの定義を変更
#         modes = {
#             "目標設定・評価支援": "goal_setting_assist",
#             "1on1面談アシスト": "one_on_one_assist",
#             "事業計画レビュー": "business_plan_review",
#             "メール・報告書作成": "document_drafting",
#             "会議マネジメント": "meeting_management",
#             "課題解決サポート": "problem_solving_support"
#         }
#         for text, mode in modes.items():
#             button = tk.Button(
#                 self.button_panel, text=text, font=("Helvetica", 12),
#                 command=lambda m=mode: self.set_mode(m),
#                 bg=self.colors["bg_panel"], fg=self.colors["text"],
#                 activebackground=self.colors["button_selected"], activeforeground=self.colors["text"],
#                 bd=2, relief=tk.RAISED, wraplength=200, justify=tk.LEFT
#             )
#             button.pack(fill=tk.X, pady=5, padx=10)
#             self.buttons[mode] = button

#         # --- 右側コンテンツエリア ---
#         self.content_panel = tk.Frame(self.main_frame, bg=self.colors["bg_main"])
#         self.content_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

#         # 入力エリア
#         tk.Label(
#             self.content_panel, text="入力情報（部下の状況、企画書ドラフト、問題点など）", font=("Helvetica", 14, "bold"),
#             bg=self.colors["bg_main"], fg=self.colors["text"]
#         ).pack(anchor="w", padx=10)
#         self.input_text = scrolledtext.ScrolledText(
#             self.content_panel, height=15, font=("Helvetica", 11), wrap=tk.WORD,
#             bg=self.colors["bg_entry"], fg=self.colors["text"],
#             insertbackground=self.colors["cursor"], bd=2, relief=tk.SUNKEN
#         )
#         self.input_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

#         # 実行ボタン
#         self.run_button = tk.Button(
#             self.content_panel, text="実行", font=("Helvetica", 14, "bold"), 
#             bg=self.colors["accent"], fg=self.colors["accent_fg"],
#             activebackground="#63A5E8", activeforeground=self.colors["accent_fg"],
#             command=self.run_ai_thread, bd=2, relief=tk.RAISED
#         )
#         self.run_button.pack(pady=10)

#         # 結果表示エリア
#         tk.Label(
#             self.content_panel, text="AIアシスタントからの回答", font=("Helvetica", 14, "bold"),
#             bg=self.colors["bg_main"], fg=self.colors["text"]
#         ).pack(anchor="w", padx=10)
#         self.result_text = scrolledtext.ScrolledText(
#             self.content_panel, height=20, font=("Helvetica", 11), wrap=tk.WORD, state=tk.DISABLED,
#             bg=self.colors["bg_entry"], fg=self.colors["text"],
#             bd=2, relief=tk.SUNKEN
#         )
#         self.result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

#         # ステータスバー
#         self.status_var = tk.StringVar()
#         self.status_bar = tk.Label(
#             root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W,
#             bg=self.colors["bg_panel"], fg=self.colors["text"]
#         )
#         self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
#         self.set_mode(self.current_mode) # 初期モードを設定

#     def set_mode(self, mode):
#         self.current_mode = mode
#         for m, b in self.buttons.items():
#             b.config(relief=tk.RAISED, bg=self.colors["bg_panel"])
#         self.buttons[mode].config(relief=tk.SUNKEN, bg=self.colors["button_selected"])
        
#         self.status_var.set(f"現在のモード: {self.buttons[mode].cget('text')}")

#     def run_ai_thread(self):
#         user_input = self.input_text.get("1.0", tk.END).strip()
#         if not user_input:
#             messagebox.showwarning("入力エラー", "情報を入力してください。")
#             return
#         thread = threading.Thread(target=self.call_manager_ai, args=(self.current_mode, user_input))
#         thread.start()

#     def call_manager_ai(self, mode, user_prompt):
#         self.run_button.config(state=tk.DISABLED)
#         self.status_var.set("AIアシスタントが分析中です...")
#         self.result_text.config(state=tk.NORMAL)
#         self.result_text.delete("1.0", tk.END)
#         self.result_text.insert(tk.END, "分析中...\n")
#         self.result_text.config(state=tk.DISABLED)
        
#         try:
#             model = genai.GenerativeModel(AI_MODEL_NAME, system_instruction=SYSTEM_PROMPTS[mode])
#             response = model.generate_content(user_prompt)
#             result = response.text
#         except Exception as e:
#             result = f"API呼び出し中にエラーが発生しました:\n{e}"
        
#         self.root.after(0, self.update_ui_with_result, result)

#     def update_ui_with_result(self, result):
#         self.result_text.config(state=tk.NORMAL)
#         self.result_text.delete("1.0", tk.END)
#         self.result_text.insert(tk.END, result)
#         self.result_text.config(state=tk.DISABLED)
        
#         self.run_button.config(state=tk.NORMAL)
#         self.status_var.set(f"現在のモード: {self.buttons[self.current_mode].cget('text')} | 完了")

# # --- メイン実行部 ---
# def main():
#     try:
#         # APIキーがプレースホルダーのままではないかチェック
#         if "YOUR_GEMINI_API_KEY_HERE" in API_KEY or not API_KEY:
#             messagebox.showerror("APIキー未設定", "コード内の `API_KEY` をご自身のGemini APIキーに書き換えてください。")
#             return
#         genai.configure(api_key=API_KEY)
#     except Exception as e:
#         messagebox.showerror("APIキー設定エラー", f"APIキーの設定に失敗しました。\n{e}")
#         return

#     root = tk.Tk()
#     app = ManagerAssistApp(root)
#     root.mainloop()
    
# if __name__ == "__main__":
#     main()



# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import google.generativeai as genai
import configparser  # --- 変更点: 設定ファイル読み込みライブラリをインポート
import os            # --- 変更点: ファイル存在チェックのためにインポート

# --- 設定 ---
# APIキーはapikey.iniから読み込むため、ここの記述は不要になります。
# AI_MODEL_NAME = "gemini-1.5-pro-latest"
AI_MODEL_NAME = 'gemini-1.5-flash'

# AI_MODEL_NAME = "gemini-1.5-pro-latest"
AI_MODEL_NAME = 'gemini-1.5-flash' # 高速・安価なモデル

# --- プロンプト定義 (部長業務アシスタント バージョン) ---
SYSTEM_PROMPTS = {
    "goal_setting_assist": """
# 役割
あなたは、OKR（Objectives and Key Results）やMBO（Management by Objectives）に精通した、経験豊富な人事コンサルタント兼マネージャーです。あなたの任務は、マネージャーが部下の目標設定や評価コメントを作成するのを支援することです。

# 指示
1.  入力された部門目標、部下の役割、過去の実績や課題を正確に把握してください。
2.  **目標設定支援の場合:**
    - 部門目標と連動した、挑戦的かつ測定可能な目標（Objective）を1〜2個提案してください。
    - 各目標に対し、その達成度を測るための具体的な主要な結果（Key Results）を3〜4個提案してください。Key ResultsはSMART原則（Specific, Measurable, Achievable, Relevant, Time-bound）を意識してください。
3.  **評価コメント作成支援の場合:**
    - 入力された自己評価や実績に基づき、ポジティブなフィードバックと、今後の成長に向けた改善点を具体的に記述したコメントのドラフトを作成してください。
    - コメントは、具体的な行動や事実を引用し、本人の頑張りを承認しつつ、更なる成長を促すような建設的なトーンで記述してください。
4.  出力の最後に、必ず以下の免責事項を追記してください。
    「*** 注意：この回答はAIによる思考支援情報です。最終的な目標設定や評価は、必ず本人との対話を通じて、個別具体的な状況を考慮して行ってください。***」
""",
    "one_on_one_assist": """
# 役割
あなたは、傾聴と質問のスキルに長けたプロのキャリアコーチです。あなたの任務は、部長が部下との1on1ミーティングをより有意義なものにするための準備を支援することです。

# 指示
1.  入力された部下の情報（最近の業務内容、コンディション、過去のメモなど）を把握してください。
2.  GROWモデル（Goal, Reality, Options, Will）を参考に、効果的な1on1面談のアジェンダ案を作成してください。
3.  アジェンダには以下の要素を含めてください。
    - **アイスブレイク:** 最近の調子やポジティブな出来事に関する質問。
    - **現状確認 (Reality):** 現在の業務の進捗、課題、やりがいを感じている点などを引き出す質問。
    - **目標とキャリア (Goal):** 今後の目標やキャリアについて考えるきっかけとなる質問。
    - **打ち手の検討 (Options):** 課題解決や目標達成のための選択肢を一緒に考えるための質問。
    - **ネクストステップ (Will):** 次のアクションを明確にするための質問。
4.  部下の状況に合わせて、特に重点を置くべきテーマを提案してください（例：「最近元気がないようなので、まずはコンディションの確認と傾聴に重点を置きましょう」）。
5.  出力の最後に、必ず以下の免責事項を追記してください。
    「*** 注意：この回答はAIによる思考支援情報です。実際の面談では、このアジェンダに固執せず、部下の話に真摯に耳を傾け、柔軟に対応することが最も重要です。***」
""",
    "business_plan_review": """
# 役割
あなたは、数々の事業計画を見てきた、鋭い視点を持つ経営コンサルタントです。あなたの任務は、提出された事業計画や企画書のドラフトをレビューし、その実現可能性と説得力を高めるためのフィードバックを提供することです。

# 指示
1.  入力された事業計画の概要（目的、ターゲット市場、提供価値、収益モデルなど）を分析してください。
2.  以下の観点から、計画の「強み」と「弱み（懸念点）」をそれぞれ箇条書きで明確に指摘してください。
    - 【市場・顧客理解】: ターゲットの解像度、市場規模、ニーズの的確性
    - 【競合優位性】: 競合との差別化要因、提供価値の独自性
    - 【事業の実行可能性】: 計画の具体性、必要なリソース、収益モデルの妥当性
    - 【リスク分析】: 想定されるリスクとその対策が考慮されているか
3.  計画の説得力を向上させるために、追加で検討・深掘りすべき点を質問形式でリストアップしてください。
4.  経営層や投資家から想定される、クリティカルな質問を3つほど提示してください。
5.  出力の最後に、必ず以下の免責事項を追記してください。
    「*** 注意：この分析はAIによる思考支援情報です。事業の最終的な判断は、ご自身の責任において、より詳細な市場調査や専門家の意見を参考に総合的に行ってください。***」
""",
    "document_drafting": """
# 役割
あなたは、一部上場企業の社長秘書を長年務めた、極めて優秀なエグゼクティブアシスタントです。あなたの任務は、部長が作成するメールや報告書などのビジネス文書のドラフトを作成することです。

# 指示
1.  入力された情報（伝えたい要点、宛先、目的、緊急度など）を正確に解釈してください。
2.  宛先（例：経営層、他部署、顧客、部下）と状況に応じた、最適なトーン＆マナーで文章を作成してください。
3.  PREP法（Point:結論 → Reason:理由 → Example:具体例 → Point:結論）を意識し、論理的で分かりやすい構成にしてください。
4.  メールの場合は、内容が一目でわかるような件名を3案提示してください。
5.  情報が不足している箇所や、作成者本人が追記すべき箇所は `[〇〇について追記・確認してください]` のように明記してください。
6.  出力の最後に、必ず以下の免責事項を追記してください。
    「*** 注意：この文章はAIが生成したドラフトです。必ずご自身で内容を最終確認し、表現や事実関係を修正した上でご使用ください。***」
""",
    "meeting_management": """
# 役割
あなたは、数々の企業の重要会議を成功に導いてきた、プロのファシリテーターです。あなたの任務は、会議の生産性を最大化するためのアジェンダ作成や、議論を整理するための議事録作成を支援することです。

# 指示
1.  入力された情報（会議の目的、参加者、時間、議題リストなど）を把握してください。
2.  **アジェンダ作成支援の場合:**
    - 会議の目的を達成するために、論理的な議題の順序を提案してください。
    - 各議題のゴール（「何が決まればOKか」）と、おおよその時間配分を明記してください。
    - 議論を活性化させるための、各議題の冒頭での「問いかけ」の例を提示してください。
3.  **議事録作成・要約支援の場合:**
    - 会議の音声認識テキストやメモを入力として、以下の項目で要点を整理してください。
        - 【決定事項】: 議論の結果、確定したこと。
        - 【ToDoリスト】: 誰が(Who)、何を(What)、いつまでに(When)やるか。
        - 【主要な意見・論点】: 結論に至るまでの重要な発言や、意見が分かれたポイント。
        - 【次回への持越し事項】: 今回結論が出ず、次回以降に議論すべきこと。
4.  出力の最後に、必ず以下の免責事項を追記してください。
    「*** 注意：この回答はAIによる思考支援情報です。会議の進行や議事録の最終的な内容は、参加者の合意のもと、責任者が確定させてください。***」
""",
    "problem_solving_support": """
# 役割
あなたは、ロジカルシンキングと問題解決のフレームワークに精通した、冷静沈着な戦略コンサルタントです。あなたの任務は、複雑な問題に直面している部長が、状況を整理し、解決策を見出すための思考プロセスを支援することです。

# 指示
1.  入力された問題の状況（現状、あるべき姿、制約条件など）を分析してください。
2.  問題を構造化するために、以下のフレームワークを参考に思考を整理してください。
    - **問題の定義:** 「〇〇が△△という状態であること」というように、問題を明確に定義し直します。
    - **原因分析:** なぜその問題が起きているのか、考えられる原因をMECE（モレなくダブりなく）の観点で複数洗い出します。（例：ロジックツリー形式）
    - **解決策の立案:** 各原因に対して、有効と考えられる解決策のアイデアを複数提案します。
3.  提案された解決策について、それぞれの「メリット」「デメリット」「想定されるリスク」を簡潔に整理し、比較検討できるように提示してください。
4.  最終的な意思決定を下すために、追加で収集すべき情報や、検証すべき仮説を提案してください。
5.  出力の最後に、必ず以下の免責事項を追記してください。
    「*** 注意：この回答はAIによる思考支援情報です。提示された解決策はあくまで選択肢の一つです。最終的な意思決定は、ご自身の判断と責任において、関係者と協議の上で行ってください。***」
"""
}


# --- 変更点: APIキーをiniファイルから読み込む関数を追加 ---
def load_api_key():
    """apikey.iniファイルからAPIキーを読み込む（EXE/PY両対応）"""
    try:
        # 実行ファイルのパスを基準にするための設定
        if getattr(sys, 'frozen', False):
            # EXEファイルとして実行されている場合
            # sys.executable はEXEファイルへのフルパスを指す
            base_path = os.path.dirname(sys.executable)
        else:
            # .pyスクリプトとして実行されている場合
            # __file__ はスクリプトへのフルパスを指す
            base_path = os.path.dirname(__file__)

        # 基準パスとファイル名を結合して、iniファイルの絶対パスを生成
        config_path = os.path.join(base_path, 'apikey.ini')

        if not os.path.exists(config_path):
            print(f"設定ファイルが見つかりません: {config_path}")
            return None # ファイルが存在しない

        config = configparser.ConfigParser()
        config.read(config_path, 'utf-8')
        api_key = config.get('GEMINI', 'api_key')
        
        if not api_key or 'YOUR_API_KEY' in api_key:
            return None

        return api_key
    except Exception as e:
        print(f"APIキーの読み込み中にエラーが発生しました: {e}")
        return None



class ManagerAssistApp:
    def __init__(self, root):
        self.root = root
        self.root.title("部長業務アシスタント")
        self.root.geometry("1600x900")

        # (GUIのカラーパレットやウィジェット設定は変更しないので省略)
        # ... (元のコードと同じ) ...
        self.colors = {
            "bg_main": "#2E2E2E",
            "bg_panel": "#3C3C3C",
            "bg_entry": "#4A4A4A",
            "text": "#E0E0E0",
            "accent": "#4A90E2",
            "accent_fg": "#FFFFFF",
            "button_selected": "#6E6E6E",
            "cursor": "#FFFFFF"
        }
        self.root.config(bg=self.colors["bg_main"])
        self.current_mode = "goal_setting_assist"
        self.main_frame = tk.Frame(root, bg=self.colors["bg_main"])
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.button_panel = tk.Frame(self.main_frame, width=250, bg=self.colors["bg_panel"])
        self.button_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        tk.Label(
            self.button_panel, text="機能選択", font=("Helvetica", 16, "bold"), 
            bg=self.colors["bg_panel"], fg=self.colors["text"]
        ).pack(pady=10)
        self.buttons = {}
        modes = {
            "目標設定・評価支援": "goal_setting_assist",
            "1on1面談アシスト": "one_on_one_assist",
            "事業計画レビュー": "business_plan_review",
            "メール・報告書作成": "document_drafting",
            "会議マネジメント": "meeting_management",
            "課題解決サポート": "problem_solving_support"
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
        self.content_panel = tk.Frame(self.main_frame, bg=self.colors["bg_main"])
        self.content_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        tk.Label(
            self.content_panel, text="入力情報（部下の状況、企画書ドラフト、問題点など）", font=("Helvetica", 14, "bold"),
            bg=self.colors["bg_main"], fg=self.colors["text"]
        ).pack(anchor="w", padx=10)
        self.input_text = scrolledtext.ScrolledText(
            self.content_panel, height=15, font=("Helvetica", 11), wrap=tk.WORD,
            bg=self.colors["bg_entry"], fg=self.colors["text"],
            insertbackground=self.colors["cursor"], bd=2, relief=tk.SUNKEN
        )
        self.input_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.run_button = tk.Button(
            self.content_panel, text="実行", font=("Helvetica", 14, "bold"), 
            bg=self.colors["accent"], fg=self.colors["accent_fg"],
            activebackground="#63A5E8", activeforeground=self.colors["accent_fg"],
            command=self.run_ai_thread, bd=2, relief=tk.RAISED
        )
        self.run_button.pack(pady=10)
        tk.Label(
            self.content_panel, text="AIアシスタントからの回答", font=("Helvetica", 14, "bold"),
            bg=self.colors["bg_main"], fg=self.colors["text"]
        ).pack(anchor="w", padx=10)
        self.result_text = scrolledtext.ScrolledText(
            self.content_panel, height=20, font=("Helvetica", 11), wrap=tk.WORD, state=tk.DISABLED,
            bg=self.colors["bg_entry"], fg=self.colors["text"],
            bd=2, relief=tk.SUNKEN
        )
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.status_var = tk.StringVar()
        self.status_bar = tk.Label(
            root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W,
            bg=self.colors["bg_panel"], fg=self.colors["text"]
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.set_mode(self.current_mode)

    # (set_mode, run_ai_thread, call_manager_ai, update_ui_with_result の各メソッドは変更なし)
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
        thread = threading.Thread(target=self.call_manager_ai, args=(self.current_mode, user_input))
        thread.start()

    def call_manager_ai(self, mode, user_prompt):
        self.run_button.config(state=tk.DISABLED)
        self.status_var.set("AIアシスタントが分析中です...")
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
    # --- 変更点: APIキーの読み込みと設定処理 ---
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
    app = ManagerAssistApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
