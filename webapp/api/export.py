# -*- coding: utf-8 -*-
"""XUAT ra .xlsx.

Hai duong, hai muc dich khac nhau:
    /api/manual/export       BANG DU LIEU HOC PHAN - khuon FATE 29 cot, nap lai
                             duoc o ky sau (round-trip). Xem fate_export.py.
    /api/manual/export-luoi  LUOI THOI KHOA BIEU - dung cai dang hien tren man
                             hinh, de in/gui di. Xem fate_export_luoi.py.

CA HAI deu xuat DUNG PHAN DANG HIEN theo bo loc cua man hinh, khong phai toan bo
du lieu: giao vu xep rieng cho mot chuong trinh thi file gui di cung phai la cua
rieng chuong trinh do. Cach lam: frontend gui kem danh sach dang hien
(`sectionIds`, hoac ca bo cuc luoi) - no la noi duy nhat biet chac man hinh dang
hien cai gi. Bat backend doan lai bo loc la mo duong cho hai ben lech nhau.
"""

from flask import Blueprint, jsonify, request, send_file

from api.common import can_du_lieu
from api.import_excel import XLSX_MIME
from domain.response import build_classes_list

import fate_export
import fate_export_luoi

bp = Blueprint("export", __name__)


def _ten_file(label, duoi=""):
    """FATE.TKB.<hoc ky>.xlsx - giu dung quy uoc dat ten cac file dang dung."""
    an_toan = "".join(c for c in (label or "TKB") if c not in '\\/:*?"<>|').strip() or "TKB"
    return f"FATE.TKB.{an_toan}{duoi}.xlsx"


def _loc_theo_section_ids(classes, section_ids):
    """Giu dung cac lop dang hien, THEO DUNG THU TU man hinh dang sap xep.

    None = khong loc (xuat het) - giu duong cu cho ban GET khong kem tham so."""
    if section_ids is None:
        return classes
    theo_id = {c["sectionId"]: c for c in classes}
    return [theo_id[sid] for sid in section_ids if sid in theo_id]


@bp.get("/api/manual/export")
@can_du_lieu
def api_manual_export(data):
    """Xuat TOAN BO bang 'Du lieu hoc phan' ra .xlsx.

    Giu lai duong GET khong tham so: no la duong tai file don gian nhat (dieu
    huong thang, khong can fetch) va van dung khi khong loc gi."""
    label = (request.args.get("label") or "").strip() or "TKB"
    buf = fate_export.build_workbook(build_classes_list(data), label)
    return send_file(buf, as_attachment=True,
                     download_name=_ten_file(label), mimetype=XLSX_MIME)


@bp.post("/api/manual/export")
@can_du_lieu
def api_manual_export_loc(data):
    """Xuat bang 'Du lieu hoc phan' CHI cac lop dang hien.

    Body: {"label": str, "sectionIds": [int] | null}

    `sectionIds` la danh sach man hinh dang hien sau khi loc (CTDT/Khoa/trang
    thai/tu khoa). Khong truyen = xuat het, y het duong GET."""
    body = request.get_json(silent=True) or {}
    label = (body.get("label") or "").strip() or "TKB"
    ids = body.get("sectionIds")
    if ids is not None and not isinstance(ids, list):
        return jsonify({"error": "sectionIds phải là danh sách."}), 400

    classes = _loc_theo_section_ids(build_classes_list(data),
                                    None if ids is None else [int(x) for x in ids])
    if not classes:
        return jsonify({"error": "Bộ lọc hiện tại không còn lớp nào để xuất."}), 400

    buf = fate_export.build_workbook(classes, label)
    return send_file(buf, as_attachment=True,
                     download_name=_ten_file(label), mimetype=XLSX_MIME)


@bp.post("/api/manual/export-luoi")
@can_du_lieu
def api_manual_export_luoi(data):
    """Xuat LUOI THOI KHOA BIEU dang hien ra .xlsx.

    Body la ban do luoi do frontend dung san (xem adapters/xuatLuoi.js:
    dungDuLieuXuatLuoi) - o day khong tinh lai gi, chi kiem so luong roi ghi file.

    Vi sao nhan ca bo cuc chu khong chi sectionIds: yeu cau la file phai co "dinh
    dang y het" man hinh, ma bo cuc (buoi nao nam cot con thu may trong ngay, mau
    gi) la ket qua tinh cua giao dien. Tinh lai o day bang mot ban thu hai cua
    thuat toan chia cot la chac chan co ngay hai ben lech nhau."""
    du_lieu = request.get_json(silent=True) or {}
    if not isinstance(du_lieu.get("cells"), list):
        return jsonify({"error": "Thiếu dữ liệu lưới để xuất."}), 400
    if not du_lieu["cells"]:
        return jsonify({"error": "Bộ lọc hiện tại không còn buổi nào để xuất."}), 400

    label = (du_lieu.get("label") or "").strip() or "TKB"
    buf = fate_export_luoi.build_workbook(du_lieu)
    return send_file(buf, as_attachment=True,
                     download_name=_ten_file(label, ".luoi"), mimetype=XLSX_MIME)
