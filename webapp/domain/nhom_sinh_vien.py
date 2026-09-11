# -*- coding: utf-8 -*-
"""NHOM SINH VIEN = (CTDT, Khoa): "FTH khoa VJU2024" la MOT nhom nguoi hoc, va
mot nguoi khong the ngoi hai lop cung mot luc.

VI SAO CAN: mo hinh cu chi biet ba loai tai nguyen - GIANG VIEN (mot nguoi mot
buoi), PHONG (ltPool/labPool), va KHU VUC (khong day hai co so trong mot ngay).
Khong cho nao noi ve NGUOI HOC. Nen lich xep ra "khong trung" theo nghia cua he
thong van co the la lich ma sinh vien FTH khoa 2023 phai co mat o hai giang duong
cung tiet - do tren gio da chot trong file: 25 cap nhu vay o 12 nhom.

VI SAO LA (CTDT, Khoa) CHU KHONG PHAI RIENG KHOA: "VJU2024" khong phai mot lop
nguoi hoc - sinh vien BCSE khoa 2024 va sinh vien FTH khoa 2024 hoc hai chuong
trinh khac han, hai lop cua ho trung gio la chuyen binh thuong. Loc theo rieng
Khoa se bao hang loat vu trung khong co that; phai giao CA HAI ve moi ra dung mot
tap nguoi.

O GHEP thuoc CA HAI ve, y het domain/pham_vi.py: lop "FTH.ESAS" la lop cua nhom
FTH lan nhom ESAS (sinh vien ca hai chuong trinh cung ngoi do), "VJU2024+VJU2023"
thuoc ca hai khoa. Nen mot lop co the nam trong NHIEU nhom.

BA TRUONG HOP CUNG GIO LA DUNG Y, khong duoc bao:
  - HOC CHUNG (domain/hoc_chung.py): ca nhom la MOT buoi day vat ly, chung PHAI
    o cung o gio.
  - LOP SONG SONG cua cung mot HOC PHAN ("Xac suat - Thong ke" chia CSE3013-1 va
    CSE3013-2): sinh vien chia doi, moi nguoi hoc mot lop, trung gio la binh thuong.
  - LOP TRUC TUYEN (o "Hinh thuc" ghi truc tuyen/online): mon linh dong, o tren
    thoi khoa bieu chi de co trong danh sach dang ky chu khong phai mot buoi hoc
    co dinh. Sinh vien tu thu xep duoc nen no khong chiem cho cua mon nao.

GIOI HAN DA BIET: hai hoc phan ma sinh vien chi hoc MOT trong hai (file that:
"Tieng Nhat so cap 1" va "Tieng Nhat so cap 2" xep cung tiet cho cung mot khoa)
van bi bao la trung - he thong khong co cach nao biet dieu do tu du lieu. Bao ra
de con nguoi doc va bo qua, thay vi im lang bo sot cac vu that.

Ban SONG SINH o giao dien: frontend/src/adapters/nhomSinhVien.js - cung mot luat,
lech nhau la hop thu bao mot dang con solver ne mot dang khac.
"""

import scheduler_core as sc
from domain import bo_qua
from domain.programs import KHOA_SPLIT_RE, tach_phan


def nhom_cua_lop(data, s):
    """Cac nhom sinh vien cua mot lop -> [(ctdt, khoa)], chu thuong.

    RONG khi lop khong ghi Khoa: khong biet no cua ai thi khong ket luan gi ca -
    xem lop_chua_ghi_khoa(). Doan bua ("chac la khoa moi nhat") se sinh ra ca
    dong vu trung khong co that.

    Dung DUNG hai ham ma domain/response.py dung de sinh programParts/cohortParts
    cho giao dien, ly le nhu domain/pham_vi.py: man hinh loc ra lop nao thi solver
    phai coi lop do thuoc dung nhom ay."""
    khoa = [k.lower() for k in tach_phan(s.get("cohort"), KHOA_SPLIT_RE)]
    if not khoa:
        return []
    ctdt = [t.lower() for t in sc.section_program_names(data, s)]
    return [(c, k) for c in ctdt for k in khoa]


def nhan(nhom):
    """Nhan doc duoc cua mot nhom: ('fth', 'vju2023') -> 'FTH/VJU2023'."""
    return f"{nhom[0].upper()}/{nhom[1].upper()}"


def chiem_gio_cua_sinh_vien(data, s):
    """Lop nay co chiem thoi gian cua sinh vien khong?

    KHOA PHAI XEP -> dĩ nhiên có. Nhưng CA lop do DON VI KHAC dieu phoi ma DA CO
    GIO cung chiem: "Triet hoc Mac-Lenin" do Phong Dao tao xep Thu 2 tiet 2-5 cho
    BCSE/VJU2026 thi sinh vien khoa do dang ngoi hoc that, khoa khong duoc xep mon
    khac vao dung o ay. Do la ly do duy nhat chung phai co mat o day - chung KHONG
    vao model CP-SAT va KHONG tinh trung giang vien (xem domain/bo_qua.py).

    Lop bo qua CHUA co gio thi khong: chua ai xep thi khong co gi de ne."""
    return sc.khoa_phai_xep(s) or bo_qua.van_len_luoi(s)


