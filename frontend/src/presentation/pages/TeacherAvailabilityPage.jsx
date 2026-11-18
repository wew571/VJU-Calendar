import { useMemo, useState } from "react";
import { GraduationCap, Plus, TriangleAlert } from "lucide-react";
import { useAppData } from "../../context/AppDataContext";
import TeacherEditDrawer from "../manual/TeacherEditDrawer";
import { ListSearch } from "@/components/shared/list-search";
import { FilterSelect } from "@/components/shared/filter-select";
import { Notice } from "@/components/shared/notice";
import { Pill } from "@/components/shared/pill";
import { Button } from "@/components/ui/button";
import { NativeSelect } from "@/components/ui/native-select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { cn } from "@/lib/utils";
import { getRoleDefinition } from "../../constants/roles";

// Trang nay GOP HAI man truoc day: "Giảng viên" (nhom rieng ngang hang, 2 tab
// Co huu/Thinh giang) va "Chuẩn bị dữ liệu → Giờ rảnh GV" (chi xem/khai gio cua
// THINH GIANG). Ca hai deu la MOT viec - quan ly giang vien - chi khac o loc
// theo loai truoc khi tim ten, nen gio con MOT man duy nhat: chon loai (Co huu/
// Thinh giang) bang nhan o dau trang, roi loc/tim TEN trong dung loai do. Bam
// vao mot dong mo TeacherEditDrawer - ngan keo do da co san CA thong tin GV VA
// luoi "gio co the day" (ke ca co huu, xem TeacherEditDrawer) nen khong can
// luoi rieng ngay tren trang danh sach nua.
const LOAI = {
  RESIDENT: {
    nhan: "cơ hữu",
    moTa: "Giảng viên của trường — lớp của họ được xếp ở Giai đoạn 2.",
  },
  GUEST: {
    nhan: "thỉnh giảng",
    moTa: "Khách mời từ đơn vị khác — lớp của họ được xếp ở Giai đoạn 1, theo khung giờ đã khai.",
  },
};

function tongTiet(classes, teacherId) {
  let n = 0;
  for (const c of classes) {
    if (!(c.teacherIds ?? [c.teacherId]).includes(teacherId)) continue;
    if (c.periodStart == null || c.periodEnd == null) continue;
    n += c.periodEnd - c.periodStart + 1;
  }
  return n;
}

