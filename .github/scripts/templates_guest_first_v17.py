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
    'template-carousel-track',
    'template-library-grid',
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

# The original three-step indicator predated guest editing. Keep its caller
# contract (1 = auth, 2 = templates, 3 = builder), but describe the actual flow.
indicator = root / 'components/OnboardingSteps.tsx'
indicator.write_text('''type Props = {
  current: 1 | 2 | 3;
  language?: 'en' | 'ar';
};

export default function OnboardingSteps({ current, language = 'en' }: Props) {
  // Account pages can be opened independently: do not invent CV progress there.
  if (current === 1) return null;
  const arabic = language === 'ar';
  const active = current - 1;
  const steps = arabic ? [
    ['اختيار القالب', 'اختر التصميم'],
    ['كتابة السيرة', 'راجع بياناتك'],
    ['تنزيل PDF', 'مجاني · يلزم حساب']
  ] : [
    ['Choose template', 'Your style'],
    ['Build your CV', 'Review your details'],
    ['Download PDF', 'Free · Account required']
  ];
  return (
    <nav className="journey-steps" dir={arabic ? 'rtl' : 'ltr'}
      aria-label={arabic ? 'مراحل إنشاء السيرة' : 'CV creation progress'}>
      {steps.map(([label, hint], index) => {
        const number = index + 1;
        const state = number < active ? 'complete' : number === active ? 'active' : 'upcoming';
        return (
          <div className="journey-step-wrap" key={number}>
            <div className={`journey-step ${state}`} aria-current={state === 'active' ? 'step' : undefined}>
              <span className="journey-number" aria-hidden="true">{state === 'complete' ? '✓' : number}</span>
              <span className="journey-copy">
                <strong>{label}</strong><small>{hint}</small>
              </span>
            </div>
            {index < steps.length - 1 && <span className={`journey-line ${number < active ? 'complete' : ''}`} aria-hidden="true" />}
          </div>
        );
      })}
    </nav>
  );
}
''', encoding='utf-8')
once('<OnboardingSteps current={2} />',
     '<OnboardingSteps current={2} language={language} />', 'localized template progress')
once('STEP 2 OF 3', "{language === 'ar' ? 'الخطوة ١ من ٣' : 'STEP 1 OF 3'}",
     'template step number')
page.write_text(source, encoding='utf-8')
builder = root / 'app/builder/page.tsx'
builder_source = builder.read_text(encoding='utf-8')
for old, new in (
    ('<OnboardingSteps current={3} />', '<OnboardingSteps current={3} language={language} />'),
    ('STEP 3 OF 3 · BUILD YOUR CV',
     "{language === 'ar' ? 'الخطوة ٢ من ٣ · كتابة السيرة' : 'STEP 2 OF 3 · BUILD YOUR CV'}"),
):
    if builder_source.count(old) != 1:
        raise RuntimeError('Guest journey progress: Builder presentation anchor changed')
    builder_source = builder_source.replace(old, new, 1)
builder.write_text(builder_source, encoding='utf-8')
print('PASS: guest progress follows template → edit → download; account page has no assumed CV state.')
