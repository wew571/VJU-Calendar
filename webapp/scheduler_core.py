# -*- coding: utf-8 -*-
"""MO HINH CP-SAT (hai giai doan) + cac ham doc thuoc tinh cua mot lop.

Tach rieng khoi Flask de de test/tai su dung: khong import gi tu webapp ca, chi
nhan vao/tra ve bo du lieu `data` (xem domain/sections.py: empty_manual_data).

Hai giai doan:
    solve_guest_phase()     xep lop THINH GIANG trong khung gio ho da bao
    solve_resident_phase()  ghep lop CO HUU vao cho con lai, giu nguyen GD1

check_cross_program_conflicts() la buoc "giao vu khoa check trung" chay TRUOC khi
giai: xet rieng tung giang vien xem cac khung gio hai dieu phoi vien bao cho ho
co the cung ton tai duoc khong.
"""

import bisect
import itertools
import time
from ortools.sat.python import cp_model

from app_config import CONFIG

DAY_NAMES = tuple(CONFIG["calendar"]["slotDayNames"])


def slot_label(s, slots_per_day):
    day, period = divmod(s, slots_per_day)
    return f"{DAY_NAMES[day]} tiet {period + 1}"


def _giao_nhau(a, dur_a, b, dur_b):
    """Hai buoi co chong gio nhau khong (cung mot cong thuc voi app._overlaps va
    overlaps() ben frontend - ba noi phai giong nhau de khong bao lech)."""
    return not (a + dur_a <= b or b + dur_b <= a)


# Quy tac gio day: THINH GIANG duoc day toi Thu 7 (ngay index 5), CO HUU chi
# duoc day toi Thu 6 (ngay index 4) - gio hanh chinh Thu 7 danh rieng cho
# thinh giang, khong ai duoc day Chu nhat (index 6). Index tinh theo DAY_NAMES
# o tren (0 = Thu 2).
MAX_DAY_INDEX = dict(CONFIG["teacherDayLimits"])


def max_day_index(teacher_type):
    return MAX_DAY_INDEX.get(teacher_type, CONFIG["calendar"]["numDays"] - 1)


def valid_starts(num_days, slots_per_day, duration, teacher_type=None):
    """teacher_type: neu co, gioi han so ngay theo MAX_DAY_INDEX (GUEST toi Thu 7,
    RESIDENT toi Thu 6) - bo qua (giu hanh vi cu, toan bo num_days) neu None."""
    if teacher_type is not None:
        num_days = min(num_days, max_day_index(teacher_type) + 1)
    return [
        d * slots_per_day + p
        for d in range(num_days)
        for p in range(slots_per_day - duration + 1)
    ]


def program_label(program_id, program_faculty, faculty_names, program_names_reverse=None):
    name = program_names_reverse.get(program_id) if program_names_reverse else None
    name = name or f"CT{program_id}"
    return f"{name} ({faculty_names[program_faculty[program_id]]})"


# KHU VUC (co so): hai co so cach rat xa nhau, khong di chuyen kip trong ngay -
# rang buoc nghiep vu la "trong 1 ngay, 1 giang vien khong duoc day o ca 2 khu
# vuc" (xem QUY-TRINH-NGHIEP-VU-XEP-TKB.md muc 6).
#
# Tai lieu do noi buoc [4] KHONG xet khu vuc vi phong chua duoc gan. Nhung o
# CHINH file ke hoach da co cot "Dia diem giang day": 276/313 lop that su da ghi
# san Hoa Lac / My Dinh. Da biet thi phai dung - do duoc 2 truong hop mot giang
# vien bi xep ca hai co so trong cung mot ngay (Dang Minh Hieu Thu 2, Le Viet Lan
# Huong Thu 6).
#
# BO DAU khi so sanh: file that ghi ca "Hòa Lạc" lan "Hoà Lạc" (dat dau o hai chu
# khac nhau) - de nguyen thi thanh HAI khu vuc, va lop "Hoà Lạc" duy nhat kia se
# bi bao trung voi 169 lop "Hòa Lạc" con lai.
_DAU = str.maketrans(
    "àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ",
    "a" * 17 + "e" * 11 + "i" * 5 + "o" * 17 + "u" * 11 + "y" * 5 + "d")


def bo_dau(t):
    """Chuoi da chuan hoa de SO KHOP nhan tieng Viet do nguoi go tay: gop khoang
    trang, bo hoa/thuong, bo dau.

    Dung chung cho moi cho phai doc mot O CHU TU DO trong file ("Dia diem giang
    day", "Hinh thuc") - cac o do khong co danh sach chon nen cung mot y duoc go
    ra nhieu kieu ("Hoa Lac" / "Hoa Lac" dat dau o hai chu khac nhau, "Truc tuyen"
    / "truc tuyen")."""
    return " ".join(str(t or "").split()).lower().translate(_DAU)


def khu_vuc(s):
    """Khu vuc (co so) cua mot lop, dang da chuan hoa. None = khong tinh.

    None cho: o trong (37 lop chua ghi), va "Online" - hoc truc tuyen thi khong
    ai phai di chuyen, gop no vao la bao vi pham oan."""
    t = bo_dau(s.get("location"))
    if not t or "online" in t:
        return None
    return t


# THU TU GOM CHUYEN DI: co so cang XA thi cang phai gom lai it ngay. Hoa Lac cach
# trung tam ~30km - len day mot buoi la mat gan ca ngay di lai, nen ba buoi 2 tiet
# rai ra Thu 3/Thu 4/Thu 6 (thay Dang Minh Hieu, HK1 2026-2027-2) la ba chuyen di
# cho sau tiet, trong khi gom mot ngay van du cho. My Dinh trong noi thanh nen
# xep sau. Ten viet o dang da qua bo_dau().
#
# Khu vuc khong co ten trong day (o trong, co so moi) duoc gom chung vao mot muc
# CUOI cung: khong biet cai nao xa hon thi doi xu nhu nhau, con hon doan bua.
THU_TU_KHU_VUC = tuple(CONFIG["campuses"]["priority"])


# KHOI CA HOC theo CO SO: mot buoi day phai nam GON trong mot khoi, khong duoc
# vat ngang. Ghi theo TIET (dem tu 1), khoa la ten khu vuc da qua bo_dau().
#
# HOA LAC: sang tiet 2-5; tu tiet 6 den 13 la mot dai lien (chieu + toi). Tiet 1
# khong dung. Vat ngang tiet 5->6 la bat giang vien cho khong qua gio nghi trua
# (11h50-13h) ma ca hai dau buoi deu khong day du.
#
# Day khong phai luat tu suy dien: du lieu that tuan thu TUYET DOI. Trong 133 lop
# Hoa Lac da chot gio trong file, KHONG lop nao vat ngang tiet 5->6 va KHONG lop
# nao bat dau tiet 1. Chinh SOLVER moi la cho vi pham - 10/10 lan chay deu sinh ra
# it nhat mot buoi sai luat, vi valid_starts() truoc day chi kiem "dung tran sang
# ngay hom sau".
#
# MY DINH: cung cam vat ngang nghi trua, nhung khoi sang bat dau tu TIET 1 chu
# khong phai tiet 2 - khac Hoa Lac o dung cho do. Du lieu that noi ro: trong 76
# lop My Dinh da chot gio co 3 lop bat dau tiet 1, con Hoa Lac thi 0/133. Lay
# (2,5) cho ca hai se bien 3 lop do thanh sai luat oan.
#
# Ca hai co so deu KHONG co ranh gioi sau tiet 9: giao vu da chot la tu tiet 6 den
# 13 mot dai lien. Nen "ca toi" chi la mot cach goi, khong phai mot rang buoc -
# du lieu that cung co 8 lop vat ngang 9->10 (tieng Anh LMS, thuc hanh).
#
# Lop CHUA GHI DIA DIEM (khu_vuc tra None) khong bi rang buoc: khong biet no o co
# so nao thi khong ap luat cua co so nao ca.
#
# Quy dinh CHI ap khi HE THONG chon gio, y het MAX_DAY_INDEX o tren: gio da chot
# trong file hay giao vu ghim tay la quyet dinh cua con nguoi - xem
# loc_theo_khoi_buoi() ve cach ha canh an toan.
KHOI_CA_HOC = {
    kv: tuple(tuple(khoi) for khoi in cac_khoi)
    for kv, cac_khoi in CONFIG["campuses"]["sessionBlocks"].items()
}


def khoi_ca_hoc(s):
    """Cac khoi ca hoc ma mot buoi cua lop nay phai nam gon trong.

    None = khong rang buoc: co so khong co trong KHOI_CA_HOC, hoac lop chua ghi
    dia diem / hoc online (khu_vuc tra None)."""
    return KHOI_CA_HOC.get(khu_vuc(s))


def _gon_trong_khoi(slot, duration, slots_per_day, khoi):
    tiet_dau = slot % slots_per_day + 1
    tiet_cuoi = tiet_dau + duration - 1
    return any(a <= tiet_dau and tiet_cuoi <= b for a, b in khoi)


