# -*- coding: utf-8 -*-
"""PHAM VI XEP: xep thoi khoa bieu cho RIENG mot chuong trinh dao tao (CTDT) +
cac khoa cua no, thay vi ca khoa mot luc.

VI SAO CAN: theo QUY-TRINH-NGHIEP-VU-XEP-TKB.md, mot khoa co nhieu CTDT, moi CTDT
co mot GDCT phu trach. Nut "Giai" cu chay tren TOAN BO sections nen khong ai xep
duoc phan cua rieng minh: bam Giai la ca khoa bi xep lai, ke ca nhung lop cua
chuong trinh khac da thong nhat xong voi giang vien.

VI SAO KHONG CHI LOC SECTIONS ROI GIAI: do tren du lieu that (FTH x VJU2026/2025/
2024, 33 lop) - bo han cac lop ngoai pham vi ra khoi model thi ra ngay 2 cap
TRUNG GIO GIANG VIEN khi ghep lai voi lich cua cac CTDT khac:
    GV#88  #208 FTH/VJU2024 tiet 52  <->  #297 FTH/VJU2023 tiet 53
    GV#29  #209 FTH/VJU2024 tiet 0   <->  #299 Chung "Ky thuat cam quan" tiet 1
10/24 giang vien cua pham vi FTH con day lop ngoai pham vi - bo lop ngoai ra la
solver khong con biet ho ban gio nao. Pool phong (ltPool/labPool) cung la tai
nguyen dung chung ca khoa, dem thieu la xep qua so phong that.

CACH LAM: KHONG cat bot model. Toan bo lop van vao CP-SAT nhu cu, pham vi chi
quyet dinh lop nao duoc PHEP DI CHUYEN:
    - lop TRONG pham vi   : tu do nhu thuong le
    - lop NGOAI pham vi   : GHIM CUNG vao dung o no dang hien tren luoi
Nho vay moi rang buoc cheo (NoOverlap theo GV, Cumulative theo phong, hoc chung)
van nguyen ven va tu dung, khong phai viet lai mot ban solver thu hai.

Ghim bang cach THU HEP MIEN, dung co che san co cua domain/pinning.py:
    Giai doan 1 (thinh giang)  submissions[sid] = [slot]   (tam thoi, tra lai sau)
    Giai doan 2 (co huu)       them vao dict ghim_tay
nen scheduler_core.py KHONG phai sua mot dong nao.

CHI GHI GIO CHO LOP THUOC PHAM VI: cac lop ngoai pham vi ma truoc luc giai CHUA
co gio o dau ca (khong ghim duoc) van nam trong model va van chiem cho GV/phong -
dung huong an toan - nhung vi tri solver bia ra cho chung bi BO DI o cuoi
(xem bo_gio_bia_them). Xep FTH khong duoc quyet ho gio cua BCSE.
"""

import contextlib

import scheduler_core as sc
from domain.luoi import slot_dang_hien
from domain.programs import KHOA_SPLIT_RE, tach_phan
from state import STATE


def chuan_hoa(raw):
    """Doc pham vi tu body request -> {"programs": [...], "cohorts": [...]} hoac
    None (= toan khoa, dung hanh vi cu).

    Rong ca hai ve cung tra None: "vua mo o chon chuong trinh nhung chua chon cai
    nao" phai la toan khoa chu khong phai "khong lop nao" - khong thi bam Giai ra
    0 lop ma khong hieu vi sao."""
    if not isinstance(raw, dict):
        return None

    def lam_sach(ds):
        return [x.strip() for x in (ds or []) if isinstance(x, str) and x.strip()]

    programs, cohorts = lam_sach(raw.get("programs")), lam_sach(raw.get("cohorts"))
    if not programs and not cohorts:
        return None
    return {"programs": programs, "cohorts": cohorts}


def mo_ta(pham_vi):
    """Nhan doc duoc de ghi vao thong bao/loi: 'FTH - VJU2026, VJU2025, VJU2024'."""
    if not pham_vi:
        return "toàn khoa"
    ve = []
    if pham_vi["programs"]:
        ve.append(", ".join(pham_vi["programs"]))
    if pham_vi["cohorts"]:
        ve.append(", ".join(pham_vi["cohorts"]))
    return " · ".join(ve)


