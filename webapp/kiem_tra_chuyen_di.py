# -*- coding: utf-8 -*-
"""KIEM TRA "GOM CHUYEN DI CHO GIANG VIEN" tren du lieu THAT dang co
(manual_state_snapshot.json).

Chay:  py kiem_tra_chuyen_di.py            (tu thu muc webapp/)
       py kiem_tra_chuyen_di.py --giay 60  (noi gioi han thoi gian moi pha)

Muc 4 cua ham muc tieu (scheduler_core._muc_tieu) hua: moi giang vien phai len
tung co so trong IT NGAY nhat co the, Hoa Lac truoc roi den My Dinh. Day la thu
KHONG NHIN THAY tren luoi - lich xep ra van kin va van hop le, chi sai khi doc
theo HANG cua mot nguoi: ba buoi 2 tiet o Hoa Lac rai ra Thu 3/Thu 4/Thu 6 la ba
lan vuot 30km cho sau tiet, ma gom mot ngay van du cho.

Do bang cach GIAI HAI LAN tren cung du lieu - mot lan co muc 4, mot lan tat no
di (tai hien dung hanh vi truoc day) - roi so:

  1. Bat muc 4 KHONG duoc lam mat buoi nao. Muc 1 ("xep duoc nhieu nhat") dung
     tren, nen day phai la bat bien tuyet doi chu khong phai "thuong thi khong".
  2. So chuyen di Hoa Lac phai GIAM (hoac it nhat khong tang).
va BA muc BAO CAO, khong phai loi hua:

  3. Vi pham "1 giang vien 2 co so trong 1 ngay" (muc 3) tang hay giam.
     KHONG phai bat bien, du muc 3 nam TREN muc 4 trong thap tu dien. Thu tu tu
     dien chi dam bao TRONG MOT lan giai, con day la mot DAY CHUYEN hai pha: GD1
     xep thinh giang roi DONG BANG ket qua, GD2 moi ghep co huu vao cho con lai.
     Bat muc 4 lam GD1 doi cho cac buoi thinh giang de gom chuyen di, tuc GD2 nhan
     mot DAU VAO KHAC HAN - va nghiem toi uu cua no tren dau vao moi hoan toan co
     the xau hon o muc 3. Do tren du lieu that (nhieu dot, moi dot 5-6 lan chay):
     phan lon lan giu nguyen 1 vu, thinh thoang thanh 2 vu - ti le dao dong giua
     cac dot vi CP-SAT chay 8 luong nen khong tat dinh.
     Muon bien no thanh bat bien that su thi phai gop hai pha lam MOT mo hinh -
     mot viec khac han, va se mat cai gia da tra o Giai doan 2 (xem chu thich cho
     on_day_bools trong scheduler_core.py).

  4. Nhung giang vien VAN phai len Hoa Lac tu 3 ngay tro len sau khi giai - kem
     so lop da bi GHIM cung gio, tuc phan thuat toan khong con quyen dong. Con
     so do moi la viec cua giao vu (bam "Bo ghim"), khong phai loi cua solver.
  5. Tai cua ngay nang nhat - muc 5, nam DUOI muc 4 nen se nhinh len mot chut.
     Do la danh doi co chu y, khong phai hoi quy.

KHONG ghi gi xuong dia: save_snapshot bi vo hieu ngay dau file.
"""

import collections
import copy
import sys

import snapshot
snapshot.save_snapshot = lambda *a, **k: None   # doc-only, khong dung du lieu that

import scheduler_core as sc
from domain import nhom_sinh_vien as nsv
from state import STATE

NGAY = ["Thu 2", "Thu 3", "Thu 4", "Thu 5", "Thu 6", "Thu 7", "CN"]


