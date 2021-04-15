import praw
import json
import sys
import codecs
import numpy as np
import statistics as stats
from collections import Counter, namedtuple
import tldextract
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA
from pprint import pprint
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, RegexpTokenizer
from nltk.probability import FreqDist

class Subreddit_Sentiment_Analysis:

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
        self.top_comments = []

        self.stats = {}

        
        with open(self.subreddit + '_subreddit_data.json') as data_file:    
            data = json.load(data_file)
            for post in data[subreddit]:
                self.post_ids.append(post['id'])
                self.score_per_post.append(int(post['score']))
                self.comments_per_post.append(int(post['num_comments']))
                self.titles.append(post['title'].strip())
                self.urls.append(post['url'])

                for comment in post['top_comments']:
                    if comment['author'] != "AutoModerator":
                        self.top_comments.append(comment['text'])
                
                    
    def stopwords(self):
        stopwords = ['a', 'about', 'above', 'across', 'after', 'afterwards']
        stopwords += ['again', 'against', 'all', 'almost', 'alone', 'along']
        stopwords += ['already', 'also', 'although', 'always', 'am', 'among']
        stopwords += ['amongst', 'amoungst', 'amount', 'an', 'and', 'another']
        stopwords += ['any', 'anyhow', 'anyone', 'anything', 'anyway', 'anywhere']
        stopwords += ['are', 'around', 'as', 'at', 'back', 'be', 'became']
        stopwords += ['because', 'become', 'becomes', 'becoming', 'been']
        stopwords += ['before', 'beforehand', 'behind', 'being', 'below']
        stopwords += ['beside', 'besides', 'between', 'beyond', 'bill', 'both']
        stopwords += ['bottom', 'but', 'by', 'call', 'can', 'cannot', 'cant']
        stopwords += ['co', 'computer', 'con', 'could', 'couldnt', 'cry', 'de']
        stopwords += ['describe', 'detail', 'did', 'do', 'done', 'down', 'due']
        stopwords += ['during', 'each', 'eg', 'eight', 'either', 'eleven', 'else']
        stopwords += ['elsewhere', 'empty', 'enough', 'etc', 'even', 'ever']
        stopwords += ['every', 'everyone', 'everything', 'everywhere', 'except']
        stopwords += ['few', 'fifteen', 'fifty', 'fill', 'find', 'fire', 'first']
        stopwords += ['five', 'for', 'former', 'formerly', 'forty', 'found']
        stopwords += ['four', 'from', 'front', 'full', 'further', 'get', 'give']
        stopwords += ['go', 'had', 'has', 'hasnt', 'have', 'he', 'hence', 'her']
        stopwords += ['here', 'hereafter', 'hereby', 'herein', 'hereupon', 'hers']
        stopwords += ['herself', 'him', 'himself', 'his', 'how', 'however']
        stopwords += ['hundred', 'i', 'ie', 'if', 'in', 'inc', 'indeed']
        stopwords += ['interest', 'into', 'is', 'it', 'its', 'itself', 'keep']
        stopwords += ['last', 'latter', 'latterly', 'least', 'less', 'ltd', 'made']
        stopwords += ['many', 'may', 'me', 'meanwhile', 'might', 'mill', 'mine']
        stopwords += ['more', 'moreover', 'most', 'mostly', 'move', 'much']
        stopwords += ['must', 'my', 'myself', 'name', 'namely', 'neither', 'never']
        stopwords += ['nevertheless', 'next', 'nine', 'no', 'nobody', 'none']
        stopwords += ['noone', 'nor', 'not', 'nothing', 'now', 'nowhere', 'of']
        stopwords += ['off', 'often', 'on','once', 'one', 'only', 'onto', 'or']
        stopwords += ['other', 'others', 'otherwise', 'our', 'ours', 'ourselves']
        stopwords += ['out', 'over', 'own', 'part', 'per', 'perhaps', 'please']
        stopwords += ['put', 'rather', 're', 's', 'same', 'see', 'seem', 'seemed']
        stopwords += ['seeming', 'seems', 'serious', 'several', 'she', 'should']
        stopwords += ['show', 'side', 'since', 'sincere', 'six', 'sixty', 'so']
        stopwords += ['some', 'somehow', 'someone', 'something', 'sometime']
        stopwords += ['sometimes', 'somewhere', 'still', 'such', 'system', 'take']
        stopwords += ['ten', 'than', 'that', 'the', 'their', 'them', 'themselves']
        stopwords += ['then', 'thence', 'there', 'thereafter', 'thereby']
        stopwords += ['therefore', 'therein', 'thereupon', 'these', 'they']
        stopwords += ['thick', 'thin', 'third', 'this', 'those', 'though', 'three']
        stopwords += ['three', 'through', 'throughout', 'thru', 'thus', 'to']
        stopwords += ['together', 'too', 'top', 'toward', 'towards', 'twelve']
        stopwords += ['twenty', 'two', 'un', 'under', 'until', 'up', 'upon']
        stopwords += ['us', 'very', 'via', 'was', 'we', 'well', 'were', 'what']
        stopwords += ['whatever', 'when', 'whence', 'whenever', 'where']
        stopwords += ['whereafter', 'whereas', 'whereby', 'wherein', 'whereupon']
        stopwords += ['wherever', 'whether', 'which', 'while', 'whither', 'who']
        stopwords += ['whoever', 'whole', 'whom', 'whose', 'why', 'will', 'with']
        stopwords += ['within', 'without', 'would', 'yet', 'you', 'your']
        stopwords += ['yours', 'yourself', 'yourselves']

        return stopwords 
        
    def removeStopwords(self, wordlist, stopwords):
        return [w for w in wordlist if w not in stopwords]

    def process_text(self, headlines):
        tokens = []
        stop_words = stopwords.words('english')
        tokenizer = RegexpTokenizer(r'\w+')
        for line in headlines:
            toks = tokenizer.tokenize(line)
            toks = [t.lower() for t in toks if t.lower() not in stop_words]
            tokens.extend(toks)
        
        return tokens

    def get_average_stddev_counts(self):
        
        # calculates average score and average comment counts for top posts in given subreddit

        self.stats['average_score'] = np.mean(self.score_per_post)
        self.stats['average_comment_count'] = np.mean(self.comments_per_post)
        self.stats['std_dev_score'] = stats.stdev(self.score_per_post)
        self.stats['std_dev_comment_count'] = stats.stdev(self.comments_per_post)

        return

    def get_title_word_counts(self):
        all_title_text = " ".join(self.titles)
        all_title_text = all_title_text.lower()
        all_title_text = all_title_text.split()

        # remove stopwords, rejoin
        all_title_text = self.removeStopwords(all_title_text, self.stopwords)

        # split() returns list of all the words in the string 
        word_counts = Counter(all_title_text) 

        return
    
    def get_words(self, df, group):
        
        ## most common words overall
        neg_lines = list(df.headline)

        neg_tokens = self.process_text(neg_lines)
        neg_freq = FreqDist(neg_tokens)

        return list(neg_freq.most_common(30))
         
    def get_positive_words(self, df, group):

        if group == 'headline':
            pos_lines = list(df[df.label == 1].headline)
        if group == 'comment':
            pos_lines = list(df[df.label == 1].comment)

        pos_tokens = self.process_text(pos_lines)
        pos_freq = FreqDist(pos_tokens)
        return pos_freq.most_common(20)
    
    def get_negative_words(self, df, group):
        
        if group == 'headline':
            neg_lines = list(df[df.label == -1].headline)
        if group == 'comment':
            neg_lines = list(df[df.label == -1].comment)


        neg_tokens = self.process_text(neg_lines)
        neg_freq = FreqDist(neg_tokens)

        return list(neg_freq.most_common(20))

    def conduct_sentiment_analysis(self, group):
        sia = SIA()
        results = []

        for line in self.titles:
            #if 'george' in line.lower():
                pol_score = sia.polarity_scores(line)
                pol_score[group] = line
                results.append(pol_score)
        
        # pprint(results, width=100)
        # print(len(self.titles))


        df = pd.DataFrame.from_records(results)
        df['label'] = 0
        df.loc[df['compound'] > 0.25, 'label'] = 1
        df.loc[df['compound'] < -0.25, 'label'] = -1
        df.head()

        df2 = df[[group, 'label']]
        df2.to_csv(self.subreddit + '_' + group + '_labels.csv', mode='a', encoding='utf-8', index=False)

        fig, ax = plt.subplots(figsize=(8, 8))

        counts = df.label.value_counts(normalize=True, ascending = True) * 100
        counts.sort_index()
        print(counts)
        print(type(counts))


        sns.barplot(x=counts.index, y=counts, ax=ax)

        ax.set_xticklabels(['Negative', 'Neutral', 'Positive'])
        ax.set_ylabel("Percentage")
        ax.set_xlabel("Sentiment")


        rects = ax.patches
        indexes = [-1, 0, 1]
        count = 0
        overall_percentages = []
        
        for rect, label in zip(rects, counts):
            height = rect.get_height()
            ax.text(rect.get_x() + rect.get_width() / 2, height - 5, str(round(counts[indexes[count]], 2)) + '%',
                    ha='center', va='bottom')
            overall_percentages.append(round(counts[indexes[count]], 2))
            count += 1

        plt.title('Sentiment Analysis of /r/' + self.subreddit + ' Top 1000 Posts\' ' + group.capitalize() + 's')

        plt.show()

        return df, overall_percentages
    
    def conduct_sentiment_analysis_headlines_keyword_exclude(self, group, keyword, bucket):
        sia = SIA()
        results = []
        count = 0
        for line in self.titles:
                if keyword not in line.lower():
                    pol_score = sia.polarity_scores(line)
                    pol_score[group] = line
                    results.append(pol_score)
                    count += 1
        print(count)
        # pprint(results, width=100)
        # print(len(self.titles))


        df = pd.DataFrame.from_records(results)
        df['label'] = 0
        df.loc[df['compound'] > 0.2, 'label'] = 1
        df.loc[df['compound'] < -0.2, 'label'] = -1
        df.head()

        df2 = df[[group, 'label']]
        df2.to_csv(self.subreddit + '_' + group + 's_labels.csv', mode='a', encoding='utf-8', index=False)

        fig, ax = plt.subplots(figsize=(8, 8))

        counts = df.label.value_counts(normalize=True, ascending = True) * 100
        counts.sort_index()

        sns.barplot(x=counts.index, y=counts, ax=ax)

        ax.set_xticklabels(['Negative', 'Neutral', 'Positive'])
        ax.set_ylabel("Percentage")
        ax.set_xlabel("Sentiment")

        rects = ax.patches
        indexes = [-1, 0, 1]
        count = 0
        keyword_percentages = []

        for rect, label in zip(rects, counts):
            height = rect.get_height()
            ax.text(rect.get_x() + rect.get_width() / 2, height - 5, str(round(counts[indexes[count]], 2)) + '%',
                    ha='center', va='bottom')
            keyword_percentages.append(round(counts[indexes[count]], 2))
            count += 1


        plt.title('Sentiment Analysis of /r/' + self.subreddit + ' Posts\' ' + group.capitalize() + 's Without "' + keyword + '" in Them')

        # plt.show()

        return df, keyword_percentages

    def conduct_sentiment_analysis_headlines_keywords_include(self, group, keyword, bucket):
        sia = SIA()
        results = []

        for line in self.titles:
                if keyword in line.lower():
                    pol_score = sia.polarity_scores(line)
                    if pol_score['compound'] > .20:
                        print(line)
                    pol_score[group] = line
                    results.append(pol_score)
        
        # pprint(results, width=100)
        # print(len(self.titles))


        df = pd.DataFrame.from_records(results)
        df['label'] = 0
        df.loc[df['compound'] > 0.20, 'label'] = 1
        df.loc[df['compound'] < -0.20, 'label'] = -1
        df.head()

        df2 = df[[group, 'label']]
        df2.to_csv(self.subreddit + '_' + group + 's_labels.csv', mode='a', encoding='utf-8', index=False)

        fig, ax = plt.subplots(figsize=(8, 8))

        counts = df.label.value_counts(normalize=True, ascending = True) * 100
        counts.sort_index()

        sns.barplot(x=counts.index, y=counts, ax=ax)
        print(counts)

        ax.set_xticklabels(['Negative', 'Neutral', 'Positive'])
        ax.set_ylabel("Percentage")
        ax.set_xlabel("Sentiment")

        rects = ax.patches
        indexes = [-1, 0, 1]
        count = 0
        keyword_percentages = []

        for rect, label in zip(rects, counts):
            height = rect.get_height()
            ax.text(rect.get_x() + rect.get_width() / 2, height - 5, str(round(counts[indexes[count]], 2)) + '%',
                    ha='center', va='bottom')
            keyword_percentages.append(round(counts[indexes[count]], 2))
            count += 1


        plt.title('Sentiment Analysis of /r/' + self.subreddit + ' Posts\' ' + group.capitalize() + 's with "' + keyword + '" in Them')

        plt.show()

        return df, keyword_percentages

    def conduct_keyword_analysis_overall(self):
        score = 0
        num_comments = 0
        for count, line in enumerate(self.titles):
            score += self.score_per_post[count]
            num_comments += self.comments_per_post[count]


        return score / len(self.titles), num_comments / len(self.titles)

    def conduct_keyword_analysis_keywords(self, keywords):
        word_score_pairs = []
        word_num_comments_pairs = []
        for word in keywords:
            avg_score = self.calc_avg_score(word)
            word_score_pairs.append((word, avg_score))

            avg_comments = self.calc_avg_comments(word)
            word_num_comments_pairs.append((word, avg_comments))

        return word_score_pairs, word_num_comments_pairs

    def calc_avg_score(self, word):
        total = 0
        score = 0
        for count, line in enumerate(self.titles):
            if word in line.lower():
                score += self.score_per_post[count]
                total += 1
        
        return score / total
    
    def calc_avg_comments(self, word):
        total = 0
        score = 0
        for count, line in enumerate(self.titles):
            if word in line.lower():
                score += self.comments_per_post[count]
                total += 1
        
        return score / total

    def create_score_comment_histograms(self, pairs, average, y):
        
        plt.bar(*zip(*pairs))
        plt.axhline(average, color='green', linewidth=2)
        plt.ylabel(y)
        plt.xlabel('Most Popular Keywords Across Headlines')

        if y == 'Average Score for Posts with Keyword in Headline':
            plt.title('Average Scores of /r/' + self.subreddit + ' Posts that Have Specific Keywords in Headline')
        
        elif y == 'Average Number of Comments For Posts with Keyword in Headline':
            plt.title('Average Number of Comments of /r/' + self.subreddit + ' Posts that Have Specific Keywords in Headline')

        plt.show()

        return
    
    def get_post_data(self):
        self.get_average_stddev_counts()
        self.get_title_word_counts()

        group = 'headline'
        df, overall_percentages = self.conduct_sentiment_analysis(group)

        # positive = self.get_positive_words(df, group)
        # negative = self.get_negative_words(df, group)
        words_tuples = self.get_words(df, group)
        print(words_tuples)
        conservative_words = ['trump', 'china', 'cases']
        liberal_words = ['sanders']

        words = []
        news_out = ['says', 'u', 'us', '19', 'new', 'million', '000', 'judge', 'video', 'home', 'year', '19', 'calls', 'first', 'two', 'one']
        for tup in words_tuples:
            if tup[0] not in news_out:
                words.append(tup[0])
        print(words)

        # words = ['trump']

        # ## sentiment analysis on keywords
        # all_keyword_percentages = []

        # for word in words:
        #     df2, keyword_percentages = self.conduct_sentiment_analysis_headlines_keyword_exclude(group, word, 'conservative') # trump
        #     all_keyword_percentages.append(keyword_percentages)
        
        for word in conservative_words:
             self.conduct_sentiment_analysis_headlines_keywords_include(group, word, 'conservative') # trump
        
        # print(overall_percentages)
        # print(all_keyword_percentages)

        # highest_sum = -1
        # index = -1
        # for count, percentages in enumerate(all_keyword_percentages):
        #     current_sum = abs(percentages[0] - overall_percentages[0]) + abs(percentages[1] - overall_percentages[1])  + abs(percentages[2] - overall_percentages[2]) 
        #     if highest_sum < current_sum:
        #         highest_sum = current_sum
        #         index = count
        
        # print(highest_sum)
        # print(index)
        # print(words[index])
            


        
        ## keyword analysis on keywords

        # words_scores, words_num_comments = self.conduct_keyword_analysis_keywords(words)
        # words_scores.sort(key=lambda x:x[1])
        # words_num_comments.sort(key=lambda x:x[1])

        # avg_score, avg_num_comments = self.conduct_keyword_analysis_overall()

        # print(words_scores)
        # print(words_num_comments)

        # self.create_score_comment_histograms(words_scores, avg_score, 'Average Score for Posts with Keyword in Headline')
        # self.create_score_comment_histograms(words_num_comments, avg_num_comments, 'Average Number of Comments For Posts with Keyword in Headline')


        # print(self.stats['average_score'])
        # print(self.stats['average_comment_count']) 
        # print(self.stats['std_dev_score'])
        # print(self.stats['std_dev_comment_count'])



    
        

        return
        
def main():
    subreddit = sys.argv[1]
    test_object = Subreddit_Sentiment_Analysis(subreddit)
    test_object.get_post_data()
    # test_object.get_title_word_counts()



if __name__ == "__main__":
    main()
