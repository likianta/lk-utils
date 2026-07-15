import typing as tp
from uuid import UUID
from uuid import uuid3
from uuid import uuid4

# https://chatgpt.com/share/6a56eb55-3678-83ee-96f0-def6ee9c3c1f
_MY_NAMESPACE = UUID('250a9d96-a3be-4631-85d9-6d2308fff567')


def uuid(name: tp.Optional[str] = None) -> str:
    return uuid4().hex if name is None else uuid3(_MY_NAMESPACE, name).hex
