import os
import sys
import json
import argparse
from typing import List, Dict, Any

# Ensure utf-8 output on Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from jd_bot.crawlers.base_crawler import JobItem
from jd_bot.crawlers.linkedin_crawler import LinkedInCrawler
from jd_bot.crawlers.itviec_crawler import ITViecCrawler
from jd_bot.crawlers.careerviet_crawler import CareerVietCrawler
from jd_bot.crawlers.vietnamworks_crawler import VietnamWorksCrawler
from jd_bot.crawlers.cissp_facebook_crawler import CISSPFacebookCrawler
from jd_bot.analyzer.cv_parser import CVParser
from jd_bot.analyzer.jd_extractor import JDExtractor
from jd_bot.analyzer.date_utils import DateUtils
from jd_bot.analyzer.profile_matcher import ProfileMatcher
from jd_bot.analyzer.roadmap_generator import RoadmapGenerator
from jd_bot.reports.dashboard_generator import DashboardGenerator
from jd_bot.reports.summary_markdown import SummaryMarkdownGenerator
from jd_bot.reports.private_gap_generator import PrivateGapGenerator

DATA_DIR = os.path.join(os.path.dirname(__file__), "jd_bot", "data")
RAW_JDS_PATH = os.path.join(DATA_DIR, "raw_jds.json")

def resolve_candidate_profile(cv_arg: str = "") -> Dict[str, Any]:
    if cv_arg and os.path.exists(cv_arg):
        print(f"[+] Loading custom candidate profile from: {cv_arg}")
        return CVParser.parse_cv_file(cv_arg)

    root_dir = os.path.dirname(__file__)
    candidate_locations = [
        os.path.join(root_dir, "local_private", "cv", "profile.json"),
        os.path.join(root_dir, "local_private", "cv", "current_cv.pdf"),
        os.path.join(root_dir, "local_private", "cv", "Nguyen-Thanh-Duc-TopCV.vn-240726.145808.pdf"),
        os.path.join(root_dir, "local_private", "reports", "profile.json"),
        os.path.join(root_dir, "user_profiles", "profile.json"),
        os.path.join(root_dir, "user_profiles", "current_cv.pdf")
    ]
    for loc in candidate_locations:
        if os.path.exists(loc):
            return CVParser.parse_cv_file(loc)

    return CVParser.get_default_profile()

def run_crawlers(sources: List[str] = None, max_per_source: int = 30) -> List[JobItem]:
    if not sources:
        sources = ["linkedin", "itviec", "careerviet", "vietnamworks", "cissp_fb"]

    os.makedirs(DATA_DIR, exist_ok=True)
    all_jobs: List[JobItem] = []

    if "linkedin" in sources:
        print("\n[1/5] Running LinkedIn Crawler...")
        lic = LinkedInCrawler()
        keywords = [
            "DFIR",
            "Incident Response",
            "Cloud Security",
            "DevSecOps",
            "Application Security",
            "Security Engineer",
            "Information Security GRC",
            "Security Architect",
            "Penetration Tester"
        ]
        try:
            li_jobs = lic.crawl(keywords, location="Vietnam", max_results_per_kw=5)
            all_jobs.extend(li_jobs)
        except Exception as e:
            print(f"[!] Error in LinkedIn Crawler: {e}")

    if "itviec" in sources:
        print("\n[2/5] Running ITviec Crawler...")
        itv = ITViecCrawler()
        try:
            itv_jobs = itv.crawl(tags=["security", "cloud", "devops"], max_jobs=20)
            all_jobs.extend(itv_jobs)
        except Exception as e:
            print(f"[!] Error in ITviec Crawler: {e}")

    if "careerviet" in sources:
        print("\n[3/5] Running CareerViet Crawler...")
        cvc = CareerVietCrawler()
        try:
            cv_jobs = cvc.crawl(search_keywords=["an-toan-thong-tin", "devsecops"], max_jobs=20)
            all_jobs.extend(cv_jobs)
        except Exception as e:
            print(f"[!] Error in CareerViet Crawler: {e}")

    if "vietnamworks" in sources:
        print("\n[4/5] Running VietnamWorks Crawler...")
        vnw = VietnamWorksCrawler()
        try:
            vnw_jobs = vnw.crawl(max_results_per_query=10)
            all_jobs.extend(vnw_jobs)
        except Exception as e:
            print(f"[!] Error in VietnamWorks Crawler: {e}")

    if "cissp_fb" in sources:
        print("\n[5/5] Running CISSP Facebook Group Crawler...")
        cfb = CISSPFacebookCrawler()
        try:
            fb_jobs = cfb.crawl(max_jobs=150)
            all_jobs.extend(fb_jobs)
        except Exception as e:
            print(f"[!] Error in CISSP Facebook Crawler: {e}")

    print(f"\n[+] Enriching, classifying and deduplicating {len(all_jobs)} jobs across 5 platforms...")
    enriched_jobs = []
    seen_ids = set()
    for job in all_jobs:
        if job.id in seen_ids:
            continue
        seen_ids.add(job.id)
        enriched = JDExtractor.enrich_job(job)
        enriched_jobs.append(enriched)

    # 1. Sort strictly from newest to oldest (thời gian gần đây nhất đến xa nhất)
    sorted_jobs = DateUtils.sort_jobs_by_date(enriched_jobs, descending=True)

    # 2. Pruning guard: If dataset exceeds 100MB, prune oldest JDs
    final_jobs = DateUtils.prune_jobs_by_size(sorted_jobs, max_size_mb=100.0)

    with open(RAW_JDS_PATH, "w", encoding="utf-8") as f:
        json.dump([j.to_dict() for j in final_jobs], f, ensure_ascii=False, indent=2)

    file_size_mb = os.path.getsize(RAW_JDS_PATH) / 1024 / 1024
    print(f"[+] Successfully saved {len(final_jobs)} jobs to {RAW_JDS_PATH} (Size: {file_size_mb:.2f} MB, Limit: 100 MB)")
    return final_jobs

