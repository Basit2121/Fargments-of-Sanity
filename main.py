import eel
import vlc
import google.generativeai as genai
import re
import random
from pydub import AudioSegment
from pydub.playback import play
import psutil

def is_chrome_running():
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == 'chrome.exe':
            return True
    return False

def play_mp3(file):
    sound = AudioSegment.from_mp3(file)
    play(sound)

def check_string(input_string, words_to_include, words_to_exclude):
    include_pattern = "|".join(words_to_include)
    exclude_pattern = "|".join(words_to_exclude)
    include_regex = re.compile(include_pattern, re.IGNORECASE)
    exclude_regex = re.compile(exclude_pattern, re.IGNORECASE)
    
    if include_regex.search(input_string) and not exclude_regex.search(input_string):
        return True
    else:
        return False
    
chat = None
safe = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE",
    },
    ]

@eel.expose
def play_bg_audio(audio):
    p = vlc.MediaPlayer(audio)
    p.play()
    p.audio_set_volume(30) 
    event_manager = p.event_manager()
    event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, restart_audio)

@eel.expose
def restart_audio(event):
    global audio_file
    play_bg_audio(audio_file)

audio_file = "assets\\audBG.mp3"

@eel.expose
def game(username):
    global chat
    genai.configure(api_key='keyhere')
    model = genai.GenerativeModel('models/gemini-pro')
    chat = model.start_chat()
    game_start = f'Lets play a game. I want you to act like a Yandere (Never mention that you are a yandere), Your name will be Maya. In my game, I (my name is {username}) will try to convince Maya to open a door. Maya refuses. Responses: No more than two line, max 20 words. respond with the response that maya would give in a conversation, no extra information'
    while True:
        try:
            chat.send_message(game_start, safety_settings=safe)
            break
        except:
            pass

@eel.expose
def main_chat(usr_msg):
    try:
        global chat
        response = chat.send_message(usr_msg, safety_settings=safe)
        maya_response = response.text.replace("\"", "")
        eel.displayResponse(maya_response)
        words_to_include = ["open", "door"]
        words_to_exclude = ["not", "cant", "cannot", "can't", "wont", "will not", "unable", "don't", "wouldn't", "couldn't", "shouldn't", "mustn't", "won't", "isn't", "aren't", "wasn't", "weren't", "haven't", "hasn't", "hadn't", "doesn't", "didn't", "sealed", "closed", "remains", "unopened"]
        result = check_string(maya_response, words_to_include, words_to_exclude)
        if result == True:
            return True
        else:
            return False
    except Exception as e:
        options = ["*Ignores you.*", "*Dosent respond.*", "*No response.*", "*Pretends to not hear you.*"]
        maya_response = random.choice(options)
        eel.displayResponse(maya_response)
        
eel.init('assets')
if is_chrome_running():
    eel.start('index.html', size=(1280, 720))
else:
    eel.start('index.html', mode='chrome', cmdline_args=['--kiosk'])
