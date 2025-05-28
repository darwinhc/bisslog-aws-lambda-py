"""
Manager for coordinating multiple AWS Lambda trigger code generators.

This module defines a class that aggregates various specialized trigger generators
(e.g., HTTP, WebSocket, SQS, SNS) and delegates trigger processing to them in order.
"""
from typing import List, Iterable, Optional

from bisslog_schema.schema import TriggerInfo

from .trigger_generator.aws_handler_trigger_generator import AWSHandlerTriggerGenerator
from .trigger_generator.consumer_aws_event_bridge_handler_generator import \
    ConsumerAWSEventBridgeHandlerGenerator
from .trigger_generator.consumer_aws_sns_handler_generator import ConsumerAWSSNSHandlerGenerator
from .trigger_generator.consumer_aws_sqs_handler_generator import ConsumerAWSSQSHandlerGenerator
from .trigger_generator.http_aws_handler_generator import HttpAWSHandlerGenerator
from .trigger_generator.schedule_aws_handler_generator import ScheduleAWSHandlerGenerator
from .trigger_generator.websocket_aws_handler_generator import WebSocketAWSHandlerGenerator
from ..aws_handler_gen_response import AWSHandlerGenResponse
from ..aws_handler_generator import AWSHandlerGenerator


class ManagerTriggerHandlerGenerator(AWSHandlerGenerator):
    """
    Aggregates and invokes multiple AWS trigger generators in a defined order.

    This class sequentially delegates a list of triggers to various specialized
    AWSHandlerTriggerGenerator instances, merging their responses into a single result.

    Notes
    -----
    The order of execution is important and must not be changed, as each generator
    is responsible for filtering the triggers it supports.

    Parameters
    ----------
    trigger_generator : Optional[Iterable[AWSHandlerTriggerGenerator]]
        Custom list of generators to use instead of the default ones.
    """
    triggers_sorted_generators = (  # DO NOT CHANGE ORDER
        HttpAWSHandlerGenerator(),
        ConsumerAWSSQSHandlerGenerator(),
        ConsumerAWSSNSHandlerGenerator(),
        ScheduleAWSHandlerGenerator(),
        ConsumerAWSEventBridgeHandlerGenerator(),
        WebSocketAWSHandlerGenerator()
    )

    def __init__(self, trigger_generator: Optional[Iterable[AWSHandlerTriggerGenerator]] = None):
        self._trigger_generators = trigger_generator or self.triggers_sorted_generators

    def __call__(self, triggers: List[TriggerInfo], var_name: str) -> AWSHandlerGenResponse:
        """
        Processes a list of trigger metadata using available generators.

        Each registered generator is invoked with the full list of triggers and
        the variable name to bind the use case. Their responses are merged.

        Parameters
        ----------
        triggers : List[TriggerInfo]
            List of all triggers associated with a use case.
        var_name : str
            Name of the variable representing the use case instance.

        Returns
        -------
        AWSHandlerGenResponse
            A merged response from all matching generators.
        """
        res = AWSHandlerGenResponse()

        for trigger_generator in self._trigger_generators:
            res_trigger: AWSHandlerGenResponse = trigger_generator(triggers, var_name)
            res += res_trigger

        return res
