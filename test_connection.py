from supabase_config import supabase

try:

    response = (
        supabase
        .table("assessment_history")
        .select("id")
        .limit(1)
        .execute()
    )

    print("Supabase database connection successful!")

    print("Database response:", response.data)

except Exception as e:

    print("Connection failed:", e)