# Prompt thêm chức năng khai báo giờ rảnh của giảng viên

> Đây là khung prompt dành cho AI Agent. Các nội dung nằm trong dấu `[ ... ]` cần được bổ sung hoặc điều chỉnh khi yêu cầu nghiệp vụ được làm rõ.

## Prompt

```text
Bạn là một AI Agent chuyên phát triển phần mềm. Hãy phân tích codebase hiện tại và triển khai chức năng mới trong phần sửa thông tin giảng viên.

# 1. Bối cảnh

Hệ thống hiện có màn hình sửa thông tin giảng viên, trong đó có phần khai báo giờ rảnh của giảng viên.

Khu vực cần chỉnh sửa:
- Màn hình/chức năng: Sửa thông tin giảng viên
- Phần: Khai báo giờ rảnh
- Công nghệ hiện tại: Hãy tự kiểm tra trong codebase
- Các file liên quan: Hãy tìm kiếm và xác định trước khi sửa

# 2. Chức năng cần bổ sung

Tên chức năng:
Tự động khai báo giờ rảnh

Mô tả:
Bổ sung chức năng tự động sinh và lưu lại toàn bộ giờ rảnh của giảng viên trong tuần theo ba khung thời gian được cấu hình sẵn: buổi sáng, buổi chiều và buổi tối. Mỗi lần chạy, hệ thống yêu cầu người dùng xác nhận, xóa toàn bộ giờ rảnh hiện có nhưng giữ nguyên giờ đang dạy, sau đó sinh danh sách giờ rảnh mới. Thuật toán xử lý độc lập từng ngày và dựa trên số khung có giờ dạy để áp dụng xác suất tương ứng. Đối với ngày không có giờ dạy, khung sáng, chiều và tối được chọn theo trọng số lần lượt là 45%, 45% và 10%.

Mục tiêu:
Tự động hóa quá trình khai báo khả năng giảng dạy (teacher availability), giảm thao tác chọn thủ công trên lưới thời gian và bảo đảm dữ liệu giờ rảnh được sinh nhất quán với lịch dạy hiện tại cũng như giới hạn ngày làm việc của từng loại giảng viên.

# 3. Luồng sử dụng mong muốn

1. Người dùng truy cập màn hình quản lý giảng viên.
2. Người dùng chọn một giảng viên để mở màn hình sửa thông tin.
3. Trong phần "Giờ có thể dạy", người dùng nhấn nút "Tự động khai giờ rảnh".
4. Hệ thống luôn hiển thị hộp thoại xác nhận, thông báo rõ rằng thao tác sẽ xóa toàn bộ giờ rảnh hiện tại và sinh lại dữ liệu mới.
5. Nếu người dùng hủy, đóng hộp thoại và không thay đổi dữ liệu. Nếu người dùng xác nhận, tiếp tục xử lý.
6. Hệ thống giữ nguyên giờ đang dạy, loại bỏ toàn bộ giờ rảnh hiện tại khỏi dữ liệu dùng để sinh lại, sau đó xác định loại giảng viên và phạm vi ngày hợp lệ.
7. Hệ thống duyệt độc lập từng ngày trong toàn bộ tuần, đếm số khung có giờ dạy và áp dụng xác suất tương ứng.
8. Các slot mới chỉ được tạo tại những tiết không trùng với giờ đang dạy.
9. Hệ thống thay thế toàn bộ danh sách giờ rảnh cũ bằng kết quả mới và lưu ngay thông qua API cập nhật giờ rảnh hiện có.
10. Sau khi lưu thành công, cập nhật lưới và hiển thị thông báo thành công ngắn gọn. Khi mở lại thông tin giảng viên, các tiết rảnh mới phải được hiển thị chính xác.

# 4. Yêu cầu giao diện

- Bổ sung nút "Tự động khai giờ rảnh" trong nhóm thao tác của lưới "Giờ có thể dạy".
- Nút mới phải nằm ngay cạnh các thao tác "Xóa giờ rảnh" và "Bỏ chọn hết" hiện có.
- Khi nhấn nút, luôn hiển thị hộp thoại xác nhận trước khi thực hiện thao tác phá hủy dữ liệu giờ rảnh hiện có.
- Nội dung xác nhận phải nêu rõ: toàn bộ giờ rảnh hiện tại sẽ bị xóa và thay thế bằng kết quả tự động mới; giờ đang dạy không bị thay đổi.
- Hộp thoại phải có hai hành động rõ ràng: "Hủy" và "Xác nhận sinh lại" hoặc nhãn tương đương.
- Sau khi người dùng xác nhận, hệ thống sinh dữ liệu và gọi thao tác cập nhật để lưu ngay; không yêu cầu thêm một bước lưu riêng.
- Sau khi lưu thành công, cập nhật trạng thái các ô trên lưới và hiển thị toast/notice thành công ngắn gọn.
- Không được đánh dấu các ô tương ứng với tiết giảng viên đang dạy.
- Trong thời gian xử lý, nút và hành động xác nhận phải có trạng thái loading/disabled để ngăn gửi nhiều yêu cầu đồng thời.
- Nếu cập nhật thất bại, sử dụng cơ chế hiển thị lỗi hiện có, không hiển thị dữ liệu chưa được lưu như thể thao tác đã thành công và không làm mất dữ liệu giờ rảnh cũ trên giao diện.
- Nút phải sử dụng component, kích thước, khoảng cách và phong cách trực quan thống nhất với các nút hiện có.
- Bố cục nhóm nút không được vỡ hoặc tràn khỏi vùng hiển thị trên màn hình nhỏ.

Giao diện mới phải đồng nhất với phong cách, component và quy ước thiết kế đang được sử dụng trong dự án.

# 5. Quy tắc nghiệp vụ

## 5.1. Các khung thời gian

Các khung phải được đọc từ `CONFIG["availabilityGenerator"]["sessionBlocks"]`, không hard-code trong thuật toán. Cấu hình mặc định:

- Khung `morning` — Buổi sáng: tiết 2 đến tiết 5, thuộc nhóm `daytime`.
- Khung `afternoon` — Buổi chiều: tiết 6 đến tiết 9, thuộc nhóm `daytime`.
- Khung `evening` — Buổi tối: tiết 10 đến tiết 12, thuộc nhóm `evening`.

Mặc dù `calendar.slotsPerDay` hiện hỗ trợ 13 tiết, chức năng tự động chỉ sử dụng khung tối đến tiết 12 theo cấu hình trên. Mọi khung phải nằm trong giới hạn `calendar.slotsPerDay`.

## 5.2. Thuật toán lựa chọn

Thuật toán phải xử lý độc lập từng ngày hợp lệ trong toàn bộ tuần. Đơn vị dùng để xác định trạng thái của một ngày là **khung/buổi**, không phải số tiết riêng lẻ hoặc số môn học.

Trước khi random, hệ thống phải loại toàn bộ giờ rảnh hiện tại khỏi tập dữ liệu đầu vào và chỉ đếm số khung trong ngày có chứa ít nhất một tiết đang dạy. Giờ rảnh cũ không được dùng để xác định xác suất vì kết quả sẽ được sinh lại hoàn toàn.

Thuật toán sinh tuần tự và dừng khi phép thử thất bại, không còn khung hợp lệ hoặc đã đạt `maxGeneratedBlocksPerDay`:

1. Ghi nhận số khung có giờ dạy ban đầu là `teachingBlockCount` và đặt `generatedBlockCount = 0`.
2. Chỉ số dùng để lấy xác suất ở mỗi vòng là `teachingBlockCount + generatedBlockCount`.
3. Lấy xác suất tương ứng từ `generationChanceByBlockStage`: `0 → 100%`, `1 → 35%`, `2 → 10%`, từ `3` trở lên → `0%`.
4. Nếu phép thử thất bại, dừng xử lý ngày đó và giữ các khung đã sinh thành công trước đó.
5. Nếu thành công, chọn một khung ứng viên theo trọng số nhóm, thêm các tiết còn trống của khung vào kết quả, đánh dấu tên khung đã được chọn trong lượt chạy và tăng `generatedBlockCount`.
6. Một tên khung chỉ được chọn tối đa một lần trong cùng lượt sinh, kể cả khi khung đó bị giờ dạy chiếm một phần.
7. Lặp lại cho đến khi đạt một trong các điều kiện dừng.

Hệ quả với từng trạng thái ban đầu:

- **Không có khung đang dạy:** khung rảnh thứ nhất có xác suất 100%, khung thứ hai 35%, khung thứ ba 10%.
- **Có đúng một khung đang dạy:** khung rảnh thứ nhất có xác suất 35%, khung thứ hai 10%.
- **Có đúng hai khung đang dạy:** khung rảnh thứ nhất có xác suất 10%.
- **Có từ ba khung đang dạy trở lên:** không sinh giờ rảnh.

Khi phép thử 35% thành công, lựa chọn khung cần thêm theo trọng số sau:

- Tổng xác suất dành cho các khung ban ngày (sáng và chiều) là 90%; xác suất dành cho khung tối là 10%.
- Nếu cả khung sáng và khung chiều đều hợp lệ, chia đều phần xác suất ban ngày: sáng 45%, chiều 45%, tối 10%.
- Nếu chỉ còn một khung ban ngày hợp lệ và khung tối cũng hợp lệ, khung ban ngày có xác suất 90% và khung tối có xác suất 10%.
- Nếu khung sáng vẫn còn tiết trống, khung sáng tiếp tục là ứng viên ban ngày. Ví dụ, giảng viên dạy tiết 2–3 nhưng tiết 4–5 còn trống thì tỷ lệ chọn sáng/chiều/tối là 45%/45%/10%.
- Nếu toàn bộ khung sáng không còn tiết trống, khi phép thử 35% thành công hệ thống chọn khung chiều với xác suất 90% và khung tối với xác suất 10%.
- Nếu một hoặc nhiều khung không còn tiết trống, loại các khung đó khỏi tập ứng viên và chuẩn hóa lại trọng số trên các khung còn hợp lệ.

Với cấu hình mặc định `maxGeneratedBlocksPerDay = 1`, thuật toán dừng ngay sau khung đầu tiên nên hành vi tương đương quy tắc một khung mỗi ngày đã mô tả trước đó. Khi tăng giới hạn lên `2` hoặc `3`, các phép thử 35% và 10% tiếp theo mới được kích hoạt theo trình tự trên.

Tất cả tỷ lệ phải được đọc từ `CONFIG["availabilityGenerator"]`, không sử dụng magic number rải rác trong mã nguồn. Cấu hình sử dụng số nguyên trong khoảng `0–100`. Không dùng seed cố định trong môi trường chạy thực tế để mỗi lần sinh lại có thể cho kết quả khác nhau; tuy nhiên, thiết kế bộ sinh số ngẫu nhiên theo hướng có thể mock hoặc inject để unit test cho kết quả xác định.

## 5.3. Loại trừ giờ đang dạy

- Dữ liệu giờ đang dạy phải được lấy từ nguồn thời khóa biểu hiện có của giảng viên, không suy đoán từ trạng thái giao diện.
- Không tự động tạo bất kỳ slot nào trùng với `teachingSlots` hoặc cấu trúc dữ liệu tương đương trong codebase.
- Giờ đang dạy và giờ rảnh mới không được chồng lấn.
- Chỉ cần một tiết trong khung có giờ dạy thì khung đó được tính là một khung đã có dữ liệu khi xác định xác suất 35% hoặc 10%.
- Nếu khung chỉ bị chiếm một phần, hệ thống vẫn có thể chọn các tiết còn trống trong chính khung đó. Ví dụ, nếu giảng viên đang dạy tiết 2–3 thì khung sáng được tính là đã có dữ liệu, nhưng tiết 4–5 vẫn có thể được thêm làm giờ rảnh khi khung sáng được chọn.
- Các ô giờ đang dạy phải giữ nguyên trạng thái hiển thị hiện tại và không được chuyển thành giờ rảnh do thao tác tự động.

## 5.4. Giới hạn theo loại giảng viên

Tuân thủ quy tắc tại `doc/PHAN-TICH-RANG-BUOC.md`:

- Giảng viên thỉnh giảng (`GUEST`): chỉ tự động khai báo từ thứ Hai đến thứ Bảy.
- Giảng viên cơ hữu (`RESIDENT`): chỉ tự động khai báo từ thứ Hai đến thứ Sáu.
- Không tự động khai báo giờ rảnh vào Chủ nhật cho bất kỳ loại giảng viên nào.
- Chức năng này không được xóa hoặc thay đổi các giờ dạy đã được con người chốt trong hệ thống.

## 5.5. Sinh lại và thay thế dữ liệu giờ rảnh

- Luôn yêu cầu xác nhận trước khi sinh lại vì thao tác sẽ thay thế toàn bộ dữ liệu giờ rảnh hiện có.
- Sau khi xác nhận, xem `availabilitySlots` hiện tại là tập rỗng khi chạy thuật toán; không sử dụng giờ rảnh cũ để đếm số khung hoặc tính xác suất.
- Các tiết đang dạy có độ ưu tiên cao hơn kết quả sinh tự động, phải được giữ nguyên và luôn bị loại khỏi tập giờ rảnh mới.
- Vì `replaceExistingAvailability` bắt buộc là `true`, kết quả mới thay thế toàn bộ `availabilitySlots` cũ trong một lần cập nhật; không thực hiện phép hợp với dữ liệu cũ.
- Chuẩn hóa, sắp xếp và loại bỏ slot trùng lặp theo đúng định dạng mà frontend, API và backend hiện đang sử dụng.
- Số khung tối đa được sinh cho mỗi ngày phải lấy từ `maxGeneratedBlocksPerDay`; giá trị mặc định là `1`.
- Chỉ cập nhật trạng thái giao diện sau khi API lưu thành công. Nếu API thất bại, dữ liệu giờ rảnh cũ phải tiếp tục hiển thị và không được coi là đã bị xóa.

# 6. Cấu hình, dữ liệu và API

## 6.1. Cấu hình `availabilityGenerator`

Bổ sung nhóm cấu hình cấp cao `availabilityGenerator` trong `webapp/config.json`. Một bộ cấu hình dùng chung cho cả giảng viên cơ hữu (`RESIDENT`) và thỉnh giảng (`GUEST`). Schema mặc định:

{
  "availabilityGenerator": {
    "sessionBlocks": {
      "morning": {
        "startPeriod": 2,
        "endPeriod": 5,
        "selectionGroup": "daytime"
      },
      "afternoon": {
        "startPeriod": 6,
        "endPeriod": 9,
        "selectionGroup": "daytime"
      },
      "evening": {
        "startPeriod": 10,
        "endPeriod": 12,
        "selectionGroup": "evening"
      }
    },
    "selectionGroupWeights": {
      "daytime": 90,
      "evening": 10
    },
    "generationChanceByBlockStage": {
      "0": 100,
      "1": 35,
      "2": 10,
      "3OrMore": 0
    },
    "maxGeneratedBlocksPerDay": 1,
    "replaceExistingAvailability": true
  }
}

Ý nghĩa:

- `sessionBlocks`: định nghĩa tên khung, tiết bắt đầu, tiết kết thúc và nhóm trọng số của khung.
- `selectionGroupWeights`: tổng trọng số chọn nhóm. Hai khung `morning` và `afternoon` chia đều trọng số `daytime`; nếu chỉ còn một khung ban ngày hợp lệ thì khung đó nhận toàn bộ trọng số của nhóm.
- `generationChanceByBlockStage`: xác suất sinh khung tiếp theo theo chỉ số giai đoạn; chỉ số ban đầu bằng số khung đang dạy và tăng thêm một sau mỗi khung rảnh được sinh thành công.
- `maxGeneratedBlocksPerDay`: số khung rảnh tối đa được sinh trong một ngày cho mỗi lần chạy. Giá trị mặc định là `1`; khi tăng lên `2` hoặc `3`, thuật toán tiếp tục qua phép thử 35% rồi 10% theo số khung dạy và số khung đã sinh.
- `replaceExistingAvailability`: bắt buộc là `true`; kết quả mới luôn thay thế toàn bộ giờ rảnh cũ sau khi người dùng xác nhận.
- Không thêm seed cố định vào cấu hình. Mỗi lần sinh lại có thể cho kết quả khác nhau.

## 6.2. Nạp cấu hình và giá trị mặc định

- Cập nhật `webapp/app_config.py` để nạp và validate `availabilityGenerator` cùng các nhóm cấu hình hiện có.
- Nếu toàn bộ khóa `availabilityGenerator` không tồn tại, tự động sử dụng nguyên bộ giá trị mặc định ở trên để tương thích với file cấu hình cũ.
- Nếu `availabilityGenerator` có tồn tại nhưng sai kiểu, thiếu trường con hoặc chứa giá trị không hợp lệ, dừng khởi động và trả về thông báo lỗi chỉ rõ đường dẫn cấu hình bị lỗi; không âm thầm fallback vì có thể che giấu lỗi gõ sai.
- Không thay đổi trực tiếp object JSON nguồn ngoài việc tạo cấu hình runtime đã chuẩn hóa.

Validation bắt buộc:

- `startPeriod` và `endPeriod` là số nguyên; `1 <= startPeriod <= endPeriod <= calendar.slotsPerDay`.
- Các khung không được chồng lấn và mỗi `selectionGroup` phải tồn tại trong `selectionGroupWeights`.
- Mọi trọng số và xác suất là số nguyên trong khoảng `0–100`, không chấp nhận boolean.
- Tổng `selectionGroupWeights` phải bằng `100`.
- `generationChanceByBlockStage` phải có đủ các khóa `0`, `1`, `2`, `3OrMore`.
- `maxGeneratedBlocksPerDay` là số nguyên từ `1` đến số lượng `sessionBlocks`.
- `replaceExistingAvailability` phải là boolean và phải có giá trị `true`; giá trị `false` chưa được hỗ trợ vì trái với nghiệp vụ sinh lại toàn bộ.

## 6.3. Dữ liệu xử lý

Dữ liệu đầu vào:

- Loại giảng viên (`GUEST` hoặc `RESIDENT`).
- Danh sách ngày và `calendar.slotsPerDay`.
- Danh sách giờ rảnh hiện tại (`availabilitySlots`) để thay thế sau khi xác nhận.
- Danh sách giờ đang dạy (`teachingSlots`) được suy ra từ thời khóa biểu đã chốt.
- Cấu hình runtime `availabilityGenerator` đã được validate và áp dụng fallback.

Dữ liệu cần lưu:

- Danh sách slot giờ rảnh mới sau khi tự động sinh; danh sách này thay thế toàn bộ dữ liệu giờ rảnh cũ.
- Dữ liệu phải sử dụng đúng schema availability hiện tại; không tạo nguồn dữ liệu song song chỉ dành cho chức năng tự động.

## 6.4. API chuyên dụng

- Bổ sung endpoint backend chuyên dụng theo convention hiện tại, đề xuất: `POST /api/manual/teacher/<int:teacher_id>/generate-availability`.
- Frontend chỉ gọi endpoint sau khi người dùng xác nhận trong popup.
- Backend phải kiểm tra giảng viên tồn tại, đọc cấu hình runtime, lấy giờ đang dạy, chạy thuật toán, chuẩn hóa slot và thay thế giờ rảnh.
- Sinh toàn bộ kết quả trong biến tạm; chỉ cập nhật `manual_teacher_windows`, đồng bộ các lớp liên quan và lưu snapshot sau khi thuật toán hoàn tất thành công.
- Nếu có lỗi trước khi hoàn tất, không được thay đổi dữ liệu giờ rảnh cũ.
- Tái sử dụng decorator phân quyền/kiểm tra dữ liệu, hàm response, đồng bộ lớp và cơ chế lưu snapshot đang dùng tại `webapp/api/manual_teacher.py`.
- Response thành công phải cung cấp dữ liệu mới nhất và đủ thông tin để frontend hiển thị thông báo thành công.

## 6.5. Yêu cầu tương thích

- Dữ liệu giờ rảnh hiện tại chỉ được thay thế sau khi người dùng xác nhận và API cập nhật thành công.
- Không được thay đổi hoặc xóa dữ liệu giờ đang dạy.
- Phải giữ nguyên dữ liệu cũ nếu người dùng hủy hoặc endpoint thất bại.
- File config cũ chưa có `availabilityGenerator` vẫn phải khởi động bằng bộ giá trị mặc định.
- Chỉ thay đổi cấu trúc dữ liệu hoặc API khi thực sự cần thiết.

# 7. Phạm vi triển khai

AI Agent cần:

1. Khảo sát codebase trước khi chỉnh sửa.
2. Xác định frontend, backend, API, model và database liên quan.
3. Trình bày ngắn gọn hiện trạng và kế hoạch triển khai.
4. Ưu tiên tái sử dụng component, utility và pattern có sẵn.
5. Bổ sung `availabilityGenerator` vào `webapp/config.json` theo schema đã thống nhất.
6. Cập nhật `webapp/app_config.py` để cung cấp fallback và validation đầy đủ.
7. Triển khai thuật toán tại backend và endpoint chuyên dụng theo convention của `api/manual_teacher.py`.
8. Tích hợp frontend với popup xác nhận, trạng thái loading, xử lý lỗi và thông báo thành công.
9. Không để frontend tự thực hiện random hoặc sao chép các giá trị xác suất từ config.
10. Viết hoặc cập nhật test cho cấu hình, thuật toán, API và giao diện.
11. Chạy các bước kiểm tra cần thiết như test, lint, typecheck và build.
12. Báo cáo những file đã thay đổi và kết quả kiểm tra.

# 8. Ràng buộc

- Không thay đổi những chức năng không liên quan.
- Không tự ý thay đổi kiến trúc tổng thể của dự án.
- Không thêm dependency mới nếu có thể sử dụng công cụ hiện tại.
- Không phá vỡ API hoặc dữ liệu cũ.
- Không xóa các quy tắc nghiệp vụ đang tồn tại.
- Tuân thủ convention và cấu trúc code hiện có.
- Không chỉ sửa giao diện bằng dữ liệu giả; chức năng phải hoạt động với dữ liệu thật.
- Nếu yêu cầu chưa rõ hoặc có nhiều phương án ảnh hưởng đến nghiệp vụ, hãy hỏi lại trước khi triển khai.
- Không thực hiện thao tác phá hủy dữ liệu hoặc migration nguy hiểm.

# 9. Tiêu chí nghiệm thu

Chức năng được coi là hoàn thành khi:

- Nút "Tự động khai giờ rảnh" xuất hiện đúng vị trí trong nhóm thao tác của lưới giờ rảnh.
- Mỗi ngày hợp lệ chỉ được tự động chọn các tiết thuộc một trong ba khung đã định nghĩa.
- Ngày hoàn toàn trống chọn khung sáng, chiều và tối theo đúng tỷ lệ 45%/45%/10%.
- Khi không có khung đang dạy, xác suất sinh khung rảnh thứ nhất/thứ hai/thứ ba lần lượt là 100%/35%/10%; khi đã có một khung dạy thì bắt đầu từ 35%, khi đã có hai khung dạy thì bắt đầu từ 10%.
- Quá trình dừng khi phép thử thất bại, hết khung ứng viên hoặc đạt `maxGeneratedBlocksPerDay`.
- Giờ rảnh cũ không được dùng để đếm trạng thái ngày hoặc tính xác suất.
- Khi phép thử 35% thành công, các khung ban ngày còn tiết trống nhận tổng trọng số 90% và khung tối nhận trọng số 10%; nếu cả sáng và chiều đều hợp lệ thì tỷ lệ là 45%/45%/10%.
- Nếu toàn bộ khung sáng đã bị chiếm, trong khi chiều và tối còn trống, hệ thống chọn chiều với xác suất 90% và tối với xác suất 10%.
- Nếu khung sáng chỉ bị chiếm một phần, phần còn trống của sáng vẫn là ứng viên; khi sáng, chiều và tối đều còn tiết trống thì tỷ lệ là 45%/45%/10%.
- Ngày có giờ dạy trong từ ba khung trở lên không được sinh thêm giờ rảnh.
- Số khung được sinh trong ngày không vượt `maxGeneratedBlocksPerDay`; mỗi tên khung chỉ được chọn một lần trong cùng lượt chạy.
- Với giá trị mặc định `maxGeneratedBlocksPerDay = 1`, mỗi ngày chỉ sinh tối đa một khung; cấu hình 2 hoặc 3 phải kích hoạt đúng chuỗi phép thử tiếp theo.
- Không có tiết đang dạy nào bị đánh dấu thành giờ rảnh bởi chức năng tự động.
- Giảng viên cơ hữu không được tự động chọn thứ Bảy hoặc Chủ nhật.
- Giảng viên thỉnh giảng không được tự động chọn Chủ nhật.
- Khung tối mặc định chỉ bao gồm tiết 10–12, dù `calendar.slotsPerDay` hiện hỗ trợ đến tiết 13.
- Mỗi lần nhấn nút đều hiển thị xác nhận rằng toàn bộ giờ rảnh hiện tại sẽ bị xóa và sinh lại.
- Chọn "Hủy" không làm thay đổi dữ liệu; chọn xác nhận sẽ thay thế toàn bộ giờ rảnh cũ bằng kết quả mới và lưu ngay.
- Sau khi lưu thành công, hệ thống cập nhật lưới và hiển thị thông báo thành công ngắn gọn.
- Nếu lưu thất bại, dữ liệu giờ rảnh cũ vẫn được giữ nguyên và hiển thị chính xác.
- Dữ liệu mới được tải lại và hiển thị chính xác khi mở lại thông tin giảng viên.
- Không xuất hiện slot trùng lặp hoặc slot nằm ngoài phạm vi cấu hình.
- Thuật toán đọc khung, trọng số, xác suất và giới hạn từ `CONFIG["availabilityGenerator"]`; không hard-code các giá trị nghiệp vụ.
- Thiếu toàn bộ `availabilityGenerator` phải sử dụng đúng bộ mặc định; cấu hình có tồn tại nhưng không hợp lệ phải làm ứng dụng dừng với lỗi rõ ràng.
- `replaceExistingAvailability: false` bị từ chối bởi validation; `maxGeneratedBlocksPerDay` chấp nhận từ 1 đến số khung cấu hình.
- Endpoint chuyên dụng thực hiện sinh và thay thế dữ liệu theo kiểu all-or-nothing: lỗi giữa chừng không được làm mất giờ rảnh cũ.
- Không sử dụng seed cố định trong runtime, nhưng test có thể mock bộ sinh số ngẫu nhiên.
- Validation và thông báo lỗi hoạt động đúng.
- Không ảnh hưởng đến chức năng khai báo giờ rảnh thủ công hiện tại.
- Có test cho thuật toán sinh tuần tự với giới hạn 1/2/3, trọng số chọn khung, khung bị chiếm một phần, giới hạn ngày theo loại giảng viên, fallback/validation cấu hình, endpoint chuyên dụng, hộp thoại xác nhận, hành vi thay thế dữ liệu và việc loại trừ giờ đang dạy.
- Các bài test và bước kiểm tra của dự án đều vượt qua.

# 10. Cách AI Agent phản hồi

Trước khi viết code, hãy cung cấp:

1. Các file và luồng xử lý liên quan.
2. Tóm tắt cách chức năng hiện tại hoạt động.
3. Phương án triển khai đề xuất.
4. Những điểm chưa rõ cần xác nhận.

Chỉ bắt đầu chỉnh sửa sau khi đã hiểu rõ yêu cầu.

Sau khi hoàn thành, hãy cung cấp:

1. Tóm tắt thay đổi.
2. Danh sách file đã chỉnh sửa.
3. Các quyết định kỹ thuật quan trọng.
4. Kết quả test, lint, typecheck và build.
5. Các giới hạn hoặc vấn đề còn tồn tại.
```

## Lịch sử cập nhật

| Ngày | Nội dung |
|---|---|
| 2026-09-21 | Tạo khung prompt ban đầu |
| 2026-09-21 | Bổ sung tên, mô tả và mục tiêu của chức năng tự động khai báo giờ rảnh |
| 2026-09-21 | Bổ sung luồng thao tác, vị trí nút, thuật toán chọn khung giờ, giới hạn theo loại giảng viên và tiêu chí nghiệm thu |
| 2026-09-21 | Chốt tỷ lệ xác suất, quy tắc theo số khung đã có, hợp nhất dữ liệu cũ và lưu ngay khi tự động khai báo |
| 2026-09-21 | Chốt quy tắc ưu tiên 90% cho khung ban ngày và 10% cho khung tối sau khi phép thử 35% thành công |
| 2026-09-21 | Bổ sung xác nhận sinh lại, thay thế toàn bộ giờ rảnh, giữ nguyên giờ dạy, giới hạn khung tối đến tiết 12 và thông báo thành công |
| 2026-09-21 | Thiết kế `availabilityGenerator`, fallback/validation config, thuật toán sinh tuần tự và endpoint backend chuyên dụng |
