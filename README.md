# Learn with Jiji – The AI Learning Companion


## 🎬 Demo



## 🎯 Project Overview

This backend service:
- Accepts user learning queries via REST API (anonymous or authenticated)
- Stores queries in Supabase database
- Returns database-driven responses with relevant learning resources
- Implements full authentication and authorization via Supabase Auth
- Uses Row Level Security (RLS) for data protection
- Dynamically matches resources based on query content

## 🛠️ Tech Stack

- **Framework**: FastAPI (Python)
- **Database**: Supabase (PostgreSQL)
- **Authentication**: Supabase Auth (JWT)
- **Validation**: Pydantic


## 📁 Project Structure

```
learn-with-jiji-backend/
│
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Environment configuration
│   ├── supabase_client.py   # Supabase client initialization
│   ├── schemas.py           # Pydantic models for validation
│   ├── routes.py            # API endpoints
│
├── supabase/
│   └── schema.sql           # Database schema with RLS policies
│
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
└── README.md               # This file
```

## 🚀 How to Run Locally

### Prerequisites
- Python 3.9+
- Supabase account (free tier works)
- Git

### Step 1: Clone and Setup

```bash
cd learn-with-jiji-backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Configure Supabase

1. Create a new project at [supabase.com](https://supabase.com)
2. Go to SQL Editor and run the contents of `supabase/schema.sql`
3. Create a storage bucket named `learning-resources` (make it public)
4. Get your project URL and API keys from Settings > API

### Step 3: Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your Supabase credentials:
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
JWT_SECRET=your-jwt-secret
```

### Step 4: Run the Server

```bash
uvicorn app.main:app --reload
```

Server runs at: `http://localhost:8000`

API docs available at: `http://localhost:8000/docs`

## 📡 API Usage

### Authentication Endpoints

#### Sign Up: POST /api/auth/signup

**Request:**
```bash
curl -X POST "http://localhost:8000/api/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123",
    "name": "John Doe"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "uuid-here",
    "email": "user@example.com"
  }
}
```

#### Sign In: POST /api/auth/signin

**Request:**
```bash
curl -X POST "http://localhost:8000/api/auth/signin" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "uuid-here",
    "email": "user@example.com"
  }
}
```

#### Get Profile: GET /api/auth/me (Protected)

**Request:**
```bash
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Query Endpoints

#### Ask Jiji: POST /api/ask-jiji

**Request (Anonymous):**
```bash
curl -X POST "http://localhost:8000/api/ask-jiji" \
  -H "Content-Type: application/json" \
  -d '{"query": "Explain RAG"}'
```

**Request (Authenticated):**
```bash
curl -X POST "http://localhost:8000/api/ask-jiji" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{"query": "Explain RAG"}'
```

**Response:**
```json
{
  "answer": "Based on your query about 'Explain RAG', here's what I found:\n\n1. **RAG Introduction** (ppt): Learn the fundamentals of Retrieval-Augmented Generation...\n\nThese resources should provide you with comprehensive coverage of the topic.",
  "resources": [
    {
      "title": "RAG Introduction",
      "type": "ppt",
      "url": "https://storage.supabase.co/learning-resources/rag-intro.pptx"
    },
    {
      "title": "RAG Deep Dive",
      "type": "video",
      "url": "https://storage.supabase.co/learning-resources/rag-video.mp4"
    }
  ]
}
```

#### Get User Queries: GET /api/queries (Protected)

**Request:**
```bash
curl -X GET "http://localhost:8000/api/queries" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Health Check

```bash
curl http://localhost:8000/health
```

## 🔐 Supabase Auth & RLS

### Row Level Security (RLS)

**Profiles Table:**
- Users can only read/update their own profile
- Automatically created on user signup via trigger

**Queries Table:**
- Public insert allowed (for anonymous queries)
- Users can only read their own queries

**Resources Table:**
- Public read access (learning resources are public)
- Only authenticated users can insert new resources

### RLS Benefits
- Database-level security (not just application-level)
- Prevents unauthorized data access even if API is compromised
- Automatic filtering based on user context

## 🗄️ Database Schema

### Tables

1. **profiles** - User profile information
   - Linked to `auth.users` via foreign key
   - Stores email, name, avatar

2. **queries** - User learning queries
   - Stores all questions asked to Jiji
   - Optional user_id for authenticated users

3. **resources** - Learning materials
   - PPT, video, PDF, article types
   - Public URLs from Supabase Storage
   - Tagging system for categorization

## 🔒 Security Features

- No secrets in code (environment variables only)
- Input validation via Pydantic (max length, required fields)
- Row Level Security on all tables
- CORS configured for frontend integration
- JWT-based authentication ready

## 🎨 One Improvement with More Time

**Implement Vector Search for Semantic Resource Matching**

Instead of keyword-based matching, I would:
1. Generate embeddings for all learning resources using OpenAI/Cohere
2. Store embeddings in Supabase using pgvector extension
3. Convert user queries to embeddings
4. Perform similarity search to find most relevant resources
5. Integrate actual LLM (GPT-4, Claude) for answer generation

This would provide:
- More accurate resource recommendations
- Semantic understanding of queries
- Personalized learning paths based on user history
- Multi-language support



## 📝 License

MIT License - Feel free to use for learning and production.

## 👨‍💻 Author

Built as part of the "Learn with Jiji" assignment.
