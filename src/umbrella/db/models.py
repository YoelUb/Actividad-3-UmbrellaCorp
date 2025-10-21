import datetime
from typing import Optional
from zoneinfo import ZoneInfo
from sqlmodel import SQLModel, Field


def get_madrid_time() -> datetime.datetime:

    return datetime.datetime.now(ZoneInfo("Europe/Madrid"))


class Evento(SQLModel, table=True):


    id: Optional[int] = Field(default=None, primary_key=True)

    event_id:str = Field(index=True)

    tipo_dato: str

    worker: str

    status: str

    created_at: datetime = Field(default_factory=get_madrid_time, nullable=False)

