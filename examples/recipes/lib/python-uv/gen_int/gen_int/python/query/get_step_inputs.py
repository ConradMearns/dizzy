# AUTO-GENERATED — do not edit
from dataclasses import dataclass
from typing import Protocol

from gen_def.pydantic.query.get_step_inputs import GetStepInputsInput, GetStepInputsOutput
from gen_int.python.adapters.sqla import SqlaAdapter


@dataclass
class get_step_inputs_context:
    adapter: SqlaAdapter


class get_step_inputs_query(Protocol):
    """The typed inputs of a recipe's steps, as parallel lists"""

    def __call__(
        self, input: GetStepInputsInput, context: get_step_inputs_context
    ) -> GetStepInputsOutput:
        ...
