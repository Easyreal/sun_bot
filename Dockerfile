FROM python:3.10

RUN apt-get update && apt-get install -y python3-dev supervisor nginx \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir /app

COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt

COPY . /app/

WORKDIR /app
CMD ["python3", "main.py"]

