from typing import List, Optional, Tuple, Set

from bisslog_schema.schema.enums.trigger_type import TriggerEnum
from bisslog_schema.schema.triggers.trigger_http import TriggerHttp
from bisslog_schema.schema.triggers.trigger_info import TriggerInfo

from .aws_handler_trigger_generator import AWSHandlerTriggerGenerator
from ...aws_handler_gen_response import AWSHandlerGenResponse


class HttpAWSHandlerGenerator(AWSHandlerTriggerGenerator):

    init = 'if "httpMethod" in event:'

    @staticmethod
    def _generate_conditional_by_path_method(path: str, method: str) -> str:
        path_standard = path.replace("<", "{").replace(">", "}")

        return (f'if event.get("resource", "").endswith("{path_standard}")' 
                f' and event.get("httpMethod") == "{method.upper()}":')


    @classmethod
    def _generate_http_mapper(cls, required_source: Set[str], depth: int = 0, full: bool = False):

        buffer = depth * cls.indent + """mapper_http = Mapper("mapper_http", {\n"""

        depth += 1
        if "body" in required_source or full:
            buffer += depth*cls.indent + """"event.payload": "body",\n"""
        if "params" in required_source or full:
            buffer += depth*cls.indent + """"event.queryStringParameters": "params",\n"""

        if "path_query" in required_source or full:
            buffer += depth*cls.indent + """"event.pathParameters": "path_query",\n"""
        if "headers" in required_source or full:
            buffer += depth*cls.indent + """"event.headers": "headers",\n"""

        depth -= 1
        buffer += "})"
        return buffer



    def __call__(self, triggers: List[TriggerInfo],
                 uc_var_name: str) -> Optional[AWSHandlerGenResponse]:
        triggers = [
            trigger for trigger in triggers
            if trigger.type == TriggerEnum.HTTP and isinstance(trigger.options, TriggerHttp)
        ]


        if not triggers:
            return None

        is_one_trigger = len(triggers) == 1
        depth = 1

        lines: List[Tuple[str, int]] = [(self.init, depth)]
        depth += 1
        required_mapper_source = set()
        pre_build_lines = []

        lines.append(
            (f'mapped_standard_request = mapper_http.map({{"event": event, "context": context}})',
             depth))
        mapper_in_each = not all(trigger.options.mapper for trigger in triggers)

        before_depth = depth
        for i, trigger in enumerate(triggers):
            depth = before_depth
            keyname = trigger.keyname
            options = trigger.options


            conditional = self._generate_conditional_by_path_method(options.path, options.method)

            if is_one_trigger:
                conditional = "# " + conditional
                lines.append((conditional, depth))
            else:
                lines.append((conditional, depth))
                depth += 1

            if options.mapper:
                mapper_name = self.generate_mapper_name(trigger.type.val, keyname, i)
                line_mapper_construct, required_mapper_source_i = self.generate_mapper_with_requires(
                    mapper_name, options.mapper)
                pre_build_lines.append(line_mapper_construct)
                required_mapper_source.update(required_mapper_source_i)
                lines.append(
                    (f"request_to_uc : dict = {mapper_name}.map(mapped_standard_request)", depth))
            else:
                lines.append((f'request_to_uc = mapped_standard_request', depth))
                lines.append((f'request_to_uc.update(mapped_standard_request.get("params"))', depth))
                lines.append((f'request_to_uc.update(mapped_standard_request.get("path_query"))', depth))
            lines.append((f"uc_response = {uc_var_name}(**request_to_uc)", depth))
            lines.append((f"""return {{"statusCode": 200, "body": uc_response}}""", depth))

        pre_build_lines.append(
            self._generate_http_mapper(required_mapper_source, full=not mapper_in_each))


        return AWSHandlerGenResponse(self.join_with_depth(lines), "\n".join(pre_build_lines), {})


