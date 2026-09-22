import re
from typing import Dict, List, Any, Tuple
from jd_bot.crawlers.base_crawler import JobItem
from jd_bot.analyzer.date_utils import DateUtils

CAREER_TRACKS = {
    "Digital Forensics & Incident Response (DFIR)": {
        "keywords": [
            "dfir", "digital forensics", "forensic", "incident response", "điều tra số",
            "xử lý sự cố", "ứng cứu sự cố", "malware analysis", "phân tích mã độc",
            "reverse engineering", "volatility", "velociraptor", "memory forensics", "yara",
            "incident commander", "forensics investigator"
        ],
        "weight": 1.3
    },
    "Cloud Security / DevSecOps": {
        "keywords": [
            "cloud security", "devsecops", "aws security", "azure security", "gcp security",
            "terraform", "kubernetes security", "k8s security", "container security",
            "ci/cd security", "pipeline security", "cspm", "cwpp", "iac", "cloud & network security"
        ],
        "weight": 1.2
    },
    "SecOps Automation & Platform Engineering": {
        "keywords": [
            "secops", "detection engineering", "soar", "security automation", "detection as code",
            "sigma rule", "shuffle", "tines", "cortex xsoar", "siem engineer", "siem admin",
            "security platform", "elastic engineer", "splunk engineer"
        ],
        "weight": 1.2
    },
    "AppSec / Product Security": {
        "keywords": [
            "application security", "appsec", "product security", "sast", "dast",
            "secure code review", "threat modeling", "stride", "ssdlc", "sonarqube",
            "checkmarx", "snyk", "owasp", "burp suite"
        ],
        "weight": 1.2
    },
    "GRC & Compliance / IT Auditor": {
        "keywords": [
            "grc", "governance", "compliance", "tuân thủ", "it audit", "kiểm toán it",
            "iso 27001", "iso/iec 27001", "pci-dss", "pci dss", "nist", "thông tư 09",
            "thông tư 75", "nghị định 13", "risk assessment", "đánh giá rủi ro", "chính sách an toàn"
        ],
        "weight": 1.2
    },
    "Pre-Sales & Security Solutions Architect": {
        "keywords": [
            "solution architect", "pre-sales", "presales", "tư vấn giải pháp", "security architect",
            "consultant", "chuyên gia tư vấn", "kiến trúc an toàn", "boq", "rfp", "poc"
        ],
        "weight": 1.15
    },
    "Offensive Security (Pentest / Red Team)": {
        "keywords": [
            "penetration test", "pentest", "red team", "offensive security", "ethical hacker",
            "web pentest", "mobile pentest", "kiểm thử xâm nhập", "active directory attack"
        ],
        "weight": 1.15
    },
    "SOC Operations & Monitoring": {
        "keywords": [
            "soc tier", "soc analyst", "soc lead", "trực soc", "giám sát an ninh", "ca trực soc",
            "alert monitoring", "l1 analyst", "l2 analyst", "trực ca soc"
        ],
        "weight": 1.0
    }
}

TAG_ROLE_MAP = {
    "Reverse Engineering / Malware Analysis": "Digital Forensics & Incident Response (DFIR)",
    "Penetration Testing / Red Team": "Offensive Security (Pentest / Red Team)",
    "Cloud & Network Security": "Cloud Security / DevSecOps",
    "DevSecOps / Application Security": "AppSec / Product Security",
    "GRC / Tuân thủ & Quản trị Rủi ro": "GRC & Compliance / IT Auditor",
    "SOC / Blue Team / Threat Monitoring": "SOC Operations & Monitoring"
}

