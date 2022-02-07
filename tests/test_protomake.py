from pathlib import Path

from click.testing import CliRunner
import pytest
from pytest import TempdirFactory

from protomake import protomake


@pytest.fixture
def temp(tmpdir_factory: TempdirFactory) -> Path:
    """Return path to temporary test directory."""
    data_dir = Path(__file__).parent / "data"
    good = data_dir / "good.proto"
    bad = data_dir / "bad.proto"
    tmpdir = tmpdir_factory.mktemp("mydir")
    tmpgood = tmpdir.join("good.proto")
    tmpbad = tmpdir.join("bad.proto")
    tmprandom = tmpdir.join("random.txt")
    tmpclean = tmpdir.join("good_pb2.py")
    tmpgood.write(good.read_text())
    tmpbad.write(bad.read_text())
    tmprandom.write("")
    tmpclean.write("THIS SHOULD NOT EXIST")
    return Path(tmpdir)


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


def test_good(runner: CliRunner, temp: Path) -> None:
    """It generates .py and .pyi files from .proto file."""
    source = str(temp / "good.proto")
    target = str(temp)
    result = runner.invoke(protomake.generate, args=(source, target))
    assert result.exit_code == 0
    assert {"good_pb2.py", "good_pb2.pyi", "good_pb2_grpc.py"}.issubset(set(f.name for f in temp.iterdir()))
    assert "THIS SHOULD NOT EXIST" not in (temp / "good_pb2.py").read_text()
    # check that imports are fixed
    assert (temp / "good_pb2_grpc.py").read_text().split("\n")[4] == "from .import good_pb2 as good__pb2"


def test_bad_proto(runner: CliRunner, temp: Path) -> None:
    """It errors out if .proto file is borken."""
    source = str(temp / "bad.proto")
    target = str(temp)
    result = runner.invoke(protomake.generate, args=(source, target))
    assert result.exit_code == 1
    assert result.output.strip() == 'bad.proto:5:5: "int" is not defined.'


def test_missing_proto(runner: CliRunner, temp: Path) -> None:
    """It errors out if file is missing."""
    source = str(temp / "missing.proto")
    target = str(temp)
    result = runner.invoke(protomake.generate, args=(source, target))
    assert result.exit_code == 1
    assert "missing.proto does not exist" in result.output


def test_not_a_file(runner: CliRunner, temp: Path) -> None:
    """It errors out if source is not a file."""
    source = str(temp)
    target = str(temp)
    result = runner.invoke(protomake.generate, args=(source, target))
    assert result.exit_code == 1
    assert "is not a file" in result.output


def test_not_a_proto(runner: CliRunner, temp: Path) -> None:
    """It errors out if source is not a .proto file."""
    source = str(temp / "random.txt")
    target = str(temp)
    result = runner.invoke(protomake.generate, args=(source, target))
    assert result.exit_code == 1
    assert "random.txt is not a .proto file" in result.output


def test_target_not_a_dir(runner: CliRunner, temp: Path) -> None:
    """It errors out if output location is not a directory."""
    source = str(temp / "good.proto")
    target = str(temp / "random.txt")
    result = runner.invoke(protomake.generate, args=(source, target))
    assert result.exit_code == 1
    assert "random.txt is not a directory" in result.output
