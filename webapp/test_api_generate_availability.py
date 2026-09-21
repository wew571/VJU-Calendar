# -*- coding: utf-8 -*-
"""Test endpoint POST /api/manual/teacher/<id>/generate-availability - xem
api/manual_teacher.py va PROMPT-THEM-CHUC-NANG-GIO-RANH-GIANG-VIEN.md muc 6.4.

Chay: cd webapp && py -m pytest test_api_generate_availability.py -q

KHONG dung file snapshot that: monkeypatch save_snapshot thanh no-op (giong
kiem_tra_nhom_sinh_vien.py) va tu dung STATE truc tiep thay vi nap file.
"""

import pytest

import api.manual_teacher as manual_teacher_api
from domain.sections import empty_manual_data
from state import STATE


@pytest.fixture(autouse=True)
def _khong_ghi_snapshot(monkeypatch):
    monkeypatch.setattr(manual_teacher_api, "save_snapshot", lambda: None)


@pytest.fixture
def client():
    from app import app
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


@pytest.fixture(autouse=True)
def _du_lieu_rong():
    """Moi test bat dau tu mot bo du lieu nhap tay TRONG, doc lap voi cac test
    khac va voi file snapshot that tren may."""
    STATE["data"] = empty_manual_data()
    STATE["data"]["teachers"][1] = {"id": 1, "name": "GV test", "type": "GUEST", "org": "", "title": "", "email": "", "phone": ""}
    STATE["extra"] = None
    STATE["guestResult"] = None
    STATE["residentResult"] = None
    yield
    STATE["data"] = None


def test_khong_tim_thay_giang_vien_tra_400_va_khong_doi_du_lieu(client):
    STATE["data"]["manual_teacher_windows"][1] = [1, 2, 3]
    res = client.post("/api/manual/teacher/999/generate-availability")
    assert res.status_code == 400
    assert "error" in res.get_json()
    # Du lieu GV #1 khong bi dung cham toi.
    assert STATE["data"]["manual_teacher_windows"][1] == [1, 2, 3]


def test_sinh_va_thay_the_toan_bo_gio_ranh_cu(client):
    STATE["data"]["manual_teacher_windows"][1] = [999]  # gio ranh CU vo ly, phai bi xoa het
    res = client.post("/api/manual/teacher/1/generate-availability")
    assert res.status_code == 200
    body = res.get_json()
    teacher = next(t for t in body["teachers"] if t["id"] == 1)
    assert 999 not in teacher["availabilitySlots"]
    assert "generatedSlotCount" in body
    assert body["generatedSlotCount"] == len(teacher["availabilitySlots"])


def test_giu_nguyen_gio_dang_day(client):
    # GV #1 dang day T2 tiet 2-3 (lop DA CHOT GIO: khong time_assumed, co original_slot).
    STATE["data"]["courses"][1] = {"id": 1, "code": "TEST101", "name": "Mon test", "credits": 3}
    STATE["data"]["program_faculty"]["Chung"] = 0
    STATE["data"]["sections"][1] = {
        "id": 1, "course_id": 1, "course_name": "Mon test", "teacher_id": 1, "teacher_ids": [1],
        "teacher_type": "GUEST", "duration": 2, "time_assumed": False,
        "original_slot": 1, "room_type": "LT", "program": "Chung", "program_ids": [],
        "class_code": "", "cohort": "",
    }
    res = client.post("/api/manual/teacher/1/generate-availability")
    assert res.status_code == 200
    body = res.get_json()
    teacher = next(t for t in body["teachers"] if t["id"] == 1)
    assert 1 in teacher["teachingSlots"] and 2 in teacher["teachingSlots"]
    # Khong duoc dam gio ranh moi vao dung gio dang day.
    assert 1 not in teacher["availabilitySlots"]
    assert 2 not in teacher["availabilitySlots"]


def test_loi_giua_chung_khong_lam_mat_gio_ranh_cu(client, monkeypatch):
    STATE["data"]["manual_teacher_windows"][1] = [5, 6, 7]

    def _loi(*a, **k):
        raise RuntimeError("gia lap loi giua thuat toan")

    monkeypatch.setattr(manual_teacher_api, "generate_teacher_availability", _loi)
    with pytest.raises(RuntimeError):
        client.post("/api/manual/teacher/1/generate-availability")
    # Loi truoc khi ghi -> gio ranh cu con nguyen, khong bi xoa nua chung.
    assert STATE["data"]["manual_teacher_windows"][1] == [5, 6, 7]
