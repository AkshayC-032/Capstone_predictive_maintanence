from confluent_kafka import Consumer, KafkaError
import pandas as pd
import numpy as np
import pickle
import json

# Confluent Cloud configuration for consumer
confluent_cloud_config_consumer = {
    'bootstrap.servers': 'pkc-6ojv2.us-west4.gcp.confluent.cloud:9092',
    'sasl.mechanisms': 'PLAIN',
    'security.protocol': 'SASL_SSL',
    'sasl.username': 'PZMRHTPU6B25K5YN',  # Your Confluent Cloud API key
    'sasl.password': '7H4SijWfepAnd44C7s6j9MqM1eiPhKSMmHRW72Epc7dDEnT8Qc3IztVr/TVEMdg5',  # Your Confluent Cloud API secret
    'group.id': 'kafka-consumer-group',
    'auto.offset.reset': 'earliest',
}

# Create a Kafka consumer
consumer = Consumer(confluent_cloud_config_consumer)

# Load the machine learning model
try:
    with open('finalized_model.sav', 'rb') as f:
        model = pickle.load(f)
except Exception as e:
    print("Error loading the machine learning model:", str(e))

# Create a list to store results
result_list = []

# Subscribe to the Kafka topic (Sensor_data)
kafka_topic = 'sensor_value'
consumer.subscribe([kafka_topic])

# Define feature names for 'unit', 'cycle', 's_2' to 's_21'
feature_names = ['machine_id','Timestamp','Date', 'cycle', 's_2', 's_3', 's_4', 's_6', 's_7', 's_8', 's_9', 's_11', 's_12', 's_13', 's_14', 's_15', 's_17', 's_20', 's_21']

# Continuously read and process messages from the Kafka topic
while True:
    msg = consumer.poll(1.0)

    if msg is None:
        continue

    if msg.error():
        if msg.error().code() == KafkaError._PARTITION_EOF:
            print('Reached the end of the partition')
        else:
            print('Error while consuming: {}'.format(msg.error()))
    else:
        try:
            # Deserialize the message data from JSON
            message_data = json.loads(msg.value())

            # Create a DataFrame with named columns for 'unit', 'cycle', 's_2' to 's_21'
            data = pd.DataFrame([list(message_data.values())], columns=feature_names)

            # Perform prediction using the machine learning model
            res = model.predict(data[['s_2', 's_3', 's_4', 's_6', 's_7', 's_8', 's_9', 's_11', 's_12', 's_13', 's_14', 's_15', 's_17','s_20', 's_21']])

            # Append the result to the list
            result_list.append([message_data['machine_id'],message_data['Timestamp'],message_data['Date'], message_data['cycle'], res[0]])

            # Save the results to a CSV file including 'unit', 'cycle', and 'rul'
            d = pd.DataFrame(result_list, columns=['machine_id','Timestamp','Date', 'cycle', 'rul'])
            d.to_csv('output-file1.csv', index=False)

        except Exception as e:
            print("Error processing message:", str(e))
