import { Eye, TriangleAlert, Users } from "lucide-react";
import { Button } from "@/components/ui/button";
import { NativeSelect } from "@/components/ui/native-select";
import { ThemeSwitcher } from "@/components/layout/theme-switcher";
import { useEffect, useState } from "react";
import { ROLE_DEFINITIONS } from "@/constants/roles";

// Thay LoginScreen gốc (JWT thật) — công cụ demo này không có hệ thống tài
// khoản, nên "đăng nhập" chỉ là chọn vai trò để giới hạn các màn hình được
// vào (tránh 1 người xem vô tình bấm giải lại/nạp đè dữ liệu người khác đang
// xem, vì STATE phía Flask là dùng chung 1 phiên duy nhất).
//
// Dung style man dang nhap cua app Nhap hoc: nen do dam (token --sidebar - bo
// token nay o reference CHI dung cho man dang nhap, khong phai cho sidebar),
// khoi thuong hieu o giua, the trang do bong.
export default function RolePickerScreen({ onPick, programs, initialProgram }) {
  const [selectedProgram, setSelectedProgram] = useState(initialProgram || programs[0] || "");

  useEffect(() => {
    if (!programs.includes(selectedProgram)) setSelectedProgram(programs[0] || "");
  }, [programs, selectedProgram]);

  return (
    <div className="liquid-role-canvas relative flex min-h-dvh items-center justify-center p-4">
      <ThemeSwitcher className="absolute top-3 right-3" />
      <div className="w-full max-w-sm">
        {/* Thương hiệu */}
        <div className="mb-6 flex flex-col items-center gap-2 text-center">
          <span className="glass-brand-mark flex size-12 items-center justify-center rounded-xl text-sm font-bold tracking-tight text-white">
            VJU
          </span>
          <div>
            <p className="text-foreground text-lg font-semibold">Xếp thời khoá biểu</p>
            <p className="text-muted-foreground text-sm">Phòng Đào tạo</p>
          </div>
        </div>

        {/* Thẻ chọn vai trò */}
        <div className="glass-hero-card rounded-2xl border p-6">
          <h1 className="text-lg font-semibold">Vào công cụ xếp TKB</h1>
          <p className="text-muted-foreground mt-1 text-sm">
            Chọn hồ sơ nghiệp vụ để xem giao diện và luồng thao tác phù hợp.
          </p>

          <div className="mt-5 space-y-4">
            <div className="space-y-2 rounded-lg border p-3">
              <p className="text-sm font-medium">{ROLE_DEFINITIONS.gdct.label}</p>
              <p className="text-muted-foreground text-xs">{ROLE_DEFINITIONS.gdct.description}</p>
              <label className="text-sm font-medium" htmlFor="gdct-program">
                CTĐT GĐCT phụ trách
              </label>
              <NativeSelect
                id="gdct-program"
                value={selectedProgram}
                onChange={(event) => setSelectedProgram(event.target.value)}
                disabled={programs.length === 0}
              >
                {programs.length === 0 ? (
                  <option value="">Chưa có CTĐT trong dữ liệu</option>
                ) : programs.map((program) => (
                  <option key={program} value={program}>{program}</option>
                ))}
              </NativeSelect>
              <Button
                type="button"
                className="w-full"
                disabled={!selectedProgram}
                onClick={() => onPick("gdct", selectedProgram)}
              >
                Vào với hồ sơ GĐCT
              </Button>
            </div>

            {["dpct", "assistant", "resident"].map((role) => {
              const details = ROLE_DEFINITIONS[role];
              return (
                <div className="space-y-1.5" key={role}>
                  <Button
                    type="button"
                    variant="outline"
                    className="h-11 w-full justify-start"
                    onClick={() => onPick(role)}
                  >
                    <Users className="size-4" />
                    {details.label}
                  </Button>
                  <p className="text-muted-foreground text-xs">{details.description}</p>
                </div>
              );
            })}

            <div className="space-y-1.5">
              <Button
                type="button"
                variant="outline"
                className="h-11 w-full"
                onClick={() => onPick("viewer")}
              >
                <Eye className="size-4" />
                Xem thôi
              </Button>
              <p className="text-muted-foreground text-xs">
                Chỉ tra cứu lịch giảng viên, xem check trùng và nhật ký — không
                sinh/giải lại dữ liệu.
              </p>
            </div>
          </div>

          <p className="bg-muted/60 text-muted-foreground mt-4 flex items-start gap-1.5 rounded-md p-2 text-xs">
            <TriangleAlert className="mt-px size-3.5 shrink-0" />
            <span>
              Đây chỉ là hồ sơ giao diện cục bộ, <span className="text-foreground font-medium">
              không xác thực người dùng và không bảo vệ API</span>. Chọn vai trò
              không phải cơ chế phân quyền tài khoản.
            </span>
          </p>
        </div>
      </div>
    </div>
  );
}
