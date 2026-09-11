# -*- coding: utf-8 -*-
"""KIEM TRA "XEP THEO PHAM VI" tren du lieu THAT dang co (manual_state_snapshot.json).

Chay:  py kiem_tra_pham_vi.py            (tu thu muc webapp/)
       py kiem_tra_pham_vi.py FTH VJU2026 VJU2025 VJU2024
       py kiem_tra_pham_vi.py --bo-chan FTH VJU2026 VJU2025 VJU2024

Tinh nang "xep cho rieng mot chuong trinh" (domain/pham_vi.py) hua DUNG BA dieu.
Ca ba deu la thu KHONG NHIN THAY tren giao dien - lich xep ra van dep, chi sai
khi doi chieu voi phan cua chuong trinh khac. Nen phai co mot cho do lai bang so:

  1. Lop NGOAI pham vi khong bi xe dich mot o nao.
  2. Khong PHAT SINH THEM cap trung gio giang vien nao (tru hoc chung). Do theo
     muc TANG THEM chu khong tuyet doi: du lieu that co the da co san trung gio
     tu gio chot trong file, lan giai nay khong chiu trach nhiem ve cai do.
  3. Khong o gio nao vuot pool phong (ltPool/labPool).

va mot dieu thu tu, khong phai loi hua ma la ranh gioi phai biet:

  4. Bao nhieu lop cua chuong trinh khac CHUA co gio o dau ca - chung chua thanh
     rang buoc that, nen den luot ho xep se phai ne minh chu khong nguoc lai.

KHONG ghi gi xuong dia: save_snapshot bi vo hieu ngay dau file.
"""

import sys

import snapshot
snapshot.save_snapshot = lambda *a, **k: None   # doc-only, khong dung du lieu that

import scheduler_core as sc
from domain import pham_vi as pv
from domain.time_rules import overlaps
from state import STATE


def _cac_buoi_dang_hien():
    g = STATE["guestResult"] or {"lessons": []}
    r = STATE["residentResult"] or {"lessons": []}
    return g["lessons"] + r["lessons"]


def trung_gio_giang_vien(data, lessons):
    """Cac cap buoi cung mot GV ma chong gio nhau. Hoc chung KHONG tinh: ca nhom
    la MOT buoi, chung PHAI o cung o gio (xem domain/hoc_chung.py)."""
    dai_dien = sc.dai_dien_hoc_chung(data)
    theo_gv = {}
    for l in lessons:
        for tid in (l.get("teacherIds") or [l["teacherId"]]):
            theo_gv.setdefault(tid, []).append(l)

    xung = []
    for tid, ds in theo_gv.items():
        for i in range(len(ds)):
            for j in range(i + 1, len(ds)):
                a, b = ds[i], ds[j]
                if dai_dien.get(a["id"]) is not None and dai_dien.get(a["id"]) == dai_dien.get(b["id"]):
                    continue
                if overlaps(a["slot"], a["duration"], b["slot"], b["duration"]):
                    xung.append((tid, a["id"], b["id"]))
    return xung


def vuot_pool_phong(data, lessons):
    """O gio nao dang can nhieu phong hon so phong dang co."""
    p = data["params"]
    dai_dien = sc.dai_dien_hoc_chung(data)
    qua_tai = []
    for loai, pool in (("LT", p["ltPool"]), ("LAB", p["labPool"])):
        for slot in range(p["numDays"] * p["slotsPerDay"]):
            dang_dung = {
                dai_dien.get(l["id"], l["id"])
                for l in lessons
                if l["roomType"] == loai and l["slot"] <= slot < l["slot"] + l["duration"]
            }
            if len(dang_dung) > pool:
                qua_tai.append((loai, slot, len(dang_dung), pool))
    return qua_tai


