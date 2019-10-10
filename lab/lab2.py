# -*- coding: utf-8 -*-
"""
-------------------------------
   Time    : 2019/10/7 9:44 AM
   Author  : diw
   Email   : di.W@hotmail.com
   File    : lab2.py
   Desc:
-------------------------------
"""
import lab1
from lab1 import token_lower_nostop_stem_list,load_stopword
import xml.etree.ElementTree as ET

is_sample = 1
data_folder = '../data/collections/'
sample_txt_path = '../data/collections/sample.txt'
trec_samle_path = '../data/collections/trec.sample.xml'
sample_xml_path = '../data/collections/sample.xml'
stopword_filepath = '../data/englishST.txt'

def to_standard_xml(xml_file_path):
    new_file_name = 'standard_' + xml_file_path.split('/')[-1]
    new_file_path = data_folder + new_file_name

    with open(new_file_path,'w',encoding='utf-8') as new_file:
        with open(xml_file_path,'r') as original_file:
            new_file.write('<?xml version="1.0"?>\n')
            new_file.write('<sample>\n')
            for line in original_file:
                if(len(line.strip()) == 0):
                    continue
                new_file.write(line)
            new_file.write('</sample>')
    return new_file_path

def xml_sample(xml_file_path):
    tree = ET.parse(trec_samle_path)
    root = tree.getroot()
    return root

def output_index(index_dic,file_path):
    with open(file_path,'w',encoding='utf-8') as file_1:
        for current_stem,current_stem_doc_position_dic in index_dic.items():
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

if __name__ == '__main__':
    stopword_list = load_stopword(stopword_filepath)

    #for txt file
    # all_text = lab1.text_file(lab1.bible_path)
    # stem_token = token_lower_nostop_stem_list(all_text,stopword_list)

    #for xml file
    if(is_sample):
        # sample
        standard_xml_path = to_standard_xml(sample_xml_path)
        tree = ET.parse(standard_xml_path)
        root = tree.getroot()
        all_text_list = [token_lower_nostop_stem_list(child.text,stopword_list) for child in root.findall("./DOC/Text")]
    else:
        # trec
        standard_xml_path = to_standard_xml(trec_samle_path)
        tree = ET.parse(standard_xml_path)
        root = tree.getroot()
        all_text_list = [token_lower_nostop_stem_list(child.text,stopword_list) for child in root.findall("./DOC/TEXT")]

    stem_set = set()
    for current_doc in all_text_list:
        for current_stem in current_doc:
            stem_set.add(current_stem)

    # index index[stem]={'doc_id':position}
    index_dic = {}
    for current_stem in stem_set:
        current_stem_doc_position_dic = {}
        for doc_id in range(len(all_text_list)):
            current_doc_text_list = all_text_list[doc_id]
            if(current_stem not in current_doc_text_list):
                continue

            position_list = [index for index in range(len(current_doc_text_list))
                              if current_doc_text_list[index]==current_stem ]
            current_stem_doc_position_dic[doc_id] = position_list
        index_dic[current_stem] = current_stem_doc_position_dic

    #output sample
    if(is_sample):
        output_path = '../data/collections/sample.index'
    else:
        output_path = '../data/collections/trec.index'
    output_index(index_dic,output_path)