def get_custom_css() -> str:
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600;700&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

    :root {
        --navy: #1B2430;
        --bg: #F5F6F8;
        --teal: #2F6F5E;
        --teal-light: #E8F0EE;
        --amber: #C97B3D;
        --amber-light: #FBEEE3;
        --text-muted: #6B7280;
        --border: #E2E5EA;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main {
        background-color: var(--bg);
    }

    h1, h2, h3 {
        font-family: 'IBM Plex Sans', sans-serif !important;
        color: var(--navy) !important;
        font-weight: 700 !important;
    }

    [data-testid="stSidebar"] {
        background-color: var(--navy);
    }

    [data-testid="stSidebar"] * {
        color: #F5F6F8 !important;
    }

    /* Chat message cards */
    .stChatMessage {
        background-color: white;
        border-radius: 10px;
        border: 1px solid var(--border);
        padding: 4px;
    }

    /* Access strip - signature element */
    .access-strip {
        border-left: 4px solid var(--teal);
        padding: 10px 14px;
        background-color: var(--teal-light);
        border-radius: 6px;
        margin-top: 8px;
        margin-bottom: 8px;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.82rem;
        color: var(--navy);
    }

    .access-strip.blocked {
        border-left: 4px solid var(--amber);
        background-color: var(--amber-light);
    }

    .role-badge {
        display: inline-block;
        background-color: var(--teal);
        color: white;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 500;
    }

    .metric-card {
        background-color: white;
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 16px 20px;
    }

    div[data-testid="stMetricValue"] {
        color: var(--navy);
        font-family: 'IBM Plex Sans', sans-serif;
    }
    </style>
    """