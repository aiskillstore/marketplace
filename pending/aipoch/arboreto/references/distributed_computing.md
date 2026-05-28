# Distributed Computing with Dask

Arboreto leverages Dask for parallel computation.

## Local Mode
By default, Arboreto runs on a local Dask client, utilizing all available cores on the machine. No extra configuration is needed.

## Cluster Mode
To run on a cluster:
1. Setup a Dask Scheduler and Workers.
2. Connect the Dask Client in your script before running inference.

```python
from dask.distributed import Client
client = Client('scheduler-address:8786')
# Arboreto will automatically use this client
```
