# Отчёт по комплексному аттестационному заданию

## Разработка кроссплатформенного консольного приложения для мониторинга и базового управления периферийными устройствами

**Выполнил:** Козинец Н.С., группа 23-ИВТ-01  
**Проверил:** Зозуля С.В., преподаватель кафедры МиВТ  
**Дисциплина:** ЭВМ и периферийные устройства  
**Год:** 2026

---

## Цель работы

Формирование профессиональных компетенций в области системного программирования, проектирования кроссплатформенных приложений и взаимодействия с аппаратным обеспечением вычислительных систем. Разработка консольного приложения, осуществляющего мониторинг и базовое управление периферийными устройствами компьютера (CPU, RAM, накопители, устройства ввода-вывода), а также выполнение задач системного администрирования целевой операционной системы.

## Задачи работы

1. Анализ предметной области и проектирование архитектуры приложения.
2. Реализация базового функционала CLI и сбора информации об оборудовании.
3. Интеграция с периферийными устройствами (клавиатура, мышь, принтер).
4. Реализация расширенного функционала (не менее двух функций: генерация отчётов, веб-интерфейс).
5. Выполнение задач системного администрирования в целевой ОС (Windows).
6. Тестирование и отладка.
7. Документирование (README.md и настоящий отчёт).

## Оборудование и ПО

- ПК: Intel Core i7 (12 ядер, 16 потоков), 32 ГБ RAM, SSD 367 ГБ + HDD 537 ГБ
- ОС: Windows 11 Pro 22H2
- Python 3.11.9
- Библиотеки: `psutil`, `matplotlib`, `flask`, `PyYAML`, `pywin32`, `pytest`, `pytest-cov`
- Редактор: VS Code
- Терминал: Windows PowerShell

Установка окружения:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

---

## 1. Анализ аналогов

| Утилита | Функциональность | CLI-интерфейс | Производительность | Документация |
|---|---|---|---|---|
| htop | CPU, RAM, процессы | интерактивный TUI | высокая | полная |
| nvidia-smi | GPU NVIDIA | табличный, XML/JSON | высокая | полная |
| lm-sensors | датчики Linux | простой | высокая | средняя |
| psutil (библиотека) | CPU/RAM/диски/сеть | нет CLI | высокая | полная |
| WMIC / PowerShell | системная информация | cmdlet-стиль | средняя | полная |
| **pcrmgmt** (разрабатываемое) | CPU/RAM/диски/GPU + отчёты + web | argparse + JSON | высокая | README + отчёт |

**Вывод:** заимствуем у `htop` структуру вывода метрик, у `psutil` — кросс-платформенную абстракцию сбора данных, у `nvidia-smi` — режим машиночитаемого вывода. Реализуем собственный CLI с двумя расширениями: генерацией HTML-отчётов и веб-интерфейсом.

---

## 2. Архитектура приложения

Приложение построено по модульному принципу с чётким разделением ответственности:

- `src/cli/` — парсер команд и обработчики;
- `src/core/` — ядро: логирование, кэш, конфигурация, ошибки;
- `src/devices/` — драйверы устройств (CPU, RAM, Disk, GPU, Fan, Keyboard, Mouse, Printer);
- `src/features/` — расширения: генерация отчётов и веб-интерфейс;
- `tests/` — модульные тесты.

Абстрактный интерфейс `Device` (в `src/devices/base.py`) задаёт контракт `get_metrics()` / `get_status()`, которому следуют все устройства. Это реализует принцип инверсии зависимостей (SOLID-D): CLI не знает, работает ли он с реальным драйвером или с симулятором.

### JSON-схема команды `info --output json`

```json
{
  "cpu": {
    "model": "Intel64 Family 6 ...",
    "cores": 12,
    "threads": 16,
    "load_percent": 13.0,
    "frequency_ghz": 2.7,
    "temperature_c": 42,
    "temperature_simulated": true
  },
  "ram": {"total_gb": 31.7, "used_gb": 15.6, "percent": 49.3},
  "disks": [{"device": "C:\\", "fs": "NTFS", "total_gb": 367.8, "percent": 45.9}],
  "gpu": {"model": "Simulated GPU", "load_percent": 33, "temperature_c": 53},
  "fans": [{"id": 0, "rpm": 1200, "simulated": true}],
  "printers": ["Brother DCP-1610W series Printer"]
}
```

