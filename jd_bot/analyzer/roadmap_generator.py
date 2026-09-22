from typing import Dict, Any, List

class RoadmapGenerator:
    @staticmethod
    def generate_all_roadmaps() -> Dict[str, Any]:
        return {
            "Digital Forensics & Incident Response (DFIR)": {
                "title": "Lộ Trình: Nâng Cấp Từ Tier 2 Lên Senior DFIR / Incident Response Lead",
                "target_timeline": "6 - 8 tháng (Chinh phục mốc lương 30M - 50M/tháng)",
                "phases": [
                    {
                        "phase": "Giai đoạn 1: Master Phân Tích Artifacts & Memory Sâu (Tháng 1 - 2)",
                        "focus": "Hiểu tường tận ngóc ngách Windows/Linux Artifacts & Memory không phụ thuộc tool tự động",
                        "tasks": [
                            "Đào sâu các Artifacts ẩn của Windows: $MFT, $LogFile, USN Journal, Shimcache, Amcache, LNK/Jumplist, SRUM, Registry hives.",
                            "Memory Forensics nâng cao với Volatility 3: Phân tích tiến trình tiêm mã (Process Injection - Process Hollowing, APC Injection), bóc tách DLL ẩn, phát hiện rootkit.",
                            "Tự động hóa phân tích bằng Python: Tự viết script parse các cấu trúc file nhị phân độc quyền bằng thư viện `construct` hoặc `pefile`.",
                            "Thực hành Lab: Điều tra các case APT thực tế trên nền tảng CyberDefenders (Blue Team Labs) và LetsDefend."
                        ],
                        "resources": [
                            "Sách gối đầu: Windows Forensic Analysis Toolkit (Harlan Carvey), The Art of Memory Forensics",
                            "Platform luyện lab: CyberDefenders (BlueYard), LetsDefend DFIR track"
                        ]
                    },
                    {
                        "phase": "Giai đoạn 2: Luận Ngược Mã Độc & Phân Tích Hành Vi (Tháng 3 - 5)",
                        "focus": "Lấp đầy lỗ hổng lớn nhất: Phân tích tĩnh & động mã độc (IDA Pro, Ghidra, x64dbg)",
                        "tasks": [
                            "Thiết lập môi trường cô lập phân tích mã độc (REMnux + Windows Flare-VM).",
                            "Phân tích hành vi (Dynamic Analysis): Sử dụng Procmon, Regshot, Wireshark, FakeNet-NG để theo dõi hành vi C2 và ghi nhận IoC.",
                            "Dịch ngược mã máy (Reverse Engineering với Ghidra / IDA Pro): Nắm vững kiến trúc x86/x64, nhận diện các kỹ thuật né tránh (Anti-debugging, Anti-VM, Packing).",
                            "Kỹ thuật Unpack mã độc: Thực hành unpack các dòng dropper/loader, ransomware phổ biến bằng x64dbg.",
                            "Viết luật phát hiện: Đóng gói IoC thành quy tắc YARA và Sigma rule để quét trên toàn hệ thống."
                        ],
                        "resources": [
                            "Khóa học: Practical Malware Analysis and Triage (PMAT) - TCM Security",
                            "Sách chuẩn: Practical Malware Analysis (Michael Sikorski)",
                            "Tài nguyên: MalwareBazaar, Hybrid-Analysis, ANY.RUN"
                        ]
                    },
                    {
                        "phase": "Giai đoạn 3: Tiếng Anh Báo Cáo C-Level, Kỹ Năng Chỉ Huy & Săn Chứng Chỉ (Tháng 6 - 8)",
                        "focus": "Trở thành Incident Commander & chuẩn bị hồ sơ ứng tuyển Senior",
                        "tasks": [
                            "Nâng cấp Tiếng Anh Báo cáo Sự cố: Luyện viết báo cáo điều tra (Incident Report) bằng tiếng Anh chuẩn chỉnh cho C-level/Board of Directors.",
                            "Tư duy Incident Commander: Kỹ năng điều phối khủng hoảng, thương thảo với khách hàng/ngân hàng khi bị mã hóa dữ liệu, đưa ra chiến lược cô lập và khôi phục (Remediation & Hardening).",
                            "Chinh phục chứng chỉ quốc tế: Ôn luyện và thi SANS FOR508 (GCFA) hoặc SANS FOR500, hoặc OffSec Certified Defense Professional (OSDF).",
                            "Cập nhật CV Master: Viết lại toàn bộ kinh nghiệm VNCERT bằng tiếng Anh chuẩn ATS, làm nổi bật vai trò Root Cause Analysis và chỉ huy ứng cứu."
                        ],
                        "resources": [
                            "Chứng chỉ mục tiêu: SANS GCFA (GIAC Certified Forensic Analyst), OffSec OSDF",
                            "Mẫu báo cáo: SANS DFIR Poster & Real-world Incident Reports"
                        ]
                    }
                ]
            },
            "SecOps Automation & Platform Engineering": {
                "title": "Lộ Trình: Trở Thành Kỹ Sư Tự Động Hóa An Ninh (SecOps / Detection as Code)",
                "target_timeline": "3 - 4 tháng (Tận dụng tối đa 80% gốc SOC Tier 2)",
                "phases": [
                    {
                        "phase": "Giai đoạn 1: Nâng cấp Kỹ năng Lập trình Python Thuần (Tháng 1)",
                        "focus": "Viết code độc lập không phụ thuộc hoàn toàn vào AI, làm chủ REST API",
                        "tasks": [
                            "Luyện viết Python tương tác với các API an ninh: Tự động tra cứu VirusTotal, AbuseIPDB, AlienVault OTX bằng thư viện `requests` / `httpx`.",
                            "Xử lý dữ liệu quy mô lớn: Đọc hiểu và xử lý JSON, CSV, Syslog với xử lý ngoại lệ (Error handling, Logging, Retry logic chuẩn production).",
                            "Đóng gói công cụ CLI: Viết một tool CLI hoàn chỉnh bằng thư viện `argparse` hoặc `click` hỗ trợ điều tra IP/Hash hàng loạt."
                        ],
                        "resources": [
                            "Khóa học: Python for Cybersecurity (Coursera / TCM Security)",
                            "Bài tập: Xây dựng bộ công cụ triage tự động mã nguồn mở trên GitHub"
                        ]
                    },
                    {
                        "phase": "Giai đoạn 2: Tự động hóa Playbook với SOAR (Tháng 2 - 3)",
                        "focus": "Xây dựng quy trình phản ứng tự động không cần người can thiệp",
                        "tasks": [
                            "Triển khai nền tảng SOAR mã nguồn mở Shuffle (shuffler.io) hoặc Tines trên Docker.",
                            "Thiết kế Playbook tự động hóa các ca trực: Khi SIEM báo alert Phishing -> Tự bóc tách mail header, link -> Quét VirusTotal -> Cách ly máy bằng EDR API -> Gửi thông báo Slack/Telegram.",
                            "Tích hợp Jira / TheHive để tự động mở ticket sự cố và cập nhật IoC."
                        ],
                        "resources": [
                            "Tài liệu & Lab: Shuffle SOAR documentation & Community workflows",
                            "Dự án thực hành: Open-source SOC Lab (Elasticsearch + Shuffle + TheHive + Wazuh)"
                        ]
                    },
                    {
                        "phase": "Giai đoạn 3: Detection Engineering & Detection as Code (Tháng 4)",
                        "focus": "Nâng cấp từ viết query đơn giản sang quản lý rule chuyên nghiệp",
                        "tasks": [
                            "Chuyển toàn bộ rule SIEM sang định dạng chuẩn Sigma Rule (YAML).",
                            "Sử dụng công cụ `sigmac` / `pySigma` để tự động biên dịch Sigma rule sang Elastic Query / Splunk SPL / QRadar AQL.",
                            "Thiết lập Git repository quản lý rule phát hiện, tích hợp CI/CD kiểm tra cú pháp và test rule trên tập dữ liệu log mẫu (Evtx).",
                            "Cập nhật CV định vị vị trí: SecOps Automation Engineer / Detection Engineer (Lương 25 - 40 triệu, thoát trực ca)."
                        ],
                        "resources": [
                            "Tài nguyên: SigmaHQ official repository, Detection Engineering Handbook",
                            "Chứng chỉ khuyên dùng: Certified Detection Engineer (CDE) hoặc Elastic Certified Analyst"
                        ]
                    }
                ]
            },
            "Cloud Security / DevSecOps": {
                "title": "Lộ Trình: Trở Thành Kỹ Sư Cloud Security & DevSecOps",
                "target_timeline": "6 tháng (10-15 giờ/tuần)",
                "phases": [
                    {
                        "phase": "Giai đoạn 1: Nền tảng Cloud & Hạ tầng mã nguồn (Tháng 1 - 2)",
                        "focus": "Làm chủ AWS Core Services và Terraform (IaC)",
                        "tasks": [
                            "Học AWS Cloud Practitioner & SysOps nền tảng (VPC, Subnet, Route Table, Security Group, IAM Roles/Policies).",
                            "Thực hành Terraform: Viết mã tạo VPC chuẩn an toàn, EC2 hardened, RDS trong private subnet có KMS mã hóa.",
                            "Lab thực hành: Tự build môi trường AWS 3-tier an toàn bằng Terraform, đẩy code lên GitHub."
                        ],
                        "resources": [
                            "Khóa học: Stephane Maarek (Udemy) - AWS Certified Solutions Architect / Security",
                            "Tài liệu: HashiCorp Terraform Associate Guide & Tutorials",
                            "Lab: Cloud Academy / Whizlabs AWS Hands-on labs"
                        ]
                    },
                    {
                        "phase": "Giai đoạn 2: Container Security & K8s (Tháng 3 - 4)",
                        "focus": "Bảo mật Docker, Kubernetes và Triển khai CI/CD an toàn",
                        "tasks": [
                            "Học Docker: Viết Dockerfile chuẩn bảo mật (Non-root user, Multi-stage build, Minimal base image Alpine/Distroless).",
                            "Quét lỗ hổng Container: Tích hợp Trivy / Grype vào quy trình build.",
                            "Kubernetes Security: Cấu hình RBAC, NetworkPolicy, Pod Security Standards (PSS), Seccomp/AppArmor.",
                            "Xây dựng pipeline CI/CD an toàn: Dùng GitHub Actions quét secret (Gitleaks), quét IaC (Tfsec / Checkov)."
                        ],
                        "resources": [
                            "Khóa học: Mumshad Mannambeth (KodeKloud) - CKA & CKS",
                            "Công cụ thực hành: Minikube / K3s, Trivy, Checkov, Gitleaks"
                        ]
                    },
                    {
                        "phase": "Giai đoạn 3: Cloud Detection, Tự động hóa & Săn Chứng chỉ (Tháng 5 - 6)",
                        "focus": "Bảo mật vận hành trên Cloud và thi chứng chỉ tạo lợi thế tuyển dụng",
                        "tasks": [
                            "Vận hành Cloud Security Services: Cấu hình AWS GuardDuty, Security Hub, AWS Config, CloudTrail, AWS WAF.",
                            "Tự động phản hồi (Auto-remediation): Dùng AWS Lambda (Python) tự động khóa Security Group khi bị mở port 22/3389 ra 0.0.0.0/0.",
                            "Ôn thi và lấy chứng chỉ: AWS Certified Security - Specialty (SCS-C02).",
                            "Đóng gói CV: Viết lại CV chuẩn tiếng Anh làm nổi bật các dự án Cloud Terraform & CI/CD Security đã tự build."
                        ],
                        "resources": [
                            "Chứng chỉ mục tiêu: AWS Certified Security - Specialty ($300)",
                            "Đề thi mẫu: Tutorial Dojo (Jon Bonso)"
                        ]
                    }
                ]
            },
            "GRC & Compliance / IT Auditor": {
                "title": "Lộ Trình: Trở Thành Chuyên Viên GRC & Đánh Giá Tuân Thủ An Toàn Thông Tin",
                "target_timeline": "4 - 5 tháng (Phù hợp khối Ngân hàng, Bảo hiểm, Big 4)",
                "phases": [
                    {
                        "phase": "Giai đoạn 1: Nắm vững Khung Tiêu chuẩn Quốc tế (Tháng 1 - 2)",
                        "focus": "Làm chủ ISO/IEC 27001:2022 và PCI-DSS v4.0",
                        "tasks": [
                            "Học chi tiết 93 biện pháp kiểm soát an toàn (Controls) trong Phụ lục A của ISO/IEC 27001:2022.",
                            "Nắm rõ quy trình xây dựng Hệ thống quản lý ATTT (ISMS): Soạn thảo Chính sách an toàn, Bảng đánh giá rủi ro (Risk Assessment), Kế hoạch xử lý rủi ro (Risk Treatment Plan - RTP).",
                            "Nghiên cứu 12 yêu cầu cốt lõi của tiêu chuẩn thanh toán thẻ PCI-DSS v4.0."
                        ],
                        "resources": [
                            "Tài liệu chuẩn: ISO/IEC 27001:2022 Standard & Implementation Guidance",
                            "Khóa học: ISO 27001 Lead Implementer / Auditor Training"
                        ]
                    },
                    {
                        "phase": "Giai đoạn 2: Quy định Ngân hàng Việt Nam & Đánh giá Thực tế (Tháng 3 - 4)",
                        "focus": "Áp dụng Thông tư 09/2020/TT-NHNN, Thông tư 75 và Nghị định 13",
                        "tasks": [
                            "Đọc sâu Thông tư 09/2020/TT-NHNN quy định về an toàn hệ thống thông tin trong hoạt động ngân hàng.",
                            "Tìm hiểu quy trình đánh giá tuân thủ và bảo vệ dữ liệu cá nhân theo Nghị định 13/2023/NĐ-CP.",
                            "Thực hành đóng vai kiểm toán viên: Lập bảng Check-list kiểm toán cho một hệ thống ngân hàng mẫu."
                        ],
                        "resources": [
                            "Văn bản pháp luật: Cổng thông tin Ngân hàng Nhà nước & Bộ Công an",
                            "Mẫu tài liệu: ISMS Template Toolkit"
                        ]
                    },
                    {
                        "phase": "Giai đoạn 3: Lấy Chứng chỉ ISO 27001 LA / CISA & Ứng tuyển (Tháng 5)",
                        "focus": "Hợp thức hóa năng lực bằng chứng chỉ quốc tế uy tín",
                        "tasks": [
                            "Tham gia khóa học và thi chứng chỉ ISO/IEC 27001:2022 Lead Auditor (TÜV SÜD / PECB / BSI cấp).",
                            "Ứng tuyển vị trí GRC Specialist / IT Auditor tại các Ngân hàng lớn hoặc Big 4."
                        ],
                        "resources": [
                            "Chứng chỉ: ISO 27001:2022 Lead Auditor, ISACA CISA"
                        ]
                    }
                ]
            }
        }
