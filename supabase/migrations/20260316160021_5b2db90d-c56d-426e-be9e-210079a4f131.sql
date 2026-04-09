-- Create early_access_submissions table
CREATE TABLE public.early_access_submissions (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  full_name TEXT NOT NULL,
  email TEXT NOT NULL,
  clinic_name TEXT,
  role TEXT,
  phone TEXT,
  source TEXT NOT NULL DEFAULT 'early_access_form',
  status TEXT NOT NULL DEFAULT 'new',
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  last_submitted_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Unique constraint on email for upsert
ALTER TABLE public.early_access_submissions ADD CONSTRAINT early_access_submissions_email_unique UNIQUE (email);

-- Enable RLS
ALTER TABLE public.early_access_submissions ENABLE ROW LEVEL SECURITY;

-- Allow anonymous inserts (the edge function uses service role, but this is a safety net)
CREATE POLICY "Allow anonymous inserts" ON public.early_access_submissions
  FOR INSERT TO anon, authenticated
  WITH CHECK (true);

-- No public reads - only accessible via service role / dashboard
CREATE POLICY "No public reads" ON public.early_access_submissions
  FOR SELECT TO anon, authenticated
  USING (false);