### Таблица совместимости методов с ОС

| Метод | Windows | Linux | Fallback |
|---|---|---|---|
| CPU load | psutil | psutil | симуляция |
| CPU temperature | — | /sys/class/hwmon | симуляция |
| RAM | psutil | psutil | — |
| Диски | psutil | psutil | — |
| GPU | — | nvidia-ml-py | симуляция |
| Клавиатура | msvcrt | termios | сообщение |
| Мышь | user32.GetCursorPos | /dev/input | сообщение |
| Принтер | win32print | lpstat | Simulated_Printer |

---

## 3. Реализация базового функционала

### 3.1 Команды CLI

| Команда | Назначение |
|---|---|
| `help` | Справка |
| `exit` | Выход |
| `status` | Краткое состояние системы |
| `info --output text\|json` | Подробная информация |
| `monitor --interval N [--force]` | Динамический мониторинг |
| `report generate --output FILE [--export-data FILE]` | HTML-отчёт |
| `serve --port N` | Веб-интерфейс |

![help](screenshots/01_help.png)  
*Рисунок 1 — Вывод команды help*

### 3.2 Команда status

![status](screenshots/02_status.png)  
*Рисунок 2 — Вывод команды status*

### 3.3 Команда info (текстовый и JSON режимы)

![info text](screenshots/03_info_text.png)  
*Рисунок 3 — Вывод команды info*

![info json 1](screenshots/04_info_json/04_info_json_1.png)  
![info json 2](screenshots/04_info_json/04_info_json_2.png)  
![info json 3](screenshots/04_info_json/04_info_json_3.png)  
![info json 4](screenshots/04_info_json/04_info_json_4.png)  
*Рисунок 4 — Вывод команды info --output json*

### 3.4 Команда monitor

![monitor](screenshots/05_monitor.png)  
*Рисунок 5 — Динамический мониторинг (monitor --interval 1)*

### 3.5 Обработка ошибок

![error](screenshots/06_error_interval.png)  
*Рисунок 6 — Корректная обработка некорректного аргумента --interval*

### 3.6 Логирование

Все действия пишутся в `app.log` в формате:

```
2026-10-11T17:24:31,044 INFO  CLI User issued command: monitor --interval 1
2026-10-11T17:24:31,045 WARNI DISK skip F:\: [WinError 21] Устройство не готово
```

![log](screenshots/11_log.png)  
*Рисунок 7 — Содержимое app.log*

---

## 4. Интеграция с периферийными устройствами

### 4.1 Клавиатура

Неблокирующий мониторинг через `msvcrt.kbhit()` (Windows). Тайм-аут 30 секунд, выход по Esc, вывод состояния модификаторов (Caps Lock, Num Lock).

### 4.2 Мышь

Координаты курсора через `user32.GetCursorPos`. При выходе за границы экрана выводится `Cursor out of bounds: X=..., Y=...`.

### 4.3 Принтер

- Список принтеров через `win32print.EnumPrinters`;
- проверка размера файла (макс. 10 МБ) и кодировки (UTF-8);
- логирование печати в `print_output.txt` с MD5-хешем для файлов >1 КБ.

---

## 5. Расширенный функционал (2 из 5)

### 5.1 Генерация HTML-отчёта (`report generate`)

Команда:

```powershell
python -m src.main report generate --output report.html --export-data report.json
```

Функциональность:

- сбор исторических метрик (60 точек за последний час);
- построение графиков matplotlib: CPU/RAM (линейный), температура CPU (линейный), использование дисков (столбчатый);
- встраивание PNG в HTML через Base64;
- экспорт сырых данных в JSON.

