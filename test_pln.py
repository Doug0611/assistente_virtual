from textblob.classifiers import NaiveBayesClassifier
import json
import re
from typing import Optional


def classifier_commands(command: str) -> str:
    try:
        with open('./cmds.json', mode='r', encoding='utf-8') as file:
            cl = NaiveBayesClassifier(file, format='json')
            return cl.classify(command)
    except FileNotFoundError:
        return None


def mine_search_term(text: str, label: Optional[str] = '') -> str:
    try:
        with open('cmds.json', encoding='utf-8') as cmds:
            data = json.loads(cmds.read())
            stopwords = []
            for word in data:
                if label:
                    if word['label'] == label:
                        stopwords.append(word['text'])
                else:
                    stopwords.append(word['text'])
    except FileNotFoundError:
        pass
    else:
        for term in stopwords:
            if re.findall(term, text):
                remove_stopwords = list(text.partition(term))
                remove_stopwords.remove('')
                return remove_stopwords.pop().strip()
        return text
