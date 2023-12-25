from selenium import webdriver
from selenium.webdriver.chromium.options import ChromiumOptions
from selenium.webdriver.common.by import By
import hashlib
import requests

import datetime
import time
import pytz
import pandas as pd
from pandas import ExcelWriter

#input your MLX account login credentials
USERNAME = "your MLX account email"
PASSWORD = "your MLX account pass"

MLX_BASE = "https://api.multilogin.com"
MLX_LAUNCHER = "https://launcher.mlx.yt:45001/api/v1"
HEADERS = {
 'Accept': 'application/json',
 'Content-Type': 'application/json'
 }

filepath='your subreddit excel filepath'
def getToken() -> str:
     payload = {'email': USERNAME,'password': hashlib.md5(PASSWORD.encode()).hexdigest()}
     response = requests.post(f'{MLX_BASE}/user/signin', json=payload)
     if(response.status_code != 200):
        print(f'\nError during login: {response.text}\n')
     response_json = response.json()
     token = response_json['data']['token']
     return token

HEADERS['Authorization'] = 'Bearer ' + getToken()
def start_quickProfile()->webdriver:
    Payload={
        'browser_type': 'mimic',
        'os_type': 'windows',
        "core_version": 120,
        "automation": "selenium",
        # Reddit does not like VPN, if not using residential proxy, please use your real ISP connection, not VPN
        "proxy": {
            "host": "rotating.proxyempire.io",
            "type": "http",
            "port": 9000,
            "username": "yzBYkTa4iCrZYvmn",
            "password": "wifi;us;spectrum;new+york;massena"
        },
        'parameters': {
            'flags': {
                'navigator_masking': 'mask',
                'audio_masking': 'natural',
                'localization_masking': 'mask',
                'geolocation_popup': 'prompt',
                'geolocation_masking': 'mask',
                'timezone_masking': 'mask',
                'graphics_noise': 'natural',
                'graphics_masking': 'natural',
                'webrtc_masking': 'mask',
                'fonts_masking': 'mask',
                'media_devices_masking': 'natural',
                'screen_masking': 'mask',
                'proxy_masking': 'custom',
                'ports_masking': 'mask',
            },
            'fingerprint': {},
        },
    }
    response = requests.post(url=f'{MLX_LAUNCHER}/profile/quick', json=Payload, headers=HEADERS)
    if (response.status_code != 200):
        print(f'\nError during launch quick profile: {response.text}\n')
    resp_json=response.json()
    port=resp_json['status']['message']
    driver = webdriver.Remote(command_executor=f'http://127.0.0.1:{port}', options=ChromiumOptions())
    return driver
def getSubreddit(file)->list:
    """This function will load an excel file with subreddit title and return a list of subreddits"""
    df=pd.read_excel(file,sheet_name='subreddits')
    subreddits=df['Title'].tolist()
    return subreddits
def getPost(driver,topic):
    """This function will get a list of information for the fist 50+ posts from a subreddit"""
    driver.get(f'https://www.reddit.com/r/{topic}')
    time.sleep(5)
    # Scroll down to page buttom multiple times to make sure to enough posts show up
    for y in range(25):
        PostEles = driver.find_elements(By.XPATH, '//*[@id="main-content"]//shreddit-post')
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        """Sleep longer time, if you use a residential proxies for quick profile! You might scroll down multiple times, 
        but the page is not loading fully due to slow connection of residential proxies"""
        time.sleep(6)
        if len(PostEles) > 50:
            print(f'●Find {len(PostEles)} posts, scroll down {y} times')
            break
    Posts = []
    """process post data in to dictionary: HoursAgo- when this post is published; UpVote- like number of the post;
    Link: link of the post; Title: title of the post"""
    for PostEle in PostEles:
        PostTimeEle = PostEle.find_element(By.CSS_SELECTOR, 'span>span>faceplate-timeago>time').get_attribute('datetime')
        PostTime = datetime.datetime.strptime(PostTimeEle, '%Y-%m-%dT%H:%M:%S.%f%z')
        NowTime = datetime.datetime.now(tz=pytz.timezone('UTC'))
        OnePost = {'HoursAgo': round((NowTime-PostTime).total_seconds()/3600),
                   'Upvote': PostEle.shadow_root.find_element(By.CSS_SELECTOR,'div>span faceplate-number').get_attribute('number'),
                   'Link': PostEle.find_element(By.XPATH, 'a[1]').get_attribute('href'),
                   'Title': PostEle.find_element(By.XPATH, 'a[1]').get_attribute('aria-label')}
        Posts.append(OnePost)
    print("●Get posts done, see below a list: ")
    print(Posts)
    return Posts

def filterPost(Posts)->list:
    """This function will filter out a list of posts published within one day with an upvote number over 1000"""
    TrendingPost = []
    for Post in Posts:
        # change hours and upvote number here to meet your gauge for "viral posts"
        if Post['HoursAgo'] < 24 and int(Post['Upvote']) > 1000:
            TrendingPost.append(Post)
        else:
            continue
    print('●Filter trending posts done, see below a list:')
    print(TrendingPost)
    return TrendingPost
def automation():
    """This function will output qualified posts and save to local excel file"""
    time.sleep(5)
    driver = start_quickProfile()
    subreddits = getSubreddit(file=filepath)
    print(f'●All subreddits: {', '.join(map(str, subreddits))}')
    total_number = len(subreddits)
    # save qualified posts into local excel file
    with pd.ExcelWriter(filepath) as writer:
        df1 = pd.DataFrame(subreddits, columns=['Title'])
        df1.to_excel(writer, sheet_name='subreddits')
        for i, subreddit in enumerate(subreddits):
            print(f'●Current subreddit is "{subreddit}", getting posts on it...')
            TrendingPosts = filterPost(Posts=getPost(driver, topic=subreddit))
            if len(TrendingPosts) == 0:
                df2 = pd.DataFrame(['No trending posts for this subreddit published within 24 hours!!!!!'])
                df2.to_excel(writer, sheet_name=subreddit)
                writer._save()
                print("No trending posts for this subreddit published within 24 hours",)
                if i+1 < total_number:
                    print('●Go to next subreddit page=======>>>>>>>>>>\n')
                else:
                    print("Get all trending subreddit post done")
            else:
                df2 = pd.DataFrame(TrendingPosts)
                df2.to_excel(writer,sheet_name=subreddit)
                writer._save()
                print(f'●No.{i+1} subreddit: "{subreddit}" trending posts saved, total subreddit count: {total_number}')
                if i+1 < total_number:
                    print('●Go to next subreddit page=======>>>>>>>>>>\n')
                else:
                    print("Get all trending subreddit post done")
    driver.close()
if __name__=='__main__':
    automation()


