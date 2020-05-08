import os
import csv
import json
import logging
from enum import IntEnum
from time import time

from wrappers.mongo_wrapper import MongoAPI
from wrappers.neo4j_wrapper import Neo4jAPI


logger = logging.getLogger("report")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(open("report_gen.log", "w"))
handler.setFormatter(logging.Formatter(
	"[%(asctime)s]:[%(levelname)s]:%(module)s - %(message)s"))
logger.addHandler(handler)


EXPORT_DIR = "export"


class Report:
	class ExportType(IntEnum):
		"""
		Enum for the Messages sent by the bot to the server.
		"""

		CSV = 0
		JSON = 1

		def __str__(self):
			return self.name

	def __init__(self):
		self.mongo = MongoAPI()
		self.neo = Neo4jAPI()
		self.exporter = Report.__Exporter(EXPORT_DIR)

	@staticmethod
	def __node_builder(node):
		query_node = "("

		if len(node) > 0:
			if "label" in node:
				query_node += ":" + node['label']
			if 'properties' in node:
				query_node += "{"
				control = False
				for prop in node['properties']:
					if control:
						query_node += "|"
					if 'screen_name' in prop:
						query_node += f"username:'{prop['screen_name']}'"
					elif 'id' in prop:
						query_node += f"id:'{prop['id']}'"
					control = True
				query_node += "}"

		return query_node+")"

	@staticmethod
	def __relation_builder(rel):
		query_rel = "["
		if len(rel) > 0:
			if 'label' in rel:
				query_rel += ":" + '|'.join(rel['label'])
			if 'depth_start' in rel:
				query_rel += "*" + str(rel['depth_start'])
			if 'depth_end' in rel:
				query_rel += ".."+str(rel['depth_end'])
		return query_rel + "]"

	def __get_mongo_info(self, node, params):
		node_type = node["labels"][0]

		if node_type in params and len(params[node_type]) > 0:

			if node_type == "Tweet":
				mongo_info = self.mongo.search('tweets', query={"id_str": node['properties']['id']},
										 fields=params[node_type], single=True)
			# It's a user or a bot
			else:
				mongo_info = self.mongo.search('users', query={"id_str": node['properties']['id']},
											 fields=params[node_type], single=True)
			if mongo_info:
				return mongo_info
			return {param: None for param in params[node_type]}
		return None

	def __get_mongo_aggregate(self, table, query, params):
		params += ["id_str"]
		if len(query) > 0 and len(params) > 0:
			result = self.mongo.search(table, query={"$or": [{"id_str": obj_id} for obj_id in query]}, fields=params)
			return result
		return None

	@staticmethod
	def __insert_info_list(info_dict, results_list, placement_dict):
		if results_list:
			for result in results_list:
				for index, key in placement_dict[result["id_str"]]:
					info_dict[index][key] = result
		return info_dict

	def __query_builder(self, query_tweets, query_bots, query_users, node):
		node_label = node["labels"][0]
		if node_label == "Tweet":
			query_tweets.append(node["properties"]["id"])
		elif node_label == "User":
			query_users.append(node["properties"]["id"])
		elif node_label == "Bot":
			query_bots.append(node["properties"]["id"])

	def __get_results(self, result, tweets, user, bots, placement, params):
		result_tweets = self.__get_mongo_aggregate("tweets", tweets, params['Tweet'])
		result_users = self.__get_mongo_aggregate("users", user, params['User'])
		result_bots = self.__get_mongo_aggregate("users", bots, params['Bot'])

		for res in [result_tweets, result_users, result_bots]:
			print(res)
			result = self.__insert_info_list(result, res, placement)

		return result
	
	def __add_to_keep_track(self, locations_dict, node, location):
		if node not in locations_dict:
			locations_dict[node] = []
		locations_dict[node].append(location)

	def create_report(self, match: dict, params: dict, limit=None, export='csv'):
		query = f"MATCH r={self.__node_builder(match['start']['node'])}" \
				f"-{self.__relation_builder(match['start']['relation'])}" \
				f"->{self.__node_builder(match['end']['node'])} " \
				f"return r"
		logger.info(query)

		if limit:
			query += f" limit {limit}"

		result = []

		query_result = self.neo.export_query(query, rel_node_properties=True)

		self.exporter.export_json(query_result)

		start = time()

		query_for_mongo = params.copy()

		keep_track_places = {}

		for row_index in range(len(query_result)):
			# Analyse each row by looking at its rels field
			row = query_result[row_index]
			relations = row['r']['rels']
			relation = {}

			# Add the detailed start node
			node_start = relations[0]["start"]
			self.__query_builder(query_tweets_start, query_bots_start, query_user_start, node_start)
			self.__add_to_keep_track(keep_track_places, node_start["properties"]["id"], (row_index, "start"))
			relation["start"] = {param: None for param in params['start'][node_start["labels"][0]]}
			relation["start"]["id_str"] = node_start["properties"]["id"]

			for index in range(len(relations) - 1):
				rel = relations[index]
				relation['rel' + str(index+1)] = {"name": rel["label"]}
				self.__query_builder(query_tweets_interm, query_bots_interm, query_user_interm, rel["end"])
				self.__add_to_keep_track(keep_track_places, rel["end"]["properties"]["id"],
										 (row_index, "interm" + str(index + 1)))
				relation["interm" + str(index+1)] = {param: None for param in params['inter'][rel["end"]["labels"][0]]}
				relation["interm" + str(index + 1)]["id_str"] = rel["end"]["properties"]["id"]

			# Add ending node
			relation['rel' + str(len(relations))] = {"name": relations[-1]["label"]}
			node_end = relations[-1]["end"]
			self.__query_builder(query_tweets_end, query_bots_end, query_user_end, node_end)
			self.__add_to_keep_track(keep_track_places, node_end["properties"]["id"], (row_index, "end"))
			relation["end"] = {param: None for param in params['end'][node_end["labels"][0]]}
			relation["end"]["id_str"] = node_end["properties"]["id"]

			# Append to result
			result.append(relation)

		logger.debug(f"It took <{time() - start} s> to finish analysing network")

		result = self.__get_results(result, query_tweets_start, query_user_start,
									query_bots_start, keep_track_places, params['start'])

		result = self.__get_results(result, query_tweets_interm, query_user_interm,
									query_bots_interm, keep_track_places, params['inter'])

		result = self.__get_results(result, query_tweets_end, query_user_end,
									query_bots_end, keep_track_places, params['end'])

		logger.debug(f"It took <{time() - start} s>")

		if export == self.ExportType.CSV:
			self.exporter.export_csv(result)
		elif export == self.ExportType.JSON:
			self.exporter.export_json(result)

	class __Exporter:
		def __init__(self, directory):
			self.directory = directory

			if not os.path.exists(self.directory):
				os.makedirs(self.directory)

		def export_csv(self, result):
			headers = [key + "_" + prop for key in result[0] for prop in result[0][key]]
			try:
				with open(f"{self.directory}/export.csv", 'w') as file:
					writer = csv.writer(file)
					writer.writerow(headers)
					for data in result:
						writer.writerow([data[key][prop] for key in data for prop in data[key]])
			except Exception as error:
				logger.exception(f"Occurred an error <{error}>: ")

		def export_json(self, result):
			try:
				with open(f"{self.directory}/export.json", "w") as file:
					json.dump(result, file, indent=3)
			except Exception as error:
				logger.exception(f"Occurred an error <{error}>: ")


