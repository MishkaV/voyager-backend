drop view if exists "public"."user_travel_stats";

alter table "public"."countries" drop column "flag_url";

alter table "public"."countries" add column "flag_full_patch" text not null;

alter table "public"."country_podcasts" drop column "audio_url";

alter table "public"."country_podcasts" add column "audio_full_patch" text not null;

create or replace view "public"."user_travel_stats" as  SELECT cv.user_id,
    count(DISTINCT cv.country_id) AS countries_visited,
    count(DISTINCT c.continent) AS continents_visited,
    round(((100.0 * (count(DISTINCT cv.country_id))::numeric) / (NULLIF(( SELECT count(*) AS count
           FROM public.countries), 0))::numeric), 1) AS world_explored_percent
   FROM (public.countries_visited cv
     JOIN public.countries c ON ((c.id = cv.country_id)))
  GROUP BY cv.user_id;



