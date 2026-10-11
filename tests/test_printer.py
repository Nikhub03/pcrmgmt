import pytest
from src.devices.printer import Printer
from src.core.errors import InvalidArgument, DeviceNotFound


def test_list_printers():
    p = Printer()
    printers = p.list_printers()
    assert isinstance(printers, list)
    assert len(printers) >= 1


def test_print_text(tmp_path):
    p = Printer()
    r = p.print_text("hello world")
    assert r["status"] == "PRINTED"


def test_print_missing_file():
    p = Printer()
    with pytest.raises(DeviceNotFound):
        p.print_file("does_not_exist.txt")


def test_print_bad_encoding(tmp_path):
    path = tmp_path / "bad.bin"
    path.write_bytes(b"\xff\xfe\x00\x01")
    p = Printer()
    with pytest.raises(InvalidArgument):
        p.print_file(str(path))
