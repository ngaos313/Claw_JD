import re
import requests
from bs4 import BeautifulSoup
from typing import List, Optional
from .base_crawler import BaseCrawler, JobItem

class VietnamWorksCrawler(BaseCrawler):
    def __init__(self, delay_range=(1.0, 2.0), timeout=15):
        super().__init__(delay_range, timeout)
        self.api_url = "https://ms.vietnamworks.com/job-search/v1.0/search"

    def crawl(self, queries: List[str] = None, max_results_per_query: int = 15) -> List[JobItem]:
        if not queries:
            queries = [
                "an toan thong tin",
                "cloud security",
                "devsecops",
                "security engineer",
                "penetration test",
                "grc"
            ]

        jobs = []
        seen_ids = set()

        for q in queries:
            print(f"[VietnamWorksCrawler] Searching query '{q}'...")
            payload = {
                "query": q,
                "filter": [],
                "ranges": [],
                "order": [],
                "hitsPerPage": max_results_per_query,
                "page": 0
            }

            try:
                self.sleep_polite()
                res = self.session.post(
                    self.api_url,
                    json=payload,
                    headers={
                        **self.get_headers(),
                        "Accept": "application/json, text/plain, */*",
                        "Content-Type": "application/json"
                    },
                    timeout=self.timeout
                )
                if res.status_code != 200:
                    print(f"[VietnamWorksCrawler] Status {res.status_code} for query: {q}")
                    continue

                data = res.json()
                items = data.get("data", [])
                print(f"  -> Found {len(items)} jobs for '{q}'")

                for item in items:
                    raw_id = str(item.get("jobId", ""))
                    job_id = f"vietnamworks_{raw_id}"
                    if job_id in seen_ids:
                        continue
                    seen_ids.add(job_id)

                    title = item.get("jobTitle", "Vị trí bảo mật")
                    company = item.get("companyName", "Doanh nghiệp VietnamWorks")
                    salary = item.get("prettySalary") or "Thương lượng"
                    url = item.get("jobUrl") or f"https://www.vietnamworks.com/job/{raw_id}"

                    # Clean html from description & requirement
                    desc_html = item.get("jobDescription") or ""
                    req_html = item.get("jobRequirement") or ""
                    soup_desc = BeautifulSoup(f"{desc_html}\n{req_html}", "html.parser")
                    clean_desc = soup_desc.get_text("\n", strip=True)

                    # Extract location
                    locations = item.get("locations", [])
                    loc_name = locations[0].get("name", "Việt Nam") if locations else "Việt Nam"

                    # Skills
                    raw_skills = item.get("skills", [])
                    skill_tags = [s.get("skillName") for s in raw_skills if isinstance(s, dict) and s.get("skillName")]
                    # Posted date
                    posted_date = str(item.get("approvedOn") or item.get("createdOn") or item.get("startDate") or "")

                    job_obj = JobItem(
                        id=job_id,
                        title=title,
                        company=company,
                        location=loc_name,
                        url=url,
                        source="VietnamWorks",
                        raw_description=clean_desc if clean_desc else title,
                        salary=salary,
                        posted_date=posted_date,
                        tags=[q] + skill_tags[:3]
                    )
                    jobs.append(job_obj)

            except Exception as e:
                print(f"[VietnamWorksCrawler] Error searching query {q}: {e}")

        print(f"[VietnamWorksCrawler] Total jobs crawled: {len(jobs)}")
        return jobs
