FROM python:3.10-slim
WORKDIR /app
RUN pip install --no-cache-dir flask
COPY . /app
EXPOSE 5000
CMD ["python3", "app.py"]
