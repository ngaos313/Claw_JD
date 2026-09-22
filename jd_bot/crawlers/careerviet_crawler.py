import re
import urllib.parse
from bs4 import BeautifulSoup
from typing import List, Optional
from .base_crawler import BaseCrawler, JobItem

class CareerVietCrawler(BaseCrawler):
    def __init__(self, delay_range=(1.5, 3.0), timeout=15):
        super().__init__(delay_range, timeout)
        self.base_url = "https://careerviet.vn"

    def crawl_job_detail(self, job_url: str) -> str:
        self.sleep_polite()
        res = self.fetch(job_url)
        if not res:
            return ""
        soup = BeautifulSoup(res.text, "html.parser")
        desc_el = soup.find("div", class_="detail-row") or \
                  soup.find("div", class_="job-detail-content") or \
                  soup.find("div", class_="content-tab") or \
                  soup.find("section", class_="job-detail-content")
        if desc_el:
            return desc_el.get_text("\n", strip=True)
        return ""

    def crawl(self, search_keywords: List[str] = None, max_jobs: int = 30) -> List[JobItem]:
        if not search_keywords:
            search_keywords = ["an-toan-thong-tin", "devsecops", "cloud-security"]

        jobs = []
        seen_ids = set()

        for kw in search_keywords:
            # CareerViet slug format: /viec-lam/<keyword>-k-vi.html
            search_url = f"{self.base_url}/viec-lam/{kw}-k-vi.html"
            print(f"[CareerVietCrawler] Searching '{kw}' at: {search_url}")
            res = self.fetch(search_url)
            if not res:
                continue

            soup = BeautifulSoup(res.text, "html.parser")
            job_items = soup.find_all("div", class_="job-item")

            for item in job_items:
                link_el = item.find("a", class_="job_link")
                if not link_el or not link_el.get("href"):
                    continue

                href = link_el["href"]
                full_url = href if href.startswith("http") else f"{self.base_url}{href}"
                clean_url = full_url.split("?")[0]

                job_id_match = re.search(r'\.([0-9A-Za-z]{6,10})\.html', clean_url)
                job_id = f"careerviet_{job_id_match.group(1)}" if job_id_match else f"careerviet_{abs(hash(clean_url))}"

                if job_id in seen_ids:
                    continue
                seen_ids.add(job_id)

                title = link_el.get("title") or link_el.get_text(strip=True)
                company_el = item.find("a", class_="company-name")
                company = company_el.get_text(strip=True) if company_el else "Doanh nghiệp CareerViet"

                loc_el = item.find("div", class_="location") or item.find("li", class_="location")
                location = loc_el.get_text(strip=True) if loc_el else "Việt Nam"

                sal_el = item.find("div", class_="salary") or item.find("li", class_="salary")
                salary = sal_el.get_text(strip=True) if sal_el else "Thỏa thuận"

                time_el = item.find("time") or item.find("div", class_="time") or item.find("li", class_="time") or item.find("span", class_="date")
                posted_date = time_el.get_text(strip=True) if time_el else ""

                print(f"  -> Found [{company}]: {title}")
                raw_desc = self.crawl_job_detail(clean_url)
                if not raw_desc:
                    raw_desc = title

                job_obj = JobItem(
                    id=job_id,
                    title=title,
                    company=company,
                    location=location,
                    url=clean_url,
                    source="CareerViet",
                    raw_description=raw_desc,
                    salary=salary,
                    posted_date=posted_date,
                    tags=[kw]
                )
                jobs.append(job_obj)

                if len(jobs) >= max_jobs:
                    break
            if len(jobs) >= max_jobs:
                break

        print(f"[CareerVietCrawler] Total jobs crawled: {len(jobs)}")
        return jobs
