from gtts import gTTS
import os
import pygame


def text_to_speech(text, lang='en', tld='com'):
    """
    將輸入的文字轉換為語音並播放。

    :param text: 要轉換的文字字串。
    :param lang: 語言代碼，如 'en' 表示英語，'zh-tw' 表示中文（台灣）。
    :param tld: 擇域名，如 'com' 用於大多數語言，'co.in' 特定於印度英語。
    """
    try:
        # 初始化pygame混音器
        pygame.mixer.init()
        # 生成語音
        tts = gTTS(text=text, lang=lang, tld=tld)
        # 暫存檔案名稱
        temp_file = "temp_audio.mp3"
        # 儲存語音檔案
        tts.save(temp_file)
        # 加載語音檔案
        pygame.mixer.music.load(temp_file)
        # 播放語音檔案
        pygame.mixer.music.play()
        # 等待播放完成
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        # 釋放資源
        pygame.mixer.music.unload()
        # 刪除暫存檔案
        os.remove(temp_file)
    except Exception as e:
        print(f"An error occurred: {e}")

import pyttsx3

def text_to_speech_with_adjustments(text):
    engine = pyttsx3.init()  # 初始化語音引擎

    # 調整語速
    rate = engine.getProperty('rate')  # 獲得當前語速
    engine.setProperty('rate', rate+50)  # 設置新的語速，減少50

    # 調整音調
    volume = engine.getProperty('volume')  # 獲得當前音量
    engine.setProperty('volume', volume+0.25)  # 提高音量

    # 調整音高
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)  # 更改語音

    # 說出文字
    engine.say(text)
    engine.runAndWait()  # 等待語音播報完成

# 範例文字
text_to_speech_with_adjustments('今天天氣不錯')





# 示例使用
text_to_speech("太扯啦", lang='zh-tw')

text_to_speech("Hello, how are you today?", lang='en')

text_to_speech('こんにちは、元気ですか？', lang='ja')