import json
from nltk import tokenize
import pyperclip
import time
import pyttsx3
import json
import os
import sys
def track_clipboard_change(prev_choice):
    previous_clipboard = pyperclip.paste()
    current_clipboard = previous_clipboard
    while current_clipboard == previous_clipboard: 
        time.sleep(1)
        current_clipboard = pyperclip.paste() 
    if prev_choice == "4":
        mode = "a"
    else:
        mode = "w"
    with open("buffer",mode) as bufferf:
        bufferf.write(current_clipboard)
    return current_clipboard



if __name__ == "__main__":
    filename = sys.argv[1]
    print("confirm filename",filename)
    input("confirm?")
    choice = None
    engine = pyttsx3.init()
    book_filepath = filename
    chapters = json.load(open(book_filepath))

    while True:
        time.sleep(1)
        track_clipboard_change(choice)

        with open("buffer") as inpf:
            paragraph = ""
            for line in inpf:
                paragraph+=line.replace("\n","")
            sentences = tokenize.sent_tokenize(paragraph)
            '''
            for sent in sentences:
                engine.say(sent)
                engine.runAndWait()
            '''
            if not paragraph:
                exit()

        print(sentences)
        choice = input(f"add as\n1-sentence\n2-paragraph\n3-section\n4-Accumulate Buffer")
        if(choice == "1"): 
            sentence = ".".join(sentences)
            chapters[-1]["sections"][-1]["paragraphs"][-1]["sentences"].append({
                    "type":"sentence",
                    "text": sentence 
                })
        elif(choice == "2"): 
            chapters[-1]["sections"][-1]["paragraphs"].append({
                    "type":"paragraph",
                    "sentences": [{
                        "type": "sentence",
                        "text":sent 
                        } for sent in sentences]
                })

        elif(choice == "3"): 
            title= ".".join(sentences)
            chapters[-1]["sections"].append({
                    "type":"section",
                    "title": title,
                    "paragraphs": []
                })
        elif(choice == "4"):
            continue
        with open(book_filepath,"w") as outf:
            outf.write(json.dumps(chapters, indent=4))
        with open("buffer","w") as cleanf:
            pass
