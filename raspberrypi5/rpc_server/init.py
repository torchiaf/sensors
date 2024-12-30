import os
import pika
from dht11 import read
from config import module, connectionParams, print

os.environ['RASPBERRYPI_VERSION'] = module.getDevice("dht11").getConfig("RASPBERRYPI_VERSION")

connection = pika.BlockingConnection(connectionParams)

channel = connection.channel()

channel.queue_declare(queue=module.routingKey)

def on_request(ch, method, props, body):
    n = int(body)

    print(f" receive {n}")
    response = read()

    ch.basic_publish(
        exchange='',
        routing_key=props.reply_to,
        properties=pika.BasicProperties(correlation_id = props.correlation_id),
        body=str(response)
    )
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue=module.routingKey, on_message_callback=on_request)

print(" [x] Awaiting RPC requests")
channel.start_consuming()