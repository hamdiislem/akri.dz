import os
from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        # Register this service with Consul on startup
        consul_host = os.getenv('CONSUL_HOST', '')
        if not consul_host:
            return
        try:
            import consul
            my_ip = os.getenv('MY_IP', '127.0.0.1')
            my_port = int(os.getenv('MY_PORT', '8000'))
            c = consul.Consul(host=consul_host, port=int(os.getenv('CONSUL_PORT', '8500')))
            c.agent.service.register(
                name='auth-service',
                service_id=f'auth-service-{my_ip}',
                address=my_ip,
                port=my_port,
                check=consul.Check.http(
                    f'http://{my_ip}:{my_port}/api/auth/verify/',
                    interval='10s',
                    timeout='5s',
                ),
            )
            print(f'[Consul] auth-service registered at {my_ip}:{my_port}')
        except Exception as e:
            print(f'[Consul] Registration failed: {e}')
