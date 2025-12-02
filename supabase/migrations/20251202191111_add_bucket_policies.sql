
  create policy "Give users authenticated access to folder 1m21l3_0"
  on "storage"."objects"
  as permissive
  for select
  to public
using (((bucket_id = 'flags'::text) AND ((storage.foldername(name))[1] = 'private'::text) AND (auth.role() = 'authenticated'::text)));



  create policy "Give users authenticated access to folder podcasts 55x1bj_0"
  on "storage"."objects"
  as permissive
  for select
  to public
using (((bucket_id = 'podcasts'::text) AND ((storage.foldername(name))[1] = 'private'::text) AND (auth.role() = 'authenticated'::text)));



