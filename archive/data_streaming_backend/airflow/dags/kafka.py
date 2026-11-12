from airflow import DAG
from airflow.operators.python import PythonVirtualenvOperator
from datetime import datetime
import logging


# Define the function for Kafka producer and consumer inside virtual environment
def test_kafka_in_venv():
    from kafka import KafkaProducer, KafkaConsumer
    import logging
    # Kafka server and topic settings
    KAFKA_SERVER = 'redback.it.deakin.edu.au:9092'
    TOPIC = 'kafka_test'

    # Kafka producer code
    def test_kafka_producer():
        producer = KafkaProducer(bootstrap_servers=[KAFKA_SERVER])
        try:
            # Send a test message to the topic
            producer.send(TOPIC, b'Kafka test message')
            producer.flush()  # Ensure the message is sent
            logging.info(f"Message sent to {TOPIC} on {KAFKA_SERVER}")
        except Exception as e:
            logging.error(f"Error sending message to Kafka: {e}")
        finally:
            producer.close()

    # Kafka consumer code
    def test_kafka_consumer():
        consumer = KafkaConsumer(
            TOPIC,
            bootstrap_servers=[KAFKA_SERVER],
            auto_offset_reset='earliest',
            group_id=None
        )
        try:
            # Read a single message from the topic
            for message in consumer:
                logging.info(f"Received message: {message.value.decode('utf-8')}")
                break  # Consume only one message for the test
        except Exception as e:
            logging.error(f"Error consuming message from Kafka: {e}")
        finally:
            consumer.close()

    # Run producer and consumer
    test_kafka_producer()
    test_kafka_consumer()

# Define the DAG
with DAG(
    dag_id="test_kafka_in_virtualenv_dag",
    schedule_interval=None,  # Manual trigger
    start_date=datetime(2025, 4, 28),
    catchup=False,
    tags=["kafka", "example"],
) as dag:

    # Task to create a virtual environment and execute the Kafka test function
    create_venv_task = PythonVirtualenvOperator(
        task_id="create_venv_and_test_kafka",
        python_callable=test_kafka_in_venv,
        requirements="kafka_requirements.txt",  # Path to your requirements.txt
        system_site_packages=False,  # Isolate the virtual environment
    )

    create_venv_task
