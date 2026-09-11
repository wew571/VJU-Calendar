// PHẠM VI XẾP: xếp thời khóa biểu cho RIÊNG một chương trình đào tạo (CTĐT) +
// các khóa của nó, thay vì cả khoa một lúc.
//
// Đây là bản SONG SINH của webapp/domain/pham_vi.py ở phía giao diện — cùng một
// luật khớp lớp vào phạm vi, để màn hình đếm ra con số nào thì backend cũng xếp
// đúng chừng ấy lớp. Lệch hai bên là giáo vụ thấy "33 lớp FTH" rồi bấm Xếp mà
// kết quả báo 31, không ai giải thích nổi.
//
// Nguồn dữ liệu là `data.classes` (bảng mirror 29 cột) chứ KHÔNG phải danh sách
// buổi trên lưới: lớp chưa có giờ thì chưa có buổi nào, mà đó lại chính là những
// lớp cần xếp nhất.

export const PHAM_VI_RONG = { programs: [], cohorts: [] };

// Phạm vi "rỗng cả hai vế" = toàn khoa (hành vi cũ). Chuẩn hóa về null để mọi
// nơi chỉ phải kiểm tra một điều kiện, và để gửi lên backend đúng thứ nó hiểu.
export function chuanHoa(phamVi) {
  const programs = (phamVi?.programs ?? []).filter(Boolean);
  const cohorts = (phamVi?.cohorts ?? []).filter(Boolean);
  if (programs.length === 0 && cohorts.length === 0) return null;
  return { programs, cohorts };
}

export function coPhamVi(phamVi) {
  return chuanHoa(phamVi) !== null;
}

// "FTH · VJU2026, VJU2025, VJU2024" — nhãn dùng ở nút bấm và thanh tiêu đề.
export function moTa(phamVi) {
  const pv = chuanHoa(phamVi);
  if (!pv) return "toàn khoa";
  const ve = [];
  if (pv.programs.length) ve.push(pv.programs.join(", "));
  if (pv.cohorts.length) ve.push(pv.cohorts.join(", "));
  return ve.join(" · ");
}

const thuong = (ds) => new Set((ds ?? []).map((x) => String(x).toLowerCase()));
const giaoNhau = (a, b) => [...a].some((x) => b.has(x));

// Ô GHÉP thuộc CẢ HAI vế: lớp "FTH.ESAS" là lớp của cả FTH lẫn ESAS nên xếp FTH
// là phải xếp nó; "VJU2024+VJU2023" thuộc cả hai khóa. Backend đã tách sẵn thành
// programParts/cohortParts (xem webapp/domain/programs.py: tach_phan) nên ở đây
// chỉ việc lấy giao — KHÔNG so khớp nguyên chuỗi.
export function lopThuoc(c, phamVi) {
  const pv = chuanHoa(phamVi);
  if (!pv) return true;
  if (pv.programs.length && !giaoNhau(thuong(c.programParts), thuong(pv.programs))) return false;
  if (pv.cohorts.length && !giaoNhau(thuong(c.cohortParts), thuong(pv.cohorts))) return false;
  return true;
}

// Bản dùng cho BUỔI trên lưới (lesson) — cùng một luật, chỉ khác chỗ lấy dữ liệu.
// buildScheduleView đã gắn programParts/cohortParts lên từng buổi.
export function buoiThuoc(l, phamVi) {
  return lopThuoc(l, phamVi);
}

// Danh sách CTĐT để chọn. Lấy từ bảng lớp chứ không từ lưới, xem chú thích đầu file.
export function danhSachChuongTrinh(data) {
  return [...new Set((data?.classes ?? []).flatMap((c) => c.programParts ?? []))].sort((a, b) =>
    a.localeCompare(b),
  );
}

// Khóa để chọn — LỌC THEO chương trình đang chọn: giáo vụ xếp FTH thì chỉ nên
// thấy các khóa FTH thật sự có lớp, không phải cả 8 khóa của toàn khoa rồi tick
// nhầm một khóa không có lớp nào. Khóa mới nhất lên đầu (VJU2026 trước VJU2023).
export function danhSachKhoa(data, programs) {
  const loc = (data?.classes ?? []).filter(
    (c) => !programs?.length || giaoNhau(thuong(c.programParts), thuong(programs)),
  );
  return [...new Set(loc.flatMap((c) => c.cohortParts ?? []))].sort().reverse();
}

// Các lớp thuộc phạm vi, ĐÃ LAN THEO NHÓM HỌC CHUNG.
//
// Một nhóm học chung là MỘT buổi dạy vật lý ghi thành nhiều mã môn (xem
// webapp/domain/hoc_chung.py), không thể xếp nửa nhóm — nên một thành viên lọt
// vào phạm vi là cả nhóm vào theo. Backend làm đúng như vậy ở
// domain/pham_vi.py: sids_thuoc.
//
// PHẢI có bản này ở đây, không được để mỗi bên một luật: dữ liệu thật có nhóm
// [#281 "Chung" – Học theo dự án (FTH3006), #301 FTH/VJU2023], nên phạm vi
// FTH×{VJU2023} mà thiếu bao đóng thì màn hình đếm 15 lớp còn backend xếp 16 —
// hai con số lệch nhau và không ai giải thích được.
export function sectionIdsTrongPhamVi(data, phamVi) {
  // Lop do don vi khac dieu phoi da bỏ qua không thuộc phạm vi nào — không phải
  // việc của khoa nên không đếm, không xếp (xem webapp/domain/bo_qua.py).
  const lop = (data?.classes ?? []).filter((c) => !c.boQua);
  if (!coPhamVi(phamVi)) return new Set(lop.map((c) => c.sectionId));
  const trong = new Set(lop.filter((c) => lopThuoc(c, phamVi)).map((c) => c.sectionId));
  for (const nhom of data?.hocChungGroups ?? []) {
    const ids = nhom?.sectionIds ?? [];
    if (ids.some((sid) => trong.has(sid))) ids.forEach((sid) => trong.add(sid));
  }
  return trong;
}

export function lopTrongPhamVi(data, phamVi) {
  const trong = sectionIdsTrongPhamVi(data, phamVi);
  return (data?.classes ?? []).filter((c) => !c.boQua && trong.has(c.sectionId));
}

// Đếm những gì giáo vụ cần biết TRƯỚC KHI bấm Xếp: phạm vi này có bao nhiêu lớp,
// bao nhiêu lớp còn chưa có giờ (đó mới là VIỆC mà nút Xếp phải làm), và bao
// nhiêu lớp dùng chung với chương trình khác.
export function demPhamVi(data, phamVi) {
  const lop = lopTrongPhamVi(data, phamVi);
  const pv = chuanHoa(phamVi);
  const cuaToi = thuong(pv?.programs);
  const dem = { tong: lop.length, GUEST: { daChot: 0, chua: 0 }, RESIDENT: { daChot: 0, chua: 0 }, dungChung: 0 };
  for (const c of lop) {
    const o = dem[c.teacherType];
    if (o) o[c.timeAssumed ? "chua" : "daChot"] += 1;
    // Ô CTĐT còn ghi cả chương trình khác ("FTH.ESAS") -> lớp này cũng nằm trong
    // phạm vi của họ, đến lượt họ xếp là họ có quyền đổi giờ. Muốn giữ cứng thì
    // phải "Chốt lịch theo học phần".
    if (cuaToi.size && (c.programParts ?? []).some((p) => !cuaToi.has(String(p).toLowerCase()))) {
      dem.dungChung += 1;
    }
  }
  dem.chuaCoGio = dem.GUEST.chua + dem.RESIDENT.chua;
  return dem;
}