def chay(programs, cohorts, bo_chan=False):
    from app import app  # nap app => nap snapshot vao STATE

    if bo_chan:
        # Cong chan "con lop chua san sang" la hanh vi DUNG cua san pham, nhung
        # no chan luon ca viec do ba bat bien o duoi. Co nay de do duoc khi du
        # lieu chua sach - khong bao gio dung trong app that.
        sc.guest_sections_can_thu_gio = lambda data, chi_xet=None: []

    data = STATE["data"]
    if data is None:
        print("Chua co du lieu (manual_state_snapshot.json) - nap file Excel truoc.")
        return 1

    pham_vi = pv.chuan_hoa({"programs": programs, "cohorts": cohorts})
    trong = pv.sids_thuoc(data, pham_vi)
    gio_truoc = pv.gio_truoc_khi_giai(data)

    print(f"Pham vi : {pv.mo_ta(pham_vi)}")
    print(f"          {len(trong)} lop / {len(data['sections'])} lop toan khoa")
    print(f"          {pv.ngoai_pham_vi_chua_co_gio(data, trong, gio_truoc)} lop ngoai pham vi "
          "CHUA co gio (chua thanh rang buoc that)")
    print()

    # CHUP TRUOC KHI GIAI: du lieu that co the DA co san trung gio (gio chot trong
    # file va cac dong nhap trung), va cac nhom hoc chung co the da bi xoa sach sau
    # mot lan nap lai file - luc do hai lop "cung mot buoi" bi doc thanh trung gio.
    # Do tuyet doi se bao "khong dat" cho mot lich ma lan giai nay khong he lam
    # hong; cai can do la co PHAT SINH THEM khong.
    truoc_xung = set(map(tuple, trung_gio_giang_vien(data, _cac_buoi_dang_hien())))
    if truoc_xung:
        print(f"LUU Y: truoc khi giai da co san {len(truoc_xung)} cap trung gio giang vien")
        if not sc.cac_nhom_hoc_chung(data):
            print("       (va khong con nhom HOC CHUNG nao - kiem tra lai neu vua nap lai file:")
            print("        hai lop cung MOT buoi day ma mat danh dau se bi doc thanh trung gio)")
        print()

    c = app.test_client()
    for buoc, duong in (("Giai doan 1 (thinh giang)", "/api/solve-guest"),
                        ("Giai doan 2 (co huu)", "/api/solve-resident")):
        res = c.post(duong, json={"phamVi": {"programs": programs, "cohorts": cohorts}})
        body = res.get_json()
        if res.status_code != 200:
            print(f"{buoc}: BI CHAN - {body.get('error')}")
            print("    (them --bo-chan de bo qua cong chan nay va van do duoc ba bat bien)")
            return 1
        tv = body.get("phamVi") or {}
        print(f"{buoc}: {body['status']} {body['elapsedSeconds']}s")
        print(f"    pham vi: {tv.get('daXep')}/{tv.get('tong')} lop da co gio"
              f" (vua xep moi {tv.get('vuaXep')})"
              + (f" - {tv['khongXepDuoc']} khong xep duoc" if tv.get("khongXepDuoc") else ""))

    lessons = _cac_buoi_dang_hien()
    xe_dich = [l["id"] for l in lessons
               if l["id"] not in trong
               and gio_truoc.get(l["id"]) is not None
               and gio_truoc[l["id"]] != l["slot"]]
    xung = trung_gio_giang_vien(data, lessons)
    moi = [x for x in xung if tuple(x) not in truoc_xung]
    qua_tai = vuot_pool_phong(data, lessons)

    print()
    print(f"[1] Lop ngoai pham vi bi xe dich : {len(xe_dich)} {xe_dich[:8]}")
    print(f"[2] Cap trung gio giang vien MOI : {len(moi)} {moi[:5]}"
          + (f"   (co san tu truoc: {len(truoc_xung)})" if truoc_xung else ""))
    print(f"[3] O gio vuot pool phong        : {len(qua_tai)} {qua_tai[:5]}")
    print(f"    (tong {len(lessons)} buoi dang tren luoi)")

    hong = bool(xe_dich or moi or qua_tai)
    print()
    print("KHONG DAT - xem cac muc khac 0 o tren." if hong else "DAT ca ba.")
    return 1 if hong else 0


if __name__ == "__main__":
    # Doi so: <CTDT> [Khoa...]. Khong truyen gi -> lay dung pham vi dang can nhat.
    doi_so = sys.argv[1:]
    bo_chan = "--bo-chan" in doi_so
    doi_so = [x for x in doi_so if not x.startswith("--")]
    if doi_so:
        sys.exit(chay(doi_so[:1], doi_so[1:], bo_chan))
    sys.exit(chay(["FTH"], ["VJU2026", "VJU2025", "VJU2024"], bo_chan))
