import { useEffect, useState } from "react";
import { CopyPlus, Plus, TriangleAlert, Trash2, X } from "lucide-react";
import { useAppData } from "../../context/AppDataContext";
import ClassTimeSlotPicker from "./ClassTimeSlotPicker";
import { FilterSelect } from "@/components/shared/filter-select";
import { FormRow } from "@/components/shared/form-row";
import { Notice } from "@/components/shared/notice";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Dialog, DialogClose, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { DrawerBody, DrawerSection } from "@/components/ui/drawer";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { NativeSelect } from "@/components/ui/native-select";

const LOCATION_OPTIONS = ["Hòa Lạc", "Mỹ Đình", "Khác"];
const TEACHING_MODE_OPTIONS = ["Trực tiếp", "Trực tuyến", "LMS"];

function suggestTeacherType(org) {
  const t = (org || "").toLowerCase();
  return t.includes("việt nhật") || t.includes("viet nhat") ? "RESIDENT" : "GUEST";
}

function emptyForm() {
  return {
    teacherIds: [""], courseId: "", classCode: "", program: "",
    ltCredits: "", thCredits: "", cohort: "", expectedStudents: "",
    duration: "2", autoSchedule: true, day: null, periodStart: null, periodEnd: null,
    location: "", teachingMode: "", language: "", otherRequirements: "", notes: "",
    coordinatorOverride: "", prevTeacherName: "", prevTeacherOrg: "",
    teachingHoursLt: "", teachingHoursTh: "",
  };
}

function formFromClass(c) {
  return {
    // MOI giang vien cua lop, vai tro ngang nhau (khong co "GV chinh").
    teacherIds: (c.teacherIds?.length ? c.teacherIds : [c.teacherId]).map(String),
    courseId: c.courseId != null ? String(c.courseId) : "",
    classCode: c.classCode || "", program: c.programName || "",
    ltCredits: c.ltCredits ?? "", thCredits: c.thCredits ?? "",
    cohort: c.cohort || "", expectedStudents: c.expectedStudents ?? "",
    duration: String(c.duration ?? "2"), autoSchedule: c.timeAssumed,
    day: c.day, periodStart: c.periodStart, periodEnd: c.periodEnd,
    location: c.location || "", teachingMode: c.teachingMode || "",
    language: c.language || "", otherRequirements: c.otherRequirements || "", notes: c.notes || "",
    coordinatorOverride: c.coordinatorOverride || "",
    prevTeacherName: c.prevTeacherName || "", prevTeacherOrg: c.prevTeacherOrg || "",
    teachingHoursLt: c.teachingHoursLt ?? "", teachingHoursTh: c.teachingHoursTh ?? "",
  };
}

