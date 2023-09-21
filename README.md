# synapsis

[Synapse](https://www.synapse.org) integration utilities with asyncio support.

Provides helper methods for common Synapse operations and seamless asyncio integration for all methods.

## Installation

`pip install synapsis`

## Usage

### Configure authentication and the synapseclient:

```python
from synapsis import Synapsis

# No configuration is necessary if using environment variables or the default synapse config file.
# For user/pass, set:
#   SYNAPSE_USERNAME=
#   SYNAPSE_PASSWORD=
# For auth token, set:
#   SYNAPSE_AUTH_TOKEN=
# For Synapse Config file, have a valid config file in:
#   ~/.synapseConfig
# Or, have the environment variable set:
#   SYNAPSE_CONFIG_FILE=

# Configure for user/pass:
Synapsis.configure(email='', password='')

# Configure for auth token:
Synapsis.configure(auth_token='')

# Configure for non-default Synapse Config file:
Synapsis.configure(synapse_args={'configPath': '~/.synapseConfigAdmin'})

# Configure the Synapse client:
Synapsis.configure(synapse_args={'cache_root_dir': '/tmp/synapse', 'silent': False})
```

### Inject authentication params into argparse.

```python
import argparse
from synapsis import cli as synapsis_cli


def main():
    parser = argparse.ArgumentParser(...)
    synapsis_cli.inject(parser)

    args = parser.parse_args
    synapsis_cli.configure(args)
    # or with logging in.
    synapsis_cli.configure(args, login=True)
```

This will inject the following args.

```text
options:
  -u USERNAME, --username USERNAME
                        Synapse username.
  -p PASSWORD, --password PASSWORD
                        Synapse password.
  --auth-token AUTH_TOKEN
                        Synapse auth token.
  --synapse-config SYNAPSE_CONFIG
                        Path to Synapse configuration file.
```

### Login to Synapse

```python
from synapsis import Synapsis

Synapsis.login()
```

### Method Chaining and Piping

Synchronous: `Synapsis.Chain.<your-method-chain>.Result()`

Asynchronous: `await Synapsis.Chain.<your-method-chain>`

Examples:

```python
from synapsis import Synapsis

# Chaining
filehandle = Synapsis.Chain.get('syn123').get('_file_handle', None).Result()
# or
filehandle = await Synapsis.Chain.get('syn123').get('_file_handle', None)

# Piping
filehandle = Synapsis.Chain.get('syn123').Pipe.Utils.get_filehandle().Result()
# or
filehandle = await Synapsis.Chain.get('syn123').Pipe.Utils.get_filehandle()
```

### Calling a Synapsis, Synapsis.Utils, synapseclient, or synapseutils method

A method called directly on `Synapsis` will resolve in the following order.

1. `Synapsis`
2. `Synapsis.Synapse`

`Utils` and `SynapseUtils` need to be called directly.

- `Synapsis.Utils`
- `Synapsis.SynapseUtils`

NOTE: For `Synapsis.SynapseUtils` (`synapseutils`) you do not have to call the method with the `syn` arg, it will be set
to the current `Synapsis.Synapse` instance automatically.

#### Calling an Asynchronous Method

Start by calling `Synapsis.Chain` then the rest of the method chain.

```python
from synapsis import Synapsis


async def my_async_method():
    # Any resolvable method on `Synapsis` can be called asynchronously. 
    await Synapsis.Chain.configure(...)
    await Synapsis.Chain.login()

    entity = await Synapsis.Chain.Synapse.get(...)
    # or
    entity = await Synapsis.Chain.get(...)

    copy = await Synapsis.Chain.SynapseUtils.copy(...)
    entity = await Synapsis.Chain.Utils.find_entity(...)
```

#### Calling a Synchronous Method

Call the method directly on `Synapsis`.

```python
from synapsis import Synapsis


def my_sync_method():
    Synapsis.configure(...)
    Synapsis.login()

    entity = Synapsis.Synapse.get(...)
    # or
    entity = Synapsis.get(...)

    copy = Synapsis.SynapseUtils.copy(...)
    entity = Synapsis.Utils.find_entity(...)
```

## Development Setup

```bash
git clone https://github.com/ki-tools/synapsis-py.git
cd synapsis-py
pipenv --python 3.10
pipenv shell
make pip_install
```

Run tests:

1. Rename `.env.template` to `.env` and set the variables in the file.
2. Run `make test` or `tox`
