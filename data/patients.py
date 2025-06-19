import json
import random
import uuid
from datetime import datetime, timedelta
import os

def generate_patient_data(num_patients=10):
    """Generate mock patient demographics data"""
    
    # Lists for generating realistic mock data
    first_names = ["James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", 
                  "Linda", "David", "Elizabeth", "William", "Susan", "Richard", "Jessica"]
    last_names = ["Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", 
                 "Wilson", "Moore", "Taylor", "Anderson", "Thomas", "Jackson", "White"]
    genders = ["Male", "Female", "Non-binary", "Other", "Prefer not to say"]
    blood_types = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    ethnicities = ["Caucasian", "African American", "Hispanic", "Asian", "Pacific Islander", 
                  "Native American", "Mixed", "Other"]
    marital_statuses = ["Single", "Married", "Divorced", "Widowed", "Separated"]
    insurance_providers = ["Aetna", "Blue Cross", "Cigna", "UnitedHealth", "Humana", 
                          "Kaiser", "Medicare", "Medicaid"]
    
    patients = []
    
    for i in range(num_patients):
        # Generate unique patient ID
        patient_id = f"PT{str(uuid.uuid4())[:8].upper()}"
        
        # Generate basic demographics
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        gender = random.choice(genders)
        age = random.randint(18, 90)
        
        # Generate date of birth based on age
        today = datetime.now()
        birth_year = today.year - age
        birth_month = random.randint(1, 12)
        birth_day = random.randint(1, 28)  # Simplifying to avoid month length issues
        dob = datetime(birth_year, birth_month, birth_day)

        # Generate random dates within 2025
        start_month = random.randint(1, 10)  # Jan to Oct to leave room for end date
        start_day = random.randint(1, 28)  # Avoiding month-end date issues
        start_date = datetime(2025, start_month, start_day)
        
        # Ensure end_date is after start_date (between 10-90 days later, still in 2025)
        end_date = start_date + timedelta(days=random.randint(10, 90))
        if end_date.year > 2025:  # Ensure we stay in 2025
            end_date = datetime(2025, 12, random.randint(1, 28))
        
        # Generate more detailed demographics
        patient = {
            "patient_id": patient_id,
            "demographics": {
                "first_name": first_name,
                "last_name": last_name,
                "full_name": f"{first_name} {last_name}",
                "gender": gender,
                "age": age,
                "date_of_birth": dob.strftime("%Y-%m-%d"),
                "blood_type": random.choice(blood_types),
                "ethnicity": random.choice(ethnicities),
                "marital_status": random.choice(marital_statuses),
                "ssn": f"{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(1000, 9999)}",
                "contact": {
                    "email": f"{first_name.lower()}.{last_name.lower()}@example.com",
                    "phone": f"{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                    "address": f"{random.randint(100, 9999)} Main St, Anytown, ST {random.randint(10000, 99999)}"
                },
                "insurance": {
                    "provider": random.choice(insurance_providers),
                    "policy_number": f"{random.randint(100000, 999999)}",
                    "group_number": f"{random.randint(1000, 9999)}"
                }
            },
            "medical": {
                "allergies": random.sample(["Penicillin", "Peanuts", "Latex", "Shellfish", "None", "Pollen", "Dust"], 
                                          k=random.randint(0, 3)),
                "conditions": random.sample(["Hypertension", "Diabetes", "Asthma", "Depression", "Arthritis", "None"], 
                                           k=random.randint(0, 2)),
                "medications": random.sample(["Lisinopril", "Metformin", "Atorvastatin", "Levothyroxine", "None"], 
                                           k=random.randint(0, 3))
            },
            "engagement": {
                # Format dates as strings
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "last_visit": (datetime.now() - timedelta(days=random.randint(1, 365))).strftime("%Y-%m-%d")
            }
        }
        patients.append(patient)
    
    return patients

def write_patients_to_json(patients, filename="patients.json"):
    """Write patient data to a JSON file"""
    # Ensure the directory exists
    directory = os.path.dirname(os.path.abspath(filename))
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    # Write to file
    with open(filename, 'w') as f:
        json.dump(patients, f, indent=2)
    
    print(f"Successfully wrote {len(patients)} patient records to {filename}")

if __name__ == "__main__":
    # Generate 10 patients
    patients = generate_patient_data(10)
    
    # Write to JSON file in the data directory
    output_path = os.path.join(os.path.dirname(__file__), "patients.json")
    write_patients_to_json(patients, output_path)
    
    # Print sample
    print(f"\nSample patient record (ID: {patients[0]['patient_id']}):")
    print(json.dumps(patients[0], indent=2))