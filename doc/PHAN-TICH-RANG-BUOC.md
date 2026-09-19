# Phân tích các quy tắc xếp thời khóa biểu VJU-Calendar

> **Lưu ý quan trọng:** File câu hỏi có vài điểm không còn khớp với mã nguồn hiện tại. Cụ thể, trùng giờ sinh viên hiện là điều hệ thống **cố tránh** chứ chưa cấm tuyệt đối; hệ thống mới quản lý **số lượng phòng theo loại**, chưa gán phòng cụ thể hay kiểm tra sức chứa từng phòng. Phần trả lời dưới đây ưu tiên mô tả đúng hệ thống hiện tại.

## Phần 1 — Bức tranh lớn

### Bài toán đang giải là gì?

Nói đơn giản, hệ thống phải tìm giờ học phù hợp cho hàng trăm lớp sao cho giảng viên, sinh viên và phòng học không “đụng nhau”, đồng thời lịch tạo ra càng thuận tiện càng tốt.

### Ba vai trò sử dụng hệ thống

1. **Giám đốc Chương trình**

   Người này xác định chương trình của mình cần mở những môn và bao nhiêu lớp, sau đó mời giảng viên thỉnh giảng. Nếu được, họ chốt luôn những khung giờ mà giảng viên có thể dạy.

2. **Chuyên viên Giáo vụ Khoa**

   Giáo vụ nhận thông tin từ nhiều chương trình trong khoa, bổ sung giờ rảnh còn thiếu của giảng viên và xếp lịch theo thời gian. Đây là người trực tiếp kiểm tra, kéo thả và chỉnh lại lịch khi cần.

3. **Chuyên viên Phòng Đào tạo**

   Phòng Đào tạo quản lý phòng học của toàn trường. Sau khi các khoa đã có lịch theo giờ, Phòng Đào tạo gán phòng cụ thể, kiểm tra loại phòng, sức chứa và tránh để nhiều khoa dùng cùng một phòng.

### Vì sao không thể tiếp tục xếp hoàn toàn bằng tay?

- Có hàng trăm lớp nhưng mỗi lớp lại liên quan đến giảng viên, nhóm sinh viên, loại phòng, cơ sở, số tiết và giờ rảnh khác nhau. Chỉ cần đổi một lớp có thể kéo theo nhiều lớp khác phải đổi.
- Phòng học được nhiều chương trình và nhiều khoa dùng chung. Một khoa tự xếp riêng có thể thấy lịch của mình ổn, nhưng khi ghép với khoa khác lại trùng giảng viên hoặc vượt số phòng đang có.

## Phần 2 — Những điều bắt buộc phải tuân thủ

### 1. Một giảng viên không thể đứng hai lớp cùng lúc

- **Nghĩa:** Mỗi giảng viên, kể cả người đồng giảng, chỉ được xuất hiện trong một buổi học tại một thời điểm.
- **Ví dụ:** Thầy Nam không thể dạy “Lập trình Python” và “Cơ sở dữ liệu” cùng vào thứ Ba, tiết 2–4.
- **Nếu vi phạm:** Thầy Nam không thể có mặt ở cả hai lớp, nên một lớp phải chuyển giờ hoặc không được xếp.
- **Ghi chú:** Với lớp có nhiều giảng viên, lịch phải tránh giờ bận của tất cả những người tham gia.

### 2. Không được dùng nhiều phòng hơn số phòng hiện có

- **Nghĩa:** Hệ thống đếm riêng số lớp Lý thuyết và số lớp Thực hành đang diễn ra cùng lúc. Số lớp mỗi loại không được vượt quá số phòng loại đó.
- **Ví dụ:** Nếu trường có 5 phòng thực hành thì cùng một thời điểm chỉ được có tối đa 5 buổi thực hành.
- **Nếu vi phạm:** Ít nhất một lớp sẽ không có phòng để học và phải chuyển giờ hoặc chưa được xếp.
- **Điểm cần hiểu đúng:** Hệ thống hiện chưa gán tên phòng như `P.401` hay `LAB-2`; nó mới giữ chỗ theo tổng số phòng Lý thuyết và Thực hành.

### 3. Phòng phải đủ chỗ cho sinh viên — yêu cầu nghiệp vụ nhưng chưa được xử lý trong phần xếp giờ hiện tại

- **Nghĩa:** Khi gán phòng cụ thể, số ghế của phòng phải lớn hơn hoặc bằng số sinh viên dự kiến.
- **Ví dụ:** Lớp “Kinh tế học” có 65 sinh viên không thể được đưa vào phòng `P.201` chỉ có 40 chỗ.
- **Nếu vi phạm:** Sinh viên không đủ chỗ ngồi, nên Phòng Đào tạo phải đổi sang phòng lớn hơn.
- **Tình trạng hiện tại:** Mã xếp lịch đang đọc số lượng sinh viên nhưng chưa dùng con số đó để chọn phòng. Việc kiểm tra này thuộc bước gán phòng cụ thể của Phòng Đào tạo.

