create type "public"."continent" as enum ('Europe', 'Asia', 'Africa', 'Oceania', 'North America', 'South America');

drop policy "Users can update their own profile" on "public"."profiles";

drop policy "Users can view their own profile" on "public"."profiles";


  create table "public"."countries" (
    "id" uuid not null default gen_random_uuid(),
    "iso2" text not null,
    "name" text not null,
    "capital" text not null,
    "continent" public.continent not null,
    "primary_language" text not null,
    "primary_language_code" text not null,
    "primary_currency" text not null,
    "primary_currency_code" text not null,
    "flag_url" text not null
      );


alter table "public"."countries" enable row level security;

CREATE UNIQUE INDEX countries_iso2_key ON public.countries USING btree (iso2);

CREATE UNIQUE INDEX countries_pkey ON public.countries USING btree (id);

alter table "public"."countries" add constraint "countries_pkey" PRIMARY KEY using index "countries_pkey";

alter table "public"."countries" add constraint "countries_iso2_check" CHECK ((iso2 = upper(iso2))) not valid;

alter table "public"."countries" validate constraint "countries_iso2_check";

alter table "public"."countries" add constraint "countries_iso2_key" UNIQUE using index "countries_iso2_key";

alter table "public"."countries" add constraint "countries_primary_currency_code_check" CHECK ((primary_currency_code = upper(primary_currency_code))) not valid;

alter table "public"."countries" validate constraint "countries_primary_currency_code_check";

alter table "public"."countries" add constraint "countries_primary_language_code_check" CHECK ((primary_language_code = upper(primary_language_code))) not valid;

alter table "public"."countries" validate constraint "countries_primary_language_code_check";

grant delete on table "public"."countries" to "anon";

grant insert on table "public"."countries" to "anon";

grant references on table "public"."countries" to "anon";

grant select on table "public"."countries" to "anon";

grant trigger on table "public"."countries" to "anon";

grant truncate on table "public"."countries" to "anon";

grant update on table "public"."countries" to "anon";

grant delete on table "public"."countries" to "authenticated";

grant insert on table "public"."countries" to "authenticated";

grant references on table "public"."countries" to "authenticated";

grant select on table "public"."countries" to "authenticated";

grant trigger on table "public"."countries" to "authenticated";

grant truncate on table "public"."countries" to "authenticated";

grant update on table "public"."countries" to "authenticated";

grant delete on table "public"."countries" to "service_role";

grant insert on table "public"."countries" to "service_role";

grant references on table "public"."countries" to "service_role";

grant select on table "public"."countries" to "service_role";

grant trigger on table "public"."countries" to "service_role";

grant truncate on table "public"."countries" to "service_role";

grant update on table "public"."countries" to "service_role";


  create policy "Authenticated users can read countries"
  on "public"."countries"
  as permissive
  for select
  to authenticated
using (true);



  create policy "Users can update their own profile"
  on "public"."profiles"
  as permissive
  for update
  to authenticated
using ((( SELECT auth.uid() AS uid) = id))
with check ((( SELECT auth.uid() AS uid) = id));



  create policy "Users can view their own profile"
  on "public"."profiles"
  as permissive
  for select
  to authenticated
using ((( SELECT auth.uid() AS uid) = id));



