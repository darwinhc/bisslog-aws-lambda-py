from typing import Tuple, List

from ..aws_handler_generator import AWSHandlerGenerator
from ..aws_handler_gen_response import AWSHandlerGenResponse

class DefaultHandlerGenerator(AWSHandlerGenerator):

    def __call__(self):

        lines: List[Tuple[str, int]] = []
        depth = 1
        lines.append(('raise RuntimeError(', depth))
        depth += 1
        lines.append(('f"Unrecognized event format. No matching handler found for the incoming event:'
                     ' {str(event)[:500]}"', depth))
        depth -= 1

        lines.append((')', depth))
        return AWSHandlerGenResponse(self.join_with_depth(lines))

