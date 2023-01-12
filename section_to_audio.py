import json
import pyttsx3
import time 
import sys
import os

books_folder, book_name, chapter_name = sys.argv[1].split("/")
filename =  chapter_name 
with open(f"./{books_folder}/{book_name}/{chapter_name}/{filename}.json") as inpf:
    data = json.load(inpf) 
    first_chapter = data[0]
    for section_idx, section in enumerate(first_chapter["sections"]):
        section_idx = str(section_idx).zfill(3)
        for p_idx, paragraph in enumerate(section["paragraphs"]):
            for s_idx, sentence in enumerate(paragraph["sentences"]):
                padded_p_idx, padded_s_idx = str(p_idx).zfill(3), str(s_idx).zfill(3)
                print(sentence["text"])
                engine = pyttsx3.init()
                #engine.say(sentence["text"])
                os.makedirs(f"audios/{book_name}/{chapter_name}", exist_ok=True)
                engine.save_to_file(sentence["text"], f"audios/{book_name}/{chapter_name}/section_{section_idx}_{padded_p_idx}_{padded_s_idx}.wav")
                engine.runAndWait()
                del engine
