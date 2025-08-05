import google.generativeai as genai
import os
import random
import re
import json
from datetime import datetime
from gtts import gTTS
from playsound import playsound
from pydub import AudioSegment
from pydub.exceptions import CouldntEncodeError

# pydubにffmpeg.exeの場所を直接教える
AudioSegment.converter = "C:/Program Files/ffmpeg-2025-07-31-git-119d127d05-full_build/bin/ffmpeg.exe"

# --- 音声入力のためのライブラリ ---
import speech_recognition as sr
import japanese_numbers

# --- 設定ゾーン ---
API_KEY = "AIzaSyC3hL8KvItlaMPg1rgqiLyM-Eff1sSRz5k"  # ★★★ 必ず自分のAPIキーに書き換えてね！ ★★★
USER_DATA_FILE = "user_data.json"
ADVICE_FILES = { "BP_HIGH": "advice_blood_pressure.txt", "PULSE_FAST": "advice_heart_rate.txt", "SPO2_LOW": "advice_oxygen.txt" }
SPEED_SETTINGS = {
    'slow':   {'rate': 1.85, 'prompt_hint': '一文を短く、相槌を多めに、間を意識して、おっとりと話してください。'},
    'normal': {'rate': 2.0,  'prompt_hint': '少しテンポよく、分かりやすく話してください。'},
    'fast':   {'rate': 2.5,  'prompt_hint': 'テキパキと、要点をまとめて簡潔に話してください。'}
}

# --- ★★★ ご要望に合わせてプロンプトを大幅に強化しました ★★★ ---
HANA_SAN_PROMPT_TEMPLATE = """
# --- キャラクタープロンプト ---
あなたは、ご高齢の方の健康相談相手、おっとりとしていて非常に聞き上手な「はな」です。
ユーザーの名前は {user_name} さんです。必ず会話の中で {user_name} さんの名前を呼んであげてください。
あなたの役割は、単なる情報伝達ではなく、温かい血の通った「会話」をすることです。

# あなたの話し方
{speech_style_hint}

# あなたの会話のルール
- 【最重要】会話のキャッチボールを意識する: 一方的に話さず、「〜でしたか？」「〜かもしれませんわね」のように、常に相手に問いかけ、共感する姿勢を見せてください。
- 【最重要】良い点から話す: まずは結果の良い部分（例：酸素飽和度など）を褒めて、相手を安心させてから、少し気になる点について触れてください。
- 決めつけない、優しい推測: 「血圧が高いですね」ではなく、「血圧がほんの少しだけ、いつもよりお元気なようですわね」のように、断定的でない、柔らかい表現を使ってください。
- 具体的な生活の提案: アドバイスは、命令ではなく、すぐに試せるような優しい提案の形にしてください。「塩分を控えろ」ではなく、「お味噌汁のお出汁をしっかり取ると、お味噌が少量でも美味しく感じられますよ」のように。
- 情報をまとめる: 関連する項目（例：血圧と脈拍）は、「血圧と脈拍が、少しだけ…」のように、まとめて話すことで、会話の流れを自然にしてください。
- 相槌を効果的に使う: 「まあ」「ええ、ええ」「あらあら」といった相槌を会話に含めることで、人間らしい「間」と思慮深さを表現してください。
- 自由会話を楽しむ: 健康チェック以外の雑談では、相手の話に興味を持って耳を傾け、会話を広げてください。

# あなたに渡される情報
- (健康チェック時) ユーザーの健康データに対する基本的なコメントと、【ワンポイントアドバイス】のテキスト。
- (自由会話時) ユーザーからのメッセージ。

# あなたの仕事
これらの情報を元に、上記の会話のルールを**絶対に**守りながら、全体を一つの自然で、温かく、聞き上手な「はなさん」の語りかけに再構成してください。

# あなたの口調ルール
- 非常に丁寧で、ゆっくり、穏やかな口調を保ってください。「〜ですわ」「〜ますね」など。
- ユーザーを不安にさせず、常に励ますような、前向きな言葉遣いをしてください。
- 決して「診断」はしないでください。「少し高めのようですわね」のように、断定は避けてください。
- 【ワンポイントアドバイス】は、自然な会話の中に、さりげなく、一つだけ含めてください。
- 【メンタルモード】については、ユーザーに結果を伝えるだけで、一切のコメントや評価をしないでください。
"""

