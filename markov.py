import re
import random
import nltk
import itertools as it
import numpy as np
import scipy.linalg as LA
from sklearn.feature_extraction.text import TfidfVectorizer as TVF

class MarkovModel:
    
    def __init__(self,sentence_vec,order):
        self.sentence_vec = sentence_vec
        self.corpus = ' '.join(sentence_vec).replace('\n',' ')
        self.order = order
        self.punc_split = r"[\w']+|[.,!?;:-]"
        self.punc_end = ['.','!','?']
    
    def word_builder(self,s):
        d = {}
        o = self.order
        for each in range(len(s)-o):
            pairs = tuple(s[each:each+o])
            if pairs in d: d[pairs].append(s[each+o])
            else: d[pairs] = [s[each+o]]
        return d

    def simple_word_dict(self):
        s = self.corpus.split(' ')
        d = self.word_builder(s)
        return d
    
    def punc_word_dict(self):
        s = re.findall(self.punc_split,self.corpus)
        d = self.word_builder(s)
        return d

    def simple_sentence(self,iterations,data=None,begin=None,gen=[]):
        '''gen random sentence with no consideration of punctuation, english language or beginning / end words'''
        o = self.order
        try:
            if data is None:
                #defaults to punctuation split, which is my standard at least
                data = self.punc_word_dict()
            if begin is None:
                begin = random.choice(list(data.keys()))
                gen = [word for word in begin]
            begin_step = data[begin]
            prec_word = begin[1-o:]
            next_word = random.choice(begin_step)
            gen.append(next_word)
            if o > 1:
                next_step = (*prec_word,next_word)
            else:
                next_step = tuple([next_word])
        except KeyError:
            return ' '.join(gen)
        if iterations > 0:
            self.simple_sentence(iterations-1,data=data,begin=next_step,gen=gen)
        return ' '.join(gen)
    
    def smarter_sentence(self,iterations,starter=None,data=None,
                            begin=None,gen=[],cnt=0,extend=False):
        '''deals with punctuation a bit more and allows user to extend a sentence'''
        o = self.order
        if data is None:
            #defaults to punctuation split, which is my standard at least
            data = self.punc_word_dict()
        if not starter is None:
            check = starter in it.chain(*list(data.keys()))
            if not check: 
                return "word not in corpus, please choose again"
            begin = random.choice([k for k in data.keys() if k[-1]==starter])
            gen = [starter]
        elif begin is None:
            #start sentences with a word that's likely a starter
            begin = random.choice([k for k in data.keys() if k[0][0].isupper()])
            gen = [word for word in begin]
        else:
            begin = begin
        try:
            begin_step = data[begin]
            prec_word = begin[1-o:]
            next_word = random.choice(begin_step)
            gen.append(next_word)
            if o > 1:
                next_step = (*prec_word,next_word)
            else:
                next_step = tuple([next_word])
        except KeyError:
            return ' '.join(gen)
        if cnt <= iterations:
            self.smarter_sentence(iterations,starter=None,
                                     data=data,begin=next_step,
                                     gen=gen,cnt=cnt+1,extend=extend)
        if extend:
            if cnt > iterations and next_word[-1] not in self.punc_end:
                self.smarter_sentence(iterations,starter=None,
                                         data=data,begin=next_step,
                                         gen=gen,cnt=cnt,extend=extend)
        return ' '.join(gen)
    
    def most_similar_sentence(self,res):

        # inefficient way to do this right now, 
        # but works well enough for quick and dirty check
        analysis = [res] + [i.replace('\n','') for i in self.sentence_vec] 
        vec = TVF(min_df=1).fit_transform(analysis)
        vals = (vec * vec.T)[0].A[0]
        index = np.where(vals==max(vals[1:]))[0][0]
        closest_sentence = analysis[index]
        return {'markov_sentence': res, 'closest_sentence': closest_sentence}



