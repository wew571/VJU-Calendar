import json
import os


CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")


def _int_value(value, name, minimum=0):
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{name} phải là số nguyên >= {minimum}.")
    return value


def _tao_config_trong():
    try:
        with open(CONFIG_PATH, "x", encoding="utf-8"):
            pass
    except FileExistsError:
        pass
    except OSError as exc:
        raise RuntimeError(f"Không thể tạo file cấu hình: {CONFIG_PATH}: {exc}") from exc
    raise RuntimeError(
        f"Đã tạo file cấu hình trống tại {CONFIG_PATH}. "
        "Hãy liên hệ người cung cấp hệ thống để nhận nội dung config.json trước khi chạy lại."
    )


def _load_config():
    try:
        with open(CONFIG_PATH, encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError:
        _tao_config_trong()
    except json.JSONDecodeError as exc:
        if os.path.getsize(CONFIG_PATH) == 0:
            raise RuntimeError(
                f"File cấu hình đang trống: {CONFIG_PATH}. "
                "Hãy liên hệ người cung cấp hệ thống để nhận nội dung config.json."
            ) from exc
        raise RuntimeError(f"File cấu hình JSON không hợp lệ: {CONFIG_PATH}: {exc}") from exc

    try:
        calendar = config["calendar"]
        rooms = config["rooms"]
        day_limits = config["teacherDayLimits"]
        campuses = config["campuses"]
        solver = config["solver"]
        legacy = config["legacyDataParams"]

        num_days = _int_value(calendar["numDays"], "calendar.numDays", 1)
        slots_per_day = _int_value(calendar["slotsPerDay"], "calendar.slotsPerDay", 1)
        _int_value(calendar["defaultDuration"], "calendar.defaultDuration", 1)
        max_imported_period = _int_value(calendar["maxImportedPeriod"], "calendar.maxImportedPeriod", slots_per_day)
        day_labels = calendar["dayLabels"]
        slot_day_names = calendar["slotDayNames"]
        if not isinstance(day_labels, list) or len(day_labels) < num_days or not all(isinstance(x, str) and x for x in day_labels):
            raise ValueError("calendar.dayLabels phải chứa đủ nhãn ngày.")
        if not isinstance(slot_day_names, list) or len(slot_day_names) < num_days or not all(isinstance(x, str) and x for x in slot_day_names):
            raise ValueError("calendar.slotDayNames phải chứa đủ nhãn ngày.")

        _int_value(rooms["ltPool"], "rooms.ltPool")
        _int_value(rooms["labPool"], "rooms.labPool")
        for teacher_type in ("GUEST", "RESIDENT"):
            limit = _int_value(day_limits[teacher_type], f"teacherDayLimits.{teacher_type}")
            if limit >= num_days:
                raise ValueError(f"teacherDayLimits.{teacher_type} phải nhỏ hơn calendar.numDays.")

        priority = campuses["priority"]
        blocks = campuses["sessionBlocks"]
        if not isinstance(priority, list) or not all(isinstance(x, str) and x for x in priority):
            raise ValueError("campuses.priority phải là danh sách tên cơ sở.")
        if not isinstance(blocks, dict):
            raise ValueError("campuses.sessionBlocks phải là object.")
        for campus, campus_blocks in blocks.items():
            if not isinstance(campus, str) or not isinstance(campus_blocks, list):
                raise ValueError("campuses.sessionBlocks không hợp lệ.")
            for block in campus_blocks:
                if not isinstance(block, list) or len(block) != 2:
                    raise ValueError(f"Khối ca của {campus} phải có dạng [tiết đầu, tiết cuối].")
                start = _int_value(block[0], f"campuses.sessionBlocks.{campus}", 1)
                end = _int_value(block[1], f"campuses.sessionBlocks.{campus}", start)
                if end > slots_per_day:
                    raise ValueError(f"Khối ca của {campus} vượt calendar.slotsPerDay.")

        _int_value(solver["timeLimitSeconds"], "solver.timeLimitSeconds", 1)
        _int_value(solver["numSearchWorkers"], "solver.numSearchWorkers", 1)
        _int_value(solver["crossProgramCombinationLimit"], "solver.crossProgramCombinationLimit", 1)
        _int_value(legacy["seed"], "legacyDataParams.seed")
        _int_value(legacy["pctPreSubmitted"], "legacyDataParams.pctPreSubmitted")
        _int_value(legacy["numForcedConflicts"], "legacyDataParams.numForcedConflicts")
        calendar["maxImportedPeriod"] = max_imported_period
    except (KeyError, TypeError) as exc:
        raise RuntimeError(f"Thiếu hoặc sai cấu trúc cấu hình tại {CONFIG_PATH}: {exc}") from exc
    except ValueError as exc:
        raise RuntimeError(f"Cấu hình không hợp lệ tại {CONFIG_PATH}: {exc}") from exc
    return config


CONFIG = _load_config()


def default_data_params():
    calendar = CONFIG["calendar"]
    rooms = CONFIG["rooms"]
    return {
        "numDays": calendar["numDays"],
        "slotsPerDay": calendar["slotsPerDay"],
        "duration": calendar["defaultDuration"],
        "ltPool": rooms["ltPool"],
        "labPool": rooms["labPool"],
        **CONFIG["legacyDataParams"],
    }
