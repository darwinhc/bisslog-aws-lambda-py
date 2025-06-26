import json
import boto3
from typing import Any, Optional
from bisslog.ports.publisher import IPublisher


class SQSPublisher(IPublisher):
    """AWS SQS implementation of the IPublisher interface."""

    def __init__(self, client=None):
        self.client = client or boto3.client("sqs")
        self._url_cache = {}

    def __call__(self, queue_name: str, body: Any, *args,
                 partition: Optional[str] = None, **kwargs):
        """Publishes a message to an SQS queue using its name."""
        if not isinstance(body, str):
            body = json.dumps(body)

        queue_url = self._url_cache.get(queue_name)
        if not queue_url:
            queue_url = self.client.get_queue_url(QueueName=queue_name)["QueueUrl"]
            self._url_cache[queue_name] = queue_url

        self.client.send_message(QueueUrl=queue_url, MessageBody=body)
