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
from unittest.mock import Mock

import aiounittest
from synapse.module_api.errors import ConfigError

from tests import create_module


class PushRulesPatcherTestCase(aiounittest.AsyncTestCase):
    async def test_no_rules(self) -> None:
        """Tests that the module can't be created if 'rules' is missing from the
        configuration.
        """
        with self.assertRaises(ConfigError):
            create_module()

    async def test_rules_no_dict(self) -> None:
        """Tests that the module can't be created if the configured set of rules isn't a
        dictionary.
        """
        with self.assertRaises(ConfigError):
            create_module({"rules": "hello"})

    async def test_set_rule_actions(self) -> None:
        """Tests that, when configuring the module with multiple rules and calling the
        callback, each rule is changed for the newly registered user.
        """
        rule_id1 = "foo"
        rule_id2 = "bar"
        actions1 = ["dont_notify"]
        actions2 = ["notify"]
        kind = "content"
        user_id = "@user:example.com"

        # Configure the module with 2 different rules.
        module = create_module(
            {
                "rules": {
                    rule_id1: {
                        "kind": kind,
                        "actions": actions1,
                    },
                    rule_id2: {
                        "kind": kind,
                        "actions": actions2,
                    },
                }
            }
        )

        # Run the callback.
        await module.set_push_rules_for_user(user_id)

        # Check the module API got called twice, and with the right arguments.
        set_push_rule_action_mock: Mock = module._api.set_push_rule_action  # type: ignore[assignment]

        self.assertEqual(set_push_rule_action_mock.call_count, 2)

        set_push_rule_action_mock.assert_any_call(
            user_id=user_id,
            scope="global",
            kind=kind,
            rule_id=rule_id1,
            actions=actions1,
        )

        set_push_rule_action_mock.assert_any_call(
            user_id=user_id,
            scope="global",
            kind=kind,
            rule_id=rule_id2,
            actions=actions2,
        )
