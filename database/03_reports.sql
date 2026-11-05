-- =====================================================================
-- Salama Check-In: service, engagement, early-warning and before/after views.
-- Run after 02_views.sql.
-- Views that read the nurse queue run with the owner's rights and check the caller's role,
-- so researchers see times and counts but never contact hints, questions or replies.
-- Group views hide any group of fewer than 10 people. Do not release adjacent groups and totals
-- together, because a hidden cell can then be worked out.
-- =====================================================================

drop view if exists public.v_events;
create view public.v_events with (security_invoker = true) as
  select id, created_at, anon_code, unit_code, event_type, detail from public.events;

drop view if exists public.v_participant_summary cascade;
drop view if exists public.v_service_summary cascade;
drop view if exists public.v_service_requests cascade;
create view public.v_service_requests as
  select id, created_at, ticket_code, anon_code, unit_code, kind, reason, urgency, risk_level, status,
         round((extract(epoch from (first_contact_at - created_at)) / 3600)::numeric, 2) as hours_to_first_contact,
         (case when urgency = 'same_day' and first_contact_at is not null
               then (first_contact_at - created_at) <= interval '8 hours' end)::int as contacted_within_8h,
         (case when urgency = 'routine' and first_contact_at is not null
               then (first_contact_at - created_at) <= interval '7 days' end)::int as contacted_within_7d,
         (visit_completed_at is not null)::int as visit_completed,
         round((extract(epoch from (replied_at - created_at)) / 3600)::numeric, 2) as hours_to_reply
  from public.service_requests
  where public.has_role(array['nurse','researcher','admin']);

create view public.v_service_summary as
  select coalesce(unit_code,'none') as unit_code, kind, urgency, count(*) as requests,
         round((percentile_cont(0.5) within group (order by hours_to_first_contact))::numeric, 2) as median_hours_to_contact,
         round(100.0 * avg(visit_completed), 1) as pct_visit_completed
  from public.v_service_requests
  group by 1, 2, 3
  having count(*) >= 10;

drop view if exists public.v_engagement_weekly;
create view public.v_engagement_weekly with (security_invoker = true) as
  select coalesce(unit_code,'none') as unit_code, date_trunc('week', created_at)::date as week_start,
         count(distinct anon_code) as active_people,
         count(*) filter (where event_type = 'checkin_completed') as checkins,
         count(*) filter (where event_type = 'pulse_completed') as pulses,
         count(*) filter (where event_type = 'lesson_opened') as lessons,
         count(*) filter (where event_type = 'ask_nurse') as questions,
         count(*) filter (where event_type = 'navigator_opened') as navigator_views,
         count(*) filter (where event_type = 'buddy_opened') as buddy_views
  from public.events
  group by 1, 2
  having count(distinct anon_code) >= 10;

-- Weekly early warning from the pulse: what is weighing on each unit this week.
drop view if exists public.v_early_warning;
create view public.v_early_warning with (security_invoker = true) as
  select coalesce(unit_code,'none') as unit_code, date_trunc('week', submitted_at)::date as week_start,
         count(distinct anon_code) as people, count(*) as pulses,
         round(100.0 * avg(pl_poor_sleep), 1) as pct_poor_sleep,
         round(100.0 * avg(pl_high_stress), 1) as pct_high_stress,
         round(100.0 * avg(pl_money_worry), 1) as pct_money_worry,
         round(100.0 * avg((pl_news = 2)::int), 1) as pct_affected_by_events_a_lot,
         round(100.0 * avg((pl_home <= 2)::int) filter (where pl_home <> 9), 1) as pct_home_tense,
         round(100.0 * avg((pl_cue = 1)::int), 1) as pct_cue_money_pay,
         round(100.0 * avg((pl_cue = 2)::int), 1) as pct_cue_debt_lender,
         round(100.0 * avg((pl_cue = 3)::int), 1) as pct_cue_operations_news,
         round(100.0 * avg((pl_cue = 4)::int), 1) as pct_cue_family_home,
         round(100.0 * avg((pl_cue = 5)::int), 1) as pct_cue_online,
         round(100.0 * avg((pl_cue = 6)::int), 1) as pct_cue_loss,
         round(100.0 * avg((pl_cue = 7)::int), 1) as pct_cue_health,
         round(100.0 * avg((pl_cue = 8)::int), 1) as pct_cue_work
  from public.v_pulse
  group by 1, 2
  having count(distinct anon_code) >= 10;

