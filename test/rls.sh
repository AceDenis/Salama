#!/bin/bash
# Role and privacy tests against the real schema. Each block prints PASS or FAIL.
export PGHOST=/var/tmp/pgt PGPORT=54329
/home/claude/salama/tools/reset_db.sh >/dev/null 2>&1
P="psql -U postgres -d salama -tA -v ON_ERROR_STOP=0"
NURSE=11111111-1111-1111-1111-111111111111; RES=22222222-2222-2222-2222-222222222222
W=33333333-3333-3333-3333-333333333333; I=44444444-4444-4444-4444-444444444444; A=55555555-5555-5555-5555-555555555555
UU=aaaaaaaa-0000-0000-0000-000000000001
t() { # name expected(ok|deny) sql role uid
  local out; out=$($P -c "set role $4; select set_config('test.uid','$5',false); $3" 2>&1 | grep -v -E '^SET$|^[0-9a-f]{8}-[0-9a-f-]{27}$|^$' | tr '\n' ' ')
  out="${out//[[:space:]]/ }"
  if [[ "$2" == "ok" && "$out" != *ERROR* && "$out" != *"permission denied"* && "$out" != "0 " && "$out" != " " && -n "${out// /}" ]] || [[ "$2" == "deny" && ( "$out" == *ERROR* || "$out" == "0 " || -z "${out// /}" ) ]]; then echo "PASS $1"; else echo "FAIL $1 -> [$out]"; fi; }
# anon inserts
t "anon can insert a response" ok "insert into public.responses(client_uuid,form,grp,answers) values (gen_random_uuid(),'pulse','personnel','{}') returning 'ins';" anon ""
t "anon cannot read responses" deny "select count(*) from public.responses;" anon ""
t "anon can insert college_sharing" ok "insert into public.college_sharing(client_uuid,anon_code,ref_text,band,context,consent_version) values ('$UU','ABCD-EFGH','INT-1',3,'selection','S1') returning 'ins';" anon ""
t "anon cannot read college_sharing" deny "select count(*) from public.college_sharing;" anon ""
t "anon cannot set status on insert" deny "insert into public.college_sharing(client_uuid,ref_text,band,status) values (gen_random_uuid(),'X1',1,'closed');" anon ""
# staff reads
t "welfare reads college_sharing" ok "select ref_text from public.college_sharing limit 1;" authenticated $W
t "nurse cannot read college_sharing" deny "select count(*) from public.college_sharing;" authenticated $NURSE
t "researcher cannot read college_sharing" deny "select count(*) from public.college_sharing;" authenticated $RES
t "interviewer cannot list college_sharing" deny "select count(*) from public.college_sharing;" authenticated $I
t "interviewer can look up exact ref" ok "select band_label from public.college_colour('int-1');" authenticated $I
t "researcher cannot call colour look-up" deny "select * from public.college_colour('INT-1');" authenticated $RES
t "nurse cannot call colour look-up" deny "select * from public.college_colour('INT-1');" authenticated $NURSE
t "interviewer cannot read audit log" deny "select count(*) from public.access_log;" authenticated $I
t "admin reads audit log (look-up was recorded)" ok "select count(*) from public.access_log where user_id='$I';" authenticated $A
$P -c "select 'AUDIT ROWS', count(*) from public.access_log" 
t "welfare can update support status only" ok "update public.college_sharing set status='support_offered' where client_uuid='$UU' returning 'upd';" authenticated $W
t "welfare cannot change the colour" deny "update public.college_sharing set band=1 where client_uuid='$UU';" authenticated $W
# withdraw
t "anon can withdraw with secret reference" ok "select public.withdraw_share('$UU');" anon ""
$P -c "select 'AFTER WITHDRAW', count(*) from public.college_sharing"
# outcomes
t "researcher can add outcomes" ok "insert into public.cohort_outcomes(anon_code,intake,status,exit_month,reason) values ('ABCD-EFGH','2026-09',4,3,3) returning 'ins';" authenticated $RES
t "nurse cannot add outcomes" deny "insert into public.cohort_outcomes(anon_code,intake,status) values ('ZZZZ-9999','2026-09',1);" authenticated $NURSE
t "welfare cannot read outcomes" deny "select count(*) from public.cohort_outcomes;" authenticated $W
t "welfare cannot read applicant data" deny "select count(*) from public.v_student_screen;" authenticated $W
t "interviewer cannot read applicant data" deny "select count(*) from public.responses;" authenticated $I
t "researcher cannot read nurse queue contact hints" deny "select contact_hint from public.service_requests;" authenticated $RES
t "outcomes cannot hold a name" deny "insert into public.cohort_outcomes(anon_code,intake,status) values ('John Mwangi','2026-09',1);" authenticated $RES
