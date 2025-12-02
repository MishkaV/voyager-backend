
  create table "public"."vibe_categories" (
    "id" uuid not null default gen_random_uuid(),
    "title" text not null
      );


alter table "public"."vibe_categories" enable row level security;


  create table "public"."vibes" (
    "id" uuid not null default gen_random_uuid(),
    "category_id" uuid not null,
    "title" text not null,
    "icon_emoji" text not null
      );


alter table "public"."vibes" enable row level security;


  create table "public"."vibes_country" (
    "country_id" uuid not null,
    "vibe_id" uuid not null
      );


alter table "public"."vibes_country" enable row level security;


  create table "public"."vibes_user" (
    "user_id" uuid not null,
    "vibe_id" uuid not null
      );


alter table "public"."vibes_user" enable row level security;

CREATE UNIQUE INDEX vibe_categories_pkey ON public.vibe_categories USING btree (id);

CREATE UNIQUE INDEX vibe_categories_title_key ON public.vibe_categories USING btree (title);

CREATE UNIQUE INDEX vibes_category_id_title_key ON public.vibes USING btree (category_id, title);

CREATE UNIQUE INDEX vibes_country_pkey ON public.vibes_country USING btree (country_id, vibe_id);

CREATE UNIQUE INDEX vibes_pkey ON public.vibes USING btree (id);

CREATE UNIQUE INDEX vibes_user_pkey ON public.vibes_user USING btree (user_id, vibe_id);

alter table "public"."vibe_categories" add constraint "vibe_categories_pkey" PRIMARY KEY using index "vibe_categories_pkey";

alter table "public"."vibes" add constraint "vibes_pkey" PRIMARY KEY using index "vibes_pkey";

alter table "public"."vibes_country" add constraint "vibes_country_pkey" PRIMARY KEY using index "vibes_country_pkey";

alter table "public"."vibes_user" add constraint "vibes_user_pkey" PRIMARY KEY using index "vibes_user_pkey";

alter table "public"."vibe_categories" add constraint "vibe_categories_title_key" UNIQUE using index "vibe_categories_title_key";

alter table "public"."vibes" add constraint "vibes_category_id_fkey" FOREIGN KEY (category_id) REFERENCES public.vibe_categories(id) ON DELETE RESTRICT not valid;

alter table "public"."vibes" validate constraint "vibes_category_id_fkey";

alter table "public"."vibes" add constraint "vibes_category_id_title_key" UNIQUE using index "vibes_category_id_title_key";

alter table "public"."vibes_country" add constraint "vibes_country_country_id_fkey" FOREIGN KEY (country_id) REFERENCES public.countries(id) ON DELETE CASCADE not valid;

alter table "public"."vibes_country" validate constraint "vibes_country_country_id_fkey";

alter table "public"."vibes_country" add constraint "vibes_country_vibe_id_fkey" FOREIGN KEY (vibe_id) REFERENCES public.vibes(id) ON DELETE RESTRICT not valid;

alter table "public"."vibes_country" validate constraint "vibes_country_vibe_id_fkey";

alter table "public"."vibes_user" add constraint "vibes_user_user_id_fkey" FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE not valid;

alter table "public"."vibes_user" validate constraint "vibes_user_user_id_fkey";

alter table "public"."vibes_user" add constraint "vibes_user_vibe_id_fkey" FOREIGN KEY (vibe_id) REFERENCES public.vibes(id) ON DELETE RESTRICT not valid;

alter table "public"."vibes_user" validate constraint "vibes_user_vibe_id_fkey";

grant delete on table "public"."vibe_categories" to "anon";

grant insert on table "public"."vibe_categories" to "anon";

grant references on table "public"."vibe_categories" to "anon";

grant select on table "public"."vibe_categories" to "anon";

grant trigger on table "public"."vibe_categories" to "anon";

grant truncate on table "public"."vibe_categories" to "anon";

grant update on table "public"."vibe_categories" to "anon";

grant delete on table "public"."vibe_categories" to "authenticated";

grant insert on table "public"."vibe_categories" to "authenticated";

grant references on table "public"."vibe_categories" to "authenticated";

grant select on table "public"."vibe_categories" to "authenticated";

grant trigger on table "public"."vibe_categories" to "authenticated";

grant truncate on table "public"."vibe_categories" to "authenticated";

grant update on table "public"."vibe_categories" to "authenticated";

grant delete on table "public"."vibe_categories" to "service_role";

grant insert on table "public"."vibe_categories" to "service_role";

grant references on table "public"."vibe_categories" to "service_role";

grant select on table "public"."vibe_categories" to "service_role";

grant trigger on table "public"."vibe_categories" to "service_role";

grant truncate on table "public"."vibe_categories" to "service_role";

