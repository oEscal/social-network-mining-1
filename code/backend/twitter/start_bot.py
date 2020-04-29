## @package twitter

import os

from bots.rabbit_messaging import MessagingSettings
import tweepy
from bots.twitter_bot import TwitterBot
from credentials import TASKS_EXCHANGE, TASKS_ROUTING_KEY_PREFIX, TASKS_QUEUE_PREFIX, LOG_EXCHANGE, LOG_ROUTING_KEY, \
    QUERY_EXCHANGE, QUERY_ROUTING_KEY, DATA_EXCHANGE, DATA_ROUTING_KEY, RABBITMQ_USERNAME, RABBITMQ_PASSWORD, VHOST, \
    RABBITMQ_FULL_HTTP_URL
from tweepy.binder import bind_api

if __name__ == "__main__":
    bot_id = 1244051405721255937 #int(os.environ.get('BOT_ID'))

    messaging_settings = {
        TASKS_EXCHANGE: MessagingSettings(exchange=TASKS_EXCHANGE, routing_key=f"{TASKS_ROUTING_KEY_PREFIX}.{bot_id}",
                                          queue=f"{TASKS_QUEUE_PREFIX}-{bot_id}"),
        LOG_EXCHANGE: MessagingSettings(exchange=LOG_EXCHANGE, routing_key=LOG_ROUTING_KEY),
        QUERY_EXCHANGE: MessagingSettings(exchange=QUERY_EXCHANGE, routing_key=QUERY_ROUTING_KEY),
        DATA_EXCHANGE: MessagingSettings(exchange=DATA_EXCHANGE, routing_key=DATA_ROUTING_KEY)
    }

    consumer_key = os.environ.get('CONSUMER_KEY', '')
    consumer_secret = os.environ.get('CONSUMER_SECRET', '')
    token = os.environ.get('TOKEN', '')
    token_secret = os.environ.get('TOKEN_SECRET', '')
    proxy = os.environ.get('PROXY', 'socks5h://localhost:9050')


    class MYAPI(tweepy.API):
        def __init__(self, auth_handler, wait_on_rate_limit, proxy):
            super().__init__(auth_handler=auth_handler, wait_on_rate_limit=wait_on_rate_limit, proxy=proxy)

        @property
        def home_timeline(self):
            """ :reference: https://developer.twitter.com/en/docs/tweets/timelines/api-reference/get-statuses-home_timeline
                :allowed_param:'since_id', 'max_id', 'count'
            """
            return bind_api(
                api=self,
                path='/statuses/home_timeline.json',
                payload_type='status', payload_list=True,
                allowed_param=['since_id', 'max_id', 'count', 'tweet_mode'],
                require_auth=True
            )


    twitter_auth = tweepy.OAuthHandler(consumer_key=consumer_key, consumer_secret=consumer_secret)
    twitter_auth.set_access_token(key=token, secret=token_secret)
    bot = TwitterBot(RABBITMQ_FULL_HTTP_URL, RABBITMQ_USERNAME, RABBITMQ_PASSWORD, VHOST, messaging_settings, bot_id,
                     MYAPI(auth_handler=twitter_auth, wait_on_rate_limit=True, proxy=proxy))
    bot.run()
