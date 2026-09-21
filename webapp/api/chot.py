# -*- coding: utf-8 -*-
"""CHOT LICH GIANG DAY theo tung LOP HOC PHAN (va bo chot)."""

from flask import Blueprint, request

from api.common import can_du_lieu, loi, tra_du_lieu
from domain.chot import bo_chot_lop_hoc_phan, chot_lop_hoc_phan
from domain.luoi import dong_bo_ket_qua
from snapshot import save_snapshot

bp = Blueprint("chot", __name__)


@bp.post("/api/manual/section/<int:section_id>/chot")
@can_du_lieu
def api_manual_chot_section(data, section_id):
    """Chot lich giang day cho mot lop hoc phan."""
    s = data.get("sections", {}).get(section_id)
    if s is None:
        return loi(f"Không tìm thấy lớp học phần id={section_id}.")
    body = request.get_json(silent=True) or {}
    err = chot_lop_hoc_phan(data, section_id, body.get("by"), body.get("note"))
    if err:
        return loi(err)
    dong_bo_ket_qua(data, [section_id])
    save_snapshot()
    course = data.get("courses", {}).get(s.get("course_id")) or {}
    return tra_du_lieu(data, classCode=s.get("class_code"), courseName=course.get("name"))


@bp.delete("/api/manual/section/<int:section_id>/chot")
@can_du_lieu
def api_manual_bo_chot_section(data, section_id):
    """Bo chot mot lop hoc phan va tra gio ve trang thai truoc khi chot."""
    s = data.get("sections", {}).get(section_id)
    if s is None:
        return loi(f"Không tìm thấy lớp học phần id={section_id}.")
    if not s.get("chot"):
        return loi("Lớp học phần này chưa được chốt.")
    bo_chot_lop_hoc_phan(data, section_id)
    dong_bo_ket_qua(data, [section_id])
    save_snapshot()
    course = data.get("courses", {}).get(s.get("course_id")) or {}
    return tra_du_lieu(data, classCode=s.get("class_code"), courseName=course.get("name"))
