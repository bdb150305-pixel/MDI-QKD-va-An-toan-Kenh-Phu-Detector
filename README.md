# MDI-QKD và An toàn kênh phụ của Detector

## 1. Giới thiệu đề tài

Đề tài nghiên cứu **Phân phối khóa lượng tử độc lập với thiết bị đo** (*Measurement-Device-Independent Quantum Key Distribution – MDI-QKD*) và vấn đề an toàn trước các cuộc tấn công kênh phụ nhắm vào detector.

Trong kiến trúc MDI-QKD, Alice và Bob gửi các trạng thái lượng tử đến Charlie để thực hiện phép đo trạng thái Bell (*Bell-State Measurement – BSM*). Charlie được xem là trạm đo không cần tin cậy. Thiết kế này giúp loại bỏ các lỗ hổng bảo mật xuất phát từ thiết bị đo trong phạm vi các giả định của giao thức MDI-QKD.

Đề tài sử dụng Python để xây dựng mô hình Monte Carlo ở mức hệ thống, khảo sát ảnh hưởng của suy hao sợi quang, hiệu suất detector và xác suất dark count đến các chỉ số mô phỏng.



## 3. Mục tiêu

- Tìm hiểu nguyên lý hoạt động của giao thức MDI-QKD.
- Mô tả kiến trúc Alice–Charlie–Bob và vai trò của phép đo trạng thái Bell.
- Khảo sát ảnh hưởng của suy hao kênh quang và hiệu suất detector.
- Khảo sát ảnh hưởng của dark count đến QBER và chỉ số tốc độ khóa mô phỏng.
- Phân tích vai trò của MDI-QKD trong việc giảm thiểu rủi ro từ các cuộc tấn công kênh phụ nhắm vào thiết bị đo.
- Xuất dữ liệu CSV và biểu đồ PNG phục vụ báo cáo, phân tích và thuyết trình.

## 4. Kiến trúc hệ thống

- **Alice:** tạo bit ngẫu nhiên và lựa chọn cơ sở.
- **Bob:** tạo bit tương quan trong mô hình nguyên mẫu và lựa chọn cơ sở.
- **Charlie:** mô phỏng trạm đo không cần tin cậy, thực hiện bước BSM đơn giản hóa.
- **Kênh quang:** mô phỏng suy hao sợi quang theo khoảng cách.
- **Detector:** mô phỏng hiệu suất phát hiện và xác suất dark count.

Quy trình mô phỏng gồm tạo bit và cơ sở, mô phỏng phát hiện, xác định sự kiện BSM, sifting các lượt cùng cơ sở, tính QBER và tính chỉ số key rate proxy.

## 5. Công nghệ sử dụng

- Python
- NumPy
- Pandas
- Matplotlib
- Visual Studio Code
- Anaconda
- Git và GitHub

## 6. Cấu trúc thư mục

```text
LTMM/
├── mdi_qkd_simulation.py
├── README.md
├── requirements.txt
├── .gitignore
└── results/
    ├── mdiqkd_distance_results.csv
    ├── mdiqkd_detector_efficiency_results.csv
    ├── mdiqkd_dark_count_results.csv
    ├── qber_vs_distance.png
    ├── key_rate_proxy_vs_distance.png
    ├── qber_vs_dark_count.png
    ├── key_rate_proxy_vs_dark_count.png
    └── key_rate_proxy_vs_detector_efficiency.png
```

Tên file kết quả thực tế có thể khác tùy phiên bản chương trình đang sử dụng.

## 7. Cài đặt môi trường

Yêu cầu Python 3 và các thư viện NumPy, Pandas, Matplotlib.

Cài đặt các thư viện bằng lệnh:

```bash
python -m pip install -r requirements.txt
```

Nếu sử dụng Anaconda trên Windows, có thể chạy chương trình bằng đường dẫn Python của môi trường đã cài đặt.

## 8. Cách chạy chương trình

Mở Terminal tại thư mục dự án và chạy:

