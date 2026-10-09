"""Professional, profession-neutral mobile builder header for Sirati.

Applies only during the existing source preparation step.
Does not change authentication, persistence, payment, or PDF logic.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
builder = root / "app" / "builder" / "page.tsx"
styles = root / "app" / "globals.css"

old_header = """      <header className="container nav no-print wizard-builder-nav">
        <Link href="/" className="brand">Sirati</Link>
        <div className="toolbar toolbar-top">
          {userId && <Link className="btn btn-secondary" href="/documents">My documents</Link>}
          <button className="btn btn-secondary" onClick={() => setData(normalizeCv(sampleNurseCv))}>Try nursing sample</button>
          <button className="btn btn-secondary" onClick={() => window.location.href = withBasePath('/templates')}>New CV</button>
          <button className="btn btn-primary" onClick={() => saveToAccount(true)}>{documentId ? 'Save version' : 'Save to account'}</button>
        </div>
      </header>"""

new_header = """      <header className="container nav no-print wizard-builder-nav sirati-builder-nav">
        <Link href="/" className="brand sirati-builder-brand">Sirati</Link>
        <div className="sirati-builder-actions">
          {userId && <Link className="btn btn-secondary sirati-builder-action sirati-builder-docs" href="/documents">My CVs</Link>}
          <details className="sirati-header-samples">
            <summary className="btn btn-secondary sirati-builder-action">Explore samples</summary>
            <div className="sirati-header-samples-menu">
              <strong>Choose an example CV</strong>
              <p>Demo data only. Replace it with your own information.</p>
              {headerSampleChoices.map(choice => (
                <button
                  type="button"
                  key={choice.category}
                  onClick={event => {
                    if (!window.confirm('Load this example? Your current CV draft will be replaced.')) return;
                    event.currentTarget.closest('details')?.removeAttribute('open');
                    setData(normalizeCv(makeHeaderSampleCv(choice)));
                  }}
                >
                  <span>{choice.category}</span>
                  <small>{choice.role}</small>
                </button>
              ))}
            </div>
          </details>
          <button type="button" className="btn btn-secondary sirati-builder-action sirati-builder-new" onClick={() => window.location.href = withBasePath('/templates')}>New CV</button>
          <button type="button" className="btn btn-primary sirati-builder-action sirati-builder-save" onClick={() => saveToAccount(true)}>{documentId ? 'Save version' : 'Save CV'}</button>
        </div>
      </header>"""

sample_helpers = """const headerSampleChoices = [
  { category: 'Healthcare', role: 'Healthcare Professional', profile: 'Healthcare professional with a focus on clear communication, accurate documentation, service quality and teamwork.', skills: 'Communication, Documentation, Teamwork, Quality, Patient Support' },
  { category: 'Technology', role: 'Software Developer', profile: 'Technology professional focused on practical problem-solving, reliable software delivery, testing and clear technical documentation.', skills: 'Software Development, Debugging, Testing, Collaboration, Documentation' },
  { category: 'Business', role: 'Operations Coordinator', profile: 'Business professional experienced in organizing workflows, coordinating schedules, maintaining records and supporting team delivery.', skills: 'Coordination, Reporting, Excel, Scheduling, Communication' },
  { category: 'Education', role: 'Teacher', profile: 'Education professional focused on lesson planning, clear communication, student engagement and continuous improvement.', skills: 'Lesson Planning, Communication, Classroom Organization, Assessment, Collaboration' }
] as const;

function makeHeaderSampleCv(example: (typeof headerSampleChoices)[number]): CvData {
  return {
    ...emptyCv,
    fullName: 'Sample Candidate',
    title: example.role,
    email: 'sample@example.com',
    location: 'Your City',
    profile: example.profile,
    skills: example.skills,
    languages: 'Language — proficiency level',
    experience: [{
      id: 'sample-experience-1',
      role: example.role,
      company: 'Example Organization',
      location: 'Your City',
      period: '20XX — Present',
      details: 'Example: Describe your responsibilities and measurable outcomes here. Replace this entire sample with your own experience.'
    }],
    education: [{
      id: 'sample-education-1',
      degree: 'Your degree or qualification',
      school: 'Institution name',
      location: 'Your City',
      period: 'Year',
      details: ''
    }],
    certifications: [],
    courses: [],
    projects: []
  };
}

