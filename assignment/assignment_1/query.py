# -*- coding: utf-8 -*-
"""
-------------------------------
   Time    : 2019/10/18 21:53
   Author  : diw
   Email   : di.W@hotmail.com
   File    : query.py
   Desc: loading a inverted index file then output the query result from queries.boolean.txt and queries.ranked.txt, output the results.boolean.txt and results.ranked.txt respectively.
   you could at most specify two files, but at least one files.
    python query.py --stopword englishST.txt --q1 queries.boolean.txt --q2 queries.ranked.txt

-------------------------------
"""
import argparse
from collections import defaultdict
from math import log10
from stemming.porter2 import stem
import re

parser = argparse.ArgumentParser(description='manual to this script')
parser.add_argument("--stopword", type=str, default="englishST.txt")
parser.add_argument("--index", type=str, default="index.txt")
parser.add_argument("--q1", type=str, default='')
parser.add_argument("--q2", type=str, default='')

args = parser.parse_args()
stopword_path = args.stopword
inverted_index_path = args.index
query_file_list = []
query_file_list.append(args.q1)

if(len(args.q1)):
    query_file_list.append(args.q1)

if(len(args.q2)):
    query_file_list.append(args.q2)

# if not specify any file, raise an error.
if(len(args.q1)==len(args.q2)==0):
    raise RuntimeError('At least specify one query file!')

# load stop word
def load_stopword(stopword_path):
    stopword_list = []
    with open(stopword_path, 'r',encoding='utf-8') as f1:
        stopword_list = [str(current_word).strip() for current_word in f1]
    return stopword_list

# load inverted index
def load_inverted_index(index_path):
    result_inverted_index = {}
    with open(index_path, 'r') as f1:
        for line in f1:
            line = line.strip()
            if (line.endswith(':')):
                current_stem = line.replace(':', '')
                result_inverted_index[current_stem] = {}
                continue

            if (len(line) == 0):
                continue

            temp_split_list = line.split(': ')
            current_doc_id, str_position_list = temp_split_list[0], temp_split_list[1]
            current_position_list = [int(current_position) for current_position in str_position_list.split(',')]
            result_inverted_index[current_stem][current_doc_id] = current_position_list
    return result_inverted_index


def get_doc_id_set(current_inverted_dic):
    doc_id_set = set()
    for current_stem, current_doc_position_dic in current_inverted_dic.items():
        for current_doc_id in current_doc_position_dic.keys():
            doc_id_set.add(str(current_doc_id))
    return doc_id_set


def query_word(current_inverted_dic, current_word, is_not=0):
    current_word_stem = stem(current_word.strip().lower())
    if (is_not):
        for current_index_stem, current_index_stem_position in current_inverted_dic.items():
            if (current_word_stem == current_index_stem):
                doc_id_set = get_doc_id_set(current_inverted_dic)
                stem_doc_list = set(current_index_stem_position.keys())
                return list(doc_id_set.difference(stem_doc_list))
    else:
        for current_index_stem, current_index_stem_position in current_inverted_dic.items():
            if (current_word_stem == current_index_stem):
                return list(current_index_stem_position.keys())
    #     raise RuntimeError('Query not found.')
    return []


# OR
def union_list(a, b):
    result_list = list(set(a).union(set(b)))
    result_list.sort(key=lambda i: int(i))
    return result_list


# AND
def intersection_list(a, b):
    result_list = list(set(a).intersection(set(b)))
    result_list.sort(key=lambda i: int(i))
    return result_list


def probability_query(doc_word_pos1, doc_word_pos2, current_distance, is_phrase=0):
    result_list = []
    for current_docid_1, current_positionlist_1 in doc_word_pos1.items():
        if (current_docid_1 not in doc_word_pos2.keys()):
            continue
        current_positionlist_2 = doc_word_pos2[current_docid_1]
        i = 0
        j = 0

        while ((i <= len(current_positionlist_1) - 1) and (j <= len(current_positionlist_2) - 1)):
            if (is_phrase):
                if (int(current_positionlist_1[i]) > int(current_positionlist_2[j]) - current_distance):
                    j += 1
                    continue
                elif (int(current_positionlist_1[i]) < int(current_positionlist_2[j]) - current_distance):
                    i += 1
                    continue
                else:
                    result_list.append(current_docid_1)
                    break
            else:
                if (int(current_positionlist_1[i]) > int(current_positionlist_2[j]) + current_distance):
                    j += 1
                    continue
                elif (int(current_positionlist_1[i]) < int(current_positionlist_2[j]) - current_distance):
                    i += 1
                    continue
                else:
                    result_list.append(current_docid_1)
                    break
    return result_list


# phrase
def phrase_query(current_inverted_dic, query_phrase):
    phrase_list = [stem(current_word.lower().strip()) for current_word in query_phrase.replace('"', '').split()]
    result_list = probability_query(current_inverted_dic[phrase_list[0]], current_inverted_dic[phrase_list[1]], 1,
                                    is_phrase=1)
    return result_list


