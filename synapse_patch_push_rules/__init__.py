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
import logging
from typing import Any, Dict, List, Union

import attr
from synapse.module_api import ModuleApi
from synapse.module_api.errors import ConfigError

logger = logging.getLogger(__name__)


@attr.s(auto_attribs=True, frozen=True)
class PushRule:
    kind: str
    conditions: List[Dict[str, Any]]
    actions: List[Union[str, Dict[str, str]]]


class PushRulesPatcherConfig:
    def __init__(self, config: Dict[str, Any]) -> None:
        self.rules: Dict[str, PushRule] = {}

        rules = config["rules"]
        for rule_id, rule in rules.items():
            self.rules[rule_id] = PushRule(**rule)


class PushRulesPatcher:
    def __init__(self, config: PushRulesPatcherConfig, api: ModuleApi):
        # Keep a reference to the config and Module API
        self._api = api
        self._config = config

        self._api.register_account_validity_callbacks(
            on_user_registration=self.set_push_rules_for_user,
        )

    @staticmethod
    def parse_config(config: Dict[str, Any]) -> PushRulesPatcherConfig:
        if "rules" not in config:
            raise ConfigError("Missing 'rules' in module configuration")

        if not isinstance(config["rules"], dict):
            raise ConfigError("'rules' must be a dictionary")

        return PushRulesPatcherConfig(config)

    async def set_push_rules_for_user(self, user_id: str) -> None:
        """Create new push rules for the given user.
        Implements the on_user_registration account validity callback.
        """
        # If we're running on a worker, make this a noop. on_user_registration callbacks
        # should only be called on the main process, so this is mostly a stopgap in case
        # something changes in the future.
        if self._api.worker_app:
            logger.warning(
                "Attempted to run callback 'set_push_rules_for_user' on a worker, aborting"
            )
            return

        for rule_id, rule in self._config.rules.items():
            await self._api.add_push_rule_for_user(
                user_id=user_id,
                scope="global",
                kind=rule.kind,
                rule_id=rule_id,
                conditions=rule.conditions,
                actions=rule.actions,
            )
