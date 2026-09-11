// fetch wrapper mong - goi cung-origin qua Vite dev proxy (vite.config.js
// chuyen tiep /api/* sang Flask tren 127.0.0.1:5055), khong can CORS.
async function request(path, { method = "GET", body } = {}) {
  const res = await fetch(path, {
    method,
    headers: body ? { "Content-Type": "application/json" } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });
  const json = await res.json().catch(() => null);
  if (!res.ok) {
    const message = json?.error || `Loi HTTP ${res.status}`;
    const err = new Error(message);
    // Gan status + body tren Error - /api/move-lesson tra ve 409 kem
    // {conflict: {...}} khi o do co van de va chua ghi ly do. Caller (drag-drop
    // handler) can doc duoc conflict de mo hop thoai, khong chi thay thong bao loi.
    err.status = res.status;
    err.body = json;
    throw err;
  }
  return json;
}

/** Tai file len (multipart). KHONG dat Content-Type - de trinh duyet tu sinh
 *  kem boundary; dat tay se lam Flask khong tach duoc phan file. */
export async function apiUpload(path, file, field = "file") {
  const form = new FormData();
  form.append(field, file);
  const res = await fetch(path, { method: "POST", body: form });
  const json = await res.json().catch(() => null);
  if (!res.ok) {
    const err = new Error(json?.error || `Loi HTTP ${res.status}`);
    err.status = res.status;
    err.body = json;
    throw err;
  }
  return json;
}

/** TAI FILE ve may qua POST.
 *
 *  Vi sao khong dung `window.location.href = "/api/..."` nhu truoc: xuat theo bo
 *  loc phai GUI LEN danh sach dang hien (co khi vai tram id, va ca ban do luoi),
 *  khong nhet vao query string duoc. Ma apiPost thi luon parse JSON nen khong
 *  nhan duoc file nhi phan - phai doc blob rieng o day.
 *
 *  Loi tu backend van la JSON (vd "bo loc khong con lop nao") nen phai doc thu
 *  JSON truoc khi coi la file, khong thi nguoi dung tai ve mot file .xlsx hong
 *  chua dung mot cau bao loi. */
export async function apiDownload(path, body, tenFileMacDinh = "tai-ve.xlsx") {
  const res = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body ?? {}),
  });
  if (!res.ok) {
    const json = await res.json().catch(() => null);
    const err = new Error(json?.error || `Loi HTTP ${res.status}`);
    err.status = res.status;
    err.body = json;
    throw err;
  }
  // Ten file do backend dat (Content-Disposition) - giu dung quy uoc
  // FATE.TKB.<hoc ky>.xlsx thay vi tu bia ten o hai noi.
  const cd = res.headers.get("Content-Disposition") || "";
  const khop = /filename\*?=(?:UTF-8'')?"?([^";]+)"?/i.exec(cd);
  const ten = khop ? decodeURIComponent(khop[1]) : tenFileMacDinh;

  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = ten;
  document.body.appendChild(a);
  a.click();
  a.remove();
  // Thu hoi ngay se lam Firefox huy download dang bat dau - hen mot nhip.
  setTimeout(() => URL.revokeObjectURL(url), 10_000);
  return ten;
}

export const apiGet = (path) => request(path);
export const apiPost = (path, body) => request(path, { method: "POST", body });
export const apiPatch = (path, body) => request(path, { method: "PATCH", body });
export const apiDelete = (path) => request(path, { method: "DELETE" });
