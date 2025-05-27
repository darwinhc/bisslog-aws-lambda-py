"""
Module for generating AWS Lambda handler code for SNS-based consumer triggers.

This module defines a generator class that creates handler code to process
SNS events, mapping them to use cases defined in the application and handling
routing based on the SNS topic ARN.
"""
from typing import List, Optional, Tuple

from bisslog_schema.schema import TriggerConsumer
from bisslog_schema.schema.enums.trigger_type import TriggerEnum
from bisslog_schema.schema.triggers.trigger_info import TriggerInfo

from .aws_handler_trigger_generator import AWSHandlerTriggerGenerator
from ...aws_handler_gen_response import AWSHandlerGenResponse


class ConsumerAWSSNSHandlerGenerator(AWSHandlerTriggerGenerator):
    """
    Generates handler code for AWS SNS consumer triggers.

    This class inspects a list of trigger configurations and generates the
    corresponding Python code required to process SNS events for those triggers.

    Attributes
    ----------
    _init : str
        Initial condition to check if the event source is SNS.
    _line_topic_arn : str
        Line of code to extract the SNS topic ARN from the event record.
    """

    _init = 'if event.get("Records") and event["Records"][0].get("EventSource") == "aws:sns":'
    _line_topic_arn = 'topic_arn = record.get("EventSubscriptionArn", "")'

    @staticmethod
    def _generate_conditional_by_topic(topic: str) -> str:
        """
        Generate a conditional line of code to filter by SNS topic ARN.

        Parameters
        ----------
        topic : str
            The name or identifier of the SNS topic.

        Returns
        -------
        str
            A conditional string that checks if the topic name is in the ARN.
        """
        return f'if "{topic}" in topic_arn:'

    def __call__(self, triggers: List[TriggerInfo],
                 uc_var_name: str) -> Optional[AWSHandlerGenResponse]:
        """
        Generates an AWS handler response object from given SNS consumer triggers.

        Parameters
        ----------
        triggers : List[TriggerInfo]
            A list of trigger configurations defined for the use case.
        uc_var_name : str
            The variable name used to call the use case implementation.

        Returns
        -------
        Optional[AWSHandlerGenResponse]
            A handler generation result with the build and handler code, or None if not applicable.
        """
        consumer_triggers = [
            trigger for trigger in triggers
            if trigger.type == TriggerEnum.CONSUMER and isinstance(trigger.options, TriggerConsumer)
        ]
        if not consumer_triggers:
            return None

        is_single = len(consumer_triggers) == 1
        depth = 1
        lines: List[Tuple[str, int]] = [(self._init, depth)]
        depth += 1

        pre_build_lines = [self.generate_mapper("mapper_consumer_sns", {"Message": "event"})]
        lines.append(("response = []", depth))
        lines.append(('for record in event["Records"]:', depth))
        depth += 1

        depth_before = depth
        for i, trigger in enumerate(consumer_triggers):
            depth = depth_before
            keyname = trigger.keyname
            options = trigger.options
            lines.append(("mapped_standard_event_sns = mapper_consumer_sns.map(record['Sns'])", depth))

            mapper_name = self.generate_mapper_name(trigger.type.val + "_sns", keyname, i)
            conditional = self._generate_conditional_by_topic(options.queue)

            if options.mapper:
                pre_build_lines.append(self.generate_mapper(mapper_name, options.mapper))

            if not is_single:
                lines.append((self._line_topic_arn, depth))
                lines.append((conditional, depth))
                depth += 1
            else:
                lines.append(("# " + self._line_topic_arn, depth))
                lines.append(("# " + conditional, depth))

            if options.mapper:
                lines.append((f"request_to_uc : dict = {mapper_name}.map(mapped_standard_event_sns)", depth))
            else:
                lines.append(("request_to_uc = mapped_standard_event_sns", depth))

            lines.append((f"uc_response = {uc_var_name}(**request_to_uc)", depth))
            lines.append(("response.append(uc_response)", depth))

        depth = depth_before
        lines.append(('return {"statusCode": 200, "body": response}', depth))

        return AWSHandlerGenResponse(
            self.join_with_depth(lines),
            "\n".join(pre_build_lines),
            {}
        )
