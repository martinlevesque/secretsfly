# Security

## Reading the loaded master keys

When the master keys are temporarily loaded in memory, it could be technically potentially possible
from an attacker to read them from an external process.

For instance, one could take a core dump of the process:

```
gcore <pid>
```

then read the core dump:

```
hexdump -Cv ./core.<pid> readcore
```

If one is able to read the master keys, please report a security issue to the project.
