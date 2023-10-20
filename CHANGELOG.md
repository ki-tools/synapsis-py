# Change Log

## Version 0.0.7 (2023-10-19)

### Changes

- Added `id_only` arg to `Synapsis.Utils.get_project()`
- Added `Synapsis.Utils.find_acl_resource_access()`
- Added `Synapsis.Utils.get_team_permission()`
- Refactored `Synapsis.Utils` get and set permissions methods.

## Version 0.0.6 (2023-10-11)

### Changes

- `Synapsis.Utils.set_entity_permission()` now accepts keyword args to pass to `Synapsis.Synapse.setPermissions()`
- Added `multi_threaded` arg to `synapse_args`.

## Version 0.0.5 (2023-10-04)

### Changes

- Synapsis.Utils.copy_file_handles_batch(...) now checks for errors and raises them.
- Ensure the `synapseclient.core.cache.CACHE_ROOT_DIR` is writable to the user, otherwise use a temp directory. This can
  happen when running on AWS Lambda.

### Changes

## Version 0.0.4 (2023-10-03)

### Changes

- Auth token will take precedence over user/pass when logging into Synapse.
- Added Synapsis.Utils.get_entity_permission(...).
- Replaced SynapsePermission.find_by(...) with SynapsePermission.get(...).
- Refactored `utils`.

## Version 0.0.3 (2023-09-25)

### Changes

- Synapsis.ConcreteTypes now handles EntityBundle.
- Synapsis.ConcreteTypes.get() will always return Synapsis.ConcreteTypes.UNKNOWN if the ConcreteType cannot be found.

## Version 0.0.2 (2023-09-22)

### Changes

- Added "after login" hook.
- Refactored properties and type hints.

## Version 0.0.1 (2023-09-21)

### Changes

- Initial release.
