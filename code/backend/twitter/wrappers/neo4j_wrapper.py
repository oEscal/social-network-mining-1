## @package twitter.wrappers
# coding: UTF-8

import logging
from neo4j import GraphDatabase
import credentials
<<<<<<< HEAD
from neo4j_labels import BOT_LABEL, USER_LABEL, TWEET_LABEL, WROTE_LABEL,\
    RETWEET_LABEL, REPLY_LABEL, FOLLOW_LABEL, QUOTE_LABEL
=======
import json
>>>>>>> f0a4702049bcf0a93998f6387869d9b087ad7dca

log = logging.getLogger("Neo4j")
log.setLevel(logging.DEBUG)
handler = logging.StreamHandler(open("neo4j.log", "w"))
handler.setFormatter(
    logging.Formatter("[%(asctime)s]:[%(levelname)s]:%(module)s - %(message)s")
)
log.addHandler(handler)


class Neo4jAPI:
    def __init__(self, FULL_URL=credentials.NEO4J_FULL_URL):
        log.debug("Connecting to Neo4j")
        self.driver = GraphDatabase.driver(
            "bolt://" + FULL_URL,
            auth=(credentials.NEO4J_USERNAME, credentials.NEO4J_PASSWORD), encrypted=False
        )

    def close(self):
        self.driver.close()

    def add_bot(self, data):
        """Method used to create a new bot

        @param data: The params of the new bot we want to create. Should include an id, name and username
        """
        if (
                "id" not in data.keys()
                or "name" not in data.keys()
                or "username" not in data.keys()
        ):
            log.error("ERROR CREATING A BOT")
            log.error(
                "Error: Specified data doesn't contain necessary fields - id, name, username"
            )

            return

        with self.driver.session() as session:
            # Caller for transactional unit of work
            return session.write_transaction(self.__create_bot, data)

    def __create_bot(self, tx, data):
        log.debug("CREATING BOT")

        # Note we use Merge rather than Create to avoid duplicates
        tx.run(
            f"MERGE (:{BOT_LABEL} {{ name: $name, id: $id, username: $username }} )",
            id=data["id"],
            name=data["name"],
            username=data["username"],
        )

    def add_user(self, data):
        """Method used to create a new user

        @param data: The params of the new bot we want to create. Should include an id, name and username
        """
        if (
                "id" not in data.keys()
                or "name" not in data.keys()
                or "username" not in data.keys()
        ):
            log.error("ERROR CREATING A USER")
            log.debug(
                "Error: Specified data doesn't contain necessary fields - id, name, username"
            )

            return

        with self.driver.session() as session:
            # Caller for transactional unit of work
            return session.write_transaction(self.__create_user, data)

    def __create_user(self, tx, data):
        log.debug("CREATING USER")

        tx.run(
            f"MERGE (:{USER_LABEL} {{ name: $name, id: $id, username: $username }})",
            id=data["id"],
            name=data["name"],
            username=data["username"],
        )

    def add_tweet(self, data):
        """
        Method used to create a tweet in the graph

        @param data: the params of the Tweet we have to create, only has to include the id
        """
        if "id" not in data.keys():
            log.error("ERROR CREATING A TWEET")
            log.debug(
                "Error: Specified data doesn't contain necessary fields - id"
            )
            return

        with self.driver.session() as session:
            # Caller for transactional unit of work
            return session.write_transaction(self.__create_tweet, data)

    def __create_tweet(self, tx, data):
        log.debug("CREATING TWEET")

        tx.run(
            f"MERGE (:{TWEET_LABEL} {{id: $id}})",
            id=data["id"],
        )

    def add_writer_relationship(self, data):
        """Method used to create a new WRITE relationship

        @param data: The params of the new relationship we want to create. Should include a tweet_id, a user_id and
        the user's type
        """

        if (
            "tweet_id" not in data.keys()
            or "user_id" not in data.keys()
            or "user_type" not in data.keys()
        ):
            log.error("ERROR CREATING A WRITE RELATIONSHIP")
            log.error(
                "Error: Specified data doesn't contain necessary fields - tweet_id, user_id, user_type"
            )

            return

        if data["user_type"] not in [BOT_LABEL, USER_LABEL]:
            log.error("ERROR CREATING A WRITE RELATIONSHIP")
            log.error(f"Error: Unacceptable specified types. Types must be {BOT_LABEL} or {USER_LABEL}")

            return

        with self.driver.session() as session:
            data['label'] = WROTE_LABEL
            data['from_type'] = data['user_type']
            data['from_id'] = data['user_id']
            data['to_type'] = TWEET_LABEL
            data['to_id'] = data['tweet_id']

            # Caller for transactional unit of work
            return session.write_transaction(self.__create_relationship, data)

    def add_retweet_relationship(self, data):
        """Method used to create a new RETWEET relationship

        @param data: The params of the new relationship we want to create. Should include a tweet_id, a user_id and
        the user's type
        """

        if (
            "tweet_id" not in data.keys()
            or "user_id" not in data.keys()
            or "user_type" not in data.keys()
        ):
            log.error("ERROR CREATING A RETWEET RELATIONSHIP")
            log.error(
                "Error: Specified data doesn't contain necessary fields - tweet_id, user_id, user_type"
            )

            return

        if data["user_type"] not in [BOT_LABEL, USER_LABEL]:
            log.error("ERROR CREATING A RETWEET RELATIONSHIP")
            log.error(f"Error: Unacceptable specified types. Types must be {BOT_LABEL} or {USER_LABEL}")

            return

        with self.driver.session() as session:
            data['label'] = RETWEET_LABEL
            data['to_type'] = TWEET_LABEL
            data['to_id'] = data['tweet_id']
            data['from_type'] = data['user_type']
            data['from_id'] = data['user_id']

            # Caller for transactional unit of work
            return session.write_transaction(self.__create_relationship, data)

    def add_quote_relationship(self, data):
        """Method used to create a new QUOTE relationship

        @param data: The params of the new relationship we want to create. Should include a tweet_id and the
        quoted_tweet
        """

        if (
            "tweet_id" not in data.keys()
            or "quoted_tweet" not in data.keys()
        ):
            log.error("ERROR CREATING A QUOTE RELATIONSHIP")
            log.error(
                "Error: Specified data doesn't contain necessary fields - tweet_id and quoted_tweet"
            )
            log.error(data)

            return

        with self.driver.session() as session:
            data['label'] = QUOTE_LABEL
            data['from_type'] = TWEET_LABEL
            data['from_id'] = data['tweet_id']
            data['to_type'] = TWEET_LABEL
            data['to_id'] = data['quoted_tweet']

            # Caller for transactional unit of work
            return session.write_transaction(self.__create_relationship, data)

    def add_reply_relationship(self, data):
        """Method used to create a new REPLY relationship

        @param data: The params of the new relationship we want to create. Should include a tweet and the reply
        """
        if (
            "tweet" not in data.keys()
            or "reply" not in data.keys()
        ):
            log.error("ERROR CREATING A REPLY RELATIONSHIP")
            log.error(
                "Error: Specified data doesn't contain necessary fields - tweet and reply"
            )

            return

        with self.driver.session() as session:
            data['label'] = REPLY_LABEL
            data['to_type'] = TWEET_LABEL
            data['to_id'] = data['tweet']
            data['from_type'] = TWEET_LABEL
            data['from_id'] = data['reply']

            # Caller for transactional unit of work
            return session.write_transaction(self.__create_relationship, data)

    def add_follow_relationship(self, data):
        """Method used to create a new FOLLOWS relationship

        @param data: The params of the new relationship we want to create. Should include a from_type, to_type, from_id, to_id
        """
        if (
                "from_id" not in data.keys()
                or "to_id" not in data.keys()
                or "from_type" not in data.keys()
                or "to_type" not in data.keys()
        ):
            log.error("ERROR CREATING A RELATIONSHIP")
            log.error(
                "Error: Specified data doesn't contain necessary fields - from_type, type_to, from_id, to_id"
            )

            return

        if data["from_type"] not in [BOT_LABEL, USER_LABEL] or data["to_type"] not in [
            BOT_LABEL,
            USER_LABEL,
        ]:
            log.error("ERROR CREATING A RELATIONSHIP")
            log.error(f"Error: Unacceptable specified types. Types must be {BOT_LABEL} or {USER_LABEL}")

            return

        with self.driver.session() as session:
            # Caller for transactional unit of work
            data['label'] = FOLLOW_LABEL
            return session.write_transaction(self.__create_relationship, data)

    def __create_relationship(self, tx, data):
        log.debug(f"CREATING RELATIONSHIP <{data['label']}>")

        result = tx.run(f"MATCH (u: {data['from_type']} {{ id: $id1 }}), (r: {data['to_type']} {{ id: $id2 }}) "
                        f"MERGE (u)-[:{data['label']}]->(r)", id1=data['from_id'], id2=data['to_id'])

        log.debug(f"Created relationship:{result}")

    def check_bot_exists(self, id):
        """Method used to check if there exists a bot with a given id

        @param id: The id of the bot we want to check the existance of
        """

        with self.driver.session() as session:
            # Caller for transactional unit of work
            return session.write_transaction(self.__bot_exists, id)

    def __bot_exists(self, tx, data):
        log.debug("CHECKING BOT EXISTANCE")

        result = tx.run(f"MATCH (r:{BOT_LABEL} {{ id:$id }}) RETURN r", id=data)

        if len(result.data()) == 0:
            return False
        else:
            return True

    def check_user_exists(self, id):
        """Method used to check if there exists a user with a given id

        @param id: The id of the user we want to check the existance of
        """

        with self.driver.session() as session:
            # Caller for transactional unit of work
            return session.write_transaction(self.__user_exists, id)

    def __user_exists(self, tx, data):
        log.debug("CHECKING USER EXISTANCE")

        result = tx.run(f"MATCH (r:{USER_LABEL} {{ id:$id }}) RETURN r", id=data)

        if len(result.data()) == 0:
            return False
        else:
            return True

    def check_tweet_exists(self, id):
        """Method used to check if there exists a tweet with a given id

        @param id: The id of the tweet we want to check the existance of
        """

        with self.driver.session() as session:
            # Caller for transactional unit of work
            return session.write_transaction(self.__tweet_exists, id)

    def __tweet_exists(self, tx, data):
        log.debug("CHECKING TWEET EXISTANCE")

        result = tx.run(f"MATCH (r:{TWEET_LABEL} {{ id:$id }}) RETURN r", id=data)

        return len(result.data()) != 0

    def update_user(self, data):
        """Method used to update a given user

        @param data: The id of the user we want to update and the other update params. Should include an old_id
        """
        if "id" not in data.keys():
            log.error("ERROR CREATING A USER")
            log.error("Error: Specified data doesn't contain necessary fields - old_id")

            return

        with self.driver.session() as session:
            # Caller for transactional unit of work
            return session.write_transaction(self.__update_user, data)

    def __update_user(self, tx, data):
        log.debug("UPDATING USER")

        set_query = ""
        if len(data.keys()) > 1:
            set_query = "SET "

        if "username" in data.keys():
            set_query += "r.username = '" + data["username"] + "',"
        if "name" in data.keys():
            set_query += "r.name = '" + data["name"] + "',"

        query = f'MATCH (r: {USER_LABEL} {{ id : {str(data["id"])} }}) {set_query[:-1]} RETURN r'

        tx.run(query)

    def update_bot(self, data):
        """Method used to update a given bot

        @param data: The params of the bot we want to update and the other update params. Should include an old_id
        """
        if "id" not in data.keys():
            log.error("ERROR UPDATING A BOT")
            log.error("Error: Specified data doesn't contain necessary fields - old_id")

            return

        with self.driver.session() as session:
            # Caller for transactional unit of work
            return session.write_transaction(self.__update_bot, data)

    def __update_bot(self, tx, data):
        log.debug("UPDATING BOT")

        set_query = ""
        if len(data.keys()) > 1:
            set_query = "SET "

        if "username" in data.keys():
            set_query += "r.username = '" + data["username"] + "',"
        if "name" in data.keys():
            set_query += "r.name = '" + data["name"] + "',"

        query = f'MATCH (r:{BOT_LABEL} {{ id: {str(data["id"])} }}) {set_query[:-1]}  RETURN r'
        # Note we use set_query[:-1] in order to remove the final comma (,)

        tx.run(query)

    def delete_user(self, id):
        """Method used to delete a given user

        @param id: The id of the user we want to delete
        """

        with self.driver.session() as session:
            # Caller for transactional unit of work
            return session.write_transaction(self.__delete_node, USER_LABEL, id)

    def delete_bot(self, id):
        """Method used to delete a given bot

        @param id: The id of the bot we want to delete
        """

        with self.driver.session() as session:
            # Caller for transactional unit of work
            return session.write_transaction(self.__delete_node, BOT_LABEL, id)

    def delete_tweet(self, id):
        """Method used to delete a given tweet

        @param id: The id of the tweet we want to delete
        """

        with self.driver.session() as session:
            # Caller for transactional unit of work
            return session.write_transaction(self.__delete_node, TWEET_LABEL, id)

    def __delete_node(self, tx, type, id):
        log.debug("DELETING NODE")

        query = f'MATCH (r:{type} {{ id: {str(id)} }}) DETACH DELETE r'

        tx.run(query)

    def delete_writer_relationship(self, data):
        """Method used to delete WRITE relationship

        @param data: The params of the new relationship we want to create. Should include a tweet_id, a user_id and
        the user's type
        """

        if (
                "tweet_id" not in data.keys()
                or "user_id" not in data.keys()
                or "user_type" not in data.keys()
        ):
            log.error("ERROR DELETING A WRITE RELATIONSHIP")
            log.error(
                "Error: Specified data doesn't contain necessary fields - tweet_id, user_id, user_type"
            )

            return

        if data["user_type"] not in [BOT_LABEL, USER_LABEL]:
            log.error("ERROR DELETING A WRITE RELATIONSHIP")
            log.error(f"Error: Unacceptable specified types. Types must be {BOT_LABEL} or {USER_LABEL}")

            return

        with self.driver.session() as session:
            data['label'] = WROTE_LABEL
            data['to_type'] = TWEET_LABEL
            data['to_id'] = data['tweet_id']
            data['from_type'] = data['user_type']
            data['from_id'] = data['user_id']

            # Caller for transactional unit of work
            return session.write_transaction(self.__delete_rel, data)

    def delete_retweet_relationship(self, data):
        """Method used to delete RETWEET relationship

        @param data: The params of the new relationship we want to create. Should include a tweet_id, a user_id and
        the user's type
        """

        if (
                "tweet_id" not in data.keys()
                or "user_id" not in data.keys()
                or "user_type" not in data.keys()
        ):
            log.error("ERROR DELETING A RETWEET RELATIONSHIP")
            log.error(
                "Error: Specified data doesn't contain necessary fields - tweet_id, user_id, user_type"
            )

            return

        if data["user_type"] not in [BOT_LABEL, USER_LABEL]:
            log.error("ERROR DELETING A RETWEET RELATIONSHIP")
            log.error(f"Error: Unacceptable specified types. Types must be {BOT_LABEL} or {USER_LABEL}")

            return

        with self.driver.session() as session:
            data['label'] = RETWEET_LABEL
            data['to_type'] = TWEET_LABEL
            data['to_id'] = data['tweet_id']
            data['from_type'] = data['user_type']
            data['from_id'] = data['user_id']

            # Caller for transactional unit of work
            return session.write_transaction(self.__delete_rel, data)

    def delete_quote_relationship(self, data):
        """Method used to delete a new QUOTE relationship

        @param data: The params of the new relationship we want to create. Should include a tweet_id and the
        quoted_tweet
        """

        if (
                "tweet_id" not in data.keys()
                or "quoted_tweet" not in data.keys()
        ):
            log.error("ERROR DELETING A QUOTE RELATIONSHIP")
            log.error(
                "Error: Specified data doesn't contain necessary fields - tweet_id and quoted_tweet"
            )

            return

        with self.driver.session() as session:
            data['label'] = QUOTE_LABEL
            data['from_type'] = TWEET_LABEL
            data['from_id'] = data['tweet_id']
            data['to_type'] = TWEET_LABEL
            data['to_id'] = data['quoted_tweet']

            # Caller for transactional unit of work
            return session.write_transaction(self.__delete_rel, data)

    def delete_reply_relationship(self, data):
        """Method used to DELETE a new REPLY relationship

        @param data: The params of the new relationship we want to create. Should include a tweet and the reply
        """
        if (
                "tweet" not in data.keys()
                or "reply" not in data.keys()
        ):
            log.error("ERROR DELETE A REPLY RELATIONSHIP")
            log.error(
                "Error: Specified data doesn't contain necessary fields - tweet and reply"
            )

            return

        with self.driver.session() as session:
            data['label'] = REPLY_LABEL
            data['to_type'] = TWEET_LABEL
            data['to_id'] = data['tweet']
            data['from_type'] = TWEET_LABEL
            data['from_id'] = data['reply']

            # Caller for transactional unit of work
            return session.write_transaction(self.__delete_rel, data)

    def delete_follow_relationship(self, data):
        """Method used to delete a given bot

        @param data: The params of the new relationship we want to delete. Should include a from_type, to_type, from_id, to_id
        """
        if (
                "from_id" not in data.keys()
                or "to_id" not in data.keys()
                or "from_type" not in data.keys()
                or "to_type" not in data.keys()
        ):
            log.error("ERROR DELETING A RELATIONSHIP")
            log.error(
                "Error: Specified data doesn't contain necessary fields - from_type, to_type, from_id, to_id"
            )

            return

        if data["from_type"] not in [BOT_LABEL, USER_LABEL] or data["to_type"] not in [
            BOT_LABEL,
            USER_LABEL,
        ]:
            log.error("ERROR DELETING A RELATIONSHIP")
            log.error(f"Error: Unaceptable specified types. Types must be {BOT_LABEL} or {USER_LABEL}")

            return

        with self.driver.session() as session:
            # Caller for transactional unit of work
            data["label"] = FOLLOW_LABEL
            return session.write_transaction(self.__delete_rel, data)

    def __delete_rel(self, tx, data):
        log.debug("DELETING RELATIONSHIP")

        query = f'MATCH (a:{str(data["from_type"])} {{ id: {str(data["from_id"])} }})-' \
                f'[r:{data["label"]}]->' \
                f'(b:{str(data["to_type"])} {{ id: {str(data["to_id"])} }}) ' \
                f' DELETE r'

        tx.run(query)

    def search_tweets(self, tweet=None):
        """Method used to search for a given tweet

        @param tweet: The params of the bot we want to look for. By default we look for all bots
        """

        with self.driver.session as session:
            return session.write_transaction(self.__search_tweet, tweet)

    def __search_tweet(self, tx, tweet):
        log.debug("SEARCHING TWEET")

        query = f"MATCH (r: {TWEET_LABEL}"
        if tweet is not None:
            query += "{id: " + tweet + "}"

        query += ") RETURN r"

        result = []
        for i in tx.run(query):
            result.append(dict(i.items()[0][1]))

        return result

    def search_bots(self, data={}):
        """Method used to search for a given bot

        @param data: The params of the bot we want to look for. By default we look for all bots
        """

        with self.driver.session() as session:
            # Caller for transactional unit of work
            return session.write_transaction(self.__search_bots, data)

    def __search_bots(self, tx, data):
        log.debug("SEARCHING BOTS")

        query_filters = "{"
        if "id" in data.keys():
            query_filters += "id: " + str(data["id"]) + ","
        if "name" in data.keys():
            query_filters += "name: '" + data["name"] + "',"
        if "username" in data.keys():
            query_filters += "username: '" + data["username"] + "',"

        query_filters = (query_filters[:-1] if len(query_filters) > 1 else query_filters) + "}"

        query = f'MATCH (r:{BOT_LABEL} {query_filters}) RETURN r'

        result = []
        for i in tx.run(query):
            result.append(dict(i.items()[0][1]))

        return result

    def search_users(self, data={}):
        """Method used to search for a given user

        @param data: The params of the user we want to look for. By default we look for all users
        """

        with self.driver.session() as session:
            # Caller for transactional unit of work
            return session.write_transaction(self.__search_users, data)

    def __search_users(self, tx, data):
        log.debug("SEARCHING USERS")

        query_filters = "{"
        if "id" in data.keys():
            query_filters += "id: " + str(data["id"]) + ","
        if "name" in data.keys():
            query_filters += "name: '" + data["name"] + "',"
        if "username" in data.keys():
            query_filters += "username: '" + data["username"] + "',"
        query_filters = (query_filters[:-1] if len(query_filters) > 1 else query_filters) + "}"

        query = f'MATCH (r:{USER_LABEL} {query_filters}) RETURN r'

        result = []
        for i in tx.run(query):
            result.append(dict(i.items()[0][1]))

        return result

    def check_writer_relationship(self, data):
        """Method used to delete WRITE relationship

        @param data: The params of the new relationship we want to create. Should include a tweet_id, a user_id and
        the user's type
        """

        if (
                "tweet_id" not in data.keys()
                or "user_id" not in data.keys()
                or "user_type" not in data.keys()
        ):
            log.error("ERROR CHECKING A WRITE RELATIONSHIP")
            log.error(
                "Error: Specified data doesn't contain necessary fields - tweet_id, user_id, user_type"
            )

            return

        if data["user_type"] not in [BOT_LABEL, USER_LABEL]:
            log.error("ERROR CHECKING A WRITE RELATIONSHIP")
            log.error(f"Error: Unacceptable specified types. Types must be {BOT_LABEL} or {USER_LABEL}")

            return

        with self.driver.session() as session:
            data['label'] = WROTE_LABEL
            data['to_type'] = TWEET_LABEL
            data['to_id'] = data['tweet_id']
            data['from_type'] = data['user_type']
            data['from_id'] = data['user_id']

            # Caller for transactional unit of work
            return session.write_transaction(self.__check_relationship, data)

    def check_retweet_relationship(self, data):
        """Method used to delete RETWEET relationship

        @param data: The params of the new relationship we want to create. Should include a tweet_id, a user_id and
        the user's type
        """

        if (
                "tweet_id" not in data.keys()
                or "user_id" not in data.keys()
                or "user_type" not in data.keys()
        ):
            log.error("ERROR CHECKING A RETWEET RELATIONSHIP")
            log.error(
                "Error: Specified data doesn't contain necessary fields - tweet_id, user_id, user_type"
            )

            return

        if data["user_type"] not in [BOT_LABEL, USER_LABEL]:
            log.error("ERROR CHECKING A RETWEET RELATIONSHIP")
            log.error(f"Error: Unacceptable specified types. Types must be {BOT_LABEL} or {USER_LABEL}")

            return

        with self.driver.session() as session:
            data['label'] = RETWEET_LABEL
            data['to_type'] = TWEET_LABEL
            data['to_id'] = data['tweet_id']
            data['from_type'] = data['user_type']
            data['from_id'] = data['user_id']

            # Caller for transactional unit of work
            return session.write_transaction(self.__check_relationship, data)

    def check_quote_relationship(self, data):
        """Method used to check a new QUOTE relationship

        @param data: The params of the new relationship we want to check. Should include a tweet_id and the
        quoted_tweet
        """

        if (
                "tweet_id" not in data.keys()
                or "quoted_tweet" not in data.keys()
        ):
            log.error("ERROR CHECKING A QUOTE RELATIONSHIP")
            log.error(
                "Error: Specified data doesn't contain necessary fields - tweet_id and quoted_tweet"
            )
            log.error(data)

            return

        with self.driver.session() as session:
            data['label'] = QUOTE_LABEL
            data['from_type'] = TWEET_LABEL
            data['from_id'] = data['tweet_id']
            data['to_type'] = TWEET_LABEL
            data['to_id'] = data['quoted_tweet']

            # Caller for transactional unit of work
            return session.write_transaction(self.__check_relationship, data)

    def check_reply_relationship(self, data):
        """Method used to check a new REPLY relationship

        @param data: The params of the new relationship we want to create. Should include a tweet and the reply
        """
        if (
                "tweet" not in data.keys()
                or "reply" not in data.keys()
        ):
            log.error("ERROR CHECK A REPLY RELATIONSHIP")
            log.error(
                "Error: Specified data doesn't contain necessary fields - tweet and reply"
            )

            return

        with self.driver.session() as session:
            data['label'] = REPLY_LABEL
            data['to_type'] = TWEET_LABEL
            data['to_id'] = data['tweet']
            data['from_type'] = TWEET_LABEL
            data['from_id'] = data['reply']

            # Caller for transactional unit of work
            return session.write_transaction(self.__check_relationship, data)

    def check_follow_exists(self, data):
        """Method used to check whether a relationship exists between two IDs

        @param data: The params of the entities involved in the relationshi+ we want to look for. Should include
            a from_type, to_type, from_id, to_id
        """
        if (
                "from_id" not in data.keys()
                or "to_id" not in data.keys()
                or "from_type" not in data.keys()
                or "to_type" not in data.keys()
        ):
            log.error("ERROR CHECKING RELATIONSHIP")
            log.debug(
                "Error: Specified data doesn't contain necessary fields - from_type, to_type, from_id, to_id"
            )

            return

        if data["from_type"] not in [BOT_LABEL, USER_LABEL] or data["to_type"] not in [
            BOT_LABEL,
            USER_LABEL,
        ]:
            log.error("ERROR CHECKING RELATIONSHIP")
            log.error(f"Error: Unacceptable specified types. Types must be {BOT_LABEL} or {USER_LABEL}")

            return

        with self.driver.session() as session:
            # Caller for transactional unit of work
            data['label'] = FOLLOW_LABEL
            return session.write_transaction(self.__check_relationship, data)

    def __check_relationship(self, tx, data):
        log.debug("VERIFYING RELATIONSHIP EXISTANCE")

        query = f'MATCH (a: {data["from_type"]} {{id: {str(data["from_id"])} }})-[r:{data["label"]}]' \
                f'->(b:{data["to_type"]} {{id: {str(data["to_id"])} }}) RETURN a, b'

        result = tx.run(query)

        return len(result.values()) != 0

    def get_following(self, data):
        """Method used to find all accounts a given entity is following

        @param data: The specification of who we want to get the followings of. Should include a id and type
        """
        if "id" not in data.keys():
            log.error("ERROR RETRIEVING FOLLOWINGS")
            log.error(
                "Error: Specified data doesn't contain necessary fields - type, id"
            )

            return

        if 'type' in data and data["type"] not in [BOT_LABEL, USER_LABEL]:
            log.error("ERROR RETRIEVING FOLLOWINGS")
            log.error(f"Error: Unaceptable specified types. Types must be {BOT_LABEL} or {USER_LABEL}")

            return

        with self.driver.session() as session:
            # Caller for transactional unit of work
            return session.write_transaction(self.__get_following, data)

    def __get_following(self, tx, data):
        log.debug("GETTING FOLLOWINGS")

        query = f"MATCH (a {':' + data['type'] if 'type' in data else ''} {{id: {str(data['id'])} }})-" \
                f"[r:{FOLLOW_LABEL}]->(b) RETURN b"

        result = []
        for i in tx.run(query):
            result.append(dict(i.items()[0][1]))

        return result

    def get_followers(self, data):
        """Method used to find all accounts following a given entity

        @param data: The specification of who we want to get the followings of. Should include a id and type
        """
        if "id" not in data.keys():
            log.error("ERROR RETRIEVING FOLLOWERS")
            log.debug(
                "Error: Specified data doesn't contain necessary fields - type, id"
            )

            return

        if 'type' in data and data["type"] not in [BOT_LABEL, USER_LABEL]:
            log.error("ERROR RETRIEVING FOLLOWINGS")
            log.error(f"Error: Unaceptable specified types. Types must be {BOT_LABEL} or {USER_LABEL}")

            return

        with self.driver.session() as session:
            # Caller for transactional unit of work
            return session.write_transaction(self.__get_followers, data)

    def __get_followers(self, tx, data):
        log.debug("GETTING FOLLOWERS")

        query = f'MATCH (b)-[r:{FOLLOW_LABEL}]->' \
                f'(a {":" + data["type"] if "type" in data else ""} {{id: {str(data["id"])} }}) RETURN b'

        result = []
        for i in tx.run(query):
            result.append(dict(i.items()[0][1]))

        return result

    def export_query(self, query, export_type="json"):

        if export_type not in ["json", "csv", "graphml"]:
            log.error("ERROR EXPORTING RESULT")
            log.error(
                "Error: ",
                "Specified export type not supported. Please use json, csv or graphml",
            )

            return

        with self.driver.session() as session:
            result = session.write_transaction(self.__export_query, export_type, query)

            output = result.data()[0]["data"]

            if export_type == "json":
                output = "[" + output.replace("\n", ",") + "]"
            
            return json.loads(output)

    def __export_query(self, tx, export_type, query):
        log.debug("EXPORTING QUERY NETWORK")

        return tx.run(f"CALL apoc.export.{export_type}.query(\"{query}\",null,{{useTypes:true, stream:true}})")

    def export_network(self, export_type="graphml"):
        """Method used to export the entire database

        @param export_type: What type we want to export to. Graphml by default
        """

        if export_type not in ["json", "csv", "graphml"]:
            log.error("ERROR EXPORTING RESULT")
            log.error(
                "Error: ",
                "Specified export type not supported. Please use json, csv or graphml",
            )

            return

        with self.driver.session() as session:
            result = session.write_transaction(self.__export_network, export_type)

            result = result.data()[0]["data"]

            if export_type == "json":
                result = "[" + result.replace("\n", ",") + "]"

            return result

    def __export_network(self, tx, export_type):
        log.debug("EXPORTING NETWORK")

        if export_type == "json":
            result = tx.run(
                "CALL apoc.export.json.all(null,{useTypes:true, stream:true})"
            )
        elif export_type == "csv":
            result = tx.run(
                "CALL apoc.export.csv.all(null,{useTypes:true, stream:true})"
            )
        else:
            result = tx.run("CALL apoc.export.graphml.all(null,{useTypes:true, stream:true})")

        return result


