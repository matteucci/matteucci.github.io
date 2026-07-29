"""Pydantic models describing the career data.

These are the contract between the editable ``data/`` files and every renderer
(LaTeX CVs, Astro website). Loading validates the YAML/BibTeX so a typo surfaces
as a clear error instead of a broken PDF. Add a field here + in the matching
YAML and every renderer can use it.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


# --------------------------------------------------------------------------- #
# Profile
# --------------------------------------------------------------------------- #
class Contact(BaseModel):
    label: str
    value: str
    url: str | None = None
    icon: str | None = None
    # Visibility: include on the PDF CV / on the website. Default to both.
    cv: bool = True
    website: bool = True


class Profile(BaseModel):
    name: str
    suffix: str | None = None
    title: str
    tagline: str | None = None
    summary: str
    bio: str | None = None
    affiliation: str | None = None
    contacts: list[Contact] = Field(default_factory=list)
    gdpr_authorization: str | None = None

    @property
    def full_name(self) -> str:
        """Name with suffix appended, e.g. ``Matteo Matteucci, Ph.D.``."""
        return f"{self.name}, {self.suffix}" if self.suffix else self.name

    @property
    def bio_or_summary(self) -> str:
        """Long bio when present, else the short summary."""
        return self.bio or self.summary


# --------------------------------------------------------------------------- #
# Dated sections
# --------------------------------------------------------------------------- #
class Detail(BaseModel):
    label: str
    text: str


class Employment(BaseModel):
    role: str
    org: str
    location: str | None = None
    start: int
    end: int | Literal["present"]
    details: list[Detail] = Field(default_factory=list)

    @property
    def period(self) -> str:
        end = "present" if self.end == "present" else str(self.end)
        return f"{self.start}–{end}" if str(self.start) != end else str(self.start)


class Education(BaseModel):
    degree: str
    org: str
    location: str | None = None
    start: int
    end: int
    grade: str | None = None
    thesis: str | None = None

    @property
    def period(self) -> str:
        return f"{self.start}–{self.end}" if self.start != self.end else str(self.start)


class Teaching(BaseModel):
    role: str
    org: str
    year: int
    course: str
    degree: str | None = None  # course level, e.g. "MSc" / "BSc"
    hours: int | None = None
    note: str | None = None


class Award(BaseModel):
    title: str
    org: str | None = None
    year: int | None = None
    note: str | None = None


class Project(BaseModel):
    """A funded research project (EU, national, regional, …).

    ``issuer`` is the funding body / programme that backs the project — for EU
    projects this is the European Commission together with the framework
    programme (e.g. "European Commission · Horizon 2020"); for national ones it
    is the ministry / agency and call. ``role`` is *my* role on the project.
    """

    name: str
    full_name: str | None = None  # expanded title behind an acronym
    issuer: str  # funding body / programme
    location: str | None = None
    role: str
    start: int
    end: int | Literal["present"]
    scope: str | None = None  # e.g. "European", "National", "Regional"
    url: str | None = None
    description: str | None = None

    @property
    def period(self) -> str:
        end = "present" if self.end == "present" else str(self.end)
        return f"{self.start}–{end}" if str(self.start) != end else str(self.start)


# --------------------------------------------------------------------------- #
# Profile-supporting sections
# --------------------------------------------------------------------------- #
class ResearchInterest(BaseModel):
    title: str
    description: str | None = None


class SkillGroup(BaseModel):
    category: str
    skills: list[str] = Field(default_factory=list)


class Talk(BaseModel):
    title: str
    event: str
    year: int
    location: str | None = None
    kind: str | None = None  # e.g. "Invited talk", "Conference", "Seminar"
    url: str | None = None


class Supervision(BaseModel):
    student: str
    degree: str  # e.g. "MSc thesis", "BSc thesis"
    title: str
    year: int | None = None
    role: str | None = None  # e.g. "Co-advisor"


# --------------------------------------------------------------------------- #
# Publications (parsed from publications.bib)
# --------------------------------------------------------------------------- #
PubKind = Literal["journal", "conference", "workshop", "preprint"]


class Publication(BaseModel):
    key: str
    kind: PubKind
    title: str
    authors: list[str]
    year: int
    venue: str | None = None
    volume: str | None = None
    pages: str | None = None
    doi: str | None = None
    arxiv: str | None = None
    keywords: list[str] = Field(default_factory=list)
    # Raw BibTeX entry, for a "copy BibTeX" button on the website.
    bibtex: str | None = None
    # Optional Scholar enrichment, filled from data/scholar_cache.json if present.
    citations: int | None = None
    # Featured on the website's "Selected" publications view (bib field
    # `selected = {true}`); the full list stays one toggle away.
    selected: bool = False

    @property
    def url(self) -> str | None:
        if self.doi:
            return f"https://doi.org/{self.doi}"
        if self.arxiv:
            return f"https://arxiv.org/abs/{self.arxiv}"
        return None


# --------------------------------------------------------------------------- #
# Aggregate
# --------------------------------------------------------------------------- #
class ScholarMetrics(BaseModel):
    """Optional bibliometrics fetched from Google Scholar."""

    h_index: int | None = None
    i10_index: int | None = None
    total_citations: int | None = None
    scholar_id: str | None = None
    fetched_at: str | None = None


class CVData(BaseModel):
    profile: Profile
    research_interests: list[ResearchInterest] = Field(default_factory=list)
    skills: list[SkillGroup] = Field(default_factory=list)
    employment: list[Employment] = Field(default_factory=list)
    education: list[Education] = Field(default_factory=list)
    teaching: list[Teaching] = Field(default_factory=list)
    talks: list[Talk] = Field(default_factory=list)
    supervision: list[Supervision] = Field(default_factory=list)
    awards: list[Award] = Field(default_factory=list)
    projects: list[Project] = Field(default_factory=list)
    publications: list[Publication] = Field(default_factory=list)
    metrics: ScholarMetrics | None = None
