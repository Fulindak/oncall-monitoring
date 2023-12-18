# Используем базовый образ с Python
FROM python:3.8

COPY custom_exporter/requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY custom_exporter/src /app

WORKDIR /app

CMD ["python", "custom_exporter.py"]
