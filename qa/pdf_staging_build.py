"""Reuse existing build-only Staging configuration; never deploy or authenticate."""
import os,re,subprocess
from pathlib import Path
repo=Path(__file__).resolve().parents[1]
workflow=(repo/'.github/workflows/staging-pdf-preview.yml').read_text()
env=os.environ.copy()
for name in ['NEXT_PUBLIC_BASE_PATH','NEXT_PUBLIC_SUPABASE_URL','NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY','NEXT_PUBLIC_SITE_URL']:
    value=re.search(r'^      '+name+r': (.+)$',workflow,re.M)
    assert value, 'Missing existing Staging build setting: '+name
    env[name]=value.group(1).strip("'\"")
env.update(NEXT_PUBLIC_ANALYTICS_ENABLED='false',NEXT_TELEMETRY_DISABLED='1')
# Reconstructed production tree already excludes all synthetic fixture routes.
source=repo/'production-src/sirati-cv-source'
subprocess.run(['npm','run','build'],cwd=source,env=env,check=True)
subprocess.run(['python3',str(repo/'qa/staging_bundle_guard.py'),str(source/'out')],check=True)
print('PASS: existing Staging-only build configuration and bundle guard; no deployment')
