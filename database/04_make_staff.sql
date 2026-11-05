-- =====================================================================
-- Give a staff account a role. Create the account first:
--   Supabase dashboard > Authentication > Users > Add user (email + password, tick "Auto confirm user").
-- Then edit the emails below and run this file.
-- Roles: nurse (queue and replies) | researcher (answers, exports, change log) | admin (all)
--        welfare (college student-support officer: sees colour band of people who chose to share)
--        interviewer (exact-reference colour look-up only). Grant ONLY with ethics committee and DCHS governance approval.
-- =====================================================================
insert into public.staff (user_id, role)
select id, 'researcher' from auth.users where email = 'researcher@example.com'
on conflict (user_id) do update set role = excluded.role;

insert into public.staff (user_id, role)
select id, 'nurse' from auth.users where email = 'nurse@example.com'
on conflict (user_id) do update set role = excluded.role;

-- Example for the college support officer:
-- insert into public.staff (user_id, role) select id, 'welfare' from auth.users where email = 'support@example.com' on conflict (user_id) do update set role = excluded.role;
