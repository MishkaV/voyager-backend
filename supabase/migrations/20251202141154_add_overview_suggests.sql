
  create table "public"."country_ai_suggests" (
    "id" uuid not null default gen_random_uuid(),
    "country_id" uuid,
    "suggest_text" text not null,
    "prompt" text not null
      );


alter table "public"."country_ai_suggests" enable row level security;


  create table "public"."country_best_times" (
    "id" uuid not null default gen_random_uuid(),
    "country_id" uuid not null,
    "title" text not null,
    "description" text not null
      );


alter table "public"."country_best_times" enable row level security;


  create table "public"."country_overview" (
    "id" uuid not null default gen_random_uuid(),
    "country_id" uuid not null,
    "body" text not null,
    "wikipedia_url" text not null
      );


alter table "public"."country_overview" enable row level security;

CREATE UNIQUE INDEX country_ai_suggests_pkey ON public.country_ai_suggests USING btree (id);

CREATE UNIQUE INDEX country_best_times_pkey ON public.country_best_times USING btree (id);

CREATE UNIQUE INDEX country_overview_pkey ON public.country_overview USING btree (id);

alter table "public"."country_ai_suggests" add constraint "country_ai_suggests_pkey" PRIMARY KEY using index "country_ai_suggests_pkey";

alter table "public"."country_best_times" add constraint "country_best_times_pkey" PRIMARY KEY using index "country_best_times_pkey";

alter table "public"."country_overview" add constraint "country_overview_pkey" PRIMARY KEY using index "country_overview_pkey";

alter table "public"."country_ai_suggests" add constraint "country_ai_suggests_country_id_fkey" FOREIGN KEY (country_id) REFERENCES public.countries(id) ON DELETE CASCADE not valid;

alter table "public"."country_ai_suggests" validate constraint "country_ai_suggests_country_id_fkey";

alter table "public"."country_best_times" add constraint "country_best_times_country_id_fkey" FOREIGN KEY (country_id) REFERENCES public.countries(id) ON DELETE CASCADE not valid;

alter table "public"."country_best_times" validate constraint "country_best_times_country_id_fkey";

alter table "public"."country_overview" add constraint "country_overview_country_id_fkey" FOREIGN KEY (country_id) REFERENCES public.countries(id) ON DELETE CASCADE not valid;

alter table "public"."country_overview" validate constraint "country_overview_country_id_fkey";

grant delete on table "public"."country_ai_suggests" to "anon";

grant insert on table "public"."country_ai_suggests" to "anon";

grant references on table "public"."country_ai_suggests" to "anon";

grant select on table "public"."country_ai_suggests" to "anon";

grant trigger on table "public"."country_ai_suggests" to "anon";

grant truncate on table "public"."country_ai_suggests" to "anon";

grant update on table "public"."country_ai_suggests" to "anon";

grant delete on table "public"."country_ai_suggests" to "authenticated";

grant insert on table "public"."country_ai_suggests" to "authenticated";

grant references on table "public"."country_ai_suggests" to "authenticated";

grant select on table "public"."country_ai_suggests" to "authenticated";

grant trigger on table "public"."country_ai_suggests" to "authenticated";

grant truncate on table "public"."country_ai_suggests" to "authenticated";

grant update on table "public"."country_ai_suggests" to "authenticated";

grant delete on table "public"."country_ai_suggests" to "service_role";

grant insert on table "public"."country_ai_suggests" to "service_role";

grant references on table "public"."country_ai_suggests" to "service_role";

grant select on table "public"."country_ai_suggests" to "service_role";

grant trigger on table "public"."country_ai_suggests" to "service_role";

grant truncate on table "public"."country_ai_suggests" to "service_role";

grant update on table "public"."country_ai_suggests" to "service_role";

grant delete on table "public"."country_best_times" to "anon";

grant insert on table "public"."country_best_times" to "anon";

grant references on table "public"."country_best_times" to "anon";

grant select on table "public"."country_best_times" to "anon";

grant trigger on table "public"."country_best_times" to "anon";

grant truncate on table "public"."country_best_times" to "anon";

grant update on table "public"."country_best_times" to "anon";

grant delete on table "public"."country_best_times" to "authenticated";

grant insert on table "public"."country_best_times" to "authenticated";

grant references on table "public"."country_best_times" to "authenticated";

grant select on table "public"."country_best_times" to "authenticated";

grant trigger on table "public"."country_best_times" to "authenticated";

grant truncate on table "public"."country_best_times" to "authenticated";

grant update on table "public"."country_best_times" to "authenticated";

grant delete on table "public"."country_best_times" to "service_role";

grant insert on table "public"."country_best_times" to "service_role";

grant references on table "public"."country_best_times" to "service_role";

grant select on table "public"."country_best_times" to "service_role";

grant trigger on table "public"."country_best_times" to "service_role";

grant truncate on table "public"."country_best_times" to "service_role";

grant update on table "public"."country_best_times" to "service_role";

grant delete on table "public"."country_overview" to "anon";

grant insert on table "public"."country_overview" to "anon";

grant references on table "public"."country_overview" to "anon";

grant select on table "public"."country_overview" to "anon";

grant trigger on table "public"."country_overview" to "anon";

grant truncate on table "public"."country_overview" to "anon";

grant update on table "public"."country_overview" to "anon";

grant delete on table "public"."country_overview" to "authenticated";

grant insert on table "public"."country_overview" to "authenticated";

grant references on table "public"."country_overview" to "authenticated";

grant select on table "public"."country_overview" to "authenticated";

grant trigger on table "public"."country_overview" to "authenticated";

grant truncate on table "public"."country_overview" to "authenticated";

grant update on table "public"."country_overview" to "authenticated";

grant delete on table "public"."country_overview" to "service_role";

grant insert on table "public"."country_overview" to "service_role";

grant references on table "public"."country_overview" to "service_role";

grant select on table "public"."country_overview" to "service_role";

grant trigger on table "public"."country_overview" to "service_role";

grant truncate on table "public"."country_overview" to "service_role";

grant update on table "public"."country_overview" to "service_role";


  create policy "Authenticated users can read country_ai_suggests"
  on "public"."country_ai_suggests"
  as permissive
  for select
  to authenticated
using (true);



  create policy "Authenticated users can read country_best_times"
  on "public"."country_best_times"
  as permissive
  for select
  to authenticated
using (true);



  create policy "Authenticated users can read country_overview"
  on "public"."country_overview"
  as permissive
  for select
  to authenticated
using (true);



