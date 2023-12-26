# villa-ML
# this bot runs on MLX quick profile, fetching the first 50+ posts in a subreddit, and outputs the popular posts info(creation time, link, title, and upvote number) into your excel.xlsx
!! popular posts are assessed by upvote number.
!! first 50+is a reasonal number. Upon investigation, popular posts within 24 hours often does not appear in after first 50.

# your need to enter your MLX account credential
USERNAME = "youraccount"
PASSWORD = "yourpassword"

# please provide the subreddits to query in a excel.xlsx file. Name your only workbook "subreddits", making only one collumn in it. Collumn title would be "Title". Provide your subreddits in this collmn.
Check all subreddits here: https://www.redditlist.com/
Please check an example exel file coming along.

# please provide your excel.xlsx full filepath to "filepath" variable.

# please note reddit does not like VPN(data-center) IP. So please just use your real connection or insert a residential proxy into your quick profile.
Important!!
Due to the fact reddit does not load all 50+ pages at once, you need to scroll down to the page bottomn multiple times to load all these posts.
However, reddit can take few seconds to load the next batch of posts depending on your connection speed. Therefore:

1. if you use residential proxy for your quick profile, try to let the driver to sleep more times after your scroll down to bottom each time in getPost func. 
Otherwise, the bot might not get 50+ posts within the scroll times(25) allowed!!!
2. if you use your real connection, for example your home wifi, you can decrease the sleep time.
