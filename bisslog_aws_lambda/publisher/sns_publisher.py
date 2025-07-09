import os

from typing import Any, Dict, Optional
import json

import boto3
from bisslog.ports.publisher import IPublisher



class SNSPublisher(IPublisher):
    """AWS SNS implementation of the IPublisher interface."""

    def __init__(self, client=None):
        self.client = client or boto3.client("sns")
        self._arn_cache: Dict[str, str] = {}
        self._arn_given = False
        arn_found = json.loads(os.getenv('ARN_SNS_TOPIC_MAP', '{}'))

        if arn_found:
            self._arn_given = True
            self._arn_cache = arn_found

    def __call__(self, queue_name: str, body: Any, *args,
                 partition: Optional[str] = None, **kwargs):
        """Publishes a message to an SNS topic using its name."""
        if not isinstance(body, str):
            body = json.dumps(body)

        topic_arn = self._arn_cache.get(queue_name)
        if not topic_arn and not self._arn_given:
            topic_arn = self.resolve_topic_arn(queue_name)
            self._arn_cache[queue_name] = topic_arn

        self.client.publish(TopicArn=topic_arn, Message=body)

    def resolve_topic_arn(self, name: str) -> str:
        """Resolves the topic ARN from its name."""
        topics = self.client.list_topics()["Topics"]
        for topic in topics:
            if topic["TopicArn"].endswith(f":{name}"):
                return topic["TopicArn"]
        raise ValueError(f"SNS topic '{name}' not found.")
