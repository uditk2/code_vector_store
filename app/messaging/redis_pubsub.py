import redis
import json
from typing import Callable, Any
from threading import Thread, Event
from app.logging.logging_config import get_logger
from time import sleep
import os

logger = get_logger()

class RedisPublisher:
    def __init__(self):
        """
        Initialize Redis Publisher
        
        Args:
            host (str): Redis host address
            port (int): Redis port number
            db (int): Redis database number
        """
        self.redis_client = redis.Redis(host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"))
    
    def publish(self, channel: str, message: Any) -> None:
        """
        Publish a message to a specific channel
        
        Args:
            channel (str): The channel to publish to
            message (Any): The message to publish (will be JSON serialized)
        """
        try:
            if not isinstance(message, str):
                message = json.dumps(message)
            self.redis_client.rpush(channel, message)
            logger.debug(f"Published message to channel {channel}")
        except Exception as e:
            logger.error(f"Error publishing message to channel {channel}: {str(e)}")
            raise

class RedisSubscriber:
    def __init__(self):
        """
        Initialize Redis Subscriber
        """
        self.redis_client = redis.Redis(host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"))
        self.pubsub = self.redis_client.pubsub()
        self.thread = None
        self._running = Event()

    def start(self, channel, callback) -> None:
        """Start listening for messages
                
        Args:
            channel (str): Channel to subscribe to
            callback (Callable): Function to call when message is received
        """
        if self.thread is not None and self.thread.is_alive():
            raise RuntimeError("Subscriber already started")
        self.channel = channel
        self._running.set()
        self.callback = callback
        self.thread = Thread(target=self._listen)
        self.thread.start()
        logger.info(f"Started subscriber for channel {self.channel}")

    def stop(self) -> None:
        """Stop listening for messages"""
        self._running.clear()
        if self.thread:
            self.thread.join()
            self.thread = None
        logger.info(f"Stopped subscriber for channel {self.channel}")

    def _listen(self) -> None:
        """Listen for messages (queue mode) and invoke callback"""
        while self._running.is_set():
            try:
                result = self.redis_client.blpop(self.channel, timeout=1)
                if result is None:
                    continue

                _, data = result
                if isinstance(data, bytes):
                    data = data.decode('utf-8')

                try:
                    parsed_data = json.loads(data)
                except json.JSONDecodeError:
                    parsed_data = data

                self.callback(parsed_data)
            except Exception as e:
                logger.error(f"Error listening to queue {self.channel}: {str(e)}")
                if self._running.is_set():
                    sleep(1)
