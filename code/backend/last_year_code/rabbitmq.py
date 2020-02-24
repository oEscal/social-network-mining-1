import pika
import json
from task import Task
import logging
import sys
import time
import settings

log = logging.getLogger('Rabbit')
log.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("[%(asctime)s]:[%(levelname)s]:%(module)s - %(message)s"))
log.addHandler(handler)

WAIT_TIME = 10
class Rabbitmq():
    """Class representing Rabbit MQ"""

    def __init__(self, host, port, vhost, username, password):
        """
        Create a Rabbit MQ instance which represents a connection to a Rabbit MQ server

        Parameters
        ----------
        host : str
            Hostname
        port : int
            Port Number
        vhost : str
            Virtual host used to avoid conflicts between instances
        username : str
            Username for authentication
        password : str
            Password for authentication
        """

        self.host = host
        self.port = port
        self.vhost = vhost
        self.username = username
        self.password = password
        self.reconnection_attempt = 0
        self.MAX_RECONNECTIONS = 10
    def _setup(self):
        
        credentials = pika.PlainCredentials(self.username, self.password)

        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host, port=self.port, virtual_host=self.vhost , credentials=credentials,heartbeat=600, blocked_connection_timeout=300))
        
        self.channel = self.connection.channel()

        self.channel.queue_declare(queue='API',durable=True)

        #Declare Exchanges
        self.channel.exchange_declare(exchange='task_deliver', exchange_type='direct', durable=True)

        self.channel.exchange_declare(exchange='twitter_data', exchange_type='direct', durable=True)

        self.channel.exchange_declare(exchange='logs', exchange_type='direct', durable=True)

        self.channel.exchange_declare(exchange='queries', exchange_type='direct', durable=True)

        #Create Bindings
        self.channel.queue_bind(exchange="data",
                   queue="API",
                   routing_key='data.twitter')

        self.channel.queue_bind(exchange="twitter_data",
                   queue="API",
                   routing_key='data.twitter')

        self.channel.queue_bind(exchange="logs",
            queue="API",
            routing_key='logs.twitter')

        self.channel.queue_bind(exchange="queries",
            queue="API",
            routing_key='queries.twitter')

        #Iniciate Task Manager
        self.task_manager = Task()

        log.info("Connection to Rabbit Established")

    def receive(self, queue):
        """
        Receive messages into the queue.

        params:
        -------
        q : (string) queue name
        """
        try:
            self.queue = queue
            self.channel.queue_declare(queue=self.queue,durable=True)
            
            log.info(' [*] Waiting for MESSAGES. To exit press CTRL+C')

            def callback(ch, method, properties, body):
                log.info("MESSAGE RECEIVED")            
                message = json.loads(body)
                self.task_manager.menu(message['type'], message)

            self.channel.basic_consume(queue=self.queue, on_message_callback=callback, auto_ack=True)
            self.channel.start_consuming()
        except Exception as e:
            log.warning("Exception detected: {0}".format(e))
            log.warning("Attempting reconnection after waiting time...")
            time.sleep(WAIT_TIME)
            self._setup()
            log.debug("Setup completed")
            self.receive(queue)
        
    def close(self):
        """
        Close the connection with the Rabbit MQ server
        """
        self.connection.close()

if __name__ == "__main__":
    rabbit = Rabbitmq(host=settings.RABBITMQ_URL, port=settings.RABBITMQ_PORT, vhost=settings.RABBITMQ_VHOST, username=settings.RABBITMQ_USERNAME, password=settings.RABBITMQ_PASSWORD)
    rabbit._setup()
    rabbit.receive(queue='API')
    rabbit.close()