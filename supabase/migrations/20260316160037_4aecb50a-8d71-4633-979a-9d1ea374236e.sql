-- Remove overly permissive insert policy since edge function uses service role
DROP POLICY IF EXISTS "Allow anonymous inserts" ON public.early_access_submissions;