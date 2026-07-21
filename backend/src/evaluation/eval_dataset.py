EVAL_QUESTIONS = [
    {
        "question": "How many days of annual leave do I get?",
        "ground_truth": "Employees are entitled to 21 days of paid annual leave per calendar year, accruing at 1.75 days per month.",
        "expected_source": "Leave_Policy.txt",
        "role": "employee",
    },
    {
        "question": "How many days of sick leave am I entitled to?",
        "ground_truth": "Employees are entitled to 14 days of paid sick leave per year, with a medical certificate required for absences longer than 2 consecutive days.",
        "expected_source": "Leave_Policy.txt",
        "role": "employee",
    },
    {
        "question": "How long is parental leave for a primary caregiver?",
        "ground_truth": "Primary caregivers are entitled to 12 weeks of paid parental leave.",
        "expected_source": "Leave_Policy.txt",
        "role": "employee",
    },
    {
        "question": "What training must I complete in my first two weeks?",
        "ground_truth": "New employees must complete Code of Conduct and Ethics Training, Information Security Awareness Training, Anti-Harassment and Workplace Conduct Training, and Data Privacy and GDPR Basics within their first two weeks.",
        "expected_source": "Onboarding_Guide.txt",
        "role": "employee",
    },
    {
        "question": "How long is the probation period for new employees?",
        "ground_truth": "All new employees undergo a 90-day probation period, with check-ins at 30, 60, and 90 days.",
        "expected_source": "Onboarding_Guide.txt",
        "role": "employee",
    },
    {
        "question": "What is the minimum password length required?",
        "ground_truth": "All company accounts must use passwords that are at least 12 characters long.",
        "expected_source": "IT_Security_Policy.txt",
        "role": "employee",
    },
    {
        "question": "How often must passwords be changed?",
        "ground_truth": "Passwords must be changed every 90 days.",
        "expected_source": "IT_Security_Policy.txt",
        "role": "employee",
    },
    {
        "question": "What should I do if I suspect a security incident?",
        "ground_truth": "Any suspected security incident must be reported to security@company.internal within 1 hour of discovery.",
        "expected_source": "IT_Security_Policy.txt",
        "role": "employee",
    },
    {
        "question": "What is required before merging code into the main branch?",
        "ground_truth": "Every change must go through a pull request with at least one approving review before merging into main. Direct pushes to main are disabled.",
        "expected_source": "Product_Engineering_Handbook.pdf",
        "role": "employee",
    },
    {
        "question": "What test coverage is required for new modules?",
        "ground_truth": "New modules require a minimum of 80 percent code coverage.",
        "expected_source": "Product_Engineering_Handbook.pdf",
        "role": "employee",
    },
    {
        "question": "What is the salary range for a Staff Engineer?",
        "ground_truth": "The salary range for a Staff Engineer (L6) is $160,000 to $195,000.",
        "expected_source": "CONFIDENTIAL_Compensation_Bands.pdf",
        "role": "hr",  # only testable with HR role due to RBAC
    },
    {
        "question": "How often are pay equity audits conducted?",
        "ground_truth": "Pay equity audits are conducted every 6 months.",
        "expected_source": "CONFIDENTIAL_Compensation_Bands.pdf",
        "role": "hr",
    },
    {
        "question": "What is the maximum unpaid leave an employee can request?",
        "ground_truth": "Unpaid leave requests should not exceed 30 consecutive days without special authorization from senior leadership.",
        "expected_source": "Leave_Policy.txt",
        "role": "employee",
    },
    {
        "question": "What VPN requirements exist for remote work?",
        "ground_truth": "Employees working remotely must connect to company systems via the approved VPN client, and should not use public Wi-Fi without an active VPN connection.",
        "expected_source": "IT_Security_Policy.txt",
        "role": "employee",
    },
    {
        "question": "When are production deployments scheduled?",
        "ground_truth": "Production deployments are scheduled during Tuesday or Thursday release windows to avoid weekend incidents.",
        "expected_source": "Product_Engineering_Handbook.pdf",
        "role": "employee",
    },
]