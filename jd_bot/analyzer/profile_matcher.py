import os
from typing import Dict, List, Any
from jd_bot.crawlers.base_crawler import JobItem
from .cv_parser import CVParser

TRACK_REQUIREMENTS = {
    "Digital Forensics & Incident Response (DFIR)": {
        "priority_skills": [
            ("Incident Response", 3.0),
            ("Digital Forensics & Artifacts", 3.0),
            ("Memory Forensics (Volatility)", 2.5),
            ("Malware Analysis / Reverse Engineering", 3.0),
            ("Windows Internals & Artifacts", 2.0),
            ("Linux Administration", 2.0),
            ("Network Protocols", 1.5),
            ("Detection as Code / Sigma", 1.5)
        ],
        "transferable_from_duc": [
            "ĐÃ CÓ KINH NGHIỆM THỰC CHIẾN XỬ LÝ SỰ CỐ: Trực tiếp hỗ trợ DFIR cho Bệnh viện 1.000 giường & Ngân hàng thương mại",
            "Nắm vững bộ công cụ Forensics chuẩn quốc tế: Velociraptor, THOR Lite, Volatility, EZ Tools (MFTCmd, AmcacheParser, KAPE)",
            "Làm chủ quy trình Triage và chuỗi tấn công Cyber Kill Chain / MITRE ATT&CK",
            "Gốc Mạng và Hệ điều hành (Windows/Linux) vững chắc từ Học viện Kỹ thuật Mật mã (KMA)"
        ],
        "critical_gaps": [
            "Luận ngược mã độc chuyên sâu (Static/Dynamic Malware Analysis với IDA Pro, Ghidra, x64dbg để unpack malware/ransomware)",
            "Kỹ năng viết báo cáo sự cố bằng tiếng Anh chuẩn cho C-level / Khách hàng quốc tế (Incident Report)",
            "Tư duy chỉ huy sự cố (Incident Commander) và quản trị khủng hoảng cho toàn bộ tập đoàn",
            "Tự viết script parsing artifacts độc quyền bằng Python/Go mà không phụ thuộc AI"
        ],
        "top_certs": ["SANS GCFA (FOR508)", "SANS GREM (FOR610)", "SANS GCIH (SEC504)", "OffSec OSDF / OSCP"],
        "difficulty": "6 - 9 tháng (Trọng tâm: Reverse Engineering & Báo cáo tiếng Anh)",
        "roi_rating": "25M - 45M+ / tháng (Senior DFIR luôn được các tập đoàn & ngân hàng trả mức đãi ngộ rất cao)"
    },
    "SecOps Automation & Platform Engineering": {
        "priority_skills": [
            ("Python", 3.0),
            ("SOAR / Playbooks", 3.0),
            ("Detection as Code / Sigma", 2.5),
            ("REST API Integration", 2.5),
            ("SIEM Detection Tuning", 2.0),
            ("Log Analysis & Correlation", 2.0),
            ("Linux Administration", 1.5),
            ("Bash / Shell Scripting", 1.5)
        ],
        "transferable_from_duc": [
            "HIỂU RÕ QUY TRÌNH SOC: Lợi thế số 1 mà developer thuần túy không có",
            "Log Analysis & Correlation (Đã xử lý 1,000 alert/ca trực tại VNCERT)",
            "Tư duy phát hiện (Detection rules, Whitelist/Blacklist, Building Blocks)",
            "Hiểu biết sâu sắc về Windows/Linux artifacts và Event IDs"
        ],
        "critical_gaps": [
            "Viết Python/Go ở mức production (OOP, Async, API clients không phụ thuộc AI)",
            "Xây dựng Playbook tự động hóa trên SOAR (Shuffle - mã nguồn mở, hoặc Tines/Cortex)",
            "Triển khai Detection as Code (Quản lý Sigma rules qua Git và CI/CD)",
            "Tích hợp API giữa SIEM, EDR, Threat Intel và Ticket System (Jira)"
        ],
        "top_certs": ["Certified Detection Engineer", "Splunk Certified / Elastic Certified", "AWS Certified Security"],
        "difficulty": "Dễ tiếp cận nhất (3-5 tháng, tận dụng 80% kinh nghiệm hiện tại)",
        "roi_rating": "25M - 45M / tháng (Thoát kiếp trực ca đêm, trở thành kỹ sư nền tảng)"
    },
    "Cloud Security / DevSecOps": {
        "priority_skills": [
            ("AWS", 3.0),
            ("Azure", 2.5),
            ("Docker / Containers", 2.5),
            ("Kubernetes / K8s", 2.5),
            ("Terraform (IaC)", 2.5),
            ("CI/CD Pipelines", 2.0),
            ("Python", 2.0),
            ("Linux Administration", 2.0)
        ],
        "transferable_from_duc": [
            "Linux Administration (nền tảng tốt từ KMA & SOC)",
            "Network Protocols & Firewall/Routing (quan trọng khi cấu hình VPC/Security Groups)",
            "Tư duy phòng thủ & phát hiện xâm nhập (Incident response mindset)",
            "MITRE ATT&CK mapping (áp dụng cho Cloud Detection)"
        ],
        "critical_gaps": [
            "AWS / Azure IAM, Security Hub, GuardDuty, KMS, WAF",
            "Terraform (Infrastructure as Code) để quản lý cấu hình hạ tầng",
            "Docker containerization & Kubernetes cluster security",
            "CI/CD pipeline integration (GitLab CI / GitHub Actions) tích hợp quét lỗ hổng"
        ],
        "top_certs": ["AWS Certified Security - Specialty", "CKA (Kubernetes Admin) / CKS", "HashiCorp Terraform Associate"],
        "difficulty": "Vừa phải (6-8 tháng)",
        "roi_rating": "Cực cao (Lương 25M - 50M+ / tháng, nhu cầu thị trường rất lớn, không phải trực ca)"
    },
    "GRC & Compliance / IT Auditor": {
        "priority_skills": [
            ("ISO 27001", 3.0),
            ("VN Regulations (TT09/TT75/NĐ13)", 3.0),
            ("Risk Assessment", 2.5),
            ("PCI-DSS", 2.5),
            ("NIST CSF", 2.0),
            ("Security Architecture", 1.5)
        ],
        "transferable_from_duc": [
            "Kinh nghiệm hỗ trợ ứng cứu tại bệnh viện và ngân hàng (đã tiếp xúc thực tế với hệ thống lớn)",
            "Hiểu biết kỹ thuật sâu về kiểm soát log, access control, triage (hơn hẳn người làm GRC thuần luật/kinh tế)"
        ],
        "critical_gaps": [
            "Bộ tài liệu & quy trình ISO/IEC 27001:2022 (ISMS)",
            "Các quy định ngân hàng bắt buộc: Thông tư 09/2020/TT-NHNN, Thông tư 75, Nghị định 13",
            "Phương pháp đánh giá rủi ro (Risk Assessment methodology)",
            "Kỹ năng soạn thảo chính sách, quy chế và phỏng vấn đánh giá tuân thủ"
        ],
        "top_certs": ["ISO 27001 Lead Auditor", "CISA (Certified Information Systems Auditor)", "CRISC"],
        "difficulty": "Trung bình (4-6 tháng)",
        "roi_rating": "Rất ổn định (Giờ hành chính 100%, ngân hàng & Big 4 trả lương cao, không áp lực trực ca)"
    },
    "Pre-Sales & Security Solutions Architect": {
        "priority_skills": [
            ("Security Architecture", 3.0),
            ("Pre-Sales / PoC", 3.0),
            ("Zero Trust", 2.0),
            ("Network Protocols", 2.0),
            ("AWS", 1.5)
        ],
        "transferable_from_duc": [
            "Kinh nghiệm thực chiến tại VNCERT (hiểu rõ kẻ tấn công đánh như thế nào)",
            "Nắm rõ bức tranh giải pháp phòng thủ (SIEM, EDR, Log, Sandbox, Firewall)"
        ],
        "critical_gaps": [
            "Kỹ năng thuyết trình, pitching giải pháp trước C-level / khách hàng",
            "Bóc tách yêu cầu kỹ thuật làm hồ sơ thầu (RFP/RFI), lập bảng BoQ/BoM chi phí",
            "Tiếng Anh giao tiếp & trình bày giải pháp với Vendor quốc tế"
        ],
        "top_certs": ["Palo Alto PCNSE", "Fortinet NSE4+", "AWS Solutions Architect Associate"],
        "difficulty": "Trung bình - Khá (Cần rèn soft skills & tiếng Anh)",
        "roi_rating": "Rất cao (Lương cứng + Thưởng hoa hồng dự án lớn tại SI/Vendor)"
    },
    "AppSec / Product Security": {
        "priority_skills": [
            ("SAST / DAST", 3.0),
            ("OWASP Top 10", 3.0),
            ("Secure Code Review", 2.5),
            ("Burp Suite Pro", 2.5),
            ("Threat Modeling", 2.0),
            ("CI/CD Pipelines", 1.5),
            ("Python", 1.5)
        ],
        "transferable_from_duc": [
            "Đã biết đọc hiểu code (C, Python, Java, JS)",
            "Nắm khái niệm OWASP cơ bản",
            "Tư duy phân tích nguyên nhân gốc (Root cause analysis)"
        ],
        "critical_gaps": [
            "Thực hành khai thác Web/API nâng cao bằng Burp Suite Pro",
            "Triển khai công cụ SAST/DAST/SCA (SonarQube, Snyk, Semgrep) vào CI/CD",
            "Kỹ năng Review mã nguồn để chỉ ra dòng code lỗi và viết code vá mẫu cho Dev",
            "Phương pháp mô hình hóa mối đe dọa (Threat Modeling với STRIDE)"
        ],
        "top_certs": ["Burp Suite Certified Practitioner (BSCP)", "OffSec Web Expert (OSWE)", "Practical DevSecOps"],
        "difficulty": "Trung bình - Khá (6-9 tháng)",
        "roi_rating": "Cao (Rất chuộng ở các công ty Product, Fintech, SaaS quốc tế)"
    },
    "Offensive Security (Pentest / Red Team)": {
        "priority_skills": [
            ("Penetration Testing", 3.0),
            ("Burp Suite Pro", 2.5),
            ("Active Directory Security", 2.5),
            ("Python", 2.0),
            ("Network Protocols", 1.5)
        ],
        "transferable_from_duc": [
            "Hiểu biết Blue Team giúp né được các detection rule",
            "Kiến thức Windows/Linux Internals từ KMA và xử lý sự cố"
        ],
        "critical_gaps": [
            "Khai thác lỗ hổng Web/API chuyên sâu",
            "Kỹ thuật tấn công Active Directory (Kerberoasting, Pass-the-Hash, DCSync)",
            "Khai thác leo quyền (Privilege Escalation trên Windows/Linux)"
        ],
        "top_certs": ["OSCP", "PNPT (TCM Security)", "CRTP (Certified Red Team Professional)"],
        "difficulty": "Khá cao (Đòi hỏi cày lab Proving Grounds / HackTheBox kiên trì)",
        "roi_rating": "Tốt nhưng cạnh tranh nhiều ở phân khúc Junior/Mid"
    }
}

