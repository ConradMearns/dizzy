# AUTO-GENERATED — do not edit
from dataclasses import dataclass
from typing import Callable

from gen_def.pydantic.events import StepPerformed
from gen_def.pydantic.events import EntityConsumed
from gen_def.pydantic.events import EntityProduced
from gen_def.pydantic.events import EntityDerived
from gen_def.pydantic.events import BatchCompleted
from gen_def.pydantic.events import BatchRunFailed
from gen_def.pydantic.query.get_batch import GetBatchInput, GetBatchOutput
from gen_def.pydantic.query.get_recipe import GetRecipeInput, GetRecipeOutput
from gen_def.pydantic.query.get_recipe_steps import GetRecipeStepsInput, GetRecipeStepsOutput
from gen_def.pydantic.query.get_step_inputs import GetStepInputsInput, GetStepInputsOutput
from gen_def.pydantic.query.check_inventory import CheckInventoryInput, CheckInventoryOutput


@dataclass
class run_batch_emitters:
    step_performed: Callable[[StepPerformed], None]
    entity_consumed: Callable[[EntityConsumed], None]
    entity_produced: Callable[[EntityProduced], None]
    entity_derived: Callable[[EntityDerived], None]
    batch_completed: Callable[[BatchCompleted], None]
    batch_run_failed: Callable[[BatchRunFailed], None]


@dataclass
class run_batch_queries:
    get_batch: Callable[[GetBatchInput], GetBatchOutput]
    get_recipe: Callable[[GetRecipeInput], GetRecipeOutput]
    get_recipe_steps: Callable[[GetRecipeStepsInput], GetRecipeStepsOutput]
    get_step_inputs: Callable[[GetStepInputsInput], GetStepInputsOutput]
    check_inventory: Callable[[CheckInventoryInput], CheckInventoryOutput]


@dataclass
class run_batch_context:
    emit: run_batch_emitters
    query: run_batch_queries