![report 1](screenshots/07_report/07_report_1.png)  
![report 2](screenshots/07_report/07_report_2.png)  
![report 3](screenshots/07_report/07_report_3.png)  
*Рисунок 8 — Сгенерированный HTML-отчёт*

![report json](screenshots/12_report_json.png)  
*Рисунок 9 — Экспортированные данные (report.json)*

### 5.2 Веб-интерфейс (`serve`)

Команда:

```powershell
python -m src.main serve --port 8080
```

Функциональность:

- Flask-сервер, доступ только с localhost;
- главная страница обновляется JavaScript каждые 2 секунды;
- API-эндпоинт `/api/metrics` возвращает JSON;
- корректное завершение по Ctrl+C.

![web](screenshots/08_web.png)  
*Рисунок 10 — Веб-интерфейс мониторинга*

---

## 6. SysAdmin-часть (Windows)

Все команды выполнены в PowerShell от имени администратора.

### 6.1 Создание пользователей и групп

```powershell
New-LocalUser -Name "admin_pcr" -Password (ConvertTo-SecureString "P@ssw0rd!" -AsPlainText -Force)
New-LocalUser -Name "guest_pcr" -Password (ConvertTo-SecureString "GuestPass123!" -AsPlainText -Force)
New-LocalGroup -Name "developers_pcr"
Add-LocalGroupMember -Group "developers_pcr" -Member "admin_pcr"
```

Результат:

```
Name               Enabled Description
----               ------- -----------
admin_pcr          True
guest_pcr          True

ObjectClass  Name                      PrincipalSource
-----------  ----                      ---------------
Пользователь DESKTOP-421CPLP\admin_pcr Local
```

![users](screenshots/13_users.png)  
*Рисунок 11 — Созданные пользователи и группа*

### 6.2 Права на директорию

```powershell
New-Item -ItemType Directory -Path C:\project -Force
icacls C:\project /grant "admin_pcr:(OI)(CI)F" "developers_pcr:(OI)(CI)M" "guest_pcr:(OI)(CI)R"
```

Результат:

```
C:\project DESKTOP-421CPLP\guest_pcr:(OI)(CI)(R)
           DESKTOP-421CPLP\developers_pcr:(OI)(CI)(M)
           DESKTOP-421CPLP\admin_pcr:(OI)(CI)(F)
           BUILTIN\Администраторы:(I)(OI)(CI)(F)
           NT AUTHORITY\СИСТЕМА:(I)(OI)(CI)(F)
           BUILTIN\Пользователи:(I)(OI)(CI)(RX)
```

![icacls](screenshots/14_icacls.png)  
*Рисунок 12 — Права доступа к C:\project*

### 6.3 Сеть

```powershell
Get-NetIPConfiguration
Test-Connection ya.ru -Count 4
```

Результат:

- Основной интерфейс: Беспроводная сеть (Intel Wi-Fi 6 AX201), IPv4 = 192.168.0.13, шлюз 192.168.0.1;
- DNS: 1.1.1.1, 1.0.0.1;
- Ping до ya.ru: 4 из 4 пакетов, время < 1 мс.

![network](screenshots/15_network.png)  
*Рисунок 13 — Настройки сети и проверка соединения*

### 6.4 Политика выполнения скриптов

```powershell
Get-ExecutionPolicy
# RemoteSigned
```

![exec policy](screenshots/16_execpolicy.png)  
*Рисунок 14 — Политика выполнения PowerShell*

### 6.5 Логирование административных действий

Все команды записаны в `admin_actions.log` с временной меткой (ISO 8601) и SHA-256 хешем:

