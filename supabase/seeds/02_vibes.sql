insert into public.vibes (category_id, title, icon_emoji) values

  -----------------------------------------------------------------------
  -- CITY & CULTURE
  -----------------------------------------------------------------------
  (
    (select id from public.vibe_categories where title = 'City & culture'),
    'Old town walks', '🏘️'
  ),
  (
    (select id from public.vibe_categories where title = 'City & culture'),
    'Museum afternoons', '🖼️'
  ),
  (
    (select id from public.vibe_categories where title = 'City & culture'),
    'Local concerts', '🎵'
  ),
  (
    (select id from public.vibe_categories where title = 'City & culture'),
    'Street art hunts', '🎨'
  ),
  (
    (select id from public.vibe_categories where title = 'City & culture'),
    'Historic landmarks', '🏛️'
  ),
  (
    (select id from public.vibe_categories where title = 'City & culture'),
    'Architecture walks', '🏗️'
  ),
  (
    (select id from public.vibe_categories where title = 'City & culture'),
    'Traditional festivals', '🎭'
  ),
  (
    (select id from public.vibe_categories where title = 'City & culture'),
    'Underground culture', '🕳️'
  ),
  (
    (select id from public.vibe_categories where title = 'City & culture'),
    'Artisan workshops', '🧵'
  ),
  (
    (select id from public.vibe_categories where title = 'City & culture'),
    'Indie cinemas', '🎬'
  ),
  (
    (select id from public.vibe_categories where title = 'City & culture'),
    'Opera & classical music', '🎼'
  ),
  (
    (select id from public.vibe_categories where title = 'City & culture'),
    'Local neighborhood exploring', '🚲'
  ),
  (
    (select id from public.vibe_categories where title = 'City & culture'),
    'Cultural food tours', '🍲'
  ),
  (
    (select id from public.vibe_categories where title = 'City & culture'),
    'Bookstore crawling', '📚'
  ),
  (
    (select id from public.vibe_categories where title = 'City & culture'),
    'Photography walks', '📸'
  ),


  -----------------------------------------------------------------------
  -- NATURE & OUTDOORS
  -----------------------------------------------------------------------
  (
    (select id from public.vibe_categories where title = 'Nature & outdoors'),
    'Mountain hikes', '🏔️'
  ),
  (
    (select id from public.vibe_categories where title = 'Nature & outdoors'),
    'Lake days', '🏞️'
  ),
  (
    (select id from public.vibe_categories where title = 'Nature & outdoors'),
    'Scenic road trips', '🛣️'
  ),
  (
    (select id from public.vibe_categories where title = 'Nature & outdoors'),
    'National parks', '🌲'
  ),
  (
    (select id from public.vibe_categories where title = 'Nature & outdoors'),
    'Beaches & swims', '🏖️'
  ),
  (
    (select id from public.vibe_categories where title = 'Nature & outdoors'),
    'Sunrise viewpoints', '🌅'
  ),
  (
    (select id from public.vibe_categories where title = 'Nature & outdoors'),
    'Wildlife spotting', '🦌'
  ),
  (
    (select id from public.vibe_categories where title = 'Nature & outdoors'),
    'Waterfall chasing', '💧'
  ),
  (
    (select id from public.vibe_categories where title = 'Nature & outdoors'),
    'Forest bathing', '🌳'
  ),
  (
    (select id from public.vibe_categories where title = 'Nature & outdoors'),
    'Cliffside viewpoints', '🪨'
  ),
  (
    (select id from public.vibe_categories where title = 'Nature & outdoors'),
    'Stargazing', '🌌'
  ),
  (
    (select id from public.vibe_categories where title = 'Nature & outdoors'),
    'Kayaking & paddling', '🛶'
  ),
  (
    (select id from public.vibe_categories where title = 'Nature & outdoors'),
    'Cave exploring', '🕳️'
  ),
  (
    (select id from public.vibe_categories where title = 'Nature & outdoors'),
    'Countryside villages', '🏡'
  ),
  (
    (select id from public.vibe_categories where title = 'Nature & outdoors'),
    'Hot springs', '♨️'
  ),


  -----------------------------------------------------------------------
  -- FOOD & GOING OUT
  -----------------------------------------------------------------------
  (
    (select id from public.vibe_categories where title = 'Food & going out'),
    'Street food runs', '🌮'
  ),
  (
    (select id from public.vibe_categories where title = 'Food & going out'),
    'Coffee house hopping', '☕'
  ),
  (
    (select id from public.vibe_categories where title = 'Food & going out'),
    'Wine & craft beer', '🍷'
  ),
  (
    (select id from public.vibe_categories where title = 'Food & going out'),
    'Late-night bars', '🍸'
  ),
  (
    (select id from public.vibe_categories where title = 'Food & going out'),
    'Food markets', '🧺'
  ),
  (
    (select id from public.vibe_categories where title = 'Food & going out'),
    'Fine dining nights', '🍽️'
  ),
  (
    (select id from public.vibe_categories where title = 'Food & going out'),
    'Dessert hunting', '🧁'
  ),
  (
    (select id from public.vibe_categories where title = 'Food & going out'),
    'Local bakeries', '🥐'
  ),
  (
    (select id from public.vibe_categories where title = 'Food & going out'),
    'Craft cocktails', '🍹'
  ),
  (
    (select id from public.vibe_categories where title = 'Food & going out'),
    'Rooftop views', '🌇'
  ),
  (
    (select id from public.vibe_categories where title = 'Food & going out'),
    'Pub nights', '🍺'
  ),
  (
    (select id from public.vibe_categories where title = 'Food & going out'),
    'Food truck parks', '🚚'
  ),
  (
    (select id from public.vibe_categories where title = 'Food & going out'),
    'Sake & wine tastings', '🍶'
  ),
  (
    (select id from public.vibe_categories where title = 'Food & going out'),
    'Live music bars', '🎶'
  ),
  (
    (select id from public.vibe_categories where title = 'Food & going out'),
    'Brunch places', '🍳'
  ),


  -----------------------------------------------------------------------
  -- SLOW & COZY TRAVEL
  -----------------------------------------------------------------------
  (
    (select id from public.vibe_categories where title = 'Slow & cozy travel'),
    'Reading in cafes', '📚'
  ),
  (
    (select id from public.vibe_categories where title = 'Slow & cozy travel'),
    'Slow morning strolls', '🚶‍♂️'
  ),
  (
    (select id from public.vibe_categories where title = 'Slow & cozy travel'),
    'Scenic train rides', '🚆'
  ),
  (
    (select id from public.vibe_categories where title = 'Slow & cozy travel'),
    'Local neighborhoods', '🏡'
  ),
  (
    (select id from public.vibe_categories where title = 'Slow & cozy travel'),
    'Cozy stays', '🛏️'
  ),
  (
    (select id from public.vibe_categories where title = 'Slow & cozy travel'),
    'Spa & thermal baths', '♨️'
  ),
  (
    (select id from public.vibe_categories where title = 'Slow & cozy travel'),
    'Gallery mornings', '🖼️'
  ),
  (
    (select id from public.vibe_categories where title = 'Slow & cozy travel'),
    'Tea rituals', '🍵'
  ),
  (
    (select id from public.vibe_categories where title = 'Slow & cozy travel'),
    'Hidden streets exploring', '🛤️'
  ),
  (
    (select id from public.vibe_categories where title = 'Slow & cozy travel'),
    'Village escapes', '🌾'
  ),
  (
    (select id from public.vibe_categories where title = 'Slow & cozy travel'),
    'Rainy-day museums', '☔'
  ),
  (
    (select id from public.vibe_categories where title = 'Slow & cozy travel'),
    'Countryside retreats', '🌻'
  ),
  (
    (select id from public.vibe_categories where title = 'Slow & cozy travel'),
    'Local libraries', '📖'
  ),
  (
    (select id from public.vibe_categories where title = 'Slow & cozy travel'),
    'Cozy fireplace evenings', '🔥'
  ),
  (
    (select id from public.vibe_categories where title = 'Slow & cozy travel'),
    'Picnic fields', '🧺'
  )

on conflict (category_id, title) do nothing;