SKILL_PATTERNS = {
    # Forensics & DFIR
    "Digital Forensics & Artifacts": r"\b(forensic|forensics|velociraptor|ez tools|mft|amcache|shimcache|registry)\b",
    "Memory Forensics (Volatility)": r"\b(volatility|winpmem|dumpit|memory analysis)\b",
    "Malware Analysis / Reverse Engineering": r"\b(malware analysis|reverse engineering|ida pro|ghidra|x64dbg|unpack)\b",
    "Incident Response": r"\b(incident response|dfir|ứng cứu sự cố|xử lý sự cố)\b",

    # Cloud & DevOps
    "AWS": r"\b(aws|amazon web services)\b",
    "Azure": r"\b(azure|microsoft azure)\b",
    "GCP": r"\b(gcp|google cloud)\b",
    "Kubernetes / K8s": r"\b(kubernetes|k8s)\b",
    "Docker / Containers": r"\b(docker|containerization|containers)\b",
    "Terraform (IaC)": r"\b(terraform|iac|infrastructure as code)\b",
    "CI/CD Pipelines": r"\b(ci/cd|jenkins|gitlab ci|github actions)\b",
    
    # AppSec
    "SAST / DAST": r"\b(sast|dast|iast)\b",
    "Secure Code Review": r"\b(secure code review|code audit|rà soát mã nguồn)\b",
    "Threat Modeling": r"\b(threat model|threat modeling|stride)\b",
    "Burp Suite Pro": r"\b(burp suite|burpsuite)\b",
    "SonarQube / Snyk": r"\b(sonarqube|snyk|checkmarx|fortify)\b",
    "OWASP Top 10": r"\b(owasp|owasp top 10)\b",

    # Automation & Tooling
    "Python": r"\b(python|python3)\b",
    "Golang": r"\b(golang|go)\b",
    "Bash / Shell Scripting": r"\b(bash|powershell|shell script)\b",
    "SOAR / Playbooks": r"\b(soar|playbook|shuffle|tines|xsoar)\b",
    "Detection as Code / Sigma": r"\b(detection engineering|sigma rule|detection as code)\b",
    "REST API Integration": r"\b(api|rest api|webhook)\b",

    # GRC & Regulations
    "ISO 27001": r"\b(iso 27001|iso/iec 27001|iso27001)\b",
    "PCI-DSS": r"\b(pci-dss|pci dss)\b",
    "NIST CSF": r"\b(nist|nist csf|nist 800)\b",
    "VN Regulations (TT09/TT75/NĐ13)": r"\b(thông tư 09|thông tư 75|nghị định 13|luật an ninh mạng|sbv)\b",
    "Risk Assessment": r"\b(risk assessment|đánh giá rủi ro|quản lý rủi ro)\b",

    # Pre-Sales & Architecture
    "Security Architecture": r"\b(security architecture|kiến trúc an toàn|kiến trúc bảo mật)\b",
    "Pre-Sales / PoC": r"\b(pre-sales|presales|poc|bảo vệ giải pháp|rfi|rfp)\b",
    "Zero Trust": r"\b(zero trust|ztna)\b",

    # Offsec
    "Penetration Testing": r"\b(pentest|penetration test|kiểm thử xâm nhập)\b",
    "Active Directory Security": r"\b(active directory|ad attack|kerberos|bloodhound)\b"
}

CERT_PATTERNS = {
    "SANS GCFA / GCIH / GREM": r"\b(gcfa|gcih|grem|for500|for508|for610|sans)\b",
    "AWS Certified Security": r"\b(aws.*security|aws security specialty|scs-c0[12])\b",
    "CKA / CKS": r"\b(cka|cks|certified kubernetes)\b",
    "Terraform Associate": r"\b(terraform associate)\b",
    "OSCP / OSDF": r"\b(oscp|osdf|offensive security certified)\b",
    "BSCP (Burp Suite)": r"\b(bscp|burp suite certified)\b",
    "CEH": r"\b(ceh|certified ethical hacker)\b",
    "CompTIA Security+ / CySA+": r"\b(security\+|cysa\+|casp\+)\b",
    "CISSP": r"\b(cissp)\b",
    "CISA / CRISC": r"\b(cisa|crisc)\b",
    "ISO 27001 Lead Auditor / Implementer": r"\b(iso 27001 la|lead auditor|lead implementer)\b"
}

