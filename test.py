from supabase import create_client
import os
from dotenv import load_dotenv




# Force authentication using API key

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Debugging: Print API Key (only for testing)
print("Supabase URL:", SUPABASE_URL)
print("Supabase Key:", SUPABASE_KEY[:10] + "********")  # Mask most of the key for security

# Create Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
supabase.postgrest.auth(SUPABASE_KEY)

# Test connection with a simple query
try:
    response = supabase.table("department").select("*").execute()
    print(response)
except Exception as e:
    print(f"Error: {e}")
