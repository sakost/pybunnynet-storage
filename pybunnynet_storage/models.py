from datetime import datetime
from pathlib import Path
from uuid import UUID

from pydantic import BaseModel, Field


class StorageObject(BaseModel):
    guid: UUID = Field(alias="Guid")
    object_name: Path = Field(alias="ObjectName")
    is_directory: bool = Field(alias="IsDirectory")
    storage_zone_name: str = Field(alias="StorageZoneName")
    path: Path = Field(alias="Path")
    length: int = Field(alias="Length")
    last_changed: datetime = Field(alias="LastChanged")
    server_id: int = Field(alias="ServerId")
    array_number: int = Field(alias="ArrayNumber")
    user_id: UUID = Field(alias="UserId")
    content_type: str = Field(alias="ContentType")
    date_created: datetime = Field(alias="DateCreated")
    storage_zone_id: int = Field(alias="StorageZoneId")
    checksum: str | None = Field(alias="Checksum")
    replicated_zones: str | None = Field(alias="ReplicatedZones")