def lop_chua_ghi_khoa(data):
    """Cac lop khong quy duoc ve nhom nao vi o Khoa bo trong.

    PHAI dem va noi ra tren giao dien: chung khong bi kiem, nen "0 vu trung" chi
    dung voi phan da ghi du Khoa. Im lang thi giao vu doc thanh "ca khoa sach"."""
    return [sid for sid, s in data["sections"].items()
            if chiem_gio_cua_sinh_vien(data, s) and not nhom_cua_lop(data, s)]


def cac_nhom(data, chi_xet=None):
    """{nhom: [section_id]} - dung cho ca rang buoc solver lan viec dem tren man.

    `chi_xet`: gioi han o mot tap section_id (vd rieng mot pha giai)."""
    ra = {}
    for sid, s in data["sections"].items():
        if not chiem_gio_cua_sinh_vien(data, s) or (chi_xet is not None and sid not in chi_xet):
            continue
        for g in nhom_cua_lop(data, s):
            ra.setdefault(g, []).append(sid)
    return ra


def gio_lop_khong_xep(data):
    """{section_id: slot} cua cac lop DON VI KHAC dieu phoi da co gio.

    Solver phai nhan chung duoi dang VAT CAN CO DINH (`gio_lop_pha_khac`): chung
    khong co bien trong model - khoa khong duoc dat lai gio cua chung - nhung lop
    cua khoa phai ne ra."""
    return bo_qua.gio_da_chot(data)


def hoc_truc_tuyen(s):
    """Lop nay hoc TRUC TUYEN - khong phai mot buoi hoc co dinh o mot cho, nen no
    khong giu chan sinh vien va khong chiem gio cua mon nao.

    Doc o "Hinh thuc" (cot Excel "Hinh thuc giang day").

    "LMS" KHONG duoc mien, du truoc day co. Giao vu da xac nhan: mon ghi LMS van
    la buoi hoc that, sinh vien phai co mat dung gio do. Truoc khi sua, "Tieng Anh
    B1 (LMS)" (Hinh thuc = "LMS") duoc coi la linh dong nen he thong tu do xep mon
    khac de len: tren du lieu that, "Khoa hoc toan cau va moi truong" (VJU2012-1,
    FTH/VJU2026) bi xep dung Thu 4 tiet 2-5 - trung khit lop Tieng Anh B1 cua CUNG
    nhom sinh vien do. Mien LMS go bo 175 cap khoi rang buoc.

    Con "Truc tuyen"/"Online" thi van mien: do la mon linh dong that, len thoi khoa
    bieu chi de co trong danh sach dang ky.

    "Online
Truc tiep" thi KHONG tinh: lop do CO buoi hoc that tai lop, sinh vien
    van phai co mat. Co "truc tiep" trong o la du de khong mien - huong sai an toan
    (bao thua mot vu de nguoi doc bo qua, con hon giau mat mot vu that)."""
    t = sc.bo_dau(s.get("teaching_mode"))
    if not t or "truc tiep" in t:
        return False
    return "truc tuyen" in t or "online" in t


def cung_gio_la_dung_y(data, sid_a, sid_b):
    """Hai lop nay cung gio thi KHONG phai loi - xem docstring dau file."""
    if sc.cung_nhom_hoc_chung(data, sid_a, sid_b):
        return True
    a, b = data["sections"].get(sid_a) or {}, data["sections"].get(sid_b) or {}
    # CHI MOT BEN truc tuyen la du: mon linh dong khong giu chan sinh vien o dau
    # ca, nen mon con lai muon xep vao gio do cung khong ai vuong.
    if hoc_truc_tuyen(a) or hoc_truc_tuyen(b):
        return True
    ma, mb = a.get("course_id"), b.get("course_id")
    return ma is not None and ma == mb


def cac_cap_can_ne(data, chi_xet=None):
    """Moi cap lop (a, b) ma sinh vien khong the hoc ca hai neu chung cung gio,
    kem nhan nhom de giai thich. Moi cap CHI RA MOT LAN du hai lop chung nhieu
    nhom (lop "FTH.ESAS" khoa 2023 chung ca hai nhom voi lop FTH.ESAS khac).

    Day la DAU VAO cua rang buoc mem trong scheduler_core - o do khong biet gi ve
    CTDT/Khoa, chi nhan "nhung cap nay khong duoc chong gio"."""
    ra = {}
    for g, sids in cac_nhom(data, chi_xet).items():
        ds = sorted(sids)
        for i in range(len(ds)):
            for j in range(i + 1, len(ds)):
                cap = (ds[i], ds[j])
                if cap in ra or cung_gio_la_dung_y(data, *cap):
                    continue
                ra[cap] = nhan(g)
    return ra


def cac_vu_trung(data, vi_tri, chi_xet=None):
    """Cac vu trung THAT SU tren mot bo vi tri dang co.

    `vi_tri`: {section_id: slot} - buoi nao dang nam o o nao (None/thieu = chua
    co cho, khong ket luan gi).

    Tra ve [{"nhom", "a", "b", "slot"}], sap xep on dinh de goi lai hai lan ra
    cung mot thu tu."""
    ra = []
    for (a, b), ten in sorted(cac_cap_can_ne(data, chi_xet).items()):
        sa, sb = vi_tri.get(a), vi_tri.get(b)
        if sa is None or sb is None:
            continue
        da = data["sections"][a]["duration"]
        db = data["sections"][b]["duration"]
        if not (sa + da <= sb or sb + db <= sa):
            ra.append({"nhom": ten, "a": a, "b": b, "slot": min(sa, sb)})
    return ra
