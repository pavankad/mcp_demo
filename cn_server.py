from fastmcp import FastMCP
import requests
import urllib.parse

# Define API server base URL
API_BASE_URL = "http://127.0.0.1:5000/api"

mcp = FastMCP("CARE_NAVIGATOR")


# ---- Demographics Tools/Resources ----
@mcp.tool()
def get_patient_demographics(first_name: str, last_name: str, dob: str) -> dict:
    """Retrieve basic demographic information for a patient
       demographics API returns Age, email, phone, address, and insurance information.
    """
    try:
        # Call the API with demographic parameters directly
        response = requests.get(f"{API_BASE_URL}/demographics", 
                               params={"first_name": first_name, "last_name": last_name, "dob": dob})
        response.raise_for_status()
        data = response.json()
        
        # Handle empty results
        if not data:
            return {"error": f"No demographic information found for patient {first_name} {last_name}"}
            
        return data[0]  # Return the first (and should be only) result
    except requests.exceptions.RequestException as e:
        return {"error": f"API request error: {str(e)}"}


# ---- Engagement Tools/Resources ----
@mcp.tool()
def get_patient_engagement_metrics(first_name: str, last_name: str, dob: str, time_period: str = "30days") -> dict:
    """Get engagement status for a patient over a specified time period"""
    try:
        # Call the API with demographic parameters directly
        response = requests.get(f"{API_BASE_URL}/engagement", 
                               params={"first_name": first_name, "last_name": last_name, "dob": dob})
        response.raise_for_status()
        data = response.json()
        
        if not data:
            return {"error": f"No engagement metrics found for {first_name} {last_name}"}
            
        # Add time_period parameter to result even though the API doesn't use it currently
        result = data[0]
        result["time_period"] = time_period
        return result
    except requests.exceptions.RequestException as e:
        return {"error": f"API request error: {str(e)}"}


# ---- HRA Status Tools/Resources ----
@mcp.tool()
def get_patient_hra_status(first_name: str, last_name: str, dob: str) -> dict:
    """Get patient's Health Risk Assessment status"""
    try:
        # Call the API with demographic parameters directly
        response = requests.get(f"{API_BASE_URL}/hra_status", 
                               params={"first_name": first_name, "last_name": last_name, "dob": dob})
        response.raise_for_status()
        data = response.json()
        
        if not data:
            return {"error": f"No HRA status found for {first_name} {last_name}"}
            
        return data[0]
    except requests.exceptions.RequestException as e:
        return {"error": f"API request error: {str(e)}"}

# ---- Medical Conditions Tools/Resources ----
@mcp.tool()
def get_patient_medical_conditions(first_name: str, last_name: str, dob: str) -> dict:
    """Get patient's medical conditions, allergies, and medications"""
    try:
        # Call the API with demographic parameters directly
        response = requests.get(f"{API_BASE_URL}/medical_conditions", 
                               params={"first_name": first_name, "last_name": last_name, "dob": dob})
        response.raise_for_status()
        data = response.json()
        
        if not data:
            return {"error": f"No medical information found for {first_name} {last_name}"}
            
        return data[0]
    except requests.exceptions.RequestException as e:
        return {"error": f"API request error: {str(e)}"}


# ---- SDOH Resources Tools ----
@mcp.tool()
def get_patient_sdoh_resources(first_name: str, last_name: str, dob: str) -> dict:
    """Get Social Determinants of Health resources for a patient"""
    try:
        # Call the API with demographic parameters directly
        response = requests.get(f"{API_BASE_URL}/sdoh_resources", 
                               params={"first_name": first_name, "last_name": last_name, "dob": dob})
        response.raise_for_status()
        data = response.json()
        
        if not data:
            return {"resources": [], "message": f"No SDOH resources found for {first_name} {last_name}"}
            
        return {"resources": data, "count": len(data)}
    except requests.exceptions.RequestException as e:
        return {"error": f"API request error: {str(e)}"}

