# -*- coding: utf-8 -*-
"""DUNG va DONG BO LUOI THOI KHOA BIEU dang hien.

guest/residentResult la SNAPSHOT rieng, khong tu doc lai data['sections'] moi lan
render - nen sau moi thao tac sua du lieu phai dong bo lai, khong thi bang "Du
lieu hoc phan" va luoi noi hai chuyen khac nhau ve cung mot lop.

Tach khoi domain/pinning.py: ben do lo RANG BUOC dua vao solver (ghim/bo ghim),
o day lo cai NGUOI DUNG NHIN THAY. Hai viec khac nhau du deu doc STATE['overrides']
- truoc day o chung mot file 487 dong.
"""

import datetime

import scheduler_core as sc
from domain import bo_qua as bq
from domain.chot import chuyen_chot_hoc_phan_cu
from domain.hoc_chung import nhom_cua, thanh_vien
from domain.pinning import ghim_gio_da_chot
from state import STATE


def buoi_tren_luoi(data, s, slot):
    """Mot BUOI HOC de dat len luoi Thoi khoa bieu, dung khuon ma
    solve_guest_phase()/solve_resident_phase() tra ve - de frontend
    (adapters/lessonAdapter.js) doc duoc y nhu buoi do solver xep.

    Mot cho duy nhat dung khuon nay (lich ban dau tu file, va dong bo lai sau moi
    lan sua form) - truoc day lich ban dau tu ghep dict rieng nen thieu
    programIds/programParts/facultyName, khien bo loc theo CTDT/Khoa tren man
    Thoi khoa bieu khong loc duoc gi cho toi khi bam Giai.
    """
    slots_per_day = data["params"]["slotsPerDay"]
    day, period = divmod(slot, slots_per_day)
    return {
        "id": s["id"], "teacherId": s["teacher_id"],
        "teacherName": sc.teacher_display(data, s["teacher_id"]),
        "teacherIds": list(s.get("teacher_ids") or [s["teacher_id"]]),
        "courseName": s.get("course_name"), "program": s["program"],
        "programLabel": sc.section_program_label(data, s),
        "programIds": sc.section_program_ids(s),
        "programParts": sc.section_program_names(data, s),
        "facultyName": sc.section_faculty_name(data, s),
        "coordinator": ", ".join(sc.section_coordinators(data, s)),
        "classCode": s.get("class_code"),
        "roomType": s["room_type"], "day": day, "period": period,
        # DIA DIEM (co so) - xem scheduler_core.khu_vuc. Phai co o CA HAI duong
        # sinh buoi (solver va lich ban dau tu file), khong thi the buoi hien dia
        # diem hay khong tuy vao da bam Giai chua.
        "location": s.get("location"), "khuVuc": sc.khu_vuc(s),
        "slot": slot, "duration": s["duration"],
        # BUOI THAM CHIEU: lop do don vi khac dieu phoi, khoa khong xep lai duoc
        # nhung van phai nhin thay (xem domain/bo_qua.py). Frontend doc co nay de
        # ve khac di va khong cho keo-tha.
        "boQua": bool(s.get("bo_qua")),
        "teacherType": s["teacher_type"], "status": "DRAFT",
        "usedWindowLabel": sc.slot_label(slot, slots_per_day),
        # HOC CHUNG: cac buoi cung nhom nam DE LEN NHAU tren luoi (dung y - mot
        # buoi that). Frontend gop chung thanh mot the theo hai truong nay.
        "hocChungId": (nhom_cua(data, s["id"]) or {}).get("id"),
        "hocChungWith": [x for x in thanh_vien(data, s["id"]) if x != s["id"]],
    }


