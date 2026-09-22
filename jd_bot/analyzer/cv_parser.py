import os
import re
import json
from typing import Dict, Any, List

class CVParser:
    @staticmethod
    def extract_text_from_pdf(pdf_path: str) -> str:
        text = ""
        try:
            import pymupdf
            doc = pymupdf.open(pdf_path)
            for page in doc:
                text += page.get_text() + "\n"
            return text
        except Exception:
            pass

        try:
            import pypdf
            reader = pypdf.PdfReader(pdf_path)
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    text += t + "\n"
            return text
        except Exception as e:
            print(f"[CVParser] Error extracting PDF {pdf_path}: {e}")
            return ""

    @classmethod
    def parse_cv_file(cls, filepath: str) -> Dict[str, Any]:
        if not os.path.exists(filepath):
            print(f"[CVParser] File {filepath} not found, falling back to default profile.")
            return cls.get_default_profile()

        if filepath.endswith(".json"):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[CVParser] Error reading JSON profile: {e}")

        raw_text = ""
        if filepath.endswith(".pdf"):
            raw_text = cls.extract_text_from_pdf(filepath)
        else:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    raw_text = f.read()
            except Exception:
                with open(filepath, "r", encoding="latin-1") as f:
                    raw_text = f.read()

        if not raw_text.strip():
            return cls.get_default_profile()

        return cls.parse_raw_text(raw_text, source_file=filepath)

    @classmethod
    def parse_raw_text(cls, text: str, source_file: str = "") -> Dict[str, Any]:
        lower = text.lower()

        # Name extraction (usually first line or near start)
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        name = lines[0] if lines else "Ứng viên ATTT"
        if len(name) > 40 or any(kw in name.lower() for kw in ["curriculum", "resume", "cv", "thông tin", "kinh nghiệm"]):
            name = "Nguyễn Thành Đức"

        # Current role
        role = "Chuyên viên ATTT / SOC Tier 2"
        for line in lines[:10]:
            if any(r in line.lower() for r in ["soc", "analyst", "tier 2", "tier 1", "engineer", "dfir", "chuyên viên", "kỹ sư"]):
                role = line
                break

        # Education
        education = "Đại học / Chuyên ngành An toàn Thông tin"
        if "kma" in lower or "mật mã" in lower or "cryptography" in lower:
            education = "Học viện Kỹ thuật Mật mã (KMA) - An toàn Thông tin"
        elif "bách khoa" in lower or "hust" in lower:
            education = "Đại học Bách Khoa Hà Nội"
        elif "fpt" in lower:
            education = "Đại học FPT - An toàn Thông tin"

        # English level
        english = "Elementary / Basic Reading"
        if any(w in lower for w in ["fluent", "toeic 800", "ielts 7.0", "chuyên nghiệp"]):
            english = "Fluent / Professional"
        elif any(w in lower for w in ["intermediate", "giao tiếp tốt", "toeic 650", "ielts 6.0"]):
            english = "Intermediate"
        elif any(w in lower for w in ["basic", "cơ bản", "reading", "đọc hiểu"]):
            english = "Elementary / Basic Reading"

        # Years of experience
        years_exp = "2+ năm kinh nghiệm"
        if any(w in lower for w in ["tier 2", "2 năm", "2024", "2025"]):
            years_exp = "2 - 3 năm kinh nghiệm (SOC Tier 2 & DFIR support)"

        # Skill detection dictionary
        SKILL_DICTIONARY = {
            "Velociraptor": r"\bvelociraptor\b",
            "THOR / THOR Lite": r"\bthor\b",
            "Volatility": r"\bvolatility\b",
            "Eric Zimmerman Tools (EZ Tools)": r"\b(ez tools|eric zimmerman|mftcmd|amcacheparser)\b",
            "Windows Internals & Artifacts": r"\b(windows|shimcache|amcache|mft|event id)\b",
            "Linux Administration": r"\b(linux|ubuntu|centos|systemd)\b",
            "Network Protocols": r"\b(network|wireshark|packet|tcp/ip|firewall|dns)\b",
            "SIEM Detection Tuning": r"\b(siem|rule|whitelist|blacklist|building block|qradar|splunk|elastic)\b",
            "Log Analysis & Correlation": r"\b(log|alert|correlation|triage)\b",
            "MITRE ATT&CK": r"\bmitre\b",
            "OWASP Top 10": r"\bowasp\b",
            "Memory Forensics": r"\b(memory forensics|dumpit|winpmem|avml)\b",
            "Incident Response Support": r"\b(incident response|dfir|ứng cứu|xử lý sự cố)\b",
            "Reverse Engineering": r"\b(reverse engineering|ghidra|ida pro|x64dbg|malware analysis)\b",
            "Python": r"\bpython\b",
            "Golang": r"\b(golang|go)\b",
            "C / C++": r"\b(c\+\+|c language)\b",
            "Java": r"\bjava\b",
            "JavaScript": r"\b(javascript|js)\b",
            "Docker": r"\bdocker\b",
            "Kubernetes": r"\b(kubernetes|k8s)\b",
            "Terraform": r"\bterraform\b",
            "AWS": r"\b(aws|amazon web services)\b",
            "Azure": r"\bazure\b",
            "ISO 27001": r"\biso 27001\b",
            "PCI-DSS": r"\bpci-dss\b"
        }

        detected_skills = []
        for skill_name, pattern in SKILL_DICTIONARY.items():
            if re.search(pattern, lower):
                detected_skills.append(skill_name)

        # Build limitations and strengths
        limitations = []
        if "AWS" not in detected_skills and "Azure" not in detected_skills:
            limitations.append("Chưa có kinh nghiệm Cloud chuyên sâu (AWS/Azure/GCP)")
        if "Terraform" not in detected_skills:
            limitations.append("Chưa có kinh nghiệm Infrastructure as Code (Terraform)")
        if "Kubernetes" not in detected_skills and "Docker" not in detected_skills:
            limitations.append("Chưa thành thạo Container Security (Docker, Kubernetes)")
        if "Reverse Engineering" not in detected_skills:
            limitations.append("Chưa có kinh nghiệm Phân tích mã độc / Reverse Engineering (IDA, Ghidra)")
        if english == "Elementary / Basic Reading":
            limitations.append("Tiếng Anh giao tiếp và viết báo cáo C-level còn hạn chế")

        return {
            "name": name,
            "education": education,
            "current_role": role,
            "years_experience": years_exp,
            "english_level": english,
            "current_skills": detected_skills if detected_skills else [
                "Network Protocols", "Windows Internals", "Linux Administration",
                "Log Analysis", "SIEM Detection", "Incident Response Support", "Python (Basic)"
            ],
            "known_limitations": limitations,
            "source_file": source_file if source_file else "Generated"
        }

    @staticmethod
    def get_default_profile() -> Dict[str, Any]:
        return {
            "name": "Nguyễn Thành Đức",
            "education": "Học viện Kỹ thuật Mật mã (KMA) - An toàn Thông tin",
            "current_role": "SOC Analyst Tier 2 tại VNCERT",
            "years_experience": "2+ năm (VSEC Intern -> Tier 1 VNCERT -> Tier 2 VNCERT)",
            "english_level": "Elementary / Basic Reading",
            "current_skills": [
                "Network Protocols", "Windows Internals", "Linux Administration",
                "MITRE ATT&CK", "OWASP Top 10", "Log Analysis & Correlation",
                "SIEM Detection Tuning", "Artifact Triage (Velociraptor, THOR, EZ Tools)",
                "Memory Forensics (Volatility, WinPmem)", "Python (Basic / AI Scripting)",
                "C", "Java (Basic)", "JavaScript (Basic)", "Incident Response Support"
            ],
            "known_limitations": [
                "Chưa có kinh nghiệm Cloud sâu (AWS/Azure/GCP)",
                "Chưa có kinh nghiệm IaC (Terraform) và Container (Docker/Kubernetes)",
                "Chưa thành thạo Luận ngược mã độc / Reverse Engineering (IDA Pro, Ghidra)",
                "Chưa có chứng chỉ quốc tế uy tín",
                "Tiếng Anh giao tiếp/viết báo cáo C-level còn hạn chế"
            ]
        }
