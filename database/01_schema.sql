-- =====================================================================
-- Salama Check-In: database schema for Supabase (PostgreSQL)
-- Run this file ONCE in the Supabase SQL editor, then 02, 03 (04 after you create staff logins).
--
-- Design rules
--   * Respondents (the app, using the public "anon" key) can only INSERT.
--     They can never read, change or delete anything.
--   * Staff sign in with an email account and a role in the "staff" table:
--     nurse | researcher | admin | welfare (college student-support officer) | interviewer (colour lookup only, off unless granted).
--   * Nurses see only the service queue. Only researchers and admins see answers.
--   * The questionnaires hold no names or service numbers. Free text exists only in optional
--     "own words" boxes and in the key informant form. The only way to reach a person is the
--     optional contact hint in a call-back request, readable by nurses only.
-- =====================================================================

create extension if not exists pgcrypto;

-- ---------------------------------------------------------------- staff
create table if not exists public.staff (
  user_id uuid primary key references auth.users(id) on delete cascade,
  role    text not null check (role in ('nurse','researcher','admin','welfare','interviewer')),
  created_at timestamptz not null default now()
);
alter table public.staff enable row level security;

create or replace function public.has_role(roles text[]) returns boolean
language sql security definer stable set search_path = public as $$
  select exists (select 1 from public.staff where user_id = auth.uid() and role = any(roles))
$$;
revoke all on function public.has_role(text[]) from public;
grant execute on function public.has_role(text[]) to authenticated;

drop policy if exists staff_self on public.staff;
create policy staff_self on public.staff for select to authenticated using (user_id = auth.uid());

-- ----------------------------------------------------------- responses
-- One row per submitted questionnaire. Answers are JSON keyed by item id; the views in 02_views.sql
-- turn them into flat numeric columns for jamovi. protocol_version records which version of the
-- questions and rules was live, so changes made during the pilot can be analysed.
create table if not exists public.responses (
  id               uuid primary key default gen_random_uuid(),
  created_at       timestamptz not null default now(),
  client_uuid      uuid not null unique,
  client_time      timestamptz,
  form             text not null check (form in ('baseline_personnel','baseline_family','checkin','pulse','informant','usability_end','student_screen','delphi')),
  grp              text not null check (grp in ('personnel','family','informant','staff','student')),
  wave             text check (wave in ('baseline','first','repeat','weekly','endline','single')),
  context          text check (context in ('routine','pre_deploy','post_deploy','after_leave','other','selection','orientation','baseline','followup')),
  unit_code        text check (unit_code ~ '^[A-Za-z0-9_-]{1,20}$'),
  anon_code        text check (anon_code ~ '^[A-Z0-9]{4}-[A-Z0-9]{4}$'),
  app_version      text check (length(app_version) <= 20),
  protocol_version text check (length(protocol_version) <= 12),
  risk_level       smallint check (risk_level between 0 and 2),
  zone             smallint check (zone between 1 and 4),
  answers          jsonb not null check (jsonb_typeof(answers) = 'object' and pg_column_size(answers) < 30000)
);
create index if not exists responses_form_idx on public.responses (form, created_at);
create index if not exists responses_anon_idx on public.responses (anon_code);
alter table public.responses enable row level security;

-- -------------------------------------------------------------- events
-- Anonymous usage counts (screen opened, lesson read). Never what was typed.
create table if not exists public.events (
  id          uuid primary key default gen_random_uuid(),
  created_at  timestamptz not null default now(),
  client_uuid uuid not null unique,
  anon_code   text check (anon_code ~ '^[A-Z0-9]{4}-[A-Z0-9]{4}$'),
  unit_code   text check (unit_code ~ '^[A-Za-z0-9_-]{1,20}$'),
  event_type  text not null check (event_type in ('app_open','checkin_started','checkin_completed','pulse_started','pulse_completed',
                                                   'callback_requested','ask_nurse','navigator_opened','navigator_topic','lesson_opened',
                                                   'buddy_opened','buddy_reminder_set','help_opened','referral_tapped','guide_opened','guide_message','situation_changed','role_changed','sms_fallback_opened')),
  detail      text check (length(detail) <= 40)
);
create index if not exists events_time_idx on public.events (created_at);
alter table public.events enable row level security;

