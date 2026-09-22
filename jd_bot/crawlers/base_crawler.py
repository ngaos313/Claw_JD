import time
import random
import requests
from dataclasses import dataclass, asdict, field
from typing import Optional, List, Dict, Any

@dataclass
class JobItem:
    id: str
    title: str
    company: str
    location: str
    url: str
    source: str
    raw_description: str
    salary: Optional[str] = "Thỏa thuận"
    posted_date: Optional[str] = ""
    posted_timestamp: Optional[int] = 0
    posted_date_display: Optional[str] = ""
    tags: List[str] = field(default_factory=list)
    track: Optional[str] = "Unclassified"
    extracted_skills: List[str] = field(default_factory=list)
    extracted_certs: List[str] = field(default_factory=list)
    english_level: Optional[str] = "Not Specified"
    experience_years: Optional[str] = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class BaseCrawler:
    def __init__(self, delay_range=(1.0, 2.5), timeout=15):
        self.delay_range = delay_range
        self.timeout = timeout
        self.session = requests.Session()
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0"
        ]

    def get_headers(self) -> Dict[str, str]:
        return {
            "User-Agent": random.choice(self.user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,vi;q=0.8",
            "Connection": "keep-alive"
        }

    def sleep_polite(self):
        duration = random.uniform(*self.delay_range)
        time.sleep(duration)

    def fetch(self, url: str, headers: Optional[Dict[str, str]] = None) -> Optional[requests.Response]:
        req_headers = self.get_headers()
        if headers:
            req_headers.update(headers)
        try:
            res = self.session.get(url, headers=req_headers, timeout=self.timeout)
            if res.status_code == 200:
                return res
            else:
                print(f"[{self.__class__.__name__}] Non-200 status {res.status_code} for URL: {url}")
                return None
        except Exception as e:
            print(f"[{self.__class__.__name__}] Request error for {url}: {e}")
            return None

    def crawl(self, keywords: List[str], max_results: int = 20) -> List[JobItem]:
        raise NotImplementedError("Subclasses must implement crawl()")
