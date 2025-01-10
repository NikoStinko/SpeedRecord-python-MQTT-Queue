# main.py
import pika
import mysql.connector
from mysql.connector import Error
import random
import time
import threading

QUEUE_NAME = "speed_data"
SPEED_LIMIT = 90

# Configuration de la base de données
db_config = {
    'user': 'root',
    'password': 'root',
    'host': 'localhost',
    'database': 'speed_data_db'
}

def generate_speed():
    speed = random.randint(50, 120)  # Génère une vitesse aléatoire entre 50 et 120 km/h
    if speed > SPEED_LIMIT:
        voyant = True
    else:
        voyant = False
    print(f"[*] Voyant: {'Allumé' if voyant else 'Eteint'}")

    return speed

def send_speed():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue=QUEUE_NAME, durable=False, exclusive=False, auto_delete=False)

    while True:
        speed = generate_speed()
        message = f"Speed: {speed} km/h"
        channel.basic_publish(exchange='', routing_key=QUEUE_NAME, body=message)
        print(f" [x] Sent '{message}'")
        time.sleep(5)  # Attendre 5 secondes avant de générer une nouvelle vitesse

    connection.close()

def insert_speed_data(speed):
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            cursor = connection.cursor()
            query = "INSERT INTO speed_data (speed) VALUES (%s)"
            cursor.execute(query, (speed,))
            connection.commit()
            print(f" [*] Inserted speed: {speed} km/h into the database")
        else:
            print("[!] Error : failed to connect to the database")
    except Error as e:
        print(f" [!] Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def storage_callback(ch, method, properties, body):
    message = body.decode()
    print(f" [x] Received '{message}'")
    try:
        # Extraire les vitesses dans les messages récupérés
        speed_str = message.split(": ")[1].split(" ")[0].replace("}", "")
        speed = float(speed_str)
        insert_speed_data(speed)
    except ValueError as e:
        print(f" [!] Error processing message: {e}")
    except Exception as e:
        print(f" [!] Unexpected error: {e}")

def consume_speed_storage():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue=QUEUE_NAME, durable=False, exclusive=False, auto_delete=False)

    print(" [*] Waiting for messages. To exit press CTRL+C")

    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=storage_callback, auto_ack=True)

    channel.start_consuming()

def mysql_consumer_callback(ch, method, properties, body):
    message = body.decode()
    print(f" [x] Received '{message}'")
    try:
        speed_str = message.split(": ")[1].split(" ")[0].replace("}", "")
        speed = float(speed_str)
        insert_speed_data(speed)
    except ValueError as e:
        print(f" [!] Error processing message: {e}")
    except Exception as e:
        print(f" [!] Unexpected error: {e}")

def consume_speed_mysql_consumer():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue=QUEUE_NAME, durable=False, exclusive=False, auto_delete=False)

    print(" [*] Waiting for messages. To exit press CTRL+C")

    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=mysql_consumer_callback, auto_ack=True)

    channel.start_consuming()

def monitor_callback(ch, method, properties, body):
    message = body.decode()
    print(f" [x] Received '{message}'")
    try:
        speed_str = message.split(": ")[1].split(" ")[0].replace("}", "")
        speed = float(speed_str)
    except ValueError as e:
        print(f" [!] Error processing message: {e}")
    except Exception as e:
        print(f" [!] Unexpected error: {e}")

def monitor_speed():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue=QUEUE_NAME, durable=False, exclusive=False, auto_delete=False)

    print(" [*] Waiting for messages. To exit press CTRL+C")

    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=monitor_callback, auto_ack=True)

    channel.start_consuming()

if __name__ == "__main__":
    speed_thread = threading.Thread(target=send_speed)
    storage_thread = threading.Thread(target=consume_speed_storage)
    mysql_consumer_thread = threading.Thread(target=consume_speed_mysql_consumer)
    monitor_thread = threading.Thread(target=monitor_speed)

    speed_thread.start()
    storage_thread.start()
    mysql_consumer_thread.start()
    monitor_thread.start()

    # Keep the main thread alive to allow background threads to run
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Terminating threads...")
        speed_thread.join()
        storage_thread.join()
        mysql_consumer_thread.join()
        monitor_thread.join()
        print("All threads terminated.")
