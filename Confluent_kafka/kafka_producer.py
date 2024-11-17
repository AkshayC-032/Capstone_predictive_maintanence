from confluent_kafka import Producer
import pandas as pd
import json

# Confluent Cloud configuration for producer
confluent_cloud_config_producer = {
    'bootstrap.servers': 'pkc-6ojv2.us-west4.gcp.confluent.cloud:9092',
    'sasl.mechanisms': 'PLAIN',
    'security.protocol': 'SASL_SSL',
    'sasl.username': 'PZMRHTPU6B25K5YN',  # Your Confluent Cloud API key
    'sasl.password': '7H4SijWfepAnd44C7s6j9MqM1eiPhKSMmHRW72Epc7dDEnT8Qc3IztVr/TVEMdg5',  # Your Confluent Cloud API secret
}

# Create a Kafka producer
producer = Producer(confluent_cloud_config_producer)

# Define the topic to produce to
kafka_topic = 'sensor_value'  # Replace with your topic name

# Read data from the 'data.csv' file, select columns 'unit', 'cycle', 's_2' to 's_21' and send as JSON messages
df = pd.read_csv("data.csv")
df = df[['machine_id','Timestamp','Date', 'cycle', 's_2', 's_3', 's_4', 's_6', 's_7', 's_8', 's_9', 's_11', 's_12', 's_13', 's_14', 's_15', 's_17', 's_20', 's_21']]

for _, row in df.iterrows():
    message_data = json.dumps(row.to_dict())
    producer.produce(kafka_topic, key=None, value=message_data)

# Wait for any outstanding messages to be delivered and delivery reports to be received
producer.flush()
