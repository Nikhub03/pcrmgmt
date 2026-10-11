"""Обработчики команд."""
import json
import time
import sys
import os
from datetime import datetime

from ..core.logger import log_info, log_error, log_warning
from ..core.errors import InvalidArgument, DeviceNotFound
from ..devices.cpu import CPU
from ..devices.ram import RAM
from ..devices.disk import Disk
from ..devices.gpu import GPU
from ..devices.fan import Fan
from ..devices.printer import Printer


_cpu = CPU()
_ram = RAM()
_disk = Disk()
_gpu = GPU()
_fan = Fan()
_printer = Printer()


def cmd_help(_args, parser):
    parser.print_help()
    print("\nКоманды: help, exit, status, info, monitor, report, serve")


def cmd_exit(_args, _parser):
    log_info("CLI", "Application terminated by user")
    sys.exit(0)


def _collect_status() -> dict:
    return {**_cpu.get_status(), **_ram.get_status(), **_disk.get_status()}


def cmd_status(_args, _parser):
    st = _collect_status()
    print("Состояние системы:")
    print(f"  CPU загрузка : {st['cpu_load']} %")
    print(f"  CPU темп.    : {st['cpu_temp']} °C (simulated)")
    print(f"  RAM          : {st['ram_percent']} % ({st['ram_used_gb']} GB)")
    print(f"  Диск (max)   : {st['disk_max_percent']} %")


def cmd_info(args, _parser):
    data = {
        "cpu": _cpu.get_metrics(),
        "ram": _ram.get_metrics(),
        "disks": _disk.get_metrics()["disks"],
        "gpu": _gpu.get_metrics(),
        "fans": _fan.get_metrics()["fans"],
        "printers": _printer.get_metrics()["printers"],
    }
    if args.output == "json":
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(f"CPU: {data['cpu']['model']} — {data['cpu']['load_percent']}% "
              f"@ {data['cpu']['frequency_ghz']} GHz, {data['cpu']['temperature_c']} °C (sim)")
        print(f"RAM: {data['ram']['used_gb']} / {data['ram']['total_gb']} GB "
              f"({data['ram']['percent']} %)")
        for d in data["disks"]:
            print(f"Disk {d['device']} [{d['mountpoint']}]: "
                  f"{d['used_gb']} / {d['total_gb']} GB ({d['percent']} %)")
        print(f"GPU: {data['gpu']['model']} — {data['gpu']['load_percent']} % "
              f"({data['gpu']['temperature_c']} °C, simulated)")
        print(f"Fans: " + ", ".join(f"#{f['id']}={f['rpm']} RPM" for f in data["fans"]))


def cmd_monitor(args, _parser):
    if args.interval < 0.5:
        raise InvalidArgument(
            f"Invalid value for --interval: must be >= 0.5, got {args.interval}")
    log_info("CLI", f"monitor started, interval={args.interval}")
    print("Мониторинг. Ctrl+C — выход.")
    try:
        while True:
            c = _cpu.get_metrics()
            r = _ram.get_metrics()
            d = _disk.get_metrics()["disks"]
            g = _gpu.get_metrics()
            line = (f"CPU {c['load_percent']:5.1f}% | "
                    f"RAM {r['percent']:5.1f}% | "
                    f"CPU_T {c['temperature_c']:>3}°C | "
                    f"GPU {g['load_percent']:>3}% | "
                    f"Disk {max((x['percent'] for x in d), default=0):5.1f}%")
            sys.stdout.write("\r" + line)
            sys.stdout.flush()
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print()
        log_info("CLI", "Application terminated by user")
        return


def cmd_report(args, _parser):
    from ..features.report import generate_report
    if args.report_cmd == "generate":
        path = generate_report(args.output, args.export_data)
        print(f"Отчёт сохранён: {path}")


def cmd_serve(args, _parser):
    from ..features.web import run_web
    run_web(port=args.port)