def run_local_gap_analysis(jobs: List[JobItem] = None, candidate_profile: Dict[str, Any] = None):
    """Generates PRIVATE local gap analysis and roadmaps strictly on local machine."""
    if not jobs:
        if os.path.exists(RAW_JDS_PATH):
            with open(RAW_JDS_PATH, "r", encoding="utf-8") as f:
                jobs = [JobItem(**d) for d in json.load(f)]
        else:
            print("[!] Raw JDs not found. Run --crawl first.")
            return

    if not candidate_profile:
        candidate_profile = resolve_candidate_profile()

    print(f"\n[🔒 LOCAL] Running Private Gap Analysis against: {candidate_profile.get('name')}...")
    matcher = ProfileMatcher(candidate_profile)
    track_results = matcher.evaluate_tracks(jobs)
    roadmaps = RoadmapGenerator.generate_all_roadmaps()

    # Generate private local HTML and Markdown in local_private/reports
    reports_dir = os.path.join(os.path.dirname(__file__), "local_private", "reports")
    os.makedirs(reports_dir, exist_ok=True)
    private_html = os.path.join(reports_dir, "private_gap_analysis.html")
    PrivateGapGenerator.generate_private_dashboard(jobs, track_results, roadmaps, candidate_profile, private_html)

    private_md = os.path.join(reports_dir, "career_pivot_report.md")
    SummaryMarkdownGenerator.generate_report(jobs, track_results, roadmaps, private_md)

    print(f"[✓] Private local gap analysis ready at: {os.path.abspath(private_html)}")
    print(f"[✓] Private local markdown report ready at: {os.path.abspath(private_md)}")

def generate_public_dashboard(jobs: List[JobItem] = None):
    """Generates the PUBLIC Job Aggregator & Market Explorer dashboard for GitHub Pages."""
    if not jobs:
        if os.path.exists(RAW_JDS_PATH):
            with open(RAW_JDS_PATH, "r", encoding="utf-8") as f:
                jobs = [JobItem(**d) for d in json.load(f)]
        else:
            jobs = []

    # Ensure jobs are sorted newest first
    jobs = DateUtils.sort_jobs_by_date(jobs, descending=True)

    # Get general track requirements for market stats
    track_meta = {}
    from jd_bot.analyzer.profile_matcher import TRACK_REQUIREMENTS
    for t_name, req in TRACK_REQUIREMENTS.items():
        track_meta[t_name] = {
            "top_certs": req.get("top_certs", []),
            "roi_rating": req.get("roi_rating", "")
        }

    print("\n[+] Generating Clean Public Aggregator Dashboard (index.html)...")
    html_path = DashboardGenerator.generate_html(jobs, track_meta, "index.html")

    print(f"[✓] Public Dashboard ready: {os.path.abspath('index.html')}")

def sync_data_from_git():
    """Pulls latest crawled JDs and data from GitHub repository to local machine."""
    import subprocess
    git_cmd = os.path.expandvars(r'%LOCALAPPDATA%\Programs\MinGit\cmd\git.exe')
    if not os.path.exists(git_cmd):
        git_cmd = 'git'
    print("\n[+] Pulling latest crawled JDs from GitHub (git pull origin main)...")
    try:
        res = subprocess.run([git_cmd, 'pull', 'origin', 'main'], capture_output=True, text=True, cwd=os.path.dirname(__file__))
        if res.stdout:
            print(res.stdout.strip())
        if res.returncode == 0:
            print("[✓] Successfully synced latest JDs from Git!")
        else:
            print(f"[!] Git note: {res.stderr.strip() or res.stdout.strip()}")
    except Exception as e:
        print(f"[!] Warning: Could not run git pull: {e}")

def main():
    parser = argparse.ArgumentParser(description="Cybersecurity Job Aggregator & Market Intelligence")
    parser.add_argument("--crawl", action="store_true", help="Crawl jobs from all sources")
    parser.add_argument("--report", action="store_true", help="Generate clean public aggregator dashboard (index.html)")
    parser.add_argument("--all", action="store_true", help="Run crawler and refresh public dashboard (used on GitHub Actions)")
    parser.add_argument("--gap", action="store_true", help="Run PRIVATE personal gap analysis & roadmap locally on your machine")
    parser.add_argument("--pull", action="store_true", help="Pull latest crawled JDs from GitHub before running local analysis")
    parser.add_argument("--cv", type=str, default="", help="Path to custom CV file for local gap analysis")
    parser.add_argument("--sources", type=str, default="", help="Comma-separated sources: linkedin,itviec,careerviet,vietnamworks,cissp_fb")

    args = parser.parse_args()
    selected_sources = [s.strip() for s in args.sources.split(",") if s.strip()] if args.sources else None

    # Sync fresh data from GitHub if requested
    if args.pull:
        sync_data_from_git()

    # If user wants local gap analysis
    if args.gap or args.cv:
        candidate_profile = resolve_candidate_profile(args.cv)
        run_local_gap_analysis(None, candidate_profile)
        return

    # Standard / Git workflow: Crawl & Refresh Dashboard
    if args.all or (not args.crawl and not args.report):
        jobs = run_crawlers(selected_sources)
        generate_public_dashboard(jobs)
    else:
        if args.crawl:
            jobs = run_crawlers(selected_sources)
            generate_public_dashboard(jobs)
        elif args.report:
            generate_public_dashboard(None)

if __name__ == "__main__":
    main()
