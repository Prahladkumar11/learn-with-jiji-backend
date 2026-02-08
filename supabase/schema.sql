-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Profiles table (linked to auth.users)
CREATE TABLE profiles (
    id UUID REFERENCES auth.users(id) PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    avatar_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Queries table (stores user queries)
CREATE TABLE queries (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    query_text TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Resources table (PPT and Video resources)
CREATE TABLE resources (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    title TEXT NOT NULL,
    resource_type TEXT NOT NULL CHECK (resource_type IN ('ppt', 'video', 'pdf', 'article')),
    url TEXT NOT NULL,
    description TEXT,
    tags TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE queries ENABLE ROW LEVEL SECURITY;
ALTER TABLE resources ENABLE ROW LEVEL SECURITY;

-- RLS Policies for profiles
CREATE POLICY "Users can read own profile"
    ON profiles FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
    ON profiles FOR UPDATE
    USING (auth.uid() = id);

-- RLS Policies for queries
CREATE POLICY "Anyone can insert queries"
    ON queries FOR INSERT
    TO public
    WITH CHECK (true);

CREATE POLICY "Users can read own queries"
    ON queries FOR SELECT
    USING (auth.uid() = user_id OR user_id IS NULL);

-- RLS Policies for resources
CREATE POLICY "Public can read resources"
    ON resources FOR SELECT
    TO public
    USING (true);

CREATE POLICY "Authenticated users can insert resources"
    ON resources FOR INSERT
    TO authenticated
    WITH CHECK (true);

-- Create indexes for performance
CREATE INDEX idx_queries_user_id ON queries(user_id);
CREATE INDEX idx_queries_created_at ON queries(created_at DESC);
CREATE INDEX idx_resources_type ON resources(resource_type);
CREATE INDEX idx_resources_created_at ON resources(created_at DESC);

-- Function to automatically create profile on user signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email, full_name)
    VALUES (NEW.id, NEW.email, NEW.raw_user_meta_data->>'full_name');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to create profile on signup
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Insert sample resources
INSERT INTO resources (title, resource_type, url, description, tags) VALUES
    ('Introduction to RAG', 'ppt', 'https://your-project.supabase.co/storage/v1/object/public/learning-resources/rag-intro.pptx', 'Learn the basics of Retrieval-Augmented Generation', ARRAY['AI', 'RAG', 'NLP']),
    ('RAG Deep Dive Video', 'video', 'https://your-project.supabase.co/storage/v1/object/public/learning-resources/rag-video.mp4', 'Comprehensive video tutorial on RAG implementation', ARRAY['AI', 'RAG', 'Tutorial']),
    ('Machine Learning Fundamentals', 'ppt', 'https://your-project.supabase.co/storage/v1/object/public/learning-resources/ml-fundamentals.pptx', 'Core concepts of machine learning', ARRAY['ML', 'Fundamentals']),
    ('Python for Beginners', 'video', 'https://your-project.supabase.co/storage/v1/object/public/learning-resources/python-basics.mp4', 'Getting started with Python programming', ARRAY['Python', 'Programming', 'Beginner']);
