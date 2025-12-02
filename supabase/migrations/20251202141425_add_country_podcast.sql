
  create table "public"."country_podcasts" (
    "id" uuid not null default gen_random_uuid(),
    "country_id" uuid not null,
    "audio_url" text not null,
    "title" text not null,
    "subtitle" text not null,
    "duration_sec" integer not null
      );


alter table "public"."country_podcasts" enable row level security;

CREATE UNIQUE INDEX country_podcasts_pkey ON public.country_podcasts USING btree (id);

alter table "public"."country_podcasts" add constraint "country_podcasts_pkey" PRIMARY KEY using index "country_podcasts_pkey";

alter table "public"."country_podcasts" add constraint "country_podcasts_country_id_fkey" FOREIGN KEY (country_id) REFERENCES public.countries(id) ON DELETE CASCADE not valid;

alter table "public"."country_podcasts" validate constraint "country_podcasts_country_id_fkey";

grant delete on table "public"."country_podcasts" to "anon";

grant insert on table "public"."country_podcasts" to "anon";

grant references on table "public"."country_podcasts" to "anon";

grant select on table "public"."country_podcasts" to "anon";

grant trigger on table "public"."country_podcasts" to "anon";

grant truncate on table "public"."country_podcasts" to "anon";

grant update on table "public"."country_podcasts" to "anon";

grant delete on table "public"."country_podcasts" to "authenticated";

grant insert on table "public"."country_podcasts" to "authenticated";

grant references on table "public"."country_podcasts" to "authenticated";

grant select on table "public"."country_podcasts" to "authenticated";

grant trigger on table "public"."country_podcasts" to "authenticated";

grant truncate on table "public"."country_podcasts" to "authenticated";

grant update on table "public"."country_podcasts" to "authenticated";

grant delete on table "public"."country_podcasts" to "service_role";

grant insert on table "public"."country_podcasts" to "service_role";

grant references on table "public"."country_podcasts" to "service_role";

grant select on table "public"."country_podcasts" to "service_role";

grant trigger on table "public"."country_podcasts" to "service_role";

grant truncate on table "public"."country_podcasts" to "service_role";

grant update on table "public"."country_podcasts" to "service_role";


  create policy "Authenticated users can read country_podcasts"
  on "public"."country_podcasts"
  as permissive
  for select
  to authenticated
using (true);



