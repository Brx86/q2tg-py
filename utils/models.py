from pydantic import BaseModel


class Forward(BaseModel):
    a: dict[int, int]
    u: dict[int, int]
    g: dict[int, int]


class Config(BaseModel):
    log_level: str
    log_format: str
    qq_ws: str
    qq_http: str
    tg_api: str
    tg_token: str
    forward: Forward


class Message(BaseModel):
    type: str
    data: dict


class File(BaseModel):
    name: str
    size: int
    url: str


class Sender(BaseModel):
    card: str | None
    level: str | None
    role: str | None
    nickname: str = "anonymous"
    sex: str
    user_id: int


class DataModel(BaseModel):
    post_type: str | None
    notice_type: str | None
    time: int
    self_id: int | None
    status: dict | None
    message_type: str | None
    meta_event_type: str | None
    user_id: int | None
    group_id: int | None
    sender: Sender | None
    raw_message: str | None = ""
    message: list[Message] | None
    message_id: int | None = 0
    file: File | None
