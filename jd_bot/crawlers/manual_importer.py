import os
import re
import json
from typing import List, Dict, Any
from .base_crawler import JobItem

class ManualImporter:
    @staticmethod
    def import_from_text(title: str, company: str, content: str, source: str = "Manual Input", url: str = "") -> JobItem:
        job_id = f"manual_{abs(hash(title + company + content[:100]))}"
        return JobItem(
            id=job_id,
            title=title,
            company=company,
            location="Vietnam / Remote",
            url=url,
            source=source,
            raw_description=content,
            tags=["manual"]
        )

    @staticmethod
    def import_from_file(filepath: str) -> List[JobItem]:
        jobs = []
        if not os.path.exists(filepath):
            return jobs

        with open(filepath, "r", encoding="utf-8") as f:
            if filepath.endswith(".json"):
                data = json.load(f)
                if isinstance(data, list):
                    for d in data:
                        jobs.append(JobItem(**d))
            else:
                text = f.read()
                jobs.append(ManualImporter.import_from_text(
                    title=os.path.basename(filepath),
                    company="Custom File",
                    content=text,
                    source="Local File"
                ))
        return jobs