def boolean_query(current_inverted_dic, current_query_word):
    is_NOT = 0
    # whether contains NOT
    if (current_query_word.startswith('NOT')):
        is_NOT = 1
        current_query_word = current_query_word.replace('NOT', '').strip()

    if (current_query_word.startswith('"') and current_query_word.endswith('"')):
        result_list = phrase_query(current_inverted_dic, current_query_word)

    elif (current_query_word.startswith('#')):
        current_query_word_list = current_query_word.split('(')
        current_word_distance = int(current_query_word_list[0].replace('#', '').strip())
        current_query_stem_list = [stem(temp_word.strip()) for temp_word in
                                   current_query_word_list[1].replace(')', '').split(',')]
        result_list = probability_query(current_inverted_dic[current_query_stem_list[0]],
                                        current_inverted_dic[current_query_stem_list[1]], current_word_distance)
    else:
        result_list = query_word(current_inverted_dic, current_query_word)

    # if contains NOT, get the difference set of the result_list from the doc_id_set
    if (is_NOT):
        doc_id_set = get_doc_id_set(current_inverted_dic)

        result_list = list(doc_id_set.difference(set(result_list)))

    return result_list



# tf-idf
def tf_idf_weight(current_inverted_dic, query_phrase, is_stop=0, stop_word_path=None):
    # doc_tfidf['doc_id'] = tf_idf
    doc_tfidf = defaultdict(int)

    # N
    doc_number = len(get_doc_id_set(current_inverted_dic))

    if (is_stop == 0):
        stem_word_list = [stem(current_query_word.strip().lower()) for current_query_word in query_phrase.split()]
    else:
        stopword_list = load_stopword(stop_word_path)
        stem_word_list = [stem(current_query_word.strip().lower()) for current_query_word in query_phrase.split() if
                          current_query_word.strip().lower() not in stopword_list]

    if (len(stem_word_list) == 0 or (
            len(list(set(stem_word_list).intersection(set(current_inverted_dic.keys())))) == 0)):
        raise RuntimeError('All query word not found!')

    for current_stem in stem_word_list:
        # current_stem_doc_tf_count['doc_id'] = count
        current_stem_doc_tf_count = {}

        if (current_stem not in current_inverted_dic.keys()):
            continue

        for current_doc_id, current_doc_pos in current_inverted_dic[current_stem].items():
            current_stem_doc_tf_count[current_doc_id] = len(current_doc_pos)

        current_stem_df = len(current_inverted_dic[current_stem].keys())

        for current_doc_id, current_stem_doc_tf in current_stem_doc_tf_count.items():
            doc_tfidf[current_doc_id] += (1 + log10(current_stem_doc_tf)) * log10(doc_number / current_stem_df)

    sorted_doc_tfidf = sorted(doc_tfidf.items(), key=lambda x: x[1], reverse=True)

    return sorted_doc_tfidf


def output_query(query_result_dic, is_boolean=1):
    if (is_boolean):
        with open('results.boolean.txt', 'w', encoding='utf-8') as oq_file:
            for current_query_id, current_query_result_list in query_result_dic.items():
                for current_doc_id in current_query_result_list:
                    oq_file.write('%d 0 %d 0 1 0\n' % (int(current_query_id), int(current_doc_id)))
    else:
        with open('results.ranked.txt', 'w', encoding='utf-8') as oq_file:
            for current_query_id, current_query_result_list in query_result_dic.items():
                for current_docid_tfidf_tuple in current_query_result_list:
                    oq_file.write('%d 0 %d 0 %.4f 0\n' % (
                    int(current_query_id), int(current_docid_tfidf_tuple[0]), current_docid_tfidf_tuple[1]))

    return

loaded_inverted_index = load_inverted_index(inverted_index_path)


stopword_list = load_stopword(stopword_path)
# must contains space
operator_list = [' AND ', ' OR ']

for query_file_path in query_file_list:
    # query_result_dic[query_id] = current_query_result_list
    query_result_dic = {}
    if (query_file_path.split('.')[1] == 'boolean'):

        with open(query_file_path, 'r') as query_file:
            for current_query_line in query_file:

                query_result_list = []
                is_operator = 0
                current_query_line = current_query_line.strip()
                if (len(current_query_line) == 0):
                    continue
                current_query_id = current_query_line.split()[0]  # get query id
                current_query = ' '.join(current_query_line.split()[1:])  # get query text

                # check whether contains any operator: ' AND ' or ' OR '
                for current_operator in operator_list:

                    if (len(re.findall(current_operator, current_query))):
                        result_list = []
                        is_operator = 1
                        #                         current_query_split_list = current_query.split(current_operator)
                        current_query_split_list = re.split(current_operator, current_query)
                        for current_query_word in current_query_split_list:
                            result_list.append(boolean_query(loaded_inverted_index, current_query_word.strip()))
                        # AND
                        if (current_operator == ' AND '):
                            query_result_list = intersection_list(result_list[0], result_list[1])
                        # OR
                        else:
                            query_result_list = union_list(result_list[0], result_list[1])
                # no operator in query
                if (not is_operator):
                    query_result_list = boolean_query(loaded_inverted_index, current_query)

                query_result_dic[str(current_query_id)] = query_result_list
            output_query(query_result_dic)
    elif (query_file_path.split('.')[1] == 'ranked'):
        with open(query_file_path, 'r') as query_file:
            for current_query_line in query_file:
                current_query_id = current_query_line.split()[0]  # get query id
                current_query = ' '.join(current_query_line.split()[1:])  # get query text

                # remove punc
                del_punc = r'[\W]'  # keep _
                current_query = re.sub('&amp', ' ', current_query)
                current_query = re.sub(del_punc, ' ', current_query)

                current_result = tf_idf_weight(loaded_inverted_index, current_query.strip(), is_stop=1,
                                               stop_word_path=stopword_path)

                # with a maximum of 1000 results per query
                query_result_dic[str(current_query_id)] = current_result[0:1000]
            output_query(query_result_dic, is_boolean=0)