def _phan_cua_lop(data, s):
    """(cac CTDT thanh phan, cac Khoa thanh phan) cua mot lop, chu thuong.

    Dung DUNG hai ham ma domain/response.py dung de sinh programParts/cohortParts
    cho giao dien - neu o day tinh kieu khac thi bo loc tren man hinh hien lop do
    la "cua FTH" ma solver lai khong coi no thuoc pham vi FTH (hoac nguoc lai),
    va khong ai giai thich noi tai sao."""
    ctdt = {t.lower() for t in sc.section_program_names(data, s)}
    khoa = {t.lower() for t in tach_phan(s.get("cohort"), KHOA_SPLIT_RE)}
    return ctdt, khoa


def lop_thuoc(data, s, pham_vi):
    """Lop nay co thuoc pham vi khong?

    O GHEP thuoc CA HAI ve: 'FTH.ESAS' la lop cua ca FTH lan ESAS nen xep FTH la
    phai xep no; 'VJU2024+VJU2023' thuoc ca hai khoa. Dung phep GIAO KHAC RONG,
    khong so khop nguyen chuoi (xem domain/programs.py: tach_phan).

    Hai ve VA voi nhau: chon FTH + khoa 2026/2025/2024 nghia la lop FTH cua ba
    khoa do, khong phai "moi lop FTH cong moi lop cua ba khoa do"."""
    if not pham_vi:
        return True
    ctdt, khoa = _phan_cua_lop(data, s)
    if pham_vi["programs"] and not (ctdt & {x.lower() for x in pham_vi["programs"]}):
        return False
    if pham_vi["cohorts"] and not (khoa & {x.lower() for x in pham_vi["cohorts"]}):
        return False
    return True


def sids_thuoc(data, pham_vi):
    """Tap section_id thuoc pham vi.

    HOC CHUNG lan CA NHOM: mot nhom hoc chung la MOT buoi day vat ly (xem
    domain/hoc_chung.py), khong the xep nua nhom. Du lieu that co nhom
    [#281 'Chung' - Hoc theo du an (FTH3006), #301 FTH/VJU2023]: chon pham vi FTH
    thi #281 phai vao theo, khong thi mot ben duoc solver xep con mot ben bi ghim
    cung cho cu -> nhom vo, hoac ca hai roi vao 'khong xep duoc'."""
    # Lop do don vi khac dieu phoi khong nam trong bai toan nao ca - khong phai
    # "trong pham vi", cung khong phai "ngoai pham vi can dong bang" (xem
    # domain/bo_qua.py). Loai han tu day de moi phep dem ben duoi deu dung.
    co_mat = {sid for sid, s in data["sections"].items() if sc.khoa_phai_xep(s)}
    if not pham_vi:
        return co_mat
    trong = {sid for sid in co_mat
             if lop_thuoc(data, data["sections"][sid], pham_vi)}
    for ds in sc.cac_nhom_hoc_chung(data):
        if trong & set(ds):
            trong |= set(ds)
    return trong


def gio_truoc_khi_giai(data):
    """{section_id: slot dang hien tren luoi} chup TRUOC khi giai - moc chung cho
    ca hai viec: ghim lop ngoai pham vi, va biet buoi nao la do chinh lan giai nay
    bia ra (bo_gio_bia_them).

    Chup MOT LAN, khong hoi lai giua chung: giai xong la STATE['guestResult'] da
    doi, hoi lai se ra so cua chinh lan giai nay chu khong phai moc truoc do."""
    return {sid: slot_dang_hien(data, sid)
            for sid, s in data["sections"].items() if sc.khoa_phai_xep(s)}


@contextlib.contextmanager
def ghim_ngoai_pham_vi(data, trong, gio_truoc):
    """GIAI DOAN 1: trong khoi `with`, moi lop THINH GIANG ngoai pham vi dang co
    gio bi thu hep khung gio ve DUNG mot slot - tuc bi ghim cung tai cho.

    Cung mot thu thuat ma domain/pinning.py: solve_guest_with_overrides dung cho
    ghim tay, va cung phai tra lai submissions nguyen ven sau do: khung gio giang
    vien da bao la du lieu THAT, pham vi chi la y kien cua lan giai nay.

    Lop ngoai pham vi CHUA co gio o dau ca thi khong ghim duoc - de nguyen tu do.
    No van chiem cho GV/phong trong model (huong AN TOAN: thieu rang buoc thi lich
    ra se trung), con vi tri no nhan duoc se bi bo o buoc bo_gio_bia_them."""
    goc = {}
    for sid, s in data["sections"].items():
        if sid in trong or s["teacher_type"] != "GUEST":
            continue
        slot = gio_truoc.get(sid)
        if slot is None:
            continue
        goc[sid] = data["submissions"].get(sid)
        data["submissions"][sid] = [slot]
    try:
        yield
    finally:
        for sid, cu in goc.items():
            if cu is None:
                data["submissions"].pop(sid, None)
            else:
                data["submissions"][sid] = cu