"""

source = builder.read_text(encoding="utf-8")
if source.count(old_header) != 1:
    raise RuntimeError("Expected builder header not found exactly once; UI patch aborted")

source = source.replace(old_header, new_header, 1)
anchor = "const STORAGE_KEY = 'sirati.cv.v2';"
if source.count(anchor) != 1:
    raise RuntimeError("Cannot place profession-neutral CV samples safely")
source = source.replace(anchor, sample_helpers + anchor, 1)
source = source.replace("import { emptyCv, sampleNurseCv } from '@/lib/defaultCv';", "import { emptyCv } from '@/lib/defaultCv';")
builder.write_text(source, encoding="utf-8")

css_marker = "/* Sirati professional builder toolbar */"
css = styles.read_text(encoding="utf-8")
if css_marker in css:
    raise RuntimeError("Builder toolbar styles already applied")
css += """
/* Sirati professional builder toolbar */
.sirati-builder-nav {
  display: flex;
  flex-wrap: nowrap;
  align-items: center;
  gap: 16px;
  padding-block: 16px;
}
.sirati-builder-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  flex-wrap: wrap;
  gap: 8px;
  margin-left: auto;
}
.sirati-builder-action {
  min-height: 40px;
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 700;
  white-space: nowrap;
}
.sirati-header-samples { position: relative; }
.sirati-header-samples > summary { list-style: none; }
.sirati-header-samples > summary::-webkit-details-marker { display: none; }
.sirati-header-samples[open] > summary { background: #e9f0ec; }
.sirati-header-samples-menu {
  position: absolute;
  top: calc(100% + 9px);
  right: 0;
  width: min(320px, calc(100vw - 36px));
  z-index: 80;
  padding: 12px;
  border: 1px solid var(--line);
  border-radius: 16px;
  background: #fffefa;
  box-shadow: 0 16px 40px rgba(25,40,34,.14);
}
.sirati-header-samples-menu > strong { display: block; font-size: 14px; }
.sirati-header-samples-menu > p {
  margin: 4px 0 10px;
  font-size: 12px;
  line-height: 1.4;
  color: var(--muted);
}
.sirati-header-samples-menu > button {
  display: flex;
  width: 100%;
  flex-direction: column;
  gap: 3px;
  align-items: flex-start;
  padding: 10px 12px;
  border: none;
  border-radius: 10px;
  background: transparent;
  cursor: pointer;
  text-align: left;
}
.sirati-header-samples-menu > button:hover,
.sirati-header-samples-menu > button:focus-visible { background: #edf3ef; outline-offset: 2px; }
.sirati-header-samples-menu > button > span { font-size: 13px; font-weight: 700; }
.sirati-header-samples-menu > button > small { color: var(--muted); font-size: 11px; }
@media (max-width: 640px) {
  .sirati-builder-nav {
    display: grid;
    grid-template-columns: repeat(6, minmax(0, 1fr));
    gap: 8px;
    padding-block: 12px;
    align-items: center;
  }
  .sirati-builder-nav > .sirati-builder-brand {
    grid-column: 1 / 5;
    grid-row: 1;
    font-size: 25px;
  }
  .sirati-builder-actions { display: contents; }
  .sirati-builder-actions > .sirati-builder-save {
    grid-column: 5 / 7;
    grid-row: 1;
  }
  .sirati-builder-actions > .sirati-builder-docs,
  .sirati-builder-actions > .sirati-header-samples,
  .sirati-builder-actions > .sirati-builder-new { grid-column: span 2; }
  .sirati-builder-action {
    width: 100%;
    min-height: 40px;
    padding: 9px 6px;
    justify-content: center;
    text-align: center;
    font-size: 12px;
  }
  .sirati-header-samples-menu { left: 0; right: auto; }
}
"""
styles.write_text(css, encoding="utf-8")
print("Applied profession-neutral builder header, 4 opt-in demo examples and compact mobile styling.")
