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

def stop_voice(params):
    '''
    expected params :
    {
     "engine": obj :# pyttx3 engine object
    }
    '''
    global state
    if len(state["actions_queue"]) > 0:
        for _ in state["actions_queue"]:
            process, group_id, expected_seconds = state["actions_queue"].pop(0).values()
            process.kill()
        threads_to_pop = []
        for thread_idx, thread_ in enumerate(state["general_threads"]):
            if thread_.group_id == group_id:
                threads_to_pop.append(thread_idx)
        for count, thread_idx in enumerate(threads_to_pop):
            state["general_threads"].pop(thread_idx-count)



def read_all_paragraph(params):
    pass

def next_element(params):
    global state
    element_type = params["type"]
    validation_flag =  f"there_is_next{element_type}"
    if params[validation_flag]:
        del params[validation_flag]
        del params["group_id"]
        state.update(params)

def prev_element(params):
    global state
    element_type = params["type"]
    validation_flag =  f"there_is_prev{element_type}"
    if params[validation_flag]:
        del params[validation_flag]
        del params["group_id"]
        state.update(params)

def read_curr(params):
    global state
    wpm = 250
    process = subprocess.Popen(["say","-r",str(wpm), f"{params['sentence']}"])
    expected_seconds = (1.25)*60*len(params['sentence'].split(" "))/wpm  
    state['actions_queue'].append({
                        "process": process,
                        "group_id": params["group_id"],
                        "expected_seconds": expected_seconds
                        })
    return process 

def load_book(book_filepath):
    with open(book_filepath) as inpf:
        d = json.load(inpf)
    return d 

def get_user_input():
    print("waiting for input")
    i, o, e = select.select( [sys.stdin], [], [], 1 )
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
    group_id = uuid.uuid4()
    if user_input == "s": # stop
        params = {
                "group_id": group_id,
                "user_request_code": "s",
                "actions_queue": state["actions_queue"]
        }
    if user_input == "r": # read
        current_sentence = book[current_chapter]["sections"][current_section]\
                                                ["paragraphs"][current_paragraph]\
                                                ["sentences"][current_sentence]["text"]
        params = {
                "group_id": group_id,
                "user_request_code": "r",
                "sentence": current_sentence,
                "queue": state["actions_queue"],
        }
    if user_input == "rap": # read all paragraph
        params = []
        paragraph_sentences = book[current_chapter]["sections"][current_section]\
                                                ["paragraphs"][current_paragraph]\
                                                ["sentences"]
        for sentence_idx, sentence in enumerate(paragraph_sentences):
            params.append({
                    "group_id": group_id,
                    "user_request_code": "r",
                    "sentence": sentence["text"]
            })
            if sentence_idx < len(paragraph_sentences) - 1:
                params.append({
                    "type": "Sentence",
                    "group_id": group_id,
                    "user_request_code": "ns",
                    "there_is_nextSentence": True, 
                    "sentence": sentence["text"],
                    "current_sentence": sentence_idx + 1
                })
    if user_input == "ps": # prev sentence
        if state["current_sentence"] >= 1:
            params = {
                    "type": "Sentence",
                    "group_id": group_id,
                    "user_request_code": "ps",
                    "there_is_prevSentence": True, 
                    "current_sentence": state["current_sentence"] - 1
            }
        else:
            params = {
                    "type": "Sentence",
                    "group_id": group_id,
                    "user_request_code": "ps",
                    "there_is_prevSentence": False, 
                    "current_sentence": state["current_sentence"]
            }
    if user_input == "ns": # next sentence
        if (state["current_sentence"] + 1) < len(book[current_chapter]["sections"][current_section]\
                                                                      ["paragraphs"][current_paragraph]\
                                                                      ["sentences"]):
            params = {
                    "type": "Sentence",
                    "group_id": group_id,
                    "user_request_code": "ns",
                    "there_is_nextSentence": True, 
                    "current_sentence": state["current_sentence"] + 1
            }
        else:
            params = {
                    "type": "Sentence",
                    "group_id": group_id,
                    "user_request_code": "ns",
                    "there_is_nextSentence": False, 
                    "current_sentence": state["current_sentence"]
            }
    if user_input == "np": # next paragraph
        if (state["current_paragraph"] + 1) < len(book[current_chapter]["sections"][current_section]\
                                                                      ["paragraphs"]):
            params = {
                    "type": "Paragraph",
                    "group_id": group_id,
                    "user_request_code": "np",
                    "there_is_nextParagraph": True, 
                    "current_paragraph": state["current_paragraph"] + 1,
                    "current_sentence": 0
            }
        else:
            params = {
                    "type": "Paragraph",
                    "group_id": group_id,
                    "user_request_code": "np",
                    "there_is_nextParagraph": False, 
                    "current_paragraph": state["current_paragraph"],
                    "current_sentence": state["current_sentence"]
            }
    if user_input == "nc": # next seCtion
        if (state["current_section"] + 1) < len(book[current_chapter]["sections"]):
            params = {
                    "type": "Section",
                    "group_id": group_id,
                    "user_request_code": "nc",
                    "there_is_nextSection": True, 
                    "current_section": state["current_section"] + 1,
                    "current_paragraph": 0,
                    "current_sentence": 0
            }
        else:
            params = {
                    "type": "Section",
                    "group_id": group_id,
                    "user_request_code": "nc",
                    "there_is_nextSection": False, 
                    "current_section": state["current_section"],
                    "current_paragraph": state["current_paragraph"],
                    "current_sentence": state["current_sentence"]
            }
    return state, params