def _giai(data, bat_muc_4, giay):
    """Chay ca hai pha. bat_muc_4=False tai hien hanh vi TRUOC khi co muc 4:
    _theo_thu_tu_khu_vuc tra ve rong -> _phat_chuyen_di khong tao muc nao, thap
    tu dien tut xuong dung bon muc cu."""
    data = copy.deepcopy(data)
    goc = sc._theo_thu_tu_khu_vuc
    if not bat_muc_4:
        sc._theo_thu_tu_khu_vuc = lambda chuyen_di: ()
    try:
        cap = nsv.cac_cap_can_ne(data)
        g = sc.solve_guest_phase(data, time_limit_s=giay, cap_can_ne=cap)
        r = sc.solve_resident_phase(data, g["lessons"], time_limit_s=giay, cap_can_ne=cap)
    finally:
        sc._theo_thu_tu_khu_vuc = goc
    return data, g["lessons"] + r["lessons"]


def chuyen_di(data, lessons):
    """{teacher_id: {khu_vuc: set(ngay)}} - mot ngay co mat o mot co so la MOT
    chuyen di, bao nhieu buoi trong ngay do cung the."""
    spd = data["params"]["slotsPerDay"]
    ra = collections.defaultdict(lambda: collections.defaultdict(set))
    for l in lessons:
        kv = sc.khu_vuc(data["sections"].get(l["id"]) or {})
        if kv is None:                     # o trong / Online - khong ai phai di
            continue
        for tid in (l.get("teacherIds") or [l["teacherId"]]):
            ra[tid][kv].add(l["slot"] // spd)
    return ra


def tong_theo_khu_vuc(tr):
    tong = collections.Counter()
    for kvs in tr.values():
        for kv, ngays in kvs.items():
            tong[kv] += len(ngays)
    return tong


def vi_pham_hai_co_so(tr):
    """Cac cap (GV, ngay) dinh ca hai co so - muc 3, phai khong tang."""
    theo_ngay = collections.defaultdict(set)
    for tid, kvs in tr.items():
        for kv, ngays in kvs.items():
            for ng in ngays:
                theo_ngay[(tid, ng)].add(kv)
    return {k for k, v in theo_ngay.items() if len(v) > 1}


def _bi_ghim(data, sid):
    """Lop nay co bi GHIM cung gio khong - tuc solver khong con quyen dong. Dung
    dung hai nguon ma solve_resident_phase dat mien theo (ghim tay o man TKB, va
    gio da chot trong file); xem chu thich `ghim_theo_file` o do."""
    if sid in STATE["bo_ghim"]:
        return False
    ov = STATE["overrides"].get(sid)
    if ov and ov.get("slot") is not None:
        return True
    s = data["sections"].get(sid) or {}
    return not s.get("time_assumed") and s.get("original_slot") is not None


def chay(giay=30):
    from app import app  # noqa: F401  - nap app => nap snapshot vao STATE

    data = STATE["data"]
    if data is None:
        print("Chua co du lieu (manual_state_snapshot.json) - nap file Excel truoc.")
        return 1

    # Cong chan "con lop chua san sang" nam o tang API; o day goi thang
    # scheduler_core nen khong vuong - va do cung dung y: cai can do la HAM MUC
    # TIEU, khong phai quy trinh nghiep vu.
    d_cu, cu = _giai(data, False, giay)
    d_moi, moi = _giai(data, True, giay)
    tr_cu, tr_moi = chuyen_di(d_cu, cu), chuyen_di(d_moi, moi)
    tong_cu, tong_moi = tong_theo_khu_vuc(tr_cu), tong_theo_khu_vuc(tr_moi)

    print(f"So lop tren luoi   : {len(cu)} (khong muc 4)  ->  {len(moi)} (co muc 4)")
    print("So (GV, ngay) phai den tung co so:")
    for kv in list(sc.THU_TU_KHU_VUC) + sorted(set(tong_moi) - set(sc.THU_TU_KHU_VUC)):
        if not (tong_cu[kv] or tong_moi[kv]):
            continue
        chenh = tong_moi[kv] - tong_cu[kv]
        print(f"    {kv:<10} {tong_cu[kv]:>4}  ->  {tong_moi[kv]:>4}"
              f"   ({chenh:+d}{'' if not tong_cu[kv] else f', {chenh / tong_cu[kv] * 100:+.0f}%'})")

    hai_cs_cu, hai_cs_moi = vi_pham_hai_co_so(tr_cu), vi_pham_hai_co_so(tr_moi)
    # So theo SO LUONG chu khong theo TAP HOP. Muc 3 (2 co so mot ngay) nam TREN
    # muc 4 trong thap tu dien, nen gia tri toi uu cua no khong doi khi bat muc 4
    # - nhung CAP (GV, ngay) nao vi pham thi duoc phep hoan doi tu do giua hai
    # nghiem cung toi uu. Truoc day cho nay lay hieu hai tap nen mot cu hoan doi
    # (cap A ra, cap B vao) bi bao thanh "phat sinh them", va phep kiem truot
    # ngau nhien 1/5 lan du khong co gi hong.
    hoan_doi = sorted(hai_cs_moi - hai_cs_cu)

    chinh = sc.THU_TU_KHU_VUC[0]
    mat_buoi = len(cu) - len(moi)
    them_hai_cs = len(hai_cs_moi) - len(hai_cs_cu)
    print()
    print(f"[1] Buoi bi mat khi bat muc 4      : {max(0, mat_buoi)}")
    print(f"[2] Chuyen di '{chinh}' tang them   : {max(0, tong_moi[chinh] - tong_cu[chinh])}")
    print(f"[3] Vi pham 2 co so tang them      : {max(0, them_hai_cs)}"
          f"   ({len(hai_cs_cu)} -> {len(hai_cs_moi)}"
          + (f", hoan doi sang cap khac: {hoan_doi[:3]}" if hoan_doi else "") + ")")

    # [4] Ai VAN phai di nhieu - va bao nhieu phan trong do la lop da bi ghim.
    con_nang = []
    for tid, kvs in tr_moi.items():
        ngays = kvs.get(chinh) or set()
        if len(ngays) < 3:
            continue
        cua_gv = [l for l in moi
                  if tid in (l.get("teacherIds") or [l["teacherId"]])
                  and sc.khu_vuc(d_moi["sections"].get(l["id"]) or {}) == chinh]
        ghim = sum(1 for l in cua_gv if _bi_ghim(d_moi, l["id"]))
        con_nang.append((len(ngays), tid, len(cua_gv), ghim, sorted(ngays)))
    print()
    print(f"[4] GV van phai len '{chinh}' >= 3 ngay/tuan: {len(con_nang)}")
    for n, tid, so_lop, ghim, ngays in sorted(con_nang, reverse=True):
        ten = (d_moi["teachers"].get(tid) or {}).get("name", f"GV#{tid}")
        print(f"      {ten:<24} {n} ngay ({', '.join(NGAY[x] for x in ngays)})"
              f" - {so_lop} lop, {ghim} lop DA GHIM"
              + ("  <- thuat toan khong con quyen dong" if ghim >= so_lop - 1 else ""))
    if con_nang:
        print("      Ghim = gio chot trong file hoac giao vu keo-tha. Muon gom them")
        print("      thi bam 'Bo ghim' cho cac lop do roi giai lai.")

    spd = d_moi["params"]["slotsPerDay"]
    tai_cu = collections.Counter(l["slot"] // spd for l in cu)
    tai_moi = collections.Counter(l["slot"] // spd for l in moi)
    print()
    print(f"[5] Tai cua ngay nang nhat         : {max(tai_cu.values())}"
          f"  ->  {max(tai_moi.values())}   (muc 5, nam duoi muc 4 - nhinh len la dung)")

    # [3] KHONG vao dieu kien dat/khong dat - xem docstring dau file: day chuyen
    # HAI PHA khong bao toan duoc no. Van in ra de theo doi: tang bat thuong thi
    # con nguoi con nhin thay.
    hong = mat_buoi > 0 or tong_moi[chinh] > tong_cu[chinh]
    print()
    print("KHONG DAT - xem muc [1]/[2] khac 0 o tren." if hong else "DAT ca hai bat bien.")
    return 1 if hong else 0


if __name__ == "__main__":
    doi_so = sys.argv[1:]
    giay = 30
    if "--giay" in doi_so:
        giay = int(doi_so[doi_so.index("--giay") + 1])
    sys.exit(chay(giay))