export default function TeacherAvailabilityPage({ role }) {
  const { data, loading } = useAppData();
  const permissions = getRoleDefinition(role);
  const allowedTypes = permissions.canDeclareOwnAvailability
    ? ["RESIDENT"]
    : permissions.canEditResidentAvailability
      ? ["GUEST", "RESIDENT"]
      : ["GUEST"];
  const [loai, setLoai] = useState(allowedTypes[0]);
  const [search, setSearch] = useState("");
  const [orgFilter, setOrgFilter] = useState("");
  const [drawerId, setDrawerId] = useState(null);
  const [myTeacherId, setMyTeacherId] = useState(() => {
    try {
      return localStorage.getItem("tkb_resident_teacher") || "";
    } catch {
      return "";
    }
  });

  const meta = LOAI[loai];
  const canEdit = loai === "GUEST"
    ? permissions.canManageGuests
    : permissions.canEditResidentAvailability || (permissions.canDeclareOwnAvailability && myTeacherId);
  const classes = data?.classes || [];

  // Lop cua tung nguoi: gom theo teacherIds (CA nhom dong giang), khong chi GV
  // chinh - nguoi thu hai tro di cung day lop do that.
  const lopTheoGv = useMemo(() => {
    const m = new Map();
    for (const c of classes) {
      for (const tid of c.teacherIds ?? [c.teacherId]) {
        if (!m.has(tid)) m.set(tid, []);
        m.get(tid).push(c);
      }
    }
    return m;
  }, [classes]);

  // Ban ghi "cho trong" (lop chua phan cong giang vien) khong phai con nguoi -
  // loc khoi ca hai loai, neu khong tab thinh giang ngap hang chuc dong
  // "Phòng Đào tạo điều phối".
  const all = useMemo(
    () => (data?.teachers || []).filter((t) => !t.isPlaceholder),
    [data],
  );
  const theoLoai = useMemo(() => {
    const m = { RESIDENT: [], GUEST: [] };
    for (const t of all) if (m[t.type]) m[t.type].push(t);
    return m;
  }, [all]);
  const residentTeachers = theoLoai.RESIDENT ?? [];
  const selectedResident = residentTeachers.find(
    (teacher) => String(teacher.id) === myTeacherId,
  );
  const cuaLoai = (theoLoai[loai] ?? []).filter((teacher) =>
    !permissions.canDeclareOwnAvailability || String(teacher.id) === myTeacherId,
  );

  const orgs = useMemo(
    () => [...new Set(cuaLoai.map((t) => (t.org || "").trim()).filter(Boolean))].sort(),
    [cuaLoai],
  );

  const visible = useMemo(() => {
    const q = search.trim().toLowerCase();
    return cuaLoai
      .filter((t) => {
        if (orgFilter && (t.org || "").trim() !== orgFilter) return false;
        if (!q) return true;
        return [t.nameRaw, t.name, t.email, t.org]
          .some((v) => (v || "").toLowerCase().includes(q));
      })
      .sort((a, b) => (a.nameRaw || a.name || "").localeCompare(b.nameRaw || b.name || ""));
  }, [cuaLoai, orgFilter, search]);

  const drawerTeacher =
    drawerId === "new" ? null : (data?.teachers || []).find((t) => t.id === drawerId) ?? null;

  // Chua nap danh sach chinh thuc thi he thong dang DOAN loai GV tu o "Don vi
  // cong tac" trong file ke hoach - o do giao vu go tay nen sai du kieu. Noi ro
  // ra thay vi de nguoi dung tin bang nay la chuan.
  const chuaNapDanhSach = all.length > 0 && all.every((t) => t.inLecturerList == null);
  const ngoaiDanhSach = cuaLoai.filter((t) => t.inLecturerList === false);

  if (!data) {
    return (
      <Notice tone="slate">
        Chưa có dữ liệu — sang “Dữ liệu học phần” để nhập hoặc nạp dữ liệu trước.
      </Notice>
    );
  }

  return (
    <div className="space-y-3">
      <div className="glass-panel rounded-xl border">
        {permissions.canDeclareOwnAvailability && (
          <div className="border-b p-3">
            <Notice tone="amber">
              {residentTeachers.length === 0
                ? "Chưa có hồ sơ giảng viên cơ hữu trong dữ liệu hiện tại."
                : selectedResident
                  ? `Đang xem hồ sơ ${selectedResident.nameRaw || selectedResident.name}.`
                  : "Chọn hồ sơ giảng viên cơ hữu trong danh sách bên phải để xem và khai báo giờ rảnh."}{" "}
              Hồ sơ này chỉ dùng mô phỏng; ứng dụng không xác minh danh tính hay bảo vệ dữ liệu theo tài khoản.
            </Notice>
          </div>
        )}
        <div className="flex flex-wrap items-center gap-2 border-b p-3">
          {/* Loc LOAI GV truoc tien - day la bo loc CAP MOT, quyet dinh ca danh
              sach ben duoi va nghia cua cot "Giờ có thể dạy". Dung chung mot
              kieu "segmented" voi tab man "Học phần" de dong bo. */}
          <div className="glass-segmented inline-flex h-9 items-center rounded-lg border p-0.75" role="tablist">
            {allowedTypes.map((key) => {
              const m = LOAI[key];
              return (
              <button
                type="button"
                key={key}
                role="tab"
                aria-selected={loai === key}
                onClick={() => { setLoai(key); setOrgFilter(""); }}
                className={cn(
                  "inline-flex h-full items-center gap-1.5 rounded-md px-2.5 text-sm font-medium capitalize transition-colors",
                  loai === key
                    ? "glass-segmented-active teacher-type-tab-active text-foreground"
                    : "text-muted-foreground hover:text-foreground",
                )}
              >
                {m.nhan}
                <span className="bg-muted-foreground/15 rounded px-1.5 text-xs tabular-nums">
                  {theoLoai[key]?.length ?? 0}
                </span>
              </button>
              );
            })}
          </div>
          <span className="text-muted-foreground text-xs">{meta.moTa}</span>

          <div className="ml-auto flex flex-wrap items-center gap-2">
            {permissions.canDeclareOwnAvailability && (
              <div className="min-w-52">
                <NativeSelect
                  aria-label="Chọn hồ sơ giảng viên cơ hữu trong bản demo"
                  value={myTeacherId}
                  onChange={(event) => {
                    const value = event.target.value;
                    setMyTeacherId(value);
                    setDrawerId(null);
                    try {
                      if (value) localStorage.setItem("tkb_resident_teacher", value);
                      else localStorage.removeItem("tkb_resident_teacher");
                    } catch {
                      // Hồ sơ vẫn dùng được trong phiên hiện tại nếu bộ nhớ cục bộ bị chặn.
                    }
                  }}
                >
                  <option value="">Chọn hồ sơ giảng viên</option>
                  {residentTeachers.map((teacher) => (
                    <option key={teacher.id} value={teacher.id}>
                      {teacher.nameRaw || teacher.name}
                    </option>
                  ))}
                </NativeSelect>
              </div>
            )}
            <ListSearch
              value={search}
              onChange={setSearch}
              placeholder="Tìm tên, email, đơn vị"
              className="w-full sm:w-60"
            />
            <FilterSelect
              label="Mọi đơn vị"
              searchable
              value={orgFilter || null}
              options={orgs}
              onChange={(v) => setOrgFilter(v ?? "")}
            />
            {!permissions.canDeclareOwnAvailability && canEdit && loai === "GUEST" && (
              <Button size="sm" disabled={loading} onClick={() => setDrawerId("new")}>
                <Plus className="size-4" />
                Mời giảng viên thỉnh giảng
              </Button>
            )}
          </div>
        </div>

        {chuaNapDanhSach && loai === "RESIDENT" && role === "assistant" && (
          <div className="border-b p-3">
            <Notice tone="amber" icon={TriangleAlert}>
              Chưa nạp danh sách giảng viên cơ hữu. Hệ thống đang <strong>đoán</strong> loại giảng
              viên từ ô “Đơn vị công tác” trong file kế hoạch giảng dạy — ô đó giáo vụ gõ tay mỗi kỳ
              nên hay bỏ trống hoặc ghi mỗi dòng một kiểu.               Cần đối chiếu danh sách chính thức trước khi dựa vào phân loại này.
            </Notice>
          </div>
        )}

        {ngoaiDanhSach.length > 0 && role === "assistant" && (
          <div className="border-b p-3">
            <Notice tone="amber" icon={TriangleAlert}>
              {ngoaiDanhSach.length} người ở tab này <strong>không có trong danh sách cơ hữu</strong>{" "}
              nhưng đang được xếp {meta.nhan}: {ngoaiDanhSach.slice(0, 5).map((t) => t.nameRaw || t.name).join(", ")}
              {ngoaiDanhSach.length > 5 && `, +${ngoaiDanhSach.length - 5}`}. Nên bổ sung vào danh
              sách hoặc chuyển loại tại đây.
            </Notice>
          </div>
        )}

        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>#</TableHead>
                <TableHead>Họ tên</TableHead>
                <TableHead>Đơn vị công tác</TableHead>
                <TableHead>Email</TableHead>
                <TableHead>SĐT</TableHead>
                <TableHead className="text-right">Lớp kỳ này</TableHead>
                <TableHead className="text-right">Tiết/tuần</TableHead>
                <TableHead>Giờ có thể dạy</TableHead>
                <TableHead>Nguồn phân loại</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {visible.length === 0 && (
                <TableRow>
                  <TableCell colSpan={9} className="text-muted-foreground py-6 text-center">
                    {permissions.canDeclareOwnAvailability && !selectedResident
                      ? residentTeachers.length === 0
                        ? "Chưa có hồ sơ giảng viên cơ hữu trong dữ liệu."
                        : "Hãy chọn hồ sơ giảng viên cơ hữu để xem dữ liệu."
                      : `Không có giảng viên ${meta.nhan} nào khớp.`}
                  </TableCell>
                </TableRow>
              )}
              {visible.map((t) => {
                const lop = lopTheoGv.get(t.id) || [];
                const daKhai = t.availabilitySlots?.length ?? 0;
                return (
                  <TableRow
                    key={t.id}
                    className={canEdit ? "hover:bg-muted/50 cursor-pointer" : ""}
                    onClick={canEdit ? () => setDrawerId(t.id) : undefined}
                  >
                    <TableCell className="text-muted-foreground tabular-nums">{t.id}</TableCell>
                    <TableCell className="font-medium">
                      {t.title ? `${t.title} ` : ""}
                      {t.nameRaw || t.name}
                    </TableCell>
                    <TableCell className="text-muted-foreground max-w-[16rem] truncate">
                      {t.org || "—"}
                    </TableCell>
                    <TableCell className="text-muted-foreground">{t.email || "—"}</TableCell>
                    <TableCell className="text-muted-foreground">{t.phone || "—"}</TableCell>
                    <TableCell className="text-right tabular-nums">{lop.length}</TableCell>
                    <TableCell className="text-right tabular-nums">
                      {tongTiet(classes, t.id) || "—"}
                    </TableCell>
                    <TableCell>
                      {daKhai > 0 ? (
                        <Pill tone="emerald">{daKhai} tiết đã khai</Pill>
                      ) : (
                        <Pill tone="slate">chưa khai — tự do cả tuần</Pill>
                      )}
                    </TableCell>
                    <TableCell>
                      {t.inLecturerList === true && <Pill tone="emerald">danh sách cơ hữu</Pill>}
                      {t.inLecturerList === false && <Pill tone="slate">ngoài danh sách</Pill>}
                      {t.inLecturerList == null && (
                        <Pill tone="amber">đoán từ ô đơn vị</Pill>
                      )}
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </div>

        <div className="text-muted-foreground border-t px-3 py-2 text-xs">
          <GraduationCap className="mr-1 inline size-3.5" />
          {loai === "GUEST"
            ? "Mời giảng viên thỉnh giảng, cập nhật hồ sơ và giờ có thể dạy."
            : permissions.canDeclareOwnAvailability
              ? "Hồ sơ đã chọn là lựa chọn mô phỏng; ứng dụng không xác minh danh tính."
              : "Trợ lý khoa có thể cập nhật giờ rảnh thay giảng viên cơ hữu."}
        </div>
      </div>

      {drawerId != null && (
        <TeacherEditDrawer
          data={data}
          teacher={drawerTeacher}
          onClose={() => setDrawerId(null)}
          mode={loai === "GUEST" ? "guest" : "availability"}
        />
      )}
    </div>
  );
}
