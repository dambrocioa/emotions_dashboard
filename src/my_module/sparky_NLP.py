from nltk.corpus import PlaintextCorpusReader
import pandas as pd
import datetime
import glob
import os
from glob import iglob
import pytz

#to clean text
from spanlp.palabrota import Palabrota
from spanlp.domain.countries import Country
from spanlp.domain.strategies import JaccardIndex, Preprocessing, RemoveUnicodeCharacters, TextToLower, RemoveAccents, RemoveExtraSpaces

def get_sequence_of_odd_numbers(num):
    # returns list of first odd numbers smaller than num
    ODD = []
    for i in range(num):
        if i % 2 == 1:
            ODD.append(i)
    return ODD

# Function to handle BACKSPACE
def handle_backspace(S):
    q = []
    S = S.replace("[BACKSPACE]","#")
    for i in range(0, len(S)):
 
        if S[i] != '#':
            q.append(S[i])
        elif len(q) != 0:
            q.pop()
 
    # Build final string
    ans = ""
 
    while len(q) != 0:
        ans += q[0]
        q.pop(0)
 
    # return final string
    return ans


def format_message(message,list_characters,len_pattern):
    print("LIST CHARACTERS: ",list_characters)
    text_to_display = []
    S = message

    for item in list_characters[:-1]:
        Min = item[0]
        max_local = item[1] 
        Max = item[1]+len_pattern

        text_to_display.append(S[Min:max_local])
        text_to_display.append(tuple([S[max_local:Max],"","#fea"]))
    text_to_display.append(S[list_characters[-1][0]:list_characters[-1][1]])
    print("TEXT TO DISPLAY: ",text_to_display)
    return text_to_display

def get_characters(clean_string,clean_pattern):
    l = clean_string.split(clean_pattern)
    odd_sequence = get_sequence_of_odd_numbers(num=len(l))
    
    min = 0
    list_characters = []
    for item in l:
        list_characters.append(tuple([min,min+len(item)]))
        min = min+len(item)+len(clean_pattern)

    return list_characters

def find_pattern(message,patterns_to_find,strategies,message_type):
    occurrences_found = {}
    #string_lower = S.lower()
    #strategies = [TextToLower(),RemoveAccents()]
    
    if message_type != "cleaned_message":
        message = Preprocessing().clean(data=message, clean_strategies=strategies)
    
    for pattern in patterns_to_find:
        clean_pattern = Preprocessing().clean(data=pattern, clean_strategies=strategies)
        print("pattern: ",clean_pattern)
        if clean_pattern in message:
            print("message: ",message)
            print("clean_pattern :",clean_pattern)
            list_characters = get_characters(message,clean_pattern)
            message_formatted = format_message(message=message,list_characters=list_characters,len_pattern=len(clean_pattern))
            occurrences_found[pattern] = message_formatted
    return occurrences_found

def clean_and_detect_matches(data,strategies):
    #strategies = [RemoveUnicodeCharacters(),TextToLower(),RemoveAccents(),RemoveExtraSpaces()]
    #strategies = [TextToLower(),RemoveAccents(),RemoveUnicodeCharacters(),RemoveExtraSpaces()]
    
    corpus = []
    try:
        for index, row in data.iterrows():
            result = {"user":row["user"],"user_name":row["user_name"],"date":row["start_time"],"short_date":row["short_start_time"],"week_info":row["week_info"],"original_message":row["words"]}
            
            file_words = row["words"]
            #print('A: ',file_words)
            #file_words = file_words.replace("[ENTER]","")
            file_words = file_words.replace("[CTRL]","")
            file_words = file_words.replace("[ESC]","")            
            file_words = file_words.replace("[FLECHA_DERECHA]","")
            file_words = file_words.replace("[FLECHA_IZQUIERDA]","")
            file_words = file_words.replace("[FLECHA_ABAJO]","")
            file_words = file_words.replace("[FLECHA_ARRIBA]","")
            file_words = file_words.replace("[MAYUSCULAS]","")
            file_words = file_words.replace("[MINUSCULAS]","")
            file_words = file_words.replace("[RIGHT_SHIFT]","")
            file_words = file_words.replace("[CTRL_DERECHA]","")
            file_words = file_words.replace("[ALT]","")
            file_words = file_words.replace("[[SUPR]]","")
            file_words = file_words.replace("[TAB]","")
            file_words = file_words.replace("[ALT_GR]","")
            file_words = file_words.replace("[BLOQ_MAYUS]","")
            file_words = file_words.replace("[WINDOWS_IZQUIERDA]","")
            file_words = file_words.replace("\\xb4a","a")
            file_words = file_words.replace("\\xb4e","e")
            file_words = file_words.replace("\\xb4i","i")  
            file_words = file_words.replace("\\xb4o","o")
            file_words = file_words.replace("\\xb4u","u")
            file_words = file_words.replace("\\xb4A","a")
            file_words = file_words.replace("\\xb4E","e")
            file_words = file_words.replace("\\xb4I","i")  
            file_words = file_words.replace("\\xb4O","o")
            file_words = file_words.replace("\\xb4U","u")
            file_words = file_words.replace("\\xf1","ñ")
            file_words = file_words.replace("\\r"," ")
            file_words = file_words.replace("\\n"," ")
            file_words = file_words.replace("\r"," ")
            file_words = file_words.replace("\n"," ")
            file_words = handle_backspace(file_words)
            print('B: ',file_words)
            result['cleaned_message'] = Preprocessing().clean(data=file_words, clean_strategies=strategies)
            corpus.append(result)
        
        return corpus
    except Exception as e:
        print(e)
        raise

