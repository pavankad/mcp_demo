import csv
import os
import random
from datetime import datetime, timedelta
from patients import generate_patient_data

def create_directory_if_not_exists(directory_path):
    """Create directory if it doesn't exist"""
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"Created directory: {directory_path}")

def generate_hra_status(patients):
    """Generate Health Risk Assessment status data for patients"""
    hra_data = []
    status_options = ["Completed", "Pending", "Not Started", "Expired"]
    risk_levels = [1, 2, 3, 4, 5]  # Risk levels from 1 (low) to 5 (high)

    for patient in patients:
        status = random.choice(status_options)
        completion_date = None
        risk_score = None
        risk_level = None
        
        if status == "Completed":
            completion_date = (datetime.now() - timedelta(days=random.randint(1, 180))).strftime("%Y-%m-%d")
            risk_score = random.randint(0, 100)
            risk_level = random.choice(risk_levels)
        
        hra_data.append({
            "patient_id": patient["patient_id"],
            "status": status,
            "completion_date": completion_date if completion_date else "",
            "risk_score": risk_score if risk_score else "",
            "risk_level": risk_level if risk_levels else "",
            "next_assessment_due": (datetime.now() + timedelta(days=random.randint(30, 365))).strftime("%Y-%m-%d")
        })
    
    return hra_data

def generate_sdoh_resources(patients):
    """Generate Social Determinants of Health resources data for patients"""
    sdoh_data = []
    resource_types = ["Housing", "Food", "Transportation", "Education", "Employment", "Financial", "Healthcare Access", "Social Support"]
    status_options = ["Referred", "Engaged", "Completed", "Declined", "Not Eligible"]
    
    # Each patient might have multiple resources
    for patient in patients:
        # Generate 0-3 resources per patient
        num_resources = random.randint(0, 3)
        for i in range(num_resources):
            resource_type = random.choice(resource_types)
            sdoh_data.append({
                "resource_id": f"RS{str(random.randint(10000, 99999))}",
                "patient_id": patient["patient_id"],
                "resource_type": resource_type,
                "provider": f"{resource_type} Services of {random.choice(['Metro Area', 'County', 'State', 'Federal'])}",
                "referral_date": (datetime.now() - timedelta(days=random.randint(1, 90))).strftime("%Y-%m-%d"),
                "status": random.choice(status_options),
                "notes": f"Patient referred for {resource_type.lower()} assistance" if random.random() > 0.5 else ""
            })
    
    return sdoh_data

def write_demographics_csv(patients, output_dir):
    """Write patient demographics to CSV"""
    filepath = os.path.join(output_dir, "demographics.csv")
    
    with open(filepath, 'w', newline='') as csvfile:
        fieldnames = ["patient_id", "first_name", "last_name", "full_name", "gender", 
                     "age", "date_of_birth", "blood_type", "ethnicity", "marital_status", 
                     "ssn", "email", "phone", "address", "insurance_provider", 
                     "policy_number", "group_number"]
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for patient in patients:
            writer.writerow({
                "patient_id": patient["patient_id"],
                "first_name": patient["demographics"]["first_name"],
                "last_name": patient["demographics"]["last_name"],
                "full_name": patient["demographics"]["full_name"],
                "gender": patient["demographics"]["gender"],
                "age": patient["demographics"]["age"],
                "date_of_birth": patient["demographics"]["date_of_birth"],
                "blood_type": patient["demographics"]["blood_type"],
                "ethnicity": patient["demographics"]["ethnicity"],
                "marital_status": patient["demographics"]["marital_status"],
                "ssn": patient["demographics"]["ssn"],
                "email": patient["demographics"]["contact"]["email"],
                "phone": patient["demographics"]["contact"]["phone"],
                "address": patient["demographics"]["contact"]["address"],
                "insurance_provider": patient["demographics"]["insurance"]["provider"],
                "policy_number": patient["demographics"]["insurance"]["policy_number"],
                "group_number": patient["demographics"]["insurance"]["group_number"]
            })
    
    print(f"Demographics data written to {filepath}")

def write_medical_csv(patients, output_dir):
    """Write patient medical information to CSV"""
    filepath = os.path.join(output_dir, "medical.csv")
    
    with open(filepath, 'w', newline='') as csvfile:
        fieldnames = ["patient_id", "allergies", "conditions", "medications"]
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for patient in patients:
            writer.writerow({
                "patient_id": patient["patient_id"],
                "allergies": "|".join(patient["medical"]["allergies"]) if patient["medical"]["allergies"] else "None",
                "conditions": "|".join(patient["medical"]["conditions"]) if patient["medical"]["conditions"] else "None",
                "medications": "|".join(patient["medical"]["medications"]) if patient["medical"]["medications"] else "None"
            })
    
    print(f"Medical data written to {filepath}")

def write_engagement_csv(patients, output_dir):
    """Write patient engagement metrics to CSV"""
    filepath = os.path.join(output_dir, "engagement.csv")
    
    with open(filepath, 'w', newline='') as csvfile:
        fieldnames = ["patient_id", "start_date", "end_date", "last_visit"]
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for patient in patients:
            writer.writerow({
                "patient_id": patient["patient_id"],
                "start_date": patient["engagement"]["start_date"],
                "end_date": patient["engagement"]["end_date"],
                "last_visit": patient["engagement"]["last_visit"]
            })
    
    print(f"Engagement data written to {filepath}")

def write_hra_status_csv(hra_data, output_dir):
    """Write HRA status to CSV"""
    filepath = os.path.join(output_dir, "hra_status.csv")
    
    with open(filepath, 'w', newline='') as csvfile:
        fieldnames = ["patient_id", "status", "completion_date", "risk_score", "risk_level", "next_assessment_due"]
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for hra in hra_data:
            writer.writerow(hra)
    
    print(f"HRA status data written to {filepath}")

def write_sdoh_resources_csv(sdoh_data, output_dir):
    """Write SDOH resources to CSV"""
    filepath = os.path.join(output_dir, "sdoh_resources.csv")
    
    with open(filepath, 'w', newline='') as csvfile:
        fieldnames = ["resource_id", "patient_id", "resource_type", "provider", "referral_date", "status", "notes"]
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for resource in sdoh_data:
            writer.writerow(resource)
    
    print(f"SDOH resources data written to {filepath}")

if __name__ == "__main__":
    # Generate patient data
    num_patients = 10
    patients = generate_patient_data(num_patients)
    
    # Generate additional data
    hra_data = generate_hra_status(patients)
    sdoh_data = generate_sdoh_resources(patients)
    
    # Create output directory
    output_dir = os.path.join(os.path.dirname(__file__), "csv_data")
    create_directory_if_not_exists(output_dir)
    
    # Write data to CSV files
    write_demographics_csv(patients, output_dir)
    write_medical_csv(patients, output_dir)
    write_engagement_csv(patients, output_dir)
    write_hra_status_csv(hra_data, output_dir)
    write_sdoh_resources_csv(sdoh_data, output_dir)
    
    print(f"\nGenerated CSV files for {num_patients} patients in {output_dir}")