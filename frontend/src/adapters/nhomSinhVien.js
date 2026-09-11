// NHÓM SINH VIÊN = (CTĐT, Khóa): "FTH khóa VJU2024" là MỘT nhóm người học, và
// một người không thể ngồi hai lớp cùng một lúc.
//
// Bản SONG SINH của webapp/domain/nhom_sinh_vien.py — cùng một luật gom nhóm và
// cùng một luật loại trừ. Backend dùng nó để RÀNG BUỘC solver, màn hình dùng nó
// để BÁO ra; lệch nhau là hộp thư kêu một đằng còn solver né một nẻo.
//
// VÌ SAO LÀ (CTĐT, Khóa) CHỨ KHÔNG PHẢI RIÊNG KHÓA: "VJU2024" không phải một lớp
// người học — sinh viên BCSE khóa 2024 và sinh viên FTH khóa 2024 học hai chương
// trình khác hẳn, hai lớp của họ trùng giờ là chuyện bình thường. Lọc theo riêng
// Khóa sẽ báo hàng loạt vụ trùng không có thật.
//
// Ô GHÉP thuộc CẢ HAI vế, y hệt adapters/phamVi.js: lớp "FTH.ESAS" là lớp của cả
// nhóm FTH lẫn nhóm ESAS, "VJU2024+VJU2023" thuộc cả hai khóa — nên một lớp có
// thể nằm trong nhiều nhóm.
//
// BA TRƯỜNG HỢP CÙNG GIỜ LÀ ĐÚNG Ý, không được báo:
//   - HỌC CHUNG: cả nhóm là MỘT buổi dạy vật lý, chúng PHẢI ở cùng ô giờ.
//   - LỚP SONG SONG của cùng một HỌC PHẦN (CSE3013-1 và CSE3013-2): sinh viên
//     chia đôi, mỗi người học một lớp.
//   - LỚP TRỰC TUYẾN (ô "Hình thức"): môn linh động, lên thời khóa biểu chỉ để có
//     trong danh sách đăng ký chứ không phải một buổi học cố định.
//
// GIỚI HẠN ĐÃ BIẾT: hai học phần mà sinh viên chỉ học MỘT trong hai ("Tiếng Nhật
// sơ cấp 1" và "sơ cấp 2" xếp cùng tiết cho cùng một khóa) vẫn bị báo — dữ liệu
// không nói ra điều đó. Báo để con người đọc và bỏ qua, còn hơn im lặng bỏ sót.

import { taoCungBuoi } from "./hocChung";

const thuong = (x) => String(x ?? "").toLowerCase();

// Bỏ dấu tiếng Việt để so khớp ô chữ tự do người gõ tay — bản song sinh của
// scheduler_core.bo_dau(). "đ" không tách ra khi normalize nên phải thay riêng.
const boDau = (t) =>
  String(t ?? "")
    .split(/\s+/)
    .join(" ")
    .trim()
    .toLowerCase()
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .replace(/đ/g, "d");

/**
 * Lớp này học TRỰC TUYẾN — không phải một buổi học cố định ở một chỗ, nên nó
 * không giữ chân sinh viên và không chiếm giờ của môn nào.
 *
 * "LMS" KHÔNG được miễn, dù trước đây có: giáo vụ đã xác nhận môn ghi LMS vẫn là
 * buổi học thật, sinh viên phải có mặt đúng giờ đó. Xem bản song sinh ở
 * webapp/domain/nhom_sinh_vien.py: hoc_truc_tuyen() — hai nơi lệch nhau là hộp
 * thư báo một đằng còn solver né một đằng.
 *
 * "Online
Trực tiếp" thì KHÔNG tính — lớp đó có buổi học thật tại lớp.
 */
export function hocTrucTuyen(c) {
  const t = boDau(c?.teachingMode);
  if (!t || t.includes("truc tiep")) return false;
  return t.includes("truc tuyen") || t.includes("online");
}

// Các nhóm sinh viên của một lớp -> [["fth","vju2023"], ...].
// RỖNG khi lớp không ghi Khóa: không biết nó của ai thì không kết luận gì cả.
export function nhomCuaLop(c) {
  const khoa = (c?.cohortParts ?? []).filter(Boolean);
  if (!khoa.length) return [];
  const ctdt = (c?.programParts ?? []).filter(Boolean);
  return ctdt.flatMap((p) => khoa.map((k) => [thuong(p), thuong(k)]));
}

