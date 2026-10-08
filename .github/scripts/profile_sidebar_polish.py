"""Polish Profile Sidebar photo framing and editorial resume hierarchy.

Inspired by customer-supplied circular-portrait/sidebar examples; original
CSS layout only, no images or text copied from reference designs. This runs
after profile_sidebar_template.py so it does not touch persisted CV data.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
css_path = root / "app/globals.css"
css = css_path.read_text(encoding="utf-8")
marker = "/* Profile Sidebar portrait polish v2: circular integrated frame */"
if marker in css:
    raise RuntimeError("Portrait polish already applied")
if "/* Profile Sidebar true two-column template */" not in css:
    raise RuntimeError("Profile Sidebar must run first")
css += r'''

/* Profile Sidebar portrait polish v2: circular integrated frame */
/* A deliberate dark rail + white document, inspired by the supplied references.
   The actual user's image remains optional, local, and controlled by the Builder. */
.cv-sheet.template-profile-sidebar {
  color: #24313e;
  font-family: Arial, Helvetica, sans-serif;
  line-height: 1.5;
}
.cv-sheet.template-profile-sidebar .profile-sidebar-layout {
  grid-template-columns: 32% minmax(0, 1fr);
}
.cv-sheet.template-profile-sidebar .profile-sidebar-rail {
  background: #183b57;
  color: #f1f6fb;
  padding: 44px 23px 39px;
  print-color-adjust: exact;
  -webkit-print-color-adjust: exact;
}
.cv-sheet.template-profile-sidebar .profile-sidebar-portrait-wrap {
  position: relative;
  width: 172px;
  height: 172px;
  max-width: 100%;
  margin: 0 auto 32px;
  display: grid;
  place-items: center;
  isolation: isolate;
}
.cv-sheet.template-profile-sidebar .profile-sidebar-portrait-wrap::before {
  content: "";
  position: absolute;
  inset: 0;
  border-radius: 50%;
  border: 1px solid rgba(255,255,255,.28);
  pointer-events: none;
}
.cv-sheet.template-profile-sidebar .profile-sidebar-portrait,
.cv-sheet.template-profile-sidebar .profile-sidebar-portrait-placeholder {
  display: block;
  position: relative;
  z-index: 1;
  box-sizing: border-box;
  width: 154px;
  height: 154px;
  max-width: none;
  min-width: 0;
  aspect-ratio: 1 / 1;
  border: 5px solid #fff;
  border-radius: 50%;
  overflow: hidden;
  box-shadow: 0 8px 19px rgba(4,22,37,.25);
}
.cv-sheet.template-profile-sidebar .profile-sidebar-portrait {
  object-fit: cover;
  object-position: 50% 30%;
  image-rendering: auto;
}
.cv-sheet.template-profile-sidebar .profile-sidebar-portrait-placeholder {
  display: grid;
  place-items: center;
  background: linear-gradient(145deg, #dce8ef, #aac7d8);
  color: #193d59;
}
.cv-sheet.template-profile-sidebar .profile-sidebar-portrait-placeholder svg {
  width: 102px;
  height: 116px;
  max-width: 100%;
  max-height: 100%;
  display: block;
}
.cv-sheet.template-profile-sidebar .profile-sidebar-block {
  margin-bottom: 26px;
}
.cv-sheet.template-profile-sidebar .profile-sidebar-block h2 {
  border-bottom: 1px solid rgba(244,249,252,.46);
  padding-bottom: 9px;
  margin-bottom: 12px;
  letter-spacing: 1.1px;
  font-size: 11.5px;
  font-weight: 800;
  color: #fff;
}
.cv-sheet.template-profile-sidebar .profile-sidebar-contact {
  gap: 11px;
}
.cv-sheet.template-profile-sidebar .profile-sidebar-contact strong {
  color: #bfd5e4;
}
.cv-sheet.template-profile-sidebar .profile-sidebar-skills,
.cv-sheet.template-profile-sidebar .profile-sidebar-languages {
  gap: 7px;
}
.cv-sheet.template-profile-sidebar .profile-sidebar-skills li {
  padding-bottom: 6px;
  border-color: rgba(255,255,255,.11);
}
.cv-sheet.template-profile-sidebar .profile-sidebar-main {
  padding: 63px 44px 45px 39px;
}
.cv-sheet.template-profile-sidebar .profile-sidebar-head {
  margin-bottom: 33px;
  padding-bottom: 19px;
  border-bottom: 1px solid #cad5de;
  position: relative;
}
.cv-sheet.template-profile-sidebar .profile-sidebar-head::after {
  content: "";
  position: absolute;
  inset-inline-start: 0;
  bottom: -2px;
  height: 3px;
  width: 54px;
  background: #183b57;
}
.cv-sheet.template-profile-sidebar .profile-sidebar-head h1 {
  color: #183b57;
  font-size: 30px;
  font-weight: 800;
  letter-spacing: .35px;
  line-height: 1.12;
  margin-bottom: 9px;
}
.cv-sheet.template-profile-sidebar .profile-sidebar-head p {
  color: #4d6273;
  font-size: 12.5px;
  letter-spacing: .7px;
}
.cv-sheet.template-profile-sidebar .profile-sidebar-section {
  margin-bottom: 21px;
}
.cv-sheet.template-profile-sidebar .profile-sidebar-section h2 {
  color: #183b57;
  border-bottom: 1px solid #aebcc9;
  letter-spacing: .8px;
  font-size: 12.5px;
  padding-bottom: 5px;
  margin-bottom: 10px;
}
.cv-sheet.template-profile-sidebar .profile-sidebar-entry-heading strong {
  color: #183b57;
}
[dir="rtl"].cv-sheet.template-profile-sidebar .profile-sidebar-main {
  padding: 63px 39px 45px 44px;
}
[dir="rtl"].cv-sheet.template-profile-sidebar .profile-sidebar-head h1,
[dir="rtl"].cv-sheet.template-profile-sidebar .profile-sidebar-head p,
[dir="rtl"].cv-sheet.template-profile-sidebar .profile-sidebar-section h2 {
  letter-spacing: 0;
}
@media (max-width: 920px) {
  .cv-sheet.template-profile-sidebar .profile-sidebar-rail { padding: 28px 17px 30px; }
  .cv-sheet.template-profile-sidebar .profile-sidebar-portrait-wrap {
    width: 138px; height: 138px; margin-bottom: 24px;
  }
  .cv-sheet.template-profile-sidebar .profile-sidebar-portrait,
  .cv-sheet.template-profile-sidebar .profile-sidebar-portrait-placeholder {
    width: 124px; height: 124px; border-width: 4px;
  }
  .cv-sheet.template-profile-sidebar .profile-sidebar-main,
  [dir="rtl"].cv-sheet.template-profile-sidebar .profile-sidebar-main { padding: 37px 26px 31px; }
}
@media (max-width: 560px) {
  .cv-sheet.template-profile-sidebar .profile-sidebar-layout {
    grid-template-columns: 35% minmax(0,1fr);
  }
  .cv-sheet.template-profile-sidebar .profile-sidebar-rail { padding: 19px 9px 23px; }
  .cv-sheet.template-profile-sidebar .profile-sidebar-portrait-wrap {
    width: 98px; height: 98px; margin-bottom: 19px;
  }
  .cv-sheet.template-profile-sidebar .profile-sidebar-portrait,
  .cv-sheet.template-profile-sidebar .profile-sidebar-portrait-placeholder {
    width: 88px; height: 88px; border-width: 3px;
  }
  .cv-sheet.template-profile-sidebar .profile-sidebar-main,
  [dir="rtl"].cv-sheet.template-profile-sidebar .profile-sidebar-main { padding: 23px 13px 24px; }
  .cv-sheet.template-profile-sidebar .profile-sidebar-head { margin-bottom: 16px; padding-bottom: 12px; }
  .cv-sheet.template-profile-sidebar .profile-sidebar-head h1 { font-size: 18px; }
  .cv-sheet.template-profile-sidebar .profile-sidebar-head p { font-size: 10px; }
  .cv-sheet.template-profile-sidebar .profile-sidebar-block h2,
  .cv-sheet.template-profile-sidebar .profile-sidebar-section h2 { font-size: 9px; letter-spacing: 0; }
}
@media print {
  .cv-sheet.template-profile-sidebar .profile-sidebar-layout {
    grid-template-columns: 32% minmax(0,1fr);
    min-height: 297mm;
  }
  .cv-sheet.template-profile-sidebar .profile-sidebar-rail {
    padding: 12mm 6mm 12mm;
    background: #183b57 !important;
  }
  .cv-sheet.template-profile-sidebar .profile-sidebar-main,
  [dir="rtl"].cv-sheet.template-profile-sidebar .profile-sidebar-main {
    padding: 17mm 11mm 12mm;
  }
  .cv-sheet.template-profile-sidebar .profile-sidebar-portrait-wrap {
    width: 48mm;
    height: 48mm;
    margin-bottom: 8mm;
  }
  .cv-sheet.template-profile-sidebar .profile-sidebar-portrait,
  .cv-sheet.template-profile-sidebar .profile-sidebar-portrait-placeholder {
    width: 43mm;
    height: 43mm;
    border: 1.4mm solid #fff;
    border-radius: 50%;
    box-shadow: none;
  }
  .cv-sheet.template-profile-sidebar .profile-sidebar-head h1 { font-size: 21pt; }
}
/* On a phone, the carousel still shows a scaled A4 paper, not a reflowed phone CV. */
@media (max-width: 920px) {
  .flow-shell .template-carousel-track .template-real-preview__stage > .cv-sheet.template-profile-sidebar .profile-sidebar-layout {
    grid-template-columns: 32% minmax(0,1fr);
    min-height: 1122px;
  }
  .flow-shell .template-carousel-track .template-real-preview__stage > .cv-sheet.template-profile-sidebar .profile-sidebar-rail {
    padding: 44px 23px 39px;
  }
  .flow-shell .template-carousel-track .template-real-preview__stage > .cv-sheet.template-profile-sidebar .profile-sidebar-main {
    padding: 63px 44px 45px 39px;
  }
  .flow-shell .template-carousel-track .template-real-preview__stage > .cv-sheet.template-profile-sidebar .profile-sidebar-portrait-wrap {
    width: 172px;
    height: 172px;
    margin-bottom: 32px;
  }
  .flow-shell .template-carousel-track .template-real-preview__stage > .cv-sheet.template-profile-sidebar .profile-sidebar-portrait,
  .flow-shell .template-carousel-track .template-real-preview__stage > .cv-sheet.template-profile-sidebar .profile-sidebar-portrait-placeholder {
    width: 154px;
    height: 154px;
    border-width: 5px;
  }
}
'''
css_path.write_text(css, encoding="utf-8")
print("Polished Profile Sidebar circular portrait and dark-rail/white-page hierarchy.")
