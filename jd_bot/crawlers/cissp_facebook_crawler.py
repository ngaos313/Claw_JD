import os
import csv
from typing import List
from .base_crawler import BaseCrawler, JobItem

class CISSPFacebookCrawler(BaseCrawler):
    def __init__(self, csv_relative_path: str = None):
        super().__init__()
        if not csv_relative_path:
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            candidate_paths = [
                os.path.join(root_dir, "local_private", "fb_crawler", "crawler", "04_du_lieu_hoan_thien", "tin_tuc_tuyen_dung_facebook_chuan_hoa.csv"),
                os.path.join(root_dir, "jd_bot", "data", "tin_tuc_tuyen_dung_facebook_chuan_hoa.csv"),
                os.path.join(root_dir, "crawler", "crawler", "04_du_lieu_hoan_thien", "tin_tuc_tuyen_dung_facebook_chuan_hoa.csv")
            ]
            self.csv_path = candidate_paths[-1]
            for p in candidate_paths:
                if os.path.exists(p):
                    self.csv_path = p
                    break
        else:
            self.csv_path = csv_relative_path

    def crawl(self, max_jobs: int = 150) -> List[JobItem]:
        print(f"[CISSPFacebookCrawler] Loading standardized jobs from: {self.csv_path}")
        if not os.path.exists(self.csv_path):
            print(f"[!] Warning: CISSP CSV not found at {self.csv_path}")
            return []

        jobs = []
        with open(self.csv_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                post_id = row.get("Mã tin (ID)") or f"fb_{len(jobs)}"
                title = row.get("Vị trí tuyển dụng (Job Title)") or row.get("Tiêu đề tin (Title)") or "Chuyên viên ATTT"
                company = row.get("Đơn vị tuyển dụng (Company)") or "Doanh nghiệp (Group CISSP)"
                location = row.get("Địa điểm làm việc (Location)") or "Việt Nam"
                salary = row.get("Mức lương hiển thị (Salary Display)") or "Thỏa thuận"
                role_group = row.get("Nhóm Role chuyên môn (Role Group)") or ""
                skills_certs = row.get("Kỹ năng & Chứng chỉ (Skills & Certs)") or ""
                email = row.get("Email nhận CV (Contact Email)") or ""
                phone = row.get("SĐT / Zalo liên hệ (Contact Phone)") or ""
                date = row.get("Thời điểm đăng tin (Published Date)") or ""
                url = row.get("Link bài gốc (Source URL)") or "https://www.facebook.com/groups/196960460470821/"
                content = row.get("Nội dung chi tiết (Content)") or ""

                # Format description with contact and role metadata
                full_desc = f"{content}\n\n[Thông tin liên hệ]\nEmail: {email}\nSĐT: {phone}\nKỹ năng & Chứng chỉ: {skills_certs}"

                tags = ["CISSP Group"]
                if role_group:
                    tags.append(role_group)
                if email:
                    tags.append(f"Email: {email}")

                job_obj = JobItem(
                    id=f"cissp_fb_{post_id}",
                    title=title.strip(),
                    company=company.strip(),
                    location=location.strip(),
                    url=url.strip(),
                    source="CISSP FB Group",
                    raw_description=full_desc.strip(),
                    salary=salary.strip(),
                    posted_date=date.strip(),
                    tags=tags
                )
                jobs.append(job_obj)

                if len(jobs) >= max_jobs:
                    break

        print(f"[CISSPFacebookCrawler] Loaded {len(jobs)} jobs from CISSP Facebook Group")
        return jobs
