from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
path = root / "app" / "builder" / "page.tsx"
text = path.read_text(encoding="utf-8")

marker = "function accountDraftStorageKey(userId: string)"
if marker not in text:
    constants = """const STORAGE_KEY = 'sirati.cv.v2';
const LEGACY_STORAGE_KEY = 'sirati.cv.v1';
"""
    replacement = """const STORAGE_KEY = 'sirati.cv.v2';
const LEGACY_STORAGE_KEY = 'sirati.cv.v1';

function accountDraftStorageKey(userId: string) {
  return \`\${STORAGE_KEY}.\${userId}\`;
}
"""
    if constants not in text:
        raise SystemExit("Could not locate builder storage constants")
    text = text.replace(constants, replacement, 1)

# When cloud accounts are configured, never auto-load the shared legacy device draft.
# It is deliberately preserved in localStorage for recovery, but account sessions use
# user-scoped draft keys to prevent cross-account exposure on shared browsers.
old_else = """    } else {
      const raw = localStorage.getItem(STORAGE_KEY) || localStorage.getItem(LEGACY_STORAGE_KEY);
"""
new_else = """    } else if (!isSupabaseConfigured()) {
      const raw = localStorage.getItem(STORAGE_KEY) || localStorage.getItem(LEGACY_STORAGE_KEY);
"""
if old_else in text:
    text = text.replace(old_else, new_else, 1)
elif new_else not in text:
    raise SystemExit("Could not locate initial local draft hydration block")

old_save = """  useEffect(() => {
    if (!hydrated) return;
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ version: 2, data, template, language }));
  }, [data, template, language, hydrated]);
"""
new_save = """  useEffect(() => {
    if (!hydrated) return;

    const payload = JSON.stringify({ version: 2, data, template, language });
    if (isSupabaseConfigured()) {
      if (!userId) return;
      localStorage.setItem(accountDraftStorageKey(userId), payload);
      return;
    }

    localStorage.setItem(STORAGE_KEY, payload);
  }, [data, template, language, hydrated, userId]);
"""
if old_save in text:
    text = text.replace(old_save, new_save, 1)
elif new_save not in text:
    raise SystemExit("Could not locate local draft save effect")

old_no_doc = """      const requestedDocumentId = new URLSearchParams(window.location.search).get('doc');
      if (!requestedDocumentId) {
        setCloudStatus('Signed in · local draft');
        cloudReadyRef.current = true;
        return;
      }
"""
new_no_doc = """      const requestedDocumentId = new URLSearchParams(window.location.search).get('doc');
      if (!requestedDocumentId) {
        const raw = localStorage.getItem(accountDraftStorageKey(user.id));
        if (raw) {
          try {
            const parsed = JSON.parse(raw);
            setData(normalizeCv(parsed.data));
            setTemplate(
              parsed.template === 'classic' ||
              parsed.template === 'compact' ||
              parsed.template === 'compact-ats'
                ? parsed.template
                : 'modern'
            );
            setLanguage(parsed.language === 'ar' ? 'ar' : 'en');
          } catch {
            // Keep the new blank CV when this user's device draft is invalid.
          }
        }

        setCloudStatus('Signed in · device draft');
        cloudReadyRef.current = true;
        return;
      }
"""
if old_no_doc in text:
    text = text.replace(old_no_doc, new_no_doc, 1)
elif new_no_doc not in text:
    raise SystemExit("Could not locate signed-in local draft branch")

path.write_text(text, encoding="utf-8")
print("Applied account-scoped local draft storage.")
