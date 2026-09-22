import json
import os
from typing import Dict, List, Any
from jd_bot.crawlers.base_crawler import JobItem

class DashboardGenerator:
    @staticmethod
    def generate_html(
        crawled_jobs: List[JobItem],
        track_analysis: Dict[str, Any] = None,
        output_filepath: str = "index.html"
    ) -> str:
        jobs_json = json.dumps([j.to_dict() for j in crawled_jobs], ensure_ascii=False)
        total_jobs = len(crawled_jobs)

        # Track counts
        track_counts = {}
        for j in crawled_jobs:
            t = j.track or "An toàn Thông tin Chung"
            track_counts[t] = track_counts.get(t, 0) + 1
        track_counts_json = json.dumps(track_counts, ensure_ascii=False)

        top_track = max(track_counts.items(), key=lambda x: x[1])[0] if track_counts else "Cloud Security / DevSecOps"

        # Source breakdown
        source_counts = {}
        for j in crawled_jobs:
            source_counts[j.source] = source_counts.get(j.source, 0) + 1
        source_counts_json = json.dumps(source_counts, ensure_ascii=False)

        track_meta = track_analysis or {}
        track_meta_json = json.dumps(track_meta, ensure_ascii=False)

        html_template = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cybersecurity Job Aggregator & Market Intelligence</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --bg-main: #0a0f1d;
            --bg-card: rgba(18, 26, 47, 0.75);
            --bg-card-hover: rgba(28, 40, 72, 0.85);
            --border-card: rgba(255, 255, 255, 0.08);
            --border-glow: rgba(56, 189, 248, 0.3);
            --primary: #38bdf8;
            --primary-glow: rgba(56, 189, 248, 0.2);
            --secondary: #818cf8;
            --accent-green: #34d399;
            --accent-purple: #c084fc;
            --accent-rose: #fb7185;
            --accent-amber: #fbbf24;
            --text-main: #f1f5f9;
            --text-muted: #94a3b8;
            --text-dim: #64748b;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: 'Plus Jakarta Sans', sans-serif;
            background-color: var(--bg-main);
            color: var(--text-main);
            min-height: 100vh;
            line-height: 1.6;
            overflow-x: hidden;
            background-image: 
                radial-gradient(circle at 10% 15%, rgba(56, 189, 248, 0.08) 0%, transparent 40%),
                radial-gradient(circle at 90% 85%, rgba(129, 140, 248, 0.08) 0%, transparent 45%),
                radial-gradient(circle at 50% 50%, rgba(52, 211, 153, 0.04) 0%, transparent 50%);
            background-attachment: fixed;
        }}

        header {{
            border-bottom: 1px solid var(--border-card);
            background: rgba(10, 15, 29, 0.85);
            backdrop-filter: blur(16px);
            position: sticky;
            top: 0;
            z-index: 50;
            padding: 1rem 2rem;
        }}

        .header-content {{
            max-width: 1400px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1rem;
        }}

        .brand {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .brand-logo {{
            width: 44px;
            height: 44px;
            border-radius: 12px;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 0 20px var(--primary-glow);
            font-weight: 800;
            font-size: 1.25rem;
            color: #fff;
        }}

        .brand-text h1 {{
            font-size: 1.3rem;
            font-weight: 800;
            background: linear-gradient(90deg, #fff, #94a3b8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .brand-text p {{
            font-size: 0.8rem;
            color: var(--text-muted);
        }}

        .nav-tabs {{
            display: flex;
            gap: 8px;
            background: rgba(18, 26, 47, 0.6);
            padding: 4px;
            border-radius: 12px;
            border: 1px solid var(--border-card);
        }}

        .nav-tab {{
            padding: 8px 18px;
            border-radius: 8px;
            border: none;
            background: transparent;
            color: var(--text-muted);
            font-weight: 600;
            font-size: 0.88rem;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .nav-tab:hover {{
            color: var(--text-main);
            background: rgba(255, 255, 255, 0.05);
        }}

        .nav-tab.active {{
            color: #fff;
            background: linear-gradient(135deg, rgba(56, 189, 248, 0.25), rgba(129, 140, 248, 0.25));
            border: 1px solid rgba(56, 189, 248, 0.4);
            box-shadow: 0 0 15px rgba(56, 189, 248, 0.15);
        }}

        .container {{
            max-width: 1400px;
            margin: 2rem auto;
            padding: 0 1.5rem;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 1.25rem;
            margin-bottom: 2rem;
        }}

        .stat-card {{
            background: var(--bg-card);
            backdrop-filter: blur(12px);
            border: 1px solid var(--border-card);
            border-radius: 16px;
            padding: 1.25rem 1.5rem;
            position: relative;
            overflow: hidden;
            transition: transform 0.3s ease, border-color 0.3s ease;
        }}

        .stat-card:hover {{
            transform: translateY(-3px);
            border-color: var(--border-glow);
        }}

        .stat-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--primary), var(--secondary));
        }}

        .stat-label {{
            font-size: 0.85rem;
            color: var(--text-muted);
            font-weight: 500;
        }}

        .stat-value {{
            font-size: 1.8rem;
            font-weight: 800;
            color: #fff;
            margin-top: 4px;
        }}

        .stat-subtext {{
            font-size: 0.75rem;
            color: var(--accent-green);
            margin-top: 4px;
            display: flex;
            align-items: center;
            gap: 4px;
        }}

        .grid-2 {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}

        @media (max-width: 992px) {{
            .grid-2 {{
                grid-template-columns: 1fr;
            }}
        }}

        .card {{
            background: var(--bg-card);
            backdrop-filter: blur(12px);
            border: 1px solid var(--border-card);
            border-radius: 18px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            position: relative;
        }}

        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.25rem;
            border-bottom: 1px solid var(--border-card);
            padding-bottom: 0.75rem;
            flex-wrap: wrap;
            gap: 8px;
        }}

        .card-title {{
            font-size: 1.15rem;
            font-weight: 700;
            color: #fff;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .badge {{
            font-size: 0.75rem;
            padding: 4px 10px;
            border-radius: 9999px;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }}

        .badge-cyan {{
            background: rgba(56, 189, 248, 0.15);
            color: var(--primary);
            border: 1px solid rgba(56, 189, 248, 0.3);
        }}

        .badge-green {{
            background: rgba(52, 211, 153, 0.15);
            color: var(--accent-green);
            border: 1px solid rgba(52, 211, 153, 0.3);
        }}

        /* Source badges */
        .source-badge {{
            font-size: 0.7rem;
            font-weight: 700;
            padding: 3px 8px;
            border-radius: 6px;
            letter-spacing: 0.02em;
        }}
        .src-linkedin {{ background: #0077b5; color: #fff; }}
        .src-itviec {{ background: #ea580c; color: #fff; }}
        .src-careerviet {{ background: #4f46e5; color: #fff; }}
        .src-vietnamworks {{ background: #0284c7; color: #fff; }}
        .src-cyberjutsu {{ background: #cf1337; color: #fff; }}
        .src-cissp {{ background: #d97706; color: #fff; }}

        .track-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
            gap: 1.25rem;
        }}

        .track-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-card);
            border-radius: 16px;
            padding: 1.25rem 1.5rem;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: all 0.3s ease;
        }}

        .track-card:hover {{
            transform: translateY(-4px);
            border-color: var(--border-glow);
            box-shadow: 0 12px 30px rgba(0, 0, 0, 0.3);
        }}

        .track-title-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.75rem;
        }}

        .track-title {{
            font-size: 1.05rem;
            font-weight: 700;
            color: #fff;
        }}

        .track-job-count {{
            background: rgba(56, 189, 248, 0.15);
            color: var(--primary);
            border: 1px solid rgba(56, 189, 248, 0.3);
            padding: 4px 10px;
            border-radius: 9999px;
            font-weight: 700;
            font-size: 0.8rem;
        }}

        .pill-list {{
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-top: 8px;
        }}

        .pill {{
            font-size: 0.75rem;
            padding: 3px 9px;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--border-card);
            color: #cbd5e1;
        }}

        .pill-accent {{
            background: rgba(56, 189, 248, 0.1);
            border-color: rgba(56, 189, 248, 0.25);
            color: var(--primary);
        }}

        /* Search Bar & Filters */
        .search-bar-row {{
            display: flex;
            gap: 1rem;
            margin-bottom: 1.25rem;
            flex-wrap: wrap;
        }}

        .search-input {{
            flex: 1;
            min-width: 280px;
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid var(--border-card);
            color: #fff;
            padding: 10px 16px;
            border-radius: 10px;
            font-size: 0.9rem;
            outline: none;
            transition: border-color 0.2s;
        }}

        .search-input:focus {{
            border-color: var(--primary);
        }}

        .select-filter {{
            background: rgba(18, 26, 47, 0.9);
            border: 1px solid var(--border-card);
            color: #fff;
            padding: 10px 16px;
            border-radius: 10px;
            font-size: 0.85rem;
            outline: none;
            cursor: pointer;
            max-width: 320px;
        }}

        .job-card-item {{
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid var(--border-card);
            border-radius: 12px;
            padding: 1.25rem;
            margin-bottom: 1rem;
            transition: all 0.2s ease;
        }}

        .job-card-item:hover {{
            background: rgba(255, 255, 255, 0.04);
            border-color: rgba(56, 189, 248, 0.3);
        }}

        .job-header-row {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 8px;
            flex-wrap: wrap;
            gap: 8px;
        }}

        .job-title-link {{
            font-size: 1.05rem;
            font-weight: 700;
            color: #fff;
            text-decoration: none;
            transition: color 0.2s;
        }}

        .job-title-link:hover {{
            color: var(--primary);
        }}

        .job-company {{
            color: var(--secondary);
            font-weight: 600;
            font-size: 0.9rem;
        }}

        .job-snippet {{
            font-size: 0.85rem;
            color: var(--text-muted);
            margin: 8px 0;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}

        .tab-pane {{
            display: none;
        }}

        .tab-pane.active {{
            display: block;
        }}

        footer {{
            border-top: 1px solid var(--border-card);
            padding: 2rem;
            text-align: center;
            color: var(--text-dim);
            font-size: 0.85rem;
            margin-top: 4rem;
        }}
    </style>
</head>
<body>

    <!-- Header -->
    <header>
        <div class="header-content">
            <div class="brand">
                <div class="brand-logo">🛡️</div>
                <div class="brand-text">
                    <h1>Cybersecurity Job & Market Aggregator</h1>
                    <p>Tổng hợp Việc làm ATTT từ 5 Nền tảng (LinkedIn, ITviec, CareerViet, VietnamWorks, CISSP FB)</p>
                </div>
            </div>

            <div class="nav-tabs">
                <button class="nav-tab active" onclick="switchTab('tab-overview')">📊 Thị trường & Xu hướng</button>
                <button class="nav-tab" onclick="switchTab('tab-jobs')">📋 Khám phá Việc làm (<span id="tabJobCount">{total_jobs}</span>)</button>
            </div>
        </div>
    </header>

    <div class="container">
        <!-- Key Metrics -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Tổng số việc làm đã tổng hợp</div>
                <div class="stat-value">{total_jobs}</div>
                <div class="stat-subtext">Cập nhật tự động trên GitHub Actions</div>
            </div>

            <div class="stat-card">
                <div class="stat-label">Nền tảng tuyển dụng tích hợp</div>
                <div class="stat-value" style="color: var(--primary);">{len(source_counts)} Nguồn</div>
                <div class="stat-subtext">LinkedIn &bull; ITviec &bull; CareerViet &bull; VietnamWorks &bull; CISSP FB</div>
            </div>

            <div class="stat-card">
                <div class="stat-label">Nhóm ngành có nhu cầu lớn nhất</div>
                <div class="stat-value" style="font-size: 1.25rem; color: var(--accent-green);">{top_track.split('/')[0]}</div>
                <div class="stat-subtext">Dựa trên phân tích {total_jobs}+ tin tuyển dụng</div>
            </div>

            <div class="stat-card">
                <div class="stat-label">Dải lương thị trường phổ biến</div>
                <div class="stat-value" style="color: var(--accent-amber);">25M - 55M+</div>
                <div class="stat-subtext">Phân khúc Middle - Senior / Specialist</div>
            </div>
        </div>

        <!-- TAB 1: OVERVIEW & MARKET CHARTS -->
        <div id="tab-overview" class="tab-pane active">
            <div class="grid-2">
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">
                            📈 Cơ Cấu Việc Làm Theo Chuyên Môn (Role Distribution)
                        </div>
                        <span class="badge badge-cyan">Tỷ trọng ngành</span>
                    </div>
                    <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 1rem;">
                        Tỷ lệ các tin tuyển dụng phân theo các nhánh chuyên môn: DFIR, Cloud Sec/DevSecOps, AppSec, SecOps SOAR, GRC, Pentest, Pre-Sales và SOC.
                    </p>
                    <div style="height: 340px; position: relative;">
                        <canvas id="trackPieChart"></canvas>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <div class="card-title">
                            🌐 Phân Bổ Nguồn Dữ Liệu Tuyển Dụng
                        </div>
                        <span class="badge badge-green">{len(source_counts)} Nền tảng</span>
                    </div>
                    <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 1rem;">
                        Số lượng bài tuyển dụng thu thập từ từng nguồn kênh (Mạng xã hội, sàn IT chuyên nghiệp, sàn việc làm chung).
                    </p>
                    <div style="height: 340px; position: relative;">
                        <canvas id="sourcePieChart"></canvas>
                    </div>
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <div class="card-title">
                        ⚡ Tổng Hợp Nhu Cầu & Kỹ Năng Theo Từng Nhánh Chuyên Môn
                    </div>
                </div>
                <div class="track-grid" id="trackCardContainer">
                    <!-- Injected via JS -->
                </div>
            </div>
        </div>

        <!-- TAB 2: LIVE JD EXPLORER -->
        <div id="tab-jobs" class="tab-pane">
            <div class="card">
                <div class="card-header">
                    <div class="card-title">
                        📋 Khám Phá & Tìm Kiếm Tin Tuyển Dụng Tổng Hợp
                    </div>
                    <span class="badge badge-cyan" id="jobFilterCount">{total_jobs} việc làm</span>
                </div>

                <div class="search-bar-row">
                    <input type="text" id="jobSearchInput" class="search-input" placeholder="Tìm kiếm vị trí, công ty, kỹ năng (DFIR, AWS, K8s, Python, ISO27001, Ngân hàng, SĐT liên hệ...)" onkeyup="filterJobs()">
                    
                    <select id="sourceFilterSelect" class="select-filter" onchange="filterJobs()">
                        <!-- Dynamically populated from JOBS_DATA -->
                    </select>

                    <select id="trackFilterSelect" class="select-filter" onchange="filterJobs()">
                        <!-- Dynamically populated from JOBS_DATA -->
                    </select>

                    <select id="sortOrderSelect" class="select-filter" onchange="filterJobs()" title="Thứ tự thời gian">
                        <option value="newest">🕒 Mới nhất trước (Gần đây nhất ⬇️)</option>
                        <option value="oldest">⏳ Cũ nhất trước (Xa nhất ⬆️)</option>
                        <option value="title">🔤 Tên vị trí (A-Z)</option>
                    </select>
                </div>

                <div id="jobListContainer">
                    <!-- Injected via JS -->
                </div>
            </div>
        </div>
    </div>

    <!-- Footer -->
    <footer>
        <p>Cybersecurity Job Aggregator & Market Intelligence &bull; Tích hợp LinkedIn, ITviec, CareerViet, VietnamWorks & CISSP Facebook Group &bull; Tự động cập nhật 24/7 qua GitHub Actions</p>
    </footer>

    <script>
        const JOBS_DATA = {jobs_json};
        const TRACK_COUNTS = {track_counts_json};
        const SOURCE_COUNTS = {source_counts_json};
        const TRACK_META = {track_meta_json};

        function switchTab(tabId) {{
            document.querySelectorAll('.tab-pane').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.nav-tab').forEach(el => el.classList.remove('active'));
            
            const target = document.getElementById(tabId);
            if (target) target.classList.add('active');

            const buttons = document.querySelectorAll('.nav-tabs .nav-tab');
            buttons.forEach(btn => {{
                if (btn.getAttribute('onclick') && btn.getAttribute('onclick').includes(tabId)) {{
                    btn.classList.add('active');
                }}
            }});
        }}

        function getSourceBadgeClass(src) {{
            if (src.includes('LinkedIn')) return 'src-linkedin';
            if (src.includes('ITviec')) return 'src-itviec';
            if (src.includes('CareerViet')) return 'src-careerviet';
            if (src.includes('VietnamWorks')) return 'src-vietnamworks';
            if (src.includes('Cyberjutsu')) return 'src-cyberjutsu';
            if (src.includes('CISSP')) return 'src-cissp';
            return 'src-linkedin';
        }}

        function populateDynamicFilters() {{
            const trackSelect = document.getElementById('trackFilterSelect');
            const sourceSelect = document.getElementById('sourceFilterSelect');

            // Count tracks directly from actual dataset
            const trackStats = {{}};
            JOBS_DATA.forEach(j => {{
                const t = j.track || 'An toàn Thông tin Chung';
                trackStats[t] = (trackStats[t] || 0) + 1;
            }});

            let trackHtml = `<option value="ALL">Tất cả nhóm ngành (${{JOBS_DATA.length}} việc làm)</option>`;
            Object.keys(trackStats).sort((a, b) => trackStats[b] - trackStats[a]).forEach(t => {{
                trackHtml += `<option value="${{t}}">${{t}} (${{trackStats[t]}} việc làm)</option>`;
            }});
            trackSelect.innerHTML = trackHtml;

            // Count sources directly from actual dataset
            const sourceStats = {{}};
            JOBS_DATA.forEach(j => {{
                const s = j.source || 'Khác';
                sourceStats[s] = (sourceStats[s] || 0) + 1;
            }});

            let sourceHtml = `<option value="ALL">Tất cả nguồn (${{Object.keys(sourceStats).length}} Nguồn - ${{JOBS_DATA.length}} việc làm)</option>`;
            Object.keys(sourceStats).sort((a, b) => sourceStats[b] - sourceStats[a]).forEach(s => {{
                sourceHtml += `<option value="${{s}}">${{s}} (${{sourceStats[s]}} việc làm)</option>`;
            }});
            sourceSelect.innerHTML = sourceHtml;
        }}

        function renderCharts() {{
            const ctxTrack = document.getElementById('trackPieChart').getContext('2d');
            const trackLabels = Object.keys(TRACK_COUNTS).map(t => t.split('/')[0].trim());
            const trackValues = Object.values(TRACK_COUNTS);

            new Chart(ctxTrack, {{
                type: 'doughnut',
                data: {{
                    labels: trackLabels,
                    datasets: [{{
                        data: trackValues,
                        backgroundColor: [
                            '#38bdf8', '#818cf8', '#34d399', '#c084fc', '#fb7185', '#fbbf24', '#f97316', '#64748b'
                        ],
                        borderColor: '#0a0f1d',
                        borderWidth: 2
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{
                            position: 'right',
                            labels: {{ color: '#cbd5e1', font: {{ size: 11 }} }}
                        }}
                    }}
                }}
            }});

            const ctxSource = document.getElementById('sourcePieChart').getContext('2d');
            const sourceLabels = Object.keys(SOURCE_COUNTS);
            const sourceValues = Object.values(SOURCE_COUNTS);

            new Chart(ctxSource, {{
                type: 'pie',
                data: {{
                    labels: sourceLabels,
                    datasets: [{{
                        data: sourceValues,
                        backgroundColor: [
                            '#0077b5', '#ea580c', '#4f46e5', '#0284c7', '#cf1337', '#d97706'
                        ],
                        borderColor: '#0a0f1d',
                        borderWidth: 2
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{
                            position: 'right',
                            labels: {{ color: '#cbd5e1', font: {{ size: 11 }} }}
                        }}
                    }}
                }}
            }});
        }}

        function renderTrackCards() {{
            const container = document.getElementById('trackCardContainer');
            let html = '';

            for (const [track, count] of Object.entries(TRACK_COUNTS)) {{
                const meta = TRACK_META[track] || {{}};
                const topCerts = meta.top_certs || ['Chứng chỉ chuyên ngành'];
                const roi = meta.roi_rating || 'Thu nhập hấp dẫn theo năng lực';

                html += `
                    <div class="track-card">
                        <div>
                            <div class="track-title-row">
                                <div class="track-title">${{track}}</div>
                                <div class="track-job-count">${{count}} JD</div>
                            </div>
                            <p style="font-size: 0.8rem; color: var(--accent-green); margin-bottom: 8px;">💰 ${{roi.split('(')[0]}}</p>
                        </div>
                        <div>
                            <div style="font-size: 0.75rem; color: var(--text-dim); text-transform: uppercase; font-weight: 700; margin-top: 8px;">Chứng chỉ & Tiêu chuẩn nổi bật</div>
                            <div class="pill-list">
                                ${{topCerts.slice(0, 3).map(c => `<span class="pill pill-accent">${{c}}</span>`).join('')}}
                            </div>
                        </div>
                    </div>
                `;
            }}
            container.innerHTML = html;
        }}

        function filterJobs() {{
            const search = (document.getElementById('jobSearchInput').value || '').toLowerCase().trim();
            const sourceFilter = document.getElementById('sourceFilterSelect').value;
            const trackFilter = document.getElementById('trackFilterSelect').value;

            const filtered = JOBS_DATA.filter(j => {{
                // 1. Keyword search match
                let matchSearch = true;
                if (search) {{
                    const fullText = (
                        (j.title || '') + ' ' +
                        (j.company || '') + ' ' +
                        (j.raw_description || '') + ' ' +
                        (j.location || '') + ' ' +
                        (j.tags || []).join(' ') + ' ' +
                        (j.extracted_skills || []).join(' ')
                    ).toLowerCase();
                    matchSearch = fullText.includes(search);
                }}

                // 2. Source filter match
                let matchSource = true;
                if (sourceFilter !== 'ALL') {{
                    matchSource = (j.source === sourceFilter) || (j.source && j.source.toLowerCase().includes(sourceFilter.toLowerCase()));
                }}

                // 3. Track filter match (Exact match + smart alias support)
                let matchTrack = true;
                if (trackFilter !== 'ALL') {{
                    if (j.track === trackFilter) {{
                        matchTrack = true;
                    }} else {{
                        // Fallback matching for legacy or substring
                        const tSel = trackFilter.toLowerCase();
                        const tJob = (j.track || '').toLowerCase();
                        if (tSel.includes('dfir') && (tJob.includes('dfir') || tJob.includes('forensic'))) {{
                            matchTrack = true;
                        }} else if (tSel.includes('cloud') && tJob.includes('cloud')) {{
                            matchTrack = true;
                        }} else if (tSel.includes('secops') && tJob.includes('secops')) {{
                            matchTrack = true;
                        }} else if (tSel.includes('appsec') && tJob.includes('appsec')) {{
                            matchTrack = true;
                        }} else if (tSel.includes('grc') && tJob.includes('grc')) {{
                            matchTrack = true;
                        }} else if (tSel.includes('pentest') && (tJob.includes('pentest') || tJob.includes('red team'))) {{
                            matchTrack = true;
                        }} else if (tSel.includes('soc') && tJob.includes('soc')) {{
                            matchTrack = true;
                        }} else {{
                            matchTrack = false;
                        }}
                    }}
                }}

                return matchSearch && matchSource && matchTrack;
            }});

            // Sort jobs: Default newest to oldest (thời gian gần đây nhất đến xa nhất)
            const sortOrder = document.getElementById('sortOrderSelect') ? document.getElementById('sortOrderSelect').value : 'newest';
            filtered.sort((a, b) => {{
                if (sortOrder === 'oldest') {{
                    return (a.posted_timestamp || 0) - (b.posted_timestamp || 0);
                }} else if (sortOrder === 'title') {{
                    return (a.title || '').localeCompare(b.title || '');
                }} else {{
                    // Default: newest first
                    return (b.posted_timestamp || 0) - (a.posted_timestamp || 0);
                }}
            }});

            document.getElementById('jobFilterCount').innerText = `${{filtered.length}} việc làm`;

            const container = document.getElementById('jobListContainer');
            if (filtered.length === 0) {{
                container.innerHTML = `<div style="text-align: center; padding: 3rem; color: var(--text-dim);">Không tìm thấy việc làm phù hợp với bộ lọc đã chọn. Vui lòng thử từ khóa khác hoặc chuyển sang "Tất cả nhóm ngành".</div>`;
                return;
            }}

            let html = '';
            filtered.forEach(j => {{
                const srcBadge = getSourceBadgeClass(j.source);
                const displayDate = j.posted_date_display || j.posted_date || 'Gần đây';
                html += `
                    <div class="job-card-item">
                        <div class="job-header-row">
                            <div>
                                <a href="${{j.url}}" target="_blank" class="job-title-link">${{j.title}}</a>
                                <div style="margin-top: 4px;">
                                    <span class="job-company">${{j.company}}</span> &bull; 
                                    <span style="color: var(--text-dim); font-size: 0.85rem;">📍 ${{j.location}}</span> &bull; 
                                    <span style="color: var(--accent-green); font-size: 0.85rem; font-weight: 600;">💰 ${{j.salary || 'Thỏa thuận'}}</span>
                                    <span style="color: #94a3b8; font-size: 0.82rem; margin-left: 6px; font-weight: 500;">📅 ${{displayDate}}</span>
                                </div>
                            </div>
                            <div style="text-align: right; display: flex; align-items: center; gap: 6px;">
                                <span class="badge badge-cyan">${{j.track}}</span>
                                <span class="source-badge ${{srcBadge}}">${{j.source}}</span>
                            </div>
                        </div>

                        <div class="job-snippet">${{j.raw_description}}</div>

                        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 8px; flex-wrap: wrap; gap: 8px;">
                            <div class="pill-list" style="margin-bottom: 0;">
                                ${{j.extracted_skills.map(s => `<span class="pill pill-accent">${{s}}</span>`).join('')}}
                                ${{j.extracted_certs.map(c => `<span class="pill" style="border-color: #f59e0b; color: #fbbf24;">${{c}}</span>`).join('')}}
                                ${{j.english_level && j.english_level !== 'Not Specified' ? `<span class="pill" style="color: var(--text-dim);">Tiếng Anh: ${{j.english_level}}</span>` : ''}}
                            </div>
                            <a href="${{j.url}}" target="_blank" style="color: var(--primary); font-size: 0.85rem; font-weight: 600; text-decoration: none;">Xem Chi Tiết / Ứng Tuyển ↗</a>
                        </div>
                    </div>
                `;
            }});
            container.innerHTML = html;
        }}

        window.addEventListener('DOMContentLoaded', () => {{
            populateDynamicFilters();
            renderCharts();
            renderTrackCards();
            filterJobs();
        }});
    </script>
</body>
</html>
"""
        with open(output_filepath, "w", encoding="utf-8") as f:
            f.write(html_template)
        
        index_path = os.path.join(os.path.dirname(os.path.abspath(output_filepath)), "index.html")
        if output_filepath != index_path:
            with open(index_path, "w", encoding="utf-8") as f:
                f.write(html_template)

        print(f"[DashboardGenerator] HTML reports generated at: {output_filepath} and {index_path}")
        return output_filepath
