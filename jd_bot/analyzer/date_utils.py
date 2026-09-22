import re
import json
from datetime import datetime, timedelta
from typing import List, Tuple, Any

class DateUtils:
    """Utilities for parsing, standardizing, sorting dates and guarding dataset size."""

    @staticmethod
    def parse_date(date_str: str, now: datetime = None) -> Tuple[int, str]:
        """
        Parses various date formats and relative strings into:
        (unix_timestamp: int, formatted_display_str: str).
        Guarantees deterministic sorting from newest to oldest.
        """
        if now is None:
            now = datetime.now()

        if not date_str or not isinstance(date_str, str):
            # Fallback for empty date: assign current timestamp so fresh crawls stay near top
            ts = int(now.timestamp())
            return ts, "Gần đây"

        s = date_str.strip()
        if not s:
            return int(now.timestamp()), "Gần đây"

        # 1. ISO 8601 formats: 2026-09-15T21:00:00+07:00 or 2026-09-15 21:00:00 or 2026-09-15
        iso_match = re.match(r'^(\d{4})-(\d{2})-(\d{2})(?:[T ](\d{2}):(\d{2}):(\d{2}))?', s)
        if iso_match:
            try:
                y, m, d = int(iso_match.group(1)), int(iso_match.group(2)), int(iso_match.group(3))
                hh = int(iso_match.group(4)) if iso_match.group(4) else 0
                mm = int(iso_match.group(5)) if iso_match.group(5) else 0
                ss = int(iso_match.group(6)) if iso_match.group(6) else 0
                dt = datetime(y, m, d, hh, mm, ss)
                delta_days = (now - dt).days
                if delta_days == 0:
                    display = "Hôm nay"
                elif 0 < delta_days <= 7:
                    display = f"{dt.strftime('%d/%m/%Y')} ({delta_days} ngày trước)"
                else:
                    display = dt.strftime('%d/%m/%Y')
                return int(dt.timestamp()), display
            except Exception:
                pass

        # 2. DD/MM/YYYY or DD-MM-YYYY format (e.g. 18-10-2026 or 02/01/2025 10:08:22)
        slash_match = re.match(r'^(\d{1,2})[-/](\d{1,2})[-/](\d{4})(?:[T ](\d{2}):(\d{2}):(\d{2}))?', s)
        if slash_match:
            try:
                d, m, y = int(slash_match.group(1)), int(slash_match.group(2)), int(slash_match.group(3))
                hh = int(slash_match.group(4)) if slash_match.group(4) else 0
                mm = int(slash_match.group(5)) if slash_match.group(5) else 0
                ss = int(slash_match.group(6)) if slash_match.group(6) else 0
                dt = datetime(y, m, d, hh, mm, ss)
                delta_days = (now - dt).days
                if delta_days == 0:
                    display = "Hôm nay"
                elif 0 < delta_days <= 7:
                    display = f"{dt.strftime('%d/%m/%Y')} ({delta_days} ngày trước)"
                else:
                    display = dt.strftime('%d/%m/%Y')
                return int(dt.timestamp()), display
            except Exception:
                pass

        # 3. Relative English formats (handles plurals: hours, days, weeks, months)
        m_hour = re.search(r'(\d+)\s*(?:hours?|hrs?|h|giờ)\b', s, re.I)
        if m_hour:
            hours = int(m_hour.group(1))
            dt = now - timedelta(hours=hours)
            display = f"Hôm nay ({hours}h trước)" if hours < 24 else dt.strftime('%d/%m/%Y')
            return int(dt.timestamp()), display

        m_day = re.search(r'(\d+)\s*(?:days?|d|ngày)\b', s, re.I)
        if m_day:
            days = int(m_day.group(1))
            dt = now - timedelta(days=days)
            display = f"{dt.strftime('%d/%m/%Y')} ({days} ngày trước)" if days <= 7 else dt.strftime('%d/%m/%Y')
            return int(dt.timestamp()), display

        m_week = re.search(r'(\d+)\s*(?:weeks?|wks?|w|tuần)\b', s, re.I)
        if m_week:
            weeks = int(m_week.group(1))
            dt = now - timedelta(weeks=weeks)
            display = f"{dt.strftime('%d/%m/%Y')} ({weeks} tuần trước)"
            return int(dt.timestamp()), display

        m_month = re.search(r'(\d+)\s*(?:months?|mos?|m|tháng)\b', s, re.I)
        if m_month:
            months = int(m_month.group(1))
            dt = now - timedelta(days=months * 30)
            display = f"{dt.strftime('%d/%m/%Y')} ({months} tháng trước)"
            return int(dt.timestamp()), display

        # Special relative keywords
        lower_s = s.lower()
        if any(w in lower_s for w in ['yesterday', 'hôm qua']):
            dt = now - timedelta(days=1)
            return int(dt.timestamp()), f"{dt.strftime('%d/%m/%Y')} (Hôm qua)"
        if any(w in lower_s for w in ['today', 'hôm nay', 'just now', 'vừa xong']):
            return int(now.timestamp()), "Hôm nay"

        # Fallback: cannot parse, use current timestamp with clean original label
        return int(now.timestamp()), s[:30]

    @classmethod
    def sort_jobs_by_date(cls, jobs: List[Any], descending: bool = True) -> List[Any]:
        """Sorts a list of JobItem objects or dicts from newest to oldest (thời gian gần đây nhất đến xa nhất)."""
        def get_ts(j):
            if hasattr(j, 'posted_timestamp'):
                return getattr(j, 'posted_timestamp') or 0
            if isinstance(j, dict):
                return j.get('posted_timestamp') or 0
            return 0

        return sorted(jobs, key=get_ts, reverse=descending)

    @classmethod
    def prune_jobs_by_size(cls, jobs: List[Any], max_size_mb: float = 100.0, safety_buffer_mb: float = 10.0) -> List[Any]:
        """
        Ensures the dataset does not exceed max_size_mb (100MB).
        If size exceeds max_size_mb, removes the oldest JDs (by timestamp)
        until the serialized JSON size drops safely below (max_size_mb - safety_buffer_mb).
        """
        max_bytes = int(max_size_mb * 1024 * 1024)
        target_bytes = int((max_size_mb - safety_buffer_mb) * 1024 * 1024)

        # First, ensure jobs are sorted descending (newest first, oldest last)
        sorted_jobs = cls.sort_jobs_by_date(jobs, descending=True)

        # Estimate serialized size
        dict_jobs = [j.to_dict() if hasattr(j, 'to_dict') else j for j in sorted_jobs]
        raw_json_str = json.dumps(dict_jobs, ensure_ascii=False)
        current_bytes = len(raw_json_str.encode('utf-8'))

        if current_bytes <= max_bytes:
            # Under threshold, no pruning needed
            return sorted_jobs

        print(f"[⚠️ SizeGuard] Dataset size ({current_bytes / 1024 / 1024:.2f} MB) exceeds limit ({max_size_mb} MB)!")
        print(f"[⚠️ SizeGuard] Pruning oldest JDs to reach safe threshold ({target_bytes / 1024 / 1024:.2f} MB)...")

        initial_count = len(sorted_jobs)
        # Pop oldest jobs from the tail
        while len(sorted_jobs) > 1 and current_bytes > target_bytes:
            excess_bytes = current_bytes - target_bytes
            avg_job_bytes = max(1, int(current_bytes / len(sorted_jobs)))
            estimated_drop = max(1, int(excess_bytes / avg_job_bytes))
            drop_count = min(len(sorted_jobs) - 1, estimated_drop)
            sorted_jobs = sorted_jobs[:-drop_count]

            dict_jobs = [j.to_dict() if hasattr(j, 'to_dict') else j for j in sorted_jobs]
            raw_json_str = json.dumps(dict_jobs, ensure_ascii=False)
            current_bytes = len(raw_json_str.encode('utf-8'))

        pruned_count = initial_count - len(sorted_jobs)
        print(f"[✓ SizeGuard] Pruned {pruned_count} oldest JDs. Remaining: {len(sorted_jobs)} JDs ({current_bytes / 1024 / 1024:.2f} MB).")
        return sorted_jobs
