# commlib-web-gw

![image](https://github.com/robotics-4-all/commlib-web-gw/assets/4770702/afa13c7d-81f0-4c07-a501-32ad43e3f9c5)


Web Gateway for [Commlib](https://github.com/robotics-4-all/commlib-py).
Privides a REST API for publishing to Topics and for calling RPCs.

This package also provides a Websocket API for subscribing and publishing to Topics asynchronously.

A common use case is the interraction with Commlib-supported brokers and protocols, such as MQTT, Redis, AMQP and Kafka, from a Web App running in a browser (client).

# Start with uvicorn

First create a virtual environment and install dependencies.

```sh
python -m venv myenv
pip install -r requirements.txt
```

Start the uvicorn wsgi server with 16 workers.

```py
uvicorn web_gw.api:app --host 0.0.0.0 --port 8080 --workers 16
```

# Build the Docker image

```sh
docker build . -t cwebgw
```

# Provided API

HTTP Rest:
- `/publish`: Publish data to a Topic of the broker.
- `/rpc`: Call an RPC on the broker.

Websockets:
- `/publish`: Publish data to a Topic of the broker via a WS connection.
- `/subscribe`: Asynchronous subscription to broker Topics via a WS connection.
