# -*- coding: utf-8 -*-
"""CHOT LICH THEO LOP HOC PHAN: khoa gio cua tung lop va mo ra khi can.

Chot lich la mot CAM KET voi giang vien. Moi lop hoc phan duoc chot doc lap, cac
lop con lai van de he thong xep tiep ma khong lam xe dich lop da chot.
"""

import datetime

from domain.hoc_chung import thanh_vien
from domain.time_rules import apply_section_time
from state import KHONG_TRUYEN, STATE


def slot_dang_hien(data, sid):
    """Slot cua mot lop DANG HIEN tren luoi Thoi khoa bieu, theo dung thu tu uu
    tien ma man do dung: ghim tay > ket qua GD2 > ket qua GD1 > gio da ghi san o
    lop. None = lop nay chua o dau ca."""
    ov = STATE["overrides"].get(sid)
    if ov and ov.get("slot") is not None:
        return ov["slot"]
    for res in (STATE.get("residentResult"), STATE.get("guestResult")):
        for l in (res or {}).get("lessons") or []:
            if l["id"] == sid:
                return l["slot"]
    if not (data["sections"][sid].get("time_assumed")):
        return data["sections"][sid].get("original_slot")
    return None


def lop_cua_hoc_phan(data, course_id):
    return [s for s in data["sections"].values() if s.get("course_id") == course_id]


def gio_doi(s, time_info):
    """Yeu cau nay co lam DOI gio cua lop khong? time_info=None nghia la "de he
    thong tu xep" - voi lop dang co gio chot thi do CUNG la mot thay doi."""
    if time_info is None:
        return not s.get("time_assumed")
    return (bool(s.get("time_assumed"))
            or s.get("day") != time_info["day"]
            or s.get("period_start") != time_info["period_start"]
            or s.get("period_end") != time_info["period_end"])


def _nhan_lop(data, s):
    hp = data.get("courses", {}).get(s.get("course_id")) or {}
    return s.get("class_code") or hp.get("name") or f'#{s.get("id")}'


def khoa_vi_da_chot(data, section_id, time_info=KHONG_TRUYEN):
    """Loi (str) neu thao tac nay dung vao GIO cua mot lop DA CHOT - hoac None.

    Chot lich la mot cam ket voi giang vien; sua gio le tren bang sau do lam ban
    chinh thuc va ban da bao cho GV lech nhau ma khong ai thay. Muon doi gio thi
    phai BO CHOT truoc - mot thao tac co y thuc, co ghi lai.

    KHOA DUNG PHAN GIO, khong khoa ca ban ghi: sau khi nhap file van con phai sua
    ma lop sai, ten GV thieu, email, dia diem... Truyen `time_info` (dang ma
    sections.validate_section_body tra ve) de so: gio KHONG doi thi cho qua.
    """
    s = data["sections"].get(section_id)
    if s is None:
        return None
    if time_info is not KHONG_TRUYEN and not gio_doi(s, time_info):
        return None

    chot = s.get("chot")
    if chot:
        return (f"Lớp học phần “{_nhan_lop(data, s)}” đã chốt lịch "
                f"({chot.get('by')}, {(chot.get('at') or '')[:16].replace('T', ' ')}). "
                f"Bỏ chốt lớp học phần trước khi sửa giờ.")

    # HOC CHUNG: khoa lan theo NHOM. Lop nay chua chot, nhung sua gio no cung lam
    # doi gio cua thanh vien da chot vi solver ep ca nhom cung slot.
    for sid_khac in thanh_vien(data, section_id):
        if sid_khac == section_id:
            continue
        s2 = data["sections"].get(sid_khac) or {}
        chot2 = s2.get("chot")
        if chot2:
            return (f"Lớp này học chung buổi với “{_nhan_lop(data, s2)}” đã chốt lịch "
                    f"({chot2.get('by')}, {(chot2.get('at') or '')[:16].replace('T', ' ')}). "
                    f"Bỏ chốt lớp đó, hoặc tách nhóm học chung, trước khi sửa giờ.")
    return None


def chot_lop_hoc_phan(data, section_id, nguoi, ghi_chu):
    """Chot lich mot lop: lay gio dang hien, ghi thanh gio chinh thuc va ghim lai.

    Ghim qua STATE['overrides'] chu khong chi ghi gio vao lop: overrides la co che
    manh nhat o CA HAI pha (xem domain/pinning.py) nen giai lai bao nhieu lan lop
    nay cung dung yen. `truoc` luu trang thai gio de bo chot tra lai dung nhu cu.
    """
    s = data["sections"].get(section_id)
    if s is None:
        return "Không tìm thấy lớp học phần."
    if s.get("chot"):
        return "Lớp học phần này đã được chốt."

    slot = slot_dang_hien(data, section_id)
    if slot is None:
        return "Chưa chốt được: lớp học phần này chưa có giờ. Hãy xếp hoặc nhập giờ trước."

    truoc = {
        "day": s.get("day"), "periodStart": s.get("period_start"),
        "periodEnd": s.get("period_end"), "timeAssumed": bool(s.get("time_assumed")),
    }
    day, period0 = divmod(slot, data["params"]["slotsPerDay"])
    teacher = data["teachers"][s["teacher_id"]]
    apply_section_time(data, section_id, teacher, s["duration"], {
        "day": day, "period_start": period0 + 1,
        "period_end": period0 + s["duration"],
    })
    STATE["overrides"][section_id] = {
        "slot": slot, "reason": "Đã chốt lịch lớp học phần", "problem": None,
    }
    STATE["bo_ghim"].discard(section_id)
    s["chot"] = {
        "at": datetime.datetime.now().isoformat(timespec="seconds"),
        "by": (nguoi or "").strip() or "Giáo vụ",
        "note": (ghi_chu or "").strip(),
        "truoc": truoc,
    }
    return None


def bo_chot_lop_hoc_phan(data, section_id):
    """Mo lai mot lop da chot, go ghim va tra gio ve trang thai truoc khi chot."""
    s = data["sections"][section_id]
    chot = s.get("chot") or {}
    cu = chot.get("truoc")
    STATE["overrides"].pop(section_id, None)
    teacher = data["teachers"][s["teacher_id"]]
    if cu is None or cu.get("timeAssumed") or cu.get("day") is None:
        apply_section_time(data, section_id, teacher, s["duration"], None)
        STATE["bo_ghim"].add(section_id)
    else:
        apply_section_time(data, section_id, teacher, s["duration"], {
            "day": cu["day"], "period_start": cu["periodStart"],
            "period_end": cu["periodEnd"],
        })
        STATE["bo_ghim"].discard(section_id)
    s.pop("chot", None)


def chuyen_chot_hoc_phan_cu(data):
    """Chuyen snapshot cu co course.chot thanh section.chot ma khong mat lich su."""
    for course_id, course in data.get("courses", {}).items():
        chot_cu = course.get("chot")
        if not chot_cu:
            continue
        truoc = chot_cu.get("truoc") or {}
        metadata = {k: v for k, v in chot_cu.items() if k not in ("truoc", "soLop")}
        for s in lop_cua_hoc_phan(data, course_id):
            if s.get("chot"):
                continue
            s["chot"] = {**metadata, "truoc": truoc.get(str(s["id"]))}
        course.pop("chot", None)
