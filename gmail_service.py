"""Send analysis reports via Gmail using Composio (same tool as Gmail MCP)."""

import os
from html import escape
from typing import Any


def _build_report_html(report: dict[str, Any]) -> str:
    profile = report.get("profile", {})
    breakdown = report.get("breakdown", {})
    suggestions = report.get("suggestions", [])
    score = report.get("score", 0)

    exp_rows = ""
    for exp in profile.get("experience", []):
        exp_rows += f"""
        <tr>
          <td style="padding:8px;border-bottom:1px solid #eee;">{escape(exp.get('title', ''))}</td>
          <td style="padding:8px;border-bottom:1px solid #eee;">{escape(exp.get('company', ''))}</td>
          <td style="padding:8px;border-bottom:1px solid #eee;">{escape(exp.get('duration', ''))}</td>
        </tr>"""

    skill_tags = "".join(
        f'<span style="display:inline-block;background:#e8f0fe;color:#1a56db;'
        f'padding:4px 10px;border-radius:12px;margin:3px;font-size:13px;">'
        f'{escape(s)}</span>'
        for s in profile.get("skills", [])
    ) or "<em>No skills found</em>"

    suggestion_items = "".join(
        f'<li style="margin-bottom:8px;">{escape(s)}</li>' for s in suggestions
    )

    return f"""
    <div style="font-family:Segoe UI,Arial,sans-serif;max-width:640px;margin:0 auto;color:#1a1a2e;">
      <div style="background:linear-gradient(135deg,#0a66c2,#004182);color:#fff;padding:28px;border-radius:12px 12px 0 0;">
        <h1 style="margin:0;font-size:24px;">LinkedIn Profile Analysis</h1>
        <p style="margin:8px 0 0;opacity:0.9;">Score: <strong>{score}/100</strong></p>
      </div>
      <div style="background:#fff;padding:24px;border:1px solid #e5e7eb;border-top:none;">
        <h2 style="color:#0a66c2;margin-top:0;">{escape(profile.get('name', 'Unknown'))}</h2>
        <p style="font-size:15px;color:#4b5563;"><strong>Headline:</strong> {escape(profile.get('headline', 'N/A'))}</p>
        <p style="font-size:14px;color:#6b7280;line-height:1.6;"><strong>About:</strong><br>{escape(profile.get('about', 'N/A'))}</p>

        <h3 style="color:#374151;margin-top:24px;">Score Breakdown</h3>
        <ul style="list-style:none;padding:0;">
          <li style="padding:6px 0;">Headline: {breakdown.get('headline', 0)}/25</li>
          <li style="padding:6px 0;">About: {breakdown.get('about', 0)}/25</li>
          <li style="padding:6px 0;">Skills: {breakdown.get('skills', 0)}/25</li>
          <li style="padding:6px 0;">Experience: {breakdown.get('experience', 0)}/25</li>
        </ul>

        <h3 style="color:#374151;">Skills</h3>
        <div>{skill_tags}</div>

        <h3 style="color:#374151;margin-top:24px;">Experience</h3>
        <table style="width:100%;border-collapse:collapse;font-size:14px;">
          <tr style="background:#f3f4f6;">
            <th style="padding:8px;text-align:left;">Title</th>
            <th style="padding:8px;text-align:left;">Company</th>
            <th style="padding:8px;text-align:left;">Duration</th>
          </tr>
          {exp_rows or '<tr><td colspan="3" style="padding:8px;"><em>No experience found</em></td></tr>'}
        </table>

        <h3 style="color:#374151;margin-top:24px;">Suggestions</h3>
        <ul style="padding-left:20px;color:#374151;">{suggestion_items}</ul>

      </div>
    </div>
    """


def send_report_email(recipient_email: str, report: dict[str, Any]) -> dict[str, Any]:
    api_key = os.environ.get("COMPOSIO_API_KEY")
    if not api_key:
        raise RuntimeError(
            "COMPOSIO_API_KEY is not set. Add it to your environment to enable Gmail sending "
            "via Composio (same integration as the Gmail MCP tool)."
        )

    try:
        from composio import Composio
    except ImportError as exc:
        raise RuntimeError(
            "composio package not installed. Run: pip install composio"
        ) from exc

    user_id = os.environ.get("COMPOSIO_USER_ID", "default")
    profile_name = report.get("profile", {}).get("name", "Profile")
    score = report.get("score", 0)
    html_body = _build_report_html(report)

    composio = Composio(api_key=api_key)
    result = composio.tools.execute(
        "GMAIL_SEND_EMAIL",
        {
            "recipient_email": recipient_email,
            "subject": f"LinkedIn Profile Analysis — {profile_name} ({score}/100)",
            "body": html_body,
            "is_html": True,
        },
        user_id=user_id,
    )

    return {"success": True, "result": result}
