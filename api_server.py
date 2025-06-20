from flask import Flask, jsonify, request
import pandas as pd
import os

app = Flask(__name__)

# Define base data directory
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "csv_data")

# Helper function to load CSV data
def load_csv_data(file_name):
    file_path = os.path.join(DATA_DIR, file_name)
    if not os.path.exists(file_path):
        return None
    return pd.read_csv(file_path)

# Helper function to find patient_id from demographics
def find_patient_id(first_name, last_name, dob):
    """Helper function to find a patient ID based on demographics"""
    # Load demographics data
    demographics_df = load_csv_data('demographics.csv')
    if demographics_df is None:
        return None
    
    # Find matching patient (case-insensitive for names)
    result = demographics_df[
        (demographics_df['first_name'].str.lower() == first_name.lower()) &
        (demographics_df['last_name'].str.lower() == last_name.lower()) &
        (demographics_df['date_of_birth'] == dob)
    ]
    
    if result.empty:
        return None
    
    return result['patient_id'].iloc[0]

@app.route('/api/find_patient', methods=['GET'])
def api_find_patient():
    """API endpoint to find a patient ID by demographics"""
    first_name = request.args.get('first_name')
    last_name = request.args.get('last_name')
    dob = request.args.get('dob')
    
    if not all([first_name, last_name, dob]):
        return jsonify({"error": "All parameters (first_name, last_name, dob) are required"}), 400
    
    patient_id = find_patient_id(first_name, last_name, dob)
    
    if patient_id:
        return jsonify({"patient_id": patient_id})
    else:
        return jsonify({"error": f"No patient found with name {first_name} {last_name} and DOB {dob}"}), 404

@app.route('/api/demographics', methods=['GET'])
def get_demographics():
    """Endpoint to fetch patient demographics data"""
    first_name = request.args.get('first_name')
    last_name = request.args.get('last_name')
    dob = request.args.get('dob')
    # Load demographics data
    demographics_df = load_csv_data('demographics.csv')
    if demographics_df is None:
        return jsonify({"error": "Demographics data not found"}), 404
    
    # Find by demographics if provided
    if all([first_name, last_name, dob]):
        patient_id = find_patient_id(first_name, last_name, dob)
        if not patient_id:
            return jsonify({"error": f"Patient with name {first_name} {last_name} and DOB {dob} not found"}), 404
        
        result = demographics_df[demographics_df['patient_id'] == patient_id]
        return jsonify(result.to_dict(orient='records'))
    
    # Return all records if no identifiers specified
    return jsonify(demographics_df.to_dict(orient='records'))

@app.route('/api/engagement', methods=['GET'])
def get_engagement():
    """Endpoint to fetch patient engagement metrics"""
    first_name = request.args.get('first_name')
    last_name = request.args.get('last_name')
    dob = request.args.get('dob')
    print(f"Received request for engagement data: {first_name} {last_name} {dob}")
    # Find by demographics if provided
    if all([first_name, last_name, dob]):
        patient_id = find_patient_id(first_name, last_name, dob)
        print(patient_id)
        if not patient_id:
            return jsonify({"error": f"Patient with name {first_name} {last_name} and DOB {dob} not found"}), 404
    
    # Load engagement data
    engagement_df = load_csv_data('engagement.csv')
    if engagement_df is None:
        return jsonify({"error": "Engagement data not found"}), 404
    
    # Find by demographics if provided
    if all([first_name, last_name, dob]):
        patient_id = find_patient_id(first_name, last_name, dob)
        if not patient_id:
            return jsonify({"error": f"Patient with name {first_name} {last_name} and DOB {dob} not found"}), 404
        
        result = engagement_df[engagement_df['patient_id'] == patient_id]
        if result.empty:
            return jsonify({"error": f"Engagement data not found for {first_name} {last_name}"}), 404
        return jsonify(result.to_dict(orient='records'))
    
    # Return all records if no identifiers specified
    return jsonify(engagement_df.to_dict(orient='records'))

@app.route('/api/hra_status', methods=['GET'])
def get_hra_status():
    """Endpoint to fetch Health Risk Assessment status"""
    first_name = request.args.get('first_name')
    last_name = request.args.get('last_name')
    dob = request.args.get('dob')
    
    # Load HRA status data
    hra_df = load_csv_data('hra_status.csv')
    if hra_df is None:
        return jsonify({"error": "HRA status data not found"}), 404
    
    # Find by demographics if provided
    if all([first_name, last_name, dob]):
        patient_id = find_patient_id(first_name, last_name, dob)
        if not patient_id:
            return jsonify({"error": f"Patient with name {first_name} {last_name} and DOB {dob} not found"}), 404
        
        result = hra_df[hra_df['patient_id'] == patient_id]
        if result.empty:
            return jsonify({"error": f"HRA status not found for {first_name} {last_name}"}), 404
        return jsonify(result.to_dict(orient='records'))
    
    # Return all records if no identifiers specified
    return jsonify(hra_df.to_dict(orient='records'))