def lich_ban_dau(data):
    """Dung LICH BAN DAU tu cac lop DA CHOT GIO trong file, khong chay solver.

    Vi sao can: nap file xong, man "Thoi khoa bieu" bao "Chua co lich nao - bam
    Giai o buoc 2" du file da chot gio cho phan lon cac lop (HK1-2: 246/343). Giao
    vu phai bam Giai moi thay duoc chinh cai minh vua nap - trong khi nhung gio do
    la DA CHOT, khong phai do thuat toan xep.

    Tra ve (ket_qua_GD1, ket_qua_GD2) dung khuon solver tra ve, kem co
    initial=True de UI biet day KHONG phai ket qua da giai (thanh tien trinh van
    hien "chua chay", nut buoc 3 van cho chay buoc 2 truoc).
    """
    theo_pha = {"GUEST": [], "RESIDENT": []}
    for sid, s in data["sections"].items():
        # Lop do don vi khac dieu phoi: khoa khong xep, nhung neu DA CO GIO thi
        # van len luoi - sinh vien khoa do dang ngoi hoc luc do that (xem
        # domain/bo_qua.py: van_len_luoi). Chi lop chua co gio moi bi giau di.
        if not sc.khoa_phai_xep(s) and not bq.van_len_luoi(s):
            continue
        if s.get("time_assumed") or s.get("original_slot") is None:
            continue
        theo_pha.setdefault(s["teacher_type"], []).append(
            buoi_tren_luoi(data, s, s["original_slot"]))

    return (_goi_ket_qua(data, "GUEST", theo_pha["GUEST"]),
            _goi_ket_qua(data, "RESIDENT", theo_pha["RESIDENT"]))


def _goi_ket_qua(data, loai, lessons):
    """Khuon ket qua "chua giai" - chi la cac gio DA CO SAN dat len luoi."""
    return {
        "status": "TU_FILE", "elapsedSeconds": 0.0,
        "total": sum(1 for s in data["sections"].values()
                     if s["teacher_type"] == loai and sc.khoa_phai_xep(s)),
        # Dem lop CUA KHOA, khong dem buoi tham chieu cua don vi khac: hai con so
        # nay tra loi "phan viec cua minh den dau roi", them lop khong phai viec
        # cua minh vao la doc sai tien do.
        "placedCount": sum(1 for l in lessons if not l.get("boQua")),
        "lessons": sorted(lessons, key=lambda l: l["id"]),
        "unplaced": [], "initial": True,
    }


def gan_buoi_don_vi_khac(data, result, loai):
    """Gan cac buoi DO DON VI KHAC DIEU PHOI (da co gio) vao ket qua giai, de
    chung hien tren luoi y nhu truoc luc bam Giai.

    VI SAO PHAI GAN LAI: solver khong biet gi ve chung (khoa_phai_xep loai tu dau,
    dung y - khoa khong duoc xep lai lop cua don vi khac), nen ket qua no tra ve
    khong co chung. Khong gan lai thi bam Giai xong 65 buoi bien mat khoi luoi, va
    giao vu nhin thay mot tuan trong tram hon thuc te roi xep mon vao dung o do.

    Khong dung vao placedCount/total: hai con so do noi ve PHAN VIEC CUA KHOA."""
    if not result:
        return result
    da_co = {l["id"] for l in (result.get("lessons") or [])}
    them = [buoi_tren_luoi(data, s, s["original_slot"])
            for sid, s in data["sections"].items()
            if s["teacher_type"] == loai and bq.van_len_luoi(s) and sid not in da_co]
    if them:
        result["lessons"] = sorted((result.get("lessons") or []) + them,
                                   key=lambda l: l["id"])
    return result


