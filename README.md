# LinkedIn Profile Analyzer

A web app that scores LinkedIn profile details 0–100 and sends formatted reports via Gmail (through Composio — the same integration used by the Gmail MCP tool).

## Features

- Manual input: Name, Headline, About, and Skills
- Scores profile on headline keywords, about length, skills count, and experience completeness
- Actionable improvement suggestions
- Send HTML report to any email via Gmail

## Quick Start

```bash
cd linkedin-profile-analyzer
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
python app.py
```

Open http://localhost:5000

## Gmail Setup (Composio)

Email sending uses the **GMAIL_SEND_EMAIL** Composio tool — the same backend as the Gmail MCP integration.

1. Get your API key from [Composio Dashboard](https://app.composio.dev)
2. Ensure Gmail is connected in Composio (Settings → Integrations → Gmail)
3. Set environment variables:

```bash
set COMPOSIO_API_KEY=your_api_key
set COMPOSIO_USER_ID=default
```

## Scoring

| Category    | Max Points | Criteria                                      |
|-------------|------------|-----------------------------------------------|
| Headline    | 25         | Length, role keywords, value proposition       |
| About       | 25         | Section length (aim for 300+ characters)      |
| Skills      | 25         | Number of listed skills (aim for 10+)           |
| Experience  | 25         | Entry count and completeness (not entered manually) |
