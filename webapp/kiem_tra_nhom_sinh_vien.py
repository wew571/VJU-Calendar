# -*- coding: utf-8 -*-
"""KIEM TRA "KHONG TRUNG LICH SINH VIEN" tren du lieu THAT dang co
(manual_state_snapshot.json).

Chay:  py kiem_tra_nhom_sinh_vien.py                (co rang buoc - mac dinh)
       py kiem_tra_nhom_sinh_vien.py --doi-chung    (chay ca ban TAT rang buoc de so)
       py kiem_tra_nhom_sinh_vien.py --bo-chan      (do duoc ca khi du lieu chua sach)

Mot NHOM SINH VIEN la mot cap (CTDT, Khoa) - vd "FTH/VJU2023" - va mot nguoi
khong the ngoi hai lop cung mot luc. Rang buoc nay la MEM (xem
scheduler_core._rang_buoc_nhom_sinh_vien) nen khong the bao "bang 0 la dat":
gio da chot trong file von da co san mot so vu trung, solver khong duoc phep doi
gio do. Cai do duoc o day la muc TANG THEM:

  1. Sau khi giai co PHAT SINH THEM vu trung nao TRANH DUOC khong (phai bang 0).
     "Tranh duoc" = lop ma solver vua dat con it nhat MOT khung gio khac khong dam
     vao lop nao cung nhom. Khong con khung nao thi do la be tac cua du lieu (giang
     vien khai qua it gio, hoac lop cung nhom da chot kin tuan) - bao ra de con
     nguoi xu ly, khong tinh la loi cua lan giai.
  2. Cac vu con lai co phai deu la gio CHOT SAN trong file khong - tuc lan giai
     nay khong go duoc chu khong phai no gay ra.
  3. Bao nhieu lop chua ghi cot Khoa - phan KHONG duoc kiem, phai noi ra chu
     khong de con so "0 vu" bi doc thanh "ca khoa sach".

--doi-chung chay them mot lan voi cap_can_ne rong (dung mo hinh cu) de thay rang
buoc that su co tac dung - khong thi mot bug lam no im lang van "dat".

KHONG ghi gi xuong dia: save_snapshot bi vo hieu ngay dau file.
"""

import sys

# Console Windows mac dinh la cp1252/cp437 - in ten hoc phan tieng Viet ra la
# UnicodeEncodeError va bao cao chet giua chung. Ep UTF-8, thay ky tu khong hien
# duoc bang "?" thay vi dung han.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, OSError):
    pass

import snapshot
snapshot.save_snapshot = lambda *a, **k: None   # doc-only, khong dung du lieu that

import scheduler_core as sc
from domain import nhom_sinh_vien as nsv
from state import STATE


def _cac_buoi_dang_hien():
    g = STATE["guestResult"] or {"lessons": []}
    r = STATE["residentResult"] or {"lessons": []}
    return g["lessons"] + r["lessons"]


def _vi_tri_hien_tai(data):
    """{sid: slot} cua cac buoi DANG NAM tren luoi.

    Lay tu chinh ket qua giai chu khong tu domain/luoi.slot_dang_hien: lop KHONG
    XEP DUOC van con `original_slot` trong file nen slot_dang_hien tra ve mot o cho
    no, trong khi tren luoi khong he co buoi nao ca (no nam o tab "Chua xep duoc").
    Hai he qua neu lay nham:
      - dem ra nhieu vu hon dung so man hinh hien (frontend doc tu ket qua giai);
      - lech voi chinh MO HINH: rang buoc trong CP-SAT chi hieu luc khi lop duoc
        xep (OnlyEnforceIf ... placed), tuc lop khong xep duoc khong chiem cho ai.
    """
    return {l["id"]: l["slot"] for l in _cac_buoi_dang_hien() if l.get("slot") is not None}


def _khoa_vu(v):
    return (v["a"], v["b"])


def _in_vu(data, ds, gioi_han=12):
    p = data["params"]
    for v in ds[:gioi_han]:
        a, b = data["sections"][v["a"]], data["sections"][v["b"]]
        print(f"      {v['nhom']:<16} {str(a.get('class_code') or a['id']):<12}"
              f" {str(a.get('course_name'))[:26]:<26} <-> {str(b.get('class_code') or b['id']):<12}"
              f" {str(b.get('course_name'))[:26]:<26} {sc.slot_label(v['slot'], p['slotsPerDay'])}")
    if len(ds) > gioi_han:
        print(f"      ... va {len(ds) - gioi_han} vu nua")


def _con_duong_thoat(data, vu, vi_tri):
    """Vu trung nay LE RA tranh duoc khong?

    Xet tung ben ma solver duoc quyen dat (lop "de he thong tu xep"): trong cac
    khung gio no duoc phep nhan, co khung nao khong dam vao BAT KY lop nao cung
    nhom dang co cho khong. Co it nhat mot -> lan giai le ra da tranh duoc, tuc
    day la loi cua mo hinh chu khong phai cua du lieu.

    Xet tren vi tri CUOI CUNG cua cac lop khac (coi chung dung yen) - khong phai
    mot phep chung minh chat che (dich mot lop khac cung co the go duoc), nhung
    huong sai la AN TOAN: no chi bo sot vu tranh duoc, khong bao oan."""
    cap = nsv.cac_cap_can_ne(data)
    for ben in (vu["a"], vu["b"]):
        s = data["sections"][ben]
        if not s.get("time_assumed"):
            continue  # gio chot trong file - solver khong duoc dat lai
        khung = data["submissions"].get(ben) or sc.valid_starts(
            data["params"]["numDays"], data["params"]["slotsPerDay"],
            s["duration"], s["teacher_type"])
        cung_nhom = [(x, data["sections"][x]["duration"]) for x in data["sections"]
                     if x != ben and (min(x, ben), max(x, ben)) in cap
                     and vi_tri.get(x) is not None]
        for k in khung:
            if all(k + s["duration"] <= vi_tri[x] or vi_tri[x] + d <= k
                   for x, d in cung_nhom):
                return True
    return False


