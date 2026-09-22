import re
import time
import random
from bs4 import BeautifulSoup
from typing import List, Optional, Set
from .base_crawler import BaseCrawler, JobItem

try:
    from curl_cffi import requests as cffi_requests
    HAS_CURL_CFFI = True
except ImportError:
    HAS_CURL_CFFI = False

# Strict positive keywords for cybersecurity verification
CYBER_KEYWORDS = [
    "an toàn thông tin", "an ninh mạng", "bảo mật", "an ninh thông tin",
    "cyber", "cybersecurity", "information security", "infosec",
    "soc", "siem", "soar", "incident response", "dfir", "forensic",
    "pentest", "penetration", "red team", "blue team", "ethical hack",
    "lỗ hổng", "appsec", "application security", "cloud security", "devsecops",
    "grc", "iso 27001", "pci-dss", "pci dss", "it audit",
    "security engineer", "security specialist", "security architect",
    "security officer", "security analyst", "security consultant"
]

# Negative exclusion keywords to eliminate unrelated generic IT jobs
EXCLUDE_KEYWORDS = [
    "tester", "qa/qc", "reactjs", "react native", "frontend", "front-end",
    "flutter", "ios developer", "android developer", "php developer",
    "kế toán", "nhân viên kinh doanh", "telesale", "tuyển dụng hr"
]

class TopCVCrawler(BaseCrawler):
    def __init__(self, delay_range=(1.5, 3.0), timeout=15):
        super().__init__(delay_range, timeout)
        self.base_url = "https://www.topcv.vn"

    def fetch_page(self, url: str) -> Optional[str]:
        self.sleep_polite()
        if HAS_CURL_CFFI:
            try:
                res = cffi_requests.get(url, impersonate="chrome124", timeout=self.timeout)
                if res.status_code == 200:
                    return res.text
                print(f"[TopCVCrawler] curl_cffi returned status {res.status_code} for {url}")
            except Exception as e:
                print(f"[TopCVCrawler] curl_cffi error: {e}")

        # Fallback to standard BaseCrawler fetch
        res = self.fetch(url)
        return res.text if res and res.status_code == 200 else None

    def crawl_job_detail(self, job_url: str) -> str:
        text = self.fetch_page(job_url)
        if not text:
            return ""
        soup = BeautifulSoup(text, "html.parser")
        desc_el = soup.select_one("div.box-job-information-detail") or \
                  soup.select_one("div.job-description__item--content") or \
                  soup.select_one("div.job-data")
        if desc_el:
            return desc_el.get_text("\n", strip=True)
        return ""

    def is_cybersecurity_job(self, title: str, tags: List[str] = None) -> bool:
        """Strictly verifies if a job belongs to Cybersecurity / Information Security."""
        content_to_check = title.lower()
        if tags:
            content_to_check += " " + " ".join(t.lower() for t in tags)

        # 1. Must match at least one positive cybersecurity keyword
        has_positive = any(kw in content_to_check for kw in CYBER_KEYWORDS)
        if not has_positive:
            return False

        # 2. Reject if title matches generic exclusion and doesn't explicitly mention security in title
        title_lower = title.lower()
        has_negative = any(ex in title_lower for ex in EXCLUDE_KEYWORDS)
        if has_negative and not any(kw in title_lower for kw in ["security", "bảo mật", "an toàn", "an ninh"]):
            return False

        return True

    def crawl(self, search_queries: List[str] = None, max_jobs: int = 30) -> List[JobItem]:
        if not search_queries:
            search_queries = [
                "tim-viec-lam-an-toan-thong-tin",
                "tim-viec-lam-an-ninh-mang",
                "tim-viec-lam-cyber-security",
                "tim-viec-lam-soc-analyst",
                "tim-viec-lam-devsecops"
            ]

        jobs: List[JobItem] = []
        seen_ids: Set[str] = set()

        print(f"[TopCVCrawler] Starting TopCV crawler strictly for Cybersecurity jobs (limit: {max_jobs})...")

        for query in search_queries:
            if len(jobs) >= max_jobs:
                break

            target_url = f"{self.base_url}/{query}" if not query.startswith("http") else query
            print(f"[TopCVCrawler] Fetching: {target_url}")
            html_content = self.fetch_page(target_url)
            if not html_content:
                continue

            soup = BeautifulSoup(html_content, "html.parser")
            cards = soup.select("div.job-item-search-result")
            print(f"  -> Found {len(cards)} raw cards on page")

            for card in cards:
                if len(jobs) >= max_jobs:
                    break

                job_id_raw = card.get("data-job-id")
                if not job_id_raw:
                    continue
                job_id = f"topcv_{job_id_raw}"
                if job_id in seen_ids:
                    continue

                # Title & URL
                title_el = card.select_one("h3.title a")
                if not title_el:
                    continue
                url = title_el.get("href", "").split("?")[0]
                span_title = title_el.select_one("span[data-toggle='tooltip']")
                title = span_title.get("title") or span_title.get("data-original-title") if span_title else title_el.get_text(strip=True)
                title = title.strip()

                # Company
                comp_span = card.select_one("a.company span.company-name")
                company = comp_span.get("title") or comp_span.get("data-original-title") or comp_span.get_text(strip=True) if comp_span else "Doanh nghiệp trên TopCV"
                company = company.strip()

                # Salary
                salary_el = card.select_one("label.title-salary, label.salary, div.info label.salary span")
                salary = salary_el.get_text(strip=True) if salary_el else "Thỏa thuận"

                # Location
                city_span = card.select_one("a.address span.city-text, a.address")
                location = city_span.get_text(strip=True) if city_span else "Việt Nam"

                # Date
                date_el = card.select_one("label.label-update")
                posted_date = ""
                if date_el:
                    posted_date = date_el.get("title") or date_el.get("data-original-title") or date_el.get_text(strip=True)
                    posted_date = posted_date.replace("Cập nhật", "").replace("Đăng", "").strip()

                # Tags / Skills from card
                card_tags = []
                for t_el in card.select("div.tag span.item-tag"):
                    card_tags.append(t_el.get_text(strip=True))
                rem_el = card.select_one("span.remaining-items")
                if rem_el and (rem_el.get("title") or rem_el.get("data-original-title")):
                    extra_tags_str = rem_el.get("title") or rem_el.get("data-original-title")
                    card_tags.extend([t.strip() for t in extra_tags_str.split(",") if t.strip()])

                # STRICT CYBERSECURITY CHECK
                if not self.is_cybersecurity_job(title, card_tags):
                    # Skip unrelated jobs
                    continue

                try:
                    print(f"  [+] [Cybersecurity Matched] {company} | {title} | {salary} | {posted_date}")
                except Exception:
                    print(f"  [+] [Cybersecurity Matched] Job {job_id} | {salary}")

                # Fetch detail description for rich skill extraction
                raw_desc = self.crawl_job_detail(url)
                if not raw_desc or len(raw_desc) < 30:
                    raw_desc = f"{title} tại {company}. Yêu cầu: {', '.join(card_tags)}"

                job_obj = JobItem(
                    id=job_id,
                    title=title,
                    company=company,
                    location=location,
                    url=url,
                    source="TopCV",
                    raw_description=raw_desc,
                    salary=salary,
                    posted_date=posted_date,
                    tags=card_tags[:5]
                )
                jobs.append(job_obj)

        print(f"[TopCVCrawler] Successfully collected {len(jobs)} verified cybersecurity jobs from TopCV!")
        return jobs
