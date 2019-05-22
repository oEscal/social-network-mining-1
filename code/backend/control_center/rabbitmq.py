import pika
import json
from task import Task
import logging

log = logging.getLogger('Rabbit')
log.setLevel(logging.INFO)

class Rabbitmq():
    def __init__(self, host, port, vhost, username, password):
        self.host = host
        self.port = port
        self.vhost = vhost
        self.username = username
        self.password = password

        credentials = pika.PlainCredentials(self.username, self.password)

        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host, port=self.port, virtual_host=self.vhost , credentials=credentials))
        
        self.channel = self.connection.channel()

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

        log.debug("Connection to Rabbit Established")

    def receive(self, q):
        self.queue = q
        self.channel.queue_declare(queue=self.queue)
        
        log.info(' [*] Waiting for MESSAGES. To exit press CTRL+C')

        def callback(ch, method, properties, body):
            log.debug("MESSAGE RECEIVED")            
            message = json.loads(body)
            self.task_manager.menu(message['type'], message)

        self.channel.basic_consume(queue=self.queue, on_message_callback=callback, auto_ack=True)
        self.channel.start_consuming()
        
    def close(self):
        self.connection.close()

if __name__ == "__main__":
    rabbit = Rabbitmq(host='mqtt-redesfis.5g.cn.atnog.av.it.pt', port=5672, vhost="PI",username='pi_rabbit_admin', password='yPvawEVxks7MLg3lfr3g')
    rabbit.receive(q='API')
    rabbit.close()
