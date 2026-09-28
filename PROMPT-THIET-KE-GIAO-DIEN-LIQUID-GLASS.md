# Prompt thiết kế lại giao diện theo hướng Liquid Glass

> Đây là prompt giao việc cho AI Agent, không phải yêu cầu thực hiện ngay khi chưa chốt phương án thiết kế. Các nội dung trong dấu `[CẦN CHỐT: ...]` cần được hỏi và xác nhận với người dùng; không được tự suy đoán rồi triển khai.

## Prompt

```text
Bạn là một AI Agent chuyên thiết kế và phát triển giao diện web. Hãy khảo sát codebase VJU-Calendar, đề xuất phương án và, sau khi người dùng duyệt hướng thiết kế, triển khai giao diện theo hướng Liquid Glass.

# 1. Bối cảnh

VJU-Calendar là công cụ web hỗ trợ xếp thời khóa biểu. Giao diện hiện dùng React + Vite, Tailwind CSS v4, các primitive kiểu shadcn/ui và Radix; backend là Flask. Có hai vai trò cục bộ: giáo vụ/điều phối viên (staff) và xem thôi (viewer). Mục tiêu của công việc này là làm mới phần nhìn của toàn bộ frontend, không xây dựng lại hệ thống hoặc thay đổi nghiệp vụ.

Các điểm vào cần tự kiểm tra lại trong codebase trước khi sửa:
- `frontend/src/main.jsx`: điểm vào React và CSS.
- `frontend/src/app.css`: token design system VJU, Tailwind và thứ tự cascade layer; nạp `styles.css` trong layer `legacy`.
- `frontend/src/styles.css`: CSS riêng cho lưới thời khóa biểu, heatmap, bảng dữ liệu dày đặc và các trạng thái liên quan.
- `frontend/src/App.jsx`, `frontend/src/constants/nav.js`: chọn vai trò, trang và điều hướng.
- `frontend/src/components/layout/`: topbar, sidebar và khung trang.
- `frontend/src/components/ui/`, `frontend/src/components/shared/`: primitive và thành phần dùng chung.
- `frontend/src/presentation/`: màn chọn vai trò, các trang, lưới lịch, bảng, modal, drawer và những thành phần nghiệp vụ khác.

Danh sách trên là bản đồ khởi đầu, không phải danh sách file được phép sửa cố định. Hãy kiểm tra các thành phần đang thực sự được render, cách chúng nhận dữ liệu và cách CSS áp dụng trước khi đề xuất phương án. Backend/API chỉ được đọc để hiểu luồng nếu cần; không thuộc phạm vi thay đổi.

# 2. Mục tiêu và định nghĩa công việc

Tên công việc: Làm mới giao diện toàn hệ thống theo hướng Liquid Glass.

Mục tiêu:
- Tạo ngôn ngữ thị giác nhất quán cho toàn bộ frontend trong chế độ sáng (light mode): cảm giác nhiều lớp, bề mặt trong mờ có kiểm soát, ánh sáng, viền và chiều sâu; không chỉ thêm `backdrop-filter` cho mọi phần tử.
- Giữ tính dễ đọc, thao tác nhanh và tín hiệu trạng thái của một công cụ có nhiều dữ liệu lịch/bảng. Chất liệu kính phải hỗ trợ nội dung, không làm nội dung khó quan sát.
- Giữ nguyên cách sử dụng, điều hướng, quyền của hai vai trò, dữ liệu và hành vi nghiệp vụ. Cho phép điều chỉnh khoảng cách, kích thước và một phần logic frontend phục vụ trình bày/chuyển động, nhưng không thiết kế lại luồng hay bố cục chức năng.

Chỉ thực hiện light mode trong đợt này. Không tự bật `.dark`, không triển khai dark mode nửa vời.

# 3. Quy trình và cổng duyệt bắt buộc

1. Khảo sát các trang, thành phần chung, CSS, trạng thái tương tác và những ràng buộc đặc biệt của lưới lịch, bảng Excel, sticky, fullscreen và modal.
2. Trước khi sửa giao diện, báo cáo ngắn gọn hiện trạng và đề xuất HAI hướng Liquid Glass khác nhau. Với mỗi hướng, nêu rõ bề mặt/nền, độ nổi bật của hiệu ứng, mức độ phù hợp với màn dữ liệu dày, chuyển động, ưu/nhược điểm và các màn nên xem trước. Có thể dùng mô tả, moodboard hoặc preview nếu điều kiện cho phép; không tự coi preview là phương án đã được duyệt.
3. Hỏi người dùng và DỪNG chờ trả lời về những điểm sau:
   - `[CẦN CHỐT: Mức độ giữ màu đỏ, logo, font và các yếu tố nhận diện VJU trên giao diện mới?]` Phân biệt việc giữ nguyên token nguồn trong code với quyết định màu sắc/bố cục sử dụng trên từng bề mặt UI.
   - Ảnh người dùng đã gửi trong chat là ví dụ KHÔNG MONG MUỐN: lưới lịch với những thanh xanh dương, xanh lá và đỏ tô đặc, phẳng, che hoàn toàn nền. Không được lấy ảnh này làm mẫu đích. `[CẦN CHỐT: Có ảnh/đường dẫn tham chiếu tích cực khác không? Nếu chưa có, người dùng chọn hướng nào trong hai hướng Agent đề xuất?]`
   - Nếu hai hướng khác nhau đáng kể về mức độ chuyển động, hỏi người dùng chọn mức độ cụ thể trong hướng đã duyệt.
4. Chỉ bắt đầu sửa frontend sau khi người dùng chọn phương án và trả lời những câu hỏi có ảnh hưởng tới thiết kế. Nếu câu trả lời còn mơ hồ, hỏi tiếp đúng điểm mơ hồ; không tự chốt thay.
5. Triển khai theo hướng đã được duyệt, xác minh giao diện và hành vi thực tế, báo cáo kết quả cùng các giới hạn còn lại.

# 4. Yêu cầu giao diện

- Thiết kế hệ phân cấp thị giác nhất quán: canvas/nền, topbar/sidebar, page header, thẻ/panel, thanh công cụ, điều khiển, dropdown, tooltip, dialog/drawer và trạng thái phủ. Dùng độ trong suốt, blur, viền sáng, bóng và highlight có tiết chế theo vai trò từng lớp.
- Có thể dùng chuyển động/hiệu ứng ánh sáng nổi bật hơn mức tối giản, kể cả phản hồi theo hover hoặc con trỏ, nhưng phải có mục đích rõ ràng, mượt trên Microsoft Edge, không gây xao nhãng khi đọc bảng/lịch hoặc cản trở thao tác.
- Thiết kế đầy đủ trạng thái mặc định, hover, active/selected, focus-visible, disabled, loading, thành công, cảnh báo và lỗi. Không biểu đạt trạng thái chỉ bằng màu hoặc độ trong suốt.
- Nội dung quan trọng, chữ nhỏ, nhãn biểu mẫu, badge, trạng thái tiết học và thao tác nguy hiểm phải có độ tương phản rõ trên nền thực tế nằm sau lớp kính; không đặt chữ lên nền mờ biến thiên nếu không có lớp lót đủ chắc.
- Yêu cầu thị giác trọng tâm cho các khung/thẻ/thanh màu: giữ màu gốc của từng loại/trạng thái ở mép/viền, cho sắc độ hoặc độ đậm giảm mềm dần từ mép về trung tâm; phần giữa sáng và trong hơn, nhìn xuyên nhẹ thấy lớp nền/vạch lưới hoặc vật thể nằm phía sau. Tạo chiều sâu như một lớp kính nhuộm màu, không phải màu đặc tô kín, không biến tâm thành lỗ trong suốt hoàn toàn hoặc làm mất màu nhận diện. Có thể phối gradient alpha, viền sáng, phản chiếu và blur nhẹ tùy thành phần; cần bảo đảm viền/các dấu hiệu trạng thái vẫn nhận ra được.
- Ảnh lưới lịch mà người dùng gửi trong chat là ví dụ cần TRÁNH: các thanh lịch xanh dương/xanh lá/đỏ đặc, phẳng, che nền. Áp dụng ngôn ngữ kính nêu trên cả cho thanh buổi học trong lưới lịch (`LessonCard`, `.lesson-bar`, kể cả thẻ ở chế độ chi tiết), không chỉ cho topbar và panel; kiểm tra trên các thanh rất hẹp để viền và vùng tâm vẫn phân biệt được.
- Với lưới thời khóa biểu, heatmap và bảng nhập liệu kiểu Excel: ưu tiên sự sắc nét, mật độ thông tin, màu trạng thái và khả năng quét hàng/cột. Đổi bề mặt các thanh/thẻ buổi học có chọn lọc, nhưng không phủ blur riêng lên từng ô nền lưới/heatmap hoặc từng ô bảng; không để hiệu ứng mới xóa mất đường kẻ, nhãn, highlight hay cảnh báo.
- Giữ layout hợp lý trên desktop, tablet và màn hình nhỏ; không gây tràn nút, che chữ, tạo thanh cuộn ngoài ý muốn hoặc làm mất chỗ cho lưới/bảng vốn cần chiều rộng.
- Nền và hiệu ứng phải có phương án dự phòng dễ đọc khi `backdrop-filter` không khả dụng hoặc bị hạn chế. Tôn trọng `prefers-reduced-motion`, bàn phím và trạng thái focus; tránh animation liên tục trên vùng dữ liệu lớn.
- Không thêm nội dung giả, số liệu demo hoặc thay đổi văn bản mang ý nghĩa nghiệp vụ chỉ để làm đẹp.

# 5. Quy tắc bảo toàn luồng và trạng thái

- Giữ nguyên lựa chọn vai trò, giới hạn quyền của viewer, điều hướng sidebar hai cấp, khả năng thu gọn sidebar trên các trang rộng và drawer menu trên màn nhỏ.
- Không phá vỡ chiều cao/khung cuộn của trang dữ liệu học phần, header/cột sticky của bảng Excel, vị trí ô lưới thời khóa biểu, kéo-thả buổi học và chế độ lịch toàn màn hình.
- Giữ đúng thứ tự lớp hiển thị của overlay, dialog/drawer, popover, màn hình giải thuật và chế độ toàn màn hình. Dialog không được bị phủ che hoặc vô hiệu hóa thao tác.
- Giữ nguyên khả năng xem và thao tác các trạng thái: rỗng, đang tải/đang xử lý, có dữ liệu, cảnh báo/lỗi và xác nhận hành động.
- Nếu cần thay logic frontend để điều khiển hiệu ứng, phải tách nó khỏi logic nghiệp vụ và không thay đổi request/response, dữ liệu lưu, quyền truy cập hay kết quả thuật toán.

# 6. Kiến trúc CSS, tài nguyên và hiệu năng

- Tái sử dụng React components, Tailwind và CSS có sẵn. Ưu tiên một lớp token/style chuyên cho bề mặt glass thay vì sao chép các giá trị blur/bóng/viền rải rác khắp trang.
- Giữ nguyên giá trị token design system VJU gốc đang được đồng bộ với ứng dụng tham chiếu trong `frontend/src/app.css`. Nếu phương án được duyệt không thể thực hiện mà buộc phải thay token gốc hoặc làm lệch nhận diện đã thống nhất, phải giải thích và xin phép riêng trước khi sửa.
- Tuân thủ thứ tự `@layer` trong `app.css`; `styles.css` đã được nhập qua layer `legacy`, không nhập trực tiếp lần nữa từ `main.jsx`. Tránh CSS override toàn cục gây ảnh hưởng tới bảng/lưới ngoài ý muốn.
- ĐƯỢC PHÉP dùng hoặc bổ sung thư viện frontend hỗ trợ hiệu ứng kính, gradient và chuyển động khi giúp hiện thực thiết kế tốt hơn. Thư viện phải tích hợp trong stack React + Vite + Tailwind CSS hiện tại, dùng được với component shadcn/Radix đang có; không thay framework, không dựng frontend song song, không thêm dependency vào backend. Cân nhắc kích thước bundle, hiệu năng trên Microsoft Edge, bảo trì, tương thích và an toàn phiên bản; nêu lý do chọn trong báo cáo. Không bắt buộc dùng thư viện nếu CSS hiện có là đủ.
- Tránh blur/animation nặng trên số lượng lớn ô lịch/bảng, và tránh thay đổi kích thước/bố cục liên tục khi cuộn hoặc kéo-thả. Nếu dùng phản ứng theo vị trí con trỏ, giới hạn trong vùng phù hợp, có cơ chế tắt cho reduced-motion và thiết bị không thích hợp.
- Không đưa dữ liệu nhạy cảm vào asset, code mẫu hoặc báo cáo; không thay đổi thiết lập an ninh hay cấu hình dự án không liên quan.

# 7. Phạm vi triển khai

AI Agent cần:

1. Khảo sát toàn bộ bề mặt frontend được render cho cả staff và viewer, bao gồm màn chọn vai trò, các trang chính, dialog/drawer, trạng thái rỗng/lỗi/loading và chế độ toàn màn hình.
2. Xác định các thành phần dùng chung để triển khai ngôn ngữ glass nhất quán trước; ghi nhận các ngoại lệ cố ý cho lưới, heatmap và bảng dày đặc.
3. Trình bày hai hướng thiết kế, câu hỏi còn thiếu và chờ duyệt theo mục 3 trước khi chỉnh sửa.
4. Sau khi duyệt, cập nhật lớp giao diện chung và các màn cụ thể theo hướng đã chọn; chỉ sửa logic frontend khi cần để hỗ trợ hiển thị/chuyển động.
5. Kiểm thử hành vi liên quan, chạy kiểm tra frontend và rà soát trực quan trên Microsoft Edge với độ rộng desktop và màn nhỏ.
6. Báo cáo file đã thay đổi, các ngoại lệ thiết kế, kết quả kiểm tra và những việc cần người dùng quyết định thêm.

Ngoài phạm vi: backend Flask, API, mô hình dữ liệu, thuật toán xếp lịch, thay đổi nghiệp vụ/phân quyền, đổi cấu trúc điều hướng, dark mode và chỉnh sửa ứng dụng VJU tham chiếu bên ngoài repo.

# 8. Ràng buộc

- Không thay đổi các chức năng không liên quan hoặc các quy tắc nghiệp vụ đang tồn tại.
- Không đánh đổi khả năng đọc, accessibility, độ ổn định của thao tác dữ liệu và hiệu năng để có hiệu ứng kính mạnh hơn.
- Không thay token VJU gốc, không tự ý nhân bản stylesheet legacy hoặc làm hỏng cascade layer.
- Không để lớp kính/animation che mất trạng thái đang được chọn, thông báo nguy hiểm hoặc nút xác nhận.
- Cho phép dùng thư viện hỗ trợ trong React/Vite/Tailwind hiện có; không được thay framework hoặc bổ sung bộ ứng dụng giao diện song song. Thư viện mới cần tương thích với stack, không làm tăng chi phí render của hàng loạt thanh lịch và phải được ghi rõ trong báo cáo.
- Không áp dụng một palette nhận diện hoặc mẫu tham chiếu chưa được người dùng duyệt.
- Nếu phát hiện xung đột giữa phương án được duyệt và ràng buộc kỹ thuật, dừng ở điểm xung đột và hỏi lại trước khi thực hiện thay đổi khó hoàn tác.

# 9. Tiêu chí nghiệm thu

Công việc triển khai sau này chỉ được coi là hoàn thành khi:

- Người dùng đã duyệt một trong hai hướng thiết kế và đã xác nhận các câu hỏi `[CẦN CHỐT: ...]` trước khi Agent sửa UI.
- Màn chọn vai trò, topbar/sidebar, toàn bộ trang đang được dùng, thành phần chung, dropdown, dialog/drawer và các trạng thái rỗng/loading/lỗi có cùng ngôn ngữ Liquid Glass theo phương án duyệt, ở light mode.
- Các thanh/thẻ buổi học trên lưới lịch không còn là mảng màu đặc như ảnh ví dụ cần tránh: màu gốc còn rõ ở viền, chuyển dần vào vùng tâm sáng/trong hơn, có thể thấy nền hoặc đường lưới phía sau ở mức nhẹ; thanh rất hẹp vẫn nhận biết được màu và trạng thái. Hiệu ứng phải hiện đúng cả khi nhiều thanh đứng cạnh nhau, hover/highlight/dim và ở chế độ chi tiết.
- Lưới lịch, heatmap và bảng Excel vẫn đọc rõ: màu ngữ nghĩa không bị lẫn, sticky đúng vị trí, dữ liệu không bị phủ mờ quá mức, kéo-thả/scroll/fullscreen hoạt động như trước.
- Luồng staff/viewer, sidebar thu gọn/drawer mobile, xác nhận và các thao tác API frontend vẫn giữ nguyên hành vi; không đổi backend, dữ liệu hoặc nghiệp vụ.
- Kiểm tra trực quan trên Microsoft Edge ở desktop và màn hình nhỏ cho bố cục thường, trạng thái phủ dialog/drawer, hover/focus và nội dung dài; không có vùng che nhau/tràn bất thường.
- Có trạng thái focus rõ khi dùng bàn phím; văn bản và trạng thái đủ tương phản trên nền thực; reduced-motion loại bỏ/giảm chuyển động không cần thiết; khi blur không hỗ trợ vẫn có nền đủ dễ đọc.
- Chuyển động không làm giật đáng kể ở lưới/bảng hoặc cản tương tác; không sử dụng hiệu ứng liên tục hàng loạt trên các ô dữ liệu.
- Các test frontend liên quan vượt qua và `npm run build` hoàn tất trong `frontend/`; chạy `npm test` khi có `config/frontend.json` hợp lệ. Nếu cấu hình hoặc dữ liệu thử thiếu, báo rõ giới hạn kiểm tra thay vì tự tạo cấu hình tùy đoán.
- Agent liệt kê file thay đổi, quyết định thiết kế, kết quả kiểm tra thủ công/tự động và các điểm chưa hoàn thành nếu có.

# 10. Cách AI Agent phản hồi

Trước khi viết code, hãy cung cấp:

1. Danh sách bề mặt giao diện và file/liên kết CSS chính đã khảo sát.
2. Rủi ro của lưới lịch, heatmap, bảng Excel, sticky, z-index, dark mode và cascade layer.
3. HAI hướng Liquid Glass cụ thể để người dùng so sánh, kèm trade-off về nhận diện, khả năng đọc và hiệu năng trên Microsoft Edge.
4. Các câu hỏi `[CẦN CHỐT: ...]` và lời đề nghị người dùng chọn phương án; DỪNG chờ câu trả lời.

Sau khi người dùng duyệt và việc triển khai hoàn tất, hãy cung cấp:

1. Tóm tắt thay đổi và đối chiếu với phương án đã duyệt.
2. Danh sách file đã chỉnh sửa và những khu vực cố ý không phủ glass.
3. Các quyết định kỹ thuật về token, fallback, animation và dependency (nếu có).
4. Kết quả `npm test`, `npm run build` và kiểm tra thủ công trên Microsoft Edge; nêu rõ phần nào chưa kiểm được.
5. Giới hạn hoặc vấn đề còn tồn tại.
```

## Lịch sử cập nhật

| Ngày | Nội dung |
|---|---|
| 2026-09-24 | Tạo prompt giao Agent thiết kế Liquid Glass cho toàn frontend; giữ cổng duyệt hướng visual và các câu hỏi nhận diện/tham chiếu chưa chốt |
| 2026-09-24 | Cho phép thư viện hỗ trợ trong stack hiện có; bổ sung hiệu ứng màu ở viền nhạt dần vào tâm, xuyên thấu nhẹ cho các thanh lịch và xác định ảnh lưới màu đặc là ví dụ cần tránh |
