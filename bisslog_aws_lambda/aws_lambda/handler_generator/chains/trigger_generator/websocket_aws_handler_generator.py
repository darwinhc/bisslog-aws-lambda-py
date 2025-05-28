"""
Module for generating AWS Lambda handler code for WebSocket API Gateway triggers.

This generator creates routing logic based on the route key from incoming WebSocket
events and delegates execution to the appropriate use case.
"""
from typing import List, Optional, Tuple, Set

from bisslog_schema.schema.enums.trigger_type import TriggerEnum
from bisslog_schema.schema.triggers.trigger_info import TriggerInfo
from bisslog_schema.schema.triggers.trigger_websocket import TriggerWebsocket

from .aws_handler_trigger_generator import AWSHandlerTriggerGenerator
from ...aws_handler_gen_response import AWSHandlerGenResponse


class WebSocketAWSHandlerGenerator(AWSHandlerTriggerGenerator):
    """
    Generates AWS Lambda handler code for WebSocket API Gateway triggers.

    This class analyzes configured route keys and generates Python code to dispatch
    incoming WebSocket events to mapped use cases, supporting optional field mappers.
    """

    main_conditional = 'if "requestContext" in event and ' \
                       '"routeKey" in event.get("requestContext", {}):'

    @staticmethod
    def _generate_conditional_by_route(route_key: str) -> str:
        """
        Constructs a conditional to match a specific WebSocket route key.

        Parameters
        ----------
        route_key : str
            The expected route key from the WebSocket event.

        Returns
        -------
        str
            Python code string for conditional matching.
        """

        return f'if "{route_key}" in event["requestContext"]["routeKey"]:'

    @classmethod
    def _generate_ws_mapper(cls, required_source: Set[str], depth: int = 0,
                            full: bool = False) -> str:
        """
        Generates code for a Mapper that extracts WebSocket-specific fields from the event.

        Parameters
        ----------
        required_source : Set[str]
            Required data fields like "body", "connection_id", etc.
        depth : int, optional
            Indentation level.
        full : bool, optional
            Whether to include all mapping fields regardless of what's required.

        Returns
        -------
        str
            Python code block that defines the Mapper.
        """
        buffer = depth * cls.indent + 'mapper_ws = Mapper("mapper_ws", {\n'
        depth += 1
        if "body" in required_source or full:
            buffer += depth * cls.indent + '"event.body": "body",\n'
        if "connection_id" in required_source or full:
            buffer += depth * cls.indent + '"event.requestContext.connectionId": "connection_id",\n'
        if "headers" in required_source or full:
            buffer += depth * cls.indent + '"event.headers": "headers",\n'
        if "route_key" in required_source or full:
            buffer += depth * cls.indent + '"event.requestContext.routeKey": "route_key",\n'
        depth -= 1
        buffer += "})"
        return buffer

    def __call__(self, triggers: List[TriggerInfo],
                 uc_var_name: str) -> Optional[AWSHandlerGenResponse]:
        """
        Generates handler code for WebSocket triggers by mapping route keys to use cases.

        Parameters
        ----------
        triggers : List[TriggerInfo]
            List of metadata trigger definitions.
        uc_var_name : str
            Name of the use case to invoke.

        Returns
        -------
        Optional[AWSHandlerGenResponse]
            Generated handler response or None if no valid triggers found.
        """
        triggers = [
            trigger for trigger in triggers
            if trigger.type == TriggerEnum.WEBSOCKET
               and isinstance(trigger.options, TriggerWebsocket)
        ]

        if not triggers:
            return None

        is_one_trigger = len(triggers) == 1
        depth = 1

        lines: List[Tuple[str, int]] = [(self.main_conditional, depth)]
        depth += 1

        required_mapper_source = set()
        pre_build_lines = []

        lines.append((
            'mapped_standard_request = mapper_ws.map({"event": event, "context": context})',
            depth
        ))

        mapper_in_each = not all(trigger.options.mapper for trigger in triggers)
        before_depth = depth

        for i, trigger in enumerate(triggers):
            depth = before_depth
            keyname = trigger.keyname
            options = trigger.options

            conditional = self._generate_conditional_by_route(options.route_key)
            if is_one_trigger:
                conditional = "# " + conditional
                lines.append((conditional, depth))
            else:
                lines.append((conditional, depth))
                depth += 1

            if options.mapper:
                mapper_name = self.generate_mapper_name(trigger.type.val, keyname, i)
                line_mapper_construct, req_mapper_src_i = self.generate_mapper_with_requires(
                    mapper_name, options.mapper)
                pre_build_lines.append(line_mapper_construct)
                required_mapper_source.update(req_mapper_src_i)
                lines.append((
                    f"request_to_uc : dict = {mapper_name}.map(mapped_standard_request)", depth
                ))
            else:
                lines.append(("request_to_uc = mapped_standard_request", depth))

            lines.append((f"uc_response = {uc_var_name}(**request_to_uc)", depth))
            lines.append(('return {"statusCode": 200, "body": uc_response}', depth))

        pre_build_lines.append(
            self._generate_ws_mapper(required_mapper_source, full=not mapper_in_each)
        )

        return AWSHandlerGenResponse(self.join_with_depth(lines), "\n".join(pre_build_lines), {})