-- ---------------------------------------------------- service_requests
-- The nurse queue: call-back requests and anonymous questions.
create table if not exists public.service_requests (
  id                 uuid primary key default gen_random_uuid(),
  created_at         timestamptz not null default now(),
  client_uuid        uuid not null unique,
  ticket_code        text not null unique check (ticket_code ~ '^T-[A-Z0-9]{8}$'),
  anon_code          text check (anon_code ~ '^[A-Z0-9]{4}-[A-Z0-9]{4}$'),
  unit_code          text check (unit_code ~ '^[A-Za-z0-9_-]{1,20}$'),
  kind               text not null check (kind in ('callback','ask_nurse','welfare_help')),
  reason             text check (reason in ('mental_health','money','both','other')),
  urgency            text not null default 'routine' check (urgency in ('routine','same_day')),
  risk_level         smallint check (risk_level between 0 and 2),
  shared_scores      jsonb check (shared_scores is null or pg_column_size(shared_scores) < 2000),
  contact_hint       text check (length(contact_hint) <= 120),
  message            text check (length(message) <= 600),
  status             text not null default 'new' check (status in ('new','contacted','visit_booked','visit_completed','closed','unreachable')),
  first_contact_at   timestamptz,
  visit_completed_at timestamptz,
  nurse_reply        text check (length(nurse_reply) <= 2000),
  replied_at         timestamptz,
  handled_by         uuid,
  updated_at         timestamptz
);
create index if not exists sr_status_idx on public.service_requests (status, created_at);
alter table public.service_requests enable row level security;

-- Clock timestamps are set by the database, so time-to-contact cannot be edited by hand.
create or replace function public.sr_touch() returns trigger language plpgsql as $$
begin
  new.updated_at := now();
  new.handled_by := auth.uid();
  if new.status <> 'new' and old.first_contact_at is null then new.first_contact_at := now(); end if;
  if new.status = 'visit_completed' and old.visit_completed_at is null then new.visit_completed_at := now(); end if;
  if new.nurse_reply is not null and new.nurse_reply is distinct from old.nurse_reply then
    new.replied_at := now();
    if new.first_contact_at is null then new.first_contact_at := now(); end if;
    if new.status = 'new' then new.status := 'contacted'; end if;
  end if;
  return new;
end $$;
drop trigger if exists sr_touch_trg on public.service_requests;
create trigger sr_touch_trg before update on public.service_requests for each row execute function public.sr_touch();

-- ------------------------------------------------------------ change_log
-- Every change made to the service during the pilot, with the trigger and who approved it.
create table if not exists public.change_log (
  id               uuid primary key default gen_random_uuid(),
  created_at       timestamptz not null default now(),
  protocol_version text not null check (length(protocol_version) <= 12),
  trigger_text     text not null check (length(trigger_text) between 3 and 500),
  change_text      text not null check (length(change_text) between 3 and 500),
  approved_by      text not null check (length(approved_by) between 2 and 120),
  logged_by        uuid
);
alter table public.change_log enable row level security;
create or replace function public.cl_touch() returns trigger language plpgsql as $$
begin new.logged_by := auth.uid(); return new; end $$;
drop trigger if exists cl_touch_trg on public.change_log;
create trigger cl_touch_trg before insert on public.change_log for each row execute function public.cl_touch();

-- --------------------------------------------------------- cohort_outcomes
-- DCHS applicant pathway. After admission, an honest broker at the college (the Registrar's designated officer, NOT a member of the
-- selection panel) sends the research team only: private code, intake, outcome status, exit month and a broad reason category.
-- No name or admission number is ever stored here. Only researchers and admins can read or write it.
-- status: 1 enrolled and continuing | 2 completed the period | 3 deferred | 4 withdrew | 5 discontinued (academic or discipline) | 6 not admitted
-- reason: 1 mental health | 2 other health | 3 money or fees | 4 family | 5 academic | 6 discipline | 7 changed plans | 9 unknown or not stated
create table if not exists public.cohort_outcomes (
  anon_code   text primary key check (anon_code ~ '^[A-Z0-9]{4}-[A-Z0-9]{4}$'),
  intake      text not null check (intake ~ '^[0-9]{4}-[0-9]{2}$'),
  status      smallint not null check (status between 1 and 6),
  exit_month  smallint check (exit_month between 0 and 72),
  reason      smallint check (reason between 1 and 9),
  recorded_at timestamptz not null default now(),
  recorded_by uuid
);
alter table public.cohort_outcomes enable row level security;
create or replace function public.co_touch() returns trigger language plpgsql as $$
begin new.recorded_by := auth.uid(); new.recorded_at := now(); return new; end $$;
drop trigger if exists co_touch_trg on public.cohort_outcomes;
create trigger co_touch_trg before insert or update on public.cohort_outcomes for each row execute function public.co_touch();

