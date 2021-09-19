import pyttsx3
import json
import os
import sys
import time
import keyboard
import threading
import sys, select
def speaking_proc(sentence):
    engine = pyttsx3.init()
    engine.say(sentence)
    engine.runAndWait()

def startSpeaking(sentence):
    p = multiprocessing.Process(target=speaking_proc, args=(sentence, ))
    p.start()
    while p.is_alive():
            if keyboard.is_pressed('q'):
                    p.terminate()
            else:
                    continue
    p.join()

def stop_voice(params):
      params["engine"].stop()

def read_curr(params):
    '''
    expected params :
    {
     "sentence": '' # string
    }
    '''
    engine = params["engine"]
    try:
        engine.endLoop()
    except:
        pass
    engine.say(params["sentence"])
    engine.runAndWait()

def next_sentence(params):
    pass

def previous_sentence(params):
    pass
    
def next_paragraph(params):
    pass

def next_section(params):
    pass

def load_book(book_filepath):
    with open(book_filepath) as inpf:
        d = json.load(inpf)
    return d 

def get_user_input():
    print("waiting for input")
    i, o, e = select.select( [sys.stdin], [], [], 5 )
    if (i):
      user_action = sys.stdin.readline().strip()
      return user_action
    else:
      return None

def get_params(user_input, state):
    s = state
    book = state["book"]
    current_chapter = state["current_chapter"]
    current_section = state["current_section"]
    current_paragraph = state["current_paragraph"]
    current_sentence = state["current_sentence"]
    if user_input == "s": # stop
        params = {
                "engine": state["engine"]
        }
    if user_input == "r": # read
        current_sentence = book[current_chapter]["sections"][current_section]\
                                                ["paragraphs"][current_paragraph]\
                                                ["sentences"][current_sentence]["text"]
        params = {
                "sentence": current_sentence,
                "engine": state["engine"]
        }
    if user_input == "ns": # next sentence
        if (state["current_sentence"] + 1) < len(book[current_chapter]["sections"][current_section]\
                                                                      ["paragraphs"][current_paragraph]\
                                                                      ["sentences"]):
            state["current_sentence"] += 1
        else:
            read_curr({
                "sentence": "last sentence on the paragraph."
                })
        params = {}
    if user_input == "ps": # prev sentence
        if state["current_sentence"] >= 1:
            state["current_sentence"] -= 1
        else:
            read_curr({
                "sentence": "first sentence on the paragraph."
                })
        params = {}
    if user_input == "np": # next paragraph
        if (state["current_paragraph"] + 1) < len(book[current_chapter]["sections"][current_section]\
                                                                      ["paragraphs"]):
            state["current_paragraph"] += 1
            state["current_sentence"] = 0 
        else:
            read_curr({
                "sentence": "last paragraph on the section."
                })
        params = {}
    if user_input == "nc": # next seCtion
        if (state["current_section"] + 1) < len(book[current_chapter]["sections"]):
            state["current_section"] += 1
            state["current_paragraph"] = 0
            state["current_sentence"] = 0
        else:
            read_curr({
                "sentence": "last section on the chapter."
                })
        params = {}
    return state, params

def init_app(state):
    book_filepath = f"./books/{state['book_name']}"
    prev_lastChanged_epoctime = os.path.getmtime(book_filepath)
    state["book"] = load_book(book_filepath)
    while True:
        time.sleep(0.1)
        print([thread.name for thread in threading.enumerate()]);
        curr_lastChanged_epoctime = os.path.getmtime(book_filepath)
        if curr_lastChanged_epoctime > prev_lastChanged_epoctime:
            state["book"] = load_book(book_filepath)
        given_user_input = get_user_input()
        if given_user_input and commands.get(given_user_input,False):
          print(f"given : {given_user_input}")
          state, params = get_params(given_user_input, state)

          thread_ = threading.Thread(target=commands[given_user_input],kwargs={'params':params})
          thread_.start()
if __name__ == "__main__":
    book_name = sys.argv[1]
    actions_queue = []
    user_inputs = []
    commands = {
            "r": read_curr,
            "ns": next_sentence,
            "ps": previous_sentence,
            "np": next_paragraph,
            "nc": next_section,
            "s": stop_voice,
            }
    state = {
            "engine": pyttsx3.init(),
            "book_name": book_name,
            "actions_queue": actions_queue,
            "user_inputs": user_inputs,
            "commands": commands,
            "current_chapter" : 0,
            "current_section" : 0,
            "current_paragraph" : 0,
            "current_sentence" : 0
            }
    init_app(state)
    #d = json.load(open("GEC"))
    
