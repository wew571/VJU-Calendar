# -*- coding: utf-8 -*-
"""Quy tac NGHIEP VU xep thoi khoa bieu - khong biet gi ve Flask/HTTP.

Moi module o day chi doc/sua bo du lieu `data` (xem sections.empty_manual_data)
va STATE (state.py). Khong module nao import tu api/ - chieu phu thuoc luon la
api/ -> domain/, de doi mot quy tac nghiep vu khong phai mo tang route.

Thu tu phu thuoc trong noi bo domain/ (khong co vong tron):

    programs.py  availability.py     <- tang duoi, khong phu thuoc domain khac
         |            |
         |       time_rules.py       <- parse/ghi gio cho mot lop
         |         |    |    |
    sections.py  teachers.py  pinning.py  chot.py
         |            |
    merge.py     response.py
         |
    excel_rows.py                    <- tang tren, dung lai gan het cac module tren

Nhanh rieng cho LUOI va PHAM VI XEP (cung khong co vong tron):

    pinning.py -> luoi.py -> pham_vi.py
                     luoi.py    "buoi nay dang hien o o gio nao"
                     pham_vi.py "lop nao duoc phep di chuyen o lan giai nay"

    programs.py  bo_qua.py -> nhom_sinh_vien.py
                     "cap lop nao khong duoc chong gio vi cung nguoi hoc"
                     (CTDT x Khoa). api/solve.py truyen ket qua xuong
                     scheduler_core duoi dang `cap_can_ne` - mo hinh CP-SAT khong
                     biet gi ve CTDT/Khoa, chi biet "hai lop nay phai ne nhau".
                     Doc bo_qua.py vi lop do DON VI KHAC dieu phoi ma da co gio
                     cung chiem thoi gian cua sinh vien (bo_qua.van_len_luoi).

    bo_qua.py -> luoi.py
                     luoi.py con dat cac lop do len luoi (chung khong co trong
                     nghiem solver) de khong ai xep mon khac de vao.
"""