-- ------------------------------------------------------- college_sharing
-- DCHS applicants and students who CHOOSE (separate, withdrawable opt-in; never a condition of applying) to tell the college's
-- student-support office how they are doing. Only a colour band is shared: 1 green, 2 amber, 3 red. No scores, no answers.
-- ref_text is what the person typed to identify themselves to the college (interview number or name); it is not in any research table.
create table if not exists public.college_sharing (
  id          uuid primary key default gen_random_uuid(),
  created_at  timestamptz not null default now(),
  client_uuid uuid not null unique,
  anon_code   text check (anon_code ~ '^[A-Z0-9]{4}-[A-Z0-9]{4}$'),
  ref_text    text not null check (length(ref_text) between 2 and 60),
  band        smallint not null check (band between 1 and 3),
  context     text check (context in ('selection','orientation','baseline','followup','routine')),
  consent_version text check (length(consent_version) <= 12),
  status      text not null default 'new' check (status in ('new','support_offered','accepted','declined','closed')),
  updated_at  timestamptz,
  handled_by  uuid
);
alter table public.college_sharing enable row level security;
create or replace function public.cs_touch() returns trigger language plpgsql as $$
begin new.updated_at := now(); new.handled_by := auth.uid(); return new; end $$;
drop trigger if exists cs_touch_trg on public.college_sharing;
create trigger cs_touch_trg before update on public.college_sharing for each row execute function public.cs_touch();

-- Every look-up of a person's colour by an interviewer is recorded.
create table if not exists public.access_log (
  id uuid primary key default gen_random_uuid(), at timestamptz not null default now(), user_id uuid, action text not null, ref_text text
);
alter table public.access_log enable row level security;

-- A person can withdraw their own share using the secret reference the app kept (client_uuid). Nobody else knows it.
create or replace function public.withdraw_share(p_client_uuid uuid) returns boolean
language plpgsql security definer set search_path = public as $$
declare n int; begin delete from public.college_sharing where client_uuid = p_client_uuid; get diagnostics n = row_count; return n > 0; end $$;
revoke all on function public.withdraw_share(uuid) from public; grant execute on function public.withdraw_share(uuid) to anon, authenticated;

-- Interviewer look-up: exact reference only, returns the colour band and nothing else, and writes an audit row. No listing is possible.
create or replace function public.college_colour(p_ref text) returns table (band smallint, band_label text)
language plpgsql security definer set search_path = public as $$
begin
  if not public.has_role(array['interviewer','welfare','admin']) then raise exception 'not allowed'; end if;
  insert into public.access_log(user_id, action, ref_text) values (auth.uid(), 'colour_lookup', left(p_ref, 60));
  return query select c.band, case c.band when 1 then 'Green' when 2 then 'Amber' else 'Red' end
               from public.college_sharing c where lower(c.ref_text) = lower(trim(p_ref)) order by c.created_at desc limit 1;
end $$;
revoke all on function public.college_colour(text) from public; grant execute on function public.college_colour(text) to authenticated;

-- ------------------------------------------------------------ privileges
-- Start from nothing, then grant only what is needed.
revoke all on public.staff, public.responses, public.events, public.service_requests, public.change_log, public.cohort_outcomes, public.college_sharing, public.access_log from anon, authenticated, public;

grant insert (client_uuid, client_time, form, grp, wave, context, unit_code, anon_code, app_version, protocol_version, risk_level, zone, answers)
  on public.responses to anon;
grant insert (client_uuid, anon_code, unit_code, event_type, detail) on public.events to anon;
grant insert (client_uuid, anon_code, ref_text, band, context, consent_version) on public.college_sharing to anon;
grant insert (client_uuid, ticket_code, anon_code, unit_code, kind, reason, urgency, risk_level, shared_scores, contact_hint, message)
  on public.service_requests to anon;

grant select on public.staff to authenticated;
grant select on public.college_sharing, public.access_log to authenticated;
grant update (status) on public.college_sharing to authenticated;
grant select on public.responses, public.events, public.service_requests, public.change_log, public.cohort_outcomes to authenticated;
grant insert (anon_code, intake, status, exit_month, reason) on public.cohort_outcomes to authenticated;
grant update (intake, status, exit_month, reason) on public.cohort_outcomes to authenticated;
grant update (status, nurse_reply) on public.service_requests to authenticated;
grant insert (protocol_version, trigger_text, change_text, approved_by) on public.change_log to authenticated;

-- ---------------------------------------------------------------- policies
drop policy if exists anon_insert_responses on public.responses;
create policy anon_insert_responses on public.responses for insert to anon with check (true);
drop policy if exists anon_insert_events on public.events;
create policy anon_insert_events on public.events for insert to anon with check (true);
drop policy if exists anon_insert_requests on public.service_requests;
create policy anon_insert_requests on public.service_requests for insert to anon
  with check (status = 'new' and first_contact_at is null and visit_completed_at is null and nurse_reply is null and replied_at is null);