def loc_theo_khoi_buoi(slots, duration, slots_per_day, khoi):
    """Bo cac khoi diem lam buoi hoc vat ngang ranh gioi ca hoc.

    khoi=None -> tra nguyen ban (co so khong rang buoc).

    LOC HET thi cung TRA NGUYEN BAN, khong tra rong: cung ly le voi "an toan: neu
    cam het thi bo qua cam" o solve_resident_phase. Hai truong hop roi vao day va
    ca hai deu phai ha canh mem:
      - buoi dai hon moi khoi (>=9 tiet o Hoa Lac) - khong khoi nao chua noi;
      - lop chi con DUNG MOT khung, ma khung do la gio con nguoi da chot (mien da
        bi thu hep ve 1 slot boi ghim - xem domain/pinning.py).
    Ca hai deu phai giu duoc lop tren luoi de giao vu nhin thay va tu xu ly, chu
    khong bien mat kem mot dong "khong xep duoc" khong ai hieu tai sao."""
    if not khoi:
        return slots
    ra = [x for x in slots if _gon_trong_khoi(x, duration, slots_per_day, khoi)]
    return ra or slots


def khoa_phai_xep(s):
    """Lop nay co phai viec cua KHOA khong?

    False = o giang vien ghi mot DON VI DIEU PHOI ("Phong Dao tao dieu phoi",
    "JLE dieu phoi") va giao vu da bam bo qua - don vi khac chiu trach nhiem xep
    gio, khoa khong duoc quyen dat. Xem domain/bo_qua.py.

    De o day chu khong o domain/ vi ca hai pha giai deu phai hoi, ma
    scheduler_core khong duoc import gi tu webapp."""
    return not s.get("bo_qua")


def section_program_ids(s):
    """CTDT cua mot lop, LUON la danh sach. Lop cu (sinh gia lap, hoac ban ghi truoc
    khi co program_ids) chi co "program" -> boc thanh danh sach 1 phan tu."""
    return list(s.get("program_ids") or [s["program"]])


def section_program_label(data, s):
    """Nhan CTDT de HIEN THI cho mot lop.

    Uu tien nguyen van trong file ("BCSE+MJM"): he thong HIEU do la hai chuong
    trinh (section_program_ids), nhung VIET ra thi phai dung nhu file - neu khong,
    lop BCSE+MJM se hien thanh "BCSE" va giao vu tuong minh doc nham dong."""
    raw = s.get("program_raw")
    if raw:
        return raw
    return program_label(s["program"], data["program_faculty"], data["faculty_names"],
                         data.get("program_names_reverse"))


def section_program_names(data, s):
    """Ten TUNG chuong trinh thanh phan (["BCSE", "MJM"]) - danh sach de UI dung
    lam muc chon trong bo loc va so khop bang `includes`, thay vi so nguyen chuoi
    "BCSE+MJM" (chon "BCSE" khong ra lop do)."""
    rev = data.get("program_names_reverse") or {}
    ten = [rev.get(pid) for pid in section_program_ids(s)]
    return [t for t in ten if t]


def section_faculty_name(data, s):
    """Ten Khoa cua lop. Truoc day UI boc tu phan trong ngoac cuoi programLabel
    ("BCSE (Chua phan khoa)") - cach do vo ngay khi nhan chuyen sang nguyen van
    nhu file ("BCSE+MJM", khong con ngoac). Gui thang truong nay thi khong ai
    phai doan tu chuoi nua."""
    fid = (data.get("program_faculty") or {}).get(s["program"])
    ten = data.get("faculty_names") or []
    return ten[fid] if fid is not None and fid < len(ten) else None


def section_coordinators(data, s):
    """Ten dieu phoi vien cua lop - MOT NGUOI CHO MOI chuong trinh thanh phan.
    Lop "BCSE+MJM" co hai DPV (DPV-BCSE, DPV-MJM), khong phai mot "DPV-BCSE+MJM"."""
    ten = [data["coordinator_names"].get(pid) for pid in section_program_ids(s)]
    return [t for t in ten if t]


def teacher_display(data, teacher_id):
    """'Ten That (GV#12)' neu co ten that, hoac 'GV 12' neu khong."""
    name = data["teachers"][teacher_id].get("name")
    return f"{name} (GV#{teacher_id})" if name else f"GV {teacher_id}"


# --- HOC CHUNG ------------------------------------------------------------
# Mot nhom hoc chung = MOT buoi day vat ly, ghi thanh NHIEU lop vi co nhieu ma
# mon (vd ECE3083 "Vat lieu tien tien trong xay dung" + BCE3023 "Vat lieu tien
# tien trong ky thuat": cung thay, cung phong LAB, cung Thu 4 tiet 2-4, sinh vien
# hai chuong trinh ngoi chung).
#
# Doc THANG tu data["hoc_chung"] chu khong nhan qua tham so: `data` la toan bo
# hop dong giua module nay va tang tren, va giu duoc nguyen tac "scheduler_core
# khong import gi tu webapp".
#
# Chinh sach (tao/xoa/validate nhom) nam o domain/hoc_chung.py - o day chi co
# hai phep TRA CUU ma solver va cac ham kiem trung can.

def cac_nhom_hoc_chung(data):
    """Danh sach nhom, moi nhom la list section_id (chi giu lop CON TON TAI)."""
    ra = []
    for nhom in data.get("hoc_chung") or []:
        ds = [sid for sid in nhom.get("sectionIds") or [] if sid in data["sections"]]
        if len(ds) > 1:
            ra.append(sorted(ds))
    return ra


def dai_dien_hoc_chung(data):
    """{section_id: section_id DAI DIEN cua nhom}. Lop khong thuoc nhom nao thi
    khong co trong dict.

    Dai dien = id nho nhat, on dinh giua cac lan giai. Solver rang buoc moi thanh
    vien BANG dai dien (cung start, cung placed) va chi dua interval cua DAI DIEN
    vao NoOverlap/Cumulative - nho vay ca nhom la mot buoi, mot phong, va khong
    tu bao trung gio voi chinh minh."""
    ra = {}
    for ds in cac_nhom_hoc_chung(data):
        for sid in ds:
            ra[sid] = ds[0]
    return ra


def cung_nhom_hoc_chung(data, sid_a, sid_b):
    """Hai lop nay la CUNG MOT buoi (hoc chung) chu khong phai trung gio?

    Moi cho kiem trung giang vien deu phai goi ham nay - xem danh sach o
    domain/hoc_chung.py."""
    if sid_a == sid_b:
        return False
    dd = dai_dien_hoc_chung(data)
    return sid_a in dd and dd[sid_a] == dd.get(sid_b)




def check_cross_program_conflicts(data):
    """'Check trung' truoc khi giai: voi moi GV thinh giang day >= 2 buoi (thuong la
    lien 2 chuong trinh, moi chuong trinh 1 dieu phoi vien bao gio rieng), thu TAT
    CA to hop lua chon window cua rieng GV do (khong xet den GV/phong khac) de xem
    co TON TAI it nhat 1 cach xep khong trung gio cho chinh GV nay hay khong.
    Day la buoc "giao vu khoa check trung" xay ra o cap 1 GV, TRUOC khi dua vao
    CP-SAT giai toan bo (CP-SAT giai ca xung dot voi GV/phong khac nua)."""
    p = data["params"]

    # HOC CHUNG: ca nhom la MOT buoi -> chi xet DAI DIEN. Giu ca nhom thi ham nay
    # bao "khong ton tai cach xep nao khong trung" cho dung cai cap ma giao vu da
    # noi ro la hoc chung.
    dai_dien = dai_dien_hoc_chung(data)

    guest_sections_by_teacher = {}
    for s in data["sections"].values():
        if s["teacher_type"] != "GUEST" or not khoa_phai_xep(s):
            continue
        dd = dai_dien.get(s["id"])
        if dd is not None and dd != s["id"]:
            continue
        for tid in (s.get("teacher_ids") or [s["teacher_id"]]):
            guest_sections_by_teacher.setdefault(tid, []).append(s)

    results = []
    for tid, secs in guest_sections_by_teacher.items():
        if len(secs) < 2:
            continue
        # HOP cac chuong trinh thanh phan cua moi lop, khong phai moi "program"
        # dai dien: lop ghi "BCSE+MJM" keo theo CA HAI dieu phoi vien, nen GV day
        # lop do cong mot lop BCSE khac VAN la day lien chuong trinh (truoc day
        # "BCSE+MJM" bi coi la mot chuong trinh thu ba nen truong hop nay bi bo sot).
        programs_involved = sorted({pid for s in secs for pid in section_program_ids(s)})
        is_multi_program = len(programs_involved) > 1
        if not is_multi_program:
            continue  # chi quan tam truong hop lien chuong trinh - dung 1 CT thi khong the co "2 dieu phoi vien"

        sec_windows = [data["submissions"][s["id"]] for s in secs]
        sec_durations = [s["duration"] for s in secs]  # duration RIENG cho tung lop

        # Brute-force: thu moi to hop (1 window/section), kiem tra khong trung
        # (chi giao nhau ve thoi gian, chua xet GV/phong khac)
        def overlaps(i, a, j, b):
            return not (a + sec_durations[i] <= b or b + sec_durations[j] <= a)

        feasible = False
        combo_count = 1
        for w in sec_windows:
            combo_count *= max(len(w), 1)
        if combo_count <= CONFIG["solver"]["crossProgramCombinationLimit"]:  # an toan, tranh no to hop voi GV qua nhieu buoi
            for combo in itertools.product(*sec_windows):
                ok = True
                for i in range(len(combo)):
                    for j in range(i + 1, len(combo)):
                        if overlaps(i, combo[i], j, combo[j]):
                            ok = False
                            break
                    if not ok:
                        break
                if ok:
                    feasible = True
                    break
        else:
            feasible = None  # khong the kiem tra het, de CP-SAT tu quyet dinh

        results.append({
            "teacherId": tid,
            "teacherName": teacher_display(data, tid),
            "sections": [
                {
                    "sectionId": s["id"],
                    "courseName": s.get("course_name"),
                    "program": s["program"],
                    "programLabel": section_program_label(data, s),
                    "programIds": section_program_ids(s),
                    "programParts": section_program_names(data, s),
                    "facultyName": section_faculty_name(data, s),
                                "coordinator": ", ".join(section_coordinators(data, s)),
                    "coordinators": section_coordinators(data, s),
                    "windowSlots": data["submissions"][s["id"]],
                    "windowLabels": [slot_label(w, p["slotsPerDay"]) for w in data["submissions"][s["id"]]],
                }
                for s in secs
            ],
            "feasible": feasible,
            "isForcedConflict": tid in data["forced_conflict_teacher_ids"],
        })

    return results


