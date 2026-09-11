import { useMemo } from "react";
import { Target, X } from "lucide-react";
import {
  chuanHoa,
  coPhamVi,
  danhSachChuongTrinh,
  danhSachKhoa,
  demPhamVi,
} from "../../adapters/phamVi";
import { FilterSelect } from "@/components/shared/filter-select";
import { Pill } from "@/components/shared/pill";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { cn } from "@/lib/utils";

// CHỌN PHẠM VI XẾP — "lần bấm Xếp này áp cho chương trình nào".
//
// Vì sao là một khối riêng chứ không nhét vào thanh lọc: thanh lọc quyết định
// NHÌN THẤY gì, khối này quyết định hệ thống ĐƯỢC PHÉP ĐỔI GIỜ của lớp nào —
// hai việc khác hẳn nhau và nhầm lẫn thì hậu quả cũng khác hẳn. Đặt ngay trên
// thanh tiến trình để đọc theo đúng thứ tự: "xếp cho ai" rồi mới tới "bấm gì".
//
// Chương trình chọn MỘT (một GĐCT phụ trách một CTĐT), khóa chọn NHIỀU: nhu cầu
// thật là "FTH khóa 2026, 2025 và 2024" trong cùng một lần xếp.
export default function PhamViXepPanel({ data, phamVi, onChange, disabled, ketQuaPhamVi }) {
  const programs = danhSachChuongTrinh(data);
  const chuongTrinh = phamVi?.programs?.[0] ?? null;
  const khoaDaChon = phamVi?.cohorts ?? [];

  // Khóa hiện ra ĐI THEO chương trình đang chọn — xem adapters/phamVi.js.
  const khoas = useMemo(
    () => danhSachKhoa(data, chuongTrinh ? [chuongTrinh] : []),
    [data, chuongTrinh],
  );
  const dem = useMemo(() => demPhamVi(data, phamVi), [data, phamVi]);
  const dangCoPhamVi = coPhamVi(phamVi);

  const datChuongTrinh = (v) =>
    // Đổi chương trình thì bỏ hết khóa đang tick: khóa của CTĐT cũ có thể không
    // tồn tại ở CTĐT mới, để lại là phạm vi rỗng lớp mà nhìn vẫn như có chọn.
    onChange(chuanHoa({ programs: v ? [v] : [], cohorts: [] }));

  const bat = (khoa) =>
    onChange(
      chuanHoa({
        programs: chuongTrinh ? [chuongTrinh] : [],
        cohorts: khoaDaChon.includes(khoa)
          ? khoaDaChon.filter((k) => k !== khoa)
          : [...khoaDaChon, khoa],
      }),
    );

  return (
    <div
      className={cn(
        "bg-card flex flex-wrap items-center gap-x-3 gap-y-2 rounded-xl border p-3 shadow-sm",
        // Đang xếp cho một phạm vi là trạng thái ĐẶC BIỆT (nút Xếp sẽ không đụng
        // tới phần còn lại của khoa) — phải nhìn ra ngay, không để lẫn với thanh
        // lọc bên dưới. Chỉ đổi viền, không đặt nền: cn() là tailwind-merge, đặt
        // bg-* sẽ xóa mất bg-card (xem chú thích cùng loại ở WorkflowStrip).
        dangCoPhamVi && "border-2 border-violet-500/60",
      )}
    >
      <span className="flex items-center gap-1.5 text-sm font-medium">
        <Target className="text-muted-foreground size-4" aria-hidden="true" />
        Xếp cho
      </span>

      <FilterSelect
        label="Toàn khoa"
        searchable
        value={chuongTrinh}
        options={programs}
        onChange={datChuongTrinh}
      />

      {chuongTrinh && khoas.length > 0 && (
        <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
          <span className="text-muted-foreground text-xs">Khoá</span>
          {khoas.map((k) => (
            <Label key={k} htmlFor={`pv-${k}`} className="text-sm font-normal">
              <Checkbox
                id={`pv-${k}`}
                checked={khoaDaChon.includes(k)}
                onCheckedChange={() => bat(k)}
                disabled={disabled}
              />
              {k}
            </Label>
          ))}
          {/* Không tick khóa nào = MỌI khóa của chương trình. Phải nói ra, không
              thì giáo vụ tưởng chưa chọn gì là chưa xếp được. */}
          {khoaDaChon.length === 0 && (
            <span className="text-muted-foreground text-xs italic">
              (chưa tick = mọi khoá)
            </span>
          )}
        </div>
      )}

      <div className="ml-auto flex flex-wrap items-center gap-2">
        {dangCoPhamVi ? (
          <>
            <Pill tone="violet">
              {dem.tong} lớp · {dem.chuaCoGio} chưa có giờ
            </Pill>
            {/* Lớp có ô CTĐT ghép ("FTH.ESAS") nằm trong phạm vi của CẢ HAI
                chương trình — đến lượt bên kia bấm Xếp, họ có quyền đổi giờ của
                nó. Muốn giữ cứng thì phải "Chốt lịch theo học phần". */}
            {dem.dungChung > 0 && (
              <Pill tone="amber">{dem.dungChung} lớp dùng chung CTĐT khác</Pill>
            )}
            {/* "Bỏ ghim" một lớp ngoài phạm vi = hai ý muốn ngược nhau của cùng
                một người. Phạm vi thắng (xem webapp/domain/pham_vi.py) nhưng
                không được im lặng, nếu không giáo vụ bấm Bỏ ghim rồi Xếp mà lớp
                đó vẫn đứng yên thì tưởng nút hỏng. */}
            {/* Lời hứa DUY NHẤT của tính năng này vừa bị phá — kêu to nhất. */}
            {ketQuaPhamVi?.ngoaiPhamViBiDoiGio > 0 && (
              <Pill tone="red">
                ⚠ {ketQuaPhamVi.ngoaiPhamViBiDoiGio} buổi ngoài phạm vi bị đổi giờ — báo lỗi
              </Pill>
            )}
            {/* Giờ đang có của các chương trình khác đã xung đột sẵn với nhau
                (thường do file có dòng nhập trùng), nên lần xếp này buộc phải
                đè lên. Không được im lặng. */}
            {ketQuaPhamVi?.ngoaiPhamViMatCho?.length > 0 && (
              <Pill tone="red">
                {ketQuaPhamVi.ngoaiPhamViMatCho.length} buổi của CTĐT khác mất chỗ (
                {ketQuaPhamVi.ngoaiPhamViMatCho.slice(0, 3).map((id) => `#${id}`).join(", ")}
                {ketQuaPhamVi.ngoaiPhamViMatCho.length > 3 ? "…" : ""})
              </Pill>
            )}
            {ketQuaPhamVi?.dongBangBiDay?.length > 0 && (
              <Pill tone="red">
                {ketQuaPhamVi.dongBangBiDay.length} buổi của CTĐT khác bị đè (
                {ketQuaPhamVi.dongBangBiDay.slice(0, 3).map((id) => `#${id}`).join(", ")}
                {ketQuaPhamVi.dongBangBiDay.length > 3 ? "…" : ""})
              </Pill>
            )}
            {ketQuaPhamVi?.boGhimNgoaiPhamVi > 0 && (
              <Pill tone="slate">
                {ketQuaPhamVi.boGhimNgoaiPhamVi} lớp đã bỏ ghim nằm ngoài phạm vi — vẫn giữ chỗ
              </Pill>
            )}
            <Button
              size="sm"
              variant="ghost"
              disabled={disabled}
              onClick={() => onChange(null)}
            >
              <X className="size-4" aria-hidden="true" />
              Bỏ phạm vi
            </Button>
          </>
        ) : (
          <span className="text-muted-foreground text-xs">
            Đang xếp cho toàn khoa — chọn một chương trình để chỉ xếp phần của
            chương trình đó, lớp của các chương trình khác giữ nguyên giờ.
          </span>
        )}
      </div>
    </div>
  );
}