export function nhanNhom([ctdt, khoa]) {
  return `${String(ctdt).toUpperCase()}/${String(khoa).toUpperCase()}`;
}

/**
 * Lớp này có chiếm thời gian của sinh viên không?
 *
 * Lớp của khoa thì dĩ nhiên có. Nhưng CẢ lớp do ĐƠN VỊ KHÁC điều phối mà ĐÃ CÓ
 * GIỜ cũng chiếm: "Triết học Mác-Lênin" do Phòng Đào tạo xếp Thứ 2 tiết 2–5 cho
 * BCSE/VJU2026 thì sinh viên khóa đó đang ngồi học thật, khoa không được xếp môn
 * khác vào đúng ô ấy. Bản song sinh của webapp/domain/nhom_sinh_vien.py:
 * chiem_gio_cua_sinh_vien().
 *
 * Lớp bỏ qua CHƯA có giờ thì không: chưa ai xếp thì không có gì để né.
 */
export function chiemGioCuaSinhVien(c) {
  return !c?.boQua || (!c.timeAssumed && c.day != null);
}

// {khoá nhóm: {nhan, sectionIds}} — mọi lớp CHIẾM GIỜ của sinh viên.
export function cacNhom(data) {
  const ra = new Map();
  for (const c of data?.classes ?? []) {
    if (!chiemGioCuaSinhVien(c)) continue;
    for (const g of nhomCuaLop(c)) {
      const k = g.join("|");
      if (!ra.has(k)) ra.set(k, { nhan: nhanNhom(g), sectionIds: [] });
      ra.get(k).sectionIds.push(c.sectionId);
    }
  }
  return ra;
}

// Lớp không quy được về nhóm nào vì ô Khóa bỏ trống. PHẢI đếm và nói ra trên giao
// diện: chúng không được kiểm, nên "0 vụ trùng" chỉ đúng với phần đã ghi đủ Khóa.
export function lopChuaGhiKhoa(data) {
  return (data?.classes ?? []).filter(
    (c) => chiemGioCuaSinhVien(c) && nhomCuaLop(c).length === 0,
  );
}

function chongGio(a, da, b, db) {
  return !(a + da <= b || b + db <= a);
}

/**
 * Các vụ trùng lịch sinh viên trên một bộ buổi ĐANG NẰM THẬT trên lưới.
 *
 * @param buoi [{id, slot, duration}] — cả hai giai đoạn, đã áp bản kéo-thả chưa lưu.
 * @returns [{nhan, a, b, slot, day}] — mỗi cặp CHỈ RA MỘT LẦN dù hai lớp chung
 *   nhiều nhóm (lớp "FTH.ESAS" khóa 2023 chung cả hai nhóm với lớp FTH.ESAS khác).
 */
export function cacVuTrung(data, buoi) {
  const cungBuoi = taoCungBuoi(data);
  const monCuaLop = new Map((data?.classes ?? []).map((c) => [c.sectionId, c.courseId]));
  const trucTuyen = new Set(
    (data?.classes ?? []).filter(hocTrucTuyen).map((c) => c.sectionId),
  );
  const viTri = new Map((buoi ?? []).filter((l) => l.slot != null).map((l) => [l.id, l]));

  const daCo = new Set();
  const ra = [];
  for (const { nhan, sectionIds } of cacNhom(data).values()) {
    const ds = sectionIds.filter((sid) => viTri.has(sid)).sort((x, y) => x - y);
    for (let i = 0; i < ds.length; i++) {
      for (let j = i + 1; j < ds.length; j++) {
        const key = `${ds[i]}-${ds[j]}`;
        if (daCo.has(key)) continue;
        if (cungBuoi(ds[i], ds[j])) continue;
        // CHỈ MỘT BÊN trực tuyến là đủ — xem hocTrucTuyen().
        if (trucTuyen.has(ds[i]) || trucTuyen.has(ds[j])) continue;
        const ma = monCuaLop.get(ds[i]);
        if (ma != null && ma === monCuaLop.get(ds[j])) continue;
        const a = viTri.get(ds[i]);
        const b = viTri.get(ds[j]);
        if (!chongGio(a.slot, a.duration ?? 1, b.slot, b.duration ?? 1)) continue;
        daCo.add(key);
        ra.push({ nhan, a: ds[i], b: ds[j], slot: Math.min(a.slot, b.slot) });
      }
    }
  }
  return ra;
}