def guest_sections_can_thu_gio(data, chi_xet=None):
    """Cac lop THINH GIANG con can xu ly truoc khi giai Giai doan 1 (xem
    api/solve.py: api_solve_guest) - dung dung 3 dieu kien nay, KHONG tinh lai
    tu dau, de giong het cach frontend (adapters/submissionQueue.js:
    analyzeSubmissions) chia "Chưa phân công giảng viên" / "Chưa khai giờ",
    tranh hai noi bao lech nhau con bao nhieu lop con thieu.

    Mot lop con can xu ly khi:
      - GV la CHO TRONG (teacher placeholder, chua ai duoc phan cong that) - giai
        luc nay se gan lich cho mot "con nguoi" khong ton tai.
      - hoac availability_assumed=True: co GV that nhung chua ai bao gio THAT,
        he thong dang tam coi la "ranh ca tuan" (xem apply_section_time) - giai
        luc nay se ra lich khong dung rang buoc gio thuc cua GV.
      - hoac dang nam trong pending_section_ids: da khai nhung khong con khung
        nao hop le (xung dot gio giua cac GV dong giang), submissions rong.

    `chi_xet`: tap section_id can xet (XEP THEO PHAM VI - xem domain/pham_vi.py).
    Chan giai phai theo dung pham vi sap xep: xep rieng FTH ma van doi ca khoa
    khai gio xong moi cho bam thi khong CTDT nao xep duoc phan cua minh, vi con
    75 lop cua cac chuong trinh khac chua san sang."""
    pending = set(data["pending_section_ids"])
    return [
        s for s in data["sections"].values()
        if s.get("teacher_type") == "GUEST"
        and khoa_phai_xep(s)
        and (chi_xet is None or s["id"] in chi_xet)
        and (
            data["teachers"].get(s["teacher_id"], {}).get("placeholder")
            or s.get("availability_assumed")
            or s["id"] in pending
        )
    ]


def _theo_thu_tu_khu_vuc(chuyen_di):
    """{khu_vuc: [BoolVar]} -> list cac nhom bool, tu khu vuc DAT nhat den RE nhat
    theo THU_TU_KHU_VUC. Khu vuc la (khong co ten trong danh sach) gop chung vao
    mot nhom cuoi."""
    con_lai = dict(chuyen_di)
    nhom = [con_lai.pop(kv) for kv in THU_TU_KHU_VUC if kv in con_lai]
    khac = [b for kv in sorted(con_lai) for b in con_lai[kv]]
    if khac:
        nhom.append(khac)
    return nhom


def _phat_chuyen_di(chuyen_di, tran_duoi, tran_muc):
    """Chi phi "SO CHUYEN DI cua giang vien" - MOT muc trong thap tu dien, nhung
    ben trong no cac khu vuc lai xep tu dien voi nhau: bot duoc mot chuyen len Hoa
    Lac dang gia hon MOI to hop chuyen di My Dinh cong lai.

    chuyen_di: list cac nhom BoolVar tu khu vuc DAT nhat den RE nhat (xem
               _theo_thu_tu_khu_vuc). Moi bool = mot cap (giang vien, ngay) ma
               nguoi do PHAI co mat o khu vuc do.
    tran_duoi: tong gia tri toi da cua moi muc THAP hon (o day la max_day_load).
    tran_muc:  tran cho rieng muc nay - xem _muc_tieu.

    Tra ve (bieu thuc phat, tran moi); `tran moi` da gom ca tran_duoi.

    VI SAO GOP LAM MOT MUC chu khong tach hai muc rieng nhu SINH VIEN/KHU VUC: he
    so cua moi muc phai lon hon TONG cac muc duoi, ma so bool chuyen di lon hon
    han (269 Hoa Lac + 276 My Dinh, so voi 76 vi pham khu vuc). Tach hai muc thi
    he so cua muc "xep duoc" phong len ~300 lan va ham muc tieu cham tran int64
    khi du lieu to len. Long trong so o day cho ra DUNG cung mot thu tu ma khong
    bat cac muc TREN phai phong theo."""
    phat, tran, w = [], tran_duoi, tran_duoi + 1
    for bools in reversed(chuyen_di):        # tu khu vuc RE nhat di len
        if not bools:
            continue
        phat.append(w * sum(bools))
        tran += w * len(bools)
        # He so cua khu vuc ke tiep: lon hon TAT CA cac muc duoi -> uu tien tuyet
        # doi. Tru khi da cham tran_muc (du lieu to gap may lan hien nay), luc do
        # lui ve "nang gap 8 lan": van dung huong uu tien, chi khong con tuyet
        # doi - hon han de he so tran int64 va solver tra ve rac.
        w = tran + 1 if tran + 1 <= tran_muc else w * 8
    return (sum(phat) if phat else 0), tran