def dong_bo_ket_qua(data, bo_vi_tri_cu=(), chi_pha=None):
    """Dong bo LUOI THOI KHOA BIEU dang cache (STATE guest/residentResult) voi
    data['sections'] hien tai. Goi sau MOI thao tac sua du lieu hoc phan.

    Vi sao can: guest/residentResult la SNAPSHOT rieng, khong tu doc lai
    data['sections'] moi lan render. Sua lop/GV/hoc phan qua form ma khong dong bo
    thi man Thoi khoa bieu con hien ban cu: lop moi them khong xuat hien, lop doi
    gio van o o cu, doi ten mon/GV thi the buoi ghi ten cu, va doi loai GV thi
    buoi ket lai o giai doan cu.

    `chi_pha`: "GUEST"/"RESIDENT" - chi dung lai mot pha, de nguyen pha kia. Dung
    ngay sau khi giai xong mot giai doan: khong duoc cham vao ket qua solver vua
    tra ve (se lam mat cac truong rieng cua no).

    `bo_vi_tri_cu`: cac section_id vua bi form GHI LAI GIO - voi chung, KHONG
    duoc dung vi tri cu tren luoi lam can cu nua. Can co tham so nay vi mot lop
    "de he thong tu xep" khong co gio rieng, nghiem cua solver la thu duy nhat
    noi no dang o dau -> phai giu. Nhung mot lop VUA BI XOA GIO thi cung o dung
    trang thai do (time_assumed=True, khong co original_slot), khong the phan biet
    bang du lieu; nen cho ben goi noi ro no vua cham vao nhung lop nao.
    """
    bo_vi_tri_cu = set(bo_vi_tri_cu)

    # Vi tri solver da chon cho tung buoi (doc TRUOC khi dung lai luoi).
    slot_solver = {}
    for res in (STATE["guestResult"], STATE["residentResult"]):
        for l in (res or {}).get("lessons") or []:
            if l["id"] not in bo_vi_tri_cu:
                slot_solver[l["id"]] = l["slot"]

    theo_pha = {"GUEST": [], "RESIDENT": []}
    for sid, s in data["sections"].items():
        if not sc.khoa_phai_xep(s) and not bq.van_len_luoi(s):
            continue
        slot = _slot_len_luoi(data, sid, slot_solver)
        if slot is None:
            continue
        theo_pha.setdefault(s["teacher_type"], []).append(buoi_tren_luoi(data, s, slot))

    for loai, khoa in (("GUEST", "guestResult"), ("RESIDENT", "residentResult")):
        if chi_pha is not None and loai != chi_pha:
            continue
        lessons = sorted(theo_pha[loai], key=lambda l: l["id"])
        cu = STATE[khoa]
        if cu is None:
            # Chua giai lan nao va cung chua nap file: chi dung ket qua "chua
            # giai" khi that su co gio de hien, khong tao khung rong.
            if lessons:
                STATE[khoa] = _goi_ket_qua(data, loai, lessons)
                attach_override_metadata(data, STATE[khoa], loai)
            continue
        cu["lessons"] = lessons
        cu["placedCount"] = sum(1 for l in lessons if not l.get("boQua"))
        cu["total"] = sum(1 for s in data["sections"].values()
                          if s["teacher_type"] == loai and sc.khoa_phai_xep(s))
        # Buoi da co cho tren luoi thi khong con "khong xep duoc"; buoi da bi xoa
        # thi khong con gi de noi. Cac muc con lai giu NGUYEN VAN ban solver tra
        # ve (kem `blockers` giai thich vi sao) - khong tu dung muc unplaced moi:
        # lop giao vu vua chuyen sang "de he thong tu xep" chua duoc giai, no
        # KHONG phai "solver khong xep duoc".
        tren_luoi = {l["id"] for l in lessons}
        cu["unplaced"] = [u for u in (cu.get("unplaced") or [])
                          if u["id"] in data["sections"] and u["id"] not in tren_luoi]
        attach_override_metadata(data, cu, loai)


def slot_dang_hien(data, sid):
    """Buoi nay DANG hien o o gio nao tren luoi? None = chua o dau ca.

    Ban tien loi cua _slot_len_luoi cho ben goi chi hoi ve MOT lop (khong dung
    lai ca luoi): tu gom bang vi tri solver roi tra loi. Xem domain/pham_vi.py -
    "dong bang lop ngoai pham vi" chinh la ghim lop do vao dung gio no dang hien,
    nen phai hoi dung mot cau hoi ma luoi dang tra loi, khong tu tinh lai."""
    slot_solver = {}
    for res in (STATE["guestResult"], STATE["residentResult"]):
        for l in (res or {}).get("lessons") or []:
            slot_solver[l["id"]] = l["slot"]
    return _slot_len_luoi(data, sid, slot_solver)