drop policy if exists staff_read_responses on public.responses;
create policy staff_read_responses on public.responses for select to authenticated using (public.has_role(array['researcher','admin']));
drop policy if exists staff_read_events on public.events;
create policy staff_read_events on public.events for select to authenticated using (public.has_role(array['researcher','admin']));
drop policy if exists staff_read_requests on public.service_requests;
-- Only nurses and admins read the queue itself (it holds contact hints and questions). Researchers use v_service_requests, which leaves those out.
create policy staff_read_requests on public.service_requests for select to authenticated using (public.has_role(array['nurse','admin']));
drop policy if exists staff_update_requests on public.service_requests;
create policy staff_update_requests on public.service_requests for update to authenticated
  using (public.has_role(array['nurse','admin'])) with check (public.has_role(array['nurse','admin']));
drop policy if exists staff_read_changes on public.change_log;
create policy staff_read_changes on public.change_log for select to authenticated using (public.has_role(array['nurse','researcher','admin']));
drop policy if exists staff_add_changes on public.change_log;
create policy staff_add_changes on public.change_log for insert to authenticated with check (public.has_role(array['researcher','admin']));

drop policy if exists staff_read_outcomes on public.cohort_outcomes;
create policy staff_read_outcomes on public.cohort_outcomes for select to authenticated using (public.has_role(array['researcher','admin']));
drop policy if exists staff_add_outcomes on public.cohort_outcomes;
create policy staff_add_outcomes on public.cohort_outcomes for insert to authenticated with check (public.has_role(array['researcher','admin']));
drop policy if exists staff_edit_outcomes on public.cohort_outcomes;
create policy staff_edit_outcomes on public.cohort_outcomes for update to authenticated
  using (public.has_role(array['researcher','admin'])) with check (public.has_role(array['researcher','admin']));

drop policy if exists anon_insert_share on public.college_sharing;
create policy anon_insert_share on public.college_sharing for insert to anon with check (status = 'new');
drop policy if exists staff_read_share on public.college_sharing;
create policy staff_read_share on public.college_sharing for select to authenticated using (public.has_role(array['welfare','admin']));
drop policy if exists staff_update_share on public.college_sharing;
create policy staff_update_share on public.college_sharing for update to authenticated
  using (public.has_role(array['welfare','admin'])) with check (public.has_role(array['welfare','admin']));
drop policy if exists admin_read_log on public.access_log;
create policy admin_read_log on public.access_log for select to authenticated using (public.has_role(array['admin']));

-- ------------------------------------------------- reply lookup for the app
-- A person can read ONLY the status and reply for a ticket code they hold.
create or replace function public.get_ticket(p_ticket text)
returns table (status text, nurse_reply text, replied_at timestamptz)
language sql security definer stable set search_path = public as $$
  select s.status, s.nurse_reply, s.replied_at from public.service_requests s where s.ticket_code = p_ticket limit 1
$$;
revoke all on function public.get_ticket(text) from public;
grant execute on function public.get_ticket(text) to anon, authenticated;


-- ------------------------------------------------------------------
-- Anonymous participant IDs, first come first served.
-- The phone asks for an ID once, the first time the person joins. IDs look like APPL-0001, PERS-0002, FAMI-0003.
-- The number says only "this was the Nth person to join in this group". It is not linked to a name, phone or service number.
-- Nobody can read the table through the public key, and the public key can only ask for the next number.
-- ------------------------------------------------------------------
create table if not exists public.participant_seq (prefix text primary key, last_n int not null default 0);
alter table public.participant_seq enable row level security;
revoke all on public.participant_seq from anon, authenticated;

create or replace function public.issue_participant_id(p_grp text) returns text
language plpgsql security definer set search_path = public as $$
declare pf text; n int;
begin
  pf := case p_grp when 'personnel' then 'PERS' when 'family' then 'FAMI' when 'student' then 'STUD' else null end;
  if pf is null then return null; end if;
  insert into public.participant_seq(prefix, last_n) values (pf, 1)
    on conflict (prefix) do update set last_n = public.participant_seq.last_n + 1 returning last_n into n;
  if n > 9999 then return null; end if;      -- the phone then makes a random code instead
  return pf || '-' || lpad(n::text, 4, '0');
end $$;
revoke all on function public.issue_participant_id(text) from public; grant execute on function public.issue_participant_id(text) to anon, authenticated;