-- Fortnightly signal from check-ins. signal_rise = 1 when the share struggling or worse is at least 10 points
-- above the average of the previous 4 fortnights. 10 points is a starting value for the clinical panel to set.
drop view if exists public.v_signals_fortnightly;
create view public.v_signals_fortnightly with (security_invoker = true) as
  with w as (
    select coalesce(unit_code,'none') as unit_code,
           (date '2026-01-05' + (floor((submitted_at::date - date '2026-01-05') / 14.0) * 14)::int) as fortnight_start,
           count(distinct anon_code) as people, count(*) as checkins,
           100.0 * avg((zone >= 3)::int) as pct_struggling_or_worse,
           100.0 * avg((zone = 4)::int) as pct_needs_care_now,
           100.0 * avg((phq_9 > 0)::int) as pct_item9_positive,
           100.0 * avg((h2 = 1)::int) as pct_unsafe_at_home,
           100.0 * avg(fm_informal) as pct_informal_loan,
           100.0 * avg(fm_security_any) as pct_security_held,
           100.0 * avg(fm_strain) as pct_money_strain,
           100.0 * avg((lp1 = 2)::int) as pct_money_big_problem,
           100.0 * avg((lp3 = 2)::int) as pct_home_conflict_big_problem
    from public.v_checkin group by 1, 2
    having count(distinct anon_code) >= 10)
  select w.unit_code, w.fortnight_start, w.people, w.checkins,
         round(w.pct_struggling_or_worse, 1) as pct_struggling_or_worse, round(w.pct_needs_care_now, 1) as pct_needs_care_now,
         round(w.pct_item9_positive, 1) as pct_item9_positive, round(w.pct_unsafe_at_home, 1) as pct_unsafe_at_home,
         round(w.pct_informal_loan, 1) as pct_informal_loan, round(w.pct_security_held, 1) as pct_security_held,
         round(w.pct_money_strain, 1) as pct_money_strain, round(w.pct_money_big_problem, 1) as pct_money_big_problem,
         round(w.pct_home_conflict_big_problem, 1) as pct_home_conflict_big_problem,
         round(avg(w.pct_struggling_or_worse) over (partition by w.unit_code order by w.fortnight_start rows between 4 preceding and 1 preceding), 1) as prev4_avg_struggling_or_worse,
         (case when w.pct_struggling_or_worse - avg(w.pct_struggling_or_worse) over (partition by w.unit_code order by w.fortnight_start rows between 4 preceding and 1 preceding) >= 10 then 1 else 0 end) as signal_rise
  from w;

-- Monthly unit report from check-ins.
drop view if exists public.v_unit_report;
create view public.v_unit_report with (security_invoker = true) as
  select coalesce(unit_code,'none') as unit_code, date_trunc('month', submitted_at)::date as month,
         count(distinct anon_code) as people, count(*) as checkins,
         round(100.0 * avg((zone = 1)::int), 1) as pct_coping_well, round(100.0 * avg((zone = 2)::int), 1) as pct_strain,
         round(100.0 * avg((zone = 3)::int), 1) as pct_struggling, round(100.0 * avg((zone = 4)::int), 1) as pct_needs_care,
         round(100.0 * avg(phq9_pos), 1) as pct_low_mood_screen_pos, round(100.0 * avg(gad7_pos), 1) as pct_anxiety_screen_pos,
         round(100.0 * avg(ptsd5_pos), 1) as pct_trauma_screen_pos, round(100.0 * avg(auditc_pos), 1) as pct_alcohol_above_low_risk,
         round(100.0 * avg(fm_informal), 1) as pct_informal_loan, round(100.0 * avg(fm_security_any), 1) as pct_security_held,
         round(100.0 * avg(fm_strain), 1) as pct_money_strain,
         round(100.0 * avg((lp3 = 2)::int), 1) as pct_home_conflict_big_problem
  from public.v_checkin group by 1, 2
  having count(distinct anon_code) >= 10;

