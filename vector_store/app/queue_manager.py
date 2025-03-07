import json
from typing import Dict, List, Any, Optional
import traceback
from app.messaging.redis_pubsub import RedisPublisher, RedisSubscriber

    
class QueueManager:
    def __init__(self, send_queue_url: str=None, receive_queue_url:str=None):
        self.send_queue_url = send_queue_url
        self.receive_queue_url = receive_queue_url
        if self.send_queue_url is not None:
            self.redis_publisher = RedisPublisher()
        if self.receive_queue_url is not None:
            self.redis_subscriber = RedisSubscriber()


    def send_message(self, message_body: Dict[str, Any]) -> Dict[str, Any]:
        return self.redis_publisher.publish(self.send_queue_url, message_body)


    def start_background_processing(self, message_handler):
        self.redis_subscriber.start(self.receive_queue_url, message_handler)