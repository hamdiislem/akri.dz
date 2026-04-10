import os
from django.apps import AppConfig


class ApiProjectConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api_project'

    def ready(self):
        consul_host = os.getenv('CONSUL_HOST', '')
        if not consul_host:
            return
        try:
            import consul
            my_ip = os.getenv('MY_IP', '127.0.0.1')
            my_port = int(os.getenv('MY_PORT', '8000'))
            c = consul.Consul(host=consul_host, port=int(os.getenv('CONSUL_PORT', '8500')))
            c.agent.service.register(
                name='api-service',
                service_id=f'api-service-{my_ip}',
                address=my_ip,
                port=my_port,
            )
            print(f'[Consul] api-service registered at {my_ip}:{my_port}')
        except Exception as e:
            print(f'[Consul] Registration failed: {e}')
