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