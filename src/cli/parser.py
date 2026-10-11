"""Парсер командной строки с подкомандами."""
import argparse


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="pcrmgmt",
        description="Кроссплатформенная утилита мониторинга периферии.",
    )
    p.add_argument("--config", help="путь к config.yaml / config.json")
    p.add_argument("--verbose", action="store_true", help="DEBUG-вывод в консоль")
    p.add_argument("--version", action="version", version="pcrmgmt 1.0.0")

    sub = p.add_subparsers(dest="command", required=True)

    # help / exit — не нуждаются в аргументах
    sub.add_parser("help", help="показать справку")
    sub.add_parser("exit", help="выход")

    sub.add_parser("status", help="краткое состояние системы")

    info = sub.add_parser("info", help="подробная информация")
    info.add_argument("--output", choices=["text", "json"], default="text")

    mon = sub.add_parser("monitor", help="мониторинг в реальном времени")
    mon.add_argument("--interval", type=float, default=2.0)
    mon.add_argument("--force", action="store_true")

    # Расширенный функционал
    rep = sub.add_parser("report", help="генерация отчёта")
    rep_sub = rep.add_subparsers(dest="report_cmd", required=True)
    gen = rep_sub.add_parser("generate")
    gen.add_argument("--output", default="report.html")
    gen.add_argument("--export-data", default=None)

    web = sub.add_parser("serve", help="веб-интерфейс")
    web.add_argument("--port", type=int, default=8080)
    web.add_argument("--force", action="store_true")

    return p