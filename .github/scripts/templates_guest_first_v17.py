"""Sirati stage 1: show the public CV template gallery without an auth round-trip.
Applied last, after all existing template/gallery generators. Fail closed on drift.
The Builder continues to enforce its own account checks when needed.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
page = root / 'app/templates/page.tsx'
source = page.read_text(encoding='utf-8')

def once(old, new, label):
    global source
    count = source.count(old)
    if count != 1:
        raise RuntimeError(f'Public templates {label}: expected 1 source anchor, got {count}')
    source = source.replace(old, new, 1)

once(
    "import { createClient, isSupabaseConfigured } from '@/lib/supabase/client';\n",
    "",
    "unneeded templates auth imports"
)
once("  const [checking, setChecking] = useState(true);\n", "",
     "blocking account checking state")
once("    if (checking || !carouselRef.current) return;",
     "    if (!carouselRef.current) return;",
     "carousel no longer waits for account")
once("  }, [checking, syncCarouselNavigation]);",
     "  }, [syncCarouselNavigation]);",
     "carousel dependency")

blocking_effect = """  useEffect(() => {
    if (!isSupabaseConfigured()) {
      setChecking(false);
      return;
    }
    const supabase = createClient();
    supabase?.auth.getUser().then(({ data }) => {
      if (!data.user) {
        window.location.href = withBasePath('/auth?next=/templates');
        return;
      }
      setChecking(false);
    });
  }, []);

"""
once(blocking_effect, "", "guest redirect and suspended account lookup")
once("""  if (checking) {
    return <main className="flow-page"><div className="flow-loading">Checking your account…</div></main>;
  }

""","", "blocking loading UI")

for required in (
    'const templateOptions:',
    'function continueToBuilder()',
    "localStorage.setItem('sirati.onboarding.template', template);",
    'window.location.href = withBasePath(',
    '<OnboardingSteps current={2} />',
    'className="template-carousel-track"',
    'className="template-library-grid"',
    '<CvPreview',
):
    if required not in source:
        raise RuntimeError(f'Public templates: required existing feature missing: {required}')
for forbidden in (
    'setChecking', 'if (checking)', 'Checking your account',
    'auth.getUser()', '/auth?next=/templates',
):
    if forbidden in source:
        raise RuntimeError(f'Public templates: obsolete auth gate still present: {forbidden}')
page.write_text(source, encoding='utf-8')
print('PASS: public gallery loads independently of auth; existing template and Builder route preserved.')
