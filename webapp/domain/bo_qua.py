# -*- coding: utf-8 -*-
"""BO QUA cac lop KHONG PHAI VIEC CUA KHOA.

File ke hoach giang day cua khoa liet ke ca nhung lop ma khoa KHONG xep: o giang
vien khong ghi ten nguoi ma ghi don vi dieu phoi - "Phong Dao tao dieu phoi",
"JLE dieu phoi". Do la mon chung (Triet hoc Mac-Lenin, Tu tuong Ho Chi Minh, Giao
duc the chat, tieng Nhat...) do don vi khac chiu trach nhiem xep gio; giao vu khoa
khong quan tam va khong duoc quyen xep.

Do tren du lieu that: 66 lop, trong do 55 la "thinh giang" - tuc chung chiem phan
lon danh sach "chua san sang" dang CHAN nut Giai. Giao vu buoc phai nhin 66 dong
khong lien quan, va khong bam giai duoc chung nao chua "xu ly" xong chung.

BO QUA CHU KHONG XOA: du lieu van la du lieu that trong file, con phai xuat lai
duoc va con phai bo danh dau duoc khi nham. Chi la mot co `bo_qua` tren section;
moi noi tinh toan doc co do ma bo qua, con bang du lieu thi an di nhung van cho
hien lai.

BO QUA KHONG CO NGHIA LA VO HINH. Lop do don vi khac dieu phoi ma DA CO GIO trong
file thi gio do la DU KIEN CO THAT: sinh vien khoa do cua chuong trinh do dang
ngoi hoc luc do. Neu giau no di thi giao vu xep mon khac vao dung o ay va sinh
vien khong hoc duoc ca hai - dung cai loi ma toan bo luat "nhom sinh vien" sinh ra
de tranh (xem domain/nhom_sinh_vien.py). Do tren du lieu that: 65/80 lop duoc de
xuat bo qua da co gio chot, phu kin 15 nhom (CTDT x Khoa), rieng BCSE/VJU2026 13 lop.

Nen "bo qua" chia lam hai muc, va van_len_luoi() la ranh gioi:
  - DA CO GIO   -> VAN hien tren luoi va VAN chiem cho cua nhom sinh vien, chi la
                   khoa khong duoc xep lai no (khong vao model CP-SAT, khong keo-tha).
  - CHUA CO GIO -> an han: chua ai xep thi khong co gi de ne.

KHONG tinh rang buoc GIANG VIEN cho chung: o giang vien cua chung ghi mot DON VI
("Phong Dao tao dieu phoi", "JLE dieu phoi") chu khong phai mot con nguoi - do
dung tren du lieu that, 65/65 lop deu vay. Bat chung vao AddNoOverlap la bao trung
gio giua hai cai cho trong.

KHAC HAN "chua phan cong": o trong / "(Chua phan cong)" nghia la KHOA VAN PHAI tim
giang vien roi xep - 6 lop trong du lieu that. Khong duoc gop hai thu lam mot,
gop la giao vu bo quen dung phan viec cua minh.
"""

import re

import scheduler_core as sc

# Dau hieu "don vi khac dieu phoi". CHI bat chu "dieu phoi" - KHONG dung
# fate_import._COORD_RE (no con bat "chua co"/"chua phan"/"tbd"/"n/a", tuc gom ca
# nhung lop khoa VAN PHAI xep vao day).
DIEU_PHOI_RE = re.compile(r"điều phối", re.IGNORECASE)


def _ten_cac_gv(data, s):
    return [(data["teachers"].get(t) or {}) for t in (s.get("teacher_ids") or [s["teacher_id"]])]


def la_don_vi_dieu_phoi(data, s):
    """Lop nay co o giang vien ghi mot DON VI DIEU PHOI (khong phai nguoi) khong?

    Doi HAI dieu kien: ten co chu "dieu phoi" VA ban ghi do la CHO TRONG
    (placeholder). File that co o ghi "TS. Ta Quang Ngoc (dieu phoi)" - la NGUOI
    THAT kem ghi chu, quet tho se bo oan ca mot lop cua khoa. fate_import da phan
    biet san bang hoc ham/hoc vi (xem _is_placeholder / _PERSON_TITLE_RE), nen o
    day chi viec dua vao ket qua do."""
    return any(gv.get("placeholder") and DIEU_PHOI_RE.search(gv.get("name") or "")
               for gv in _ten_cac_gv(data, s))


def ung_vien(data):
    """Cac section_id DUOC DE XUAT bo qua ma HIEN CHUA bo qua."""
    return sorted(sid for sid, s in data["sections"].items()
                  if not s.get("bo_qua") and la_don_vi_dieu_phoi(data, s))


def dang_bo_qua(data):
    return sorted(sid for sid, s in data["sections"].items() if s.get("bo_qua"))


def van_len_luoi(s):
    """Lop nay bi bo qua NHUNG da co gio chot -> van phai hien tren luoi va van
    chiem cho cua nhom sinh vien. Xem docstring dau file.

    Doc `original_slot` chu khong qua domain/luoi.slot_dang_hien: lop bo qua nam
    ngoai model nen khong co nghiem solver, va cung khong keo-tha duoc nen khong co
    override - `original_slot` la nguon duy nhat, hoi vong hon chi ton them mot
    duong phu thuoc."""
    return (bool(s.get("bo_qua")) and not s.get("time_assumed")
            and s.get("original_slot") is not None)


def gio_da_chot(data):
    """{section_id: slot} cua cac lop bo qua VAN len luoi - dau vao cho ca luoi
    (domain/luoi.py) lan rang buoc nhom sinh vien (domain/nhom_sinh_vien.py)."""
    return {sid: s["original_slot"] for sid, s in data["sections"].items()
            if van_len_luoi(s)}


def _lan_hoc_chung(data, sids):
    """Mot nhom hoc chung la MOT buoi day - bo qua nua nhom la vo nghia (solver ep
    ca nhom cung slot, ma mot nua lai khong con trong model). Mot thanh vien bi
    dong toi thi ca nhom di theo, dung nhu domain/pham_vi.py lam voi pham vi."""
    ra = set(sids)
    for ds in sc.cac_nhom_hoc_chung(data):
        if ra & set(ds):
            ra |= set(ds)
    return ra


def dat(data, section_ids, bo_qua=True):
    """Danh dau / bo danh dau. Tra ve danh sach sid THUC SU vua doi.

    Tra ve cai VUA DOI chu khong phai cai vua nhan: ben goi phai bao duoc "da bo
    qua them N lop" cho dung, ke ca khi nhom hoc chung keo them lop vao."""
    muon = _lan_hoc_chung(data, [int(x) for x in section_ids if int(x) in data["sections"]])
    da_doi = []
    for sid in sorted(muon):
        s = data["sections"][sid]
        if bool(s.get("bo_qua")) == bool(bo_qua):
            continue
        if bo_qua:
            s["bo_qua"] = True
        else:
            s.pop("bo_qua", None)
        da_doi.append(sid)
    return da_doi