def ghim_tay_ngoai_pham_vi(data, trong, gio_truoc, ghim_tay):
    """GIAI DOAN 2: bo sung cac lop CO HUU ngoai pham vi vao dict `ghim_tay` ma
    solve_resident_phase nhan - no dat mien cua lop bang dung slot do.

    Khong sua `ghim_tay` goc (ghim tay cua giao vu) ma tra ve ban moi. Ghim TAY
    cua giao vu duoc uu tien (setdefault): ho vua noi ro y minh o man TKB, con
    ghim theo pham vi chi la "dung dong vao lop cua chuong trinh khac"."""
    ra = dict(ghim_tay or {})
    for sid, s in data["sections"].items():
        if sid in trong or s["teacher_type"] != "RESIDENT":
            continue
        slot = gio_truoc.get(sid)
        if slot is not None:
            ra.setdefault(sid, slot)
    return ra


def khong_duoc_hy_sinh(data, trong, gio_truoc, loai=None):
    """Cac lop NGOAI pham vi DANG CO CHO tren luoi - solver khong duoc bo chung ra
    de xep duoc them lop trong pham vi (xem scheduler_core._trong_so_giu_cho).

    Ghim chi thu hep MIEN, con interval van la Optional: khong danh dau them thi
    CP-SAT hoan toan co the hy sinh mot lop cua chuong trinh khac de doi lay mot
    lop cua pham vi - do duoc tren du lieu that khi mot lop FTH chi con dung mot
    khung gio trung voi lop ECE cua cung giang vien.

    `loai`: "GUEST"/"RESIDENT" - moi pha chi biet cac lop cua chinh no."""
    return {
        sid for sid, s in data["sections"].items()
        if sid not in trong
        and gio_truoc.get(sid) is not None
        and (loai is None or s["teacher_type"] == loai)
    }


def bo_gio_bia_them(result, trong, gio_truoc):
    """Bo khoi ket qua cac buoi NGOAI pham vi ma truoc luc giai chua co gio.

    Xep FTH khong duoc quyet ho gio cua BCSE. Nhung lop do van phai o trong model
    (de chiem cho GV/phong, xem ghim_ngoai_pham_vi) nen solver van tra ve mot vi
    tri cho chung - vi tri ay chi la GIA DINH cua lan giai nay, khong phai quyet
    dinh cua ai ca, nen khong duoc ghi len luoi.

    Bo di la AN TOAN mot chieu: den luot CTDT do xep, ho se thay lop cua pham vi
    nay da bi ghim cung nen phai ne - khong the sinh ra trung gio."""
    if not result:
        return result
    result["lessons"] = [l for l in result["lessons"]
                         if l["id"] in trong or gio_truoc.get(l["id"]) is not None]
    result["placedCount"] = len(result["lessons"])
    return result


def tom_tat(data, pham_vi, trong, result, loai, gio_truoc):
    """Con so cua RIENG pham vi de gan vao ket qua tra ve (khoa "phamVi").

    Vi sao khong dung `total`/`placedCount` co san: chung dem TOAN KHOA (model van
    la ca khoa) nen xep xong 33 lop FTH thi thanh tien trinh bao "166/166 da xep" -
    giao vu khong biet phan cua minh ra sao."""
    if not pham_vi:
        return None
    cua_pham_vi = [sid for sid in trong
                   if data["sections"].get(sid, {}).get("teacher_type") == loai]
    da_xep = {l["id"] for l in (result or {}).get("lessons") or []}
    khong_xep = [u for u in (result or {}).get("unplaced") or [] if u["id"] in trong]
    return {
        "moTa": mo_ta(pham_vi),
        "programs": pham_vi["programs"],
        "cohorts": pham_vi["cohorts"],
        "tong": len(cua_pham_vi),
        "daXep": sum(1 for sid in cua_pham_vi if sid in da_xep),
        "khongXepDuoc": len(khong_xep),
        # Lop cua pham vi vua duoc xep vao mot o MOI (truoc do chua o dau ca) -
        # con so noi len lan bam nay lam duoc gi, khac han "tong so lop da co gio".
        "vuaXep": sum(1 for sid in cua_pham_vi
                      if sid in da_xep and gio_truoc.get(sid) is None),
        "ngoaiPhamViChuaCoGio": ngoai_pham_vi_chua_co_gio(data, trong, gio_truoc),
        "dungChung": len(lop_dung_chung(data, pham_vi, cua_pham_vi)),
        "boGhimNgoaiPhamVi": bo_ghim_bi_pham_vi_giu_lai(data, trong),
        # CHOT TU KIEM CHUNG. Ca tinh nang nay chi hua duy nhat mot dieu: "xep cho
        # chuong trinh nay khong lam xe dich lop cua chuong trinh khac". Dem lai
        # tren chinh ket qua vua tra ve, thay vi tin rang co che ghim luon dung -
        # bang 0 o moi lan chay, khac 0 la co loi va giao dien phai keu len.
        "ngoaiPhamViBiDoiGio": _dem_ngoai_pham_vi_bi_doi_gio(result, trong, gio_truoc),
        # Lop cua chuong trinh khac DA CO CHO ma lan giai nay khong giu duoc (roi
        # vao "khong xep duoc"). Ghim la uu tien rat manh nhung KHONG tuyet doi -
        # interval van la Optional, doi lay viec khong bao gio vo nghiem. Xay ra
        # khi chinh cac gio dang co da xung dot san voi nhau.
        "ngoaiPhamViMatCho": [
            u["id"] for u in (result or {}).get("unplaced") or []
            if u["id"] not in trong and gio_truoc.get(u["id"]) is not None
        ],
        # Buoi cua chuong trinh khac ma solver buoc phai xep de len, vi chinh cac
        # gio dang co da xung dot san (vd file co dong nhap trung). Xem
        # scheduler_core.solve_guest_phase: dong_bang_hien_dien.
        "dongBangBiDay": list((result or {}).get("dongBangBiDay") or []),
    }


