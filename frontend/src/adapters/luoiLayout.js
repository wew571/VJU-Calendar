// CHIA CỘT cho các buổi trùng giờ trong cùng một ngày (greedy interval-
// scheduling, kiểu Google Calendar).
//
// Tách ra khỏi LessonGridBoard vì giờ có HAI nơi cần đúng cách chia đó: lưới
// trên màn hình, và file Excel xuất ra từ lưới. Yêu cầu là file xuất phải có
// "định dạng y hệt" màn hình — mà bố cục chính là thuật toán này, nên nó chỉ
// được có MỘT bản. Chép làm hai là lần sửa sau hai bên lệch nhau, và không ai
// nhìn ra vì cả hai đều "trông có vẻ đúng".

// {sectionId: {colIndex, totalCols}}
//
// totalCols tính theo CẢ CỤM giao nhau bắc cầu (A trùng B, B trùng C → A/B/C
// cùng một số cột), không chỉ theo hàng xóm trực tiếp — nếu không sẽ bị lệch/đè
// lên nhau (đã phát hiện và sửa trước đó).
export function chiaCotTheoNgay(lessons) {
  const byDay = {};
  for (const l of lessons ?? []) {
    if (l.day == null || l.period == null) continue;
    (byDay[l.day] ||= []).push(l);
  }

  const result = {};
  for (const dayLessons of Object.values(byDay)) {
    const withInterval = dayLessons.map((l) => ({
      l,
      start: l.period,
      end: l.period + (l.duration || 1),
    }));
    withInterval.sort((a, b) => a.start - b.start);

    const cols = [];
    withInterval.forEach((item) => {
      let placed = false;
      for (let c = 0; c < cols.length; c++) {
        if (cols[c] <= item.start) {
          item.colIndex = c;
          cols[c] = item.end;
          placed = true;
          break;
        }
      }
      if (!placed) {
        item.colIndex = cols.length;
        cols.push(item.end);
      }
    });

    let cluster = [];
    let clusterEnd = -Infinity;
    const clusters = [];
    withInterval.forEach((item) => {
      if (item.start >= clusterEnd) {
        if (cluster.length) clusters.push(cluster);
        cluster = [];
        clusterEnd = -Infinity;
      }
      cluster.push(item);
      clusterEnd = Math.max(clusterEnd, item.end);
    });
    if (cluster.length) clusters.push(cluster);

    clusters.forEach((members) => {
      const totalCols = Math.max(...members.map((m) => m.colIndex)) + 1;
      members.forEach((m) => {
        m.totalCols = totalCols;
      });
    });

    withInterval.forEach((item) => {
      result[item.l.id] = { colIndex: item.colIndex, totalCols: item.totalCols };
    });
  }
  return result;
}

// Số cột thật sự phải dành cho mỗi ngày = cụm đông nhất của ngày đó. Ngày trống
// vẫn chiếm 1 cột, để bảng Excel còn đủ 7 cột thứ như trên màn hình.
export function soCotMoiNgay(lessons, layoutMap, numDays) {
  const widths = [];
  for (let d = 0; d < numDays; d++) {
    let max = 1;
    for (const l of lessons ?? []) {
      if (l.day !== d) continue;
      max = Math.max(max, layoutMap[l.id]?.totalCols || 1);
    }
    widths.push(max);
  }
  return widths;
}