```
[2026-10-11T18:08:33.8510023+03:00] SHA256: ECF24D9D... Command: New-LocalUser admin_pcr
[2026-10-11T18:08:33.8545297+03:00] SHA256: 26A3BDAA... Command: New-LocalUser guest_pcr
[2026-10-11T18:08:33.8570763+03:00] SHA256: 5C206638... Command: New-LocalGroup developers_pcr
[2026-10-11T18:08:33.8581070+03:00] SHA256: 6B95EBAC... Command: Add-LocalGroupMember developers_pcr admin_pcr
[2026-10-11T18:08:33.8591025+03:00] SHA256: 98640DCF... Command: New-Item C:\project
[2026-10-11T18:08:33.8601678+03:00] SHA256: 8080EE67... Command: icacls C:\project
[2026-10-11T18:08:33.8611281+03:00] SHA256: 221F0AD9... Command: Get-NetIPConfiguration
[2026-10-11T18:08:33.8621273+03:00] SHA256: CE6952A5... Command: Test-Connection ya.ru
[2026-10-11T18:08:33.8631281+03:00] SHA256: 11BBD766... Command: Get-ExecutionPolicy
```

---

## 7. Тестирование

### 7.1 Модульное тестирование

Запуск: `pytest --cov=src --cov-report=term-missing`

Результат: **32 passed in 3.89s**.

| Модуль | Покрыто | Всего | % |
|---|---|---|---|
| devices/cpu.py | 37 | 46 | 80 % |
| devices/ram.py | 15 | 15 | 100 % |
| devices/disk.py | 26 | 28 | 93 % |
| devices/fan.py | 25 | 26 | 96 % |
| devices/gpu.py | 15 | 15 | 100 % |
| devices/printer.py | 41 | 58 | 71 % |
| features/report.py | 55 | 55 | 100 % |
| features/web.py | 18 | 25 | 72 % |
| core/cache.py | 30 | 30 | 100 % |
| core/logger.py | 32 | 35 | 91 % |
| cli/parser.py | 24 | 24 | 100 % |
| **TOTAL** | **373** | **525** | **71 %** |

![tests](screenshots/09_tests.png)  
*Рисунок 15 — Результаты pytest*

![coverage](screenshots/10_coverage.png)  
*Рисунок 16 — HTML-отчёт покрытия*

**Требование задания:** покрытие ≥70 % для модулей CPU, RAM, дисков — **выполнено** (80 %, 100 %, 93 %).

### 7.2 Нагрузочный тест

Тест: `monitor --interval 1` в течение 30 секунд.

- Пиковое потребление памяти процессом: ~45 МБ;
- Среднее время отклика команды: 8 мс (норма ≤ 500 мс);
- Утечек памяти не обнаружено.

### 7.3 Стресс-тест

Тест: параллельный запуск 3 экземпляров `monitor --interval 0.5` в течение 60 секунд.

- Система стабильна;
- Ошибок синхронизации кэша: 0;
- CPU-нагрузка от утилиты: < 3 %.

### 7.4 Сценарии ошибок

| № | Сценарий | Команда | Ожидаемое поведение | Результат |
|---|---|---|---|---|
| 1 | Некорректный интервал | monitor --interval -1 | Invalid value for --interval | ✅ |
| 2 | Отсутствующее устройство | printer print --file missing.txt | Cannot read file <missing.txt> | ✅ |
| 3 | Неверная кодировка | printer print --file bad.bin | Invalid encoding: use UTF-8 | ✅ |
| 4 | Файл слишком большой | printer print --file big.bin | File too large (max 10 MB) | ✅ |
| 5 | Недоступный диск | автоматически при disk_partitions | skip F:\: Устройство не готово | ✅ |

---

## 8. Аналитические ответы

### 8.1 Монолитная vs микросервисная архитектура

Для CLI-утилиты предпочтителен монолитный подход: единая сборка, отсутствие сетевых вызовов, минимальные задержки. Микросервисы оправданы при наличии веб-интерфейса с высокой нагрузкой или при разделении сбора данных и визуализации между командами. В нашем проекте веб-сервер (`serve`) реализован как встроенный модуль монолита — этого достаточно.

### 8.2 Паттерн для парсера команд

Использован паттерн **Command**: каждая команда — отдельный обработчик (`cmd_help`, `cmd_status`, `cmd_monitor` и т. д.), а `dispatch()` выбирает нужный по имени. Это упрощает добавление новых команд без изменения существующего кода.

### 8.3 Повышенные привилегии

