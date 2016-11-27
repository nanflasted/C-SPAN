
#forked from:https://gist.github.com/yanofsky/5436496
#author yanofsky

import tweepy #https://github.com/tweepy/tweepy
import twcred
import csplog
import sys

def getAllTweets(screen_name):
    try:
        #Twitter only allows access to a users most recent 3240 tweets with this method
        consumer_key, consumer_secret, access_key, access_secret = twcred.auth()
        #authorize twitter, initialize tweepy
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_key, access_secret)
        api = tweepy.API(auth)
        
        alltweets = []	
        #make initial request for most recent tweets (200 is the maximum allowed count)
        new_tweets = api.user_timeline(screen_name = screen_name,count=200)
        alltweets.extend(new_tweets)
    
        #save the id of the oldest tweet less one
        oldest = alltweets[-1].id - 1
        #keep grabbing tweets until there are no tweets left to grab
        while len(new_tweets) > 0:
        	print "getting tweets before %s" % (oldest)
        	#all subsiquent requests use the max_id param to prevent duplicates
        	new_tweets = api.user_timeline(screen_name = screen_name,count=200,max_id=oldest)
        	#save most recent tweets
        	alltweets.extend(new_tweets)
        	#update the id of the oldest tweet less one
        	oldest = alltweets[-1].id - 1
        	print "...%s tweets downloaded so far" % (len(alltweets))
        #transform the tweepy tweets into a 2D array that will populate the text
        outtweets = [tweet.text.encode("utf-8") for tweet in alltweets]
        
        with open('./data/input.txt','w+') as f:
            map(f.write,outtweets)
        return True
    except Exception as e:
        csplog.logexc(sys.exc_info())
        return False
    return False

