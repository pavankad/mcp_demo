from fastmcp import FastMCP

mcp = FastMCP("CARE_NAVIGATOR")


@mcp.resource("engagement://metrics/{patient_id}")
def get_engagement_resource(patient_id: str) -> dict:
    """Get engagement data as a resource"""
    # Call your existing API endpoint here
    return {"app_logins": 12, "message_count": 5, "appointment_adherence": 0.9}