### 4. Sinh viên cùng chương trình và cùng khóa không nên học hai môn cùng lúc

- **Nghĩa:** “FTH khóa VJU2024” được coi là một nhóm sinh viên. Hai môn dành cho nhóm này nên được xếp khác giờ.
- **Ví dụ:** Nếu FTH/VJU2024 học “Quản trị du lịch” vào thứ Tư tiết 2–4 thì không nên xếp “Marketing căn bản” của chính nhóm đó vào cùng giờ.
- **Nếu vi phạm:** Sinh viên phải chọn bỏ một trong hai môn.
- **Tình trạng thực tế:** Đây **không còn là luật cấm tuyệt đối** trong mã hiện tại. Dữ liệu thật đã có sẵn 25 cặp lớp trùng giờ; nếu cấm tuyệt đối, cả lần xếp có thể thất bại. Vì vậy hệ thống ưu tiên rất cao việc tránh trùng nhưng vẫn chấp nhận trong trường hợp không còn cách khác.
- **Ngoại lệ:** Hai lớp học chung, hai lớp song song của cùng một học phần và lớp trực tuyến linh động không bị coi là trùng sai.

### 5. Giới hạn ngày dạy theo loại giảng viên

- **Nghĩa:** Khi hệ thống tự chọn giờ, giảng viên thỉnh giảng được xếp từ thứ Hai đến thứ Bảy; giảng viên cơ hữu chỉ từ thứ Hai đến thứ Sáu. Hệ thống không tự xếp ai vào Chủ nhật.
- **Ví dụ:** Cô Lan là giảng viên cơ hữu nên hệ thống không tự đưa lớp của cô sang thứ Bảy.
- **Nếu vi phạm:** Lịch đi ngược quy định ngày làm việc của từng loại giảng viên.
- **Ngoại lệ có chủ ý:** Giờ đã được con người chốt trong file vẫn được giữ, kể cả có lớp cơ hữu vào thứ Bảy hoặc Chủ nhật. Hệ thống không tự ý xóa một thỏa thuận đã có.

### 6. Buổi học phải nằm gọn trong một khối ca

- **Nghĩa:** Hệ thống không được xếp một buổi bắt đầu trước giờ nghỉ trưa nhưng kết thúc sau giờ nghỉ trưa.
- **Hòa Lạc:** Khối sáng là tiết **2–5**; khối còn lại là tiết **6–13**. Tiết 1 không được dùng khi hệ thống tự chọn giờ.
- **Mỹ Đình:** Khối sáng là tiết **1–5**; khối còn lại là tiết **6–13**.
- **Ví dụ:** Lớp 3 tiết ở Hòa Lạc có thể học tiết 2–4 hoặc 6–8, nhưng không thể học tiết 4–6 vì buổi đó vắt qua giờ nghỉ trưa.
- **Nếu vi phạm:** Giảng viên và sinh viên không có giờ nghỉ trưa đầy đủ.
- **Lưu ý:** Cả hai cơ sở đều cho phép buổi học đi xuyên từ tiết 9 sang tiết 10; không có ranh giới bắt buộc giữa “chiều” và “tối”.

### 7. Nhóm “học chung” phải được xử lý như một buổi duy nhất

- **Nghĩa:** Nhiều mã môn có thể chỉ là cách ghi khác nhau cho một buổi học vật lý. Các dòng đó phải cùng giờ và cùng được xếp hoặc cùng không được xếp.
- **Ví dụ:** `ECE3083` và `BCE3023` có thể là hai mã môn nhưng sinh viên ngồi chung một phòng, học cùng một buổi.
- **Nếu vi phạm:** Một buổi thật bị tách thành hai lịch khác nhau hoặc bị tính thành hai phòng.
- **Cách hệ thống xử lý:** Nhóm chỉ chiếm một suất phòng. Tất cả giảng viên được ghi trong nhóm đều được coi là có mặt tại buổi đó, nên không ai được dạy lớp khác cùng giờ.
- **Giới hạn:** Vì hệ thống chưa gán tên phòng cụ thể, “cùng phòng” hiện mới có nghĩa là cả nhóm chỉ chiếm **một suất phòng**, chưa phải cùng một mã phòng cụ thể.

## Phần 3 — Những điều hệ thống cố gắng làm tốt

### 1. Tránh để một giảng viên dạy ở hai cơ sở trong cùng ngày

