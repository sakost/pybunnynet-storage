from enum import Enum
from io import BytesIO
from pathlib import Path
from urllib import parse

import httpx

from pybunnynet_storage.exceptions import (
    EmptyParameter,
    NetworkException,
    StatusCodeException,
)
from pybunnynet_storage.models import StorageObject


class StorageZoneEnum(str, Enum):
    FALKENSTEIN = ""
    NEW_YORK = "ny."
    LOS_ANGELES = "la."
    SINGAPORE = "sg."
    SYDNEY = "syd."


class Storage:
    BASE_URL = "https://{storage_zone_region}storage.bunnycdn.com/{storage_zone}/"
    CHUNK_SIZE = 4096

    def __init__(
        self,
        api_key: str,
        storage_zone: str,
        storage_zone_region: StorageZoneEnum = StorageZoneEnum.FALKENSTEIN,
        base_url: str | None = None,
    ):
        if not storage_zone:
            raise EmptyParameter("storage_zone is not set")

        base_url = base_url or type(self).BASE_URL

        base_url = base_url.format(
            storage_zone_region=storage_zone_region.value,
            storage_zone=storage_zone,
        )

        self._http_client = httpx.Client(
            headers={
                "AccessKey": api_key,
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            base_url=base_url,
        )
        self._http_async_client = httpx.AsyncClient(
            headers=self._http_client.headers,
            base_url=self._http_client.base_url,
        )

    def _make_request(self, method: str, url: str, **kwargs) -> httpx.Response:
        try:
            response = self._http_client.request(method, url, **kwargs)
        except httpx.HTTPError as exc:
            raise NetworkException() from exc

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise StatusCodeException(response.status_code) from exc

        return response

    async def _async_make_request(self, method: str, url: str, **kwargs):
        try:
            response = await self._http_async_client.request(method, url, **kwargs)
        except httpx.HTTPError as exc:
            raise NetworkException() from exc

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise StatusCodeException(response.status_code) from exc

        return response

    @staticmethod
    def _path_to_url(path: Path):
        return parse.quote(Path(path).as_posix())

    async def async_download_file(
        self,
        storage_path: Path,
        chunk_size: int | None = None,
    ) -> BytesIO:
        if chunk_size is None:
            chunk_size = Storage.CHUNK_SIZE

        url = self._path_to_url(storage_path)
        buffer = BytesIO()

        response = await self._async_make_request("GET", url)

        async for chunk in response.aiter_bytes(chunk_size=chunk_size):
            buffer.write(chunk)

        return buffer

    def download_file(
        self,
        storage_path: Path,
        chunk_size: int | None = None,
    ) -> BytesIO:
        if chunk_size is None:
            chunk_size = Storage.CHUNK_SIZE

        url = self._path_to_url(storage_path)
        buffer = BytesIO()

        response = self._make_request("GET", url)

        for chunk in response.iter_bytes(chunk_size=chunk_size):
            buffer.write(chunk)

        return buffer

    async def async_upload_file(
        self,
        data_buffer: BytesIO,
        storage_path: Path,
    ):
        url = self._path_to_url(storage_path)
        await self._async_make_request(
            "PUT", url, files={storage_path.name: data_buffer}
        )

    def upload_file(
        self,
        data_buffer: BytesIO,
        storage_path: Path,
    ):
        url = self._path_to_url(storage_path)
        self._make_request("PUT", url, files={storage_path.name: data_buffer})

    async def async_delete_file(self, storage_path: Path):
        url = self._path_to_url(storage_path)
        await self._async_make_request("DELETE", url)

    def delete_file(self, storage_path: Path):
        url = self._path_to_url(storage_path)
        self._make_request("DELETE", url)

    async def async_get_object_list(self, storage_path: Path) -> list:
        url = self._path_to_url(storage_path)
        response = await self._async_make_request("GET", self._fix_object_list_url(url))
        response.json()
        data = response.json()

        storage_list = []

        for raw_obj in data:
            obj = StorageObject(**raw_obj)
            storage_list.append(obj)
        return storage_list

    def get_object_list(self, storage_path: Path) -> list:
        url = self._path_to_url(storage_path)
        response = self._make_request("GET", self._fix_object_list_url(url))

        data = response.json()

        storage_list = []

        for raw_obj in data:
            obj = StorageObject(**raw_obj)
            storage_list.append(obj)
        return storage_list

    @staticmethod
    def _fix_object_list_url(url):
        return url + "/"
