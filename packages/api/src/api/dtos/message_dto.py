from typing import Literal, TypedDict


class MessageDTO(TypedDict):
    content: str
    sender_type: Literal['USER', 'AI']
    sender_name: str
