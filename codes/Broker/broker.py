import logging
import asyncio
import os
from amqtt.broker import Broker
import yaml

document = """
listeners:
    default:
        max-connections: 50000
        type: tcp
    CPABE-1:
        bind: 0.0.0.0:1883
timeout-disconnect-delay: 2
auth:
    plugins: ['auth.anonymous'] #List of plugins to activate for authentication among all registered plugins
    allow-anonymous: true
topic-check:
    enabled: false
    plugins: ['topic_acl']
    acl:
        anonymous: ['message/public']  # List of topics on which an anonymous client can publish and subscribe
"""
config= yaml.load(document)

@asyncio.coroutine
def broker_coro():
    broker = Broker(config=config)
    yield from broker.start()

if __name__ == '__main__':
    formatter = "[%(asctime)s] :: %(levelname)s :: %(name)s :: %(message)s"
    logging.basicConfig(level=logging.INFO, format=formatter)
    asyncio.get_event_loop().run_until_complete(broker_coro())
    asyncio.get_event_loop().run_forever()