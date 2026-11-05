#!/bin/bash
# Test helper: rebuild the local Postgres test database from the SQL files.
export PGHOST=/var/tmp/pgt PGPORT=54329
if ! psql -U postgres -d postgres -qc "select 1" >/dev/null 2>&1; then
  su postgres -c "/usr/lib/postgresql/16/bin/pg_ctl -D /var/tmp/pgt/data -o '-p 54329 -k /var/tmp/pgt -c listen_addresses=' -l /var/tmp/pgt/pg.out -w start" >/dev/null 2>&1
fi
psql -U postgres -d postgres -q -c "drop database if exists salama" -c "create database salama" 2>&1 | grep -v NOTICE
psql -U postgres -d postgres -q -c "drop role if exists anon" -c "drop role if exists authenticated" 2>&1 | grep -v NOTICE
psql -U postgres -d salama -v ON_ERROR_STOP=1 -q -f /home/claude/salama/test/stub.sql 2>&1 | grep -v NOTICE
for f in 01_schema.sql 02_views.sql 03_reports.sql; do psql -U postgres -d salama -v ON_ERROR_STOP=1 -q -f /home/claude/salama/database/$f 2>&1 | grep -v NOTICE; done
psql -U postgres -d salama -q -c "insert into auth.users(id,email) values ('11111111-1111-1111-1111-111111111111','nurse@x'),('22222222-2222-2222-2222-222222222222','res@x'),('33333333-3333-3333-3333-333333333333','w@x'),('44444444-4444-4444-4444-444444444444','i@x'),('55555555-5555-5555-5555-555555555555','a@x'); insert into public.staff(user_id,role) values ('11111111-1111-1111-1111-111111111111','nurse'),('22222222-2222-2222-2222-222222222222','researcher'),('33333333-3333-3333-3333-333333333333','welfare'),('44444444-4444-4444-4444-444444444444','interviewer'),('55555555-5555-5555-5555-555555555555','admin');"
echo "db ready"