def init_app():
    global state
    book_filepath = f"./books/{state['book_name']}"
    prev_lastChanged_epoctime = os.path.getmtime(book_filepath)
    state["book"] = load_book(book_filepath)
    while True:
        time.sleep(0.1)
        print([thread.name for thread in threading.enumerate()]);
        print(state["current_section"],state["current_paragraph"],state["current_sentence"])
        curr_lastChanged_epoctime = os.path.getmtime(book_filepath)
        if curr_lastChanged_epoctime > prev_lastChanged_epoctime:
            state["book"] = load_book(book_filepath)
        given_user_input = get_user_input()

        if given_user_input and commands.get(given_user_input,False):
          state, params = get_params(given_user_input, state)
          threads = []
          if isinstance(params, dict):
              user_request_code = params.pop("user_request_code")
              thread_ = threading.Thread(target=commands[user_request_code],kwargs={'params':params},daemon=True)
              thread_.group_id = params["group_id"] 
              threads.append(thread_)
          if isinstance(params, list):
            for params_dict in params:
              user_request_code = params_dict.pop("user_request_code")
              thread_ = threading.Thread(target=commands[user_request_code],kwargs={'params':params_dict},daemon=True)
              thread_.group_id = params_dict["group_id"]  
              threads.append(thread_)
          print(f"given : {given_user_input}")
          if given_user_input == "s":
              for thread_ in threads:
                  state["stop_threads"].append(thread_)
          else:
              for thread_ in threads:
                  state["general_threads"].append(thread_)

        if len(state["stop_threads"]) > 0:
            next_action = state["stop_threads"].pop(0)
            next_action.start()

        elif len(state["actions_queue"]) > 0:
            for i in range(len(state["actions_queue"])):
                process_, group_id, remaining_seconds = state["actions_queue"][i].values()
                state["actions_queue"][i] = {
                        "process": process_,
                        "group_id": group_id,
                        "expected_seconds": remaining_seconds-1.1}
            for idx, action_dict  in enumerate(state["actions_queue"]):
                process_, group_id, remaining_seconds = action_dict.values()
                if remaining_seconds < 0:
                    process_.kill()
                    state["actions_queue"].pop(idx)

        elif len(state["general_threads"]) > 0:
            next_action = state["general_threads"].pop(0)
            next_action.start()

if __name__ == "__main__":
    book_name = sys.argv[1]
    actions_queue = []
    user_inputs = []
    commands = {
            "r": read_curr,
            "rap": read_all_paragraph,
            "ps": prev_element,
            "ns": next_element,
            "np": next_element,
            "nc": next_element,
            "s": stop_voice,
            }
    state = {
            "engine": pyttsx3.init(),
            "book_name": book_name,
            "actions_queue": [],
            "general_threads": [],
            "stop_threads": [],
            "user_requests": [],
            "commands": commands,
            "current_chapter" : 0,
            "current_section" : 0,
            "current_paragraph" : 0,
            "current_sentence" : 0
            }
    init_app()
    #d = json.load(open("GEC"))
    
