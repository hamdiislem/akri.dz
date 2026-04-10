FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate && python manage.py shell -c \"from accounts.models import Admin; Admin.objects.filter(email='$ADMIN_EMAIL').exists() or Admin.objects.create(email='$ADMIN_EMAIL', password='$ADMIN_PASSWORD')\" && python manage.py runserver 0.0.0.0:8000"]
