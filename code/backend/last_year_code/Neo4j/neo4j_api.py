from neo4j import GraphDatabase
from enum import IntEnum
import logging
import sys
import settings


#OMFG TOU MAD Q FODE, estes fdps criaram a classe Neo4jTypes no ficheiro enums.py e depois em vez de a importarem VOLTARAM A CRIA-LA AQUI
#FODASSE
class Neo4jTypes(IntEnum):
	CREATE_BOT = 1
	CREATE_USER = 2
	CREATE_RELATION_BOT_USER = 3
	SEARCH_USER = 4
	UPDATE_USER = 5
	SEARCH_BOT = 6
	UPDATE_BOT = 7
	CREATE_RELATION_USER_USER = 8
	CREATE_RELATION_BOT_BOT = 9


log = logging.getLogger('NEO4J')
log.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("[%(asctime)s]:[%(levelname)s]:%(module)s - %(message)s"))
log.addHandler(handler)


class Neo4jAPI:
	def __init__(self):
		self._driver = GraphDatabase.driver("bolt://" + settings.NEO4J_FULL_URL,
											auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD))

	def close(self):
		self._driver.close()

	#Basically o q eles fizeram aqui foi criar uma wrapper function - task - que vai receber o tipo da query que queremos fazer
	# e os dados necessarios, e vai chamar a funçao apropriada.
	# Sooo tipo algumas task são marcadas como transactions mas outras não...agora why idfk. A minha guess é que as Tasks são as ações que os Bots podem realizar
	def task(self, query_type, data):
		with self._driver.session() as session:
			if query_type == Neo4jTypes.CREATE_BOT:
				session.write_transaction(self.create_bot, data)
			elif query_type == Neo4jTypes.CREATE_USER:
				session.write_transaction(self.create_user, data)
			elif query_type == Neo4jTypes.CREATE_RELATION_BOT_USER:
				session.write_transaction(self.create_relationship_bot_user, data)
			elif query_type == Neo4jTypes.SEARCH_USER:
				result = session.write_transaction(self.search_user, data)
				return result
			elif query_type == Neo4jTypes.UPDATE_USER:
				session.write_transaction(self.update_user, data)
			elif query_type == Neo4jTypes.SEARCH_BOT:
				result = session.write_transaction(self.search_bot, data)
				return result
			elif query_type == Neo4jTypes.UPDATE_BOT:
				session.write_transaction(self.update_bot, data)
			elif query_type == Neo4jTypes.CREATE_RELATION_USER_USER:
				session.write_transaction(self.create_relationship_user_user, data)
			elif query_type == Neo4jTypes.CREATE_RELATION_BOT_BOT:
				session.write_transaction(self.create_relationship_bot_bot, data)

	@staticmethod
	def create_bot(tx, data):
		log.info("NEO4J TASK: CREATE BOT")
		bot_name = data['name']
		bot_id = data['id']
		bot_username = data['username']
		tx.run("MERGE (:Bot { name: $name, id: $id, username: $username })", id=bot_id, name=bot_name,
			   username=bot_username)

	@staticmethod
	def create_user(tx, data):
		log.info("NEO4J TASK: CREATE USER")
		user_name = data['name']
		user_id = data['id']
		user_username = data['username']
		tx.run("MERGE (:User { name: $name, id: $id, username: $username })", id=user_id, name=user_name,
			   username=user_username)

	@staticmethod
	def create_relationship_bot_user(tx, data):
		log.info("NEO4J TASK: CREATE RELATION BOT - USER")
		bot_id = data['bot_id']
		user_id = data['user_id']
		tx.run("MATCH (u:Bot { id: $bot_id }), (r:User {id:$user_id}) \
                MERGE (u)-[:FOLLOWS]->(r)", bot_id=bot_id, user_id=user_id)

	@staticmethod
	def create_relationship_bot_bot(tx, data):
		log.info("NEO4J TASK: CREATE RELATION BOT - BOT")
		bot1 = data['bot1']
		bot2 = data['bot2']
		tx.run("MATCH (u:Bot { id: $bot1 }), (r:Bot {id:$bot2}) \
                MERGE (u)<-[:FOLLOWS]-(r)", bot1=bot1, bot2=bot2)

	@staticmethod
	def create_relationship_user_user(tx, data):
		log.info("NEO4J TASK: CREATE RELATION USER - USER")
		user1 = data['user1']
		user2 = data['user2']
		tx.run("MATCH (u:User { id: $user1 }), (r:User { id:$user2 }) \
                MERGE (u)<-[:FOLLOWS]-(r)", user1=user1, user2=user2)

	@staticmethod
	def search_user(tx, data):
		log.info("NEO4J TASK: SEARCH USER")
		user_id = data['user_id']
		result = tx.run("MATCH (r:User { id:$id }) \
                        RETURN r", id=user_id)
		if (len(result.data()) == 0):
			return False
		else:
			return True

	@staticmethod
	def search_bot(tx, data):
		log.info("NEO4J TASK: SEARCH BOT")
		bot_id = data['bot_id']
		result = tx.run("MATCH (r:Bot { id:$id }) \
                        RETURN r", id=bot_id)
		if (len(result.data()) == 0):
			return False
		else:
			return True

	@staticmethod
	def update_user(tx, data):
		log.info("NEO4J TASK: UPDATE USER")
		user_id = data['user_id']
		user_name = data['user_name']
		user_username = data['user_username']
		tx.run("MATCH (r:User { id:$id }) \
                SET r = { id: $id, name: $name, username: $username } \
                RETURN r", id=user_id, name=user_name, username=user_username)

	@staticmethod
	def update_bot(tx, data):
		log.info("NEO4J TASK: UPDATE BOT")
		bot_id = data['bot_id']
		bot_name = data['bot_name']
		bot_username = data['bot_username']
		tx.run("MATCH (r:Bot { id:$id }) \
                SET r = { id: $id, name: $name, username: $username } \
                RETURN r", id=bot_id, name=bot_name, username=bot_username)

	def search_all_bots(self):
		with self._driver.session() as session:
			result = session.run("MATCH (a:Bot) RETURN a")
			records_iterator = result.values()
			l = []
			for i in records_iterator:
				d = {}
				a = i[0]
				d["id"] = a.get("id")
				d["name"] = a.get("name")
				d["username"] = a.get("username")
				l.append(d)
			return l

	def search_bot_by_id(self, bot_id):
		with self._driver.session() as session:
			result = session.run("MATCH (a:Bot { id:$bot_id }) RETURN a;", bot_id=bot_id)
			d = {}
			for i in result.values():
				d["id"] = i[0].get("id")
				d["name"] = i[0].get("name")
				d["username"] = i[0].get("username")
				break
		return [d]

	def search_relationship(self, user_id, bot_id):
		with self._driver.session() as session:
			result = session.run("match (b:Bot { id:$bot_id } )-[r:FOLLOWS]->(u:User { id:$user_id } ) return b,u",
								 bot_id=bot_id, user_id=user_id)
			if (len(result.values()) == 0):
				return False
			else:
				return True

	def get_following(self, user_id):
		with self._driver.session() as session:
			result = session.run("match (b { id:$id } )-[FOLLOWS]->(r) return r.id", id=user_id)
			return result.values()

	def get_followers(self, user_id):
		with self._driver.session() as session:
			result = session.run("match (r)-[FOLLOWS]->(b { id:$id } ) return r.id", id=user_id)
			return result.values()

	def export_network(self, export="csv"):
		with self._driver.session() as session:
			if export == "csv":
				val = session.run(
					"call apoc.export.csv.query('match (b)-[r:FOLLOWS]->(u) return b.id,b.name,b.username,type(r),"
					"u.id,u.name,u.username;','file.csv',{})")
			else:
				val = session.run(
					"CALL apoc.export.graphml.all('complete-graph.graphml', {useTypes:true, storeNodeIds:false})")
		return val.values()