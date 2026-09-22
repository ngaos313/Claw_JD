import re
from typing import Dict, List, Any, Tuple
from jd_bot.crawlers.base_crawler import JobItem
from jd_bot.analyzer.date_utils import DateUtils

CAREER_TRACKS = {
    "Digital Forensics & Incident Response (DFIR)": {
        "keywords": [
            "dfir", "digital forensics", "forensic", "incident response", "điều tra số",
            "ứng cứu sự cố", "ứng phó sự cố", "volatility", "velociraptor", "memory forensics", "yara",
            "incident commander", "forensics investigator", "csirt", "cert"
        ],
        "weight": 1.0
    },
    "Malware Analysis & Reverse Engineering": {
        "keywords": [
            "malware analysis", "phân tích mã độc", "reverse engineering", "mã độc",
            "dịch ngược", "ida pro", "ghidra", "x64dbg", "unpack malware", "ransomware",
            "binary analysis", "disassembly", "deobfuscation", "dynamic analysis", "static analysis"
        ],
        "weight": 1.0
    },
    "Security Engineering & Infrastructure": {
        "keywords": [
            "security engineer", "kỹ sư an ninh mạng", "kỹ sư an toàn thông tin", "kỹ sư bảo mật",
            "network security", "bảo mật hạ tầng", "system security", "cyber defense",
            "chuyên viên an ninh mạng", "chuyên viên an toàn thông tin", "security specialist",
            "an ninh mạng hạ tầng", "firewall", "ips", "ids", "edr", "endpoint security",
            "kỹ sư hệ thống an toàn thông tin", "an toàn thông tin hạ tầng"
        ],
        "weight": 1.0
    },
    "SOC Operations & Monitoring": {
        "keywords": [
            "soc tier", "soc analyst", "soc lead", "trực soc", "giám sát an ninh", "ca trực soc",
            "alert monitoring", "l1 analyst", "l2 analyst", "trực ca soc", "giám sát an toàn thông tin",
            "vận hành an ninh", "vận hành & giám sát", "siem monitoring", "blue team"
        ],
        "weight": 1.0
    },
    "Cloud Security / DevSecOps": {
        "keywords": [
            "cloud security", "devsecops", "aws security", "azure security", "gcp security",
            "terraform", "kubernetes security", "k8s security", "container security",
            "ci/cd security", "pipeline security", "cspm", "cwpp", "iac"
        ],
        "weight": 1.0
    },
    "SecOps Automation & Platform Engineering": {
        "keywords": [
            "secops", "detection engineering", "soar", "security automation", "detection as code",
            "sigma rule", "shuffle", "tines", "cortex xsoar", "siem engineer", "siem admin",
            "security platform", "elastic engineer", "splunk engineer"
        ],
        "weight": 1.0
    },
    "AppSec / Product Security": {
        "keywords": [
            "application security", "appsec", "product security", "sast", "dast",
            "secure code review", "threat modeling", "stride", "ssdlc", "sonarqube",
            "checkmarx", "snyk", "owasp", "burp suite"
        ],
        "weight": 1.0
    },
    "GRC & Compliance / IT Auditor": {
        "keywords": [
            "grc", "governance", "compliance", "tuân thủ", "it audit", "kiểm toán it",
            "iso 27001", "iso/iec 27001", "pci-dss", "pci dss", "nist", "thông tư 09",
            "thông tư 75", "nghị định 13", "risk assessment", "đánh giá rủi ro", "chính sách an toàn",
            "privacy compliance"
        ],
        "weight": 1.0
    },
    "Pre-Sales & Security Solutions Architect": {
        "keywords": [
            "solution architect", "pre-sales", "presales", "tư vấn giải pháp", "security architect",
            "consultant", "chuyên gia tư vấn", "kiến trúc an toàn", "boq", "rfp", "poc",
            "phát triển dịch vụ an ninh"
        ],
        "weight": 1.0
    },
    "Offensive Security (Pentest / Red Team)": {
        "keywords": [
            "penetration test", "pentest", "red team", "offensive security", "ethical hacker",
            "web pentest", "mobile pentest", "kiểm thử xâm nhập", "active directory attack",
            "kiểm thử an toàn thông tin", "đánh giá lỗ hổng"
        ],
        "weight": 1.0
    }
}

TAG_ROLE_MAP = {
    "Reverse Engineering / Malware Analysis": "Malware Analysis & Reverse Engineering",
    "Penetration Testing / Red Team": "Offensive Security (Pentest / Red Team)",
    "Cloud & Network Security": "Security Engineering & Infrastructure",
    "DevSecOps / Application Security": "Cloud Security / DevSecOps",
    "GRC / Tuân thủ & Quản trị Rủi ro": "GRC & Compliance / IT Auditor",
    "SOC / Blue Team / Threat Monitoring": "SOC Operations & Monitoring",
    "Incident Response / DFIR": "Digital Forensics & Incident Response (DFIR)"
}

