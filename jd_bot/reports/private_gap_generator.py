import json
import os
from typing import Dict, List, Any
from jd_bot.crawlers.base_crawler import JobItem

class PrivateGapGenerator:
    @staticmethod
    def generate_private_dashboard(
        crawled_jobs: List[JobItem],
        track_analysis: Dict[str, Any],
        roadmaps: Dict[str, Any],
        candidate_profile: Dict[str, Any],
        output_filepath: str = "user_profiles/private_gap_analysis.html"
    ) -> str:
        jobs_json = json.dumps([j.to_dict() for j in crawled_jobs], ensure_ascii=False)
        analysis_json = json.dumps(track_analysis, ensure_ascii=False)
        roadmaps_json = json.dumps(roadmaps, ensure_ascii=False)
        profile_json = json.dumps(candidate_profile or {}, ensure_ascii=False)

        total_jobs = len(crawled_jobs)
        candidate_name = candidate_profile.get("name", "Nguyễn Thành Đức")
        candidate_role = candidate_profile.get("current_role", "SOC Analyst Tier 2")

        html_template = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Báo Cáo Phân Tích Kỹ Năng & Lộ Trình Riêng Tư | {candidate_name}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --bg-main: #0a0f1d;
            --bg-card: rgba(18, 26, 47, 0.75);
            --border-card: rgba(255, 255, 255, 0.08);
            --border-glow: rgba(56, 189, 248, 0.3);
            --primary: #38bdf8;
            --secondary: #818cf8;
            --accent-green: #34d399;
            --accent-rose: #fb7185;
            --accent-amber: #fbbf24;
            --text-main: #f1f5f9;
            --text-muted: #94a3b8;
            --text-dim: #64748b;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: 'Plus Jakarta Sans', sans-serif;
            background-color: var(--bg-main);
            color: var(--text-main);
            min-height: 100vh;
            line-height: 1.6;
            padding: 2rem;
        }}
        .header-box {{
            max-width: 1200px;
            margin: 0 auto 2rem;
            background: rgba(18, 26, 47, 0.9);
            border: 1px solid var(--border-card);
            border-radius: 16px;
            padding: 1.5rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1rem;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .card {{
            background: var(--bg-card);
            border: 1px solid var(--border-card);
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 2rem;
        }}
        .nav-tabs {{
            display: flex; gap: 10px; margin-bottom: 1.5rem; flex-wrap: wrap;
        }}
        .nav-tab {{
            padding: 10px 20px; border-radius: 8px; border: 1px solid var(--border-card);
            background: rgba(255, 255, 255, 0.05); color: var(--text-muted);
            cursor: pointer; font-weight: 600;
        }}
        .nav-tab.active {{
            background: var(--primary); color: #000; border-color: var(--primary);
        }}
        .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }}
        @media (max-width: 800px) {{ .grid-2 {{ grid-template-columns: 1fr; }} }}
        .task-list {{ list-style: none; margin-top: 8px; }}
        .task-list li {{ margin-bottom: 6px; padding-left: 1.2rem; position: relative; color: #cbd5e1; font-size: 0.9rem; }}
        .task-list li::before {{ content: '▹'; position: absolute; left: 0; color: var(--primary); }}
        .timeline-step {{ margin-bottom: 1.5rem; padding: 1.2rem; background: rgba(255, 255, 255, 0.02); border-radius: 12px; border: 1px solid var(--border-card); }}
        .timeline-title {{ font-weight: 700; color: var(--primary); font-size: 1.05rem; margin-bottom: 4px; }}
    </style>
</head>
<body>
    <div class="header-box">
        <div>
            <h1 style="font-size: 1.4rem; color: #fff;">🔒 Báo Cáo Phân Tích Kỹ Năng & Lộ Trình Cá Nhân (Private)</h1>
            <p style="color: var(--text-muted); font-size: 0.85rem;">File nội bộ cá nhân trên máy của {candidate_name} &bull; Đối chiếu từ {total_jobs} tin tuyển dụng thực tế</p>
        </div>
        <div style="background: rgba(56, 189, 248, 0.1); border: 1px solid var(--primary); padding: 6px 14px; border-radius: 8px; color: var(--primary); font-weight: 700;">
            {candidate_role}
        </div>
    </div>

    <div class="container">
        <!-- Radar Chart -->
        <div class="card">
            <h2 style="font-size: 1.2rem; margin-bottom: 1rem; color: #fff;">🎯 Ma Trận Độ Tương Thích Kỹ Năng (Fit Score)</h2>
            <div style="height: 380px; position: relative;">
                <canvas id="radarChart"></canvas>
            </div>
        </div>

        <!-- Gap Analysis Section -->
        <div class="card">
            <h2 style="font-size: 1.2rem; margin-bottom: 1rem; color: #fff;">🔍 Phân Tích Khoảng Cách Kỹ Năng (Gap Analysis)</h2>
            <div id="gapContainer"></div>
        </div>

        <!-- Roadmap Section -->
        <div class="card">
            <h2 style="font-size: 1.2rem; margin-bottom: 1rem; color: #fff;">🗺️ Lộ Trình Phát Triển Chi Tiết Từng Tháng</h2>
            <div class="nav-tabs" id="roadmapTabs"></div>
            <div id="roadmapContent"></div>
        </div>
    </div>

    <script>
        const ANALYSIS_DATA = {analysis_json};
        const ROADMAPS_DATA = {roadmaps_json};

        // Render Radar
        const ctx = document.getElementById('radarChart').getContext('2d');
        const labels = Object.keys(ANALYSIS_DATA).map(t => t.split('/')[0].trim());
        const scores = Object.values(ANALYSIS_DATA).map(d => d.match_score);

        new Chart(ctx, {{
            type: 'radar',
            data: {{
                labels: labels,
                datasets: [{{
                    label: 'Fit Score (%)',
                    data: scores,
                    backgroundColor: 'rgba(56, 189, 248, 0.25)',
                    borderColor: '#38bdf8',
                    pointBackgroundColor: '#38bdf8',
                    borderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    r: {{
                        angleLines: {{ color: 'rgba(255, 255, 255, 0.1)' }},
                        grid: {{ color: 'rgba(255, 255, 255, 0.08)' }},
                        pointLabels: {{ color: '#cbd5e1', font: {{ size: 11 }} }},
                        ticks: {{ display: false, min: 0, max: 100 }}
                    }}
                }}
            }}
        }});

        // Render Gaps
        let gapHtml = '';
        for (const [track, data] of Object.entries(ANALYSIS_DATA)) {{
            gapHtml += `
                <div style="background: rgba(255, 255, 255, 0.02); border: 1px solid var(--border-card); border-radius: 12px; padding: 1.25rem; margin-bottom: 1.25rem;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                        <strong style="color: #fff; font-size: 1.05rem;">${{track}}</strong>
                        <span style="color: var(--primary); font-weight: 700;">${{data.match_score}}% Fit</span>
                    </div>
                    <div class="grid-2">
                        <div>
                            <strong style="color: var(--accent-green); font-size: 0.85rem;">✓ Điểm mạnh có sẵn:</strong>
                            <ul class="task-list">
                                ${{data.transferable_skills.map(s => `<li>${{s}}</li>`).join('')}}
                            </ul>
                        </div>
                        <div>
                            <strong style="color: var(--accent-rose); font-size: 0.85rem;">✕ Lỗ hổng cần học:</strong>
                            <ul class="task-list">
                                ${{data.critical_gaps.map(g => `<li style="color: #fca5a5;">${{g}}</li>`).join('')}}
                            </ul>
                        </div>
                    </div>
                </div>
            `;
        }}
        document.getElementById('gapContainer').innerHTML = gapHtml;

        // Render Roadmaps
        const roadmapKeys = Object.keys(ROADMAPS_DATA);
        let tabHtml = '';
        roadmapKeys.forEach((k, idx) => {{
            tabHtml += `<button class="nav-tab ${{idx === 0 ? 'active' : ''}}" onclick="showRoadmap('${{k}}', this)">${{ROADMAPS_DATA[k].title.split(':')[1] || k}}</button>`;
        }});
        document.getElementById('roadmapTabs').innerHTML = tabHtml;

        function showRoadmap(key, btn) {{
            document.querySelectorAll('#roadmapTabs .nav-tab').forEach(b => b.classList.remove('active'));
            if (btn) btn.classList.add('active');
            const data = ROADMAPS_DATA[key];
            if (!data) return;

            let html = `<p style="color: var(--accent-amber); font-weight: 600; margin-bottom: 1rem;">Thời gian: ${{data.target_timeline}}</p>`;
            data.phases.forEach(p => {{
                html += `
                    <div class="timeline-step">
                        <div class="timeline-title">${{p.phase}}</div>
                        <div style="font-size: 0.85rem; color: var(--accent-green); margin-bottom: 6px;">Trọng tâm: ${{p.focus}}</div>
                        <ul class="task-list">
                            ${{p.tasks.map(t => `<li>${{t}}</li>`).join('')}}
                        </ul>
                    </div>
                `;
            }});
            document.getElementById('roadmapContent').innerHTML = html;
        }}

        if (roadmapKeys.length > 0) showRoadmap(roadmapKeys[0]);
    </script>
</body>
</html>
"""
        os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
        with open(output_filepath, "w", encoding="utf-8") as f:
            f.write(html_template)
        print(f"[PrivateGapGenerator] Local private gap & roadmap saved at: {output_filepath}")
        return output_filepath
