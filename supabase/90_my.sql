-- 이 선생님 서버에만 더하는 것. 원래 포털의 01~04는 고치지 않고, 새로 만드는 표·함수·트리거는 이름을 my_로 시작해 여기에 모은다.
-- 다시 실행해도 안전하게 쓴다(create or replace, if not exists). Supabase → SQL Editor에 통째로 붙여 넣고 Run.

-- 학습지에서 이 사이트에 없는 시뮬레이션 칸 지우기
-- 원래 서버에서 받아 오는 학습지(매일)에 이 사이트 sims/에 없는 시뮬레이션 칸이 들어 있을 수 있다.
-- 학습지를 넣거나 고칠 때마다 그 칸(<div ... data-sim="sims/…rpg….html" class="w-sim"></div>)을 지운다. 칸 번호·답은 그대로.
create or replace function public.my_strip_missing_sims() returns trigger
language plpgsql set search_path = public as $$
begin
  if new.pages is not null and jsonb_typeof(new.pages) = 'array' then
    new.pages := (
      select coalesce(jsonb_agg(
        case when p ? 'html' then
          jsonb_set(p, '{html}', to_jsonb(regexp_replace(p ->> 'html',
            '<div[^>]*data-sim="sims/[^"]*(rpg|game)[^"]*"[^>]*>\s*</div>\s*', '', 'gi')))
        else p end
        order by i), '[]'::jsonb)
      from jsonb_array_elements(new.pages) with ordinality as t(p, i));
  end if;
  return new;
end $$;

revoke all on function public.my_strip_missing_sims() from public, anon, authenticated;

drop trigger if exists my_strip_missing_sims on public.worksheets;
create trigger my_strip_missing_sims before insert or update of pages on public.worksheets
  for each row execute function public.my_strip_missing_sims();

-- 이미 들어 있는 학습지도 한 번 정리(트리거가 지움)
update public.worksheets set pages = pages where pages::text ~* 'sims/[^"]*(rpg|game)';