-- Before and after: baseline and end-of-pilot answers for the same private code, side by side (one row per person who did both).
drop view if exists public.v_prepost;
create view public.v_prepost with (security_invoker = true) as
  select b.anon_code, b.unit_code,
         b.st1 as st1_pre, e.st1 as st1_post, b.st2 as st2_pre, e.st2 as st2_post, b.st3 as st3_pre, e.st3 as st3_post,
         b.co1 as co1_pre, e.co1 as co1_post, b.co5 as co5_pre, e.co5 as co5_post,
         b.hsi_nurse as hsi_nurse_pre, e.hsi_nurse as hsi_nurse_post, b.hsi_chaplain as hsi_chaplain_pre, e.hsi_chaplain as hsi_chaplain_post,
         b.hsi_welfare as hsi_welfare_pre, e.hsi_welfare as hsi_welfare_post, b.hsi_buddy as hsi_buddy_pre, e.hsi_buddy as hsi_buddy_post,
         b.hsi_cmdr as hsi_cmdr_pre, e.hsi_cmdr as hsi_cmdr_post, b.hsi_app as hsi_app_pre, e.hsi_app as hsi_app_post,
         b.hsi_none as hsi_none_pre, e.hsi_none as hsi_none_post
  from (select distinct on (anon_code) * from public.v_baseline_personnel where anon_code is not null order by anon_code, submitted_at) b
  join (select distinct on (anon_code) * from public.v_usability_end where anon_code is not null order by anon_code, submitted_at desc) e using (anon_code);

-- What people DO: one row per private code from check-ins, pulses, usage events and the nurse queue.
create view public.v_participant_summary as
  with ci as (select anon_code, min(submitted_at) as first_checkin_at, count(*) as n_checkins, max(risk_level) as max_risk_level,
                     (array_agg(zone order by submitted_at desc))[1] as last_zone, (array_agg(zone order by submitted_at))[1] as first_zone
              from public.v_checkin where anon_code is not null group by 1),
       pu as (select anon_code, count(*) as n_pulses from public.v_pulse where anon_code is not null group by 1),
       ev as (select anon_code, count(distinct date_trunc('week', created_at)) as active_weeks, count(*) as n_events,
                     count(*) filter (where event_type = 'lesson_opened') as lessons_opened,
                     (count(*) filter (where event_type = 'ask_nurse') > 0)::int as used_ask_nurse,
                     (count(*) filter (where event_type = 'navigator_opened') > 0)::int as used_navigator,
                     (count(*) filter (where event_type = 'buddy_opened') > 0)::int as used_buddy
              from public.events where anon_code is not null group by 1),
       sr as (select anon_code, count(*) filter (where kind = 'callback') as callbacks_requested,
                     min(hours_to_first_contact) filter (where kind = 'callback') as hours_to_first_contact,
                     max(visit_completed) filter (where kind = 'callback') as visit_completed
              from public.v_service_requests where anon_code is not null group by 1)
  select ci.anon_code, (select max(unit_code) from public.responses r where r.anon_code = ci.anon_code) as unit_code,
         ci.first_checkin_at, ci.n_checkins, coalesce(pu.n_pulses, 0) as n_pulses, ci.first_zone, ci.last_zone, ci.max_risk_level,
         coalesce(ev.active_weeks, 0) as active_weeks, coalesce(ev.n_events, 0) as n_events, coalesce(ev.lessons_opened, 0) as lessons_opened,
         coalesce(ev.used_ask_nurse, 0) as used_ask_nurse, coalesce(ev.used_navigator, 0) as used_navigator, coalesce(ev.used_buddy, 0) as used_buddy,
         coalesce(sr.callbacks_requested, 0) as callbacks_requested, sr.hours_to_first_contact, coalesce(sr.visit_completed, 0) as visit_completed
  from ci left join pu using (anon_code) left join ev using (anon_code) left join sr using (anon_code)
  where public.has_role(array['researcher','admin']);

-- What people ask the nurse about, by month (topic is the first words of the message). Months with fewer than 10 questions are hidden.
drop view if exists public.v_ask_topics_monthly;
create view public.v_ask_topics_monthly as
  select date_trunc('month', created_at)::date as month, split_part(message, ':', 1) as topic, count(*) as questions
  from public.service_requests where kind = 'ask_nurse' and public.has_role(array['researcher','admin'])
  group by 1, 2 having count(*) >= 10;

