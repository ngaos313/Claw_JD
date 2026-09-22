# 🛡️ Vietnam Cybersecurity Job Aggregator & Market Intelligence

> **Hệ thống tự động thu thập và phân tích dữ liệu tuyển dụng An toàn thông tin (Cybersecurity)** tại thị trường Việt Nam từ **6 nguồn tuyển dụng hàng đầu**, tự động phân loại theo 9 chuyên ngành bảo mật và cập nhật Dashboard trực tiếp lên **GitHub Pages** 24/7 thông qua **GitHub Actions** (không cần mở máy tính).

---

## 🌐 Dashboard Trực Quan & Khám Phá Việc Làm

Dashboard được xuất bản tĩnh tại [`index.html`](index.html), cung cấp:
- **Thống kê thị trường theo thời gian thực**: Tổng số việc làm, phân bổ theo nguồn tuyển dụng, phân bổ theo nhóm chuyên môn (Tracks).
- **Sắp xếp thời gian thông minh (Newest-First)**: Toàn bộ công việc từ 6 nguồn được chuẩn hóa timestamp để sắp xếp từ **gần đây nhất đến xa nhất**, có tùy chọn đảo chiều hoặc lọc theo thứ tự bảng chữ cái.
- **Bộ lọc đa chiều & tìm kiếm tức thì**: Lọc theo Chuyên môn (DFIR, Cloud Sec, SOC, Pentest, GRC...), Nguồn tuyển dụng (LinkedIn, ITviec, CareerViet, VietnamWorks, TopCV, CISSP FB), và tìm kiếm tự do theo từ khóa (kỹ năng, công ty, địa điểm, công nghệ).
- **Cơ chế SizeGuard (< 100MB)**: Tự động giám sát dung lượng file dữ liệu `raw_jds.json`, tự động dọn dẹp các bài đăng cũ nhất khi chạm ngưỡng 100MB để đảm bảo tuân thủ giới hạn file của GitHub và giữ repo luôn mượt mà.
- **Thẻ việc làm chi tiết**: Hiển thị mức lương, địa điểm, ngày đăng chuẩn hóa, yêu cầu kỹ năng, chứng chỉ khuyến nghị và liên kết ứng tuyển trực tiếp.

---

## 🚀 6 Nguồn Tuyển Dụng Được Tích Hợp

| Nguồn | Cơ chế thu thập | Đặc điểm vị trí |
| :--- | :--- | :--- |
| **LinkedIn** | Guest Search API | Tập đoàn đa quốc gia, công nghệ cao, ngân hàng quốc tế |
| **ITviec** | Web Scraping & Semantic Tagging | Tech / Product / Fintech, DevSecOps, AppSec, Cloud |
| **CareerViet** | Search Scraper | Khối Ngân hàng, Doanh nghiệp lớn (MB Bank, Viettel...) |
| **VietnamWorks** | Search API | Khối Doanh nghiệp & IT Services toàn quốc |
| **TopCV** | Scraper & Strict Cyber Filter | Hệ sinh thái tuyển dụng lớn nhất VN (Lọc chuyên sâu ATTT) |
| **CISSP FB Group** | Standardized 32-column Dataset | Tin tuyển dụng từ cộng đồng CISSP (kèm Email, SĐT/Zalo liên hệ) |

---

## 🎯 9 Chuyên Ngành ATTT Được Phân Loại Tự Động

Mỗi JD được hệ thống phân tích ngữ nghĩa và gán vào nhóm ngành tương ứng:
1. **Digital Forensics & Incident Response (DFIR)**: Điều tra số, ứng cứu sự cố, Malware Analysis.
2. **SOC Operations & Monitoring**: Giám sát an ninh, L1/L2/L3 Analyst, Threat Detection.
3. **Cloud Security / DevSecOps**: Bảo mật AWS/Azure/GCP, Kubernetes, CI/CD pipeline, IaC.
4. **Offensive Security (Pentest / Red Team)**: Đánh giá lỗ hổng, kiểm thử xâm nhập, Exploit.
5. **AppSec / Product Security**: Bảo mật ứng dụng, Code Review, OWASP Top 10, SAST/DAST.
6. **GRC & Compliance**: Tuân thủ tiêu chuẩn ISO 27001, PCI-DSS, chính sách ATTT, IT Audit.
7. **Pre-Sales & Solutions Architect**: Tư vấn giải pháp an ninh, kỹ sư cầu nối khách hàng/Vendor.
8. **SecOps Automation**: Tự động hóa SOAR, Python, Playbook, Tines, Shuffle.
9. **An toàn Thông tin Chung**: Quản trị hệ thống bảo mật, IT Security Engineer đa nhiệm.

---

## 📁 Cấu Trúc Thư Mục Repository

