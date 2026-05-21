FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["gunicorn", "django_admin.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
