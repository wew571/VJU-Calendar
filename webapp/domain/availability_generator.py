# -*- coding: utf-8 -*-
"""Tu dong sinh gio ranh (availability) cua 1 giang vien theo cac khung
buoi/sang/chieu/toi cau hinh san trong CONFIG["availabilityGenerator"] - xem
PROMPT-THEM-CHUC-NANG-GIO-RANH-GIANG-VIEN.md.

Xu ly DOC LAP TUNG NGAY trong pham vi ngay hop le cua loai GV (sc.max_day_index).
Voi moi ngay: dem so KHUNG (khong phai so tiet/so mon) da co gio day, roi random
tuan tu tung khung moi theo xac suat generationChanceByBlockStage cho toi khi
phep thu that bai, het khung ung vien, hoac dat maxGeneratedBlocksPerDay.

Khong dung seed co dinh trong runtime (goi generate_teacher_availability() KHONG
truyen rng se tu tao random.Random() moi lan) - test co the tu inject 1
random.Random(seed) hoac mot doi tuong gia co .uniform()/.randint() de ra ket
qua xac dinh.
"""

import random

import scheduler_core as sc
from app_config import CONFIG
from domain.teachers import teaching_slots_of


def _block_slots(day, block, slots_per_day):
    """Danh sach slot (0-indexed ca ngay lan tiet) cua 1 khung trong 1 ngay.
    startPeriod/endPeriod trong cau hinh la TIET 1-indexed (dung quy uoc
    campuses.sessionBlocks), slot = day * slotsPerDay + (tiet - 1)."""
    return [
        day * slots_per_day + (period - 1)
        for period in range(block["startPeriod"], block["endPeriod"] + 1)
    ]


def _stage_chance(chances, stage):
    key = str(stage) if stage < 3 else "3OrMore"
    return chances[key]


def _weighted_pick(candidates, group_weights, rng):
    """candidates: list (name, block, free_slots) CON hop le (con tiet trong).
    Trong so moi khung = trong so nhom / so khung CUNG nhom dang hop le - dung
    hanh vi "chia deu" mo ta o muc 5.2/6.1 (vd sang+chieu deu con trong thi moi
    ben 45%, chi con 1 ben thi ben do nhan het 90%)."""
    group_counts = {}
    for _, block, _free in candidates:
        group_counts[block["selectionGroup"]] = group_counts.get(block["selectionGroup"], 0) + 1

    weighted = []
    total = 0
    for name, block, free in candidates:
        group = block["selectionGroup"]
        w = group_weights.get(group, 0) / group_counts[group]
        weighted.append((name, block, free, w))
        total += w
    if total <= 0:
        return None

    r = rng.uniform(0, total)
    upto = 0
    for name, block, free, w in weighted:
        upto += w
        if r <= upto:
            return name, block, free
    name, block, free, _w = weighted[-1]
    return name, block, free


def _generate_day(day, teaching_slots, config, rng):
    """Sinh danh sach slot ranh moi cho 1 ngay - doc lap voi cac ngay khac."""
    ag = config["availabilityGenerator"]
    blocks = ag["sessionBlocks"]
    group_weights = ag["selectionGroupWeights"]
    chances = ag["generationChanceByBlockStage"]
    max_blocks = ag["maxGeneratedBlocksPerDay"]
    slots_per_day = config["calendar"]["slotsPerDay"]

    block_slots = {name: _block_slots(day, block, slots_per_day) for name, block in blocks.items()}
    teaching_block_count = sum(
        1 for slots in block_slots.values() if any(s in teaching_slots for s in slots)
    )

    result = []
    chosen_names = set()
    generated_count = 0

    while generated_count < max_blocks:
        stage = teaching_block_count + generated_count
        chance = _stage_chance(chances, stage)
        # randint(1, 100) <= chance co xac suat dung bang chance/100; chance=0
        # khong bao gio thanh cong, chance=100 luon thanh cong.
        if rng.randint(1, 100) > chance:
            break  # phep thu that bai - dung xu ly ngay nay

        candidates = []
        for name, block in blocks.items():
            if name in chosen_names:
                continue
            free = [s for s in block_slots[name] if s not in teaching_slots]
            if not free:
                continue
            candidates.append((name, block, free))
        if not candidates:
            break  # het khung ung vien

        picked = _weighted_pick(candidates, group_weights, rng)
        if picked is None:
            break
        name, _block, free = picked
        result.extend(free)
        chosen_names.add(name)
        generated_count += 1

    return result


def generate_teacher_availability(data, teacher_id, rng=None, config=None):
    """Sinh TOAN BO gio ranh moi cho 1 GV, xu ly doc lap tung ngay hop le theo
    loai GV (thinh giang toi Thu 7, co huu toi Thu 6, khong ai Chu nhat - xem
    sc.max_day_index). Gio dang day (teaching_slots_of) luon bi loai khoi ket
    qua va KHONG duoc dung de dem trang thai ngay/tinh xac suat tu gio ranh cu -
    ham nay khong doc `manual_teacher_windows` hien co.

    Tra ve danh sach slot da sap xep, khong trung lap. Khong ghi gi vao `data` -
    goi ham nay an toan de thu truoc, ben goi (api/manual_teacher.py) moi la noi
    quyet dinh ghi de manual_teacher_windows."""
    if rng is None:
        rng = random.Random()
    if config is None:
        config = CONFIG

    teacher = data["teachers"][teacher_id]
    teacher_type = teacher["type"]
    params = data["params"]
    num_days = min(params["numDays"], sc.max_day_index(teacher_type) + 1)

    teaching = teaching_slots_of(data, teacher_id)

    result = set()
    for day in range(num_days):
        result.update(_generate_day(day, teaching, config, rng))
    return sorted(result)
