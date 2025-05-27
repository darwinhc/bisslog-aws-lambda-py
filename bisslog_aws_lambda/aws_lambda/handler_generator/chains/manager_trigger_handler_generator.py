from typing import List

from bisslog_schema.schema import TriggerInfo

from .trigger_generator.consumer_aws_event_bridge_handler_generator import \
    ConsumerAWSEventBridgeHandlerGenerator
from .trigger_generator.consumer_aws_sns_handler_generator import ConsumerAWSSNSHandlerGenerator
from .trigger_generator.consumer_aws_sqs_handler_generator import ConsumerAWSSQSHandlerGenerator
from .trigger_generator.schedule_aws_handler_generator import ScheduleAWSHandlerGenerator
from ..aws_handler_generator import AWSHandlerGenerator
from ..aws_handler_gen_response import AWSHandlerGenResponse
from .trigger_generator.http_aws_handler_generator import HttpAWSHandlerGenerator

class ManagerTriggerHandlerGenerator(AWSHandlerGenerator):

    triggers_sorted_generators = (  # DO NOT CHANGE ORDER
        HttpAWSHandlerGenerator(),
        ConsumerAWSSQSHandlerGenerator(),
        ConsumerAWSSNSHandlerGenerator(),
        ScheduleAWSHandlerGenerator(),
        ConsumerAWSEventBridgeHandlerGenerator(),
    )

    def __call__(self, triggers: List[TriggerInfo], var_name: str) -> AWSHandlerGenResponse:

        res = AWSHandlerGenResponse()


        for trigger_generator in self.triggers_sorted_generators:
            res_trigger : AWSHandlerGenResponse = trigger_generator(triggers, var_name)
            res += res_trigger

        return res
