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
import copy
import math
import datetime
from typing import Any
import unittest
import unittest.mock as mock

import google.ai.generativelanguage as glm

from google.generativeai import caching
from google.generativeai.types import caching_types

from google.generativeai import client
from absl.testing import absltest
from absl.testing import parameterized


class UnitTests(parameterized.TestCase):
    def setUp(self):
        self.client = unittest.mock.MagicMock()

        client._client_manager.clients["cache"] = self.client

        self.observed_requests = []

        def add_client_method(f):
            name = f.__name__
            setattr(self.client, name, f)
            return f

        @add_client_method
        def create_cached_content(
            request: glm.CreateCachedContentRequest,
            **kwargs,
        ) -> glm.CachedContent:
            self.observed_requests.append(request)
            return glm.CachedContent(
                name="cachedContent/test-cached-content",
                model="models/gemini-1.0-pro-001",
                create_time="2000-01-01T01:01:01.123456Z",
                update_time="2000-01-01T01:01:01.123456Z",
                expire_time="2000-01-01T01:01:01.123456Z",
            )

        @add_client_method
        def get_cached_content(
            request: glm.GetCachedContentRequest,
            **kwargs,
        ) -> glm.CachedContent:
            self.observed_requests.append(request)
            return glm.CachedContent(
                name="cachedContent/test-cached-content",
                model="models/gemini-1.0-pro-001",
                create_time="2000-01-01T01:01:01.123456Z",
                update_time="2000-01-01T01:01:01.123456Z",
                expire_time="2000-01-01T01:01:01.123456Z",
            )

        @add_client_method
        def list_cached_contents(
            request: glm.ListCachedContentsRequest,
            **kwargs,
        ) -> glm.ListCachedContentsResponse:
            self.observed_requests.append(request)
            return [
                glm.CachedContent(
                    name="cachedContent/test-cached-content-1",
                    model="models/gemini-1.0-pro-001",
                    create_time="2000-01-01T01:01:01.123456Z",
                    update_time="2000-01-01T01:01:01.123456Z",
                    expire_time="2000-01-01T01:01:01.123456Z",
                ),
                glm.CachedContent(
                    name="cachedContent/test-cached-content-2",
                    model="models/gemini-1.0-pro-001",
                    create_time="2000-01-01T01:01:01.123456Z",
                    update_time="2000-01-01T01:01:01.123456Z",
                    expire_time="2000-01-01T01:01:01.123456Z",
                ),
            ]

        @add_client_method
        def update_cached_content(
            request: glm.UpdateCachedContentRequest,
            **kwargs,
        ) -> glm.CachedContent:
            self.observed_requests.append(request)
            return glm.CachedContent(
                name="cachedContent/test-cached-content",
                model="models/gemini-1.0-pro-001",
                create_time="2000-01-01T01:01:01.123456Z",
                update_time="2000-01-01T01:01:01.123456Z",
                expire_time="2000-01-01T03:01:01.123456Z",
            )

        @add_client_method
        def delete_cached_content(
            request: glm.DeleteCachedContentRequest,
            **kwargs,
        ) -> None:
            self.observed_requests.append(request)

    def test_create_cached_content(self):

        def add(a: int, b: int) -> int:
            return a + b

        cc = caching.CachedContent.create(
            name="test-cached-content",
            model="models/gemini-1.0-pro-001",
            contents=["Add 5 and 6"],
            tools=[add],
            tool_config={"function_calling_config": "ANY"},
            system_instruction="Always add 10 to the result.",
            ttl=datetime.timedelta(minutes=30),
        )
        self.assertIsInstance(self.observed_requests[-1], glm.CreateCachedContentRequest)
        self.assertIsInstance(cc, caching.CachedContent)
        self.assertEqual(cc.name, "cachedContent/test-cached-content")
        self.assertEqual(cc.model, "models/gemini-1.0-pro-001")

    @parameterized.named_parameters(
        [
            dict(
                testcase_name="ttl-is-int-seconds",
                ttl=7200,
            ),
            dict(
                testcase_name="ttl-is-timedelta",
                ttl=datetime.timedelta(hours=2),
            ),
            dict(
                testcase_name="ttl-is-dict",
                ttl={"seconds": 7200},
            ),
            dict(
                testcase_name="ttl-is-none-default-to-1-hr",
                ttl=None,
            ),
        ]
    )
    def test_expiration_types_for_create_cached_content(self, ttl):
        cc = caching.CachedContent.create(
            name="test-cached-content",
            model="models/gemini-1.0-pro-001",
            contents=["cache this please for 2 hours"],
            ttl=ttl,
        )
        self.assertIsInstance(self.observed_requests[-1], glm.CreateCachedContentRequest)
        self.assertIsInstance(cc, caching.CachedContent)

    def test_get_cached_content(self):
        cc = caching.CachedContent.get(name="cachedContent/test-cached-content")
        self.assertIsInstance(self.observed_requests[-1], glm.GetCachedContentRequest)
        self.assertIsInstance(cc, caching.CachedContent)
        self.assertEqual(cc.name, "cachedContent/test-cached-content")
        self.assertEqual(cc.model, "models/gemini-1.0-pro-001")

    def test_list_cached_contents(self):
        ccs = list(caching.CachedContent.list(page_size=2))
        self.assertIsInstance(self.observed_requests[-1], glm.ListCachedContentsRequest)
        self.assertLen(ccs, 2)
        self.assertIsInstance(ccs[0], caching.CachedContent)
        self.assertIsInstance(ccs[1], caching.CachedContent)

    def test_update_cached_content_invalid_update_paths(self):
        update_masks = dict(
            name="change",
            model="models/gemini-1.5-pro-001",
            system_instruction="Always add 10 to the result.",
            contents=["add this Content"],
        )

        cc = caching.CachedContent.get(name="cachedContent/test-cached-content")
        with self.assertRaises(ValueError):
            cc.update(updates=update_masks)

    def test_update_cached_content_valid_update_paths(self):
        update_masks = dict(
            ttl=datetime.timedelta(hours=2),
        )

        cc = caching.CachedContent.get(name="cachedContent/test-cached-content")
        cc = cc.update(updates=update_masks)
        self.assertIsInstance(self.observed_requests[-1], glm.UpdateCachedContentRequest)
        self.assertIsInstance(cc, caching.CachedContent)

    def test_delete_cached_content(self):
        cc = caching.CachedContent.get(name="cachedContent/test-cached-content")
        cc.delete()
        self.assertIsInstance(self.observed_requests[-1], glm.DeleteCachedContentRequest)

        cc = caching.delete_cached_content(name="cachedContent/test-cached-content")
        self.assertIsInstance(self.observed_requests[-1], glm.DeleteCachedContentRequest)

    def test_auto_delete_cached_content_with_context_manager(self):
        with caching.CachedContent.create(
            name="test-cached-content",
            model="models/gemini-1.0-pro-001",
            contents=["Add 5 and 6"],
            system_instruction="Always add 10 to the result.",
            ttl=datetime.timedelta(minutes=30),
        ) as cc:
            ...  # some logic

        self.assertIsInstance(self.observed_requests[-1], glm.DeleteCachedContentRequest)


if __name__ == "__main__":
    absltest.main()
