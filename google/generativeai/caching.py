# -*- coding: utf-8 -*-
# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import annotations

import copy
import dataclasses
from typing import Any, Iterable, Optional

from google.generativeai import protos
from google.generativeai.types import caching_types
from google.generativeai.types import content_types
from google.generativeai import string_utils
from google.generativeai.utils import flatten_update_paths
from google.generativeai.client import get_default_cache_client

from google.protobuf import field_mask_pb2


@string_utils.prettyprint
class CachedContent:
    """Cached content resource."""

    def __init__(self, name):
        """Fetches a `CachedContent` resource.

        Identical to `CachedContent.get`.

        Args:
            name: The resource name referring to the cached content.
        """
        client = get_default_cache_client()

        if "cachedContents/" not in name:
            name = "cachedContents/" + name

        request = protos.GetCachedContentRequest(name=name)
        response = client.get_cached_content(request)
        self._proto = response

    @property
    def name(self) -> str:
        return self._proto.name

    @property
    def model(self) -> str:
        return self._proto.model

    @property
    def display_name(self) -> str:
        return self._proto.display_name

    @property
    def usage_metadata(self) -> protos.CachedContent.UsageMetadata:
        return self._proto.usage_metadata

    @property
    def create_time(self) -> datetime.datetime:
        return self._proto.create_time
    @property
    def update_time(self) -> datetime.datetime:
        return self._proto.update_time
    @property
    def expire_time(self) -> datetime.datetime:
        return self._proto.expire_time

     def __new__(cls, param: str | Protos.CachedContent | CachedContent | dict) -> CachedContent:
         self = super().__new__(cls)
         
         if not isinstance(param, str):  # since we are using __init__ as a get call, this should work just fine
             if not hasattr(self, "_proto"):
                 self._proto = protos.CachedContent(updates)
                 return
    
              if not isinstance(updates, CachedContent):
                  updates = protos.CachedContent(updates)
              updates = type(updates).to_dict(updates, including_default_value_fields=False)
              for key, value in updates.items():
                  setattr(self._proto, key, value)
           
           return self
    def _with_updates(self, updates=None, **kwargs):
        if updates is None:
            updates = kwargs
        else:
            raise ValueError("supply an object, or key word arguments, not both")
        new = copy.deepcopy(self)
        new._update(updates)
        return new

    def _get_update_fields(self, **input_only_update_fields) -> protos.CachedContent:
        proto_paths = {
            "name": self.name,
        }
        proto_paths.update(input_only_update_fields)
        return protos.CachedContent(**proto_paths)

    def _apply_update(self, path, value):
        self = self._proto
        parts = path.split(".")
        for part in parts[:-1]:
            self = getattr(self, part)
        setattr(self, parts[-1], value)

    @staticmethod
    def _prepare_create_request(
        model: str,
        *,
        display_name: str | None = None,
        system_instruction: Optional[content_types.ContentType] = None,
        contents: Optional[content_types.ContentsType] = None,
        tools: Optional[content_types.FunctionLibraryType] = None,
        tool_config: Optional[content_types.ToolConfigType] = None,
        ttl: Optional[caching_types.TTLTypes] = None,
        expire_time: Optional[caching_types.ExpireTimeTypes] = None,
    ) -> protos.CreateCachedContentRequest:
        """Prepares a CreateCachedContentRequest."""
        if ttl and expire_time:
            raise ValueError(
                "Exclusive arguments: Please provide either `ttl` or `expire_time`, not both."
            )

        if "/" not in model:
            model = "models/" + model

        if display_name and len(display_name) > 128:
            raise ValueError("`display_name` must be no more than 128 unicode characters.")

        if system_instruction:
            system_instruction = content_types.to_content(system_instruction)

        tools_lib = content_types.to_function_library(tools)
        if tools_lib:
            tools_lib = tools_lib.to_proto()

        if tool_config:
            tool_config = content_types.to_tool_config(tool_config)

        if contents:
            contents = content_types.to_contents(contents)
            if not contents[-1].role:
                contents[-1].role = _USER_ROLE   # define _USER_ROLE at the top

        ttl = caching_types.to_optional_ttl(ttl)
        expire_time = caching_types.to_optional_expire_time(expire_time)

        cached_content = protos.CachedContent(
            model=model,
            display_name=display_name,
            system_instruction=system_instruction,
            contents=contents,
            tools=tools_lib,
            tool_config=tool_config,
            ttl=ttl,
            expire_time=expire_time,
        )

        return protos.CreateCachedContentRequest(cached_content=cached_content)

    @classmethod
    def create(
        cls,
        model: str,
        *,
        display_name: str | None = None,
        system_instruction: Optional[content_types.ContentType] = None,
        contents: Optional[content_types.ContentsType] = None,
        tools: Optional[content_types.FunctionLibraryType] = None,
        tool_config: Optional[content_types.ToolConfigType] = None,
        ttl: Optional[caching_types.TTLTypes] = None,
        expire_time: Optional[caching_types.ExpireTimeTypes] = None,
    ) -> CachedContent:
        """Creates `CachedContent` resource.

        Args:
            model: The name of the `model` to use for cached content creation.
                   Any `CachedContent` resource can be only used with the
                   `model` it was created for.
            display_name: The user-generated meaningful display name
                          of the cached content. `display_name` must be no
                          more than 128 unicode characters.
            system_instruction: Developer set system instruction.
            contents: Contents to cache.
            tools: A list of `Tools` the model may use to generate response.
            tool_config: Config to apply to all tools.
            ttl: TTL for cached resource (in seconds). Defaults to 1 hour.
                 `ttl` and `expire_time` are exclusive arguments.
            expire_time: Expiration time for cached resource.
                         `ttl` and `expire_time` are exclusive arguments.

        Returns:
            `CachedContent` resource with specified name.
        """
        client = get_default_cache_client()

        request = cls._prepare_create_request(
            model=model,
            display_name=display_name,
            system_instruction=system_instruction,
            contents=contents,
            tools=tools,
            tool_config=tool_config,
            ttl=ttl,
            expire_time=expire_time,
        )

        response = client.create_cached_content(request)
        result = object.__new__(CachedContent)
        result._update(response)
        return result

    @classmethod
    def get(cls, name: str) -> CachedContent:
        """Fetches required `CachedContent` resource.

        Args:
            name: The resource name referring to the cached content.

        Returns:
            `CachedContent` resource with specified `name`.
        """
        client = get_default_cache_client()

        if "cachedContents/" not in name:
            name = "cachedContents/" + name

        request = protos.GetCachedContentRequest(name=name)
        response = client.get_cached_content(request)
        result = object.__new__(CachedContent)
        result._update(response)
        return result

    @classmethod
    def list(cls, page_size: Optional[int] = 1) -> Iterable[CachedContent]:
        """Lists `CachedContent` objects associated with the project.

        Args:
            page_size: The maximum number of permissions to return (per page).
            The service may return fewer `CachedContent` objects.

        Returns:
            A paginated list of `CachedContent` objects.
        """
        client = get_default_cache_client()

        request = protos.ListCachedContentsRequest(page_size=page_size)
        for cc in client.list_cached_contents(request):
            cached_content = object.__new__(CachedContent)
            cached_content._update(cc)
            yield cached_content

    def delete(self) -> None:
        """Deletes `CachedContent` resource."""
        client = get_default_cache_client()

        request = protos.DeleteCachedContentRequest(name=self.name)
        client.delete_cached_content(request)
        return

    def update(
        self,
        updates: dict[str, Any],
    ) -> CachedContent:
        """Updates requested `CachedContent` resource.

        Args:
            updates: The list of fields to update. Currently only
            `ttl/expire_time` is supported as an update path.

        Returns:
            `CachedContent` object with specified updates.
        """
        client = get_default_cache_client()

        if "ttl" in updates and "expire_time" in updates:
            raise ValueError(
                "Exclusive arguments: Please provide either `ttl` or `expire_time`, not both."
            )

        field_mask = field_mask_pb2.FieldMask()

        updates = flatten_update_paths(updates)
        for update_path in updates:
            update_path_val = updates.get(update_path)
            if update_path == "ttl":
                updates[update_path] = caching_types.to_optional_ttl(update_path_val)
            elif update_path == "expire_time":
                updates[update_path] = caching_types.to_optional_expire_time(update_path_val)
            else:
                raise ValueError(
                    f"Bad update name: As of now, only `ttl`  or `expire_time` can be \
                    updated for `CachedContent`. Got: `{update_path}` instead."
                )

            field_mask.paths.append(update_path)

        for path, value in updates.items():
            self._apply_update(path, value)

        request = protos.UpdateCachedContentRequest(
            cached_content=self._get_update_fields(**updates), update_mask=field_mask
        )
        updated_cc = client.update_cached_content(request)
        self._update(updated_cc)

        return self
