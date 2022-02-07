import os
from pathlib import Path
import re
import subprocess
import sys

import click

COMMAND = "{exe} -m grpc_tools.protoc -I {source_dir} --plugin=protoc-gen-mypy={protoc_mypy} --python_out={target} --grpc_python_out={target} --mypy_out={target} {source_file}"


@click.command()
@click.argument("source")
@click.argument("target")
def generate(source: str, target: str) -> None:
    """Generate Python files from Protobuf schema.

    Args:
        source: path to .proto file.
        target: path to target directory.
    """
    source_path = (Path(os.getcwd()) / source).resolve()
    target_path = (Path(os.getcwd()) / target).resolve()

    # check that source exists
    if not source_path.exists():
        click.secho(f"{source} does not exist", fg="red")
        sys.exit(1)

    # check that source is a file
    if not source_path.is_file():
        click.secho(f"{source} is not a file", fg="red")
        sys.exit(1)

    # check that source is a .proto file
    if not source_path.suffix == ".proto":
        click.secho(f"{source} is not a .proto file", fg="red")
        sys.exit(1)

    # check that target is a directory
    if not target_path.is_dir():
        click.secho(f"{target} is not a directory")
        sys.exit(1)

    # clean existing files
    for f in target_path.iterdir():
        if source_path.stem in f.stem and f.suffix in [".py", ".pyi"]:
            f.unlink()

    # generate
    command = COMMAND.format(
        exe=sys.executable,
        source_dir=str(source_path.parent),
        protoc_mypy=str(Path(sys.executable).parent / "protoc-gen-mypy"),
        target=str(target_path),
        source_file=str(source_path),
    )
    result = subprocess.run(command.split(" "), capture_output=True)

    # check status code
    if result.returncode != 0:
        click.secho(result.stderr.decode("utf-8"), fg="red")
        sys.exit(1)

    # fix imports
    for f in target_path.iterdir():
        if source_path.stem in f.stem and f.suffix in [".py", ".pyi"]:
            fix_imports(f)
            click.secho(f"generated {f}", fg="green")

    sys.exit(0)


def fix_imports(f: Path) -> None:
    """Fix the import structure so the files can be dumped in a spearate sub-package.

    Args:
        f: File to fix imports for.
    """
    new_content = []
    for line in f.read_text().split("\n"):
        if re.match(r"^import .*pb2.*", line) and "google" not in line:
            line = re.sub(r"^(import .*pb2*.)", r"from .\1", line)
        new_content.append(line)
    f.write_text("\n".join(new_content))
