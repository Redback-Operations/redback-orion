import os
from confluent_kafka import Producer, Consumer, KafkaException
from dotenv import load_dotenv

# Load configuration from .env file
load_dotenv()

class KafkaConnector:
    def __init__(self):
        # Load Kafka configuration from environment variables
        self.broker = os.getenv('KAFKA_BROKER')
        self.topic = os.getenv('KAFKA_TOPIC')
        self.group_id = os.getenv('KAFKA_GROUP_ID')

    def create_producer(self):
        # Producer configuration
        conf = {'bootstrap.servers': self.broker}
        producer = Producer(conf)
        return producer

    def create_consumer(self):
        # Consumer configuration
        conf = {
            'bootstrap.servers': self.broker,
            'group.id': self.group_id,
            'auto.offset.reset': 'earliest'
        }
        consumer = Consumer(conf)
        return consumer

    def produce_message(self, producer, message):
        # Delivery report callback
        def delivery_report(err, msg):
            if err is not None:
                print(f"Message delivery failed: {err}")
            else:
                print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

        # Produce message
        producer.produce(self.topic, message.encode('utf-8'), callback=delivery_report)
        producer.flush()

    def consume_messages(self, consumer):
        # Subscribe to the topic
        consumer.subscribe([self.topic])
        try:
            while True:
                # Poll for messages
                msg = consumer.poll(1.0)

                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaException._PARTITION_EOF:
                        print(f"Reached end of partition: {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")
                    else:
                        print(f"Error: {msg.error()}")
                    continue

                # Print received message
                print(f"Received message: {msg.value().decode('utf-8')}")

        except KeyboardInterrupt:
            print("Consumer stopped by user")

        finally:
            consumer.close()
