import fs from 'node:fs/promises';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
import { spawn } from 'node:child_process';
import readline from 'node:readline';
const sourceDir = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(sourceDir, '../..');
const require = createRequire(path.join(repo, 'frontend/package.json'));
let chromium;
try { ({ chromium } = require('playwright')); }
catch {
  const bundled = createRequire('C:/Program Files/WindowsApps/OpenAI.CodexPrimaryRuntime.v26-1030-493-0_26.1030.493.0_x64__3k8sg7r9htsxt/dependencies/node/node_modules/runtime-loader.cjs');
  ({ chromium } = bundled('playwright'));
}
const work = path.resolve(process.env.VJU_SPRINT0_WORKDIR || path.join(repo, 'work/sprint0-tests'));
const relativeWork = path.relative(path.join(repo, 'work'), work);
if (relativeWork.startsWith('..') || path.isAbsolute(relativeWork)) throw new Error('Test outputs must stay inside work/.');
const evidence = path.join(work, 'evidence');
const bridge = spawn(process.env.VJU_TEST_PYTHON || 'C:/Users/Minh/AppData/Local/Programs/Python/Python314/python.exe', ['-X', 'utf8', path.join(sourceDir, 'flask_bridge.py')], { windowsHide: true, stdio: ['pipe', 'pipe', 'pipe'] });
const pending = new Map(); let sequence = 0;
const apiCalls = [];
readline.createInterface({ input: bridge.stdout }).on('line', line => {
  const response = JSON.parse(line); apiCalls.push(response); pending.get(response.id)?.(response); pending.delete(response.id);
});
const api = (method, url, body, contentType = 'application/json') => new Promise(resolve => {
  const id = ++sequence; pending.set(id, resolve);
  bridge.stdin.write(JSON.stringify({ id, method, path: url, body, contentType }) + '\n');
});
const browser = await chromium.launch({ executablePath: process.env.VJU_TEST_CHROME || 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true, args: ['--no-sandbox'] });
const context = await browser.newContext({ viewport: { width: 1440, height: 1000 }, locale: 'vi-VN' });
const page = await context.newPage();
page.setDefaultTimeout(9000);
// Render the real production bundle and call the real isolated Flask API through
// test_client IPC. The browser's loopback network is unavailable in this sandbox.
await context.route('**/*', async route => {
  const request = route.request(); const url = new URL(request.url());
  if (url.pathname.startsWith('/api/')) {
    const response = await api(request.method(), url.pathname + url.search, request.postData(), request.headers()['content-type']);
    await route.fulfill({ status: response.status, contentType: response.contentType, body: response.body });
  } else {
    const relative = url.pathname === '/' ? 'index.html' : url.pathname.slice(1);
    try {
      const body = await fs.readFile(path.join(work, 'isolated-app/frontend/dist', relative));
      const extension = path.extname(relative);
      await route.fulfill({ status: 200, contentType: ({ '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.svg': 'image/svg+xml' })[extension] || 'application/octet-stream', body });
    } catch { await route.fulfill({ status: 404, body: '' }); }
  }
});
const errors = [];
page.on('pageerror', error => errors.push(error.message));
await page.goto('http://127.0.0.1:5074', { waitUntil: 'networkidle' });
await page.screenshot({ path: path.join(evidence, 'role-picker.png'), fullPage: true });
console.log((await page.locator('body').innerText()).slice(0, 2600));
await page.getByRole('button', { name: 'Giáo vụ / Điều phối viên', exact: true }).click();
await page.waitForLoadState('networkidle');
await page.screenshot({ path: path.join(evidence, 'schedule-incomplete.png'), fullPage: true });
await fs.writeFile(path.join(evidence, 'initial-dom.txt'), await page.locator('body').innerText(), 'utf8');
const observations = [];
const shot = async name => { await page.screenshot({ path: path.join(evidence, name), fullPage: true }); return name; };
const getData = async () => JSON.parse((await api('GET', '/api/data')).body);
const check = async (id, task) => {
  try { observations.push({ id, status: 'PASS', ...(await task()) }); }
  catch (error) { observations.push({ id, status: 'FAIL', error: error.message, screenshot: await shot(id + '-failure.png') }); }
  console.log(id, observations.at(-1).status);
  await fs.writeFile(path.join(evidence, 'browser-results.json'), JSON.stringify(observations, null, 2));
};
const workflow = () => page.getByRole('dialog', { name: 'Quy trình xếp lịch', exact: true });
const states = async () => workflow().locator('.glass-panel[data-state]').evaluateAll(nodes => nodes.map(n => ({ state: n.dataset.state, text: n.textContent })));
const openWorkflow = async () => { await page.getByRole('button', { name: /Mở quy trình xếp lịch/ }).click(); await workflow().waitFor(); };
const closeWorkflow = async () => { if (await workflow().count()) await workflow().getByRole('button', { name: 'Đóng', exact: true }).click(); };
await check('TC-06', async () => {
  await openWorkflow();
  const steps = await states();
  if (steps.length !== 3 || steps.some(step => step.state === 'done')) throw new Error('Bước chưa đủ điều kiện bị đánh dấu hoàn tất: ' + JSON.stringify(steps));
  return { steps, screenshot: await shot('workflow-incomplete.png') };
});
await check('TC-08', async () => {
  const steps = await states();
  const disabled = await workflow().locator('.glass-panel[data-state]').nth(1).getByRole('button').isDisabled();
  const response = await api('POST', '/api/solve-guest', '{}');
  if (!disabled || response.status !== 400 || steps[1].state === 'done') throw new Error('Thiếu giờ không bị chặn');
  return { steps, disabled, rejectedRequest: JSON.parse(response.body), screenshot: 'workflow-incomplete.png' };
});
await closeWorkflow();
await page.getByTitle('Dữ liệu học phần', { exact: true }).click();
await page.getByRole('heading', { name: 'Dữ liệu học phần', exact: true }).waitFor();
await shot('manual-data.png');
await check('TC-11', async () => {
  await page.getByRole('button', { name: 'Học phần', exact: true }).click();
  const form = page.getByRole('dialog', { name: 'Thêm học phần mới', exact: true });
  await form.getByRole('textbox', { name: 'Mã học phần', exact: true }).fill('TEST101-UI');
  await form.getByRole('textbox', { name: /Tên học phần/ }).fill('Kiểm thử phần mềm UI');
  await form.getByRole('combobox', { name: 'Số tín chỉ', exact: true }).selectOption('3');
  const screenshot = await shot('course-valid-input.png');
  await form.getByRole('button', { name: 'Lưu', exact: true }).click();
  await form.waitFor({ state: 'hidden' });
  const saved = (await getData()).courses.find(c => c.code === 'TEST101-UI');
  if (!saved || saved.name !== 'Kiểm thử phần mềm UI' || saved.credits !== 3) throw new Error('Dữ liệu UI không được lưu đúng');
  return { screenshot, saved };
});
await page.keyboard.press('Escape');
await page.getByTitle('Chuẩn bị dữ liệu', { exact: true }).click();
await page.getByRole('button', { name: 'Giảng viên', exact: true }).click();
await page.getByRole('heading', { name: 'Giảng viên', exact: true }).waitFor();
await shot('teachers-staff.png');
for (const [id, availability] of [[0, [0, 1, 2]], [1, [13, 14, 15]], [2, [26, 27, 28]]]) {
  const response = await api('PATCH', `/api/manual/teacher/${id}`, JSON.stringify({ availability }));
  if (response.status !== 200) throw new Error('Không chuẩn bị được giờ rảnh cũ: ' + response.body);
}
await page.reload({ waitUntil: 'networkidle' });
await shot('teachers-old-availability.png');
const roles = { picker: 'Chỉ có staff (Giáo vụ) và viewer (Xem thôi), không có lựa chọn Tester.', staffBulkVisible: await page.getByRole('button', { name: 'Khai toàn bộ giờ rảnh', exact: true }).isVisible() };
await check('TC-16', async () => {
  const before = await getData();
  await page.getByRole('button', { name: 'Khai toàn bộ giờ rảnh', exact: true }).click();
  const dialog = page.getByRole('dialog', { name: 'Khai toàn bộ giờ rảnh?', exact: true });
  const screenshot = await shot('bulk-confirm-cancel.png');
  await dialog.getByRole('button', { name: 'Hủy', exact: true }).click();
  const after = await getData();
  if (JSON.stringify(before) !== JSON.stringify(after)) throw new Error('Hủy đã thay đổi dữ liệu');
  return { screenshot, dataUnchanged: true, teacherCount: before.teachers.length, oldSlots: before.teachers.map(t => ({ id: t.id, slots: t.availabilitySlots })) };
});
await check('TC-17', async () => {
  await page.getByRole('button', { name: 'Khai toàn bộ giờ rảnh', exact: true }).click();
  const dialog = page.getByRole('dialog', { name: 'Khai toàn bộ giờ rảnh?', exact: true });
  await dialog.getByRole('button', { name: 'Xác nhận', exact: true }).click();
  await dialog.waitFor({ state: 'hidden' });
  const data = await getData();
  const slots = data.teachers.map(t => ({ id: t.id, type: t.type, slots: t.availabilitySlots }));
  if (slots.length !== 3 || slots.some(t => !t.slots?.length)) throw new Error('Khai giờ thiếu giảng viên');
  return { screenshot: await shot('bulk-confirmed.png'), slots, limit: 'Đã chạy bằng staff; chưa có vai trò Tester hoặc phê duyệt khuôn mẫu PO.' };
});
await page.getByRole('button', { name: 'Thời khoá biểu', exact: true }).click();
await check('TC-07', async () => {
  await openWorkflow();
  const ready = await states();
  await workflow().locator('.glass-panel[data-state]').nth(1).getByRole('button').click();
  await workflow().locator('.glass-panel[data-state="done"]').filter({ hasText: 'Xếp thỉnh giảng' }).waitFor();
  const guest = await states();
  await workflow().locator('.glass-panel[data-state]').nth(2).getByRole('button').click();
  await workflow().locator('.glass-panel[data-state="done"]').filter({ hasText: 'Ghép cơ hữu' }).waitFor();
  const complete = await states();
  if (complete.some(step => step.state !== 'done')) throw new Error('Không đủ 3 bước hoàn tất');
  return { ready, guest, complete, screenshot: await shot('workflow-complete.png') };
});
await closeWorkflow();
await shot('schedule-grid.png');
await check('TC-04', async () => {
  await page.locator('.lesson-bar[aria-label*="TEST101-1"]').first().hover();
  await page.locator('.lesson-popover').waitFor();
  const text = await page.locator('.lesson-popover').innerText();
  if (!text.includes('TEST101-1') || !text.includes('Kiểm thử phần mềm') || !text.includes('Nguyễn Văn A')) throw new Error('Popup không khớp lớp/GV: ' + text);
  const style = await page.locator('.lesson-popover').evaluate(el => ({ backdropFilter: getComputedStyle(el).backdropFilter, background: getComputedStyle(el).backgroundColor }));
  return { text, style, screenshot: await shot('lesson-popup.png') };
});
await page.mouse.move(1400, 900);
await check('TC-02', async () => {
  const button = page.getByRole('button', { name: 'Bộ lọc thêm', exact: true });
  const style = () => button.evaluate(el => ({ borderColor: getComputedStyle(el).borderColor, background: getComputedStyle(el).backgroundColor, backdropFilter: getComputedStyle(el).backdropFilter }));
  const normal = await style(); await button.hover(); const hover = await style();
  await page.mouse.down(); const pressed = await style(); await page.mouse.up();
  const screenshot = await shot('button-border-states.png');
  await fs.writeFile(path.join(evidence, 'button-style-observation.json'), JSON.stringify({ normal, hover, pressed, screenshot }, null, 2));
  if (![normal, hover, pressed].every(s => /^rgb\(2[0-5]\d,\s*[0-9]{1,2},\s*[0-9]{1,2}\)/.test(s.borderColor))) throw new Error('Nút Bộ lọc thêm không có viền đỏ ở đủ ba trạng thái: ' + JSON.stringify({ normal, hover, pressed }));
  return { normal, hover, pressed, screenshot };
});
await page.keyboard.press('Escape');
await page.getByRole('button', { name: 'Bảng', exact: true }).click();
await shot('schedule-table.png');
await page.getByRole('button', { name: 'Lưới', exact: true }).click();
await check('TC-05', async () => {
  const before = await getData();
  const section = before.classes.find(c => c.classCode === 'TEST101-1');
  const fixed = { teacherIds: [0], courseId: 0, duration: 3, program: 'CSE', cohort: 'K2025', day: 0, periodStart: 2, periodEnd: 4 };
  for (const [endpoint, method, extra] of [['/api/manual/section/0', 'PATCH', { classCode: 'TEST101-1' }], ['/api/manual/section', 'POST', { classCode: 'TEST101-CONFLICT' }]]) {
    const response = await api(method, endpoint, JSON.stringify({ ...fixed, ...extra }));
    if (response.status !== 200) throw new Error('Không tạo được lỗi mẫu: ' + response.body);
  }
  await page.reload({ waitUntil: 'networkidle' });
  const bar = page.locator('.lesson-bar').filter({ hasText: 'TEST101-1' });
  const target = await bar.count() ? bar.first() : page.locator('.lesson-bar').first();
  await target.hover(); await page.locator('.lesson-popover').waitFor();
  const text = await page.locator('.lesson-popover').innerText();
  if (!/trùng giảng viên/i.test(text)) throw new Error('Popup thiếu cảnh báo: ' + text);
  return { screenshot: await shot('lesson-popup-conflict.png'), text, conflict: 'Hai lớp cùng GV Nguyễn Văn A, CSE/K2025, Thứ Hai tiết 2–4.' };
});
await page.mouse.move(1400, 900);
await check('TC-03', async () => {
  const header = await page.locator('.glass-page-header').evaluate(el => ({ text: el.innerText, backdropFilter: getComputedStyle(el).backdropFilter, background: getComputedStyle(el).backgroundColor }));
  await openWorkflow();
  const modal = await workflow().evaluate(el => ({ backdropFilter: getComputedStyle(el).backdropFilter, background: getComputedStyle(el).backgroundColor }));
  if (!header.backdropFilter.includes('blur') || !modal.backdropFilter.includes('blur')) throw new Error('Thiếu hiệu ứng kính: ' + JSON.stringify({ header, modal }));
  return { header, modal, screenshot: await shot('glass-titles.png') };
});
await closeWorkflow();
observations.push({ id: 'TC-01', status: errors.length ? 'FAIL' : 'PASS', scope: 'Bốn màn được yêu cầu, Chrome headless; API thật qua Flask test_client IPC.', screenshots: ['manual-data.png', 'teachers-staff.png', 'schedule-grid.png', 'schedule-table.png'], pageErrors: errors });
roles.availableRoleButtons = ['Giáo vụ / Điều phối viên', 'Xem thôi'];
await fs.writeFile(path.join(evidence, 'role-observation.json'), JSON.stringify(roles, null, 2));
await fs.writeFile(path.join(evidence, 'browser-results.json'), JSON.stringify(observations, null, 2));
await fs.writeFile(path.join(evidence, 'api-bridge-responses.json'), JSON.stringify(apiCalls, null, 2));
await fs.writeFile(path.join(evidence, 'browser-errors.json'), JSON.stringify(errors, null, 2));
await context.unrouteAll({ behavior: 'ignoreErrors' });
await context.close();
await browser.close();
bridge.stdin.end();
bridge.kill();
process.exit(observations.some(item => item.status === 'FAIL') ? 1 : 0);
