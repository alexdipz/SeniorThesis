import praw
import json
import sys
import codecs
from datetime import datetime


def get_post_data(submission, sort, sub):

    post = {}
    now = datetime.now()
    post['date_gathered'] = now.strftime("%m/%d/%Y")
    post['author'] = str(submission.author)
    post['selftext'] = submission.selftext
    post['id'] = submission.id
    post['subreddit'] = sub
    post['score'] = submission.score
    post['title'] = submission.title
    post['url'] = submission.url
    post['num_comments'] = submission.num_comments
    post['upvote_ratio'] = submission.upvote_ratio
    post['created'] = submission.created_utc
    
    submission.comment_sort = 'best'
    submission.comment_limit = 5
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

    subreddits = ["politics", "news", "worldnews"]
    
    with open('subreddit_data.json') as f:
        
        data = json.load(f) 
        
        politics = data['politics'] 
        news = data['news']
        worldnews = data['worldnews']

        # go through each subreddit
        for sr in subreddits:
            sub = reddit.subreddit(sr)

            # go through top 10 posts of the day
            for idx, submission in enumerate(sub.top("day")):
                if idx > 10:
                    break
                
                post = get_post_data(submission, "top/day", str(sub))

                if post['subreddit'] == "politics":
                    politics.append(post)
                if post['subreddit'] == "news":
                    news.append(post)
                if post['subreddit'] == "worldnews":
                    worldnews.append(post)
            
            # go through top 10 controversial posts of the day
            for idx, submission in enumerate(sub.controversial()):
                if idx > 10:
                    break
                
                post = get_post_data(submission, "controversial", str(sub))

                if post['subreddit'] == "politics":
                    politics.append(post)
                if post['subreddit'] == "news":
                    news.append(post)
                if post['subreddit'] == "worldnews":
                    worldnews.append(post)
        
        with open('subreddit_data.json','w', encoding='utf-8') as f: 
            json.dump(data, f, indent=4, sort_keys=True, ensure_ascii=False) 
            

           

if __name__ == "__main__":
    get_reddit_data()