-- Why people ask for a call-back (mental health, money, both), by month. Months with fewer than 10 requests are hidden.
drop view if exists public.v_callback_reasons_monthly;
create view public.v_callback_reasons_monthly as
  select date_trunc('month', created_at)::date as month, coalesce(reason,'unspecified') as reason, count(*) as requests
  from public.service_requests where kind = 'callback' and public.has_role(array['researcher','admin'])
  group by 1, 2 having count(*) >= 10;

revoke all on public.v_events, public.v_service_requests, public.v_service_summary, public.v_engagement_weekly, public.v_early_warning,
  public.v_signals_fortnightly, public.v_unit_report, public.v_prepost, public.v_participant_summary, public.v_ask_topics_monthly,
  public.v_callback_reasons_monthly from anon, authenticated, public;
grant select on public.v_events, public.v_service_requests, public.v_service_summary, public.v_engagement_weekly, public.v_early_warning,
  public.v_signals_fortnightly, public.v_unit_report, public.v_prepost, public.v_participant_summary, public.v_ask_topics_monthly,
  public.v_callback_reasons_monthly to authenticated;

-- =====================================================================
-- DCHS student pathway (research views, researchers and admins only)
-- =====================================================================
-- First screen done (baseline for enrolled students, or selection for applicants), one row per private code, joined to the later outcome. Ready for jamovi:
-- attrition = 1 deferred, withdrew or discontinued; 0 enrolled or completed; blank = not admitted or outcome not yet known.
drop view if exists public.v_student_outcomes cascade;
create view public.v_student_outcomes with (security_invoker = true) as
with sel as (
  select distinct on (anon_code) * from public.v_student_screen
  where context in ('baseline','selection') and anon_code is not null order by anon_code, submitted_at
)
select s.*, o.intake, o.status as outcome_status, o.exit_month, o.reason as exit_reason,
       case when o.status in (3,4,5) then 1 when o.status in (1,2) then 0 end as attrition
from sel s left join public.cohort_outcomes o on o.anon_code = s.anon_code;
revoke all on public.v_student_outcomes from anon, authenticated, public;
grant select on public.v_student_outcomes to authenticated;

-- Same person at the first check (baseline or selection) and at the latest later check (follow-up or orientation). t1 = first, t2 = later.
-- For enrolled students the change shows how wellbeing moves over the term; stakes_t1 and honest_t1 show how much fear of consequences or looking well may colour answers.
drop view if exists public.v_student_paired cascade;
create view public.v_student_paired with (security_invoker = true) as
with sel as (select distinct on (anon_code) * from public.v_student_screen where context in ('baseline','selection') and anon_code is not null order by anon_code, submitted_at),
     ori as (select distinct on (anon_code) * from public.v_student_screen where context in ('followup','orientation') and anon_code is not null order by anon_code, submitted_at desc)
select s.anon_code, s.unit_code,
       s.phq9 as phq9_t1, o.phq9 as phq9_t2, o.phq9 - s.phq9 as phq9_change,
       s.gad7 as gad7_t1, o.gad7 as gad7_t2, o.gad7 - s.gad7 as gad7_change,
       s.auditc as auditc_t1, o.auditc as auditc_t2, o.auditc - s.auditc as auditc_change,
       s.brs as brs_t1, o.brs as brs_t2, o.brs - s.brs as brs_change,
       s.fm_informal as borrow_t1, o.fm_informal as borrow_t2,
       s.fm_strain as strain_t1, o.fm_strain as strain_t2,
       s.stakes as stakes_t1, o.stakes as stakes_t2,
       s.av3 as honest_t1, o.av3 as honest_t2,
       s.zone as zone_t1, o.zone as zone_t2
from sel s join ori o on o.anon_code = s.anon_code;
revoke all on public.v_student_paired from anon, authenticated, public;
grant select on public.v_student_paired to authenticated;

