# -*- coding: utf-8 -*-
"""BO QUA cac lop do DON VI KHAC dieu phoi (khong phai viec cua khoa).

Quy tac nghiep vu nam o domain/bo_qua.py - o day chi doc request, goi domain,
dong bo lai luoi va tra ve.
"""

from flask import Blueprint, jsonify, request

from api.common import can_du_lieu, loi, tra_du_lieu
from domain import bo_qua as bq
from domain.luoi import dong_bo_ket_qua
from snapshot import save_snapshot

bp = Blueprint("bo_qua", __name__)


@bp.get("/api/manual/bo-qua")
@can_du_lieu
def api_bo_qua_xem(data):
    """Xem truoc: he thong de xuat bo qua nhung lop nao, va dang bo qua nhung lop nao."""
    ung_vien = bq.ung_vien(data)
    return jsonify({
        "ungVien": ung_vien,
        "soUngVien": len(ung_vien),
        "dangBoQua": bq.dang_bo_qua(data),
    })


@bp.post("/api/manual/bo-qua")
@can_du_lieu
def api_bo_qua(data):
    """Danh dau / bo danh dau.

    Body: {"sectionIds": [int] | null, "boQua": bool}
      sectionIds = null  -> lay dung danh sach he thong de xuat (bq.ung_vien),
                            tuc nut "Bo qua N lop do don vi khac dieu phoi".
    """
    body = request.get_json(silent=True) or {}
    bat = body.get("boQua", True) is not False
    ids = body.get("sectionIds")
    if ids is None:
        ids = bq.ung_vien(data) if bat else bq.dang_bo_qua(data)
    if not isinstance(ids, list):
        return loi("sectionIds phải là danh sách.")

    # KHONG chan theo "da chot lich" - day la mot loai thao tac KHAC.
    #
    # Chot lich khoa cai GIO cua mot hoc phan (cam ket voi giang vien). Bo qua
    # khong dong vao gio cua lop nao: gio van nguyen trong data, van xuat ra
    # Excel duoc, va bo danh dau la hien lai y nguyen. No chi tra loi cau "day co
    # phai viec cua khoa khong".
    #
    # Chan o day con lam tinh nang vo dung dung cho can nhat: nap file xong,
    # chot_hoc_phan_du_gio_tu_file() tu danh dau DA CHOT cho moi hoc phan du gio
    # trong file - ma 54/66 lop don vi khac dieu phoi deu co gio san, nen gan nhu
    # ca 66 lop deu bi chan (do that: "Triet hoc Mac-Lenin da chot lich").
    da_doi = bq.dat(data, ids, bat)
    # Luoi phai bo/hien lai cac buoi nay NGAY, khong doi den lan giai ke tiep -
    # neu khong bang noi "da bo qua" ma luoi van con the buoi do.
    dong_bo_ket_qua(data)
    save_snapshot()
    return tra_du_lieu(data, boQuaChanged=da_doi, boQua=bat,
                       soDangBoQua=len(bq.dang_bo_qua(data)))
