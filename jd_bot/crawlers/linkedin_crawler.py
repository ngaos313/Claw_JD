import re
import urllib.parse
from bs4 import BeautifulSoup
from typing import List, Optional
from .base_crawler import BaseCrawler, JobItem

class LinkedInCrawler(BaseCrawler):
    def __init__(self, delay_range=(1.5, 3.0), timeout=15):
        super().__init__(delay_range, timeout)
        self.search_api_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"

    def crawl_job_detail(self, job_url: str) -> str:
        self.sleep_polite()
        # Clean url
        clean_url = job_url.split('?')[0]
        res = self.fetch(clean_url)
        if not res:
            return ""
        soup = BeautifulSoup(res.text, "html.parser")
        desc_el = soup.find("div", class_="show-more-less-html__markup") or \
                  soup.find("div", class_="description__text") or \
                  soup.find("section", class_="show-more-less-html")
        if desc_el:
            return desc_el.get_text("\n", strip=True)
        return ""

    def crawl(self, keywords: List[str], location: str = "Vietnam", max_results_per_kw: int = 15) -> List[JobItem]:
        jobs = []
        seen_ids = set()

        for kw in keywords:
            print(f"[LinkedInCrawler] Searching keyword: '{kw}' in '{location}'...")
            start = 0
            while len(jobs) < max_results_per_kw * len(keywords) and start < max_results_per_kw:
                params = {
                    "keywords": kw,
                    "location": location,
                    "start": start
                }
                url = f"{self.search_api_url}?{urllib.parse.urlencode(params)}"
                res = self.fetch(url)
                if not res or not res.text.strip():
                    break

                soup = BeautifulSoup(res.text, "html.parser")
                cards = soup.find_all("li")
                if not cards:
                    break

                new_in_batch = 0
                for card in cards:
                    title_el = card.find("h3", class_="base-search-card__title")
                    company_el = card.find("h4", class_="base-search-card__subtitle") or card.find("a", class_="hidden-nested-link")
                    loc_el = card.find("span", class_="job-search-card__location")
                    link_el = card.find("a", class_="base-card__full-link")
                    date_el = card.find("time") or card.find("span", class_="job-search-card__listdate")

                    if not title_el or not link_el:
                        continue

                    title = title_el.get_text(strip=True)
                    company = company_el.get_text(strip=True) if company_el else "Unknown Company"
                    loc = loc_el.get_text(strip=True) if loc_el else location
                    raw_link = link_el.get("href", "")
                    job_id_match = re.search(r'-([0-9]{8,15})', raw_link) or re.search(r'view/([0-9]{8,15})', raw_link)
                    job_id = f"linkedin_{job_id_match.group(1)}" if job_id_match else f"linkedin_{abs(hash(raw_link))}"

                    if job_id in seen_ids:
                        continue
                    seen_ids.add(job_id)
                    new_in_batch += 1

                    posted_date = date_el.get_text(strip=True) if date_el else ""

                    print(f"  -> Found [{company}]: {title} ({job_id})")
                    # Fetch description
                    raw_desc = self.crawl_job_detail(raw_link)
                    if not raw_desc:
                        raw_desc = title

                    item = JobItem(
                        id=job_id,
                        title=title,
                        company=company,
                        location=loc,
                        url=raw_link.split('?')[0],
                        source="LinkedIn",
                        raw_description=raw_desc,
                        posted_date=posted_date,
                        tags=[kw]
                    )
                    jobs.append(item)

                    if len([j for j in jobs if kw in j.tags]) >= max_results_per_kw:
                        break

                if new_in_batch == 0:
                    break
                start += 10
                self.sleep_polite()

        print(f"[LinkedInCrawler] Total jobs crawled: {len(jobs)}")
        return jobs