-- Group-level report for college support planning. It never shows fewer than 10 people and carries no individual information.
-- It is for planning counselling and welfare capacity, never for choosing between applicants.
drop view if exists public.v_student_cohort cascade;
create view public.v_student_cohort with (security_invoker = true) as
select coalesce(unit_code,'none') as unit_code, context, date_trunc('month', submitted_at)::date as month,
       count(distinct anon_code) as people,
       round(100.0 * avg(case when zone >= 3 then 1 else 0 end), 1) as pct_struggling_or_worse,
       round(100.0 * avg(phq9_pos), 1) as pct_phq9_10plus, round(100.0 * avg(gad7_pos), 1) as pct_gad7_10plus,
       round(100.0 * avg(fm_strain), 1) as pct_money_strain, round(100.0 * avg(fm_informal), 1) as pct_informal_borrowing,
       round(avg(stakes), 2) as mean_perceived_stakes, round(avg(brs) / 6.0, 2) as mean_resilience_1to5
from public.v_student_screen
where anon_code is not null
group by 1, 2, 3
having count(distinct anon_code) >= 10;
revoke all on public.v_student_cohort from anon, authenticated, public;
grant select on public.v_student_cohort to authenticated;


-- ---------------------------------------------------------------------
-- Portal views: the dashboard and the monthly report read these. Groups of fewer than 10 people are never shown.
-- They combine the student wellbeing check and the repeat check-in, so a month's figures count every check done.
-- ---------------------------------------------------------------------
drop view if exists public.v_portal_monthly cascade;
create view public.v_portal_monthly with (security_invoker = true) as
with a as (
  select unit_code, submitted_at, anon_code, zone, phq9_pos, gad7_pos, ptsd5_pos, auditc_pos, fm_strain, fm_informal, cl1 from public.v_student_screen
  union all
  select unit_code, submitted_at, anon_code, zone, phq9_pos, gad7_pos, ptsd5_pos, auditc_pos, fm_strain, fm_informal, null::int as cl1 from public.v_checkin
)
select coalesce(unit_code,'none') as unit_code, date_trunc('month', submitted_at)::date as month,
       count(distinct anon_code) as people, count(*) as checkins,
       round(100.0 * avg((zone = 1)::int), 1) as pct_coping_well, round(100.0 * avg((zone = 2)::int), 1) as pct_strain,
       round(100.0 * avg((zone = 3)::int), 1) as pct_struggling, round(100.0 * avg((zone = 4)::int), 1) as pct_needs_care,
       round(100.0 * avg(phq9_pos), 1) as pct_low_mood_screen_pos, round(100.0 * avg(gad7_pos), 1) as pct_anxiety_screen_pos,
       round(100.0 * avg(ptsd5_pos), 1) as pct_trauma_screen_pos, round(100.0 * avg(auditc_pos), 1) as pct_alcohol_above_low_risk,
       round(100.0 * avg(fm_strain), 1) as pct_money_strain, round(100.0 * avg(fm_informal), 1) as pct_informal_loan,
       round(100.0 * avg((cl1 >= 1)::int) filter (where cl1 is not null), 1) as pct_thought_leaving
from a where anon_code is not null group by 1, 2
having count(distinct anon_code) >= 10;
revoke all on public.v_portal_monthly from anon, authenticated, public;
grant select on public.v_portal_monthly to authenticated;

drop view if exists public.v_portal_pressures cascade;
create view public.v_portal_pressures with (security_invoker = true) as
select coalesce(s.unit_code,'none') as unit_code, date_trunc('month', s.submitted_at)::date as month, p.pressure,
       count(distinct s.anon_code) as people, round(100.0 * avg((p.v = 2)::int) filter (where p.v is not null), 1) as pct_big_problem
from public.v_student_screen s
cross join lateral (values ('Money: fees, upkeep or debt', s.la1), ('Being far from family or home', s.la2), ('Conflict or problems at home', s.la3),
  ('Accommodation or housing', s.la4), ('Pressure to succeed or fear of failing', s.la5), ('Your health', s.la6),
  ('Loneliness or fitting in', s.la7), ('Bereavement or loss', s.la8)) as p(pressure, v)
where s.anon_code is not null
group by 1, 2, 3
having count(distinct s.anon_code) >= 10;
revoke all on public.v_portal_pressures from anon, authenticated, public;
grant select on public.v_portal_pressures to authenticated;