- **Nghĩa:** Một giảng viên nên chỉ dạy tại Hòa Lạc hoặc Mỹ Đình trong một ngày.
- **Ví dụ:** Nếu thầy Minh đã dạy tại Hòa Lạc sáng thứ Ba thì hệ thống sẽ cố không xếp thầy ở Mỹ Đình chiều thứ Ba.
- **Nếu vi phạm:** Thầy phải di chuyển quãng đường xa trong cùng ngày, có nguy cơ không kịp giờ.
- **Vì sao không cấm tuyệt đối:** Dữ liệu thật đã có những giờ được chốt sẵn vi phạm điều này. Nếu cấm tuyệt đối, toàn bộ lần xếp có thể không cho ra kết quả.

### 2. Giảm số ngày giảng viên phải đi đến từng cơ sở

- **Nghĩa:** Các buổi ở cùng một cơ sở nên được gom vào ít ngày nhất có thể.
- **Ví dụ:** Cô Hoa có ba lớp tại Hòa Lạc. Xếp cả ba vào thứ Ba và thứ Năm tốt hơn việc bắt cô đi Hòa Lạc vào thứ Ba, thứ Tư và thứ Sáu.
- **Nếu vi phạm:** Giảng viên phải thực hiện nhiều chuyến đi chỉ để dạy một hoặc hai tiết.
- **Vì sao không cấm tuyệt đối:** Giờ rảnh của giảng viên, trùng sinh viên và số phòng có thể khiến việc gom lịch không thực hiện được.
- **Thứ tự:** Hệ thống ưu tiên giảm chuyến đi Hòa Lạc trước vì xa hơn, sau đó mới đến Mỹ Đình.

### 3. Dàn đều số buổi học trong tuần

- **Nghĩa:** Hệ thống cố tránh dồn quá nhiều lớp vào một ngày.
- **Ví dụ:** Có 15 buổi thì phân bổ khoảng 3 buổi mỗi ngày thường tốt hơn xếp 10 buổi vào thứ Hai và để thứ Năm gần như trống.
- **Nếu vi phạm:** Một ngày trở nên quá tải trong khi những ngày khác lại ít lớp.
- **Vì sao không cấm tuyệt đối:** Giảng viên thỉnh giảng có thể chỉ rảnh một hoặc hai ngày. Khi đó đáp ứng giờ của họ quan trọng hơn việc làm lịch trông cân đối.

### 4. Tránh trùng giờ sinh viên

Đây cũng là một ưu tiên mềm trong phiên bản hiện tại. Tuy không cấm tuyệt đối, nó đứng rất cao trong bảng ưu tiên vì lịch bắt sinh viên học hai nơi cùng lúc gần như không sử dụng được.

## Phần 4 — Thứ tự ưu tiên của hệ thống

Khi không thể có một lịch hoàn hảo, hệ thống lựa chọn theo thứ tự sau:

### 1. Xếp được nhiều buổi nhất

Một buổi được xếp vẫn quan trọng hơn việc làm phần còn lại của lịch đẹp hơn. Hệ thống không bỏ một lớp chỉ để giảm số chuyến đi hoặc làm lịch đều hơn.

Khi xếp riêng một chương trình, những lớp của chương trình khác đã có giờ còn được ưu tiên giữ lại đặc biệt, tránh việc hệ thống “hy sinh” lịch cũ để nhường chỗ cho lịch mới.

### 2. Ít trùng giờ sinh viên nhất

Nếu hai phương án xếp được số lớp bằng nhau, hệ thống chọn phương án khiến ít nhóm sinh viên phải học hai môn cùng lúc hơn.

Lý do là sinh viên không thể có mặt ở hai lớp. Đây là vấn đề làm lịch gần như không dùng được, không chỉ là bất tiện.

### 3. Ít trường hợp một giảng viên phải dạy ở hai cơ sở trong một ngày nhất

Nếu mức trùng sinh viên bằng nhau, hệ thống tiếp tục chọn lịch có ít ngày buộc giảng viên chạy giữa Hòa Lạc và Mỹ Đình hơn.

### 4. Ít chuyến đi cho giảng viên nhất

Hệ thống cố gom những buổi ở cùng cơ sở vào cùng ngày. Việc giảm số ngày phải đến Hòa Lạc được ưu tiên trước việc giảm số ngày đến Mỹ Đình.

### 5. Dàn đều buổi học trong tuần

Cuối cùng, nếu các phương án phía trên ngang nhau, hệ thống chọn lịch có ngày bận nhất nhẹ hơn. Nói cách khác, đây là tiêu chí dùng để phân thắng thua giữa những lịch vốn đã tốt gần như nhau.

## Phần 5 — Vì sao phải xếp thành hai giai đoạn?

### Giai đoạn 1: Xếp lớp có giảng viên thỉnh giảng

