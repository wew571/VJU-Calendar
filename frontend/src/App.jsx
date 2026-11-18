import { useEffect, useState } from "react";
import { AppLayout } from "@/components/layout/app-layout";
import {
  NAV_HOME,
  PAGE_LABELS,
  firstSubKey,
  subLabel,
} from "./constants/nav";
import { EventLogProvider } from "./context/EventLogContext";
import { AppDataProvider, useAppData } from "./context/AppDataContext";
import Footer from "./presentation/Footer";
import RolePickerScreen from "./presentation/RolePickerScreen";
import DataPage from "./presentation/pages/DataPage";
import SchedulePage from "./presentation/pages/SchedulePage";
import HistoryPage from "./presentation/pages/HistoryPage";
import ManualEntryPage from "./presentation/pages/ManualEntryPage";
import GuidePage from "./presentation/pages/GuidePage";
import { readUrlState, writeUrlState } from "./adapters/urlState";
import { danhSachChuongTrinh } from "./adapters/phamVi";
import { clampPageForRole, clampSubForRole, isRole } from "./constants/roles";

const PAGES = {
  data: DataPage,
  schedule: SchedulePage,
  history: HistoryPage,
  manual: ManualEntryPage,
  guide: GuidePage,
};

// "Dang nhap" o day chi la chon vai trò (xem RolePickerScreen) - truoc day
// role song trong React state THUAN, khong luu o dau ca, nen bam F5 la mat:
// toan cay component (ke ca AppShell) mount lai tu dau, role ve lai null ->
// hien RolePickerScreen, du activePage/sub/filter van con nho dung nho URL
// hash (xem urlState.js). Luu vao localStorage - cung pattern voi SIDEBAR_KEY
// o app-layout.jsx - de F5 giu duoc vai tro dang chon, giong cach cac trang
// khac giu duoc vi tri dang xem.
const ROLE_KEY = "tkb_role";
const PROGRAM_KEY = "tkb_program";

function loadRole() {
  if (typeof window === "undefined") return null;
  try {
    const r = localStorage.getItem(ROLE_KEY);
    if (r === "staff") return "assistant";
    return isRole(r) ? r : null;
  } catch {
    return null;
  }
}

function loadProgram() {
  if (typeof window === "undefined") return "";
  try {
    return localStorage.getItem(PROGRAM_KEY) || "";
  } catch {
    return "";
  }
}

function saveRole(r, program) {
  try {
    if (r) {
      localStorage.setItem(ROLE_KEY, r);
      if (program) localStorage.setItem(PROGRAM_KEY, program);
      else localStorage.removeItem(PROGRAM_KEY);
    } else {
      localStorage.removeItem(ROLE_KEY);
    }
  } catch {
    /* ignore */
  }
}

// "Du lieu hoc phan" la bang mirror 29 cot Excel - rong hon man hinh ngay ca o
// man rong nhat. Cho no tran sat mep vung noi dung thay vi ngoi trong the co
// padding: moi px be ngang deu dang gia. Cac trang con lai giu padding chuan.
const BLEED_PAGES = new Set(["manual"]);

// Trang TU LO cuon doc thay vi de <main> cuon ca trang (xem `fullHeight` trong
// AppLayout). "Du lieu hoc phan" can dieu nay de DONG BANG hang tieu de 2 tang +
// 5 cot dau cua bang: sticky chi bam duoc vao khung cuon gan nhat, nen chinh
// khung cuon cua bang phai la thu cuon doc.
const FULL_HEIGHT_PAGES = new Set(["manual"]);

function AppShell() {
  const { data } = useAppData();
  const programs = danhSachChuongTrinh(data);
  const [role, setRoleState] = useState(loadRole);
  const [program, setProgram] = useState(loadProgram);
  const setRole = (r, assignedProgram = "") => {
    setRoleState(r);
    setProgram(assignedProgram);
    saveRole(r, assignedProgram);
  };
  const initial = readUrlState();
  const [activePage, setActivePage] = useState(initial.page || "data");
  const [sub, setSub] = useState(initial.sub);
  const [filter, setFilter] = useState(initial.filter);
  const [manualViewState, setManualViewState] = useState();
  const [manualFocusRequest, setManualFocusRequest] = useState(null);

  // Ghi lai SAFE PAGE (sau kep), khong ghi activePage tho - neu khong URL co the
  // noi "p=data" trong luc noi dung dang hien thuc te la "schedule" (da bi kep
  // vi role viewer), gay lech giua URL va man dang thay.
  useEffect(() => {
    const page = clampPageForRole(activePage, role);
    writeUrlState({ page, sub: clampSubForRole(page, sub, role), filter });
  }, [activePage, sub, filter, role]);

  if (!role) {
    return (
      <RolePickerScreen
        programs={programs}
        initialProgram={program}
        onPick={(r, assignedProgram) => {
          setRole(r, assignedProgram);
          const next = clampPageForRole(initial.page || NAV_HOME.key, r);
          setActivePage(next);
          setSub(clampSubForRole(next, initial.sub ?? firstSubKey(next), r));
        }}
      />
    );
  }

  // Kep lai ngay ca khi role da co san (vd URL doi hash trong luc dang xem, hoac
  // component nay re-mount) - khong chi luc chon role o RolePickerScreen.
  const safePage = clampPageForRole(activePage, role);
  const safeSub = clampSubForRole(safePage, sub, role);
  const ActivePageComponent = PAGES[safePage] || DataPage;

  // Sidebar cap 2 truyen ca (page, sub). Bam vao NHOM (sub = null) thi rot ve
  // muc con dau tien - nhom khong co man rieng, no chi la cai vo.
  const goto = (pageKey, subKey) => {
    const page = clampPageForRole(pageKey, role);
    setActivePage(page);
    setSub(clampSubForRole(page, subKey ?? firstSubKey(page), role));
  };

  const openManualSections = (targets) => {
    setManualFocusRequest((current) => ({ targets, seq: (current?.seq ?? 0) + 1 }));
    goto("manual");
  };

  const currentSubLabel = subLabel(safePage, safeSub);

  return (
    <AppLayout
      page={safePage}
      sub={safeSub}
      role={role}
      // Co muc con -> ten muc con lam tieu de, ten nhom lam duong dan phia tren.
      title={currentSubLabel ?? PAGE_LABELS[safePage]}
      crumbs={currentSubLabel ? PAGE_LABELS[safePage] : null}
      bleed={BLEED_PAGES.has(safePage)}
      fullHeight={FULL_HEIGHT_PAGES.has(safePage)}
      onNavigate={goto}
      onChangeRole={() => setRole(null)}
      footer={<Footer />}
    >
      <ActivePageComponent
        role={role}
        sub={safeSub}
        assignedProgram={program}
        onSubChange={setSub}
        filter={filter}
        onFilterChange={setFilter}
        viewState={manualViewState}
        onViewStateChange={setManualViewState}
        focusRequest={manualFocusRequest}
        onFocusHandled={(seq) => setManualFocusRequest((request) => request?.seq === seq ? null : request)}
        onOpenManualSections={openManualSections}
      />
    </AppLayout>
  );
}

export default function App() {
  return (
    <EventLogProvider>
      <AppDataProvider>
        <AppShell />
      </AppDataProvider>
    </EventLogProvider>
  );
}