def _muc_tieu(model, so_lop, dat_duoc, vi_pham_kv, max_day_load, vi_pham_sv=(),
              chuyen_di=()):
    """Ham muc tieu chung cua ca hai pha, NAM muc uu tien theo THU TU TU DIEN:

        1. XEP DUOC nhieu buoi nhat  (tuyet doi - khong bao gio danh doi)
        2. It cap lop bat SINH VIEN mot nhom hoc hai cho cung luc nhat
           (xem _rang_buoc_nhom_sinh_vien)
        3. It cap (GV, ngay) bi dinh HAI CO SO nhat   (xem _rang_buoc_khu_vuc)
        4. It CHUYEN DI nhat cho moi giang vien: Hoa Lac truoc, roi den My Dinh
           (xem _phat_chuyen_di va THU_TU_KHU_VUC)
        5. Tai cua ngay nang nhat thap nhat - dan deu ra ca tuan

    Viet bang trong so chu khong giai nam lan: he so cua muc tren phai lon hon
    TONG GIA TRI TOI DA ma moi muc duoi cong lai co the dat, thi khong to hop nao
    o muc duoi bu noi mot don vi o muc tren.

    Vi sao SINH VIEN dung tren KHU VUC: mot buoi bi trung khu vuc thi giang vien
    con di chuyen duoc (chi la rat vat va, va thuong con sua tay duoc sau); con
    hai lop cung gio cua mot nhom sinh vien thi khong ai du hai cho mot luc -
    lich do khong dung duoc, khong phai lich xau.

    Vi sao CHUYEN DI dung tren DAN NGAY: muc 5 chu dong DAY cac buoi ra cac ngay
    khac nhau, va do chinh la cai da rai ba lop Hoa Lac cua mot giang vien ra ba
    ngay. Hai muc nay nguoc huong nhau nen thu tu la tat ca: dat chuyen di len
    tren thi dan ngay chi con la tieu chi pha hoa.

    So vi pham toi da lay theo DUNG SO BIEN da tao (len(...)) chu khong uoc luong
    theo so lop nhu ban dau: so cap (GV, ngay) hay so cap lop cung nhom deu co the
    nhieu hon so lop, va uoc thap thi thu tu tu dien HONG am tham - solver duoc
    phep danh doi mot bac tren de lay nhieu bac duoi."""
    n_kv, n_sv = len(vi_pham_kv), len(vi_pham_sv)
    tran = so_lop + 1                          # muc 5: max_day_load, he so 1

    # Tran rieng cho muc CHUYEN DI. Moi muc TREN no deu nhan len, nen phai chua
    # cho san: he so cao nhat ~ tran * (n_kv+1) * (n_sv+1), roi con nhan tiep voi
    # dat_duoc (toi da ~2*so_lop*(so_lop+1) khi co lop "khong duoc hy sinh", xem
    # _trong_so_giu_cho). CP-SAT tu choi mien vuot 2^62 nen lay do lam moc.
    # Tren du lieu that (294 lop) muc nay can ~2.2e7 con tran cho phep ~4.4e8.
    nhan_len = (n_kv + 1) * (n_sv + 1) * 2 * (so_lop + 1) ** 2
    phat_di, tran = _phat_chuyen_di(chuyen_di, tran, 2 ** 62 // max(1, nhan_len))

    w_kv = tran + 1                            # 1 vi pham nang hon moi to hop chuyen di
    tran += w_kv * n_kv
    w_sv = tran + 1                            # 1 vu trung SV nang hon moi to hop khu vuc
    tran += w_sv * n_sv
    w_dat = tran + 1                           # 1 buoi mat cho nang hon tat ca muc duoi
    return (w_dat * dat_duoc
            - w_sv * sum(vi_pham_sv)
            - w_kv * sum(vi_pham_kv)
            - phat_di
            - max_day_load)


def _co_the_chong(mien_a, dur_a, mien_b, dur_b):
    """Hai lop nay CO THE chong gio nhau khong, xet tren mien khoi diem cua chung?

    Khong the thi khoi tao bien vi pham - tren du lieu that phan lon cap lop cung
    nhom deu roi vao truong hop nay (khung gio cach xa nhau), tao bien cho ca
    1567 cap la nang mo hinh vo ich."""
    if not mien_a or not mien_b:
        return False
    b = sorted(mien_b)
    for x in mien_a:
        # Chong gio <=> ton tai y thoa  x - dur_b < y < x + dur_a
        i = bisect.bisect_right(b, x - dur_b)
        if i < len(b) and b[i] < x + dur_a:
            return True
    return False


def _rang_buoc_nhom_sinh_vien(model, cap_can_ne, bien, co_dinh):
    """Rang buoc MEM "sinh vien mot nhom (CTDT x Khoa) khong hoc hai lop cung luc".

    Tra ve danh sach BoolVar `vi_pham`, moi cai la MOT CAP LOP dang chong gio.
    Ben goi tru chung trong ham muc tieu.

    Module nay khong biet gi ve CTDT/Khoa - luat gom nhom nam o
    domain/nhom_sinh_vien.py va di vao day duoi dang `cap_can_ne`, dung nguyen tac
    "scheduler_core khong import gi tu webapp" (xem docstring dau file va
    khoa_phai_xep). Nho vay doi luat gom nhom khong phai dong vao mo hinh.

    cap_can_ne: {(sid_a, sid_b): nhan_nhom} - cac cap KHONG duoc chong gio.
    bien:       {sid: (start IntVar, placed BoolVar, duration, mien khoi diem)}
    co_dinh:    {sid: (slot, duration)} - buoi da co cho ma pha nay khong dat lai
                (ket qua Giai doan 1, hoac lop bi dong bang khi xep theo pham vi).

    MEM chu khong CUNG, cung ly le voi _rang_buoc_khu_vuc: gio cua phan lon lop da
    chot san trong file va trong so do da co san 25 cap trung nhau. Rang buoc cung
    se lam ca bai toan vo nghiem va giao vu mat trang ket qua. Mem thi lich xau
    nhat cung chi bang lich hien tai, con thuong thi solver tu tranh."""
    vi_pham = []
    for (a, b), _ten in sorted(cap_can_ne.items()):
        va, vb = bien.get(a), bien.get(b)
        ca, cb = co_dinh.get(a), co_dinh.get(b)
        # Ca hai deu da co cho co dinh: pha nay khong dat lai cai nao, co bao vi
        # pham cung khong doi duoc gi - de vong kiem tra ben ngoai bao ra.
        if va and vb:
            if not _co_the_chong(va[3], va[2], vb[3], vb[2]):
                continue
            v = model.NewBoolVar(f"trungsv_{a}_{b}")
            # `truoc` chon THU TU: khong co no thi "khong chong gio" la mot phep
            # HOAC hai ve, ma OnlyEnforceIf chi ap duoc cho MOT rang buoc.
            truoc = model.NewBoolVar(f"trungsv_thutu_{a}_{b}")
            model.Add(va[0] + va[2] <= vb[0]).OnlyEnforceIf([v.Not(), truoc, va[1], vb[1]])
            model.Add(vb[0] + vb[2] <= va[0]).OnlyEnforceIf([v.Not(), truoc.Not(), va[1], vb[1]])
            vi_pham.append(v)
            continue
        for bien_1, co_dinh_1 in ((va, cb), (vb, ca)):
            if not (bien_1 and co_dinh_1):
                continue
            slot, dur = co_dinh_1
            cho_phep = [x for x in bien_1[3]
                        if x + bien_1[2] <= slot or slot + dur <= x]
            if len(cho_phep) == len(bien_1[3]):
                break  # khong the dam vao buoi co dinh do -> khong can bien nao
            v = model.NewBoolVar(f"trungsv_{a}_{b}")
            # Mien rong (moi khung gio deu dam vao) van hop le: rang buoc thanh
            # sai, ep v = 1 hoac lop khong duoc xep - dung nhu y nghia can co.
            model.AddLinearExpressionInDomain(
                bien_1[0], cp_model.Domain.FromValues(cho_phep)
            ).OnlyEnforceIf([v.Not(), bien_1[1]])
            vi_pham.append(v)
            break
    return vi_pham


def _rang_buoc_khu_vuc(model, data, ngay_bools, co_dinh, num_days):
    """Rang buoc MEM "1 giang vien khong day 2 co so trong 1 ngay", VA dem so
    chuyen di cua tung giang vien.

    Tra ve (vi_pham, chuyen_di):
      vi_pham:   [BoolVar] - moi cai la mot cap (giang vien, ngay) bi dinh ca hai
                 co so. Ben goi TRU chung trong ham muc tieu.
      chuyen_di: {khu_vuc: [BoolVar]} - moi bool la mot cap (giang vien, ngay) ma
                 nguoi do PHAI co mat o khu vuc do. Ben goi phat theo THU_TU_KHU_VUC
                 de gom bot so ngay phai len Hoa Lac (xem _phat_chuyen_di).

    Hai thu di chung mot vong vi dung chung dung mot bien: "GV nay co mat o khu vuc
    kia trong ngay do khong". Tach ra la tao hai lan cung mot bool.

    MEM chu khong CUNG: gio cua phan lon lop da chot san trong file, ma khong it
    cap trong so do von da vi pham san (do duoc 2 truong hop). Rang buoc cung se
    lam ca bai toan vo nghiem va giao vu mat trang ket qua - dung cai gia da tra
    mot lan o Giai doan 2 (xem chu thich cho on_day_bools). Mem thi lich xau nhat
    cung chi la lich hien tai, con thuong thi solver tu tranh.

    ngay_bools: {section_id: {ngay: [BoolVar]}} - "lop nay co roi vao ngay do khong".
    co_dinh:    {(teacher_id, ngay): set(khu_vuc)} - tu cac buoi DA CO CHO ma pha
                nay khong dat lai (dong bang / ket qua Giai doan 1). Thieu phan nay
                thi xep rieng mot chuong trinh se khong thay lop cua chuong trinh
                khac, va bao "khong vi pham" trong khi thuc te co."""
    theo_gv = {}
    for sid, theo_ngay in ngay_bools.items():
        kv = khu_vuc(data["sections"].get(sid) or {})
        if kv is None:
            continue
        for tid in (data["sections"][sid].get("teacher_ids")
                    or [data["sections"][sid]["teacher_id"]]):
            for ngay, bools in theo_ngay.items():
                theo_gv.setdefault((tid, ngay), {}).setdefault(kv, []).extend(bools)

    # Cac cap (GV, ngay) chi co the roi vao dung mot khu vuc thi khong can bien nao.
    for khoa, kv_co_dinh in co_dinh.items():
        for kv in kv_co_dinh:
            theo_gv.setdefault(khoa, {}).setdefault(kv, [])

    vi_pham, chuyen_di = [], {}
    # sorted() de mo hinh duoc dung theo mot thu tu co dinh, khong phu thuoc thu
    # tu chen vao dict - cung ly le voi _rang_buoc_nhom_sinh_vien.
    for (tid, ngay), theo_kv in sorted(theo_gv.items()):
        co = []
        for kv, bools in sorted(theo_kv.items()):
            if kv in co_dinh.get((tid, ngay), ()):
                co.append(1)          # buoi da co cho o khu vuc nay - chac chan co mat
                # KHONG ke vao chuyen_di: chuyen nay chac chan xay ra, pha nay
                # khong go duoc, ma hang so trong ham muc tieu thi khong doi
                # nghiem. Bo di vua giu thap tu dien thap, vua dung nghiep vu -
                # da phai len do roi thi xep them buoi nua vao dung ngay do la
                # MIEN PHI, chinh la cai ta muon solver lam.
                continue
            if not bools:
                continue
            b = model.NewBoolVar(f"kv_{tid}_{ngay}_{abs(hash(kv)) % 10**6}")
            model.AddMaxEquality(b, bools)   # OR: co it nhat mot buoi o khu vuc nay
            co.append(b)
            chuyen_di.setdefault(kv, []).append(b)
        # Vi pham "hai co so mot ngay" chi co nghia khi cap (GV, ngay) nay co the
        # cham toi tu hai khu vuc tro len; `chuyen_di` o tren thi van dem du.
        if len(co) < 2:
            continue
        v = model.NewBoolVar(f"vipham_kv_{tid}_{ngay}")
        model.Add(sum(co) <= 1).OnlyEnforceIf(v.Not())
        vi_pham.append(v)
    return vi_pham, chuyen_di


def _trong_so_giu_cho(placed, uu_tien_giu):
    """Trong so cua tung lop trong muc tieu "toi da hoa so buoi xep duoc".

    Mac dinh moi lop nang bang nhau (=1) - dung nhu truoc. `uu_tien_giu` la cac
    lop KHONG DUOC HY SINH: chung nang bang CA DAN cong mot, nen khong to hop lop
    thuong nao bu noi viec mat mot lop trong nhom nay. Tuc mot thu tu tu dien
    ("giu bang duoc nhom nay da, roi moi toi da hoa phan con lai") viet bang trong
    so, khong phai giai hai lan.

    DUNG DE LAM GI: khi XEP THEO PHAM VI (domain/pham_vi.py), lop cua chuong trinh
    KHAC bi ghim vao dung cho no dang dung. Nhung ghim = thu hep mien, ma interval
    van la Optional - solver hoan toan co the BO no de xep duoc them lop trong pham
    vi. Do tren du lieu that: ep mot lop FTH chi con dung mot khung gio trung voi
    lop ECE cua cung giang vien -> lop ECE bi hat ra khoi luoi. Dung cai ma tinh
    nang nay sinh ra de tranh.

    VI SAO KHONG DONG BANG CUNG (interval co dinh, khong Optional): hai buoi dong
    bang chong gio nhau cua cung mot nguoi se lam mo hinh INFEASIBLE va MAT TRANG
    ca ket qua - cai gia da tra mot lan o Giai doan 2 (xem chu thich cho on_day_bools).
    Du lieu that co dong nhap trung, nen phai chon huong hong nhe: lop do roi vao
    "khong xep duoc" kem ly do, chu khong lam ca bai toan vo nghiem."""
    if not uu_tien_giu:
        return {sid: 1 for sid in placed}
    manh = len(placed) + 1
    return {sid: (manh if sid in uu_tien_giu else 1) for sid in placed}


def solve_guest_phase(data, time_limit_s=CONFIG["solver"]["timeLimitSeconds"], dong_bang=None, uu_tien_giu=None,
                      cap_can_ne=None, gio_lop_pha_khac=None):
    """dong_bang: cac buoi DA CO CHO ma pha nay khong duoc dung toi - dua vao mo
    hinh nhu interval dat CUNG mot slot de vua chiem gio giang vien, vua chiem mot
    phong. Nhan cung khuon lesson ma solve_resident_phase nhan qua
    `frozen_guest_lessons` (id/slot/duration/roomType/teacherIds), nhung o day la
    interval OPTIONAL co trong so rat nang chu khong CO DINH - xem chu thich ngay
    tai cho tao interval, va _trong_so_giu_cho().

    MAC DINH None = y het hanh vi cu (Giai doan 1 khong biet gi ve lop co huu, va
    Giai doan 2 chay sau se ne no). Chi dung khi XEP THEO PHAM VI (xem
    domain/pham_vi.py): luc do Giai doan 2 KHONG duoc phep dich cac lop co huu
    ngoai pham vi de nhuong cho nua, nen Giai doan 1 phai biet truoc ho o dau -
    khong thi mot buoi thinh giang cua pham vi de len lop co huu cua chuong trinh
    khac va khong con ai go duoc.

    cap_can_ne: {(sid_a, sid_b): nhan} - cac cap lop CUNG NHOM SINH VIEN, khong
    duoc chong gio (rang buoc mem, xem _rang_buoc_nhom_sinh_vien). MAC DINH None =
    khong xet, y het hanh vi cu. Luat gom nhom nam o domain/nhom_sinh_vien.py.

    gio_lop_pha_khac: {section_id: slot} - gio cua cac lop CO HUU ma Giai doan 2
    se khong doi duoc (gio chot trong file, hoac giao vu da ghim tay). CHI dung
    cho rang buoc nhom sinh vien, khong dung vao GV/phong - khac han `dong_bang`.

    Vi sao can: pha nay von khong biet gi ve lop co huu, va do la co y - GD2 chay
    sau se ne no. Nhung "ne" chi lam duoc voi lop GD2 con quyen dich; lop co huu
    da chot gio thi khong. Khong bao truoc thi GD1 dat mot lop thinh giang de len
    dung o do va KHONG CON AI GO DUOC - do tren du lieu that: "Ky nang bo tro"
    (BCSE/VJU2025) de len "Quan tri kinh doanh" da chot Thu 6 tiet 3."""
    p = data["params"]
    guest_sections = [s for s in data["sections"].values()
                      if s["teacher_type"] == "GUEST" and khoa_phai_xep(s)]

    model = cp_model.CpModel()
    starts, placed = {}, {}
    intervals_by_teacher = {}
    intervals_by_roomtype = {"LT": [], "LAB": []}
    day_load_terms = {d: [] for d in range(p["numDays"])}  # cho muc tieu dan ngay (phu)

    # HOC CHUNG: ca nhom la MOT buoi -> chi DAI DIEN gop mat trong NoOverlap
    # (khong tu bao trung voi chinh minh) va Cumulative (chi ton 1 phong), con
    # cac thanh vien bi rang buoc BANG dai dien o cuoi vong lap.
    ngay_bools = {}    # sid -> {ngay: [BoolVar]} - cho rang buoc khu vuc
    dai_dien = dai_dien_hoc_chung(data)
    gv_cua_nhom = {}   # sid dai dien -> hop teacher_ids cua CA NHOM
    for s in guest_sections:
        dd = dai_dien.get(s["id"])
        if dd is not None:
            gv_cua_nhom.setdefault(dd, set()).update(s.get("teacher_ids") or [s["teacher_id"]])

    # Buoi bi DONG BANG (chi co khi xep theo pham vi): interval co dinh, vao ca
    # rang buoc GV lan rang buoc phong - hai thu ma pha nay se pha neu khong biet.
    # HOC CHUNG chi dong bang DAI DIEN, y het solve_resident_phase: dong bang ca
    # nhom la hai interval CO DINH trung khit nhau cung vao AddNoOverlap cua cung
    # mot nguoi -> mo hinh INFEASIBLE ngay.
    dong_bang_hien_dien = {}   # sid -> BoolVar "buoi dong bang nay CO duoc ton trong"
    # Buoi da co cho ma pha nay khong dat lai - lop cua pham vi khac phai NE gio
    # cua chung, ke ca ve phia sinh vien. Lay TAT CA (khong loc dai dien hoc chung
    # nhu vong duoi): mot cap can ne co the tro thang vao mot thanh vien.
    co_dinh_sv = {
        sid: (slot, (data["sections"].get(sid) or {}).get("duration", p["duration"]))
        for sid, slot in (gio_lop_pha_khac or {}).items() if slot is not None
    }
    co_dinh_sv.update({g["id"]: (g["slot"], g.get("duration", p["duration"]))
                       for g in (dong_bang or [])})
    bien_sv = {}
    for g in (dong_bang or []):
        dd = dai_dien.get(g["id"])
        if dd is not None and dd != g["id"]:
            continue
        # OPTIONAL chu khong CO DINH, du day la buoi "khong duoc dong toi".
        #
        # Hai buoi dong bang chong gio nhau cua CUNG mot giang vien se lam
        # AddNoOverlap vo nghiem NGAY -> ca lan giai mat trang, dung cai gia da
        # tra mot lan o Giai doan 2 (xem chu thich cho on_day_bools). Ma tap dong
        # bang KHONG dam bao sach: gio cua chung co the den tu `original_slot`
        # trong file, ma file that co dong nhap trung dat cung mot o cho cung mot
        # nguoi.
        #
        # Nen: cho phep bo, nhung dat trong so RAT NANG trong ham muc tieu (xem
        # _trong_so_giu_cho) de solver chi bo khi that su khong con duong nao.
        # Hong nhe = mot buoi bi bao ten trong `dongBangBiDay`; hong nang = khong
        # co ket qua nao ca.
        hien_dien = model.NewBoolVar(f"dongbang_co_{g['id']}")
        dong_bang_hien_dien[g["id"]] = hien_dien
        iv = model.NewOptionalFixedSizeIntervalVar(
            g["slot"], g.get("duration", p["duration"]), hien_dien, f"dongbang_{g['id']}")
        intervals_by_roomtype[g["roomType"]].append(iv)
        gv = set(g.get("teacherIds") or [g["teacherId"]])
        if dd is not None:
            for sid2 in next((x for x in cac_nhom_hoc_chung(data) if x[0] == dd), []):
                s2 = data["sections"].get(sid2) or {}
                gv.update(s2.get("teacher_ids") or ([s2["teacher_id"]] if s2 else []))
        for tid in gv:
            intervals_by_teacher.setdefault(tid, []).append(iv)

    for s in guest_sections:
        sid = s["id"]
        # KHOI CA HOC: bo cac khung lam buoi vat ngang nghi trua (xem KHOI_CA_HOC).
        # Loc BAN SAO dung cho mo hinh, khong dung vao data["submissions"]: cai do
        # la "khung gio dieu phoi vien DA BAO", mot su that ve con nguoi - man hinh
        # phai hien nguyen van, va `submitted_windows` o duoi doc thang tu no.
        windows = loc_theo_khoi_buoi(
            data["submissions"][sid], s["duration"], p["slotsPerDay"], khoi_ca_hoc(s))
        start = model.NewIntVar(0, p["numDays"] * p["slotsPerDay"] - 1, f"start_{sid}")
        is_placed = model.NewBoolVar(f"placed_{sid}")
        window_bools = []
        for wi, slot in enumerate(windows):
            b = model.NewBoolVar(f"win_{sid}_{wi}")
            model.Add(start == slot).OnlyEnforceIf(b)
            window_bools.append(b)
            day_load_terms[slot // p["slotsPerDay"]].append(b)
            # Gom theo NGAY de rang buoc khu vuc biet "lop nay co roi vao ngay do
            # khong" - GD1 khong co bien ngay rieng, ngay la he qua cua khung gio
            # nao duoc chon.
            ngay_bools.setdefault(sid, {}).setdefault(
                slot // p["slotsPerDay"], []).append(b)
        model.Add(sum(window_bools) == 1).OnlyEnforceIf(is_placed)
        model.Add(sum(window_bools) == 0).OnlyEnforceIf(is_placed.Not())
        interval = model.NewOptionalFixedSizeIntervalVar(start, s["duration"], is_placed, f"iv_{sid}")

        starts[sid] = start
        placed[sid] = is_placed
        bien_sv[sid] = (start, is_placed, s["duration"], windows)
        dd = dai_dien.get(sid)
        if dd is not None and dd != sid:
            continue  # thanh vien: rang buoc theo dai dien, khong chiem GV/phong rieng
        # Doi voi lesson co NHIEU GV dong giang day (teacher_ids), cung 1 interval
        # duoc dua vao NoOverlap cua TAT CA nguoi do - dam bao khong ai trong nhom
        # bi trung lich o cho khac, ma khong nhan doi nhu cau phong.
        # Lop la DAI DIEN mot nhom hoc chung thi lay hop GV cua ca nhom: buoi do
        # co mat CA HO, nen ho khong the day cho khac cung gio.
        for tid in (gv_cua_nhom.get(sid) or s.get("teacher_ids") or [s["teacher_id"]]):
            intervals_by_teacher.setdefault(tid, []).append(interval)
        intervals_by_roomtype[s["room_type"]].append(interval)

    # Thanh vien nhom hoc chung: CUNG gio va CUNG so phan voi dai dien.
    for ds in cac_nhom_hoc_chung(data):
        rep = ds[0]
        if rep not in starts:
            continue  # nhom nay khong thuoc pha nay
        for sid in ds[1:]:
            if sid in starts:
                model.Add(starts[sid] == starts[rep])
                model.Add(placed[sid] == placed[rep])

    for ivs in intervals_by_teacher.values():
        if len(ivs) > 1:
            model.AddNoOverlap(ivs)

    for room_type, ivs in intervals_by_roomtype.items():
        pool = p["ltPool"] if room_type == "LT" else p["labPool"]
        if ivs:
            model.AddCumulative(ivs, [1] * len(ivs), pool)

    # Muc tieu chinh: toi da hoa so buoi xep duoc (trong so lon, luon uu tien
    # tuyet doi truoc). Muc tieu phu: giam tai cao nhat cua 1 ngay bat ky (dan
    # deu ra ca tuan, tranh don het vao 1 ngay khi khong bat buoc).
    max_day_load = model.NewIntVar(0, len(guest_sections) + 1, "max_day_load_guest")
    for d in range(p["numDays"]):
        if day_load_terms[d]:
            model.Add(sum(day_load_terms[d]) <= max_day_load)
    kv_co_dinh = {}
    for g in (dong_bang or []):
        kv = khu_vuc(data["sections"].get(g["id"]) or {})
        if kv is None:
            continue
        ngay = g["slot"] // p["slotsPerDay"]
        for tid in (g.get("teacherIds") or [g["teacherId"]]):
            kv_co_dinh.setdefault((tid, ngay), set()).add(kv)
    vi_pham_kv, chuyen_di = _rang_buoc_khu_vuc(
        model, data, ngay_bools, kv_co_dinh, p["numDays"])
    vi_pham_sv = _rang_buoc_nhom_sinh_vien(model, cap_can_ne or {}, bien_sv, co_dinh_sv)

    trong_so = _trong_so_giu_cho(placed, uu_tien_giu)
    # Buoi DONG BANG nang y het lop "khong duoc hy sinh": chung deu la lop cua
    # chuong trinh khac dang co cho, chi khac la pha nay khong co bien cho chung.
    manh = len(placed) + 1
    model.Maximize(_muc_tieu(
        model, len(guest_sections),
        dat_duoc=(sum(trong_so[sid] * v for sid, v in placed.items())
                  + manh * sum(dong_bang_hien_dien.values())),
        vi_pham_kv=vi_pham_kv, max_day_load=max_day_load, vi_pham_sv=vi_pham_sv,
        chuyen_di=_theo_thu_tu_khu_vuc(chuyen_di)))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit_s
    solver.parameters.num_search_workers = CONFIG["solver"]["numSearchWorkers"]

    t0 = time.time()
    status = solver.Solve(model)
    elapsed = time.time() - t0

    lessons = []
    unplaced = []
    for s in guest_sections:
        sid = s["id"]
        prog_label = section_program_label(data, s)
        # Danh sach chuong trinh thanh phan + ten Khoa: UI loc/gom theo cai nay,
        # khong boc tach lai tu chuoi nhan (xem section_program_names).
        prog_meta = {"programIds": section_program_ids(s),
                     "programParts": section_program_names(data, s),
                     "facultyName": section_faculty_name(data, s)}
        coordinator = ", ".join(section_coordinators(data, s))
        submitted_windows = data["submissions"][sid]
        if solver.Value(placed[sid]) == 1:
            slot = solver.Value(starts[sid])
            day, period = divmod(slot, p["slotsPerDay"])
            unused_windows = [w for w in submitted_windows if w != slot]
            lessons.append({
                "id": sid, "teacherId": s["teacher_id"], "teacherName": teacher_display(data, s["teacher_id"]),
                # TAT CA GV cua buoi nay (dong giang day). teacherId van la GV
                # chinh de hien thi; cac man kiem trung/lich cua 1 GV phai doc
                # teacherIds, khong thi buoi nay vo hinh voi nguoi thu 2 tro di
                # du solver DA rang buoc ho (xem AddNoOverlap o tren).
                "teacherIds": list(s.get("teacher_ids") or [s["teacher_id"]]),
                "courseName": s.get("course_name"), "program": s["program"],
                "programLabel": prog_label, **prog_meta, "coordinator": coordinator,
                "roomType": s["room_type"], "day": day, "period": period,
                # DIA DIEM (co so): giao vu phai doi chieu duoc "ngay do co bi day
                # ca hai co so khong" ngay tren the buoi - xem khu_vuc().
                "location": s.get("location"), "khuVuc": khu_vuc(s),
                "slot": slot, "duration": s["duration"], "teacherType": "GUEST",
                "usedWindowLabel": slot_label(slot, p["slotsPerDay"]),
                "unusedFlexibleWindows": [slot_label(w, p["slotsPerDay"]) for w in unused_windows],
            })
        else:
            other_sections = [
                {
                    "sectionId": s2["id"],
                    "courseName": s2.get("course_name"),
                    "program": s2["program"],
                    "programLabel": section_program_label(data, s2),
                    "programIds": section_program_ids(s2),
                    "programParts": section_program_names(data, s2),
                    "facultyName": section_faculty_name(data, s2),
                    "coordinator": ", ".join(section_coordinators(data, s2)),
                    "windows": [slot_label(w, p["slotsPerDay"]) for w in data["submissions"][s2["id"]]],
                }
                for s2 in guest_sections
                if s2["teacher_id"] == s["teacher_id"] and s2["id"] != sid
            ]
            unplaced.append({
                "id": sid, "teacherId": s["teacher_id"], "teacherName": teacher_display(data, s["teacher_id"]),
                "teacherIds": list(s.get("teacher_ids") or [s["teacher_id"]]),  # dong giang day
                "courseName": s.get("course_name"), "program": s["program"],
                "programLabel": prog_label, **prog_meta, "coordinator": coordinator,
                "roomType": s["room_type"],
                "windows": [slot_label(w, p["slotsPerDay"]) for w in submitted_windows],
                "isForcedConflict": s["teacher_id"] in data["forced_conflict_teacher_ids"],
                "notSubmittedYet": len(submitted_windows) == 0,
                "otherSectionsSameTeacher": other_sections,
            })

    return {
        "status": solver.StatusName(status),
        "elapsedSeconds": round(elapsed, 3),
        "total": len(guest_sections),
        "placedCount": len(lessons),
        "lessons": lessons,
        "unplaced": unplaced,
        # Buoi dong bang ma pha nay buoc phai xep de len (tap dong bang tu no da
        # co xung dot) - phai bao ten, khong duoc im lang. Rong trong moi truong
        # hop binh thuong.
        "dongBangBiDay": [sid for sid, b in dong_bang_hien_dien.items()
                          if solver.Value(b) == 0],
    }


def solve_resident_phase(data, frozen_guest_lessons, forbidden=None, time_limit_s=CONFIG["solver"]["timeLimitSeconds"],
                         ghim_tay=None, bo_ghim=None, uu_tien_giu=None, cap_can_ne=None,
                         gio_lop_pha_khac=None):
    """forbidden: dict {section_id: [danh sach slot bi tu choi]}
    ghim_tay: dict {section_id: slot} - giao vu keo-tha/ghim tay o man TKB.
    bo_ghim: set section_id - giao vu BAM "Bo ghim" o man TKB, tuc noi ro "cho he
    thong xep lai lop nay". Bo qua ghim theo `original_slot` cho cac lop do; app.py
    lo phan submissions (xem _mien_sau_khi_bo_ghim).

    uu_tien_giu: tap section_id KHONG DUOC HY SINH de xep duoc lop khac (lop cua
    chuong trinh NGOAI pham vi dang xep) - xem _trong_so_giu_cho().

    cap_can_ne: {(sid_a, sid_b): nhan} - cac cap lop CUNG NHOM SINH VIEN, y het
    solve_guest_phase. Buoi cua Giai doan 1 vao day duoi dang CO DINH: lop co huu
    phai ne gio cua chung ve phia sinh vien, khong chi ve phia giang vien/phong.

    gio_lop_pha_khac: {section_id: slot} - gio cua cac lop KHONG NAM TRONG PHA NAY
    ma van chiem thoi gian cua sinh vien: lop do don vi khac dieu phoi da co gio
    (domain/bo_qua.py). CHI dung cho rang buoc nhom sinh vien - chung khong chiem
    giang vien cung khong chiem phong o day.

    ghim_tay dat domain THANG bang slot do, khong di qua valid_starts(): nho vay
    ghim duoc sang Thu 7/Chu nhat. Truoc day app.py ghim bang cach cam moi slot
    hop le TRU slot da ghim, ma slot Chu nhat KHONG nam trong valid_starts cua
    RESIDENT -> "cam tat ca" -> domain rong -> ghim bi bo qua am tham."""
    p = data["params"]
    forbidden = forbidden or {}
    bo_ghim = bo_ghim or set()
    resident_sections = [s for s in data["sections"].values()
                         if s["teacher_type"] == "RESIDENT" and khoa_phai_xep(s)]

    model = cp_model.CpModel()
    starts, placed = {}, {}
    intervals_by_teacher = {}
    intervals_by_roomtype = {"LT": [], "LAB": []}

    # Buoi da xep o Giai doan 1: dong bang (interval co dinh), dua vao CA HAI rang
    # buoc - phong (Cumulative) VA khong-trung-gio theo tung GIANG VIEN.
    #
    # Truoc day chi dua vao rang buoc phong. Khong ai thay lo do vi mot GV co huu
    # khong the co lop o GD1: loai lop = loai cua GV chinh. Nhung tu khi loai lop
    # tinh theo CA NHOM (app._loai_lop: nhom co mot khach moi -> ca lop di GD1),
    # mot GV CO HUU co the co lop o GD1 va lop khac o GD2 -> GD2 khong biet gio cua
    # ho da bi chiem -> xep chong nhau. Do tren HK2: 2 GV nam o ca hai giai doan,
    # va co lan chay ra dung 1 o chong nhau (solver co nhieu loi giai toi uu nen
    # khong phai lan nao cung tro).
    # HOC CHUNG o Giai doan 1: chi dong bang DAI DIEN. Neu dong bang ca nhom thi
    # hai interval CO DINH trung khit nhau (cung slot, cung GV) cung vao
    # AddNoOverlap cua nguoi do -> mo hinh INFEASIBLE ngay, Giai doan 2 mat trang
    # ket qua. Phong cung vay: mot buoi chi ton mot phong.
    dai_dien = dai_dien_hoc_chung(data)
    for g in frozen_guest_lessons:
        dd = dai_dien.get(g["id"])
        if dd is not None and dd != g["id"]:
            continue
        iv = model.NewFixedSizeIntervalVar(
            g["slot"], g.get("duration", p["duration"]), f"frozen_{g['id']}")
        intervals_by_roomtype[g["roomType"]].append(iv)
        # Dai dien mang theo GV cua CA NHOM hoc chung (buoi do co mat ca ho).
        gv = set(g.get("teacherIds") or [g["teacherId"]])
        if dd is not None:
            for sid in next((x for x in cac_nhom_hoc_chung(data) if x[0] == dd), []):
                s2 = data["sections"].get(sid) or {}
                gv.update(s2.get("teacher_ids") or ([s2["teacher_id"]] if s2 else []))
        for tid in gv:
            intervals_by_teacher.setdefault(tid, []).append(iv)

    on_day_by_section = {}  # sid -> [bool theo ngay] - dung cho muc tieu dan ngay (phu)
    pending_ids = set(data.get("pending_section_ids") or [])
    # Buoi Giai doan 1 la CO DINH voi pha nay - xem _rang_buoc_nhom_sinh_vien.
    co_dinh_sv = {
        sid: (slot, (data["sections"].get(sid) or {}).get("duration", p["duration"]))
        for sid, slot in (gio_lop_pha_khac or {}).items() if slot is not None
    }
    co_dinh_sv.update({g["id"]: (g["slot"], g.get("duration", p["duration"]))
                       for g in frozen_guest_lessons})
    bien_sv = {}

    # Hop GV cua tung nhom hoc chung o pha nay - dai dien mang theo ca nhom (xem
    # solve_guest_phase, cung mot ly le).
    gv_cua_nhom = {}
    for s in resident_sections:
        dd = dai_dien.get(s["id"])
        if dd is not None:
            gv_cua_nhom.setdefault(dd, set()).update(s.get("teacher_ids") or [s["teacher_id"]])

    for s in resident_sections:
        sid = s["id"]
        own_valid_starts = valid_starts(p["numDays"], p["slotsPerDay"], s["duration"], "RESIDENT")
        cam = forbidden.get(sid, [])

        # Gio DA CHOT (doc tu file ke hoach giang day, hoac giao vu go tay vao form)
        # -> GHIM dung o do, khong phai chon lai.
        #
        # Truoc day cho nay luon dung own_valid_starts, tuc GD2 xep lai tu dau moi
        # lop co huu: do tren file HK1 2026-2027-2, 139/140 lop co gio chot bi xep
        # sang gio khac (VJU2031 file ghi Thu 2 tiet 6 -> he thong xep Thu 3 tiet 1).
        # Mot dong trong file la mot lop GV va dieu phoi vien da thong nhat gio voi
        # nhau, he thong khong co quyen doi.
        #
        # Ghim bang cach thu hep DOMAIN chu khong AddHint: interval van la Optional
        # nen neu o do bi trung (file co dong nhap trung) thi lop roi vao "khong xep
        # duoc" kem ly do - thay vi lam ca bai toan vo nghiem, cung khong am tham
        # doi gio da chot.
        # `bo_ghim` la CHO DUY NHAT go duoc ghim nay: giao vu phai noi ro y minh
        # bang mot cu bam, khong co duong nao khac lam gio trong file tu troi di.
        ghim_theo_file = (s.get("original_slot")
                          if not s.get("time_assumed") and sid not in bo_ghim else None)

        # Khung gio GV DA KHAI cho lop nay (domain/time_rules.py:
        # apply_section_time da giao khung cua ca nhom va loc theo do dai buoi).
        # Rong = chua ai khai -> tu do.
        #
        # Truoc day Giai doan 2 KHONG doc submissions: co huu luon tu do ca tuan
        # (Thu 2-Thu 6), nen khai gio ranh cho co huu la vo tac dung. Nay khai roi
        # thi GIOI HAN CUNG, dung nhu Giai doan 1 lam voi thinh giang.
        da_khai = data["submissions"].get(sid) or []
        # DA KHAI gio nhung khong con khung nao du dai cho lop nay: app.py de
        # submissions rong VA dua lop vao pending_section_ids. Phai phan biet voi
        # "chua ai khai" (cung submissions rong nhung KHONG trong pending) - neu
        # khong thi khai xong lai duoc tu do ca tuan, nguoc han y nghia.
        khai_nhung_het_cho = (not da_khai) and sid in pending_ids

        # KHOI CA HOC: chi ap cho cac nhanh ma HE THONG chon gio (khung da khai,
        # va mien tu do ca tuan). Hai nhanh GHIM di thang: gio do la quyet dinh
        # cua con nguoi, he thong khong co quyen doi - y het cach MAX_DAY_INDEX
        # chi ap cho lop chua co gio (xem domain/time_rules.py).
        khoi = khoi_ca_hoc(s)
        def _loc(ds):
            return loc_theo_khoi_buoi(ds, s["duration"], p["slotsPerDay"], khoi)

        if sid in (ghim_tay or {}):
            # Quyet dinh TAY o man TKB - moi nhat nen thang moi thu khac.
            domain_starts = [ghim_tay[sid]]
        elif cam:
            domain_starts = _loc([v for v in own_valid_starts if v not in cam])
        elif ghim_theo_file is not None:
            domain_starts = [ghim_theo_file]
        elif da_khai:
            domain_starts = _loc(list(da_khai))
        else:
            domain_starts = _loc(own_valid_starts)
        if not domain_starts:
            domain_starts = own_valid_starts  # an toan: neu cam het thi bo qua cam
        start = model.NewIntVarFromDomain(cp_model.Domain.FromValues(domain_starts), f"start_{sid}")
        is_placed = model.NewBoolVar(f"placed_{sid}")
        interval = model.NewOptionalFixedSizeIntervalVar(start, s["duration"], is_placed, f"iv_{sid}")

        # Ngay cua lesson nay = start // slotsPerDay - can 1 IntVar rieng (khong
        # phai bieu thuc) de dung lam dieu kien reify ben duoi.
        day_var = model.NewIntVar(0, p["numDays"] - 1, f"day_{sid}")
        model.AddDivisionEquality(day_var, start, p["slotsPerDay"])
        # b = "lop nay DA XEP va roi vao ngay d". Chi can implication mot chieu:
        #   b => (day_var == d) va b => is_placed
        # cong voi sum(b) == is_placed.
        #
        # KHONG duoc them chieu nguoc (day_var != d khi b sai): `start` luon co mot
        # gia tri cu the trong domain ke ca khi lop KHONG duoc xep, nen day_var luon
        # bang dung mot ngay -> ep sum(b) == 1 -> is_placed bi ep = 1 cho MOI lop.
        # Tuc Giai doan 2 khong he co khai niem "lop khong xep duoc": xep het thi
        # OPTIMAL, khong thi INFEASIBLE va MAT TRANG ket qua. Lo ra ngay khi bat dau
        # ghim gio da chot: HK2 tu 119/119 thanh INFEASIBLE 0/119 chi vi file co vai
        # dong nhap trung doi cung mot o cua cung mot nguoi.
        on_day_bools = []
        for d in range(p["numDays"]):
            b = model.NewBoolVar(f"onday_{sid}_{d}")
            model.Add(day_var == d).OnlyEnforceIf(b)
            model.AddImplication(b, is_placed)
            on_day_bools.append(b)
        model.Add(sum(on_day_bools) == is_placed)
        on_day_by_section[sid] = on_day_bools

        starts[sid] = start
        placed[sid] = is_placed
        bien_sv[sid] = (start, is_placed, s["duration"], domain_starts)
        if khai_nhung_het_cho:
            # Khong xep duoc THAT (khung da khai khong con cho) - de solver bao ra
            # thay vi am tham xep ra ngoai khung GV da khai.
            model.Add(is_placed == 0)
        dd = dai_dien.get(sid)
        if dd is not None and dd != sid:
            continue  # thanh vien hoc chung: xem khoi rang buoc o cuoi
        for tid in (gv_cua_nhom.get(sid) or s.get("teacher_ids") or [s["teacher_id"]]):
            intervals_by_teacher.setdefault(tid, []).append(interval)
        intervals_by_roomtype[s["room_type"]].append(interval)

    # Thanh vien nhom hoc chung: CUNG gio va CUNG so phan voi dai dien.
    for ds in cac_nhom_hoc_chung(data):
        rep = ds[0]
        if rep not in starts:
            continue  # nhom nay khong thuoc pha nay
        for sid in ds[1:]:
            if sid in starts:
                model.Add(starts[sid] == starts[rep])
                model.Add(placed[sid] == placed[rep])

    for ivs in intervals_by_teacher.values():
        if len(ivs) > 1:
            model.AddNoOverlap(ivs)

    for room_type in ("LT", "LAB"):
        pool = p["ltPool"] if room_type == "LT" else p["labPool"]
        ivs = intervals_by_roomtype[room_type]
        if ivs:
            model.AddCumulative(ivs, [1] * len(ivs), pool)

    # Muc tieu chinh: toi da hoa so buoi xep duoc (trong so lon, uu tien tuyet
    # doi). Muc tieu phu: giam tai cao nhat cua 1 ngay bat ky trong tuan - day
    # chinh la phan xu ly hien tuong "don het vao Thu 2" da phat hien truoc do.
    max_day_load = model.NewIntVar(0, len(resident_sections) + 1, "max_day_load_resident")
    for d in range(p["numDays"]):
        terms = [on_day_by_section[s["id"]][d] for s in resident_sections]
        if terms:
            model.Add(sum(terms) <= max_day_load)
    # GD2 da co san bool theo ngay cho tung lop (on_day_by_section) - dung lai luon.
    # Khu vuc CO DINH: cac buoi Giai doan 1 (frozen_guest_lessons) va lop co huu
    # ngoai pham vi da bi ghim - pha nay khong dat lai chung nhung van phai dem.
    kv_co_dinh = {}
    for g in frozen_guest_lessons:
        kv = khu_vuc(data["sections"].get(g["id"]) or {})
        if kv is None:
            continue
        ngay = g["slot"] // p["slotsPerDay"]
        for tid in (g.get("teacherIds") or [g["teacherId"]]):
            kv_co_dinh.setdefault((tid, ngay), set()).add(kv)
    vi_pham_kv, chuyen_di = _rang_buoc_khu_vuc(
        model, data, {sid: {d: [b] for d, b in enumerate(bs)}
                      for sid, bs in on_day_by_section.items()},
        kv_co_dinh, p["numDays"])

    vi_pham_sv = _rang_buoc_nhom_sinh_vien(model, cap_can_ne or {}, bien_sv, co_dinh_sv)

    trong_so = _trong_so_giu_cho(placed, uu_tien_giu)
    model.Maximize(_muc_tieu(
        model, len(resident_sections),
        dat_duoc=sum(trong_so[sid] * v for sid, v in placed.items()),
        vi_pham_kv=vi_pham_kv, max_day_load=max_day_load, vi_pham_sv=vi_pham_sv,
        chuyen_di=_theo_thu_tu_khu_vuc(chuyen_di)))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit_s
    solver.parameters.num_search_workers = CONFIG["solver"]["numSearchWorkers"]

    t0 = time.time()
    status = solver.Solve(model)
    elapsed = time.time() - t0

    lessons = []
    chua_xep = []
    for s in resident_sections:
        sid = s["id"]
        if solver.Value(placed[sid]) == 1:
            slot = solver.Value(starts[sid])
            day, period = divmod(slot, p["slotsPerDay"])
            lessons.append({
                "id": sid, "teacherId": s["teacher_id"], "teacherName": teacher_display(data, s["teacher_id"]),
                "teacherIds": list(s.get("teacher_ids") or [s["teacher_id"]]),  # dong giang day - xem GD1
                "courseName": s.get("course_name"), "program": s["program"],
                "programLabel": section_program_label(data, s),
                "programIds": section_program_ids(s),
                "programParts": section_program_names(data, s),
                "facultyName": section_faculty_name(data, s),
                            "roomType": s["room_type"], "day": day, "period": period,
                "location": s.get("location"), "khuVuc": khu_vuc(s),
                "slot": slot, "duration": s["duration"], "teacherType": "RESIDENT", "status": "DRAFT",
            })
        else:
            chua_xep.append(s)

    # Cac lop GD2 khong xep duoc - TRUOC DAY KHONG CO danh sach nay (xem chu thich
    # o cho tao on_day_bools: is_placed bi ep = 1 nen GD2 chi co "xep het" hoac
    # INFEASIBLE mat trang). Gio da xep duoc bao nhieu thi xep, phan con lai phai
    # noi ro LOP NAO va AI/CAI GI dang chiem cho - de giao vu sap lai.
    slot_da_xep = {l["id"]: l for l in lessons}
    frozen_by_id = {g["id"]: g for g in frozen_guest_lessons}
    unplaced = []
    for s in chua_xep:
        sid = s["id"]
        ghim = s.get("original_slot") if not s.get("time_assumed") else None
        tids = set(s.get("teacher_ids") or [s["teacher_id"]])
        # Cac o MA LOP NAY DUOC PHEP nam: gio da chot (1 o), hoac khung GV da khai.
        # Khong co gi ca (chua khai, khong chot) thi khong the chi ra "ai chiem cho"
        # - lop khong xep duoc vi het phong/qua tai, khong vi mot buoi cu the.
        o_cho_phep = [ghim] if ghim is not None else list(data["submissions"].get(sid) or [])
        blockers = []
        for l in list(slot_da_xep.values()) + list(frozen_by_id.values()):
            l_tids = set(l.get("teacherIds") or [l["teacherId"]])
            if not (tids & l_tids):
                continue
            if any(_giao_nhau(o, s["duration"], l["slot"], l["duration"]) for o in o_cho_phep):
                blockers.append({
                    "sectionId": l["id"], "courseName": l.get("courseName"),
                    "teacherName": l.get("teacherName"),
                    "slotLabel": slot_label(l["slot"], p["slotsPerDay"]),
                    "phase": "GD1" if l["id"] in frozen_by_id else "GD2",
                })
        unplaced.append({
            "id": sid, "teacherId": s["teacher_id"],
            "teacherName": teacher_display(data, s["teacher_id"]),
            "teacherIds": list(s.get("teacher_ids") or [s["teacher_id"]]),
            "courseName": s.get("course_name"), "program": s["program"],
            "programLabel": section_program_label(data, s),
            "programIds": section_program_ids(s),
            "programParts": section_program_names(data, s),
            "facultyName": section_faculty_name(data, s),
            "coordinator": ", ".join(section_coordinators(data, s)),
            "roomType": s["room_type"], "duration": s["duration"],
            "pinnedSlot": ghim,
            "pinnedLabel": slot_label(ghim, p["slotsPerDay"]) if ghim is not None else None,
            # PINNED_CONFLICT: co gio da chot nhung o do bi chiem (hay gap nhat la
            # file co hai dong nhap trung doi cung mot o cua cung mot nguoi).
            # NO_SLOT: khong co gio chot, khong con cho nao vua.
            "reason": "PINNED_CONFLICT" if ghim is not None else "NO_SLOT",
            "blockers": blockers,
        })

    return {
        "status": solver.StatusName(status),
        "elapsedSeconds": round(elapsed, 3),
        "total": len(resident_sections),
        "placedCount": len(lessons),
        "lessons": lessons,
        "unplaced": unplaced,
    }
