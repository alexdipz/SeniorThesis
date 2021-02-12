import praw
import json
import sys
import codecs
import numpy as np
import statistics as stats
from collections import Counter, namedtuple
import tldextract

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
        self.stopwords = self.stopwords()
        self.urls = []
        self.domain_counts = {}

        self.stats = {}

        
        with open('subreddit_data.json') as data_file:    
            data = json.load(data_file)
            for post in data[subreddit]:
                self.post_ids.append(post['id'])
                self.score_per_post.append(int(post['score']))
                self.comments_per_post.append(int(post['num_comments']))
                self.titles.append(post['title'].strip())
                self.urls.append(post['url'])
                    

    ## manually collected Jan 1, last updated Nov 2020 it seems. 
    def domain_bias_ratings(self):
        bias = {}
        bias['independent'] = -10.68
        bias['thedailybeast'] = -18.52
        bias['commondreams'] = -17.80
        bias['newsweek'] = -11.03
        bias['theweek'] = -14.77
        bias['cnn'] = -10.13
        bias['buzzfeednews'] = -10.56
        bias['cnbc'] = -1.88
        bias['slate'] = -19.40
        bias['businessinsider'] = -5.97
        bias['thehill'] = 0.05
        bias['apnews'] = -1.80
        bias['theatlantic'] = -11.85
        bias['nytimes'] = -8.07
        bias['vice'] = -13.84
        bias['latimes'] = -8.16
        bias['marketwatch'] = -5.52
        bias['axios'] = -7.09
        bias['washingtonpost'] = -7.48
        bias['propublica'] = -7.28
        bias['thenation'] = -19.15
        bias['talkingpointsmemo'] = -10.45
        bias['huffpost'] = -13.18
        bias['usatoday'] = -4.34
        bias['nbcnews'] = 7.87
        bias['azcentral'] = -5.30
        bias['reuters'] = -1.89
        bias['theintercept'] = -17.77
        bias['forbes'] = -2.69
        bias['cbsnews'] = -3.56
        bias['nydailynews'] = -7.88
        bias['theroot'] = -19.78
        bias['nymag'] = -13.79
        bias['vanityfair'] = -19.53
        bias['abc'] = -4.79
        bias['msnbc'] = -14.74
        bias['salon'] = -18.75
        bias['washingtonexaminer'] = 17.83
        bias['nypost'] = 14.51
        bias['time'] = -10.66
        bias['vox'] =  -11.72
        bias['fox'] = 17.78
        bias['truthout'] = -20.73
        bias['theguardian'] = -10.82
        bias['politico'] = -8.90
        bias['mercurynews'] = -5.33 
        bias['motherjones'] = -16.02 
        bias['teenvogue'] = -14.27
        bias['npr'] = -4.46
        bias['foreignpolicy'] = -0.92 
        bias['bloomberg'] = -3.75
        bias['jacobinmag'] = -23.31
        bias['newrepublic'] = -18.90
        bias['inthesetimes'] = -19.70
        bias['washingtonmonthly'] = -17.19 
        bias['usnews'] = -3.31
        bias['cnet'] = -0.72 
        bias['theverge'] = -1.69 
        bias['cnsnews'] = 19.28 
        bias['fivethirtyeight'] = -7.53 
        bias['fortune'] = -0.07 
        bias['dallasnews'] = -5.35 


        return bias
    
    ## manually collected Jan 1, last updated Nov 2020 it seems. 
    def domain_reliability_ratings(self):
        reliability = {}
        reliability['independent'] = 41.39
        reliability['thedailybeast'] = 35.53
        reliability['commondreams'] = 41.29
        reliability['newsweek'] = 38.24
        reliability['theweek'] = 30.77
        reliability['cnn'] = 44.20
        reliability['buzzfeednews'] = 40.17
        reliability['cnbc'] = 47.04
        reliability['slate'] = 33.83
        reliability['businessinsider'] = 43.98
        reliability['thehill'] = 45.99
        reliability['apnews'] = 52.14
        reliability['theatlantic'] = 41.76
        reliability['nytimes'] = 46.86
        reliability['vice'] = 39.54
        reliability['latimes'] = 48.26
        reliability['marketwatch'] = 43.86
        reliability['axios'] = 46.59
        reliability['washingtonpost'] = 44.60
        reliability['propublica'] = 48.59
        reliability['thenation'] = 34.42
        reliability['talkingpointsmemo'] = 41.20
        reliability['huffpost'] = 38.68
        reliability['usatoday'] = 46.34
        reliability['nbcnews'] =  47.23
        reliability['azcentral'] =  44.27
        reliability['reuters'] = 51.04
        reliability['theintercept'] =  39.62
        reliability['forbes'] = 43.61
        reliability['cbsnews'] = 48.88
        reliability['nydailynews'] = 44.94
        reliability['theroot'] = 30.28
        reliability['nymag'] = 41.65
        reliability['vanityfair'] = 33.77
        reliability['abc'] = 48.22
        reliability['msnbc'] = 43.45
        reliability['salon'] =  36.51
        reliability['washingtonexaminer'] = 25.20
        reliability['nypost'] = 34.07
        reliability['time'] = 44.08 
        reliability['vox'] = 41.46
        reliability['fox'] = 31.62
        reliability['truthout'] = 26.91
        reliability['theguardian'] = 45.41
        reliability['politico'] = 46.48
        reliability['mercurynews'] = 50.48
        reliability['motherjones'] = 39.89 
        reliability['teenvogue'] = 39.83
        reliability['npr'] = 49.96 
        reliability['foreignpolicy'] = 42.29
        reliability['bloomberg'] = 47.20
        reliability['jacobinmag'] = 29.58 
        reliability['newrepublic'] = 35.51 
        reliability['inthesetimes'] = 35.52 
        reliability['washingtonmonthly'] = 30.00 
        reliability['usnews'] = 45.79 
        reliability['cnet'] = 46.33
        reliability['theverge'] = 44.99
        reliability['cnsnews'] = 31.48
        reliability['fivethirtyeight'] = 43.62
        reliability['fortune'] = 44.71
        reliability['dallasnews'] = 44.76


        return reliability
    
    def get_url_domain_counts(self):
       
        count = 0
        for url in self.urls:
            ext = tldextract.extract(url)
            domain = getattr(ext, 'domain')
            if 'fox' in domain:
                domain = 'fox'

            if domain in self.domain_counts:
                self.domain_counts[domain] = self.domain_counts[domain] + 1
            else:
                self.domain_counts[domain] = 1
            
            count += 1
        
        print(self.domain_counts)
        print("")
        print(sum(self.domain_counts.values()))
            
        return
    
    def get_domain_calculations(self):
        bias = self.domain_bias_ratings()
        reliability = self.domain_reliability_ratings()
        count = 0

        for key in bias:
            if key in self.domain_counts:
                count += self.domain_counts[key]

        print(count)

        weighted_average_bias = 0
        weighted_average_reliability = 0

        for key in bias:
            weighted_average_bias += bias[key] * self.domain_counts[key]
            weighted_average_reliability += reliability[key] * self.domain_counts[key]
        
        weighted_average_bias /= count
        weighted_average_reliability /= count

        print(weighted_average_bias)
        print(weighted_average_reliability)
    
    def get_post_data(self):
        self.get_url_domain_counts()
        self.get_domain_calculations()
        return

def main():
    subreddit = sys.argv[1]
    test_object = Subreddit_Domain_Data(subreddit)
    test_object.get_post_data()



if __name__ == "__main__":
    main()
