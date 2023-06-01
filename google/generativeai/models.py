# -*- coding: utf-8 -*-
# Copyright 2023 Google LLC
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
import re
from typing import Optional, List

import google.ai.generativelanguage as glm
from google.generativeai.client import get_default_model_client
from google.generativeai.types import model_types

# A bare model name, with no preceding namespace. e.g. foo-bar-001
_BARE_MODEL_NAME = re.compile(r"^\w+-\w+-\d+$")


def get_model(name: str, *, client=None) -> model_types.Model:
    """Get the `types.Model` for the given model name."""
    if client is None:
        client = get_default_model_client()

    # If only a bare model name is passed, give it the structure we expect.
    if _BARE_MODEL_NAME.match(name):
        name = f"models/{name}"

    result = client.get_model(name=name)
    result = type(result).to_dict(result)
    return model_types.Model(**result)


class ModelsIterable(model_types.ModelsIterable):
    def __init__(
        self,
        *,
        page_size: int,
        page_token: str | None,
        models: List[model_types.Model],
        client: glm.ModelServiceClient | None,
    ):
        self._page_size = page_size
        self._page_token = page_token
        self._models = models
        self._client = client

    def __iter__(self):
        while self:
            page = self._models
            yield from page
            self = self._next_page()

    def _next_page(self):
        if not self._page_token:
            return None
        return _list_models(
            page_size=self._page_size, page_token=self._page_token, client=self._client
        )


def _list_models(page_size, page_token, client):
    result = client.list_models(page_size=page_size, page_token=page_token)
    result = result._response
    result = type(result).to_dict(result)

    result["models"] = [model_types.Model(**mod) for mod in result["models"]]
    result["page_size"] = page_size
    result["page_token"] = result.pop("next_page_token")
    result["client"] = client
    return ModelsIterable(**result)


def list_models(
    *, page_size: int | None = None, client: glm.ModelServiceClient | None = None
) -> model_types.ModelsIterable:
    """Lists available models.

    ```
    import pprint
    for model in genai.list_models():
        pprint.pprint(model)
    ```

    Args:
        page_size: How many `types.Models` to fetch per page (api call).
        client: You may pass a `glm.ModelServiceClient` instead of using the default client.

    Returns:
        An iterable of `types.Model` objects.

    """
    if client is None:
        client = get_default_model_client()

    return _list_models(page_size, page_token=None, client=client)