def get_hana_san_prompt(user_name, speed_key):
    style_hint = SPEED_SETTINGS.get(speed_key, SPEED_SETTINGS['normal'])['prompt_hint']
    return HANA_SAN_PROMPT_TEMPLATE.format(user_name=user_name, speech_style_hint=style_hint)

def change_audio_speed(audio_segment, speed=2.0):
    if speed == 2.0: return audio_segment
    new_frame_rate = int(audio_segment.frame_rate * speed)
    try:
        return audio_segment._spawn(audio_segment.raw_data).set_frame_rate(new_frame_rate)
    except Exception as e:
        print(f"（音声速度の変更でエラーが発生しました: {e}）"); return audio_segment

def speak(text, speed_key='normal', character_name="はな"):
    print(f"\n{character_name}： {text}")
    playback_rate = SPEED_SETTINGS.get(speed_key, SPEED_SETTINGS['normal'])['rate']
    try:
        sentences = re.split(r'(?<=[。！？])', text); sentences = [s.strip() for s in sentences if s.strip()]
        for i, sentence in enumerate(sentences):
            temp_fn, proc_fn = f"temp_{i}.mp3", f"proc_{i}.mp3"
            tts = gTTS(text=sentence, lang='ja'); tts.save(temp_fn)
            if not os.path.exists(temp_fn): continue
            sound = AudioSegment.from_mp3(temp_fn)
            sound = change_audio_speed(sound, playback_rate)
            sound.export(proc_fn, format="mp3")
            if os.path.exists(proc_fn): playsound(proc_fn)
            if os.path.exists(temp_fn): os.remove(temp_fn)
            if os.path.exists(proc_fn): os.remove(proc_fn)
    except Exception as e: print(f"（音声の再生でエラー: {e}）")
    return len(text)

def convert_japanese_number_to_int(text):
    try:
        return int(text)
    except ValueError:
        try:
            result_list = japanese_numbers.to_arabic_numbers(text)
            if result_list: return int(result_list[0][0])
        except (IndexError, TypeError): return None
    return None

def listen_for_voice(timeout_seconds=5):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("（マイクでどうぞ...）"); r.adjust_for_ambient_noise(source)
        try:
            audio = r.listen(source, timeout=timeout_seconds, phrase_time_limit=10)
            recognized_text = r.recognize_google(audio, language='ja-JP')
            print(f"（認識結果: {recognized_text}）"); return recognized_text
        except sr.WaitTimeoutError: print("（タイムアウトしました。キーボードで入力してください。）")
        except sr.UnknownValueError: print("（すみません、うまく聞き取れませんでした。）")
        except Exception as e: print(f"（音声入力でエラーが発生しました: {e}）")
        return None

def get_user_input(prompt_text, speed_key, is_numeric=False):
    text_length = speak(prompt_text, speed_key)
    additional_time = text_length // 20
    timeout = min(5 + additional_time, 15)
    
    while True:
        voice_input = listen_for_voice(timeout_seconds=timeout)
        if voice_input:
            if is_numeric:
                num = convert_japanese_number_to_int(voice_input)
                if num is not None: return num
                else: speak("あら、ごめんなさい。数字で教えていただけますか？", speed_key)
            else:
                return voice_input
        
        kb_input = input(f"{prompt_text}（キーボードでどうぞ）: ")
        if not kb_input: continue
        if is_numeric:
            try: return int(kb_input)
            except ValueError: speak("申し訳ありません。数字で入力してくださいね。", speed_key)
        else: return kb_input

def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r', encoding='utf-8') as f: data = json.load(f)
        if "speech_speed" not in data: data["speech_speed"] = "normal"
        if "ai_model" not in data: data["ai_model"] = "gemini-1.5-flash"
        return data
    else:
        name = input("はじめまして。あなたのお名前を教えていただけますか？: ")
        user_data = {"name": name, "speech_speed": "normal", "ai_model": "gemini-1.5-flash", "health_records": []}
        save_user_data(user_data)
        return user_data

def save_user_data(data):
    with open(USER_DATA_FILE, 'w', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False, indent=4)
def save_health_data(user_data, new_data):
    record = {"date": datetime.now().isoformat(), "systolic": new_data["s"], "diastolic": new_data["d"], "pulse": new_data["p"], "spo2": new_data["o"]}
    user_data["health_records"].append(record); save_user_data(user_data)
    print("\n（今回の測定結果を記録しました）")
