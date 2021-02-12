import praw
import json
import sys
import codecs
from datetime import datetime


def get_post_data(submission, sort, sub):

    post = {}
    now = datetime.now()
    post['author'] = str(submission.author)
    post['selftext'] = submission.selftext
    post['id'] = submission.id
    post['subreddit'] = sub
    post['score'] = submission.score
    post['title'] = submission.title
    post['url'] = submission.url
    post['num_comments'] = submission.num_comments
    post['upvote_ratio'] = submission.upvote_ratio
    post['created_utc'] = submission.created_utc
    post['created_normal'] = datetime.utcfromtimestamp(post['created_utc']).strftime('%m-%d-%Y')

    submission.comment_sort = 'best'
    submission.comment_limit = 10
    submission.comments.replace_more(limit=0)
    top_comments = []

    # get top 5 best comments
    for top_comment in submission.comments:
        comment = {}
        comment['text'] = top_comment.body
        comment['score'] = top_comment.score
        comment['link'] = top_comment.permalink
        comment['id'] = top_comment.id
        comment['author'] = str(top_comment.author)
        top_comments.append(comment)

    post['top_comments'] = top_comments
    post['sort'] = sort

    return post

def get_reddit_data():
    reddit = praw.Reddit(
    client_id="77poxuL4XVYzFA",
    client_secret="UfWWVSymGKRdPKh4UwCPFdL2LGc",
    user_agent= "Collecting post data by /u/KimiNoNaWa",
    username="KimiNoNaWa",
    password="!Divisi04")

    subreddits = ["politics"]

    data = {}
    data['politics'] = []
            
    # go through each subreddit
    for sr in subreddits:
        sub = reddit.subreddit(sr)

        count = 0
        for submission in sub.top("year", limit = None):
            if count > 1001:
                break
            
            if submission.created_utc < 1586304000 and submission.created_utc > 1607558399:
                continue
            
            post = get_post_data(submission, "n/a", str(sub))
            data['politics'].append(post)
            count += 1 
    
    print(len(data['politics']))
    
    with open('subreddit_data.json','w', encoding='utf-8') as f: 
        json.dump(data, f, indent=4, sort_keys=True, ensure_ascii=False) 
            

           

if __name__ == "__main__":
    get_reddit_data()
