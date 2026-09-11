import { useState } from "react";
import { Download } from "lucide-react";
import * as scheduler from "../../services/schedulerService";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Notice } from "@/components/shared/notice";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

/**
 * Xuat bang "Du lieu hoc phan" ra file .xlsx dung khuon FATE (sheet "FATE", xem
 * webapp/fate_export.py) - dat ten hoc ky de dat ten file va ghi vao dong tieu
 * de trong sheet, giong quy uoc FATE.TKB.<hoc ky>.xlsx dang dung.
 *
 * XUAT THEO BO LOC: mac dinh xuat dung phan dang hien tren bang (giao vu loc
 * CTDT=FTH thi file ra la cua rieng FTH). Gui thang danh sach sectionId dang
 * hien len backend thay vi mo ta lai bo loc - man hinh moi la noi biet chac no
 * dang hien cai gi.
 *
 * Tai file qua apiDownload (POST + blob) chu khong con dieu huong
 * window.location: danh sach id khong nhet vao query string duoc.
 */
export default function ExportExcelDialog({ open, onOpenChange, sectionIdsDangHien, tongSoLop }) {
  const [label, setLabel] = useState("HK1 2026-2027");
  const [chiPhanDangLoc, setChiPhanDangLoc] = useState(true);
  const [dangChay, setDangChay] = useState(false);
  const [loi, setLoi] = useState(null);

  const soDangHien = sectionIdsDangHien?.length ?? 0;
  const coLoc = soDangHien > 0 && tongSoLop != null && soDangHien < tongSoLop;

  const handleExport = async () => {
    setDangChay(true);
    setLoi(null);
    try {
      await scheduler.exportClasses(
        label.trim() || "TKB",
        chiPhanDangLoc && sectionIdsDangHien ? sectionIdsDangHien : null,
      );
      onOpenChange(false);
    } catch (e) {
      setLoi(e.message);
    } finally {
      setDangChay(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Xuất file Excel</DialogTitle>
          <DialogDescription>
            Xuất bảng "Dữ liệu học phần" ra file theo khuôn FATE (sheet "FATE"),
            dùng lại được cho kỳ sau qua "Nhập từ Excel".
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-3">
          <div className="space-y-2">
            <Label htmlFor="export-label">Tên học kỳ</Label>
            <Input
              id="export-label"
              value={label}
              onChange={(e) => setLabel(e.target.value)}
              placeholder="HK1 2026-2027"
              autoFocus
            />
            <p className="text-muted-foreground text-xs">
              Dùng để đặt tên file (FATE.TKB.{label.trim() || "…"}.xlsx) và ghi vào dòng
              tiêu đề trong sheet.
            </p>
          </div>

          <Label htmlFor="export-loc" className="text-sm font-normal">
            <Checkbox
              id="export-loc"
              checked={chiPhanDangLoc}
              onCheckedChange={(v) => setChiPhanDangLoc(v === true)}
            />
            Chỉ xuất phần đang lọc ({soDangHien}
            {tongSoLop != null ? `/${tongSoLop}` : ""} lớp)
          </Label>

          {/* Nạp lại file ĐÃ LỌC bằng chế độ "Thay thế" sẽ xóa các lớp không có
              trong file — nói trước, đây là đường mất dữ liệu dễ vấp nhất khi
              bắt đầu xuất theo từng chương trình. */}
          {chiPhanDangLoc && coLoc && (
            <Notice tone="amber">
              File này chỉ chứa {soDangHien} lớp. Dùng để <strong>gửi đi</strong>; nếu nạp
              lại vào hệ thống, phải chọn "Gộp thêm" — chọn "Thay thế" sẽ xóa{" "}
              {tongSoLop - soDangHien} lớp còn lại.
            </Notice>
          )}

          {loi && <Notice tone="red">{loi}</Notice>}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Hủy
          </Button>
          <Button onClick={handleExport} disabled={dangChay}>
            <Download className="size-4" />
            {dangChay ? "Đang xuất…" : "Xuất file"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