@app.route('/api/medical_conditions', methods=['GET'])
def get_medical_conditions():
    """Endpoint to fetch medical conditions data"""
    first_name = request.args.get('first_name')
    last_name = request.args.get('last_name')
    dob = request.args.get('dob')
    
    # Load medical data
    medical_df = load_csv_data('medical.csv')
    if medical_df is None:
        return jsonify({"error": "Medical data not found"}), 404
    
    # Process pipe-separated values
    for column in ['allergies', 'conditions', 'medications']:
        medical_df[column] = medical_df[column].apply(
            lambda x: x.split('|') if pd.notna(x) and x != 'None' else []
        )
    
    # Find by demographics if provided
    if all([first_name, last_name, dob]):
        patient_id = find_patient_id(first_name, last_name, dob)
        if not patient_id:
            return jsonify({"error": f"Patient with name {first_name} {last_name} and DOB {dob} not found"}), 404
        
        result = medical_df[medical_df['patient_id'] == patient_id]
        if result.empty:
            return jsonify({"error": f"Medical data not found for {first_name} {last_name}"}), 404
        return jsonify(result.to_dict(orient='records'))
    
    # Return all records if no identifiers specified
    return jsonify(medical_df.to_dict(orient='records'))

@app.route('/api/sdoh_resources', methods=['GET'])
def get_sdoh_resources():
    """Endpoint to fetch Social Determinants of Health resources"""
    first_name = request.args.get('first_name')
    last_name = request.args.get('last_name')
    dob = request.args.get('dob')
    
    # Load SDOH resources data
    sdoh_df = load_csv_data('sdoh_resources.csv')
    if sdoh_df is None:
        return jsonify({"error": "SDOH resources data not found"}), 404
    
    # Find by demographics if provided
    if all([first_name, last_name, dob]):
        patient_id = find_patient_id(first_name, last_name, dob)
        if not patient_id:
            return jsonify({"error": f"Patient with name {first_name} {last_name} and DOB {dob} not found"}), 404
        
        result = sdoh_df[sdoh_df['patient_id'] == patient_id]
        if result.empty:
            return jsonify({"resources": [], "message": f"No SDOH resources found for {first_name} {last_name}"}), 200
        return jsonify(result.to_dict(orient='records'))
    
    # Return all records if no identifiers specified
    return jsonify(sdoh_df.to_dict(orient='records'))

@app.route('/api/sdoh_resources/update', methods=['POST'])
def update_sdoh_resources():
    """
    Endpoint to update or add SDOH resources for a patient
    
    Request body format:
    {
        "patient_id": "PT0F013D1E",  # Required - patient ID
        "resources": [
            {
                "resource_id": "RS41876",  # Optional for existing resources
                "resource_type": "Healthcare Access",  # Required for new resources
                "provider": "Healthcare Access Services of Federal",  # Required for new resources
                "status": "Engaged",  # Required for new resources
                "referral_date": "2025-05-22",  # Optional - defaults to today
                "notes": "Patient referred for healthcare access assistance"  # Optional
            },
            {
                # New resource - resource_id will be generated
                "resource_type": "Food",
                "provider": "Local Food Bank",
                "status": "Referred",
                "notes": "Patient needs food assistance"
            }
        ]
    }
    """
    # Parse JSON data from request
    data = request.get_json()
    
    # Validate required fields
    if not data or "patient_id" not in data or "resources" not in data:
        return jsonify({"error": "Invalid request data. 'patient_id' and 'resources' are required."}), 400
    
    patient_id = data["patient_id"]
    resources = data["resources"]
    
    # Load current SDOH resources data
    file_path = os.path.join(DATA_DIR, 'sdoh_resources.csv')
    sdoh_df = pd.read_csv(file_path) if os.path.exists(file_path) else pd.DataFrame(columns=[
        "resource_id", "patient_id", "resource_type", "provider", 
        "referral_date", "status", "notes"
    ])
    
    # Verify patient exists
    demographics_df = load_csv_data('demographics.csv')
    if demographics_df is None or not (demographics_df['patient_id'] == patient_id).any():
        return jsonify({"error": f"Patient with ID {patient_id} not found"}), 404
    
    # Track changes
    updated_resources = []
    new_resources = []
    
    # Process each resource in the request
    for resource in resources:
        # Check if this is an update to an existing resource
        if "resource_id" in resource and not pd.isna(resource["resource_id"]):
            resource_id = resource["resource_id"]
            # Find the resource in the dataframe
            mask = (sdoh_df["resource_id"] == resource_id) & (sdoh_df["patient_id"] == patient_id)
            
            if mask.any():
                # Update fields that are provided
                for field in ["resource_type", "provider", "status", "notes"]:
                    if field in resource:
                        sdoh_df.loc[mask, field] = resource[field]
                
                # Update referral date if provided
                if "referral_date" in resource:
                    sdoh_df.loc[mask, "referral_date"] = resource["referral_date"]
                
                updated_resources.append(resource_id)
            else:
                return jsonify({
                    "error": f"Resource {resource_id} not found for patient {patient_id}"
                }), 404
        else:
            # This is a new resource
            resource_id = f"RS{uuid.uuid4().hex[:5].upper()}"
            
            # Validate required fields for new resources
            if not all(key in resource for key in ["resource_type", "provider", "status"]):
                return jsonify({
                    "error": "New resources must include 'resource_type', 'provider', and 'status'"
                }), 400
            
            # Create new resource row
            new_row = {
                "resource_id": resource_id,
                "patient_id": patient_id,
                "resource_type": resource["resource_type"],
                "provider": resource["provider"],
                "referral_date": resource.get("referral_date", datetime.now().strftime("%Y-%m-%d")),
                "status": resource["status"],
                "notes": resource.get("notes", "")
            }
            
            # Add to dataframe
            sdoh_df = pd.concat([sdoh_df, pd.DataFrame([new_row])], ignore_index=True)
            new_resources.append(resource_id)
    
    # Save the updated dataframe back to CSV
    try:
        sdoh_df.to_csv(file_path, index=False)
        return jsonify({
            "success": True,
            "patient_id": patient_id,
            "updated_resources": updated_resources,
            "new_resources": new_resources
        }), 200
    except Exception as e:
        return jsonify({
            "error": f"Failed to save data: {str(e)}"
        }), 500


