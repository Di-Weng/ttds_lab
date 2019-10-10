# -*- coding: utf-8 -*-
"""
-------------------------------
   Time    : 2019/9/30 9:36 AM
   Author  : diw
   Email   : di.W@hotmail.com
   File    : lab.py
   Desc:
-------------------------------
"""
import re
from stemming.porter2 import stem
import matplotlib.pyplot as plt
import numpy as np
from math import log
from scipy.optimize import curve_fit

bible_path = '../data/pg10.txt'
wiki_abstract = '../data/abstracts.wiki.txt'
stopword_filepath = '../data/englishST.txt'

def load_stopword(stopword_path):
    stopword_list = []
    with open(stopword_path, 'r',encoding='utf-8') as f1:
        stopword_list = [str(current_word).strip() for current_word in f1]
    return stopword_list

def tokenisation_text(text):
    del_punc = '\W'
    text_nopunc = re.sub(del_punc,' ',text)
    with open('a.txt','w+') as f1:
        f1.write(text_nopunc)
    tokenisation_list = text_nopunc.split()
    return tokenisation_list

def text_file(text_path):
    with open(text_path, 'r',encoding='utf-8') as file1:
        all_text = file1.read()
    return all_text

def lower_word(word_list):
    return [current_word.lower() for current_word in word_list]

def rank_stem(stem_list,rank = True):
    stem_count_dic = {}
    for current_stem in stem_list:
        if(current_stem not in stem_count_dic.keys()):
            stem_count_dic[current_stem] = 1
        else:
            stem_count_dic[current_stem] += 1
    if(not rank):
        return stem_count_dic
    else:
        stem_frequence_sorted = sorted(stem_count_dic.items(), key=lambda x: x[1], reverse=True)
    return stem_frequence_sorted

def draw_zipsLaw(stem_frequence_sorted):
    fig = plt.figure(figsize=[8,7])
    fig.suptitle('Zip\'s Law')
    ax = plt.subplot(1, 2, 1)
    frequence_rank = np.asarray([[i+1,stem_frequence_sorted[i][1]] for i in range(len(stem_frequence_sorted))])
    plt.plot(frequence_rank[:,0],frequence_rank[:,1])
    plt.axis('square')
    ax.set_xlabel('rank')
    ax.set_ylabel('frequence')

    ax = plt.subplot(1, 2, 2)
    logFrequence_logRank = np.asarray([[log(i + 1), log(stem_frequence_sorted[i][1])] for i in range(len(stem_frequence_sorted))])
    plt.plot(logFrequence_logRank[:, 0], logFrequence_logRank[:, 1])
    ax.set_xlabel('log_rank')
    ax.set_ylabel('log_frequence')
    plt.axis('square')
    plt.show()

    return

def count_firstdigit(stem_frequence_dic):
    digit_frequence_dic = {}
    for i in range(10):
        digit_frequence_dic[str(i)] = 0
    for current_frequence in stem_frequence_dic.values():
        digit_str = str(current_frequence)
        digit_frequence_dic[str(digit_str[0])] += 1

    return digit_frequence_dic

def draw_benfordLaw(firstdigit_dic):

    fig = plt.figure(figsize=[12,5])

    ax = plt.subplot(1, 2, 1)

    plt.bar(firstdigit_dic.keys(),firstdigit_dic.values())
    ax.set_xlabel('first digit')
    ax.set_ylabel('occurrence')

    ax = plt.subplot(1, 2, 2)
    temp_digit = []
    temp_occurence=[]
    for current_digit,current_occurence in firstdigit_dic.items():
        if(current_occurence >= 10):
            temp_digit.append(current_digit)
            temp_occurence.append(current_occurence)

    plt.bar(temp_digit,temp_occurence)
    ax.set_xlabel('first digit filtered')
    ax.set_ylabel('occurrence')

    plt.show()
    return

def heap_func(x, k, n):
    return k * pow(x,n)

def draw_heapLaw(token_lowerlist_nostop):
    y_list = []
    x_list = [i+1 for i in range(len(token_lowerlist_nostop))]
    vocabulary_set = set()
    previous_x = 0
    for current_word in token_lowerlist_nostop:
        if(current_word not in vocabulary_set):
            previous_x+=1
            vocabulary_set.add(current_word)
        y_list.append(previous_x)

    plt.figure(figsize=[6,6])
    plt.title('Heap\'s Law')
    plt.plot(x_list,y_list,'b',label='original count')

    popt, pcov = curve_fit(heap_func, x_list, y_list)
    plt.plot(x_list, heap_func(np.asarray(x_list), *popt), 'r-',label='fit function:k=%.3f n=%.3f'%tuple(popt))
    plt.legend()
    plt.show()

def token_lower_nostop_stem_list(all_text, stopword_list):
    token_list = tokenisation_text(all_text)
    token_lowerlist = lower_word(token_list)
    token_lowerlist_nostop = [str(current_word) for current_word in token_lowerlist if str(current_word) not in stopword_list]
    stem_list = [stem(current_word) for current_word in token_lowerlist_nostop]

    return stem_list

if __name__ == '__main__':
    stopword_list = load_stopword(stopword_filepath)

    all_text = text_file(bible_path)
    # all_text = text_file(wiki_abstract)

    token_list = tokenisation_text(all_text)
    token_lowerlist = lower_word(token_list)
    token_lowerlist_nostop = [current_word for current_word in token_lowerlist if current_word not in stopword_list]
    stem_list = [stem(current_word) for current_word in token_lowerlist_nostop]

    #zip's law
    # stem_frequence_sorted = rank_stem(stem_list)
    # draw_zipsLaw(stem_frequence_sorted)

    #Benford's law
    # stem_frequence_dic = rank_stem(stem_list,rank=False)
    # firstdigit_dic = count_firstdigit(stem_frequence_dic)
    # draw_benfordLaw(firstdigit_dic)

    #Heap's law
    draw_heapLaw(token_lowerlist_nostop)