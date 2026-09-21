import { apiGet, apiPost, apiPatch, apiDelete, apiUpload, apiDownload } from "./api";

export const getData = () => apiGet("/api/data");
// `phamVi` = {programs: [...], cohorts: [...]} - XEP CHO RIENG mot chuong trinh
// dao tao + cac khoa cua no; null/bo trong = toan khoa (hanh vi cu). Backend
// dong bang moi lop ngoai pham vi nen bam Xep cho FTH khong lam xe dich lop cua
// chuong trinh khac - xem webapp/domain/pham_vi.py.
//
// LUON gui khoa "phamVi" (ke ca khi null): backend phan biet "khong gui" (= giu
// pham vi cua lan giai truoc) voi "gui null" (= lan nay xep toan khoa).
export const solveGuest = (phamVi = null) => apiPost("/api/solve-guest", { phamVi });
export const solveResident = (phamVi = null) => apiPost("/api/solve-resident", { phamVi });
// Keo-tha sua tay (thay cho "Tu choi - luan chuyen" cu). moveLesson khong ghi
// reason se bi 409 neu o do dang co van de - xem api.js (err.body.conflict).
export const moveLesson = (sectionId, slot, reason) =>
  apiPost("/api/move-lesson", { sectionId, slot, reason });
export const clearOverride = (sectionId) => apiPost("/api/clear-override", { sectionId });
// "Luu thoi khoa bieu": ghi ket qua dang xem tren luoi thanh du lieu chinh
// thuc cua lop hoc phan (Thu/Tiet BD/Tiet KT/Trang thai).
export const saveSchedule = () => apiPost("/api/manual/save-schedule");
export const getState = () => apiGet("/api/state");
// Ket qua giai dang cache ben Flask - de tai lai trang khong mat luoi da xep.
export const getResults = () => apiGet("/api/results");

export const initManual = () => apiPost("/api/manual/init");
// Nap file ke hoach giang day cu vao form. HAI BUOC: xem truoc (khong ghi gi,
// chi doc file va bao se ra cai gi) roi moi commit (ghi de toan bo du lieu).
export const importPreview = (file) => apiUpload("/api/manual/import/preview", file);
// mode: "replace" (xoa het roi nap) | "merge" (gop them vao du lieu dang co)
export const importCommit = (mode = "replace") =>
  apiPost("/api/manual/import/commit", { mode });
// DANH SACH GV CO HUU cua truong - nguon CHINH THUC de phan loai co huu/thinh
// giang. Cung 2 buoc nhu nhap file ke hoach: nap no co the doi loai nhieu GV,
// keo theo lop chuyen giai doan xep lich.
export const lecturersPreview = (file) => apiUpload("/api/manual/lecturers/preview", file);
export const lecturersCommit = () => apiPost("/api/manual/lecturers/commit");
export const lecturersClear = () => apiDelete("/api/manual/lecturers");
export const getLecturers = () => apiGet("/api/manual/lecturers");
export const addManualTeacher = (payload) => apiPost("/api/manual/teacher", payload);
export const updateManualTeacher = (teacherId, payload) => apiPatch(`/api/manual/teacher/${teacherId}`, payload);
// "Tu dong khai gio ranh": xoa toan bo gio ranh hien co (giu nguyen gio dang
// day) roi sinh lai theo cac khung sang/chieu/toi cau hinh san
// (CONFIG["availabilityGenerator"]) va luu ngay - xem webapp/api/manual_teacher.py.
export const generateTeacherAvailability = (teacherId) =>
  apiPost(`/api/manual/teacher/${teacherId}/generate-availability`);
// CHOT LICH rieng mot lop hoc phan: ghi gio dang hien thanh gio chinh thuc va
// ghim lai - cac lop khac cung hoc phan van co the xep/sua doc lap.
export const chotSection = (sectionId, payload) =>
  apiPost(`/api/manual/section/${sectionId}/chot`, payload);
export const boChotSection = (sectionId) => apiDelete(`/api/manual/section/${sectionId}/chot`);
export const addManualCourse = (payload) => apiPost("/api/manual/course", payload);
export const updateManualCourse = (courseId, payload) => apiPatch(`/api/manual/course/${courseId}`, payload);
export const addManualSection = (payload) => apiPost("/api/manual/section", payload);
export const updateManualSection = (sectionId, payload) => apiPatch(`/api/manual/section/${sectionId}`, payload);
export const deleteManualSection = (sectionId) => apiDelete(`/api/manual/section/${sectionId}`);
// "Xoa gio" hang loat - dat lai Thu/Tiet dau/Tiet cuoi cua nhieu lop thanh
// "de he thong tu xep" cung mot luc (xem app.py: api_manual_clear_times).
export const clearManualTimes = (sectionIds) => apiPost("/api/manual/clear-times", { sectionIds });

// HOC CHUNG: danh dau nhieu lop (nhieu ma mon) la MOT buoi day. KHONG chi la tat
// canh bao - backend ep solver xep ca nhom vao cung mot slot va chi tinh mot
// phong, nen giai lai bao nhieu lan ca nhom cung dung yen (xem
// webapp/domain/hoc_chung.py).
export const markHocChung = (sectionIds, payload = {}) =>
  apiPost("/api/manual/hoc-chung", { sectionIds, ...payload });
export const unmarkHocChung = (groupId) => apiDelete(`/api/manual/hoc-chung/${groupId}`);

// "Huy thay doi" o man Thoi khoa bieu: tra TOAN BO trang thai ve dung lan LUU gan
// nhat (hoac luc vua nap file, neu chua luu lan nao) - gio cua moi lop, ghim,
// trang thai chot, nhom hoc chung va ca luoi. Xem webapp/domain/hoan_tac.py: dat_moc().
export const hoanTac = () => apiPost("/api/manual/hoan-tac");

// XUAT EXCEL - ca hai duong deu xuat DUNG PHAN DANG HIEN theo bo loc cua man hinh.
//
// `sectionIds` = danh sach lop dang hien sau khi loc (null = xuat het). Gui len
// thay vi de backend doan lai bo loc: man hinh moi la noi biet chac no dang hien
// cai gi - xem webapp/api/export.py.
export const exportClasses = (label, sectionIds = null) =>
  apiDownload("/api/manual/export", { label, sectionIds }, "FATE.TKB.xlsx");

// Xuat LUOI thoi khoa bieu (hang = tiet, cot = thu) dung bo cuc dang hien.
// `duLieuLuoi` do adapters/xuatLuoi.js dung san.
export const exportLuoi = (duLieuLuoi) =>
  apiDownload("/api/manual/export-luoi", duLieuLuoi, "FATE.TKB.luoi.xlsx");

// BO QUA cac lop do DON VI KHAC dieu phoi ("Phong Dao tao dieu phoi", "JLE dieu
// phoi") - khoa khong xep nhung lop nay nen chung khong nen nam trong danh sach
// viec, cung khong duoc vao thuat toan. Xem webapp/domain/bo_qua.py.
//
// sectionIds = null: lay dung danh sach he thong de xuat (khi bat) hoac toan bo
// lop dang bo qua (khi tat) - dung cho nut "Bo qua N lop..." / "Hien lai".
export const xemBoQua = () => apiGet("/api/manual/bo-qua");
export const datBoQua = (sectionIds = null, boQua = true) =>
  apiPost("/api/manual/bo-qua", { sectionIds, boQua });