def detect_issues(corpus,patterns_to_find,size,strategies):
    #jaccard = JaccardIndex(threshold=0.7, normalize=False, n_gram=1)
    #palabrota = Palabrota(distance_metric=jaccard)
    palabrota = Palabrota(countries=[Country.MEXICO],exclude=["cono"])
    len_corpus = len(corpus)
    bad_words_detected = []
    patterns_detected = {}
    patterns_occurrences = {}


    for n,element in enumerate(corpus):
        #DETECTING BAD WORDS IN SPANISH (THIS METHOD IS NOT PERFECT)
        #funciona mejor con solo minúsculas y sin acentos
        
        cleaned_message = element["cleaned_message"]


        min_index=max(0,n-size)
        max_index=min(len_corpus,n+size)

        print("n: ",n)
        print("min_index: ",min_index)
        print("max_index:",max_index )
        
        #lines_before = str(data_into_list[min_index:index_pattern_found]).replace("b\\'","").replace("\\'","").replace("[","").replace("]","").replace("\\","").replace('\"','').replace(",","").replace("\'","")
        #lines_after = str(data_into_list[index_pattern_found:max_index]).replace("b\\'","").replace("\\'","").replace("[","").replace("]","").replace("\\","").replace('\"','').replace(",","").replace("\'","")

        lines_before_raw = [item["cleaned_message"] for item in corpus[min_index:n]]
        lines_after_raw = [item["cleaned_message"] for item in corpus[n:max_index]]

        lines_before = ''
        for item in lines_before_raw:
            lines_before = lines_before +item

        lines_after = ''
        for item in lines_after_raw:
            lines_after = lines_after + item

        print('cleaned_message: ',cleaned_message)
        
        try:
            if len(cleaned_message)>=4:
                palabrota_found = palabrota.contains_palabrota(cleaned_message)
                if palabrota_found:
                    bad_words_detected.append({"cleaned_message":cleaned_message,"lines_before":lines_before,"lines_after":lines_after})
        except:
            print("help")
            #import code; code.interact(local=locals())
            raise
        #DETECTING PATTERNS
        """
        patterns_occurrences = {"pattern":n_ocurrences,...}
        patterns_detected    = {"pattern"=[{occurrence details},{occurrence details},{occurrence details},...]}
        """

        detected = find_pattern(cleaned_message,patterns_to_find,strategies,message_type="cleaned_message")
        print("detected: ",detected)
        if len(detected)>0:
            for pattern in detected:
                if pattern not in patterns_detected.keys():
                    patterns_detected[pattern] = []
                patterns_detected[pattern].append({"pattern":pattern,"original_message":element["original_message"],"cleaned_message":cleaned_message,"lines_before":lines_before,"lines_after":lines_after,"message_formatted":detected[pattern],"date":element["date"],"short_date":element["short_date"],"week_info":element["week_info"]})
                if pattern not in patterns_occurrences.keys():
                    patterns_occurrences[pattern] = 0
                patterns_occurrences[pattern] = patterns_occurrences[pattern]+1
        #DETECTING PERSON NAMES
    return patterns_detected,patterns_occurrences,

def get_ocurrences(data,patterns_to_find,size):
    strategies = [TextToLower(),RemoveAccents(),RemoveUnicodeCharacters(),RemoveExtraSpaces()]
    print("AA patterns_to_find: ",patterns_to_find)
    #read files, clean text 
    corpus = clean_and_detect_matches(data,strategies)
    print("corpus",corpus)
    
    #detect_matches
    print("patterns_to_find:",patterns_to_find)
    patterns_detected,patterns_occurrences = detect_issues(corpus,patterns_to_find,size,strategies)

    return corpus,patterns_detected,patterns_occurrences#,bad_words_detected

def test_func():
    result = [("suelo", "ocurrencia","#fea"),("accidente", "ocurrencia","#8ef")]
    return result