def get_random_advice(c):
    fp=ADVICE_FILES.get(c)
    if not fp or not os.path.exists(fp): return None
    try:
        with open(fp, "r", encoding="utf-8") as f: lines = [l.strip() for l in f.readlines() if l.strip()]; return random.choice(lines) if lines else None
    except: return None
def check_health_data(s,d,p,o):
    r={};a_s,a_d,a_p=125,75,70
    if s>=140 or d>=90:r["blood_pressure"]=("少し高めのようですわね","BP_HIGH")
    elif s>=a_s+20 or d>=a_d+10:r["blood_pressure"]=("いつもより、少し高めかもしれませんね","BP_HIGH")
    elif s<100:r["blood_pressure"]=("少し低めかもしれませんね。念のため、もう一度測ってみるのも良いかもしれません",None)
    else:r["blood_pressure"]=("落ち着いていて、よろしいですわね",None)
    if p>=100:r["pulse"]=("少し速いようですわね","PULSE_FAST")
    elif p>=a_p+20:r["pulse"]=("いつもより、少し速いかもしれませんね","PULSE_FAST")
    elif p<50:r["pulse"]=("少しゆっくりかもしれませんね。もし気になるようでしたら、もう一度測ってみましょうか",None)
    else:r["pulse"]=("落ち着いていて、よろしいですわね",None)
    if o<=96:r["spo2"]=("少し低めかもしれませんね","SPO2_LOW")
    else:r["spo2"]=("しっかり酸素が取り込めていて、素晴らしいですわ",None)
    return r

def health_check_mode(user_data):
    speed_key = user_data["speech_speed"]
    model_name = user_data["ai_model"]
    print("\n--- 健康チェックモード ---")
    speak("今日の健康状態を、一緒に入力してみましょうか。", speed_key)
    
    s = get_user_input("上の血圧（収縮期）を教えていただけますか？", speed_key, is_numeric=True)
    d = get_user_input("下の血圧（拡張期）を教えていただけますか？", speed_key, is_numeric=True)
    p = get_user_input("脈拍を教えていただけますか？", speed_key, is_numeric=True)
    o = get_user_input("血中酸素（SpO2）を教えていただけますか？", speed_key, is_numeric=True)
    save_health_data(user_data, {"s": s, "d": d, "p": p, "o": o})
    
    health_results = check_health_data(s, d, p, o)
    final_comments, advice_to_give = [], None
    for item, (comment, condition) in health_results.items():
        final_comments.append(f"・{item.replace('_', ' ').title()}: {comment}")
        if condition and not advice_to_give: advice_to_give = get_random_advice(condition)
    mental_mode = random.choice(["ハツラツモード", "安定モード", "リラックスモード"])
    final_comments.append(f"・メンタルモード: {mental_mode} ですわね。")
    comment_text = '\n'.join(final_comments)
    
    # AIに渡すためのプロンプトを生成
    prompt_for_gemini = f"""
ユーザーの健康測定結果と、それに対するあなたの基本的なコメントは以下の通りです。
{comment_text}

もし【ワンポイントアドバイス】があれば、それも会話に含めてください。
なければ、結果を伝えて励ますだけで結構です。
あなたのキャラクターを守りながら、これらを一つの自然で優しい語りかけにまとめてください。

【ワンポイントアドバイス】: {advice_to_give if advice_to_give else "なし"}
"""
    speak("結果を見てみますね、少々お待ちください…", speed_key); print("-" * 50)
    try:
        model = genai.GenerativeModel(model_name)
        hana_san_prompt = get_hana_san_prompt(user_data['name'], speed_key)
        response = model.generate_content([hana_san_prompt, prompt_for_gemini])
        speak(response.text, speed_key)
    except Exception as e:
        speak("あら、申し訳ありません。少し調子が悪いようですわ。", speed_key); print(f"（内部エラー: {e}）")

