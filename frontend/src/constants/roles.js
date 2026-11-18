export const ROLE_DEFINITIONS = {
  gdct: {
    label: "Giám đốc CT",
    initials: "GĐ",
    description: "Quản lý giảng viên thỉnh giảng và xếp lịch trong CTĐT được chọn.",
    pages: ["schedule", "data", "history", "guide"],
    dataSubKeys: ["availability"],
    canManageGuests: true,
    canEditResidentAvailability: false,
    canSchedule: true,
    scheduleScope: "program",
  },
  dpct: {
    label: "Điều phối CT",
    initials: "ĐP",
    description: "Quản lý hồ sơ và giờ có thể dạy của giảng viên thỉnh giảng.",
    pages: ["data", "guide"],
    dataSubKeys: ["availability"],
    canManageGuests: true,
    canEditResidentAvailability: false,
    canSchedule: false,
    scheduleScope: null,
  },
  assistant: {
    label: "Trợ lý khoa",
    initials: "TK",
    description: "Quản lý giảng viên thỉnh giảng, cập nhật giờ rảnh cơ hữu và xếp lịch toàn trường.",
    pages: ["schedule", "data", "history", "guide"],
    dataSubKeys: ["availability"],
    canManageGuests: true,
    canEditResidentAvailability: true,
    canSchedule: true,
    scheduleScope: "school",
  },
  resident: {
    label: "Giảng viên cơ hữu",
    initials: "GV",
    description: "Khai báo giờ rảnh cho hồ sơ giảng viên được chọn trong bản demo.",
    pages: ["data", "guide"],
    dataSubKeys: ["availability"],
    canManageGuests: false,
    canEditResidentAvailability: false,
    canDeclareOwnAvailability: true,
    canSchedule: false,
    scheduleScope: null,
  },
  viewer: {
    label: "Xem thôi",
    initials: "XT",
    description: "Chỉ tra cứu lịch và nhật ký.",
    pages: ["schedule", "history", "guide"],
    dataSubKeys: [],
    canManageGuests: false,
    canEditResidentAvailability: false,
    canDeclareOwnAvailability: false,
    canSchedule: false,
    scheduleScope: null,
  },
};

export function isRole(role) {
  return Object.prototype.hasOwnProperty.call(ROLE_DEFINITIONS, role);
}

export function getRoleDefinition(role) {
  if (role === "staff") return ROLE_DEFINITIONS.assistant;
  return ROLE_DEFINITIONS[role] ?? ROLE_DEFINITIONS.viewer;
}

export function allowedDataSubKeys(role) {
  return getRoleDefinition(role).dataSubKeys;
}

export function clampPageForRole(page, role) {
  const allowedPages = getRoleDefinition(role).pages;
  return allowedPages.includes(page) ? page : allowedPages[0];
}

export function clampSubForRole(page, sub, role) {
  if (page !== "data") return sub;
  const allowed = allowedDataSubKeys(role);
  return allowed.includes(sub) ? sub : allowed[0] ?? null;
}
