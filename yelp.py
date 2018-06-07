import os
import json
import itertools as it
import pandas as pd

class YelpData:
    
    def __init__(self,path):
        '''initiatize yelp class and load the appropriate data once'''
        self.path = path
        self.business = 'business.json'
        self.review = 'review.json'
        self.cols_biz = ('address','business_id','city','name','review_count','stars')
        self.cols_cat = ('business_id','categories')
        self.cols_review = ('business_id','review_id','stars','text','cool','funny','useful')
        #Use these variables to access data once instance of class initialized
        self.businesses = self._business_details()
        self.categories = self._business_categories()
        self.reviews = self._review_details()
    
    def see_files(self):
        '''simple method to see the files in the yelp directory'''
        os.chdir(self.path)
        return os.listdir()
    
    #helper function to get all the data for a file
    def retrieve_all_data(self,f):
        '''retrieves all the data from a file given the path of the yelp directory'''
        os.chdir(self.path)
        with open(f) as json_data:
            data = [json.loads(line) for line in json_data]
        return data
    
    def _b_dict(self,d,cols):
        return dict((k,v) for k,v in d.items() if k in cols)
    
    def _business_details(self,cols=None):
        # Hard Coded - cols_biz only thing allowed right now
        cols = self.cols_biz
        '''flatten structure to get all details of business, with key as index'''
        businesses = self.retrieve_all_data(self.business)
        #reduce each business object to get the information we care about
        business_df = pd.DataFrame([self._b_dict(d,cols) for d in businesses])
        return business_df.set_index('business_id')

    def _business_categories(self):
        # Hard Coded - cols_cat only thing allowed right now
        cols = self.cols_cat
        '''categories will function as a table in 1NF w/ business_id,category'''
        businesses = self.retrieve_all_data(self.business)
        business_cats = [self._b_dict(d,cols) for d in businesses]
        flattened_cats = list(it.chain(*[list(zip(it.cycle([d['business_id']]),
            d['categories'])) for d in business_cats]))
        return pd.DataFrame(flattened_cats,columns=['business_id', 'category'])
    
    def _review_details(self):
        # Hard Coded - cols_review only thing allowed right now
        cols = self.cols_review
        '''flatten structure to get all details of users'''
        reviews = self.retrieve_all_data(self.review)
        review_df = pd.DataFrame([self._b_dict(d,cols) for d in reviews])
        return review_df.set_index('review_id')