def free_talk_mode(user_data):
    user_name, speed_key, model_name = user_data["name"], user_data["speech_speed"], user_data["ai_model"]
    print("\n--- 自由会話モード ---")
    
    hana_san_prompt = get_hana_san_prompt(user_name, speed_key)
    model = genai.GenerativeModel(model_name, system_instruction=hana_san_prompt)
    chat = model.start_chat(history=[])
    
    user_input = get_user_input(f"{user_name}さん、こんにちは。今日はどんな一日でしたか？", speed_key)
    
    while True:
        if not user_input or user_input in ["終了", "さようなら", "またね", "終わり", "おわり"]:
            speak("ええ、またお話ししましょうね。どうぞお元気で。", speed_key); break
        try:
            response = chat.send_message(user_input)
            user_input = get_user_input(response.text, speed_key)
        except Exception as e:
            speak("あら、申し訳ありません。もう一度お話しいただけますか？", speed_key); print(f"（内部エラー: {e}）")
            user_input = get_user_input("どうぞ。", speed_key)

def change_speed_mode(user_data):
    speed_key = user_data["speech_speed"]
    print("\n--- 話す速度の変更 ---")
    speak(f"現在の速度は「{speed_key}」ですわ。", speed_key)
    
    choice = get_user_input("どの速さにしますか？ (1: ゆっくり / 2: ふつう / 3: はやく)", speed_key)
    if not choice: return

    if any(w in choice for w in ['1', 'ゆっくり']): user_data['speech_speed'] = 'slow'
    elif any(w in choice for w in ['2', 'ふつう']): user_data['speech_speed'] = 'normal'
    elif any(w in choice for w in ['3', 'はやく']): user_data['speech_speed'] = 'fast'
    else: speak("あら、1, 2, 3のどれかで教えてくださいね。", speed_key); return

    save_user_data(user_data)
    speak(f"かしこまりました。これからは「{user_data['speech_speed']}」の速さでお話ししますね。", user_data['speech_speed'])

def change_model_mode(user_data):
    speed_key = user_data["speech_speed"]
    current_model = user_data["ai_model"]
    speak(f"現在のAIモデルは「{current_model}」ですわ。", speed_key)
    
    choice = get_user_input("どちらのモデルに変更しますか？ (1: 通常のFlash / 2: アドバンスのPro)", speed_key)
    if not choice: return

    if any(w in choice for w in ['1', 'flash', 'フラッシュ', '通常']):
        user_data['ai_model'] = 'gemini-1.5-flash'
    elif any(w in choice for w in ['2', 'pro', 'プロ', 'アドバンス']):
        user_data['ai_model'] = 'gemini-pro'
    else:
        speak("あら、1か2で教えてくださいね。", speed_key); return
        
    save_user_data(user_data)
    speak(f"AIモデルを「{user_data['ai_model']}」に変更しました。", user_data['speech_speed'])

def main():
    try: genai.configure(api_key=API_KEY)
    except Exception as e: print(f"APIキー設定エラー: {e}"); return

    user_data = load_user_data()
    
    hour = datetime.now().hour
    greeting = "こんばんは"
    if 4 <= hour < 10: greeting = "おはようございます"
    elif 10 <= hour < 17: greeting = "こんにちは"

    print("-" * 50); speak(f"{user_data['name']}さん、{greeting}。わたくし、お話し相手の「はな」と申します。", user_data['speech_speed'])
    
    while True:
        prompt = "\n今日は何をいたしましょうか？ (1: 健康チェック / 2: おしゃべり / 3: 速度変更 / 4: AIモデル変更 / 5: 終了)"
        mode_choice = get_user_input(prompt, user_data["speech_speed"])
        if not mode_choice: continue
        
        if any(w in mode_choice for w in ['1', '健康', 'チェック']):
            health_check_mode(user_data)
        elif any(w in mode_choice for w in ['2', 'おしゃべり', '会話']):
            free_talk_mode(user_data)
        elif any(w in mode_choice for w in ['3', '速度']):
            change_speed_mode(user_data)
        elif any(w in mode_choice for w in ['4', 'モデル']):
            change_model_mode(user_data)
        elif any(w in mode_choice for w in ['5', '終了', 'おわり']):
            speak("では、これで失礼いたしますね。どうぞ、お健やかにお過ごしください。", user_data["speech_speed"]); break
        else: speak("あら？ もう一度教えていただけますか。", user_data["speech_speed"])
        print("-" * 50)

if __name__ == "__main__":
    if not API_KEY or "AIzaSyC" not in API_KEY:
        print("エラー：コードの中の API_KEY を、ご自身のGemini APIキーに書き換えてください。")
    else:
        main()