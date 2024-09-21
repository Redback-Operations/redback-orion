from kafka_connector import KafkaConnector

# Initialize the Kafka connector
kafka_conn = KafkaConnector()

# Create producer and produce a message
producer = kafka_conn.create_producer()
kafka_conn.produce_message(producer, "Hello, Kafka!")

# Create consumer and consume messages
consumer = kafka_conn.create_consumer()
kafka_conn.consume_messages(consumer)