if __name__ == '__main__':
	rep = Report()
	query = {
		'start': {
			'node': {
				'properties': [
					{'screen_name': 'RaffaMasse'},
					{'screen_name': 'KingstonBrasil'},
					{'id': '1250175440020529152'}
				],
				'label': "User"
			},
			'relation': {
				'label': ['FOLLOWS']
			}
		},
		'end': {
			'node': {
				'properties': [{'screen_name': 'KimKardashian'}],
				'label': "User"
			}
		}
	}
	params = {
		'start': {
			'Tweet': ['retweet_count', 'favourite_count', 'text', "id_str"],
			'User': ['name', 'screen_name', 'followers_count', "id_str"],
			'Bot': ['name', 'screen_name', 'friends_count', "id_str"]
		},
		'inter': {
			'Tweet': ['id', "id_str"],
			'User': ['screen_name', "id_str"],
			'Bot': ['name', "id_str"]
		},
		'end': {
			'Tweet': ['favorite_count', "id_str"],
			'User': ['followers_count', "id_str"],
			'Bot': ['friends_count', "id_str"]
		}
	}

	for export_type in Report.ExportType:
		print(export_type)
		rep.create_report(query, params, export=export_type)
#
#
#
# 	test_report(query, params, limit)
# 	test_report(query, params, limit, "json")
