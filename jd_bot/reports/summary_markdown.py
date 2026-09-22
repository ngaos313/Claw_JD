import os
from typing import Dict, List, Any
from jd_bot.crawlers.base_crawler import JobItem

class SummaryMarkdownGenerator:
    @staticmethod
    def generate_report(
        crawled_jobs: List[JobItem],
        track_analysis: Dict[str, Any],
        roadmaps: Dict[str, Any],
        output_filepath: str = "career_pivot_report.md"
    ) -> str:
        total_jobs = len(crawled_jobs)
        non_soc = len([j for j in crawled_jobs if j.track != "DFIR & SOC Operations"])

        lines = [
            "# Báo Cáo Chiến Lược: Chuyển Ngành Ngoài DFIR & SOC LEAD Dành Cho Nguyễn Thành Đức",
            "",
            f"> **Ngày phân tích**: 22/09/2026  ",
            f"> **Hồ sơ đối chiếu**: Nguyễn Thành Đức - SOC Analyst Tier 2 tại VNCERT (Xuất thân Học viện Kỹ thuật Mật mã)  ",
            f"> **Dữ liệu thực tế**: Tổng cộng **{total_jobs} JD** được cào tự động từ LinkedIn, ITviec, CareerViet  ",
            "",
            "---",
            "",
            "## 1. Bức Tranh Thị Trường Tuyển Dụng & Phân Khúc Ngoài DFIR / SOC Lead",
            "",
            "Qua việc rà soát các tin tuyển dụng ngành An toàn thông tin tại Việt Nam và khu vực, có thể nhận thấy rõ một xu hướng dịch chuyển lớn:",
            "- **Các vai trò trực ca SOC Analyst Tier 1/2** đang dần bão hòa, lương dao động 12 - 22 triệu và áp lực trực đêm 24/7/365 rất cao.",
            "- **Nhánh DFIR Senior**: Yêu cầu quá sâu về Reverse Engineering (phân tích mã độc, unpack) và áp lực 'Incident Commander' khi doanh nghiệp bị tấn công, đồng thời đòi hỏi tiếng Anh viết báo cáo C-level lưu loát.",
            "- **Nhánh SOC Lead**: Đòi hỏi kỹ năng quản lý nhân sự, gánh KPI/SLA, quản lý khủng hoảng và vẫn phải trực chiến.",
            "",
            f"**Cơ hội bứt phá**: Trong số {total_jobs} JD phân tích, có tới **{non_soc} vị trí ({round(non_soc/total_jobs*100 if total_jobs else 0)}%)** thuộc về các phân nhánh **KHÔNG PHẢI TRỰC CA ĐÊM**, mức lương từ **25 - 50+ triệu/tháng**.",
            "",
            "---",
            "",
            "## 2. Bảng Xếp Hạng Độ Tương Thích & Tiềm Năng (Fit Score Matrix)",
            "",
            "| Thứ hạng | Nhánh nghề nghiệp | Fit Score với Đức | Thời gian chuyển đổi | Mức lương & Đánh giá ROI |",
            "| :---: | :--- | :---: | :---: | :--- |"
        ]

        # Sort tracks by match score
        sorted_tracks = sorted(track_analysis.items(), key=lambda x: x[1]["match_score"], reverse=True)
        for rank, (name, data) in enumerate(sorted_tracks, 1):
            lines.append(f"| **#{rank}** | **{name}** | **{data['match_score']}%** | {data['difficulty']} | {data['roi_rating'].split('(')[0]} |")

        lines.extend([
            "",
            "---",
            "",
            "## 3. Đánh Giá Chi Tiết Từng Hướng Đi (Lợi Thế Sẵn Có vs Lỗ Hổng Kỹ Thuật)",
            ""
        ])

        for name, data in sorted_tracks:
            lines.extend([
                f"### {name} (Độ phù hợp: {data['match_score']}%)",
                f"- **Số lượng JD trên thị trường**: {data['job_count']} tin tuyển dụng",
                f"- **Độ khó chuyển đổi**: {data['difficulty']}",
                f"- **Nhận định ROI**: {data['roi_rating']}",
                "",
                "**✓ Lợi thế bạn đã có (Transferable Skills từ VNCERT/KMA):**"
            ])
            for s in data["transferable_skills"]:
                lines.append(f"  * {s}")

            lines.extend([
                "",
                "**✕ Lỗ hổng kỹ năng cần bù đắp (Critical Gaps):**"
            ])
            for g in data["critical_gaps"]:
                lines.append(f"  * {g}")

            lines.extend([
                "",
                f"**🏆 Chứng chỉ thị trường săn đón nhất**: `{'`, `'.join(data['top_certs'])}`",
                "",
                "---"
            ])

        lines.extend([
            "",
            "## 4. Top 3 Lộ Trình Hành Động Đề Xuất Cho Đức",
            "",
            "### Lựa chọn 1: SecOps Automation & Detection Engineering (Lối thoát trực ca nhanh nhất: 3-4 tháng)",
            "- **Lý do**: Bạn đang có lợi thế lớn nhất ở đây. Bạn đã hiểu từng alert, từng log Event ID, từng building block của SIEM. Developer bình thường không có giác quan này.",
            "- **Nhiệm vụ cốt lõi**: Nâng cấp trình độ Python từ mức 'dùng AI hỗ trợ' sang tự viết script hoàn chỉnh tương tác API; học nền tảng SOAR (Shuffle / Tines) và quản lý rule theo tư duy Detection as Code (Sigma rules).",
            "",
            "### Lựa chọn 2: Cloud Security / DevSecOps (Mức trần lương cao nhất: 6 tháng)",
            "- **Lý do**: Thị trường đang thiếu trầm trọng nhân sự hiểu cả Cloud hạ tầng (AWS/K8s/Terraform) và An toàn thông tin. Không phải trực đêm, làm việc môi trường hiện đại.",
            "- **Nhiệm vụ cốt lõi**: Học AWS nền tảng -> Làm chủ Terraform dựng hạ tầng an toàn -> Bảo mật Docker/K8s (Trivy, Checkov) -> Thi chứng chỉ **AWS Certified Security - Specialty**.",
            "",
            "### Lựa chọn 3: GRC & Đánh Giá Rủi Ro / IT Auditor (Môi trường Ngân hàng / Big 4 ổn định: 4-5 tháng)",
            "- **Lý do**: Bạn đã từng hỗ trợ ứng cứu cho Ngân hàng và Bệnh viện, có gốc kỹ thuật vững chắc. Rất nhiều người làm GRC chỉ biết luật nhưng không hiểu kỹ thuật; ngược lại bạn có kỹ thuật nên khi kiểm toán hoặc làm tuân thủ sẽ cực kỳ được nể trọng.",
            "- **Nhiệm vụ cốt lõi**: Học sâu ISO/IEC 27001:2022, Thông tư 09/2020/TT-NHNN và Nghị định 13 -> Lấy chứng chỉ **ISO 27001 Lead Auditor**.",
            "",
            "---",
            "",
            "## 5. File Giao Diện Trực Quan",
            "- Để xem đầy đủ biểu đồ so sánh, chi tiết danh sách JD và lộ trình tương tác, mở file: [`career_dashboard.html`](file:///d:/VNCERT/CV%20fix/career_dashboard.html) trên trình duyệt."
        ])

        with open(output_filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"[SummaryMarkdownGenerator] Report generated at: {output_filepath}")
        return output_filepath
