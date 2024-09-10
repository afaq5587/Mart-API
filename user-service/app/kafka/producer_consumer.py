from app.config.setting import (
    BOOTSTRAP_SERVER1,
    BOOTSTRAP_SERVER2,
    BOOTSTRAP_SERVER3,
)
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from app.protobuf import user_pb2

bootstrap_servers = ["broker1:19092", "broker2:19092", "broker3:19092"]

# ? Kafka Producer as a dependency:
async def kafka_producer():
    producer = AIOKafkaProducer(bootstrap_servers=bootstrap_servers)
    await producer.start()
    try:
        yield producer
    finally:
        await producer.stop()


# ? Kafka consumer:
async def kafka_consumer(topic, bootstrap_servers, group_id):
    # Create a consumer instance.
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id=group_id,
        auto_offset_reset="earliest",
    )

    # Start the consumer.
    await consumer.start()
    try:
        # Continuously listen for messages.
        async for message in consumer:
            print(f"\n\n Consumer Raw message Vaue: {message.value}")

            user = user_pb2.Users()
            user.ParseFromString(message.value)
            print(f"\n\n Consumer Deserialized data: {user}")
            # Here you can add code to process each message.
            # Example: parse the message, store it in a database, etc.
    finally:
        # Ensure to close the consumer when done.
        await consumer.stop()
