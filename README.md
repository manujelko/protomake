# CLI for generating .py from .proto

```cmd
python -m protomake ./source/example.proto ./destination/
```

Best to add this as a --dev dependency if using poetry, or requirements_dev.txt if using pip.

It should also be possible to install it with pipx and use it as a project independent CLI.