SKILL_PATTERNS = {
    # Forensics & DFIR
    "Digital Forensics & Artifacts": r"\b(forensic|forensics|velociraptor|ez tools|mft|amcache|shimcache|registry)\b",
    "Memory Forensics (Volatility)": r"\b(volatility|winpmem|dumpit|memory analysis)\b",
    "Malware Analysis / Reverse Engineering": r"\b(malware analysis|reverse engineering|ida pro|ghidra|x64dbg|unpack|phân tích mã độc)\b",
    "Incident Response": r"\b(incident response|dfir|ứng cứu sự cố|xử lý sự cố|ứng phó sự cố)\b",

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
        title_lower = title.lower()

        # 1. Precise Title Matching (Ordered from most specific to general)
        # Malware Analysis
        if any(w in title_lower for w in ["malware", "mã độc", "reverse engineer", "reverse engineering", "dịch ngược"]):
            return "Malware Analysis & Reverse Engineering"

        # DFIR (Forensics / Incident Response)
        if any(w in title_lower for w in ["dfir", "digital forensic", "forensic", "điều tra số", "ứng cứu sự cố", "ứng phó sự cố", "incident response"]):
            return "Digital Forensics & Incident Response (DFIR)"

        # Pentest / Offensive Security
        if any(w in title_lower for w in ["pentest", "penetration", "red team", "kiểm thử xâm nhập", "kiểm thử an toàn", "đánh giá và kiểm thử", "ethical hack"]):
            return "Offensive Security (Pentest / Red Team)"

        # Cloud Security / DevSecOps
        if any(w in title_lower for w in ["devsecops", "cloud security", "aws security", "azure security", "container security"]):
            return "Cloud Security / DevSecOps"

        # AppSec / Product Security
        if any(w in title_lower for w in ["appsec", "application security", "product security", "bảo mật ứng dụng", "secure code"]):
            return "AppSec / Product Security"

        # GRC / Compliance / IT Audit
        if any(w in title_lower for w in ["grc", "compliance", "tuân thủ", "kiểm toán it", "it audit", "iso 27001", "quản trị rủi ro", "privacy compliance"]):
            return "GRC & Compliance / IT Auditor"

        # Pre-Sales & Solution Architecture
        if any(w in title_lower for w in ["pre-sales", "presale", "solution architect", "tư vấn giải pháp", "phát triển dịch vụ an ninh", "security consultant", "kiến trúc an toàn"]):
            return "Pre-Sales & Security Solutions Architect"

        # SOC Operations & Monitoring
        if any(w in title_lower for w in ["soc", "giám sát an toàn thông tin", "giám sát an ninh", "vận hành & giám sát", "vận hành an ninh", "trực ca soc"]):
            return "SOC Operations & Monitoring"

        # SecOps Automation / SOAR
        if any(w in title_lower for w in ["soar", "detection engineer", "secops", "security automation"]):
            return "SecOps Automation & Platform Engineering"

        # Security Engineering & Infrastructure
        if any(w in title_lower for w in [
            "kỹ sư an toàn thông tin", "kỹ sư an ninh mạng", "security engineer", "kỹ sư bảo mật",
            "kỹ sư hệ thống an toàn thông tin", "network security", "chuyên viên an ninh mạng",
            "chuyên viên an toàn thông tin", "cyber defense", "an toàn thông tin hạ tầng", "hạ tầng an ninh"
        ]):
            return "Security Engineering & Infrastructure"

        # Obvious generic or non-specialized roles -> Other
        if any(w in title_lower for w in ["giảng viên", "teacher", "sales", "kinh doanh", "it officer", "senior it officer"]):
            return "Other / An toàn Thông tin Chung"

        # 2. Check tag role group mappings if available
        if tags:
            for t in tags:
                if t in TAG_ROLE_MAP:
                    return TAG_ROLE_MAP[t]

        # 3. Score-based matching on text content
        combined = f"{title} {title} {text}".lower()
        track_scores = {}
        for track, config in CAREER_TRACKS.items():
            score = 0
            for kw in config["keywords"]:
                if kw in combined:
                    in_title = kw in title_lower
                    weight = 4 if in_title else 1
                    score += weight
            track_scores[track] = score * config["weight"]

        best_track = max(track_scores, key=track_scores.get)
        # Require a solid score threshold to avoid random false positives
        if track_scores[best_track] < 3:
            return "Other / An toàn Thông tin Chung"

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
