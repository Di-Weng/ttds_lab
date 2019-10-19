# COURSEWORK 1
Given a specific xml, output the inverted index to index.txt. And load the inverted index from file to test on two queries.boolean.txt and queries.ranked.txt.

There are two .py files, train_inverted_index.py and query.py. 

train_inverted_index.py: Given a specific xml, transforming it into a *standard xml file*, then output the inverted index to *index.txt*.

query.py: Loading a inverted index file then output the query result from queries.boolean.txt and queries.ranked.txt, output the *results.boolean.txt* and *results.ranked.txt* respectively.

## Dependency
* python = 3.7.4
* numpy = 1.17.2
* scikit-learn = 0.21.3
* scipy = 1.3.1
* stemming = 1.0.1
     
## Usage
1. train inverted index
```
python train_inverted_index.py --stopword englishST.txt --collection trec.5000.xml
 #--stopword: path of stopword
 #--collection: path of trec xml file, not standard form. Similar to trec.5000.xml and trec.sample.xml
```

2. test on query files
```
python query.py --stopword englishST.txt --index index.txt --q1 queries.boolean.txt --q2 queries.ranked.txt
 #--stopword: the path of stopword
 #--index: the path of index file
 #q1: query_file 1
 #q1: query_file 2
 #you could at most specify two files, but at least one files.
```