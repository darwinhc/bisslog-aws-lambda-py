"""
Module for generating AWS Lambda handler code for EventBridge-based schedule triggers.

This module defines a generator class that creates handler code to process
EventBridge events, mapping them to use cases defined in the application.
"""
from typing import List, Optional, Tuple

from bisslog_schema.schema import TriggerSchedule
from bisslog_schema.schema.enums.trigger_type import TriggerEnum
from bisslog_schema.schema.triggers.trigger_info import TriggerInfo

from .aws_handler_trigger_generator import AWSHandlerTriggerGenerator
from ...aws_handler_gen_response import AWSHandlerGenResponse


class ScheduleAWSHandlerGenerator(AWSHandlerTriggerGenerator):
    """
    Generates handler code for AWS EventBridge schedule triggers.

    This class inspects a list of trigger configurations and generates the
    corresponding Python code required to process EventBridge events.

    Attributes
    ----------
    _init : str
        Initial condition to check if the event is from EventBridge.
    """

    _init = 'if event.get("source") == "aws.events" and event.get("detail-type") == "Scheduled Event":'

    @staticmethod
    def _generate_conditional_by_source(source: str) -> str:
        """
        Generate a conditional line of code to filter by EventBridge source.

        Parameters
        ----------
        source : str
            The expected source field from the EventBridge event.

        Returns
        -------
        str
            A conditional string that checks if the source matches.
        """
        return f'if event.get("source") == "{source}":'

    def __call__(self, triggers: List[TriggerInfo],
                 uc_var_name: str) -> Optional[AWSHandlerGenResponse]:
        """
        Generates an AWS handler response object from given EventBridge schedule triggers.

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
        schedule_triggers = [
            trigger for trigger in triggers
            if trigger.type == TriggerEnum.SCHEDULE and isinstance(trigger.options, TriggerSchedule)
        ]
        if not schedule_triggers:
            return None

        depth = 1
        lines: List[Tuple[str, int]] = [(self._init, depth)]
        depth += 1

        pre_build_lines = [self.generate_mapper("mapper_schedule_event_bridge", {"detail": "event"})]
        lines.append(("response = []", depth))

        depth_before = depth
        for _ in schedule_triggers:
            depth = depth_before
            lines.append(("request_to_uc = mapper_schedule_event_bridge.map(event)", depth))
            lines.append((f"uc_response = {uc_var_name}(**request_to_uc)", depth))
            lines.append(("response.append(uc_response)", depth))

        depth = depth_before
        lines.append(('return {"statusCode": 200, "body": response}', depth))

        return AWSHandlerGenResponse(
            self.join_with_depth(lines),
            "\n".join(pre_build_lines),
            {}
        )