if __name__ == "__main__":
    neo = Neo4jAPI()

    # neo.add_bot({"id":0,"name":"Jonas","username":"Jonas_Pistolas"})
    # neo.add_user({"id":0,"name":"DS","username":"FenixD.S"})
    # neo.add_follow_relationship({"from_id": 0, "to_id": 0, "from_type": BOT_LABEL, "to_type": USER_LABEL})

    # print(neo.check_bot_exists(0))
    # print(neo.check_user_exists(0))

    # neo.update_user({"id": 0, "name": "Diogo Ass"})
    # neo.update_user({"id": 0, "username": "FenixDickSucker","name":"DS"})

    # neo.update_bot({"id":0,"name":"bot lindo"})

    # print(neo.search_bots({"name":"bot lindo"}))
    # print(neo.search_users({"id":0}))
    # print(neo.check_relationship_exists({"id_1": 0, "to_id": 0, "type_1": BOT_LABEL, "to_type": USER_LABEL}))

    # print(neo.get_following({"type": BOT_LABEL, "id": 0}))
    # print(neo.get_followers({"type": USER_LABEL, "id": 0}))

    # print(neo.get_following({"type": "BOT", "id": 0}))
    # print(neo.get_followers({"type": "USER", "id": 0}))

    # neo.export_network()
    # print(neo.export_network("csv"))
    # print()
    # print(neo.export_network("json"))
    # print()
    # print(neo.export_network())

    # neo.export_network()
    # neo.export_network("csv")
    # neo.export_network("json")

    # neo.delete_user(0)
    # neo.delete_follow_relationship({"id_1": 0, "to_id": 0, "type_1": BOT_LABEL, "to_type": USER_LABEL})
    neo.close()