grant update on table "public"."vibe_categories" to "service_role";

grant delete on table "public"."vibes" to "anon";

grant insert on table "public"."vibes" to "anon";

grant references on table "public"."vibes" to "anon";

grant select on table "public"."vibes" to "anon";

grant trigger on table "public"."vibes" to "anon";

grant truncate on table "public"."vibes" to "anon";

grant update on table "public"."vibes" to "anon";

grant delete on table "public"."vibes" to "authenticated";

grant insert on table "public"."vibes" to "authenticated";

grant references on table "public"."vibes" to "authenticated";

grant select on table "public"."vibes" to "authenticated";

grant trigger on table "public"."vibes" to "authenticated";

grant truncate on table "public"."vibes" to "authenticated";

grant update on table "public"."vibes" to "authenticated";

grant delete on table "public"."vibes" to "service_role";

grant insert on table "public"."vibes" to "service_role";

grant references on table "public"."vibes" to "service_role";

grant select on table "public"."vibes" to "service_role";

grant trigger on table "public"."vibes" to "service_role";

grant truncate on table "public"."vibes" to "service_role";

grant update on table "public"."vibes" to "service_role";

grant delete on table "public"."vibes_country" to "anon";

grant insert on table "public"."vibes_country" to "anon";

grant references on table "public"."vibes_country" to "anon";

grant select on table "public"."vibes_country" to "anon";

grant trigger on table "public"."vibes_country" to "anon";

grant truncate on table "public"."vibes_country" to "anon";

grant update on table "public"."vibes_country" to "anon";

grant delete on table "public"."vibes_country" to "authenticated";

grant insert on table "public"."vibes_country" to "authenticated";

grant references on table "public"."vibes_country" to "authenticated";

grant select on table "public"."vibes_country" to "authenticated";

grant trigger on table "public"."vibes_country" to "authenticated";

grant truncate on table "public"."vibes_country" to "authenticated";

grant update on table "public"."vibes_country" to "authenticated";

grant delete on table "public"."vibes_country" to "service_role";

grant insert on table "public"."vibes_country" to "service_role";

grant references on table "public"."vibes_country" to "service_role";

grant select on table "public"."vibes_country" to "service_role";

grant trigger on table "public"."vibes_country" to "service_role";

grant truncate on table "public"."vibes_country" to "service_role";

grant update on table "public"."vibes_country" to "service_role";

grant delete on table "public"."vibes_user" to "anon";

grant insert on table "public"."vibes_user" to "anon";

grant references on table "public"."vibes_user" to "anon";

grant select on table "public"."vibes_user" to "anon";

grant trigger on table "public"."vibes_user" to "anon";

grant truncate on table "public"."vibes_user" to "anon";

grant update on table "public"."vibes_user" to "anon";

grant delete on table "public"."vibes_user" to "authenticated";

grant insert on table "public"."vibes_user" to "authenticated";

grant references on table "public"."vibes_user" to "authenticated";

grant select on table "public"."vibes_user" to "authenticated";

grant trigger on table "public"."vibes_user" to "authenticated";

grant truncate on table "public"."vibes_user" to "authenticated";

grant update on table "public"."vibes_user" to "authenticated";

grant delete on table "public"."vibes_user" to "service_role";

grant insert on table "public"."vibes_user" to "service_role";

grant references on table "public"."vibes_user" to "service_role";

grant select on table "public"."vibes_user" to "service_role";

grant trigger on table "public"."vibes_user" to "service_role";

grant truncate on table "public"."vibes_user" to "service_role";

grant update on table "public"."vibes_user" to "service_role";


  create policy "Authenticated users can read vibe_categories"
  on "public"."vibe_categories"
  as permissive
  for select
  to authenticated
using (true);



  create policy "Authenticated users can read vibes"
  on "public"."vibes"
  as permissive
  for select
  to authenticated
using (true);



  create policy "Authenticated users can read vibes_country"
  on "public"."vibes_country"
  as permissive
  for select
  to authenticated
using (true);



  create policy "Users can delete own vibes"
  on "public"."vibes_user"
  as permissive
  for delete
  to authenticated
using ((( SELECT auth.uid() AS uid) = user_id));



  create policy "Users can insert own vibes"
  on "public"."vibes_user"
  as permissive
  for insert
  to authenticated
with check ((( SELECT auth.uid() AS uid) = user_id));



  create policy "Users can read own vibes"
  on "public"."vibes_user"
  as permissive
  for select
  to authenticated
using ((( SELECT auth.uid() AS uid) = user_id));



  create policy "Users can update own vibes"
  on "public"."vibes_user"
  as permissive
  for update
  to authenticated
using ((( SELECT auth.uid() AS uid) = user_id))
with check ((( SELECT auth.uid() AS uid) = user_id));



