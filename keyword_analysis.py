import praw
import json
import sys
import codecs
import numpy as np
import statistics as stats
from collections import Counter, namedtuple
import tldextract
import matplotlib.pyplot as plt

class Subreddit_Domain_Data:

    ## constructor for subreddit class
    def __init__(self, subreddit): 
        self.subreddit = subreddit
        self.post_ids = []
        self.score_per_post = []
        self.comments_per_post = []
        self.titles = []
        self.words_in_titles = []
        self.words_in_comments_on_posts = []
        self.urls = []
        self.domain_counts = {}

        self.stats = {}

        
        with open(self.subreddit + '_subreddit_data.json') as data_file:    
            data = json.load(data_file)
            for post in data[subreddit]:
                self.post_ids.append(post['id'])
                self.score_per_post.append(int(post['score']))
                self.comments_per_post.append(int(post['num_comments']))
                self.titles.append(post['title'].strip())
                self.urls.append(post['url'])

    def upvote_analysis_overall(self, keywords):

        return
    
    def upvote_analysis_keywords(self, keywords):

        return


        

    def get_post_data(self):
        self.get_url_domain_counts()
        self.get_domain_calculations()
        self.get_reliability_histogram()
        self.get_bias_histogram()
        self.get_scatterplot()
        return

def main():
    subreddit = sys.argv[1]
    test_object = Subreddit_Domain_Data(subreddit)
    test_object.get_post_data()



if __name__ == "__main__":
    main()
