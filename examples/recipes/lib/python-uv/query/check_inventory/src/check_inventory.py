# Whether an available entity of a given type exists, and its id.
from gen_int.python.query.check_inventory import check_inventory_context
from gen_def.pydantic.query.check_inventory import CheckInventoryInput, CheckInventoryOutput
from gen_def.sqla.models.inventory import InventoryEntity


def check_inventory(
    input: CheckInventoryInput, context: check_inventory_context
) -> CheckInventoryOutput:
    lot = (
        context.adapter.session.query(InventoryEntity)
        .filter(
            InventoryEntity.entity_type == input.entity_type,
            InventoryEntity.available == True,  # noqa: E712 — SQLAlchemy column comparison
        )
        .first()
    )
    if lot is None:
        return CheckInventoryOutput(available=False, entity_id=None)
    return CheckInventoryOutput(available=True, entity_id=lot.id)
