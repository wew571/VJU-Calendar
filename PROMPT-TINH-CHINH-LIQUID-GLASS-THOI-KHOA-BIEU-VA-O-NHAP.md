# Prompt tinh chỉnh Liquid Glass cho thời khóa biểu, ô tích và ô nhập

> Đây là prompt giao việc cho AI Agent, không phải yêu cầu làm lại toàn bộ giao diện. Mẫu để đối chiếu là menu xổ xuống hiện có trong hệ thống: bề mặt kính nhìn xuyên nhẹ, thấy được lớp phía sau. Nếu gặp điểm không thể xác định từ giao diện và mã nguồn, hãy hỏi người dùng thay vì tự đoán.

## Prompt

```text
Bạn là AI Agent làm việc trên dự án VJU-Calendar. Hãy tinh chỉnh những phần giao diện còn trắng hoặc chưa có hiệu ứng Liquid Glass cho đồng bộ với chất liệu kính đang dùng trong hệ thống. Đọc mã và xem giao diện thật trước khi sửa; sau đó triển khai, kiểm tra và báo lại bằng tiếng Việt dễ hiểu.

# 1. Bối cảnh

Frontend dùng React, Vite, Tailwind CSS v4 và các component kiểu shadcn/Radix. Hệ thống đã có Liquid Glass ở nhiều nơi, đặc biệt là menu xổ xuống của bộ lọc: khi mở menu, nền có độ trong và có thể nhìn xuyên nhẹ qua lớp phía sau. Đó là mẫu cần bám theo về chất liệu, không phải popup chi tiết buổi học màu tối.

Hãy tự kiểm tra các điểm này trước khi thay đổi:
- `frontend/src/app.css`: màu đỏ VJU, các bề mặt kính, CSS cho menu xổ xuống (`[data-slot='dropdown-menu-content']`) và thứ tự `@layer`. File này nhập `styles.css` trong layer `legacy`.
- `frontend/src/components/shared/filter-select.jsx`, `frontend/src/components/ui/dropdown-menu.jsx`: menu xổ xuống đang dùng làm mẫu.
- `frontend/src/presentation/pages/SchedulePage.jsx` và `frontend/src/presentation/schedule/`: các khối quanh màn thời khóa biểu. Kiểm tra cả chế độ thường và toàn màn hình, người dùng staff và viewer.
- `frontend/src/components/ui/checkbox.jsx`, `frontend/src/components/ui/input.jsx`, `frontend/src/components/shared/list-search.jsx`: ô tích và ô nhập dùng chung.
- Các chỗ có ô nhập viết trực tiếp, như ô tìm trong `filter-select.jsx` và textarea trong `frontend/src/presentation/schedule/MoveReasonDialog.jsx`. Tìm thêm các chỗ thực sự đang được render, không coi danh sách này là đầy đủ.

Một số khối lịch đã dùng `glass-panel`; một số ô nhập cũng đã có nền hơi trong. Đừng kết luận tất cả đều chưa có kính chỉ vì nhìn thấy màu trắng trong mã. Hãy kiểm tra phần nào trên giao diện vẫn trắng đặc, chưa nhìn xuyên hoặc chưa đồng bộ, rồi sửa đúng phần đó.

# 2. Mục tiêu

Chỉ tinh chỉnh ba nhóm sau, trong giao diện sáng hiện tại:

1. Các khối giao diện màu trắng quanh thời khóa biểu: thanh lọc, khối chọn phạm vi xếp, các bước tiến trình, hộp vấn đề, thẻ thông tin liên quan và nền của nút chọn chế độ Lưới/Bảng. Đổi bề mặt còn trắng đặc sang cùng ngôn ngữ Liquid Glass với menu xổ xuống: có độ trong vừa phải, viền và chiều sâu nhẹ, nhìn xuyên được nền phía sau nhưng chữ vẫn rõ. Chỉ chỉnh những nơi cần thiết; không phủ thêm hiệu ứng lên từng ô của lưới lịch và không đổi thiết kế/màu phân loại của thanh buổi học.
2. Tất cả checkbox thực sự trong hệ thống: khi được tích, không để cả ô là một mảng đỏ đặc hoặc chỉ là kính không nhận ra trạng thái. Giữ cảm giác kính ở phần nền, thêm viền đỏ nhẹ dựa trên màu đỏ VJU có sẵn, và giữ dấu tích đủ rõ. Khi chưa tích, ô vẫn trung tính; trạng thái indeterminate (nếu có), disabled và focus cũng phải dễ phân biệt. Không áp quy tắc này bừa lên icon dấu tick của menu, nút chọn chế độ hay những ô chọn giờ có màu trạng thái nghiệp vụ riêng.
3. Những ô cho phép người dùng gõ nội dung trên toàn hệ thống: ô chữ, tìm kiếm, số, ngày/giờ và textarea, kể cả ô viết trực tiếp thay vì dùng component `Input`. Cho chúng chất liệu kính có thể nhìn xuyên nhẹ tương tự menu xổ xuống. Khi người dùng bấm vào để nhập hoặc điều hướng tới bằng bàn phím, khung ô có viền đỏ VJU nhẹ và dấu hiệu focus rõ. Đảm bảo chữ, placeholder, icon, thông báo lỗi và giá trị đã nhập vẫn đọc được.

Dropdown/select vốn đã có hiệu ứng kính là mẫu tham chiếu và chỉ cần kiểm tra để giữ đồng bộ, không phải hạng mục thiết kế lại. Input chọn file và từng ô chỉnh sửa của bảng dữ liệu dày đặc cũng không nằm trong phạm vi phủ kính mới. Đừng sửa chúng chỉ vì có thẻ `<input>`.

# 3. Cách làm

1. Mở giao diện và đối chiếu thực tế các khối lịch, checkbox và ô nhập ở những trang đang dùng. Xem chúng có bị nền của component cha, class tiện ích hay CSS legacy che mất độ trong không. Kiểm tra cả khi menu, dialog/drawer hoặc chế độ toàn màn hình đang mở.
2. Tìm nguyên nhân của từng vùng còn trắng đặc, rồi tận dụng token/class/component dùng chung trước khi thêm kiểu riêng cho từng trang. Với ô tìm có icon hoặc nút xóa, áp dụng hiệu ứng lên đúng khung bao, không chỉ lên thẻ `<input>` trong suốt nằm bên trong. Với textarea và các ô nhập trực tiếp, đảm bảo chúng nhận cùng cách xử lý mà không ảnh hưởng ô không thuộc phạm vi.
3. Dùng màu đỏ VJU đã có trong hệ thống để tạo viền nhẹ cho checkbox được tích và ô nhập đang focus. Không đổi giá trị token nhận diện VJU gốc; nếu cần một sắc độ nhẹ hơn, tạo kiểu dùng chung từ token hiện có. Giữ dấu tích và trạng thái focus đủ tương phản trên nền kính thật.
4. Sau khi sửa, xem lại ở nhiều màn/trạng thái. Nếu một nơi đã có kính và trông đúng mẫu, giữ nguyên. Không thêm thư viện chỉ để làm hiệu ứng có thể thực hiện gọn bằng CSS hiện tại; nếu thật sự cần thư viện, nêu rõ lý do và kiểm tra tương thích trước.

Đây là việc tinh chỉnh theo mẫu đã có, không cần đề xuất hai hướng thiết kế rồi dừng chờ duyệt như prompt thiết kế ban đầu. Chỉ hỏi người dùng và dừng ở điểm liên quan nếu gặp xung đột thực tế về nghiệp vụ, khả năng đọc hoặc có chi tiết quan trọng không thể xác định từ hệ thống.

# 4. Những điều phải giữ nguyên

- Giữ nghiệp vụ, dữ liệu, API/backend, phân quyền staff/viewer, điều hướng, nội dung và các thao tác hiện có. Không bật dark mode trong đợt này.
- Không đổi màu mang ý nghĩa cảnh báo/lỗi, các thanh buổi học (`LessonCard`, `.lesson-bar`), từng ô lưới/heatmap, bảng nhập liệu dày đặc hay vị trí các mục để đổi lấy hiệu ứng kính. Giữ sticky, scroll, kéo-thả và toàn màn hình hoạt động như trước.
- Tôn trọng thứ tự layer trong `app.css`; không import `styles.css` lần nữa ra ngoài layer `legacy` và không viết selector toàn cục khiến checkbox, file input hoặc ô bảng bị đổi ngoài ý muốn.
- Không để lớp kính làm mờ chữ hoặc mất tín hiệu trạng thái. Có nền dự phòng dễ đọc khi `backdrop-filter` không khả dụng, giữ focus khi dùng bàn phím, disabled/error rõ ràng và tôn trọng `prefers-reduced-motion`. Tránh blur nặng trên vùng có nhiều phần tử.
- Dialog, drawer, menu xổ xuống và chế độ toàn màn hình phải giữ đúng thứ tự hiển thị và nhận được thao tác.

# 5. Tiêu chí nghiệm thu

- Những khối giao diện đã nêu quanh thời khóa biểu không còn là mảng trắng đặc không cần thiết; chất liệu kính nhìn xuyên nhẹ giống menu xổ xuống hiện có, nhưng văn bản và trạng thái vẫn dễ đọc. Lưới và thẻ buổi học giữ màu, kích thước và cách tương tác cũ.
- Checkbox ở mọi chỗ đang dùng có viền đỏ nhẹ khi tích, bề mặt kính không bị tô đỏ đặc, dấu tick vẫn rõ; chưa tích, focus, disabled và indeterminate (nếu có) phân biệt được. Không biến icon menu hay ô chọn giờ thành checkbox kiểu mới.
- Các ô nhập nội dung trên các trang, trong dialog/drawer và ô tìm có khung bao đều có hiệu ứng kính; bấm vào hoặc dùng Tab tới ô sẽ thấy viền đỏ nhẹ, chữ và placeholder vẫn dễ đọc. Ô nhập file, select/dropdown và ô bảng dày không bị thay đổi ngoài phạm vi.
- Giao diện vẫn sử dụng bình thường ở màn nhỏ, desktop và chế độ lịch toàn màn hình trên Microsoft Edge; không bị tràn, che nhau, mất focus hay giảm hiệu năng đáng kể. Khi trình duyệt không hỗ trợ blur vẫn đọc và nhập liệu được.
- Chạy các bài kiểm tra frontend có liên quan, `npm test` và `npm run build` trong `frontend/` khi có cấu hình cần thiết (đặc biệt `config/frontend.json`). Nếu thiếu cấu hình hoặc không kiểm tra được một trạng thái, nêu rõ giới hạn; không tự tạo dữ liệu/cấu hình thật bằng phỏng đoán.

# 6. Cách báo lại

Hãy ghi ngắn gọn: đã kiểm tra những bề mặt nào; chỗ nào trước đó còn trắng hoặc chưa đồng bộ; đã sửa gì và ở file nào; phần nào cố ý giữ nguyên; kết quả kiểm tra tự động và xem giao diện trên Edge; điểm nào chưa kiểm được hoặc cần người dùng xác nhận. Đừng nói đã xác minh bằng mắt nếu thực tế chưa mở được giao diện.
```
