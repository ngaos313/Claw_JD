import re
import urllib.parse
from bs4 import BeautifulSoup
from typing import List, Optional
from .base_crawler import BaseCrawler, JobItem

class ITViecCrawler(BaseCrawler):
    def __init__(self, delay_range=(1.5, 3.0), timeout=15):
        super().__init__(delay_range, timeout)
        self.base_url = "https://itviec.com"

    def crawl_job_detail(self, job_url: str) -> str:
        self.sleep_polite()
        res = self.fetch(job_url)
        if not res:
            return ""
        soup = BeautifulSoup(res.text, "html.parser")
        desc_el = soup.find("div", class_="job-details") or \
                  soup.find("div", class_="job-description") or \
                  soup.find("div", class_="job-details__paragraph")
        if desc_el:
            return desc_el.get_text("\n", strip=True)
        return ""

    def crawl(self, tags: List[str] = None, max_jobs: int = 30) -> List[JobItem]:
        if not tags:
            tags = ["security", "cloud", "devops"]

        jobs = []
        seen_ids = set()

        for tag in tags:
            tag_url = f"{self.base_url}/it-jobs/{tag}"
            print(f"[ITViecCrawler] Fetching tag '{tag}' at: {tag_url}")
            res = self.fetch(tag_url)
            if not res:
                continue

            soup = BeautifulSoup(res.text, "html.parser")
            # Cards can be found by looking for h3 with links containing /it-jobs/
            h3_tags = soup.find_all("h3")
            for h3 in h3_tags:
                a_tag = h3.find("a")
                if not a_tag or not a_tag.get("href"):
                    continue

                href = a_tag["href"]
                if "/it-jobs/" not in href or href.count("/") < 3:
                    continue

                full_url = href if href.startswith("http") else f"{self.base_url}{href}"
                clean_url = full_url.split("?")[0]
                job_id_match = re.search(r'-([0-9]{3,8})', clean_url)
                job_id = f"itviec_{job_id_match.group(1)}" if job_id_match else f"itviec_{abs(hash(clean_url))}"

                if job_id in seen_ids:
                    continue
                seen_ids.add(job_id)

                title = a_tag.get_text(strip=True)

                # Try to locate parent card for company and location
                card = h3.find_parent("div", class_=lambda c: c and "job-card" in c) or h3.parent
                company = "ITViec Employer"
                location = "Vietnam"
                salary = "Thỏa thuận"
                tag_list = [tag]

                posted_date = ""
                if card:
                    comp_el = card.find("span", class_=lambda c: c and "employer" in c) or card.find("a", class_=lambda c: c and "employer" in c)
                    if comp_el:
                        company = comp_el.get_text(strip=True)
                    loc_el = card.find("span", class_=lambda c: c and ("location" in c or "city" in c))
                    if loc_el:
                        location = loc_el.get_text(strip=True)
                    sal_el = card.find("span", class_=lambda c: c and "salary" in c)
                    if sal_el:
                        salary = sal_el.get_text(strip=True)

                    time_el = card.find("span", class_=lambda c: c and "distance-time" in c) or card.find("time")
                    if time_el:
                        posted_date = time_el.get_text(strip=True)
                    else:
                        for s_el in card.find_all(["span", "div"]):
                            txt = s_el.get_text(strip=True)
                            if any(w in txt.lower() for w in ["ago", "trước", "hours", "days", "weeks"]):
                                posted_date = txt.replace("Posted", "").replace("Đăng", "").strip()
                                break

                print(f"  -> Found [{company}]: {title}")
                raw_desc = self.crawl_job_detail(full_url)
                if not raw_desc:
                    raw_desc = title

                item = JobItem(
                    id=job_id,
                    title=title,
                    company=company,
                    location=location,
                    url=clean_url,
                    source="ITviec",
                    raw_description=raw_desc,
                    salary=salary,
                    posted_date=posted_date,
                    tags=tag_list
                )
                jobs.append(item)

                if len(jobs) >= max_jobs:
                    break
            if len(jobs) >= max_jobs:
                break

        print(f"[ITViecCrawler] Total jobs crawled: {len(jobs)}")
        return jobs