@app.route('/api/sdoh_resources/delete/<patient_id>', methods=['DELETE'])
def delete_patient_sdoh_resources(patient_id):
    """
    Endpoint to delete all SDOH resources for a specific patient
    
    URL parameter:
    - patient_id: The ID of the patient whose SDOH resources should be deleted
    """
    # Load current SDOH resources data
    file_path = os.path.join(DATA_DIR, 'sdoh_resources.csv')
    if not os.path.exists(file_path):
        return jsonify({"error": "SDOH resources data not found"}), 404
    
    sdoh_df = pd.read_csv(file_path)
    
    # Check if patient has any resources
    patient_resources = sdoh_df[sdoh_df["patient_id"] == patient_id]
    if patient_resources.empty:
        return jsonify({
            "success": True,
            "patient_id": patient_id,
            "resources_deleted": 0,
            "message": f"No SDOH resources found for patient {patient_id}"
        }), 200
    
    # Count resources to be deleted
    resources_count = len(patient_resources)
    resource_ids = patient_resources["resource_id"].tolist()
    
    # Remove resources for this patient
    sdoh_df = sdoh_df[sdoh_df["patient_id"] != patient_id]
    
    # Save the updated dataframe back to CSV
    try:
        sdoh_df.to_csv(file_path, index=False)
        return jsonify({
            "success": True,
            "patient_id": patient_id,
            "resources_deleted": resources_count,
            "deleted_resources": resource_ids
        }), 200
    except Exception as e:
        return jsonify({
            "error": f"Failed to save data: {str(e)}"
        }), 500

@app.route('/api/complete', methods=['GET'])
def get_patient_complete():
    """Endpoint to fetch complete patient data including all associated records"""
    first_name = request.args.get('first_name')
    last_name = request.args.get('last_name')
    dob = request.args.get('dob')
    
     # Find by demographics if provided
    if all([first_name, last_name, dob]):
        patient_id = find_patient_id(first_name, last_name, dob)
        if not patient_id:
            return jsonify({"error": f"No patient found with name {first_name} {last_name} and DOB {dob}"}), 404

    # Load all data
    demographics_df = load_csv_data('demographics.csv')
    medical_df = load_csv_data('medical.csv')
    engagement_df = load_csv_data('engagement.csv')
    hra_df = load_csv_data('hra_status.csv')
    sdoh_df = load_csv_data('sdoh_resources.csv')
    
    # Check if dataframes exist
    if any(df is None for df in [demographics_df, medical_df, engagement_df, hra_df, sdoh_df]):
        return jsonify({"error": "One or more required data files not found"}), 404
    
    # Process medical data pipe-separated values
    for column in ['allergies', 'conditions', 'medications']:
        medical_df[column] = medical_df[column].apply(
            lambda x: x.split('|') if pd.notna(x) and x != 'None' else []
        )
    
    # Filter data for the requested patient
    demographics = demographics_df[demographics_df['patient_id'] == patient_id]
    medical = medical_df[medical_df['patient_id'] == patient_id]
    engagement = engagement_df[engagement_df['patient_id'] == patient_id]
    hra = hra_df[hra_df['patient_id'] == patient_id]
    sdoh = sdoh_df[sdoh_df['patient_id'] == patient_id]
    
    # Check if patient exists
    if demographics.empty:
        return jsonify({"error": f"Patient with ID {patient_id} not found"}), 404
    
    # Combine all data into one response
    patient_data = {
        "demographics": demographics.to_dict(orient='records')[0] if not demographics.empty else None,
        "medical": medical.to_dict(orient='records')[0] if not medical.empty else None,
        "engagement": engagement.to_dict(orient='records')[0] if not engagement.empty else None,
        "hra_status": hra.to_dict(orient='records')[0] if not hra.empty else None,
        "sdoh_resources": sdoh.to_dict(orient='records') if not sdoh.empty else []
    }
    return jsonify(patient_data)


if __name__ == '__main__':
    app.run(debug=True, port=5000)