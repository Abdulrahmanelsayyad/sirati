"""V36: English-first Sirati UI copy after V35, with opt-in Arabic left intact.

Only customer-facing literals and English default presentation are changed.
Never change Supabase auth, passwords, data, credentials, PDF data or CV content.
Run after every existing generator, so later patches cannot reinstate double labels.
"""
from pathlib import Path
import re
import sys

root = Path(sys.argv[1]).resolve()
AR = r"\u0600-\u06ff"
# Normalize bilingual *one-piece* UI text without touching language-dependent
# alternatives such as: ar ? '...Arabic...' : '...English...'
AR_EN = re.compile(r"[" + AR + r"][^·\n<>'\"{}]{0,160}\s*·\s*(?P<en>[A-Za-z][^<>'\"{}\n]{0,180})")
EN_AR = re.compile(r"(?P<en>[A-Za-z][^·\n<>'\"{}]{0,160})\s*·\s*[" + AR + r"][^<>'\"{}\n]{0,160}")

def change(relative, mapping=(), clean=True):
    path = root / relative
    if not path.is_file():
        raise RuntimeError("V36 expected generated UI file: " + relative)
    source = path.read_text(encoding="utf-8")
    if clean:
        source = AR_EN.sub(lambda match: match["en"].strip(), source)
        source = EN_AR.sub(lambda match: match["en"].strip(), source)
    for before, after in mapping:
        if before in source:
            source = source.replace(before, after)
    if clean:
        source = AR_EN.sub(lambda match: match["en"].strip(), source)
        source = EN_AR.sub(lambda match: match["en"].strip(), source)
    path.write_text(source, encoding="utf-8")

# Authentication retains English/Arabic controls; English is default and
# explicitly selecting Arabic or using ?lang=ar still shows its translations.
change("app/auth/page.tsx", [
    ("useState<Language>('ar')", "useState<Language>('en')"),
])

# Utility screens do not have their own language picker. Show clean English
# instead of one Arabic + one English version of each instruction.
change("app/auth/confirm/page.tsx")
change("app/auth/recovery/page.tsx", [
    ("إذا كان البريد مسجلًا، ستصلك رسالة برابط الاستعادة. افحص البريد غير المرغوب أيضًا. · If the account exists, a reset email will arrive. Check spam as well.",
     "If the account exists, a reset email will arrive. Check spam as well."),
])
change("app/account/password/page.tsx", [
    ("الحساب: <strong>", "Account: <strong>"),
])
menu_map = {
    "إنشاء CV": "Build a CV",
    "مكتبة القوالب": "CV Templates",
    "مساعد الكتابة الذكي": "Smart CV Assistant",
    "مراجعة جودة السيرة": "CV Quality Review",
    "طباعة السيرة PDF": "Download PDF",
    "خطاب التقديم": "Cover Letter",
    "ملف LinkedIn": "LinkedIn Profile",
    "التحضير للمقابلة": "Interview Preparation",
    "مساحة العمل": "Workspace",
    "مستنداتي المحفوظة": "My Documents",
    "الرئيسية": "Home",
    "السيرة الذاتية": "CV Tools",
    "أدوات التطوير المهني": "Career Tools",
    "المساعدة": "Help & Support",
    "الأسئلة الشائعة": "FAQs",
    "التواصل والدعم": "Contact & Support",
    "الملف الشخصي وبياناتي": "My Profile",
    "جارٍ تحميل الحساب…": "Loading account…",
    "حسابك في Sirati": "Your Sirati Account",
    "سجّل دخولك لإظهار بياناتك ومستنداتك": "Sign in to view your profile and documents",
    "تسجيل الدخول": "Sign in",
    "تقييمات المستخدمين": "Visitor Feedback",
    "استوديو المسار المهني": "Career Studio",
    "لوحة التحكم": "Dashboard",
    "خاص بالمالك": "Owner only",
    "أدوات المالك": "Owner tools",
    "البحث عن أداة": "Search features",
    "مثال: LinkedIn أو CV أو خطاب": "Try LinkedIn, CV or Cover Letter",
    "ابحث بالعربي أو الإنجليزي للوصول للأداة بسرعة": "Find CV and career tools quickly",
    "لا توجد أدوات مطابقة": "No matching tools",
    "No matching tools. Try CV, LinkedIn or Interview.": "Try CV, LinkedIn or Interview.",
    "إظهار كل الأدوات": "Show all",
    "كل الأدوات مجانية": "All tools are free",
}
change("components/SiratiSiteMenu.tsx",
    list(sorted(menu_map.items(), key=lambda pair: -len(pair[0]))) + [
    ('dir="rtl"', 'dir="ltr"'),
    # Keep legacy Arabic search alias without displaying a translated title.
    ("const matches = (item: Item) => (item.title + ' ' + item.detail).toLocaleLowerCase().includes(query);",
     "const matches = (item: Item) => (item.title + ' ' + item.detail + (item.route.includes('tool=letter') ? ' خطاب' : '')).toLocaleLowerCase().includes(query);"),
    ("      'قد توجد تغييرات غير محفوظة. احفظ السيرة في مستنداتي أولاً. المتابعة تحذف مسودة الجهاز فقط.'", "      ''"),
    ("<span className=\"sirati-menu-arrow\" aria-hidden=\"true\">‹</span>",
     "<span className=\"sirati-menu-arrow\" aria-hidden=\"true\">›</span>"),
])
# Pure English, accessible copy for the private profile page.
profile_map = {
    'dir="rtl"': 'dir="ltr"',
    "Profile name saved. / تم حفظ الاسم.": "Profile name saved.",
    "الملف الشخصي": "My Profile",
    "راجع بيانات حسابك وأدر اسم العرض الخاص بك. لا تظهر بيانات أي حساب آخر.": "Manage your display name and account details securely.",
    "جارٍ تحميل الحساب…": "Loading account…",
    "سجّل دخولك لعرض بياناتك": "Sign in to view your profile",
    "بيانات الحساب متاحة فقط لصاحب الحساب بعد تسجيل الدخول.": "Your account details are only available when you sign in.",
    "تسجيل الدخول": "Sign in",
    "الاسم الظاهر على الملف الشخصي / Display name": "Display name",
    "جارٍ الحفظ…": "Saving…",
    "حفظ الاسم": "Save name",
    "البريد الإلكتروني / Email": "Email",
    "حالة البريد / Email status": "Email status",
    "مؤكد / Verified": "Verified",
    "غير مؤكد / Not verified": "Not verified",
    "تاريخ إنشاء الحساب / Joined": "Joined",
    "مستنداتي / My documents": "My Documents",
}
change("app/profile/page.tsx", list(sorted(profile_map.items(), key=lambda pair: -len(pair[0]))))

