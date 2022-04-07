# Push rules patcher

Synapse module to create specific push rules when a new user registers


## Installation

From the virtual environment that you use for Synapse, install this module with:
```shell
pip install path/to/synapse-patch-push-rules
```
(If you run into issues, you may need to upgrade `pip` first, e.g. by running
`pip install --upgrade pip`)

Then alter your homeserver configuration, adding to your `modules` configuration:
```yaml
modules:
  - module: synapse_patch_push_rules.PushRulesPatcher
    config:
      # Rules to set when new users register.
      # Required.
      rules:
        # The rule ID. Must be unique within rules of the same kind.
        my_rule:
          # See https://spec.matrix.org/latest/client-server-api/#push-rules for a
          # reference on the allowed values and format for 'kind', 'conditions' and
          # 'actions'.
          # 'kind', 'conditions' and 'actions' are all required.
          kind: "content"
          conditions:
            - kind: "event_match"
              key: "content.body"
              pattern: "testword"
          actions:
            - "notify"
```


## Development

In a virtual environment with pip ≥ 21.1, run
```shell
pip install -e .[dev]
```

To run the unit tests, you can either use:
```shell
tox -e py
```
or
```shell
trial tests
```

To run the linters and `mypy` type checker, use `./scripts-dev/lint.sh`.


## Releasing

The exact steps for releasing will vary; but this is an approach taken by the
Synapse developers (assuming a Unix-like shell):

 1. Set a shell variable to the version you are releasing (this just makes
    subsequent steps easier):
    ```shell
    version=X.Y.Z
    ```

 2. Update `setup.cfg` so that the `version` is correct.

 3. Stage the changed files and commit.
    ```shell
    git add -u
    git commit -m v$version -n
    ```

 4. Push your changes.
    ```shell
    git push
    ```

 5. When ready, create a signed tag for the release:
    ```shell
    git tag -s v$version
    ```
    Base the tag message on the changelog.

 6. Push the tag.
    ```shell
    git push origin tag v$version
    ```

 7. Create a source distribution and upload it to PyPI:
    ```shell
    python -m build
    twine upload dist/synapse_patch_push_rules-$version*
    ```
