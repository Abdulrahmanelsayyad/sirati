"""Add an owner-only feedback dashboard shortcut to the existing mobile/site drawer.

UI discoverability only: no changes to authentication, data, RLS, or access rules.
The dashboard enforces the same trusted app_metadata claim and database RLS.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
path = root / "components" / "SiratiSiteMenu.tsx"
source = path.read_text(encoding="utf-8")
anchor = '          <NavGroup title="السيرة الذاتية" items={cvFeatures} close={close} />'
if source.count(anchor) != 1 or "sirati-feedback-owner-link" in source:
    raise RuntimeError("Owner feedback menu: unexpected existing navigation layout")

owner_link = """          {user?.app_metadata?.sirati_feedback_admin === true && (
            <section className="sirati-menu-group" aria-label="Owner tools · أدوات المالك">
              <h3>لوحة التحكم · Owner dashboard</h3>
              <a className="sirati-menu-item sirati-feedback-owner-link"
                href={withBasePath('/feedback-dashboard/')} onClick={close}>
                <span className="sirati-menu-icon" aria-hidden="true">★</span>
                <span className="sirati-menu-item-copy">
                  <strong>تقييمات المستخدمين</strong>
                  <small>Visitor feedback · خاص بالمالك</small>
                </span>
                <span className="sirati-menu-arrow" aria-hidden="true">‹</span>
              </a>
            </section>
          )}
"""
source = source.replace(anchor, owner_link + anchor, 1)
path.write_text(source, encoding="utf-8")
print("PASS: owner-only feedback dashboard shortcut added to site menu")
