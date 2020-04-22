import json
import logging
import random

from control_center.text_generator import DumbReplier, DumbReplierTypes
from wrappers.mongo_wrapper import MongoAPI
from wrappers.neo4j_wrapper import Neo4jAPI
from wrappers.postgresql_wrapper import PostgresAPI
from wrappers.rabbitmq_wrapper import Rabbitmq

from control_center.policies_types import PoliciesTypes
from control_center.PEP import PEP
from bots.messages_types import ServerToBot, BotToServer

import log_actions

log = logging.getLogger('Database Writer')
log.setLevel(logging.DEBUG)
handler = logging.StreamHandler(open("dbwritter.log", "w"))
handler.setFormatter(logging.Formatter(
	"[%(asctime)s]:[%(levelname)s]:%(module)s - %(message)s"))
log.addHandler(handler)


class Control_Center(Rabbitmq):
	"""
	Class to smulate the behaviour of a bot:
	On receiving a message from a message broker, this class will act accordingly
	"""

	def __init__(self):
		"""
		This will start instaces for all the DB's API
		"""

		super().__init__()

		self.postgres_client = PostgresAPI()
		self.mongo_client = MongoAPI()
		self.neo4j_client = Neo4jAPI()
		self.pep = PEP()

	def action(self, message):
		message_type = message['type']
		log.info(f"Received new action: {message['bot_id']} wants to do {message_type.name}")

		log.debug(f"Received message of type {message_type}")

		if message_type == BotToServer.EVENT_TWEET_LIKED:
			self.like_tweet(message)

		elif message_type == BotToServer.EVENT_TWEET_RETWEETED:
			self.retweet(message)

		elif message_type == BotToServer.EVENT_TWEET_REPLIED:
			self.reply_tweet(message)

		elif message_type == BotToServer.QUERY_TWEET_LIKE:
			self.request_tweet_like(message)

		elif message_type == BotToServer.QUERY_TWEET_RETWEET:
			self.request_retweet(message)

		elif message_type == BotToServer.QUERY_TWEET_REPLY:
			self.request_tweet_reply(message)

		elif message_type == BotToServer.QUERY_FOLLOW_USER:
			self.request_follow_user(message)

		elif message_type == BotToServer.SAVE_USER:
			self.save_user(message)

		elif message_type == BotToServer.SAVE_TWEET:
			self.save_tweet(message)

		elif message_type == BotToServer.SAVE_DIRECT_MESSAGES:
			self.save_dm(message)

		elif message_type == BotToServer.EVENT_USER_BLOCKED:
			self.error(message)

		elif message_type == BotToServer.SAVE_FOLLOWERS:
			self.find_followers(message)

		elif message_type == BotToServer.QUERY_KEYWORDS:
			self.send_keywords(message)

	# Need DB API now
	def __follow_user(self, user1_id, user2_id, user1_is_bot=False):
		"""
		Action to follow user:
				Calls neo4j to add new relation between user (bot or normal user) and user
				Calls postgres_stats to add new log with the action details

		@param data: dict containing bot and the user he's following
		"""
		log.debug(f"User {user1_id} is following {user2_id}")
		type1 = "Bot" if self.neo4j_client.check_bot_exists(user1_id) else "User"
		type2 = "Bot" if self.neo4j_client.check_bot_exists(user2_id) else "User"

		relationship = {
			"id_1": user1_id,
			"id_2": user2_id,
			"type_1": type1,
			"type_2": type2
		}

		if self.neo4j_client.check_relationship_exists(relationship):
			log.debug(f"User {user1_id} already follows the user {user2_id}")
			return
		self.neo4j_client.add_relationship(relationship)

		if user1_is_bot:
			self.postgres_client.insert_log({
				"bot_id": user1_id,
				"action": log_actions.FOLLOW,
				"target_id": user2_id
			})
			log.info(f"Bot {user1_id} successfully followed the user {user2_id}")

		log.info("Saved follow relation with success")

	def like_tweet(self, data):
		"""
		Action to like tweet:
				Calls postgres_stats to add new log

		@param data dict with the bot id and the tweet he liked
		"""
		result = self.postgres_client.insert_log({
			"bot_id": data["bot_id"],
			"action": log_actions.TWEET_LIKE,
			"target_id": data['data']['id']
		})
		if result['success']:
			log.debug(f"Bot {data['bot_id']} liked tweet {data['data']['id']}")
		else:
			log.debug(f"Bot {data['bot_id']} could not like tweet {data['data']['id']}")
			log.error(f"Bot like caused error {result['error']}")

	def retweet(self, data):
		"""
		Action to retweet:
				Calls postgres_stats to add new log

		@param data: dict containing bot and the tweet he retweeted
		"""
		result = self.postgres_client.insert_log({
			"bot_id": data["bot_id"],
			"action": log_actions.RETWEET,
			"target_id": data['data']['id']
		})
		if result['success']:
			log.debug(f"Bot {data['bot_id']} retweeted {data['data']['id']}")
		else:
			log.debug(f"Bot {data['bot_id']} could not retweet tweet {data['data']['id']}")
			log.error(f"Bot like caused error {result['error']}")

	def reply_tweet(self, data):
		"""
		Action to reply a tweet:
				Calls progres_stats to add what the bot replied and to which tweet

		@param data: dict contaning bot and the reply they made
		"""
		result = self.postgres_client.insert_log({
			"bot_id": data["bot_id"],
			"action": log_actions.TWEET_REPLY,
			"target_id": data['data']['id']
		})
		if result['success']:
			log.debug(f"Bot {data['bot_id']} replied with {data['data']['id']}")
		else:
			log.debug(f"Bot {data['bot_id']} could not reply with {data['data']['id']}")
			log.error(f"Bot like caused error {result['error']}")

	def request_tweet_like(self, data):
		"""
		Action to request a like on tweeter:
				Calls the PEP to request a like
				Adds the log to postgres_stats, for the request and its result
				The result is based on the PDP methods

		@param data: dict containing the bot id and the tweet id
		"""
		log.info(f"Bot {data['bot_id']} requests a like to tweet {data['data']['id']}")
		self.postgres_client.insert_log({
			"bot_id": data["bot_id"],
			"action": log_actions.LIKE_REQ,
			"target_id": data['data']['id']
		})

		request_accepted = self.pep.receive_message({
			"type": PoliciesTypes.REQUEST_TWEET_LIKE,
			"bot_id": data['bot_id'],
			"user_id": data['data']['user'],
			"tweet_id": data['data']['id'],
			"tweet_text": data['data']['text'],
			"tweet_entities": data['data']['entities']
		})

		if request_accepted:
			log.info(f"Bot {data['bot_id']} request accepted to like a tweet {data['data']['id']}")
			self.postgres_client.insert_log({
				"bot_id": data["bot_id"],
				"action": log_actions.LIKE_REQ_ACCEPT,
				"target_id": data['data']['id']
			})
			self.send(
				data['bot_id'], ServerToBot.LIKE_TWEETS,
				data['data']['id']
			)
		else:
			log.warning(f"Bot {data['bot_id']} request denied to like a tweet {data['data']['id']}")
			self.postgres_client.insert_log({
				"bot_id": data["bot_id"],
				"action": log_actions.LIKE_REQ_DENY,
				"target_id": data['data']['id']
			})

	def request_retweet(self, data):
		"""
		Action to request a retweet:
				Calls the PEP to request the retweet
				Adds the log to postgres_stats, for the request and its result
				The result is based on the PDP methods

		@param data: dict containing the bot id and the tweet id
		"""
		log.info(f"Bot {data['bot_id']} requests a retweet {data['data']['id']}")
		self.postgres_client.insert_log({
				"bot_id": data["bot_id"],
				"action": log_actions.RETWEET_REQ,
				"target_id": data['data']['id']
		})
		request_accepted = self.pep.receive_message({
			"type": PoliciesTypes.REQUEST_TWEET_RETWEET,
			"bot_id": data['bot_id'],
			"user_id": data['data']['user'],
			"tweet_id": data['data']['id'],
			"tweet_text": data['data']['text'],
			"tweet_entities": data['data']['entities']
		})

		if request_accepted:
			log.info(f"Bot {data['bot_id']} request accepted to retweet {data['data']['id']}")
			self.postgres_client.insert_log({
				"bot_id": data["bot_id"],
				"action": log_actions.RETWEET_REQ_ACCEPT,
				"target_id": data['data']['id']
			})
			self.send(
				data['bot_id'],
				ServerToBot.RETWEET_TWEETS, data['data']['id']
			)
		else:
			log.warning(f"Bot {data['bot_id']} request denied to retweet {data['data']['id']}")
			self.postgres_client.insert_log({
				"bot_id": data["bot_id"],
				"action": log_actions.RETWEET_REQ_DENY,
				"target_id": data['data']['id']
			})

	def request_tweet_reply(self, data):
		"""
		Action to request a reply:
				Calls the control center to request the reply
				Adds the log to postgres_stats, for the request and its result
				The result is based on the Policy API object

		@param data: dict containing the bot id and the tweet id
		"""
		log.info(f"Bot {data['bot_id']} requests a reply {data['data']['id']}")

		self.postgres_client.insert_log({
				"bot_id": data["bot_id"],
				"action": log_actions.REPLY_REQ,
				"target_id": data['data']['id']
		})
		request_accepted = self.pep.receive_message({
			"type": PoliciesTypes.REQUEST_TWEET_REPLY,
			"bot_id": data['bot_id'],
			"tweet_id": data['data']['id'],
			"user_id": data['data']['user'],
			"tweet_text": data['data']['text'],
			"tweet_entities": data['data']['entities'],
			"tweet_in_reply_to_status_id_str": data['data']['in_reply_to_status_id_str'],
			"tweet_in_reply_to_user_id_str": data['data']['in_reply_to_user_id_str'],
			"tweet_in_reply_to_screen_name": data['data']['in_reply_to_screen_name']
		})

		if request_accepted:
			log.info(f"Bot {data['bot_id']} request accepted to reply {data['data']['id']}")

			self.postgres_client.insert_log({
				"bot_id": data["bot_id"],
				"action": log_actions.REPLY_REQ_ACCEPT,
				"target_id": data['data']['id']
			})

			replier = DumbReplier(random.choice(list(DumbReplierTypes.__members__.values())))
			reply_text = replier.generate_response(data['data']['text'])
			log.info(f"Sending reply text <{reply_text}>")

			self.send(data['bot_id'], ServerToBot.POST_TWEET, {
				"reply_id": data['data']['id'],
				"text": reply_text
			})
		else:
			log.warning(f"Bot {data['bot_id']} request denied to reply {data['data']['id']}")
			self.postgres_client.insert_log({
				"bot_id": data["bot_id"],
				"action": log_actions.REPLY_REQ_DENY,
				"target_id": data['data']['id']
			})

	def request_follow_user(self, data):
		"""
		Action to request a follow:
				Calls the control center to request the follow
				Adds the log to postgres_stats, for the request and its result
				The result is based on the Policy API object

		@param data: dict containing the bot id and the tweet id
		"""
		
		log.info(f"Bot {data['bot_id']} requests a follow from {data['data']['id']}")

		self.postgres_client.insert_log({
				"bot_id": data["bot_id"],
				"action": log_actions.FOLLOW_REQ,
				"target_id": data['data']['id']
		})
		request_accepted = self.pep.receive_message({
			"type": PoliciesTypes.REQUEST_FOLLOW_USER,
			"bot_id": data['bot_id'],
			"user_id": data['data']['id']
		})

		if request_accepted:
			log.info(f"Bot {data['bot_id']} request accepted to follow {data['data']['id']}")

			self.postgres_client.insert_log({
				"bot_id": data["bot_id"],
				"action": log_actions.FOLLOW_REQ_ACCEPT,
				"target_id": data['data']['id']
			})
			self.send(
				data['bot_id'],
				ServerToBot.FOLLOW_USERS,
				{
					"type": "id",
					"data": [data['data']['id']]
				}
			)
		else:
			log.warning(f"Bot {data['bot_id']} request denied to follow {data['data']['id']}")
			self.postgres_client.insert_log({
				"bot_id": data["bot_id"],
				"action": log_actions.FOLLOW_REQ_DENY,
				"target_id": data['data']['id']
			})

	def save_user(self, data):
		"""
		Stores info about a user:
				Calls the neo4j and the mongo object to update or store the user be it a bot or a user)
				Adds the log of the operation to postgres_stats
				If the user is a bot, must also call the Policy API object

		@param data: dict containing the id of the bot and the user object
		"""

		log.info("Saving User")

		user, bot_id = data["data"], data["bot_id"]

		exists = self.neo4j_client.check_bot_exists(bot_id)
		if not exists:
			log.info(f"Bot {bot_id} is new to the party")

			# save bot to mongo and neo4j
			self.neo4j_client.add_bot({
				"id": bot_id,
				"name": data['bot_name'],
				"username": data['bot_screen_name']
			})

			# we send the list of initial users to follow
			follow_list = self.pep.first_time_policy()
			self.send(bot_id, ServerToBot.FOLLOW_USERS, {
				"type": "screen_name",
				"data": follow_list,
			})

		is_bot = self.neo4j_client.check_bot_exists(user["id"])
		if is_bot:
			log.info("It's a bot that's already been registered in the database")
			# Update the info of the bot
			self.mongo_client.update_users(
				match={"id": user['id']},
				new_data=user,
				all=False
			)
			self.neo4j_client.update_bot({
				"id": user['id'],
				"name": user['name'],
				"username": user['screen_name']
			})
		else:
			if self.neo4j_client.check_user_exists(user["id"]):
				log.info(f"User {user['id']} has already been registered in the database")
				self.mongo_client.update_users(
					match={"id": user['id']},
					new_data=user,
					all=False
				)
				self.neo4j_client.update_user({
					"id": user["id"],
					"name": user['name'],
					"username": user['screen_name']
				})
				self.postgres_client.insert_log({
					"bot_id": bot_id,
					"action": log_actions.UPDATE_USER,
					"target_id": user['id']
				})
			else:
				log.info(
					f"User {data['data']['id']} is new to the party")
				self.mongo_client.insert_users(data["data"])
				self.neo4j_client.add_user({
					"id": user["id"],
					"name": user['name'],
					"username": user['screen_name']
				})
				self.postgres_client.insert_log({
					"bot_id": bot_id,
					"action": log_actions.INSERT_USER,
					"target_id": user['id']
				})
			self.postgres_client.insert_user({
				"user_id": user["id"],
				"followers": user["followers_count"],
				"following": user["friends_count"]
			})

		if 'following' in user:
			self.__follow_user(bot_id, user['id'], user1_is_bot=True)

	def save_tweet(self, data):
		"""
		Stores info about a tweet:
				Calls the mongo object to save or update a tweet
				Adds the operation log to postgress_stats

		@param data: dict containing the id of the tweet to bee saved
		"""
		tweet_exists = self.mongo_client.search(
			collection="tweets",
			query={"id": data["data"]["id"]},
			single=True
		)
		if tweet_exists:
			log.info(f"Updating tweet {data['data']['id']}")
			self.mongo_client.update_tweets(
				match={"id": data["data"]['id']},
				new_data=data["data"],
				all=False
			)
			self.postgres_client.insert_log({
				"bot_id": data["bot_id"],
				"action": log_actions.UPDATE_TWEET,
				"target_id": data['data']['id']
			})
		else:
			log.info(f"Inserting tweet {data['data']['id']}")
			self.mongo_client.insert_tweets(data['data'])
			self.postgres_client.insert_log({
				"bot_id": data["bot_id"],
				"action": log_actions.INSERT_TWEET,
				"target_id": data['data']['id']
			})
		self.postgres_client.insert_tweet({
			"tweet_id": data['data']['id'],
			"user_id": data['data']['user'],
			"likes": data['data']['favorite_count'],
			"retweets": data['data']['retweet_count']
		})

	def save_dm(self, data):
		"""
		Stores the info about a bot's direct messages:
				Calls the mongo object to save or update a dm
				Adds the operation log to postgress_stats

		@param data: dict containignt the id of the bot and the DMs
		"""
		for message in data['data']:
			message["bot_id"] = data["bot_id"]
			message_exists = self.mongo_client.search(
				collection="messages",
				query={"id": message["bot_id"]},
				single=True
			)
			if not message_exists:
				log.info(f"New message {data['data']['id']}")
				self.postgres_client.insert_log({
					"bot_id": data["bot_id"],
					"action": log_actions.INSERT_MESSAGE,
					"target_id": data['data']['id']
				})
				self.mongo_client.insert_messages(message)

	def error(self, data):
		"""
		Stores error that may have occured in the running of a bot:
				Calls the postgres stats to log the error

		@param data: dict with the id of a bot and the error object
		"""
		self.postgres_client.insert_log({
			"bot_id": data["bot_id"],
			"action": f"Error occured for {data['data']}"
		})
		log.error(f"Error in trying to do action <{data['data']}>")

	def find_followers(self, data):
		"""
		Function that writes the follow relationship on the Neo4j API database;
		The function will also request for the bot who sent the message to follow the users who follow
		one of the bot's followers

		@param data: dict with the id of a bot and a second dictionary with the bot's followers' ID as keys that map
		to his followers
		"""
		log.info(f"Starting to create the Follow Relationship for bot {data['bot_id']}")
		for follower in data["data"]:
			self.postgres_client.insert_log({
				"bot_id": data['bot_id'],
				"action": f"Save list of followers for {follower}"
			})
			log.info(f"Save list of followers for {follower}")

			# Verify if the follower is on the database as a user
			is_user = self.neo4j_client.check_user_exists(follower)
			is_bot = self.neo4j_client.check_bot_exists(follower)
			if not (is_user or is_bot):
				# The follower isn't registered in the database, so that must be handled
				self.save_user({
					"bot_id": data["bot_id"],
					"data": {
						"id": int(follower),
						"name": "",
						"screen_name": "",
						"followers_count": 0,
						"friends_count": 0
					}
				})

			for follower_follower in data["data"][follower]:
				follower_follower_is_user = self.neo4j_client.check_user_exists(
					follower_follower)
				if follower_follower_is_user:
					self.request_follow_user({
						"bot_id": data['bot_id'],
						"data": {"id": follower_follower}
					})

				self.follow_user({
					"bot_id": int(follower),
					"data": {
						"id": follower_follower
					}
				})

	def send_keywords(self, data):
		log.info("Starting to sending the keywords to the bot")

		bot_id = data["bot_id"]

		policies = self.postgres_client.search_policies({
			"bot_id": bot_id, "filter": "Keywords"
		})

		response = []
		if policies['success']:
			policy_list = policies['data']
			log.debug(f"Obtained policies: {policy_list}")

			if len(policy_list) > 0:
				response = random.choice(policy_list)["params"]

			log.debug(f"Keywords to send: {response}")

			log.info(f"Sending keywords {response} to bot {response}")
		self.send(
			bot_id,
			ServerToBot.KEYWORDS,
			response
		)

	def send(self, bot, message_type, params):
		"""
		Function the task uses to send messages through rabbit

		@param bot: id of the bot to reply
		@param message_type: ResponseTypes object with the type of message
		@param params: dict with arguments of the message
		"""
		log.info(f"Sending {message_type.name} to Bot with ID: <{bot}>")
		log.debug(f"Content: {params}")
		payload = {
			'type': message_type,
			'params': params
		}
		try:
			self._send(routing_key='tasks.twitter.' + str(bot), message=payload)
			# self._close()
		except Exception as e:
			log.error(f"FAILED TO SEND MESSAGE: {e}")

	def received_message_handler(self, channel, method, properties, body):
		log.info("MESSAGE RECEIVED")
		message = json.loads(body)
		self.action(message)

	def run(self):
		self._receive()
		self._close()

	def close(self):
		self.neo4j_client.close()
		self.pep.pdp.close()
