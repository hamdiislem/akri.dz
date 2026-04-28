import os
import json
import time
import threading
import pika
from http.server import HTTPServer, BaseHTTPRequestHandler

RABBITMQ_URL = os.getenv('RABBITMQ_URL', '')
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', '5672'))
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'guest')
RABBITMQ_PASS = os.getenv('RABBITMQ_PASS', 'guest')
CONSUL_HOST = os.getenv('CONSUL_HOST', '')
MY_IP = os.getenv('MY_IP', '127.0.0.1')


def register_with_consul():
    """Enregistrer ce worker dans Consul (service discovery)."""
    if not CONSUL_HOST:
        return
    try:
        import consul
        c = consul.Consul(host=CONSUL_HOST)
        c.agent.service.register(
            name='notification-worker',
            service_id=f'notification-worker-{MY_IP}',
            address=MY_IP,
            port=0,
        )
        print(f'[Consul] notification-worker enregistré')
    except Exception as e:
        print(f'[Consul] Erreur: {e}')


# ============================================================
# HANDLERS — traitement des messages RabbitMQ
# ============================================================

def on_booking_confirmed(ch, method, properties, body):
    """Traitement d'une réservation confirmée."""
    try:
        data = json.loads(body)
        print('\n' + '=' * 60)
        print('[NOTIFICATION] Réservation CONFIRMÉE')
        print(f"  Réservation : #{data.get('booking_id')}")
        print(f"  Voiture     : {data.get('car')}")
        print(f"  Client ID   : {data.get('client_id')}")
        print(f"  Agence ID   : {data.get('agency_id')}")
        print(f"  Période     : {data.get('start_date')} → {data.get('end_date')}")
        print(f"  Total       : {data.get('total_price')} DZD")
        print('=' * 60)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f'[ERREUR] on_booking_confirmed: {e}')
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def on_booking_cancelled(ch, method, properties, body):
    """Traitement d'une réservation annulée."""
    try:
        data = json.loads(body)
        print('\n' + '=' * 60)
        print('[NOTIFICATION] Réservation ANNULÉE')
        print(f"  Réservation : #{data.get('booking_id')}")
        print(f"  Voiture     : {data.get('car')}")
        print(f"  Client ID   : {data.get('client_id')}")
        print('=' * 60)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f'[ERREUR] on_booking_cancelled: {e}')
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def connect_and_listen():
    """Se connecter à RabbitMQ et écouter les files d'attente."""
    if RABBITMQ_URL:
        params = pika.URLParameters(RABBITMQ_URL)
    else:
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
        params = pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            credentials=credentials,
            heartbeat=600,
            blocked_connection_timeout=300,
        )
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    # Déclarer les files d'attente (idempotent)
    channel.queue_declare(queue='booking.confirmed', durable=True)
    channel.queue_declare(queue='booking.cancelled', durable=True)

    # Abonner les handlers
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='booking.confirmed', on_message_callback=on_booking_confirmed)
    channel.basic_consume(queue='booking.cancelled', on_message_callback=on_booking_cancelled)

    print('[Worker] En attente de messages RabbitMQ...')
    channel.start_consuming()


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'OK')
    def log_message(self, format, *args):
        pass  # Suppress HTTP logs


def run_worker():
    register_with_consul()
    while True:
        try:
            connect_and_listen()
        except pika.exceptions.AMQPConnectionError:
            print('[Worker] RabbitMQ non disponible, nouvelle tentative dans 5s...')
            time.sleep(5)
        except KeyboardInterrupt:
            break


if __name__ == '__main__':
    # Run RabbitMQ worker in background thread
    t = threading.Thread(target=run_worker, daemon=True)
    t.start()

    # HTTP health check server (required for Render web service)
    port = int(os.getenv('PORT', 8000))
    print(f'[Worker] Health server on port {port}')
    HTTPServer(('0.0.0.0', port), HealthHandler).serve_forever()
