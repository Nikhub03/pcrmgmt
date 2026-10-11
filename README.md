# pcrmgmt — кроссплатформенная утилита мониторинга периферии

**Цель:** консольное приложение для сбора данных о CPU, RAM, дисках, GPU,
управления вентиляторами, принтером, клавиатурой, мышью; генерация
HTML-отчётов и веб-интерфейс.

## Требования
- Python 3.10+
- Windows 10/11 (или Linux: Ubuntu 22.04 / CentOS Stream 9)
- Зависимости: см. `requirements.txt`

## Установка
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Запуск
```powershell
python -m src.main help
python -m src.main status
python -m src.main info --output json
python -m src.main monitor --interval 0.5
python -m src.main report generate --output report.html --export-data report.json
python -m src.main serve --port 8080
```

## Команды
| Команда | Назначение |
|---|---|
| `help` | Справка |
| `exit` | Выход |
| `status` | Краткое состояние |
| `info [--output text\|json]` | Подробная информация |
| `monitor [--interval N]` | Динамический мониторинг |
| `report generate --output FILE [--export-data FILE]` | HTML-отчёт с графиками |
| `serve [--port N]` | Веб-интерфейс |

## Обработка ошибок
- `InvalidArgument` → код возврата 2
- `DeviceNotFound` → код возврата 3
- `Ctrl+C` → корректное завершение с записью в `app.log`

## Логи
Все действия пишутся в `app.log` в формате ISO 8601 с миллисекундами:
```
2025-03-11T14:35:22,123 INFO  CLI User issued command: monitor --interval 0.5
```

## Тестирование
```powershell
pytest --cov=src --cov-report=html
```
Отчёт о покрытии: `htmlcov/index.html`.

## Ограничения
- Температура CPU/GPU, S.M.A.R.T. и вентиляторы — **симуляция** (помечаются `(simulated)`).
- Мониторинг клавиатуры/мыши работает только на Windows.
- Для реальных датчиков в Linux нужны права на `/sys/class/hwmon`.