def _slot_len_luoi(data, sid, slot_solver):
    """Buoi nay phai hien o o gio nao tren luoi? None = chua o dau ca.

    Thu tu uu tien, tu manh den yeu:
      1. GHIM  - keo-tha sua tay, hoac gio vua go o form (ghim_theo_gio_form)
      2. GIO CO DINH cua lop - con nguoi da chot, solver buoc phai theo
      3. NGHIEM SOLVER - lop "de he thong tu xep", chi solver biet no o dau
    Dung thu tu ma _detect_move_conflict/chot.slot_dang_hien dang dung, chi khac
    o cho (2) len truoc (3): gio con nguoi vua go phai thang mot nghiem cu.
    """
    ov = STATE["overrides"].get(sid)
    if ov and ov.get("slot") is not None:
        return ov["slot"]
    s = data["sections"][sid]
    if not s.get("time_assumed") and s.get("original_slot") is not None:
        return s["original_slot"]
    return slot_solver.get(sid)


def chot_lop_du_gio_tu_file(data, nguon=None):
    """Danh dau DA CHOT LICH rieng cho moi lop co gio co dinh trong file."""
    now = datetime.datetime.now().isoformat(timespec="seconds")
    dem = 0
    for s in data["sections"].values():
        if s.get("chot") or s.get("time_assumed") or s.get("original_slot") is None:
            continue
        s["chot"] = {
            "at": now, "by": "Nhập từ Excel",
            "note": f"Giờ đã chốt sẵn trong {nguon}" if nguon else "Giờ đã chốt sẵn trong file",
            "tuFile": True,
            "truoc": {"day": s.get("day"), "periodStart": s.get("period_start"),
                       "periodEnd": s.get("period_end"), "timeAssumed": False},
        }
        dem += 1
    return dem


def dat_lich_ban_dau(data, nguon=None):
    """Ghim gio da chot + danh dau tung lop co gio la DA CHOT + dat lich ban dau
    vao STATE (dung sau khi nap file)."""
    chuyen_chot_hoc_phan_cu(data)
    ghim_gio_da_chot(data)
    chot_lop_du_gio_tu_file(data, nguon)
    g, r = lich_ban_dau(data)
    attach_override_metadata(data, g, "GUEST")
    attach_override_metadata(data, r, "RESIDENT")
    STATE["guestResult"], STATE["residentResult"] = g, r


def attach_override_metadata(data, result, teacher_type):
    """Gan {reason, problem, pinFailed} tu STATE['overrides'] len tren ket qua
    giai - CHI la metadata hien thi, khong doi vi tri bat ky buoi nao. pinFailed=
    True khi mot buoi da GHIM van roi vao unplaced (rang buoc cung nhu NoOverlap/
    Cumulative buoc CP-SAT phai bo no du domain chi con 1 lua chon) - ghim la uu
    tien rat manh nhung khong tuyet doi truoc rang buoc cung, dung nhu da chon o
    dong 1."""
    if not result:
        return result
    overrides = {
        sid: ov for sid, ov in STATE["overrides"].items()
        if data["sections"].get(sid, {}).get("teacher_type") == teacher_type
    }
    # LUON gan lai (ke ca rong {}) - neu overrides rong ma return som o day, key
    # result["overrides"] cu se con SOT LAI gia tri cua lan goi truoc (vi du sau
    # khi bo ghim buoi DUY NHAT dang co, ban { } moi khong duoc ghi de len ban cu).
    if not overrides:
        result["overrides"] = {}
        return result

    placed_ids = {l["id"] for l in result["lessons"]}
    out = {}
    for sid, ov in overrides.items():
        out[sid] = {
            "reason": ov.get("reason"),
            "problem": ov.get("problem"),
            "pinFailed": sid not in placed_ids,
        }
    result["overrides"] = out
    return result


def attach_ca_hai(data):
    """Gan metadata ghim cho CA HAI ket qua dang cache - go tat mot buoc lap lai
    o 5 endpoint (chot/bo chot/bo ghim/doc lai ket qua)."""
    attach_override_metadata(data, STATE["guestResult"], "GUEST")
    attach_override_metadata(data, STATE["residentResult"], "RESIDENT")