Реальные датчики температуры, S.M.A.R.T. и управления вентиляторами требуют прав администратора/root. Альтернативы: udev-правила (Linux), специальные группы (`input`, `video`), настройка sudo для конкретных команд. В нашем проекте основная реализация — симуляция, поэтому привилегии не требуются.

### 8.4 Обработка аномальных данных

Правило: значения вне допустимого диапазона (температура > 120 °C, отрицательный RPM) игнорируются, в лог пишется WARNING, пользователю отдаётся последнее валидное значение с пометкой `stale`. Команда продолжает работу.

### 8.5 CLI vs GUI

CLI предпочтителен для автоматизации (CI/CD, cron), интеграции в скрипты, работы по SSH. GUI удобен для визуализации трендов (например, графиков температуры за сутки). Наш проект совмещает: CLI для сбора и веб-страница для визуализации.

---

## Заключение

В ходе работы разработано кроссплатформенное консольное приложение `pcrmgmt` на Python 3.11, реализующее:

- сбор метрик CPU, RAM, дисков, GPU (с симуляцией датчиков, недоступных без специальных драйверов);
- мониторинг клавиатуры, мыши, принтера;
- TTL-кэширование и централизованное структурированное логирование;
- две расширенные функции: генерацию HTML-отчётов с графиками и веб-интерфейс с JSON API;
- обработку пяти типовых сценариев ошибок;
- модульные тесты с покрытием 71 % (для CPU/RAM/диск — 80/100/93 %, что превышает требование ≥70 %);
- документацию: `README.md` и настоящий отчёт.

Задачи системного администрирования выполнены в Windows: созданы пользователи `admin_pcr` и `guest_pcr`, группа `developers_pcr`, настроены права на `C:\project`, проверены сеть и политика выполнения скриптов. Все действия залогированы в `admin_actions.log` с хешами SHA-256.

**Цель работы достигнута.** Возможные направления развития: интеграция с OpenHardwareMonitor для получения реальных температур, добавление аутентификации в веб-интерфейс, поддержка Linux-специфичных датчиков через `lm-sensors`.

---

## Список использованных источников

1. Документация Python 3.11. — URL: https://docs.python.org/3/
2. psutil documentation. — URL: https://psutil.readthedocs.io/
3. Flask documentation. — URL: https://flask.palletsprojects.com/
4. matplotlib documentation. — URL: https://matplotlib.org/
5. Microsoft Docs: Local Accounts. — URL: https://learn.microsoft.com/
6. ГОСТ 19.701-90 (ЕСПД). Схемы алгоритмов, программ, данных и систем.

---

## Приложение А. Структура проекта

```
pcrmgmt/
├── src/
│   ├── main.py
│   ├── cli/         — парсер и команды
│   ├── core/        — логгер, кэш, конфиг, ошибки
│   ├── devices/     — драйверы устройств
│   └── features/    — отчёты и веб-интерфейс
├── tests/           — 12 файлов, 32 теста
├── docs/
│   ├── report.md
│   └── screenshots/
├── config.yaml
├── pyproject.toml
├── requirements.txt
├── README.md
├── app.log
├── admin_actions.log
├── print_output.txt
├── report.html
└── report.json
```

## Приложение Б. Пример конфигурации (config.yaml)

```yaml
thresholds:
  cpu_temp: 80
  ram_usage: 90
  disk_usage: 95

printer:
  name: "Brother DCP-1610W series Printer"
  timeout: 30

monitor:
  default_interval: 2.0
  min_interval: 0.5
```

## Приложение В. Фрагмент логирования

```python
# src/core/logger.py
LOG = _build_logger()

def log_info(component, msg):
    log("INFO", component, msg)

def log_warning(component, msg):
    log("WARNING", component, msg)
```

Формат записи в `app.log`:

```
ГГГГ-ММ-ДДTЧЧ:ММ:СС,ммм УРОВЕНЬ КОМПОНЕНТ Сообщение
2026-10-11T18:08:33,851 INFO  CLI User issued command: info --output json
```