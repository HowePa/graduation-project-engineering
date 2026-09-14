"""Compile and execute actual Java domain tests; no Spring/MySQL acceptance claim."""
from pathlib import Path
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

out = Path(sys.argv[1]).resolve()
out.mkdir(parents=True, exist_ok=True)
subprocess.run(['javac', '--release', '11', '-encoding', 'UTF-8', '-d', str(out),
                'backend/src/main/java/example/Achievement.java', 'tests/DomainChecks.java'], check=True)
names = ['normal_review', 'reject_review', 'blank_title', 'title_boundary', 'foreign_update',
         'foreign_submit', 'teacher_review', 'draft_review', 'repeat_submit', 'submitted_update']
suite = ET.Element('testsuite', name='AchievementDomain', tests=str(len(names)))
failures = 0
for name in names:
    start = time.monotonic()
    result = subprocess.run(['java', '-cp', str(out), 'example.DomainChecks', name], text=True, capture_output=True)
    case = ET.SubElement(suite, 'testcase', classname='AchievementDomain', name=name, time=str(time.monotonic()-start))
    if result.returncode:
        failures += 1
        ET.SubElement(case, 'failure', message='Java domain assertion failed').text = result.stdout + result.stderr
suite.set('failures', str(failures))
ET.ElementTree(suite).write(out/'junit.xml', encoding='utf-8', xml_declaration=True)
print(f'{len(names)} Java domain cases executed, {failures} failed')
sys.exit(1 if failures else 0)
