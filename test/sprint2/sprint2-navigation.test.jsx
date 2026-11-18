import { act, cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import App from "@/App";

vi.mock("@/context/EventLogContext", () => ({ EventLogProvider: ({ children }) => children }));
vi.mock("@/context/AppDataContext", () => ({ AppDataProvider: ({ children }) => children }));
vi.mock("@/components/layout/theme-switcher", () => ({ ThemeSwitcher: () => null }));
vi.mock("@/presentation/Footer", () => ({ default: () => null }));
vi.mock("@/presentation/pages/ManualEntryPage", () => ({ default: () => <div data-testid="route-manual" /> }));
vi.mock("@/presentation/pages/GuidePage", () => ({ default: () => <div data-testid="route-guide" /> }));
vi.mock("@/presentation/pages/HistoryPage", () => ({ default: () => <div data-testid="route-history" /> }));
vi.mock("@/presentation/pages/DataPage", () => ({
  default: ({ sub }) => <div data-testid="route-data">{sub}</div>,
}));
vi.mock("@/presentation/pages/SchedulePage", () => ({
  default: ({ filter, onFilterChange }) => (
    <div data-testid="route-schedule">
      <output data-testid="route-filter">{JSON.stringify(filter)}</output>
      <input aria-label="QA schedule search" value={filter.search} onChange={(event) => onFilterChange({ ...filter, search: event.target.value })} />
    </div>
  ),
}));

// Real App, URL adapter, layout and sidebar. Page bodies/providers are isolated:
// these tests prove shell routing, not backend authorization or page data fetching.
beforeEach(() => {
  localStorage.clear();
  localStorage.setItem("tkb_role", "staff");
  vi.stubGlobal("ResizeObserver", class { observe() {} disconnect() {} });
  vi.stubGlobal("matchMedia", () => ({ matches: false, addEventListener() {}, removeEventListener() {} }));
  window.history.replaceState(null, "", "#p=manual");
});
afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
  window.history.replaceState(null, "", "#");
  localStorage.clear();
});

function assertRoute(page, title) {
  expect(screen.getByTestId(`route-${page}`)).toBeInTheDocument();
  expect(screen.getByRole("heading", { level: 1, name: title })).toBeInTheDocument();
  const menu = within(document.querySelector("aside"));
  expect(menu.getByRole("button", { name: title })).toHaveClass("glass-nav-active");
}
async function travel(direction, page, title) {
  await act(async () => { window.history[direction](); });
  await waitFor(() => expect(new URLSearchParams(window.location.hash.slice(1)).get("p")).toBe(page));
  assertRoute(page, title);
}

describe("Sprint 2 BL02 — URL and browser history", () => {
  it("S2-B02-01: changing a valid hash updates body, title and menu without reload", async () => {
    render(<App />);
    assertRoute("manual", "Dữ liệu học phần");
    await act(async () => { window.location.hash = "p=schedule"; });
    await waitFor(() => assertRoute("schedule", "Thời khoá biểu"));
  });

  it("S2-B02-02: deep links and remount restore subpage and encoded schedule filters [shell portion]", () => {
    window.history.replaceState(null, "", "#p=data&s=availability");
    const first = render(<App />);
    expect(screen.getByTestId("route-data")).toHaveTextContent("availability");
    expect(screen.getByRole("heading", { level: 1, name: "Giảng viên" })).toBeInTheDocument();
    first.unmount();
    const hash = "#p=schedule&programs=CSE&khoas=K2025&guest=1&resident=0&search=QA";
    window.history.replaceState(null, "", hash);
    const second = render(<App />);
    const expected = { programs: ["CSE"], khoas: ["K2025"], guest: true, resident: false, search: "QA" };
    expect(JSON.parse(screen.getByTestId("route-filter").textContent)).toMatchObject(expected);
    second.unmount();
    render(<App />);
    assertRoute("schedule", "Thời khoá biểu");
    expect(JSON.parse(screen.getByTestId("route-filter").textContent)).toMatchObject(expected);
  });

  it("S2-B02-03: Back and Forward preserve the order A-B-C [shell portion]", async () => {
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: "Thời khoá biểu" }));
    assertRoute("schedule", "Thời khoá biểu");
    fireEvent.click(screen.getByRole("button", { name: "Hướng dẫn sử dụng" }));
    assertRoute("guide", "Hướng dẫn sử dụng");
    await travel("back", "schedule", "Thời khoá biểu");
    await travel("back", "manual", "Dữ liệu học phần");
    await travel("forward", "schedule", "Thời khoá biểu");
    await travel("forward", "guide", "Hướng dẫn sử dụng");
  });

  it("S2-B02-04: invalid page and subpage redirect to valid URL states [route portion]", async () => {
    window.history.replaceState(null, "", "#p=missing-page");
    const first = render(<App />);
    const validPages = ["manual", "schedule", "data", "history", "guide"];
    await waitFor(() => expect(validPages).toContain(new URLSearchParams(window.location.hash.slice(1)).get("p")));
    expect(screen.getByRole("heading", { level: 1 })).not.toBeEmptyDOMElement();
    first.unmount();
    window.history.replaceState(null, "", "#p=data&s=missing-subpage");
    render(<App />);
    await waitFor(() => expect(["hours", "availability"]).toContain(new URLSearchParams(window.location.hash.slice(1)).get("s")));
    expect(["hours", "availability"]).toContain(screen.getByTestId("route-data").textContent);
  });

  it("S2-B02-06: page navigation creates history while typing search does not", async () => {
    render(<App />);
    const startingLength = window.history.length;
    fireEvent.click(screen.getByRole("button", { name: "Thời khoá biểu" }));
    const afterNavigation = window.history.length;
    const push = vi.spyOn(window.history, "pushState");
    for (const value of ["Q", "QA", "QA-CSE19"]) {
      fireEvent.change(screen.getByRole("textbox", { name: "QA schedule search" }), { target: { value } });
    }
    expect(window.history.length).toBe(afterNavigation);
    expect(push).not.toHaveBeenCalled();
    expect(new URLSearchParams(window.location.hash.slice(1)).get("search")).toBe("QA-CSE19");
    expect(afterNavigation).toBe(startingLength + 1);
    await travel("back", "manual", "Dữ liệu học phần");
  });
});
