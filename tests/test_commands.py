import json
import pytest
from src.cli.parser import build_parser
from src.cli import commands
from src.core.errors import InvalidArgument


def test_cmd_status(capsys):
    p = build_parser()
    args = p.parse_args(["status"])
    commands.cmd_status(args, p)
    out = capsys.readouterr().out
    assert "CPU" in out
    assert "RAM" in out


def test_cmd_info_text(capsys):
    p = build_parser()
    args = p.parse_args(["info"])
    commands.cmd_info(args, p)
    out = capsys.readouterr().out
    assert "CPU" in out


def test_cmd_info_json(capsys):
    p = build_parser()
    args = p.parse_args(["info", "--output", "json"])
    commands.cmd_info(args, p)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "cpu" in data


def test_cmd_monitor_bad_interval():
    p = build_parser()
    args = p.parse_args(["monitor", "--interval", "-1"])
    with pytest.raises(InvalidArgument):
        commands.cmd_monitor(args, p)
