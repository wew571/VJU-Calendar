import { useState } from "react";
import { Lock, TriangleAlert } from "lucide-react";
import { useAppData } from "../../context/AppDataContext";
import { Notice } from "@/components/shared/notice";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

const NGUOI_KEY = "tkb_nguoi_chot";

function dayNumber(day) {
  if (day == null) return "—";
  return day === 6 ? "CN" : `T${day + 2}`;
}

/**
 * CHOT LICH rieng cho mot lop hoc phan.
 *
 * Chot = ghi gio dang hien tren luoi thanh gio CHINH THUC va khoa lai. Hop thoai
 * cho nguoi dung kiem tra dung ma lop, gio va giang vien truoc khi cam ket.
 */
export default function ChotSectionDialog({ open, onOpenChange, section }) {
  const { loading, doChotSection } = useAppData();
  const [nguoi, setNguoi] = useState(() => {
    try {
      return localStorage.getItem(NGUOI_KEY) || "";
    } catch {
      return "";
    }
  });
  const [note, setNote] = useState("");
  const [error, setError] = useState(null);
  const thieuGio = section?.day == null || section?.periodStart == null;

  const handleChot = async () => {
    setError(null);
    try {
      if (nguoi.trim()) localStorage.setItem(NGUOI_KEY, nguoi.trim());
    } catch {
      /* ignore */
    }
    try {
      await doChotSection(section.sectionId, { by: nguoi, note });
      onOpenChange(false);
      setNote("");
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[85vh] overflow-y-auto sm:max-w-xl">
        <DialogHeader>
          <DialogTitle>Chốt lớp — {section?.classCode || `#${section?.sectionId}`}</DialogTitle>
          <DialogDescription>
            Chỉ lớp này thuộc học phần <strong>{section?.courseName}</strong> sẽ bị ghim cứng.
            Các lớp khác của cùng học phần vẫn có thể sửa hoặc xếp lại độc lập.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-3 text-sm">
          {thieuGio && (
            <Notice tone="amber" icon={TriangleAlert}>
              Lớp này <strong>chưa có giờ</strong>. Hãy chạy xếp lịch hoặc nhập giờ trước khi chốt.
            </Notice>
          )}

          <div className="rounded-lg border px-3 py-2 text-xs">
            <div className="flex items-baseline justify-between gap-2">
              <span className="min-w-0 truncate">
                <span className="font-medium">{section?.classCode || `#${section?.sectionId}`}</span>
                <span className="text-muted-foreground">
                  {" "}· {(section?.teachers ?? []).map((t) => t.name).join(", ") || "chưa phân công"}
                </span>
              </span>
              <span className={thieuGio ? "shrink-0 text-amber-700" : "text-muted-foreground shrink-0 tabular-nums"}>
                {thieuGio
                  ? "chưa có giờ"
                  : `${dayNumber(section.day)} tiết ${section.periodStart}-${section.periodEnd}`}
              </span>
            </div>
          </div>

          <label className="block">
            <span className="text-muted-foreground text-xs">Người chốt</span>
            <Input
              value={nguoi}
              onChange={(e) => setNguoi(e.target.value)}
              placeholder="Tên người chốt (để trống = “Giáo vụ”)"
            />
          </label>

          <label className="block">
            <span className="text-muted-foreground text-xs">Ghi chú</span>
            <Input
              value={note}
              onChange={(e) => setNote(e.target.value)}
              placeholder="Ví dụ: đã xác nhận qua email với cô A ngày 12/8"
            />
          </label>

          {error && (
            <Notice tone="red" icon={TriangleAlert}>
              {error}
            </Notice>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)} disabled={loading}>
            Hủy
          </Button>
          <Button onClick={handleChot} disabled={loading || thieuGio}>
            <Lock className="size-4" />
            {loading ? "Đang chốt…" : "Chốt lớp này"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
