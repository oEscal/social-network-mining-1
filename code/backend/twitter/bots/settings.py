import os


# -----------------------------------------------------------
# Tweepy errors
# -----------------------------------------------------------

ACCOUNT_SUSPENDED_ERROR_CODES = [63, 64, 326]
FOLLOW_USER_ERROR_CODE = 161


# -----------------------------------------------------------
# Tweepy settings
# -----------------------------------------------------------

MAX_NUMBER_TWEETS_RETRIEVE_TIMELINE = 5


# -----------------------------------------------------------
# Redis
# -----------------------------------------------------------

REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')


# -----------------------------------------------------------
# Other settings
# -----------------------------------------------------------

WAIT_TIME_BETWEEN_WORK = 60*60*2            # two hours
WAIT_TIME_RANDOM_STOP = 60*30               # half an hour
WAIT_TIME_IM_ALIVE = 30                     # 30 seconds
BOT_TTL = 60*60*24							# one day
