import copy
import json
import os


CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")

# Fallback dung khi file cau hinh cu CHUA co khoa "availabilityGenerator" - xem
# PROMPT-THEM-CHUC-NANG-GIO-RANH-GIANG-VIEN.md muc 6.1/6.2. Neu khoa nay CO mat
# nhung sai/thieu thi KHONG duoc am tham dung bo mac dinh (xem
# _validate_availability_generator) - de tranh che giau loi go sai.
DEFAULT_AVAILABILITY_GENERATOR = {
    "sessionBlocks": {
        "morning": {"startPeriod": 2, "endPeriod": 5, "selectionGroup": "daytime"},
        "afternoon": {"startPeriod": 6, "endPeriod": 9, "selectionGroup": "daytime"},
        "evening": {"startPeriod": 10, "endPeriod": 12, "selectionGroup": "evening"},
    },
    "selectionGroupWeights": {"daytime": 90, "evening": 10},
    "generationChanceByBlockStage": {"0": 100, "1": 35, "2": 10, "3OrMore": 0},
    "maxGeneratedBlocksPerDay": 1,
    "replaceExistingAvailability": True,
}


def _int_value(value, name, minimum=0):
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{name} phải là số nguyên >= {minimum}.")
    return value


def _int_0_100(value, name):
    if isinstance(value, bool) or not isinstance(value, int) or not (0 <= value <= 100):
        raise ValueError(f"{name} phải là số nguyên trong khoảng 0-100.")
    return value


def _validate_availability_generator(avail_gen, slots_per_day):
    """Validate `availabilityGenerator` - xem
    PROMPT-THEM-CHUC-NANG-GIO-RANH-GIANG-VIEN.md muc 6.2. Khong am tham fallback
    tung phan: sai kieu/thieu truong/gia tri ngoai khoang deu phai dung khoi
    dong voi thong bao chi ro duong dan cau hinh loi."""
    p = "availabilityGenerator"
    if not isinstance(avail_gen, dict):
        raise ValueError(f"{p} phải là object.")

    blocks = avail_gen.get("sessionBlocks")
    if not isinstance(blocks, dict) or not blocks:
        raise ValueError(f"{p}.sessionBlocks phải là object không rỗng.")

    weights = avail_gen.get("selectionGroupWeights")
    if not isinstance(weights, dict) or not weights:
        raise ValueError(f"{p}.selectionGroupWeights phải là object không rỗng.")
    for group, w in weights.items():
        _int_0_100(w, f"{p}.selectionGroupWeights.{group}")
    if sum(weights.values()) != 100:
        raise ValueError(f"{p}.selectionGroupWeights phải có tổng bằng 100.")

    parsed_blocks = []
    for name, block in blocks.items():
        if not isinstance(block, dict):
            raise ValueError(f"{p}.sessionBlocks.{name} phải là object.")
        start = _int_value(block.get("startPeriod"), f"{p}.sessionBlocks.{name}.startPeriod", 1)
        end = _int_value(block.get("endPeriod"), f"{p}.sessionBlocks.{name}.endPeriod", start)
        if end > slots_per_day:
            raise ValueError(f"{p}.sessionBlocks.{name}.endPeriod vượt calendar.slotsPerDay.")
        group = block.get("selectionGroup")
        if not isinstance(group, str) or group not in weights:
            raise ValueError(
                f"{p}.sessionBlocks.{name}.selectionGroup phải là một khóa có trong "
                f"{p}.selectionGroupWeights.")
        parsed_blocks.append((name, start, end))

    for i, (name_a, start_a, end_a) in enumerate(parsed_blocks):
        for name_b, start_b, end_b in parsed_blocks[i + 1:]:
            if max(start_a, start_b) <= min(end_a, end_b):
                raise ValueError(
                    f"{p}.sessionBlocks: khung '{name_a}' và '{name_b}' chồng lấn tiết.")

    chances = avail_gen.get("generationChanceByBlockStage")
    if not isinstance(chances, dict) or set(chances.keys()) != {"0", "1", "2", "3OrMore"}:
        raise ValueError(f"{p}.generationChanceByBlockStage phải có đủ đúng các khóa 0, 1, 2, 3OrMore.")
    for stage, chance in chances.items():
        _int_0_100(chance, f"{p}.generationChanceByBlockStage.{stage}")

    max_blocks = avail_gen.get("maxGeneratedBlocksPerDay")
    _int_value(max_blocks, f"{p}.maxGeneratedBlocksPerDay", 1)
    if max_blocks > len(blocks):
        raise ValueError(f"{p}.maxGeneratedBlocksPerDay không được vượt số lượng sessionBlocks.")

    replace = avail_gen.get("replaceExistingAvailability")
    if not isinstance(replace, bool):
        raise ValueError(f"{p}.replaceExistingAvailability phải là boolean.")
    if replace is not True:
        raise ValueError(f"{p}.replaceExistingAvailability phải là true (false chưa được hỗ trợ).")


def _resolve_availability_generator(config, slots_per_day):
    """"availabilityGenerator" la nhom cau hinh MOI (xem
    PROMPT-THEM-CHUC-NANG-GIO-RANH-GIANG-VIEN.md) - file cau hinh cu chua co
    khoa nay thi dung nguyen bo mac dinh de tuong thich nguoc; CO khoa nhung
    sai/thieu thi dung khoi dong, khong am tham fallback (che giau go sai).
    Tach rieng ham nay (thay vi lam thang trong _load_config) de test duoc
    truc tiep ma khong can dung file config.json that."""
    avail_gen = config.get("availabilityGenerator")
    if avail_gen is None and "availabilityGenerator" not in config:
        avail_gen = copy.deepcopy(DEFAULT_AVAILABILITY_GENERATOR)
    _validate_availability_generator(avail_gen, slots_per_day)
    return avail_gen


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

        config["availabilityGenerator"] = _resolve_availability_generator(config, slots_per_day)
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
