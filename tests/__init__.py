# Copyright 2022 The Matrix.org Foundation C.I.C.
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
from asyncio import Future
from typing import Any, Awaitable, Dict, Optional, TypeVar
from unittest.mock import Mock

from synapse.module_api import ModuleApi

from synapse_patch_push_rules import PushRulesPatcher

TV = TypeVar("TV")


def make_awaitable(result: TV) -> Awaitable[TV]:
    """
    Makes an awaitable, suitable for mocking an `async` function.
    This uses Futures as they can be awaited multiple times so can be returned
    to multiple callers.
    """
    future = Future()  # type: ignore
    future.set_result(result)
    return future


def create_module(config: Optional[Dict[str, Any]] = None) -> PushRulesPatcher:
    # Create a mock based on the ModuleApi spec, but override some mocked functions
    # because some capabilities are needed for running the tests.
    module_api = Mock(spec=ModuleApi)
    module_api.add_push_rule_for_user = Mock(return_value=make_awaitable(None))

    # If necessary, give parse_config some configuration to parse.
    if config is None:
        config = {}
    parsed_config = PushRulesPatcher.parse_config(config)

    return PushRulesPatcher(parsed_config, module_api)