```bash
python mdi_qkd_simulation.py
```

Chương trình sẽ thực hiện lần lượt:
1. Khảo sát theo khoảng cách Alice–Bob.
2. Khảo sát theo hiệu suất detector.
3. Khảo sát theo xác suất dark count.
4. Lưu dữ liệu CSV và biểu đồ PNG vào thư mục `results/`.
5. In các bảng kết quả chính ra Terminal.

Thư mục `results/` được xác định tương đối theo vị trí file Python, do đó kết quả sẽ được lưu cạnh chương trình thay vì phụ thuộc vào thư mục làm việc hiện tại.

## 9. Các tham số mô phỏng chính

| Tham số | Giá trị mặc định hoặc phạm vi |
|---|---|
| Số vòng Monte Carlo | 500.000 |
| Suy hao sợi quang | 0,20 dB/km |
| Hiệu suất detector mặc định | 85% |
| Xác suất dark count mặc định | 10⁻⁶ |
| Xác suất BSM thành công trong mô hình | 50% |
| Lỗi nội tại | 1% |
| Hệ số hiệu chỉnh lỗi | 1,16 |
| Khoảng cách khảo sát | 0–50 km, bước 5 km |
| Seed ngẫu nhiên | 20261008 |

Các tham số có thể được điều chỉnh trong phần cấu hình của file Python. Những giá trị dùng cho stress test dark count không nhất thiết đại diện cho detector thực tế.

## 10. Chỉ số đầu ra

- **Số sự kiện BSM:** số lượt mà mô hình ghi nhận BSM thành công.
- **Số bit được giữ:** số lượt còn lại sau BSM và sifting.
- **QBER:** tỷ lệ bit lỗi trong số bit được giữ.
- **Tỷ lệ bit được giữ:** số bit được giữ chia cho tổng số vòng mô phỏng.
- **Key rate proxy:** chỉ số tốc độ khóa đơn giản để so sánh xu hướng giữa các cấu hình.

Các kết quả được xuất thành bảng CSV và biểu đồ PNG để thuận tiện cho việc phân tích.

## 11. Giới hạn mô hình và lưu ý về bảo mật

Đây là **mô hình nguyên mẫu Monte Carlo ở mức hệ thống**, không phải mô phỏng quang lượng tử đầy đủ.

Phiên bản hiện tại:
- Sử dụng mô hình đơn giản hóa cho phát hiện và BSM.
- Chưa mô phỏng đầy đủ trạng thái lượng tử, thiết bị quang học và các kết quả đo Bell thực tế.
- Chưa triển khai đầy đủ ước lượng decoy-state.
- Chưa thực hiện chứng minh bảo mật hữu hạn hoặc tính toán khóa bí mật theo một phân tích bảo mật hoàn chỉnh.
- Dùng `key_rate_proxy` để khảo sát xu hướng; chỉ số này **không phải tốc độ khóa bí mật đã được chứng minh an toàn**.

Khi diễn giải kết quả, cần phân biệt xu hướng do mô hình tạo ra với kết luận có thể khẳng định từ lý thuyết bảo mật MDI-QKD. Các giả định, giới hạn và cách xây dựng mô hình cần được nêu rõ trong báo cáo.

## 12. Tài liệu tham khảo

1. H.-K. Lo, M. Curty, and B. Qi, “Measurement-Device-Independent Quantum Key Distribution,” *Physical Review Letters*, 108, 130503 (2012).
2. S. L. Braunstein and S. Pirandola, “Side-Channel-Free Quantum Key Distribution,” *Physical Review Letters*, 108, 130502 (2012).

## 13. Trạng thái dự án

Dự án đang ở giai đoạn mô phỏng nguyên mẫu và khảo sát tham số. Các bước phát triển tiếp theo có thể gồm cải thiện mô hình sự kiện BSM, kiểm tra độ ổn định thống kê bằng nhiều seed độc lập, đối chiếu với các công thức trong tài liệu chuyên ngành và nghiên cứu mô hình decoy-state phù hợp.
