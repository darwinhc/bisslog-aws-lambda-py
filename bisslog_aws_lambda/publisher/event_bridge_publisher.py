import json
import boto3
from typing import Any, Optional
from bisslog.ports.publisher import IPublisher


class EventBridgePublisher(IPublisher):
    """EventBridge Publisher implementation for IPublisher interface."""

    def __init__(self, client=None):
        self.client = client or boto3.client("events")

    def __call__(self, queue_name: str, body: Any, *args, partition: Optional[str] = None, **kwargs):
        """Send an event to EventBridge.

        queue_name refers to the EventBusName.
        """
        if not isinstance(body, str):
            body = json.dumps(body)

        detail_type = kwargs.get("detail_type", "bisslog.message")
        source = kwargs.get("source", "bisslog")

        self.client.put_events(
            Entries=[
                {
                    "EventBusName": queue_name,
                    "Source": source,
                    "DetailType": detail_type,
                    "Detail": body,
                }
            ]
        )
