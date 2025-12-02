insert into public.vibe_categories (title) values
  ('City & culture'),
  ('Nature & outdoors'),
  ('Food & going out'),
  ('Slow & cozy travel')
on conflict (title) do nothing;