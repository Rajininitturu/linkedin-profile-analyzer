"""LinkedIn profile scoring from manual input."""

from dataclasses import asdict, dataclass, field
from typing import Any

HEADLINE_KEYWORDS = {
    "strong": {
        "engineer", "developer", "manager", "director", "lead", "founder", "ceo",
        "cto", "designer", "analyst", "consultant", "architect", "specialist",
        "expert", "strategist", "product", "marketing", "sales", "data", "ai",
        "machine learning", "cloud", "security", "growth", "operations",
    },
    "value": {
        "building", "helping", "driving", "scaling", "delivering", "transforming",
        "passionate", "experienced", "certified", "award", "results", "impact",
        "innovation", "solutions", "strategy", "leadership",
    },
}


@dataclass
class ExperienceEntry:
    title: str = ""
    company: str = ""
    duration: str = ""
    description: str = ""


@dataclass
class ProfileData:
    name: str = ""
    headline: str = ""
    about: str = ""
    experience: list[ExperienceEntry] = field(default_factory=list)
    skills: list[str] = field(default_factory=list)


@dataclass
class ScoreBreakdown:
    headline: int = 0
    about: int = 0
    skills: int = 0
    experience: int = 0

    @property
    def total(self) -> int:
        return self.headline + self.about + self.skills + self.experience


def parse_skills(raw: str) -> list[str]:
    if not raw or not raw.strip():
        return []
    parts = [s.strip() for s in raw.replace("\n", ",").split(",")]
    return list(dict.fromkeys(s for s in parts if s))


def build_profile(name: str, headline: str, about: str, skills_raw: str) -> ProfileData:
    return ProfileData(
        name=name.strip(),
        headline=headline.strip(),
        about=about.strip(),
        skills=parse_skills(skills_raw),
    )


def score_headline(headline: str) -> int:
    if not headline:
        return 0
    text = headline.lower()
    score = 10
    if 40 <= len(headline) <= 220:
        score += 8
    elif len(headline) >= 20:
        score += 4

    keyword_hits = sum(1 for kw in HEADLINE_KEYWORDS["strong"] if kw in text)
    value_hits = sum(1 for kw in HEADLINE_KEYWORDS["value"] if kw in text)
    score += min(7, keyword_hits * 2)
    score += min(5, value_hits * 2)
    return min(25, score)


def score_about(about: str) -> int:
    if not about:
        return 0
    length = len(about.strip())
    if length >= 500:
        return 25
    if length >= 300:
        return 20
    if length >= 150:
        return 14
    if length >= 80:
        return 8
    return 4


def score_skills(skills: list[str]) -> int:
    count = len(skills)
    if count >= 15:
        return 25
    if count >= 10:
        return 20
    if count >= 7:
        return 15
    if count >= 4:
        return 10
    if count >= 1:
        return 5
    return 0


def score_experience(experience: list[ExperienceEntry]) -> int:
    if not experience:
        return 0
    score = min(10, len(experience) * 3)
    complete = sum(
        1 for exp in experience
        if exp.title and (exp.company or exp.duration or exp.description)
    )
    score += min(15, complete * 4)
    return min(25, score)


def generate_suggestions(profile: ProfileData, breakdown: ScoreBreakdown) -> list[str]:
    suggestions: list[str] = []

    if breakdown.headline < 18:
        suggestions.append(
            "Strengthen your headline with your role, niche, and a value statement "
            "(e.g. 'Senior Data Engineer | Building scalable ML pipelines')."
        )
    if breakdown.about < 18:
        suggestions.append(
            "Expand your About section to at least 300 characters. Share your story, "
            "key achievements, and what you're looking for."
        )
    if breakdown.skills < 15:
        suggestions.append(
            "Add more relevant skills (aim for 10+). Include tools, frameworks, and "
            "domain expertise recruiters search for."
        )
    if breakdown.experience < 18:
        suggestions.append(
            "Complete your Experience entries with company names, dates, and bullet "
            "points highlighting measurable impact."
        )
    if not profile.name:
        suggestions.append("Ensure your profile displays your full name prominently.")
    if len(profile.skills) > 0 and len(profile.skills) < 5:
        suggestions.append("Reorder skills so your top 3 appear first in your profile.")

    if not suggestions:
        suggestions.append(
            "Great profile! Consider adding recommendations, featured content, "
            "and a custom banner to stand out further."
        )

    return suggestions


def analyze_profile(
    name: str,
    headline: str,
    about: str,
    skills: str,
) -> dict[str, Any]:
    if not name.strip():
        raise ValueError("Name is required.")

    profile = build_profile(name, headline, about, skills)
    breakdown = ScoreBreakdown(
        headline=score_headline(profile.headline),
        about=score_about(profile.about),
        skills=score_skills(profile.skills),
        experience=score_experience(profile.experience),
    )
    suggestions = generate_suggestions(profile, breakdown)

    return {
        "profile": {
            **asdict(profile),
            "experience": [asdict(exp) for exp in profile.experience],
        },
        "score": breakdown.total,
        "breakdown": asdict(breakdown),
        "suggestions": suggestions,
    }
