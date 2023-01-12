import pyttsx3
import json
import os
import sys
import time
import keyboard
import concurrent.futures
import threading
import sys, select
import subprocess
import uuid
import pyperclip
from nltk import tokenize

def track_clipboard_change():
    #previous_clipboard = pyperclip.paste()
    #current_clipboard = previous_clipboard
    pyperclip.copy("")
    current_clipboard = ""
    while current_clipboard == "":# == previous_clipboard: 
        time.sleep(1)
        current_clipboard = pyperclip.paste() 
    mode = "w"
    with open("read_buffer",mode) as bufferf:
        bufferf.write(current_clipboard)
    pyperclip.copy("")
    return current_clipboard

def read_sent(sent,voice,wpm):
    process = subprocess.Popen(["say","-v",f"{voice}","-r",str(wpm), f"{sent}"])
    sent = "".join([char_ if ord(char_) < 128 else " " for char_ in sent ])
    expected_seconds = (1.7)*60*len(sent.split(" "))/wpm  
    return process, expected_seconds 

if __name__ == "__main__":
    choice = None
    # spanish voices 
    # ['com.apple.speech.synthesis.voice.diego', 'com.apple.speech.synthesis.voice.jorge', 'com.apple.speech.synthesis.voice.juan', 'com.apple.speech.synthesis.voice.monica', 'com.apple.speech.synthesis.voice.paulina']
    # selected_id = "com.apple.speech.synthesis.voice.paulina"
    # selected_voice = [v for v in engine.getProperty("voices") if v.id == selected_id][0]
    # Lekha
    selected_voice = "victoria"
    wpm = 150 

    while True:
        time.sleep(1)
        track_clipboard_change()

        with open("read_buffer") as inpf:
            paragraph = ""
            for line in inpf:
                paragraph+=line.strip().replace("\n","")
            sentences = tokenize.sent_tokenize(paragraph)
            if not paragraph:
                exit()

        print(sentences)
        choice = "1"#input(f"add as\n1-sentence\n2-paragraph\n3-section\n4-Accumulate Buffer")
        if(choice == "1"): 
            for sent in sentences:
                process, expected_seconds = read_sent(sent, voice=selected_voice, wpm=wpm)
                time.sleep(expected_seconds)

        with open("read_buffer","w") as cleanf:
            pass
