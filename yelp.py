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
        flattened_cats = list(it.chain(*[list(zip(it.cycle([d['business_id']]),
            d['categories'])) for d in business_cats]))
        return pd.DataFrame(flattened_cats,columns=['business_id', 'category'])
    
    def _review_details(self):
        '''flatten structure to get all details of users'''
        reviews = self.retrieve_all_data(self.review)
        #we don't care about users in this context
        cols = ('business_id','review_id','stars','text','cool','funny','useful')
        review_df = pd.DataFrame([self._b_dict(d,cols) for d in reviews])
        return review_df.set_index('review_id')

