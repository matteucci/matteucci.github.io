// Loads the generated career data. `site.json` is produced by `cv build-site`
// from the same data/ YAML + BibTeX the LaTeX CVs use — single source of truth.
import data from './site.json';

export type Contact = {
  label: string; value: string; url: string | null; icon: string | null;
  cv: boolean; website: boolean;
};
export type Detail = { label: string; text: string };
export type Employment = {
  role: string; org: string; location: string | null;
  start: number; end: number | 'present'; details: Detail[];
};
export type Education = {
  degree: string; org: string; location: string | null;
  start: number; end: number; grade: string | null; thesis: string | null;
};
export type Teaching = {
  role: string; org: string; year: number; course: string;
  degree: string | null; hours: number | null; note: string | null;
};
export type Award = { title: string; org: string | null; year: number | null; note: string | null };
export type Publication = {
  key: string; kind: 'journal' | 'conference' | 'workshop' | 'preprint';
  title: string; authors: string[]; year: number; venue: string | null;
  volume: string | null; pages: string | null; doi: string | null;
  arxiv: string | null; keywords: string[]; bibtex: string | null; citations: number | null;
  selected: boolean;
};

export type ResearchInterest = { title: string; description: string | null };
export type SkillGroup = { category: string; skills: string[] };
export type Talk = {
  title: string; event: string; year: number;
  location: string | null; kind: string | null; url: string | null;
};
export type Supervision = {
  student: string; degree: string; title: string;
  year: number | null; role: string | null;
};
export type Project = {
  name: string; full_name: string | null; issuer: string;
  location: string | null; role: string; start: number; end: number | 'present';
  scope: string | null; url: string | null; description: string | null;
};

export const cv = data as unknown as {
  profile: {
    name: string; suffix: string | null; title: string;
    tagline: string | null; summary: string; bio: string | null;
    affiliation: string | null;
    contacts: Contact[]; gdpr_authorization: string | null;
  };
  research_interests: ResearchInterest[];
  skills: SkillGroup[];
  employment: Employment[];
  education: Education[];
  teaching: Teaching[];
  talks: Talk[];
  supervision: Supervision[];
  awards: Award[];
  projects: Project[];
  publications: Publication[];
  metrics: { h_index: number | null; total_citations: number | null } | null;
};

export const fullName = cv.profile.suffix
  ? `${cv.profile.name}, ${cv.profile.suffix}`
  : cv.profile.name;

// The published CV PDF is named after the profile surname ("archetti-cv.pdf");
// src/cli.py derives it the same way, so the link never drifts from the file.
export const cvPdfPath = `cv/${cv.profile.name.trim().split(/\s+/).pop()!.toLowerCase()}-cv.pdf`;

export const period = (start: number, end: number | 'present') =>
  end === 'present' ? `${start} – present` : start === end ? `${start}` : `${start} – ${end}`;

export const pubUrl = (p: Publication): string | null =>
  p.doi ? `https://doi.org/${p.doi}` : p.arxiv ? `https://arxiv.org/abs/${p.arxiv}` : null;