class ProfileMatcher:
    def __init__(self, candidate_profile: Dict[str, Any] = None):
        self.profile = candidate_profile or CVParser.get_default_profile()

    def evaluate_tracks(self, crawled_jobs: List[JobItem]) -> Dict[str, Any]:
        track_stats = {}
        user_skills_lower = [s.lower() for s in self.profile.get("current_skills", [])]

        for track_name, reqs in TRACK_REQUIREMENTS.items():
            matching_jobs = [j for j in crawled_jobs if j.track == track_name]
            
            skill_freq = {}
            cert_freq = {}
            for j in matching_jobs:
                for s in j.extracted_skills:
                    skill_freq[s] = skill_freq.get(s, 0) + 1
                for c in j.extracted_certs:
                    cert_freq[c] = cert_freq.get(c, 0) + 1

            total_weight = sum(weight for _, weight in reqs["priority_skills"])
            candidate_score = 0
            
            for skill_name, weight in reqs["priority_skills"]:
                s_low = skill_name.lower()
                matched = False
                for curr in user_skills_lower:
                    if s_low in curr or curr in s_low:
                        matched = True
                        break
                    # Broad semantic matches
                    if "incident" in s_low and ("incident" in curr or "dfir" in curr or "ứng cứu" in curr):
                        matched = True
                        break
                    if "forensic" in s_low and ("forensic" in curr or "volatility" in curr or "velociraptor" in curr or "ez tools" in curr):
                        matched = True
                        break
                    if "memory" in s_low and ("memory" in curr or "volatility" in curr):
                        matched = True
                        break
                    if "artifact" in s_low and ("artifact" in curr or "ez tools" in curr or "windows" in curr or "linux" in curr):
                        matched = True
                        break
                    if "linux" in s_low and "linux" in curr:
                        matched = True
                        break
                    if "network" in s_low and "network" in curr:
                        matched = True
                        break
                    if "siem" in s_low and "siem" in curr:
                        matched = True
                        break
                    if "log" in s_low and "log" in curr:
                        matched = True
                        break
                    if "python" in s_low and "python" in curr:
                        matched = True
                        candidate_score += weight * 0.7
                        break

                if matched and "python" not in s_low:
                    candidate_score += weight

            match_pct = round((candidate_score / total_weight) * 100) if total_weight > 0 else 50
            # Add baseline education / practical experience bonus
            match_pct = min(96, match_pct + 10)

            # Special bonus for DFIR if candidate has actual hospital/bank incident response
            if "DFIR" in track_name and any("incident" in s for s in user_skills_lower):
                match_pct = max(match_pct, 86)

            track_stats[track_name] = {
                "track_name": track_name,
                "job_count": len(matching_jobs),
                "match_score": match_pct,
                "difficulty": reqs["difficulty"],
                "roi_rating": reqs["roi_rating"],
                "transferable_skills": reqs["transferable_from_duc"],
                "critical_gaps": reqs["critical_gaps"],
                "top_certs": reqs["top_certs"],
                "skill_frequency": sorted(skill_freq.items(), key=lambda x: x[1], reverse=True)[:6],
                "cert_frequency": sorted(cert_freq.items(), key=lambda x: x[1], reverse=True)[:4]
            }

        return track_stats