# These are fixed navigation and feedback shells, not CV drafts: remove their
# parallel Arabic captions while preserving user-provided Arabic review text.
change("components/SiratiDocumentIntent.tsx", [
    ('dir="rtl"', 'dir="ltr"'),
    ("اختر سيرة ذاتية محفوظة لفتح اقتراحات الملخص المهني داخل المحرر.",
     "Choose a saved CV to open Smart CV suggestions in the editor."),
    ("اختر سيرة محفوظة لفتح تقرير الجودة داخل المحرر.",
     "Choose a saved CV to open its quality report."),
    ("فتح Smart CV", "Open Smart CV"),
    ("مراجعة الجودة", "Review quality"),
    ("ليس لديك سيرة ذاتية محفوظة بعد. ابدأ بإنشاء سيرة ثم احفظها في مستنداتي.",
     "No saved CVs yet. Create and save a CV first."),
])
change("app/documents/page.tsx")
change("components/SiratiFeedbackRating.tsx", [
    ('dir="rtl"', 'dir="ltr"'),
    ("{ value: 'pdf', label: 'تنزيل PDF' }", "{ value: 'pdf', label: 'PDF download' }"),
    ("aria-label={value + ' of 5 stars · ' + value + ' من 5 نجوم'}",
     "aria-label={value + ' of 5 stars'}"),
    ("إيه الجزء اللي بتقيّمه؟", "Which part are you rating?"),
    ("بنطوّر سيرتي خطوة بخطوة. تقييمك الصادق بيساعدنا نخلّي إنشاء الـCV أسهل وأفضل.",
     "Your feedback helps us make CV creation simpler and more useful."),
    ("Every voice shapes Sirati · كل رأي بيصنع فرق", "Every voice shapes Sirati"),
])
# Remove only the Arabic parallel caption, never the user's own review value.
feedback = root / "components/SiratiFeedbackRating.tsx"
s = feedback.read_text(encoding="utf-8")
s = re.sub(r'<span lang="ar"[^>]*>[^<]*</span>\s*', '', s)
# Standalone Arabic labels immediately followed by English-only inner spans.
s = re.sub(r'[\u0600-\u06ff][^<\n]{0,100}\s*<span lang="en">·\s*([^<]+)</span>',
           lambda m: m.group(1).strip(), s)
feedback.write_text(s, encoding="utf-8")

dashboard_map = {
    'dir="rtl"': 'dir="ltr"',
    "تقييمات المستخدمين <span lang=\"en\">· Visitor feedback</span>": "Visitor feedback",
    "الإحصائيات والتوزيع تشمل أحدث {shown} تقييم فقط (بحد أقصى 200)، وليست بالضرورة كل التقييمات.":
    "Statistics cover only the latest {shown} reviews (up to 200), not necessarily all-time results.",
    "ابحث بكلمة أو قسم…": "Search comments or categories…",
    "{filtered.length} نتيجة من {shown} تقييم محمّل · {filtered.length} matching loaded reviews":
    "{filtered.length} matching reviews from {shown} loaded",
    "الآراء تطوعية وغير موثقة بشكل مستقل. لا تظهر رسائل البريد أو السير الذاتية أو معرفات الحسابات.":
    "Reviews are voluntary and not independently verified. Emails, CVs and account IDs are not displayed.",
    "تعذر تحميل تقييمك السابق. حدّث الصفحة قبل الإرسال لتجنّب استبداله.":
    "Could not load your previous review. Refresh before submitting to avoid overwriting it.",
    "<p>لا توجد نتائج مطابقة · No matching feedback</p>": "<p>No matching feedback</p>",
}
change("app/feedback-dashboard/page.tsx", list(dashboard_map.items()))

# Top-level document language for metadata/browser translation. CV preview
# direction continues to be controlled by its own explicit user choice.
layout = root / "app/layout.tsx"
doc = layout.read_text(encoding="utf-8").replace('<html lang="ar"', '<html lang="en"')
layout.write_text(doc, encoding="utf-8")

auth = (root / "app/auth/page.tsx").read_text(encoding="utf-8")
menu = (root / "components/SiratiSiteMenu.tsx").read_text(encoding="utf-8")
assert "useState<Language>('en')" in auth
assert "lang==='ar'||lang==='en'" in auth
assert 'dir="ltr"' in menu
assert 'withBasePath' in menu
print("PASS: English-first auth, utilities, navigation, profile and feedback; language controls and auth boundaries preserved")
