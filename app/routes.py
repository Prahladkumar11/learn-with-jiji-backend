from fastapi import APIRouter, HTTPException, Depends
from app.schemas import QueryRequest, QueryResponse, Resource, SignUpRequest, SignInRequest, AuthResponse
from app.supabase_client import get_supabase
from app.auth import get_current_user, get_optional_user
from datetime import datetime
from typing import List, Dict, Any

router = APIRouter()

def build_answer_from_resources(query: str, resources: List[Dict[str, Any]]) -> str:
    """Generate natural language answer from database resources"""
    if not resources:
        return f"I couldn't find specific resources about '{query}' in our database. Please try rephrasing your question or explore our general learning materials."
    
    intro = f"Based on your query about '{query}', here's what I found:\n\n"
    
    summaries = []
    for idx, resource in enumerate(resources, 1):
        title = resource.get('title', 'Untitled')
        desc = resource.get('description', '')
        r_type = resource.get('resource_type', 'resource')
        
        if desc:
            summaries.append(f"{idx}. **{title}** ({r_type}): {desc}")
        else:
            summaries.append(f"{idx}. **{title}** - A {r_type} resource to help you learn more.")
    
    body = "\n\n".join(summaries)
    conclusion = "\n\nThese resources should provide you with comprehensive coverage of the topic. Feel free to explore them in any order that suits your learning style."
    
    return intro + body + conclusion

@router.post("/ask-jiji", response_model=QueryResponse)
async def ask_jiji(request: QueryRequest, user: dict = Depends(get_optional_user)):
    """Handle user queries with dynamic database-driven responses"""
    try:
        supabase = get_supabase()
        query_text = request.query.lower()
        
        # Store query in database
        query_data = {
            "query_text": request.query,
            "created_at": datetime.utcnow().isoformat()
        }
        if user:
            query_data["user_id"] = user["user_id"]
        
        supabase.table("queries").insert(query_data).execute()
        
        # Search resources by title, description, and tags
        response = supabase.table("resources").select("*").or_(
            f"title.ilike.%{query_text}%,description.ilike.%{query_text}%,tags.cs.{{{query_text}}}"
        ).limit(5).execute()
        
        matched_resources = response.data
        
        # Build dynamic answer from matched resources
        answer = build_answer_from_resources(request.query, matched_resources)
        
        # Format resources for response
        resources = [
            Resource(
                title=r["title"],
                type=r["resource_type"],
                url=r["url"]
            ) for r in matched_resources
        ]
        
        return QueryResponse(answer=answer, resources=resources)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@router.post("/auth/signup", response_model=AuthResponse)
async def signup(request: SignUpRequest):
    """Register new user with Supabase Auth"""
    try:
        supabase = get_supabase()
        response = supabase.auth.sign_up({
            "email": request.email,
            "password": request.password,
            "options": {"data": {"name": request.name}} if request.name else {}
        })
        
        if not response.user or not response.session:
            raise HTTPException(status_code=400, detail="Signup failed. Check if email confirmation is required.")
        
        return AuthResponse(
            access_token=response.session.access_token,
            user={"id": response.user.id, "email": response.user.email}
        )
    except HTTPException:
        raise
    except Exception as e:
        if "rate limit" in str(e).lower():
            raise HTTPException(status_code=429, detail="Rate limit exceeded. Please wait a few minutes and try again.")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/auth/signin", response_model=AuthResponse)
async def signin(request: SignInRequest):
    """Sign in existing user"""
    try:
        supabase = get_supabase()
        response = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })
        
        if not response.user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        return AuthResponse(
            access_token=response.session.access_token,
            user={"id": response.user.id, "email": response.user.email}
        )
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@router.get("/auth/me")
async def get_profile(user: dict = Depends(get_current_user)):
    """Get current user profile (protected route)"""
    try:
        supabase = get_supabase()
        profile = supabase.table("profiles").select("*").eq("id", user["user_id"]).single().execute()
        return profile.data
    except Exception as e:
        raise HTTPException(status_code=404, detail="Profile not found")

@router.get("/queries")
async def get_user_queries(user: dict = Depends(get_current_user)):
    """Get all queries for authenticated user"""
    try:
        supabase = get_supabase()
        queries = supabase.table("queries").select("*").eq("user_id", user["user_id"]).order("created_at", desc=True).execute()
        return queries.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