def chay(doi_chung=False, bo_chan=False):
    from app import app  # nap app => nap snapshot vao STATE

    if bo_chan:
        # Cong chan "con lop chua san sang" la hanh vi DUNG cua san pham, nhung no
        # chan luon ca viec do o day. Co nay de do duoc khi du lieu chua sach -
        # khong bao gio dung trong app that. Y het kiem_tra_pham_vi.py.
        sc.guest_sections_can_thu_gio = lambda data, chi_xet=None: []

    data = STATE["data"]
    if data is None:
        print("Chua co du lieu (manual_state_snapshot.json) - nap file Excel truoc.")
        return 1

    nhom = nsv.cac_nhom(data)
    chua_khoa = nsv.lop_chua_ghi_khoa(data)
    print(f"Du lieu : {len(data['sections'])} lop, {len(nhom)} nhom (CTDT x Khoa),"
          f" {len(nsv.cac_cap_can_ne(data))} cap phai ne nhau")
    print(f"          {len(chua_khoa)} lop CHUA ghi cot Khoa -> khong kiem duoc")
    print()

    truoc = nsv.cac_vu_trung(data, _vi_tri_hien_tai(data))
    print(f"TRUOC khi giai: {len(truoc)} vu trung lich sinh vien (gio dang co)")
    _in_vu(data, truoc)
    print()

    c = app.test_client()
    for buoc, duong in (("Giai doan 1 (thinh giang)", "/api/solve-guest"),
                        ("Giai doan 2 (co huu)", "/api/solve-resident")):
        res = c.post(duong, json={"phamVi": None})
        body = res.get_json()
        if res.status_code != 200:
            print(f"{buoc}: BI CHAN - {body.get('error')}")
            print("    (them --bo-chan de bo qua cong chan nay va van do duoc)")
            return 1
        print(f"{buoc}: {body['status']} {body['elapsedSeconds']}s"
              f" - {body['placedCount']}/{body['total']} buoi")

    sau = nsv.cac_vu_trung(data, _vi_tri_hien_tai(data))
    cu = {_khoa_vu(v) for v in truoc}
    moi = [v for v in sau if _khoa_vu(v) not in cu]

    # Vu con lai ma CA HAI lop deu la gio chot trong file - lan giai nay khong co
    # quyen doi, khong phai loi cua no.
    def chot(sid):
        s = data["sections"][sid]
        return not s.get("time_assumed") and s.get("original_slot") is not None
    bat_kha_khang = [v for v in sau if chot(v["a"]) and chot(v["b"])]

    vi_tri = _vi_tri_hien_tai(data)
    tranh_duoc = [v for v in moi if _con_duong_thoat(data, v, vi_tri)]
    be_tac = [v for v in moi if v not in tranh_duoc]

    print()
    print(f"SAU khi giai   : {len(sau)} vu trung lich sinh vien")
    print(f"[1] Vu phat sinh them, TRANH DUOC: {len(tranh_duoc)}")
    _in_vu(data, tranh_duoc)
    print(f"[2] Vu phat sinh them, BE TAC    : {len(be_tac)}"
          " (moi khung gio da khai deu dam vao lop cung nhom)")
    _in_vu(data, be_tac)
    print(f"[3] Vu ca hai ben da chot gio    : {len(bat_kha_khang)} (solver khong duoc doi)")
    print(f"[4] Lop chua ghi cot Khoa        : {len(chua_khoa)} (nam ngoai moi phep dem tren)")

    if doi_chung:
        print()
        print("--- DOI CHUNG: chay lai voi rang buoc TAT (mo hinh cu) ---")
        # Tat o CHINH mo hinh, khong tat o domain/nhom_sinh_vien.py: ham gom nhom
        # o do con la thuoc do de dem lai ket qua - tat no la do bang chinh cai
        # dang tat, ra "0 vu" cho moi truong hop.
        goc = sc._rang_buoc_nhom_sinh_vien
        sc._rang_buoc_nhom_sinh_vien = lambda *a, **k: []
        try:
            for duong in ("/api/solve-guest", "/api/solve-resident"):
                c.post(duong, json={"phamVi": None})
            khong_rb = nsv.cac_vu_trung(data, _vi_tri_hien_tai(data))
        finally:
            sc._rang_buoc_nhom_sinh_vien = goc
        print(f"    Khong rang buoc: {len(khong_rb)} vu  |  Co rang buoc: {len(sau)} vu")
        if len(khong_rb) <= len(sau):
            print("    CANH BAO: rang buoc khong lam giam vu nao - kiem tra lai duong truyen"
                  " cap_can_ne tu api/solve.py xuong scheduler_core.")

    print()
    print("KHONG DAT - lan giai nay tu sinh ra vu trung LE RA TRANH DUOC." if tranh_duoc else
          "DAT: khong phat sinh vu trung nao ma solver con duong tranh.")
    return 1 if tranh_duoc else 0


if __name__ == "__main__":
    sys.exit(chay("--doi-chung" in sys.argv[1:], "--bo-chan" in sys.argv[1:]))
