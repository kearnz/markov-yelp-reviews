
# coding: utf-8

#all the imports
import os
import json
import itertools as it
import numpy as np
import pandas as pd
import scipy.linalg as LA
import random
import nltk
import re
from sklearn.feature_extraction.text import TfidfVectorizer as TVF

'''
YELP DATA CLASS
- used to load yelp json files for reviews and business
- class creates a mini-database for users of the class to extract all reviews for a business or category etc.
'''

class YelpData:
    
    '''
    HOW TO USE
    - the yelp variable below initializes an instance of the YelpData class
    - it takes a while to run the first time because it loads 4+ million reviews and 15k businesses into dataframes
    - but then after it loads, you NEVER need to load the data again
    - you can interact with the following 3 variables
        - yelp.categories -- gives you all the categories for businesses
        - yelp.businesses -- gives you all the businesses and their details
        - yelp.reviews -- gives you all the reviews for businesses
    '''
    
    def __init__(self,path):
        '''initiatize yelp class and load the appropriate data once'''
        self.path = path
        self.business = 'business.json'
        self.review = 'review.json'
        #Use these variables to access data once instance of class initialized
        self.businesses = self._business_details()
        self.categories = self._business_categories()
        self.reviews = self._review_details()
    
    def see_files(self):
        '''simple method to see the files in the yelp directory'''
        os.chdir(path)
        return os.listdir()
    
    #helper function to get all the data for a file
    def retrieve_all_data(self,f):
        '''retrieves all the data from a file given the path of the yelp directory'''
        os.chdir(self.path)
        with open(f) as json_data:
            data = [json.loads(line) for line in json_data]
        return data
    
    '''
    NOTE THE UNDERSCORE IN FOLLOWING METHODS
    - in another language, these methods would be declared private, but python not about private methods
    - as Guido notes, "we are all consenting adults here". Underscore signifies private suggestion, but not mandatory
    
    - Why should these methods be private? 
        - they load data from files, and the data in those files does not change 
        - therefore, you need to load the data only once. Each subsequent load is 1) inefficient and 2) consumes memory
        - the data should be loaded once, when the class is initialized
        - users should interact with the loaded data. this is similar to an application cache
    '''
    #helper method
    def _b_dict(self,d,cols):
        return dict((k,v) for k,v in d.items() if k in cols)
    
    def _business_details(self):
        '''flatten structure to get all details of business, with key as index'''
        businesses = self.retrieve_all_data(self.business)
        #reduce each business object to get the information we care about
        cols = ('address','business_id','city','name','review_count','stars')
        business_df = pd.DataFrame([self._b_dict(d,cols) for d in businesses])
        return business_df.set_index('business_id')

    def _business_categories(self):
        '''categories will function as a table in 1NF w/ business_id,category'''
        businesses = self.retrieve_all_data(self.business)
        cols = ('business_id','categories')
        business_cats = [self._b_dict(d,cols) for d in businesses]
        
        #b/c business id is one to many, we need to cycle business ids to each category
        #then we need to flatten the list so we can make it a dataframe
        #this is cryptic, but again, this method is not for an end user of the class
        flattened_cats = list(it.chain(*[list(zip(it.cycle([d['business_id']]),d['categories'])) for d in business_cats]))
        return pd.DataFrame(flattened_cats,columns=['business_id', 'category'])
    
    def _review_details(self):
        '''flatten structure to get all details of users'''
        reviews = self.retrieve_all_data(self.review)
        #we don't care about users in this context
        cols = ('business_id','review_id','stars','text','cool','funny','useful')
        review_df = pd.DataFrame([self._b_dict(d,cols) for d in reviews])
        return review_df.set_index('review_id')

'''
MARKOV MODEL CLASS
- Used to generate random sentences from input data
- Input data we use for this is yelp dataset
'''

