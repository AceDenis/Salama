#!/bin/bash
# Rebuild everything and run all tests. Usage: test/run_all.sh
set -e
cd /home/claude/salama
python3 tools/build.py
python3 - <<'PY'
import sys,json; sys.path.insert(0,"tools")
import instrument as I
instr={k:dict(title=v["title"],minutes=v["minutes"],groups=v["groups"],sections=v["sections"]) for k,v in I.FORMS.items()}
json.dump({"INSTRUMENT":instr,"SCALES":I.SCALES},open("test/instr.json","w"))
PY
tools/reset_db.sh
node test/gen_answers.js 60 7
echo "--- parity (database scores vs app scores)"; python3 test/parity.py
echo "--- roles and privacy"; test/rls.sh | grep -c PASS; test/rls.sh | grep FAIL || true
echo "--- browser flows (demo mode)"; python3 test/e2e.py | tail -1
pkill -f test/mock_rest.py 2>/dev/null || true; (python3 test/mock_rest.py 8787 >/dev/null 2>&1 &); sleep 1.5
echo "--- full chain: app -> PostgreSQL -> console -> jamovi CSV"; python3 test/e2e_live.py | tail -1
echo "--- portal"; python3 test/e2e_portal.py | tail -1