class JDExtractor:
    @staticmethod
    def classify_track(text: str, title: str, tags: List[str] = None) -> str:
        # 1. Prioritize explicit Title markers
        title_lower = title.lower()
        if "dfir" in title_lower or "ứng cứu sự cố" in title_lower or "điều tra" in title_lower or "forensic" in title_lower or "malware" in title_lower:
            return "Digital Forensics & Incident Response (DFIR)"
        if "pentest" in title_lower or "penetration" in title_lower or "red team" in title_lower or "kiểm thử xâm nhập" in title_lower:
            return "Offensive Security (Pentest / Red Team)"
        if "devsecops" in title_lower or "cloud security" in title_lower:
            return "Cloud Security / DevSecOps"
        if "appsec" in title_lower or "application security" in title_lower or "product security" in title_lower:
            return "AppSec / Product Security"
        if "grc" in title_lower or "tuân thủ" in title_lower or "compliance" in title_lower or "kiểm toán" in title_lower:
            return "GRC & Compliance / IT Auditor"
        if "pre-sales" in title_lower or "presale" in title_lower or "solution architect" in title_lower or "tư vấn giải pháp" in title_lower:
            return "Pre-Sales & Security Solutions Architect"
        if "soar" in title_lower or "detection engineer" in title_lower or "secops" in title_lower:
            return "SecOps Automation & Platform Engineering"

        # 2. Check tag role group mappings if available
        if tags:
            for t in tags:
                if t in TAG_ROLE_MAP:
                    return TAG_ROLE_MAP[t]

        # 3. Score-based matching on text
        combined = f"{title} {title} {title} {text}".lower()
        track_scores = {}
        for track, config in CAREER_TRACKS.items():
            score = 0
            for kw in config["keywords"]:
                if kw in combined:
                    in_title = kw in title_lower
                    weight = 5 if in_title else 1
                    score += weight
            track_scores[track] = score * config["weight"]

        best_track = max(track_scores, key=track_scores.get)
        if track_scores[best_track] == 0:
            return "An toàn Thông tin Chung"
        return best_track

    @staticmethod
    def extract_skills(text: str) -> List[str]:
        found = []
        lower_text = text.lower()
        for skill_name, pattern in SKILL_PATTERNS.items():
            if re.search(pattern, lower_text, re.IGNORECASE):
                found.append(skill_name)
        return found

    @staticmethod
    def extract_certs(text: str) -> List[str]:
        found = []
        lower_text = text.lower()
        for cert_name, pattern in CERT_PATTERNS.items():
            if re.search(pattern, lower_text, re.IGNORECASE):
                found.append(cert_name)
        return found

    @staticmethod
    def extract_english_level(text: str) -> str:
        lower = text.lower()
        if any(term in lower for term in ["fluent english", "excellent english", "tiếng anh lưu loát", "toeic 750", "ielts 6.5", "working with foreign", "global team"]):
            return "Fluent / Advanced"
        elif any(term in lower for term in ["good english", "tiếng anh giao tiếp tốt", "toeic 600", "ielts 5.5", "intermediate english"]):
            return "Intermediate"
        elif any(term in lower for term in ["reading english", "đọc hiểu tiếng anh", "basic english", "tiếng anh cơ bản"]):
            return "Basic Reading"
        return "Not Specified"

    @staticmethod
    def extract_experience_level(title: str, text: str) -> str:
        lower = f"{title} {text}".lower()
        if any(term in lower for term in ["principal", "lead", "trưởng nhóm", "manager", "head of", "director"]):
            return "Lead / Manager"
        elif any(term in lower for term in ["senior", "expert", "chuyên gia", "5+ years", "4+ years", "5 năm"]):
            return "Senior"
        elif any(term in lower for term in ["junior", "fresher", "intern", "dưới 2 năm", "1-2 năm", "1 năm"]):
            return "Junior / Entry"
        return "Mid-Level"

    @classmethod
    def enrich_job(cls, job: JobItem) -> JobItem:
        text = f"{job.title} {job.raw_description}"
        job.track = cls.classify_track(text, job.title, job.tags)
        job.extracted_skills = cls.extract_skills(text)
        job.extracted_certs = cls.extract_certs(text)
        job.english_level = cls.extract_english_level(text)
        job.experience_years = cls.extract_experience_level(job.title, text)

        # Standardize date and extract timestamp for strict newest-to-oldest sorting
        ts, display_str = DateUtils.parse_date(job.posted_date)
        job.posted_timestamp = ts
        job.posted_date_display = display_str
        return job