class MarkovModel:
    
    '''
    HOW TO USE
    - the MarkovModel is built from scratch and does not use scapy or nltk (mainly to demonstrate properties) 
    - initialize by passing a list of sentences (used for corpus) and the order for n-gram creation
    - the world builders are two basic methods to build / mimic THE TRANSITION MATRIX
    - the markov_sentence_one and markov_sentence two are methods to generate random sentences based on corpus
        - these methods have multiple optional variables to make the markov model more flexible
        - iterations is used for your desired sentence length
        - data is the input data you want to use for your project, which defaults to what you use to initialize class
        - starter (sentence_two) is the start word you want to use
        - gen is used to build the final sentence after n recursive calls
        - extend (sentence_two) gives the user the option to extend the sentence until punctuation mark is reached
    - finally, the similarity method finds the most similar sentence to the autogenerated markov result
        - ideally the result of similarity is low, so the data does not overfit
        - higher order generally leads to a very similar sentence
        - the similarity metric could be vastly improved, but that is out of scope for this analysis
    '''
    
    def __init__(self,sentence_vec,order):
        self.sentence_vec = sentence_vec
        self.corpus = ' '.join(sentence_vec).replace('\n',' ')
        self.order = order
        self.punc_split = r"[\w']+|[.,!?;:-]"
        self.punc_end = ['.','!','?']
    
    #helper method
    def word_builder(self,s):
        d = {}
        o = self.order
        for each in range(len(s)-o):
            pairs = tuple(s[each:each+o])
            if pairs in d: d[pairs].append(s[each+o])
            else: d[pairs] = [s[each+o]]
        return d

    #EXAMPLE 1 - splits on space only, no consideration of punctuation
    def simple_word_dict(self):
        s = self.corpus.split(' ')
        d = self.word_builder(s)
        return d
    
    #EXAMPLE 2 - more thought given to punctuation.
    def punc_word_dict(self):
        s = re.findall(self.punc_split,self.corpus)
        d = self.word_builder(s)
        return d

    #ITERATION 1 -- SIMPLE SENTENCE
    def markov_sentence_one(self,iterations,data=None,begin=None,gen=[]):
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
            self.markov_sentence_one(iterations-1,data=data,begin=next_step,gen=gen)
        return ' '.join(gen)
    
    #ITERATION TWO -- A BIT MORE THOUGHT
    def markov_sentence_two(self,iterations,starter=None,data=None,begin=None,gen=[],cnt=0,extend=False):
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
            self.markov_sentence_two(iterations,starter=None,
                                     data=data,begin=next_step,
                                     gen=gen,cnt=cnt+1,extend=extend)
        if extend:
            if cnt > iterations and next_word[-1] not in self.punc_end:
                self.markov_sentence_two(iterations,starter=None,
                                         data=data,begin=next_step,
                                         gen=gen,cnt=cnt,extend=extend)
        return ' '.join(gen)
    
    #need to pass a string, should error handle in case anything else passed
    def most_similar_sentence(self,res):
        '''
        NOTES ON THIS METHOD
        - naive TF-IDF test to check for the most similar sentence and evaluate if too similar to markov 
        - This is a very inefficient way to implement this but works well enough for our project
        - The goal of this method is primarily to demonstrate what happens when you increase order too much 
        '''
        analysis = [res] + [i.replace('\n','') for i in self.sentence_vec] 
        vec = TVF(min_df=1).fit_transform(analysis)
        vals = (vec * vec.T)[0].A[0]
        index = np.where(vals==max(vals[1:]))[0][0]
        closest_sentence = analysis[index]
        return {'markov_sentence': res, 'closest_sentence': closest_sentence}

'''
**************EXAMPLE USAGE BELOW*****************
'''

'''NOTE -- change your path to wherever you stored the yelp reviews'''

path = '/Users/josephkearney/Desktop/U_Chicago/Classes/Linear_Algebra/yelp_dataset'
yelp = YelpData(path)

#some notes
print("Number of businesses: {}".format(len(yelp.businesses.index)))
print("Number of reviews: {}".format(len(yelp.reviews.index)))

#test on the first 2000 sentences
#in theory, we'd want some sort of filtering first. The filter below could include reviews from hotels to restaurants
sentence = yelp.reviews.text.tolist()[:2000]

#initiate matrices of different order
order_1 = MarkovModel(sentence,1)
order_2 = MarkovModel(sentence,2)
order_3 = MarkovModel(sentence,3)
order_4 = MarkovModel(sentence,4)
order_5 = MarkovModel(sentence,5)

#example of different sentences and variations of overloaded method
#note that extend = True almost always a good idea after some analysis
order_1_s = order_1.markov_sentence_two(5,extend=True)
order_2_s = order_2.markov_sentence_two(9,starter='The',extend=True)
order_3_s = order_3.markov_sentence_two(7,starter='A',extend=True)
order_4_s = order_4.markov_sentence_two(8,extend=True)
order_5_s = order_5.markov_sentence_two(9,extend=True)

#print("Order 1 example:\n {0}".format(order_1.most_similar_sentence(order_1_s)))
#print("Order 2 example:\n {0}".format(order_2.most_similar_sentence(order_2_s)))
#print("Order 3 example:\n {0}".format(order_3.most_similar_sentence(order_3_s)))
#print("Order 4 example:\n {0}".format(order_4.most_similar_sentence(order_4_s)))
#print("Order 5 example:\n {0}".format(order_5.most_similar_sentence(order_5_s)))

