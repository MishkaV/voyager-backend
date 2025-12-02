
  create table "public"."countries_visited" (
    "user_id" uuid not null,
    "country_id" uuid not null
      );


alter table "public"."countries_visited" enable row level security;

CREATE UNIQUE INDEX visited_countries_pkey ON public.countries_visited USING btree (user_id, country_id);

alter table "public"."countries_visited" add constraint "visited_countries_pkey" PRIMARY KEY using index "visited_countries_pkey";

alter table "public"."countries_visited" add constraint "visited_countries_country_id_fkey" FOREIGN KEY (country_id) REFERENCES public.countries(id) ON DELETE RESTRICT not valid;

alter table "public"."countries_visited" validate constraint "visited_countries_country_id_fkey";

alter table "public"."countries_visited" add constraint "visited_countries_user_id_fkey" FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE not valid;

alter table "public"."countries_visited" validate constraint "visited_countries_user_id_fkey";

create or replace view "public"."user_travel_stats" as  SELECT cv.user_id,
    count(DISTINCT cv.country_id) AS countries_visited,
    count(DISTINCT c.continent) AS continents_visited,
    round(((100.0 * (count(DISTINCT cv.country_id))::numeric) / (NULLIF(( SELECT count(*) AS count
           FROM public.countries), 0))::numeric), 1) AS world_explored_percent
   FROM (public.countries_visited cv
     JOIN public.countries c ON ((c.id = cv.country_id)))
  GROUP BY cv.user_id;


grant delete on table "public"."countries_visited" to "anon";

grant insert on table "public"."countries_visited" to "anon";

grant references on table "public"."countries_visited" to "anon";

grant select on table "public"."countries_visited" to "anon";

grant trigger on table "public"."countries_visited" to "anon";

grant truncate on table "public"."countries_visited" to "anon";

grant update on table "public"."countries_visited" to "anon";

grant delete on table "public"."countries_visited" to "authenticated";

grant insert on table "public"."countries_visited" to "authenticated";

grant references on table "public"."countries_visited" to "authenticated";

grant select on table "public"."countries_visited" to "authenticated";

grant trigger on table "public"."countries_visited" to "authenticated";

grant truncate on table "public"."countries_visited" to "authenticated";

grant update on table "public"."countries_visited" to "authenticated";

grant delete on table "public"."countries_visited" to "service_role";

grant insert on table "public"."countries_visited" to "service_role";

grant references on table "public"."countries_visited" to "service_role";

grant select on table "public"."countries_visited" to "service_role";

grant trigger on table "public"."countries_visited" to "service_role";

grant truncate on table "public"."countries_visited" to "service_role";

grant update on table "public"."countries_visited" to "service_role";


  create policy "Users can insert own visited_countries"
  on "public"."countries_visited"
  as permissive
  for insert
  to authenticated
with check ((( SELECT auth.uid() AS uid) = user_id));



  create policy "Users can read own visited_countries"
  on "public"."countries_visited"
  as permissive
  for select
  to authenticated
using ((( SELECT auth.uid() AS uid) = user_id));



  create policy "Users can update own visited_countries"
  on "public"."countries_visited"
  as permissive
  for update
  to authenticated
using ((( SELECT auth.uid() AS uid) = user_id))
with check ((( SELECT auth.uid() AS uid) = user_id));