# ---- Complete Patient Data Tool ----
@mcp.tool()
def get_complete_patient_data(first_name: str, last_name: str, dob: str) -> dict:
    """Get complete patient data including demographics, medical, engagement, HRA status, and SDOH resources"""
    try:
        # Call the API with demographic parameters directly
        response = requests.get(f"{API_BASE_URL}/complete", 
                               params={"first_name": first_name, "last_name": last_name, "dob": dob})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"API request error: {str(e)}"}

# ---- Care Plan Tools ----
@mcp.tool()
def update_care_plan(first_name: str, last_name: str, dob: str, care_plan_items: list) -> dict:
    """Update a patient's care plan with new items"""
    try:
        # Call the find patient API to get patient_id
        response = requests.get(f"{API_BASE_URL}/find_patient", 
                               params={"first_name": first_name, "last_name": last_name, "dob": dob})
        response.raise_for_status()
        data = response.json()
        
        if "error" in data:
            return data
            
        patient_id = data.get("patient_id")
        
        # In a real implementation, this would make a POST/PUT request to your API
        return {"status": "updated", "patient_id": patient_id, "updated_items": len(care_plan_items)}
    except requests.exceptions.RequestException as e:
        return {"error": f"API request error: {str(e)}"}

@mcp.tool()
def update_sdoh_resources(first_name: str, last_name: str, dob: str, resources: list) -> dict:
    """
    Update or add SDOH resources for a patient
    
    Parameters:
    - first_name: Patient's first name
    - last_name: Patient's last name
    - dob: Patient's date of birth in YYYY-MM-DD format
    - resources: List of resources to update or add, each containing:
        - resource_id (optional): ID of existing resource to update
        - resource_type (required for new): Type of resource (e.g., "Food", "Housing")
        - provider (required for new): Name of service provider
        - status (required for new): Status of referral (e.g., "Referred", "Engaged")
        - referral_date (optional): Date of referral in YYYY-MM-DD format
        - notes (optional): Additional notes about the referral
    """
    try:
        # First, get patient_id from demographics
        response = requests.get(f"{API_BASE_URL}/find_patient", 
                              params={"first_name": first_name, "last_name": last_name, "dob": dob})
        response.raise_for_status()
        data = response.json()
        
        if "error" in data:
            return data
            
        patient_id = data.get("patient_id")
        
        # Prepare request payload for updating SDOH resources
        payload = {
            "patient_id": patient_id,
            "resources": resources
        }
        
        # Call the API to update resources
        response = requests.post(f"{API_BASE_URL}/sdoh_resources/update", json=payload)
        response.raise_for_status()
        result = response.json()
        
        # Add patient info to the response for context
        result["patient"] = f"{first_name} {last_name} (DOB: {dob})"
        
        return result
    except requests.exceptions.RequestException as e:
        return {"error": f"API request error: {str(e)}"}

@mcp.tool()
def delete_patient_sdoh_resources(first_name: str, last_name: str, dob: str) -> dict:
    """
    Delete all SDOH resources for a specific patient
    
    Parameters:
    - first_name: Patient's first name
    - last_name: Patient's last name
    - dob: Patient's date of birth in YYYY-MM-DD format
    """
    try:
        # First, get patient_id from demographics
        response = requests.get(f"{API_BASE_URL}/find_patient", 
                              params={"first_name": first_name, "last_name": last_name, "dob": dob})
        response.raise_for_status()
        data = response.json()
        
        if "error" in data:
            return data
            
        patient_id = data.get("patient_id")
        
        # Call the API to delete SDOH resources for this patient
        response = requests.delete(f"{API_BASE_URL}/sdoh_resources/delete/{patient_id}")
        response.raise_for_status()
        result = response.json()
        
        # Add patient info to the response for context
        result["patient"] = f"{first_name} {last_name} (DOB: {dob})"
        
        return result
    except requests.exceptions.RequestException as e:
        return {"error": f"API request error: {str(e)}"}



if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="127.0.0.1", port=8001)