def _dem_ngoai_pham_vi_bi_doi_gio(result, trong, gio_truoc):
    """So buoi NGOAI pham vi dang o mot o KHAC voi luc truoc khi giai."""
    return sum(
        1 for l in (result or {}).get("lessons") or []
        if l["id"] not in trong
        and gio_truoc.get(l["id"]) is not None
        and gio_truoc[l["id"]] != l["slot"]
    )


def bo_ghim_bi_pham_vi_giu_lai(data, trong):
    """So lop da bam "Bo ghim" nhung nam NGOAI pham vi - lan giai nay VAN giu
    nguyen cho cua chung.

    Hai y muon nguoc nhau cua cung mot nguoi: "Bo ghim" = cho he thong xep lai lop
    NAY; chon pham vi = dung dong vao lop cua chuong trinh khac. Pham vi thang, vi
    hai kieu hong khong ngang nhau - bo qua mot cu bam Bo ghim thi kho hieu nhung
    vo hai, con am tham doi gio lop cua chuong trinh khac la pha dung cai ma tinh
    nang nay sinh ra de giu. Doi lai PHAI noi ra, khong duoc im lang."""
    return sum(1 for sid in STATE["bo_ghim"]
               if sid in data["sections"] and sid not in trong)


def lop_dung_chung(data, pham_vi, sids):
    """Cac lop trong pham vi ma o CTDT con ghi CA chuong trinh khac ("FTH.ESAS",
    "FTH+MJM") - tuc thuoc luon pham vi cua chuong trinh kia.

    Phai noi ra tren giao dien: den luot ESAS bam xep, nhung lop nay nam TRONG
    pham vi cua ho nen ho co quyen doi gio - khac han cac lop rieng cua FTH von
    duoc dong bang. Muon giu cung thi dung "Chot lich theo hoc phan" (domain/
    chot.py), do moi la cam ket khoa cung, con pham vi chi la "lan nay toi xep
    phan cua toi".

    Du lieu that: 23 lop toan khoa co o CTDT ghep, trong do 15 lop dinh toi FTH."""
    if not pham_vi or not pham_vi["programs"]:
        return []
    cua_toi = {x.lower() for x in pham_vi["programs"]}
    ra = []
    for sid in sids:
        s = data["sections"].get(sid)
        if s is None:
            continue
        ctdt = {t.lower() for t in sc.section_program_names(data, s)}
        if ctdt - cua_toi:
            ra.append(sid)
    return ra


def ngoai_pham_vi_chua_co_gio(data, trong, gio_truoc):
    """So lop NGOAI pham vi chua co gio o dau ca - CHUA ghim duoc nen chua thanh
    rang buoc that. Phai noi ra tren giao dien: lich vua xep chac chan khong dam
    vao nhung lop DA CO GIO cua chuong trinh khac, con cac lop chua ai xep thi den
    luot ho se phai ne minh - minh khong the ne truoc cai chua ton tai."""
    return sum(1 for sid in data["sections"]
               if sid not in trong and gio_truoc.get(sid) is None)