Giảng viên thỉnh giảng thường làm việc ở đơn vị khác và chỉ có một số khung giờ rảnh cố định. Ví dụ, thầy Tuấn chỉ có thể đến trường vào chiều thứ Tư; nếu khung đó bị lớp cơ hữu chiếm trước thì gần như không còn cách xếp lớp của thầy.

Vì vậy, hệ thống dành chỗ cho những lớp khó di chuyển này trước. Trước khi xếp, hệ thống còn kiểm tra xem giờ do các chương trình khai báo cho cùng một giảng viên có thể cùng tồn tại hay không.

### Giai đoạn 2: Xếp lớp có giảng viên cơ hữu

Giảng viên cơ hữu thường có nhiều lựa chọn hơn trong tuần. Hệ thống đưa các lớp này vào những chỗ còn lại sau khi đã biết lịch của giảng viên thỉnh giảng.

Kết quả giai đoạn 1 phải được giữ nguyên vì đó thường là giờ đã thống nhất với người ngoài trường. Nếu giai đoạn 2 tự ý đổi lại, toàn bộ ý nghĩa của việc ưu tiên giảng viên thỉnh giảng sẽ mất đi. Các buổi giai đoạn 1 vẫn tiếp tục chiếm giờ của giảng viên và một suất phòng khi xếp giai đoạn 2.

## Phần 6 — Những bẫy người mới thường hiểu nhầm

### Bẫy 1: Cắt danh sách chỉ còn chương trình đang xếp

- **Tưởng:** Muốn xếp riêng FTH thì chỉ cần lấy các lớp FTH đưa vào tính toán.
- **Thực ra:** Phải giữ toàn bộ lớp để còn thấy giờ bận của giảng viên, sinh viên và phòng từ các chương trình khác. Nếu cắt danh sách, lịch FTH có thể đè lên một lớp BCSE đang tồn tại.

### Bẫy 2: Ghim tuyệt đối mọi lớp đã có giờ

- **Tưởng:** Lớp đã có giờ thì cứ khóa tuyệt đối, như vậy chắc chắn không bị đổi.
- **Thực ra:** File thật có thể chứa hai dòng cùng giảng viên và cùng giờ. Nếu khóa tuyệt đối cả hai, hệ thống có thể không xếp được gì; cách hiện tại cho phép bỏ một lớp có lỗi và báo rõ tên lớp đó.

### Bẫy 3: Coi quy tắc hai cơ sở là luật cấm tuyệt đối

- **Tưởng:** Chỉ cần cấm giảng viên xuất hiện ở Hòa Lạc và Mỹ Đình trong cùng ngày.
- **Thực ra:** Dữ liệu đã chốt có sẵn trường hợp vi phạm. Hệ thống chỉ cố giảm các trường hợp này để vẫn giữ được lịch đã thỏa thuận.

### Bẫy 4: Coi “học chung” là hai lớp tình cờ học cùng giờ

- **Tưởng:** Hai lớp độc lập được phép trùng giờ nếu người dùng đánh dấu học chung.
- **Thực ra:** Đó là một buổi học thật được ghi thành nhiều mã môn. Cả nhóm phải di chuyển cùng nhau và chỉ chiếm một suất phòng.

### Bẫy 5: Xếp riêng chương trình nghĩa là chương trình đó hoàn toàn độc lập

- **Tưởng:** Xếp FTH xong rồi xếp BCSE sẽ không có liên hệ gì giữa hai lần.
- **Thực ra:** Các lớp đã xếp trước phải được giữ nguyên trong lần sau. Lớp có ô ghép như `FTH.ESAS` lại thuộc cả hai chương trình, nên chương trình xếp sau vẫn có thể được quyền thay đổi nó.

### Bẫy 6: Hệ thống đã chọn được phòng cụ thể và kiểm tra sức chứa

- **Tưởng:** Khi lịch hiện “phòng Lý thuyết”, nghĩa là hệ thống đã tìm được một phòng đủ ghế.
- **Thực ra:** Hiện tại hệ thống mới kiểm tra tổng số suất phòng Lý thuyết và Thực hành. Việc gán `P.401`, `LAB-2` và kiểm tra số ghế vẫn là bước nghiệp vụ riêng của Phòng Đào tạo.

## Tóm tắt trong 3 câu

VJU-Calendar phải xếp hàng trăm buổi học mà không làm giảng viên trùng giờ, không vượt số phòng và cố tránh để sinh viên học hai nơi cùng lúc. Hệ thống xếp giảng viên thỉnh giảng trước, sau đó đưa lớp cơ hữu vào chỗ còn lại, đồng thời ưu tiên giữ lịch đã được con người chốt. Khi không thể làm mọi thứ hoàn hảo, thứ tự quan trọng là: xếp được nhiều lớp, tránh trùng sinh viên, tránh hai cơ sở trong một ngày, giảm chuyến đi, rồi mới dàn đều lịch.