// Side-panel: tao lop moi (section=null) hoac sua lop da co (section=1 dong tu
// data.classes). Tu goi useAppData() truc tiep (khong qua props tu trang cha) vi
// day la 1 "man con" kha doc lap voi nhieu hanh dong rieng (them GV nhanh,
// luu, xoa) - giam prop-drilling qua ManualEntryPage.
// onOpenTeacher: mo ngan cua MOT giang vien trong lop (de sua thong tin/khai gio
// co the day) - trang cha giu state ngan nao dang mo nen phai di qua props.
export default function SectionEditDrawer({ data, section, onClose, onDuplicated, onOpenTeacher }) {
  const { loading, addManualTeacher, addManualSection, updateManualSection, deleteManualSection, doBoQua } = useAppData();
  const [form, setForm] = useState(section ? formFromClass(section) : emptyForm());
  const [error, setError] = useState(null);
  const [showAddTeacher, setShowAddTeacher] = useState(false);
  const [newTeacher, setNewTeacher] = useState({ name: "", org: "", teacherType: "GUEST" });

  // Khoa theo sectionId (so nguyen on dinh), KHONG khoa theo object 'section':
  // moi lan them nhanh GV (+ Giang vien moi) lam setData()
  // thay THE CA data -> selectedSection ben ManualEntryPage la object MOI du cung
  // sectionId, neu dependency la object se reset mat sach cac o khac dang go nua
  // chung. Chi reset khi THUC SU chuyen sang sua 1 lop khac (hoac dong/mo lai).
  const sectionKey = section?.sectionId ?? "new";
  useEffect(() => {
    setForm(section ? formFromClass(section) : emptyForm());
    setError(null);
    setShowAddTeacher(false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sectionKey]);

  const teachers = data?.teachers || [];
  const courses = data?.courses || [];
  const numDays = data?.numDays ?? 7;
  const slotsPerDay = data?.slotsPerDay ?? 12;
  const teacherTypeFor = (ids) => ids.some((id) => teachers.find((t) => String(t.id) === String(id))?.type === "GUEST")
    ? "GUEST"
    : "RESIDENT";
  const maxDayFor = (ids) => Math.min(numDays - 1, teacherTypeFor(ids) === "GUEST" ? 5 : 4);
  const maxDayIndex = maxDayFor(form.teacherIds.filter(Boolean));

  const set = (key) => (e) => setForm((f) => ({ ...f, [key]: e.target.value }));
  const setDuration = (e) => {
    const duration = e.target.value;
    setForm((f) => {
      if (section?.sectionChot || f.day == null) return { ...f, duration };
      const selectedLength = f.periodEnd - f.periodStart + 1;
      return selectedLength === Number(duration)
        ? { ...f, duration }
        : { ...f, duration, day: null, periodStart: null, periodEnd: null };
    });
  };
  const setTeacherAt = (index, teacherId) => setForm((f) => {
    const teacherIds = f.teacherIds.map((id, i) => (i === index ? teacherId : id));
    const invalidDay = !section?.sectionChot && f.day != null && f.day > maxDayFor(teacherIds.filter(Boolean));
    return {
      ...f,
      teacherIds,
      ...(invalidDay ? { day: null, periodStart: null, periodEnd: null } : {}),
    };
  });
  const removeTeacherAt = (index) => setForm((f) => {
    const teacherIds = f.teacherIds.filter((_, i) => i !== index);
    const invalidDay = !section?.sectionChot && f.day != null && f.day > maxDayFor(teacherIds.filter(Boolean));
    return {
      ...f,
      teacherIds,
      ...(invalidDay ? { day: null, periodStart: null, periodEnd: null } : {}),
    };
  });

  const submitNewTeacher = async (e) => {
    e.preventDefault();
    if (!newTeacher.name.trim()) return;
    const res = await addManualTeacher({
      name: newTeacher.name.trim(), org: newTeacher.org.trim(), teacherType: newTeacher.teacherType,
    });
    const created = res.teachers[res.teachers.length - 1];
    // GV vua tao vao dong dang trong dau tien, khong thi them dong moi.
    setForm((f) => {
      const i = f.teacherIds.findIndex((x) => !x);
      const ids = [...f.teacherIds];
      if (i >= 0) ids[i] = String(created.id);
      else ids.push(String(created.id));
      return { ...f, teacherIds: ids };
    });
    setNewTeacher({ name: "", org: "", teacherType: "GUEST" });
    setShowAddTeacher(false);
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setError(null);
    if (!form.teacherIds.filter(Boolean).length) return setError("Chưa chọn giảng viên.");
    if (!form.courseId) return setError("Chưa chọn học phần.");
    const duration = Number(form.duration);
    if (!Number.isInteger(duration) || duration <= 0 || duration > slotsPerDay) {
      return setError(`Số tiết mỗi buổi dạy phải là số nguyên từ 1 đến ${slotsPerDay}.`);
    }
    if (!form.autoSchedule && (form.day == null || form.periodStart == null || form.periodEnd == null)) {
      return setError("Chưa chọn giờ — bấm một ô trong bảng tuần, hoặc chọn \"Để hệ thống tự xếp giờ\".");
    }
    const originalTimeUnchanged = section
      && form.day === section.day
      && form.periodStart === section.periodStart
      && form.periodEnd === section.periodEnd;
    if (section?.sectionChot && !form.autoSchedule) {
      const teacherIdsUnchanged = form.teacherIds.filter(Boolean).map(Number).join(",")
        === (section.teacherIds?.length ? section.teacherIds : [section.teacherId]).map(Number).join(",");
      if (!teacherIdsUnchanged && form.day > maxDayIndex) {
        return setError("Nhóm giảng viên mới không được chọn ngày đang khóa. Hãy bỏ chốt lớp trước khi đổi giảng viên.");
      }
      if (duration !== Number(section.duration)
        && form.periodEnd - form.periodStart + 1 !== duration) {
        return setError("Không thể đổi Số tiết / buổi làm lệch giờ đang khóa. Hãy bỏ chốt lớp trước.");
      }
    }
    if (!form.autoSchedule && !section?.sectionChot && !originalTimeUnchanged) {
      if (form.day < 0 || form.day >= numDays || form.day > maxDayIndex
        || form.periodStart < 1 || form.periodEnd > slotsPerDay
        || form.periodEnd - form.periodStart + 1 !== duration) {
        return setError("Giờ đã chọn không còn hợp lệ với số tiết hoặc nhóm giảng viên. Vui lòng chọn lại.");
      }
    }

    const payload = {
      teacherIds: form.teacherIds.filter(Boolean).map(Number),
      courseId: Number(form.courseId),
      classCode: form.classCode.trim(), program: form.program.trim(),
      ltCredits: form.ltCredits === "" ? 0 : Number(form.ltCredits),
      thCredits: form.thCredits === "" ? 0 : Number(form.thCredits),
      cohort: form.cohort.trim(),
      expectedStudents: form.expectedStudents === "" ? null : Number(form.expectedStudents),
      duration: Number(form.duration),
      location: form.location, teachingMode: form.teachingMode,
      language: form.language.trim(), otherRequirements: form.otherRequirements.trim(),
      notes: form.notes.trim(), coordinatorOverride: form.coordinatorOverride.trim(),
      prevTeacherName: form.prevTeacherName.trim(), prevTeacherOrg: form.prevTeacherOrg.trim(),
      teachingHoursLt: form.teachingHoursLt === "" ? null : Number(form.teachingHoursLt),
      teachingHoursTh: form.teachingHoursTh === "" ? null : Number(form.teachingHoursTh),
    };
    if (form.autoSchedule) {
      payload.autoSchedule = true;
    } else {
      payload.day = form.day;
      payload.periodStart = form.periodStart;
      payload.periodEnd = form.periodEnd;
    }

    try {
      if (section) await updateManualSection(section.sectionId, payload);
      else await addManualSection(payload);
      onClose();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDelete = async () => {
    if (!section) return;
    if (!window.confirm(`Xóa lớp "${section.classCode || section.courseName}" (#${section.sectionId})? Không thể hoàn tác.`)) return;
    await deleteManualSection(section.sectionId);
    onClose();
  };

  // "1 lop hoc N buoi/tuan khac ngay" = N dong cung Ma lop, khac Thoi gian (xem
  // giai thich voi giao vu) - nut nay sao chep MOI THONG TIN DANG CO trong form
  // (hoc phan/GV/TC/dia diem...) sang 1 dong MOI, CHI xoa rieng gio (bat auto)
  // de khoi phai go lai tu dau, rieng gio thi bat buoc chon lai cho buoi khac.
  const handleDuplicate = async () => {
    setError(null);
    if (!form.teacherIds.filter(Boolean).length || !form.courseId) {
      return setError("Cần chọn học phần và giảng viên trước khi nhân bản.");
    }
    const payload = {
      teacherIds: form.teacherIds.filter(Boolean).map(Number),
      courseId: Number(form.courseId),
      classCode: form.classCode.trim(), program: form.program.trim(),
      ltCredits: form.ltCredits === "" ? 0 : Number(form.ltCredits),
      thCredits: form.thCredits === "" ? 0 : Number(form.thCredits),
      cohort: form.cohort.trim(),
      expectedStudents: form.expectedStudents === "" ? null : Number(form.expectedStudents),
      duration: Number(form.duration) || 2,
      location: form.location, teachingMode: form.teachingMode,
      language: form.language.trim(), otherRequirements: form.otherRequirements.trim(),
      notes: form.notes.trim(), coordinatorOverride: form.coordinatorOverride.trim(),
      prevTeacherName: form.prevTeacherName.trim(), prevTeacherOrg: form.prevTeacherOrg.trim(),
      teachingHoursLt: form.teachingHoursLt === "" ? null : Number(form.teachingHoursLt),
      teachingHoursTh: form.teachingHoursTh === "" ? null : Number(form.teachingHoursTh),
      autoSchedule: true, // buoi moi CHUA co gio - bat GV chon rieng cho buoi nay
    };
    try {
      const res = await addManualSection(payload);
      const created = res.classes[res.classes.length - 1];
      onDuplicated?.(created.sectionId);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <Dialog open onOpenChange={(o) => !o && onClose()}>
      <DialogContent
        showCloseButton={false}
        className="teacher-edit-dialog manual-edit-glass flex h-[min(750px,calc(100dvh-2rem))] w-[min(1500px,calc(100vw-2rem))] max-w-none flex-col gap-0 overflow-hidden p-0"
      >
        <DialogHeader className="flex shrink-0 flex-row items-center justify-between gap-3 border-b px-5 py-3">
          <DialogTitle className="text-xl tracking-tight">
            {section ? `Sửa lớp ${section.classCode || `#${section.sectionId}`}` : "Thêm lớp mới"}
          </DialogTitle>
          <DialogDescription className="sr-only">Chỉnh sửa thông tin lớp học phần.</DialogDescription>
          <DialogClose className="text-muted-foreground hover:bg-muted hover:text-foreground focus-visible:ring-ring/50 inline-flex size-8 shrink-0 items-center justify-center rounded-md transition-colors focus-visible:ring-[3px] focus-visible:outline-none">
            <X className="size-4" />
            <span className="sr-only">Đóng</span>
          </DialogClose>
        </DialogHeader>
        <form id="section-form" onSubmit={handleSave} className="flex min-h-0 flex-1 flex-col">
          <DrawerBody className="grid grid-cols-1 !space-y-0 !overflow-y-auto !p-0 min-[1100px]:grid-cols-3 min-[1100px]:!overflow-hidden">
            <div className="min-h-0 min-w-0 space-y-5 px-5 py-4 min-[1100px]:overflow-y-auto">
              {error && (
                <Notice tone="red" icon={TriangleAlert}>
                  {error}
                </Notice>
              )}

          <DrawerSection title="Học phần">
            <FormRow label="Học phần" required>
              {(id) => (
                <FilterSelect
                  id={id}
                  label="— Chọn học phần —"
                  emptyLabel="— Chọn học phần —"
                  searchPlaceholder="Tìm mã hoặc tên học phần…"
                  searchable
                  full
                  modal={false}
                  value={form.courseId || null}
                  options={courses.map((c) => ({
                    value: String(c.id),
                    label: c.code ? `${c.code} — ${c.name}` : c.name,
                  }))}
                  onChange={(courseId) => setForm((f) => ({ ...f, courseId: courseId ?? "" }))}
                />
              )}
            </FormRow>
          </DrawerSection>

          <DrawerSection title="Lớp học phần">
            <FormRow label="Mã lớp">
              {(id) => <Input id={id} value={form.classCode} onChange={set("classCode")} placeholder="IT101.1" />}
            </FormRow>
            <FormRow label="Chương trình (CTĐT)">
              {(id) => <Input id={id} value={form.program} onChange={set("program")} placeholder="BCSE" />}
            </FormRow>
            <FormRow label="Phân bổ TC (LT / TH)">
              <div className="flex gap-2">
                <Input type="number" min={0} step="0.5" value={form.ltCredits} onChange={set("ltCredits")} placeholder="Lý thuyết" />
                <Input type="number" min={0} step="0.5" value={form.thCredits} onChange={set("thCredits")} placeholder="Thực hành" />
              </div>
            </FormRow>
            <FormRow label="Khóa">
              {(id) => <Input id={id} value={form.cohort} onChange={set("cohort")} placeholder="K68" />}
            </FormRow>
            <FormRow label="Số SV dự kiến">
              {(id) => <Input id={id} type="number" min={0} value={form.expectedStudents} onChange={set("expectedStudents")} />}
            </FormRow>
            <FormRow label="Số tiết / buổi" required>
              {(id) => <Input id={id} type="number" min={1} max={slotsPerDay} required value={form.duration} onChange={setDuration} />}
            </FormRow>
          </DrawerSection>

          <DrawerSection title="Giờ dạy & hình thức">
            <FormRow label="Số giờ dạy (LT / TH)">
              <div className="flex gap-2">
                <Input type="number" min={0} value={form.teachingHoursLt} onChange={set("teachingHoursLt")} placeholder="Lý thuyết" />
                <Input type="number" min={0} value={form.teachingHoursTh} onChange={set("teachingHoursTh")} placeholder="Thực hành" />
              </div>
            </FormRow>
            <FormRow label="Địa điểm giảng dạy">
              {(id) => (
                <NativeSelect id={id} className="w-full" value={form.location} onChange={set("location")}>
                  <option value="">— Không rõ —</option>
                  {LOCATION_OPTIONS.map((l) => <option key={l} value={l}>{l}</option>)}
                </NativeSelect>
              )}
            </FormRow>
            <FormRow label="Hình thức giảng dạy">
              {(id) => (
                <NativeSelect id={id} className="w-full" value={form.teachingMode} onChange={set("teachingMode")}>
                  <option value="">— Không rõ —</option>
                  {TEACHING_MODE_OPTIONS.map((m) => <option key={m} value={m}>{m}</option>)}
                </NativeSelect>
              )}
            </FormRow>
          </DrawerSection>
            </div>

            <div className="min-h-0 min-w-0 space-y-5 border-white/70 px-5 py-4 min-[1100px]:overflow-y-auto min-[1100px]:border-l">
          <DrawerSection title="Giảng viên kỳ này">
            {/* DANH SACH ngang hang, khong phai "1 GV chinh + tick dong giang".
                Ban tick cu khong theo doi duoc: nguoi thu 2 tro di nam trong mot
                hop tick dai, khong thay email/SDT/don vi cua ho, va nhin khong ra
                lop dang co bao nhieu nguoi. Nay moi nguoi mot dong, doi/xoa tai
                cho, kem nut mo ngan cua chinh nguoi do de khai gio co the day. */}
            {form.teacherIds.map((tid, i) => {
              const gv = teachers.find((t) => String(t.id) === String(tid));
              return (
                <div key={`${tid}-${i}`} className="flex items-start gap-2">
                  <NativeSelect
                    className="w-full"
                    value={tid}
                    onChange={(e) => setTeacherAt(i, e.target.value)}
                  >
                    <option value="">— Chọn giảng viên —</option>
                    {teachers.map((t) => (
                      <option key={t.id} value={t.id}>
                        {t.name} · {t.type === "GUEST" ? "Thỉnh giảng" : "Cơ hữu"}
                      </option>
                    ))}
                  </NativeSelect>
                  {gv && onOpenTeacher && (
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      title="Mở giảng viên này để sửa thông tin / khai giờ có thể dạy"
                      onClick={() => onOpenTeacher(gv.id)}
                    >
                      Giờ dạy
                    </Button>
                  )}
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    disabled={form.teacherIds.length <= 1}
                    title={form.teacherIds.length <= 1 ? "Lớp phải có ít nhất một giảng viên" : "Bỏ người này khỏi lớp"}
                    onClick={() => removeTeacherAt(i)}
                  >
                    <X className="size-4" />
                  </Button>
                </div>
              );
            })}
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={() => setForm((f) => ({ ...f, teacherIds: [...f.teacherIds, ""] }))}
            >
              <Plus className="size-4" />
              Thêm giảng viên cùng dạy
            </Button>
            {!showAddTeacher ? (
              <Button type="button" variant="ghost" size="sm" onClick={() => setShowAddTeacher(true)}>
                <Plus className="size-4" />
                Giảng viên mới
              </Button>
            ) : (
              <div className="bg-muted/40 flex flex-wrap items-center gap-2 rounded-lg border p-2.5">
                <Input
                  className="min-w-36 flex-1"
                  placeholder="Họ tên"
                  value={newTeacher.name}
                  onChange={(e) => setNewTeacher((f) => ({ ...f, name: e.target.value }))}
                />
                <Input
                  className="min-w-36 flex-1"
                  placeholder="Đơn vị công tác"
                  value={newTeacher.org}
                  onChange={(e) =>
                    setNewTeacher((f) => ({ ...f, org: e.target.value, teacherType: suggestTeacherType(e.target.value) }))
                  }
                />
                <NativeSelect
                  value={newTeacher.teacherType}
                  onChange={(e) => setNewTeacher((f) => ({ ...f, teacherType: e.target.value }))}
                >
                  <option value="GUEST">Thỉnh giảng</option>
                  <option value="RESIDENT">Cơ hữu</option>
                </NativeSelect>
                <Button type="button" size="sm" onClick={submitNewTeacher}>Thêm</Button>
                <Button type="button" variant="outline" size="sm" onClick={() => setShowAddTeacher(false)}>
                  Hủy
                </Button>
              </div>
            )}
          </DrawerSection>

          <DrawerSection title="Giảng viên kỳ trước">
            <FormRow label="Họ tên">
              {(id) => <Input id={id} value={form.prevTeacherName} onChange={set("prevTeacherName")} placeholder="Không bắt buộc" />}
            </FormRow>
            <FormRow label="Đơn vị công tác">
              {(id) => <Input id={id} value={form.prevTeacherOrg} onChange={set("prevTeacherOrg")} placeholder="Không bắt buộc" />}
            </FormRow>
          </DrawerSection>

          {/* BỎ QUA MỘT LỚP — trước đây chỉ bỏ qua được cả cụm "lớp do đơn vị
              khác điều phối" ở đầu màn (một nút, một danh sách hệ thống tự đề
              xuất). Nhưng lý do bỏ qua không chỉ có một: môn linh động chỉ ghi
              vào cho có trong danh sách đăng ký cũng là lớp khoa không xếp, và
              nó không nằm trong danh sách đề xuất nào cả.

              Đặt ngay dưới "Hình thức" vì đó là chỗ người dùng vừa trả lời "lớp
              này học kiểu gì" — câu tiếp theo tự nhiên là "vậy có xếp nó không".

              Bấm là ĂN NGAY, không đợi "Lưu": đây là một hành động riêng chứ
              không phải một ô của biểu mẫu, y như "Xóa lớp"/"Thêm buổi khác". */}
          {section && (
            <DrawerSection title="Có xếp lớp này không?">
              <Label htmlFor="sec-bo-qua" className="text-sm font-normal">
                <Checkbox
                  id="sec-bo-qua"
                  checked={!!section.boQua}
                  disabled={loading}
                  onCheckedChange={(v) => doBoQua([section.sectionId], v === true)}
                />
                Bỏ qua lớp này — khoa không xếp
              </Label>
              {/* Lớp học chung là MỘT buổi dạy, bỏ qua nửa nhóm là vô nghĩa nên
                  backend kéo cả nhóm đi theo (domain/bo_qua.py: _lan_hoc_chung).
                  Phải nói trước, không thì bấm một lớp mà mất ba. */}
              {section.hocChungWith?.length > 0 && (
                <p className="text-muted-foreground text-xs">
                  Lớp này học chung một buổi với {section.hocChungWith.length} lớp khác — cả nhóm
                  sẽ được bỏ qua cùng.
                </p>
              )}
            </DrawerSection>
          )}

          <details className="rounded-lg border">
            <summary className="hover:bg-muted/60 cursor-pointer rounded-lg px-3 py-2 text-sm font-medium">
              Khác (ngôn ngữ, yêu cầu khác, ghi chú, điều phối viên)
            </summary>
            <div className="space-y-3 border-t px-3 py-3">
              <FormRow label="Ngôn ngữ giảng dạy">
                {(id) => <Input id={id} value={form.language} onChange={set("language")} placeholder="Không bắt buộc" />}
              </FormRow>
              <FormRow label="Yêu cầu khác">
                {(id) => <Input id={id} value={form.otherRequirements} onChange={set("otherRequirements")} placeholder="Không bắt buộc" />}
              </FormRow>
              <FormRow label="Ghi chú">
                {(id) => <Input id={id} value={form.notes} onChange={set("notes")} placeholder="Không bắt buộc" />}
              </FormRow>
              <FormRow label="Điều phối viên">
                {(id) => <Input id={id} value={form.coordinatorOverride} onChange={set("coordinatorOverride")} placeholder="Nếu khác mặc định" />}
              </FormRow>
            </div>
          </details>
            </div>

            <div className="min-h-0 min-w-0 space-y-5 border-white/70 px-5 py-4 min-[1100px]:overflow-y-auto min-[1100px]:border-l">
              <DrawerSection title="Thời gian">
                <Label htmlFor="sed-auto" className="text-sm font-normal">
                  <Checkbox
                    id="sed-auto"
                    checked={form.autoSchedule}
                    disabled={!!section?.sectionChot}
                    onCheckedChange={(v) =>
                      setForm((f) => ({
                        ...f,
                        autoSchedule: v === true,
                        day: null, periodStart: null, periodEnd: null,
                      }))
                    }
                  />
                  Để hệ thống tự xếp giờ
                </Label>
                {!form.autoSchedule && (
                  <ClassTimeSlotPicker
                    numDays={numDays}
                    slotsPerDay={slotsPerDay}
                    duration={form.duration}
                    maxDayIndex={maxDayIndex}
                    disabled={!!section?.sectionChot}
                    value={form.day != null ? { day: form.day, periodStart: form.periodStart, periodEnd: form.periodEnd } : null}
                    onChange={(v) => setForm((f) => ({ ...f, day: v?.day ?? null, periodStart: v?.periodStart ?? null, periodEnd: v?.periodEnd ?? null }))}
                  />
                )}
              </DrawerSection>
            </div>
          </DrawerBody>
          <DialogFooter className="shrink-0 flex-row flex-wrap items-center border-t px-5 py-3">
            {section && (
              <Button
                type="button"
                variant="outline"
                className="text-destructive min-[640px]:mr-auto"
                disabled={loading}
                onClick={handleDelete}
              >
                <Trash2 className="size-4" />
                Xóa lớp
              </Button>
            )}
            {section && (
              <Button type="button" variant="outline" disabled={loading} onClick={handleDuplicate}>
                <CopyPlus className="size-4" />
                Thêm buổi khác
              </Button>
            )}
            {/* "Hủy" ro rang canh "Lưu" - dua vao dau X goc tren hoac Esc de
                thoat la bat nguoi dung phai DOAN rang bo di thi khong ghi gi. */}
            <Button type="button" variant="outline" disabled={loading} onClick={onClose}>
              Hủy
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? "Đang lưu…" : "Lưu"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