```
├── .github/
│   └── workflows/
│       └── auto_crawler_pages.yml      # CI/CD: Chạy tự động mỗi 30 phút trên GitHub Actions & deploy Pages
├── jd_bot/                             # Mã nguồn chính của bot
│   ├── crawlers/                       # 6 Crawler thu thập dữ liệu
│   │   ├── base_crawler.py             # Lớp cơ sở chuẩn hóa JobItem
│   │   ├── linkedin_crawler.py         # Crawler LinkedIn
│   │   ├── itviec_crawler.py           # Crawler ITViec
│   │   ├── careerviet_crawler.py       # Crawler CareerViet
│   │   ├── vietnamworks_crawler.py     # Crawler VietnamWorks
│   │   ├── topcv_crawler.py            # Crawler TopCV (Bộ lọc an ninh mạng)
│   │   └── cissp_facebook_crawler.py   # Parser dữ liệu Facebook CISSP
│   ├── analyzer/                       # Module phân tích JD
│   │   ├── jd_extractor.py             # Trích xuất kỹ năng, phân loại 9 nhóm ngành
│   │   ├── profile_matcher.py          # Ma trận yêu cầu kỹ năng thị trường
│   │   └── cv_parser.py                # Bộ phân tích hồ sơ
│   ├── reports/                        # Module sinh báo cáo & dashboard
│   │   └── dashboard_generator.py      # Bộ sinh giao diện web index.html
│   └── data/
│       ├── raw_jds.json                # Cơ sở dữ liệu JD đã được làm giàu và chuẩn hóa
│       └── tin_tuc_tuyen_dung_facebook_chuan_hoa.csv # Dữ liệu tuyển dụng CISSP
├── index.html                          # Dashboard Web hoàn chỉnh phục vụ GitHub Pages
├── run_bot.py                          # CLI runner điều khiển toàn bộ pipeline
├── requirements.txt                    # Danh sách thư viện Python cần thiết
├── .gitignore                          # Cấu hình bỏ qua file cá nhân & cache
└── README.md                           # Tài liệu hướng dẫn dự án
```

---

## ⚙️ Hướng Dẫn Cài Đặt & Chạy Local

### 1. Cài đặt môi trường
```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
pip install -r requirements.txt
```

### 2. Các câu lệnh thực thi (`run_bot.py`)

- **Chạy toàn bộ quy trình (Cào tin mới + Cập nhật Dashboard)**:
  ```bash
  python run_bot.py --all
  ```
- **Chỉ cào dữ liệu từ các nguồn**:
  ```bash
  python run_bot.py --crawl
  ```
- **Chỉ cào từ một số nguồn chỉ định**:
  ```bash
  python run_bot.py --crawl --sources linkedin,itviec,vietnamworks
  ```
- **Chỉ tái tạo lại file `index.html` từ dữ liệu đã có**:
  ```bash
  python run_bot.py --report
  ```

### 3. Đồng Bộ Dữ Liệu Từ Git Về Local & Phân Tích Lộ Trình CV (1-Click)

Bạn có thể dễ dàng lấy toàn bộ JD mới nhất mà GitHub Actions tự động cào về máy tính, đồng thời đối sánh với CV cá nhân chỉ bằng 1 thao tác:

- **Cách 1 (Nhấp đúp chuột)**: Nhấp đúp vào file [`dong_bo_va_phan_tich_cv.bat`](dong_bo_va_phan_tich_cv.bat) ngay thư mục gốc.
- **Cách 2 (Dòng lệnh CLI)**:
  ```bash
  python run_bot.py --gap --pull
  ```

*Quy trình thực hiện tự động*:
1. `git pull origin main` kéo các JD mới nhất từ GitHub Actions về máy local.
2. Bộ đối sánh phân tích hồ sơ CV của bạn với toàn bộ tin tuyển dụng trong database.
3. Tự động mở báo cáo giao diện trực quan `local_private/reports/private_gap_analysis.html` trên trình duyệt (100% dữ liệu CV và báo cáo cá nhân chỉ lưu tại máy bạn, không đưa lên Git).

---

## 🤖 Tự Động Hóa 24/7 Với GitHub Actions & GitHub Pages

Dự án đã được tích hợp sẵn file cấu hình CI/CD tại [`.github/workflows/auto_crawler_pages.yml`](.github/workflows/auto_crawler_pages.yml):
- **Lập lịch (Cron)**: Chạy định kỳ mỗi **30 phút** một lần (`*/30 * * * *`) - hoàn toàn miễn phí 100% và an toàn cho cả Repo Private lẫn Public.
- **Thực thi**: Tự động cài môi trường Python, chạy `python run_bot.py --all` để cào tin mới từ các nền tảng mở.
- **Tự động Commit**: Tự động commit các file dữ liệu mới và cập nhật `index.html`.
- **Tự động Xuất bản**: Tự động deploy giao diện mới lên **GitHub Pages**.

### Cách kích hoạt GitHub Pages sau khi Push repo:
1. Truy cập repo trên GitHub: **Settings** -> **Pages**.
2. Tại mục **Build and deployment**:
   - **Source**: Chọn `Deploy from a branch`.
   - **Branch**: Chọn `main` (hoặc `master`), thư mục chọn `/ (root)`.
3. Nhấn **Save**. Sau 1-2 phút, trang web sẽ hiển thị tại:  
   `https://<your-username>.github.io/<repo-name>/`

---

## 🔒 Tính Riêng Tư & Bảo Mật

- Repository công khai trên GitHub chỉ chứa **dữ liệu việc làm tổng hợp của thị trường** và giao diện tra cứu việc làm.
- Mọi dữ liệu riêng tư (CV cá nhân, kết quả phân tích khoảng cách kỹ năng cá nhân, phiên làm việc nội bộ) được bảo lưu và quản lý an toàn tại thư mục riêng tư local (được loại trừ hoàn toàn qua `.gitignore`).
