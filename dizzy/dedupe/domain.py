from pydantic import BaseModel
from pydantic.functional_validators import BeforeValidator
from typing import Annotated, Union
import hashlib


class ItemID:
    HASH_SIZE = 8  # 8 bytes = 64 bits

    def __init__(self, hash_bytes: bytes):
        if len(hash_bytes) != self.HASH_SIZE:
            raise ValueError(f"ItemID must be {self.HASH_SIZE} bytes long")
        self._bytes = hash_bytes

    @classmethod
    def from_bytes(cls, data: bytes) -> "ItemID":
        digest = hashlib.blake2b(data, digest_size=cls.HASH_SIZE).digest()
        return cls(digest)

    @classmethod
    def from_hex(cls, hex_str: str) -> "ItemID":
        return cls(bytes.fromhex(hex_str))

    def to_hex(self) -> str:
        return self._bytes.hex()

    def __str__(self):
        return self.to_hex()

    def __repr__(self):
        return f"ItemID({self.to_hex()})"

    def __eq__(self, other):
        if isinstance(other, ItemID):
            return self._bytes == other._bytes
        return NotImplemented

    def __hash__(self):
        return hash(self._bytes)


# # Make it pydantic-compatible via Annotated validator
# def _parse_itemid(value: Union[str, ItemID]) -> ItemID:
#     if isinstance(value, ItemID):
#         return value
#     return ItemID.from_hex(value)


# PydanticItemID = Annotated[ItemID, BeforeValidator(_parse_itemid)]


# # Example usage in a Pydantic model
# class MyModel(BaseModel):
#     id: PydanticItemID


# # --- Example usage ---

# # Create an ID from data
# data = b"hello world"
# item_id = ItemID.from_bytes(data)

# # Serialize in model
# model = MyModel(id=item_id)
# print(model.json())  # → {"id":"hexstring"}

# # Deserialize from JSON
# loaded = MyModel.model_validate({"id": item_id.to_hex()})
# assert loaded.id == item_id
