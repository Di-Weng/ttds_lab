# -*- coding: utf-8 -*-
"""
-------------------------------
   Time    : 2019/10/18 21:37
   Author  : diw
   Email   : di.W@hotmail.com
   File    : train_inverted_index.py
   Desc: Given a specific xml, transforming it into a standard xml file, then output the inverted index to  index.txt.
        e.g python train_inverted_index.py --stopword englishST.txt --collection trec.5000.xml
        --stopword: the path of stopword
        --collection: trec xml file, not standard form. Similar to trec.5000.xml and trec.sample.xml
-------------------------------
"""

import xml.etree.ElementTree as ET
import re
import argparse
from stemming.porter2 import stem
from collections import defaultdict

parser = argparse.ArgumentParser(description='manual to this script')
parser.add_argument("--stopword", type=str, default="englishST.txt")
parser.add_argument("--collection", type=str, default='trec.5000.xml')

args = parser.parse_args()
stopword_path = args.stopword
trec_path = args.collection


def load_stopword(stopword_path):
    stopword_list = []
    with open(stopword_path, 'r',encoding='utf-8') as f1:
        stopword_list = [str(current_word).strip() for current_word in f1]
    return stopword_list

def tokenisation_text(text):
    # simply remove every non-letter character
    #     del_punc = r'[^A-Za-z0-9_-]' # keep _ -
    #     del_punc = r'[^A-Za-z0-9_-\']' #keep _ - '
    del_punc = r'[\W]'  # keep _

    text_nopunc = re.sub('&amp', ' ', text)
    text_nopunc = re.sub(del_punc, ' ', text)

    tokenisation_list = text_nopunc.split()
    return tokenisation_list


def lower_word(word_list):
    return [current_word.strip().lower() for current_word in word_list]


def token_lower_nostop_stem_list(all_text, stopword_list):
    token_list = tokenisation_text(all_text)
    token_lowerlist = lower_word(token_list)
    token_lowerlist_nostop = [str(current_word) for current_word in token_lowerlist if
                              str(current_word) not in stopword_list]
    stem_list = [stem(current_word) for current_word in token_lowerlist_nostop]

    return stem_list

def to_standard_xml(xml_file_path):
    new_file_name = 'standard_' + xml_file_path.split('/')[-1]

    with open(new_file_name,'w',encoding='utf-8') as new_file:
        with open(xml_file_path,'r') as original_file:
            new_file.write('<?xml version="1.0"?>\n')
            new_file.write('<sample>\n')
            for line in original_file:
                if(len(line.strip()) == 0):
                    continue
                new_file.write(line)
            new_file.write('</sample>')
    return new_file_name

def merge_text(text1,text2):
    merged_text = text1 + text2
    return merged_text

def xml_all_text(xml_file_path,stopword_list):
    # trec
    standard_xml_path = to_standard_xml(xml_file_path)
    tree = ET.parse(standard_xml_path)
    root = tree.getroot()
    all_text_list = [(child.find('DOCNO').text, token_lower_nostop_stem_list(merge_text(child.find('HEADLINE').text,child.find('TEXT').text), stopword_list)) for child in root.findall("./DOC")]

    return all_text_list


def inverted_index(all_text_list):
    '''
    return: # index dic[stem]={'doc_id':position}
    '''
    index_dic = defaultdict(dict)

    for current_doc_tupple in all_text_list:
        current_doc_id = current_doc_tupple[0]
        current_doc_text_list = current_doc_tupple[1]

        for index in range(len(current_doc_text_list)):
            current_stem = current_doc_text_list[index]
            if (current_doc_id not in index_dic[current_stem].keys()):
                index_dic[current_stem][current_doc_id] = [index + 1]
            else:
                index_dic[current_stem][current_doc_id].append(index + 1)

    return index_dic

def output_index(index_dic,file_path):
    sorted_index_dic_list = sorted(index_dic.items(),key=lambda x:x[0],reverse=False)
    with open(file_path,'w',encoding='utf-8') as file_1:
        for current_tupple in sorted_index_dic_list:
            current_stem = current_tupple[0]
            current_stem_doc_position_dic = current_tupple[1]
            file_1.write(current_stem)
            file_1.write(':\n')
            for current_doc_id,current_doc_id_position_list in current_stem_doc_position_dic.items():
                file_1.write('\t')
                file_1.write(str(current_doc_id))
                file_1.write(': ')
                current_doc_id_position_list_new = map(lambda x: str(x), current_doc_id_position_list)
                # print(','.join(current_doc_id_position_list_new))
                file_1.write(','.join(current_doc_id_position_list_new))
                file_1.write('\n')
            file_1.write('\n')

    return

stopword_list = load_stopword(stopword_path)

all_text_list = xml_all_text(trec_path,stopword_list)
index_dic = inverted_index(all_text_list)

output_index_path = 'index.txt'
output_index(index_dic,output_index_path)
