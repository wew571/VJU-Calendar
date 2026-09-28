# Prompt tìm nguyên nhân Liquid Glass không hiện trên máy khác

> Đây là prompt để giao việc cho AI Agent. Những nguyên nhân nêu bên dưới chỉ là điều cần kiểm tra, **chưa phải kết luận**. Nếu thiếu thông tin từ máy người khác, hãy hỏi thay vì tự đoán.

## Prompt

```text
Bạn là AI Agent hỗ trợ dự án VJU-Calendar. Hãy tìm hiểu vì sao giao diện Liquid Glass hiện trên máy của người phát triển nhưng không hiện trên máy của một người khác sau khi người đó kéo mã từ GitHub về. Sau khi tìm được nguyên nhân và có bằng chứng, hãy sửa đúng phần gây ra vấn đề và kiểm tra lại.

# 1. Tình huống

- Người phát triển đã viết tính năng Liquid Glass và đẩy mã lên GitHub. Trên máy của họ, webapp có hiệu ứng này.
- Một người khác kéo mã về và chạy webapp, nhưng toàn bộ giao diện trên máy đó không có Liquid Glass. Người này dùng Windows 11 và Microsoft Edge.
- Chưa rõ hai người đã chạy lệnh nào, mở địa chỉ web nào, đang ở cùng phiên bản mã hay chưa. Có thể có ảnh so sánh, nhưng nếu bạn chưa nhận được thì hãy xin ảnh từ cả hai máy.
- Mục đích là tìm ra sự khác biệt thực sự, không phải thiết kế lại giao diện Liquid Glass.

# 2. Điều cần làm trước khi sửa

1. Hỏi người dùng những thông tin còn thiếu: ảnh của cùng một màn trên hai máy (nếu có), lệnh chạy web, địa chỉ web đang mở, và máy người phát triển dùng trình duyệt nào. Nếu cần, hỏi thêm bước để nhìn thấy lỗi trên máy kia.
2. Xác nhận hai máy đang xem đúng ứng dụng, đúng màn và cùng phiên bản mã. Kiểm tra nhánh và mã phiên bản Git trên từng máy; đừng coi việc đã "pull" là bằng chứng chắc chắn rằng hai bên có cùng mã.
3. Kiểm tra địa chỉ mà chương trình in ra khi chạy. Dự án có thể mở giao diện bằng Vite để phát triển, hoặc bằng Flask từ bản giao diện đã build. Trong `main.py`, Vite và Flask chạy cùng lúc nhưng ở hai địa chỉ khác nhau. Cổng của Vite cũng có thể đổi nếu cổng thường dùng đã bị chiếm. Hãy xác định người kia thực sự đã mở địa chỉ nào; đừng kết luận từ số cổng thường gặp.
4. Nếu họ mở giao diện từ Flask, kiểm tra `frontend/dist` có phải bản mới không: thư mục này không được đưa lên Git và không tự cập nhật chỉ vì đã pull mã. Nếu họ mở Vite, kiểm tra nó có đang chạy từ đúng thư mục dự án và đang tải mã mới không.
5. Kiểm tra các tệp tạo hiệu ứng có thực sự được dùng trên trang: `frontend/src/main.jsx` nạp `app.css`, `app.css` nạp `styles.css` trong lớp `legacy`. `app.css` chứa kiểu kính của nền, thanh điều hướng và bảng; `styles.css` chứa kiểu của các thanh buổi học `.lesson-bar`. Hãy xem trang có nhận các kiểu này không, có lỗi tải tệp không, hoặc có kiểu khác ghi đè lên chúng không. Xem cả màn chọn vai trò, khung trang và lưới lịch để biết vấn đề nằm ở đâu.
6. Nếu mã và cách mở trang đều đúng, so sánh Microsoft Edge, cài đặt hiển thị, khả năng hiện hiệu ứng trong suốt, dữ liệu trang cũ được trình duyệt giữ lại và lỗi báo trên trình duyệt. Kiểm tra việc cài thư viện và tạo bản giao diện nếu có dấu hiệu liên quan. Những điều này chỉ là hướng kiểm tra, không phải nguyên nhân đã được xác nhận.

# 3. Cách tìm và xử lý nguyên nhân

- Làm từng bước, ghi lại điều đã thấy trên mỗi máy: mã phiên bản, địa chỉ trang, cách chạy, tệp kiểu dáng có tải không, và kết quả so sánh hình ảnh. Chỉ kết luận nguyên nhân khi có bằng chứng cho thấy vì sao một bên có Liquid Glass còn bên kia không có.
- Nếu có thể, làm cho lỗi xuất hiện lại trong điều kiện tương tự rồi kiểm tra cách khắc phục. Nếu bạn không thể truy cập máy người kia, nói rõ phần nào chỉ người đó mới kiểm tra được và đưa các bước ngắn gọn để họ làm theo.
- Sửa ít nhất có thể để hai máy hiển thị đúng thiết kế hiện tại. Nếu vấn đề chỉ là mở nhầm trang, dùng bản build cũ hoặc chạy sai cách, hãy hướng dẫn cách chạy đúng; không sửa mã giao diện khi không cần. Nếu lỗi nằm trong mã giao diện, sửa đúng chỗ và kiểm tra lại. Không làm lại thiết kế, không tự thêm thư viện hay thay đổi thuật toán xếp lịch, dữ liệu, quyền sử dụng hoặc backend không liên quan.
- Không xóa dữ liệu hoặc thư mục của người dùng để thử sửa lỗi. Không coi việc làm mất hiệu ứng trên cả hai máy là cách khắc phục.

# 4. Kiểm tra sau khi xử lý

- Kiểm tra lại màn chọn vai trò, khung trang và lưới lịch trên Microsoft Edge nếu có thể. Khi có dữ liệu lịch, xem cả thanh buổi học hẹp và chế độ xem chi tiết; chữ, màu trạng thái và thao tác vẫn phải rõ và dùng được.
- Kiểm tra đúng cách chạy đã gây ra lỗi. Nếu cách mở bằng Vite và cách mở bằng Flask đều có liên quan, kiểm tra cả hai để tránh một bên vẫn dùng giao diện cũ.
- Chạy `npm test` và `npm run build` trong `frontend/` khi có `config/frontend.json` hợp lệ; nêu rõ nếu chưa thể chạy do thiếu cấu hình hoặc chưa có quyền truy cập máy người kia. Không tự điền cấu hình thật bằng thông tin đoán mò.
- Nêu kết quả đã tự kiểm chứng và các bước người kia cần làm để xác nhận giao diện đã có Liquid Glass. Nếu không xác nhận được trực tiếp trên máy đó, đừng nói rằng lỗi đã được giải quyết chắc chắn.

# 5. Cập nhật hướng dẫn chạy nếu cần

Sau khi kiểm tra nguyên nhân, hãy rà soát `README.md` và `doc/run.md`. Nếu cách cài, chạy, tạo bản giao diện hoặc mở đúng địa chỉ có liên quan đến lỗi mà tài liệu đang thiếu hoặc viết dễ gây hiểu nhầm, hãy sửa những phần bị ảnh hưởng trong hai tệp này để người mới làm theo được. Nếu một tệp không bị ảnh hưởng, giữ nguyên và nói ngắn gọn vì sao. Không sửa tài liệu chỉ cho đủ tên tệp.

# 6. Cách báo lại cho người dùng

Viết bằng tiếng Việt dễ hiểu và nêu:
1. Nguyên nhân đã tìm được và bằng chứng cụ thể; nếu chưa đủ bằng chứng, nêu rõ điều còn thiếu thay vì đoán.
2. Những gì đã sửa, những tệp đã thay đổi, và vì sao cần sửa.
3. Các bước đơn giản để người kia chạy lại và thấy đúng giao diện.
4. Kết quả kiểm tra, phần chưa kiểm tra được, và `README.md` / `doc/run.md` có được sửa hay không.
```

## Lịch sử cập nhật

| Ngày | Nội dung |
|---|---|
| 2026-09-25 | Tạo prompt điều tra sự khác biệt Liquid Glass giữa hai máy; yêu cầu sửa đúng nguyên nhân, kiểm tra lại và cập nhật hướng dẫn chạy khi có liên quan. |
