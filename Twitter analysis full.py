#!/usr/bin/env python
# coding: utf-8

# In[1]:


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoAlertPresentException

import unittest, time, re
from bs4 import BeautifulSoup as bs
from dateutil import parser
import pandas as pd
import itertools
import matplotlib.pyplot as plt


# In[2]:


## Define which browser to use & open login page
driver = webdriver.Firefox(executable_path=r"C:\Users\Downloads\geckodriver-v0.24.0-win64 (1)\geckodriver.exe")
driver.get('https://twitter.com/login')
driver.implicitly_wait(5)
## implicity_wait makes the bot wait 5 seconds before every action
    ## so the site content can load up
    
## Define the user and email combo. 
bot_name = "TwitterBot"
bot_email = "insertemail@gmail"
bot_password = "password"
print(bot_name + " is getting started")


# In[3]:


## This is looking for the element with xpath associated w/username box
text_field_username = driver.find_element_by_xpath('//*[@id="page-container"]/div/div[1]/form/fieldset/div[1]/input')
text_field_username.clear()
text_field_username.send_keys(bot_email)

##1 second delay between username and password entry
time.sleep(1)

## This is looking for the element with class name "js-password-field" (password)
textfield_pass = driver.find_element_by_class_name('js-password-field')
textfield_pass.clear()
textfield_pass.send_keys(bot_password)

## This is looking for the element with the xpath associated w/enter button
submit_button  = driver.find_element_by_xpath('//*[@id="page-container"]/div/div[1]/form/div[2]/button')
submit_button.click()

##I had an issue trying to use the find_element_by_id with Twitter, so I used the xpath model to ensure it worked. 
##password issue: switched to class_name error:NoSuchElementException: Message: Unable to locate element: [id="session[password]"]
##The program would run but not enter the password. I found a way to circumvent this issue by adding a delay (1 sec) in entering the username then password![image.png](attachment:image.png)

# In[4]:


##locate the follower tab and select

followers_button = driver.find_element_by_xpath('//*[@id="page-container"]/div[1]/div[1]/div/div[2]/ul/li[3]/a')
followers_button.click()


# In[5]:


df = pd.read_csv(r'C:\Desktop\Python\twitter_data.csv', encoding = "ISO-8859-1")
arr = df.usernames


# In[6]:


main = pd.DataFrame(data = {
        'user': ['swyx'],
        'text': ['text'],
        'tweetTimestamps': ['tweetTimestamps'],
        'engagements': ['engagements'],
        'name': ['name'],
        'loc': ['loc'],
        'url': ['url'],
        'stats_tweets': ['stats_tweets'],
        'stats_following': ['stats_following'],
        'stats_followers': ['stats_followers'],
        'stats_favorites': ['stats_favorites'],
    })


# In[7]:


def getTimestamps(x):
    temp = x.findAll('span', '_timestamp')
    if len(temp) > 0:
        return temp[0].get('data-time')
    else:
        return None
# now get the user's own timeline
for i in range(0,len(arr)):
    currentUser = arr[i]
    print('doing user:' + str(i) + ' ' + currentUser)
    driver.base_url = "https://twitter.com/" + currentUser + '/with_replies'
    driver.get(driver.base_url)
    html_source = driver.page_source
    dailyemail_links = html_source.encode('utf-8')
    soup=bs(dailyemail_links, "lxml")
    time.sleep(2)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)
    # name
    name = soup.find('a', "ProfileHeaderCard-nameLink").text
    # loc
    temp = soup.find('span', 'ProfileHeaderCard-locationText')
    temp = temp.text if temp else ''
    loc = temp.strip() if temp else ''
    # url
    temp = soup.find('span', 'ProfileHeaderCard-urlText')
    temp = temp.a if temp else None
    temp2 = temp.get('title') if temp else None
    url = temp2 if temp2 else (temp.get('href') if temp else None)
    # stats
    temp = soup.find('a',{'data-nav': 'tweets'})
    stats_tweets = temp.find('span', 'ProfileNav-value')['data-count'] if temp else 0
    temp = soup.find('a',{'data-nav': 'following'})
    stats_following = temp.find('span', 'ProfileNav-value')['data-count'] if temp else 0
    temp = soup.find('a',{'data-nav': 'followers'})
    stats_followers = temp.find('span', 'ProfileNav-value')['data-count'] if temp else 0
    temp = soup.find('a',{'data-nav': 'favorites'})
    stats_favorites = temp.find('span', 'ProfileNav-value')['data-count'] if temp else 0
    # all text
    text = [''.join(x.findAll(text=True)) for x in soup.body.findAll('p', 'tweet-text')]
    # most recent activity
    alltweets = soup.body.findAll('li', attrs={'data-item-type':'tweet'})
    tweetTimestamps = list(map(getTimestamps, alltweets)) if len(alltweets) > 0 else 0
    # engagements
    noretweets = [x.findAll('span', 'ProfileTweet-actionCount') for x in alltweets if not x.div.get('data-retweet-id')]
    templist = [x.findAll('span', 'ProfileTweet-actionCount') for x in alltweets if not x.div.get('data-retweet-id')]
    templist = [item for sublist in templist for item in sublist]
    engagements = sum([int(x.get('data-tweet-stat-count')) for x in templist if x.get('data-tweet-stat-count')])
    main = pd.concat([main, pd.DataFrame(data = {
        'user': [currentUser],
        'text': [text],
        'mostrecentTimestamp': [tweetTimestamps],
        'engagements': [engagements],
        'name': [name],
        'loc': [loc],
        'url': [url],
        'stats_tweets': [stats_tweets],
        'stats_following': [stats_following],
        'stats_favorites': [stats_favorites],
    })])
    main.to_csv(r'C:\Python\twitter_data_full.csv')

