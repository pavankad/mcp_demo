import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import json
from io import StringIO
import re
import asyncio
import os

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from langgraph.prebuilt import create_react_agent

from azure.identity import DefaultAzureCredential, get_bearer_token_provider

# Get Azure token
default_credential = DefaultAzureCredential()
access_token = default_credential.get_token("https://cognitiveservices.azure.com/.default")

# Set API key from the access token
os.environ['OPENAI_API_KEY'] = access_token.token
os.environ['AZURE_OPENAI_ENDPOINT'] = 'https://api.uhg.com/api/cloud/api-management/ai-gateway/1.0'
# Define the MCP server URL
MCP_SERVER_URL = "http://127.0.0.1:8001/mcp"

# Initialize model with Azure-specific parameters
model = AzureChatOpenAI(
    azure_deployment="gpt-4o_2024-05-13",  # The deployment name in Azure
    api_version="2025-01-01-preview",  # Azure API version
    default_headers={
        "projectId": "f440d3f1-df7a-45fb-a62f-5953aaf6bd55",
        "x-idp": "azuread"
    }
)



# Set page configuration
st.set_page_config(
    page_title="Care Navigator",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        margin-bottom: 1rem;
    }
    .section-header {
        font-size: 1.5rem;
        color: #0277BD;
        margin-top: 1rem;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .info-box-success {
        background-color: #E8F5E9;
        border-left: 5px solid #4CAF50;
    }
    .info-box-warning {
        background-color: #FFF8E1;
        border-left: 5px solid #FFC107;
    }
    .info-box-error {
        background-color: #FFEBEE;
        border-left: 5px solid #F44336;
    }
    .stButton button {
        background-color: #1976D2;
        color: white;
        font-weight: 500;
    }
    .metric-card {
        background-color: #E3F2FD;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)


# Function to get community resources based on zipcode and resource type
def get_community_services(resource_type, zipcode):
    """
    Searches for community services based on zipcode and resource type.
    This simulates an API call to an external service like FindHelp.org or 211.org.
    
    In a production environment, replace this with actual API calls.
    """
    try:
        # First, convert zipcode to coordinates using geocoding
        geolocator = Nominatim(user_agent="care_navigator_app")
        location = geolocator.geocode(f"{zipcode}, USA")
        
        if not location:
            return {"error": f"Could not geocode zipcode {zipcode}"}
        
        # Simulate API delay
        time.sleep(1)
        
        # Simulate API results with realistic data
        service_types = {
            "food": [
                {"name": "Local Food Bank", "address": f"{zipcode} Main St", "phone": "555-123-4567", "website": "foodbank.org", "distance": f"{random.randint(1, 5)}.{random.randint(1, 9)} miles"},
                {"name": "Community Pantry", "address": f"{zipcode} Oak Ave", "phone": "555-987-6543", "website": "communitypantry.org", "distance": f"{random.randint(1, 5)}.{random.randint(1, 9)} miles"},
                {"name": "Meals on Wheels", "address": f"{zipcode} Elm St", "phone": "555-789-0123", "website": "mealsonwheels.org", "distance": f"{random.randint(1, 5)}.{random.randint(1, 9)} miles"}
            ],
            "transportation": [
                {"name": "Medical Transit", "address": f"{zipcode} Pine Rd", "phone": "555-321-7654", "website": "medicaltransit.org", "distance": f"{random.randint(1, 5)}.{random.randint(1, 9)} miles"},
                {"name": "Senior Rides", "address": f"{zipcode} Cedar Ln", "phone": "555-456-7890", "website": "seniorrides.org", "distance": f"{random.randint(1, 5)}.{random.randint(1, 9)} miles"},
                {"name": "Community Transport", "address": f"{zipcode} Maple Ave", "phone": "555-234-5678", "website": "communitytransport.org", "distance": f"{random.randint(1, 5)}.{random.randint(1, 9)} miles"}
            ],
            "housing": [
                {"name": "Housing Assistance", "address": f"{zipcode} Birch St", "phone": "555-876-5432", "website": "housinghelp.org", "distance": f"{random.randint(1, 5)}.{random.randint(1, 9)} miles"},
                {"name": "Shelter Services", "address": f"{zipcode} Willow Rd", "phone": "555-654-3210", "website": "shelterservices.org", "distance": f"{random.randint(1, 5)}.{random.randint(1, 9)} miles"},
                {"name": "Transitional Housing", "address": f"{zipcode} Aspen Ave", "phone": "555-210-9876", "website": "transitionalhousing.org", "distance": f"{random.randint(1, 5)}.{random.randint(1, 9)} miles"}
            ],
            "utilities": [
                {"name": "Utility Assistance", "address": f"{zipcode} Spruce St", "phone": "555-543-2109", "website": "utilityhelp.org", "distance": f"{random.randint(1, 5)}.{random.randint(1, 9)} miles"},
                {"name": "Energy Assistance", "address": f"{zipcode} Fir Ave", "phone": "555-432-1098", "website": "energyhelp.org", "distance": f"{random.randint(1, 5)}.{random.randint(1, 9)} miles"}
            ]
        }
        
        # Default to food services if resource type not found
        resource_type_key = resource_type.lower()
        services = service_types.get(resource_type_key, service_types["food"])
        
        # Add location data to each service
        for service in services:
            # In a real implementation, you would use the location's coordinates to calculate actual distance
            # For now, we'll use random distances for demonstration
            service["lat"] = location.latitude + (random.random() - 0.5) * 0.05
            service["lon"] = location.longitude + (random.random() - 0.5) * 0.05
        
        return {"services": services, "location": {"lat": location.latitude, "lon": location.longitude}}
        
    except Exception as e:
        return {"error": str(e)}


# Helper function to send query to the MCP server
async def query_mcp(query):
    """Main function to process queries using the MCP client."""
    client = MultiServerMCPClient({
        "mcpstore": {
            "url": "http://127.0.0.1:8001/mcp",  # Replace with the remote server's URL
            "transport": "streamable_http"
        }
    })
    tools = await client.get_tools()
    agent = create_react_agent(model, tools)
    response = await agent.ainvoke({"messages": query})
    return response

def get_ai_message(response):
    """Parse AI message and convert to structured data"""
    # Extract the text content from the AI message
    ai_text = None
    for message in response["messages"]:
        if type(message).__name__ == "AIMessage" and message.content:
            ai_text = message.content
            break
    
    if not ai_text:
        return {"error": "No AI response found"}
    
    print(f"------AI response------\n{ai_text}")
    
    # Parse the structured data from the AI text response
    structured_data = {}
    
    # Helper function to extract section data
    def extract_section(text, section_name):
        pattern = rf"### {section_name}(.*?)(?=### |$)"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None
    
    # Extract demographics data
    demographics_text = extract_section(ai_text, "Demographics")
    if demographics_text:
        demographics = {}
        # Extract key-value pairs from bullet points
        for line in demographics_text.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.replace('**', '').replace('-', '').strip()
                value = value.strip()
                demographics[key.lower().replace(' ', '_')] = value
        structured_data['demographics'] = demographics
    
    # Extract engagement data
    engagement_text = extract_section(ai_text, "Engagement")
    if engagement_text:
        engagement = {}
        for line in engagement_text.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.replace('**', '').replace('-', '').strip()
                value = value.strip()
                engagement[key.lower().replace(' ', '_')] = value
        structured_data['engagement'] = engagement
    
    # Extract HRA status data
    hra_text = extract_section(ai_text, "Health Risk Assessment")
    if hra_text:
        hra_status = {}
        for line in hra_text.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.replace('**', '').replace('-', '').strip()
                value = value.strip()
                
                # Store the key-value pair in the hra_status dictionary
                hra_status[key.lower().replace(' ', '_')] = value
                
                # Ensure risk_level is numeric (1-5) if present
                if key.lower() == 'risk level':
                    # If it's already a number between 1-5, keep it
                    if value.isdigit() and 1 <= int(value) <= 5:
                        hra_status['risk_level'] = value
                    # Otherwise, try to convert text descriptions to numbers
                    elif value.lower() in ["very low", "low", "medium", "high", "critical"]:
                        risk_map = {
                            "very low": "1",
                            "low": "2", 
                            "medium": "3",
                            "high": "4",
                            "critical": "5"
                        }
                        hra_status['risk_level'] = risk_map.get(value.lower(), value)
        
        structured_data['hra_status'] = hra_status
    
    # Extract medical information
    medical_text = extract_section(ai_text, "Medical Information")
    if medical_text:
        medical = {}
        for line in medical_text.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.replace('**', '').replace('-', '').strip()
                value = value.strip()
                # Convert to lists if appropriate
                if value == "None":
                    value = []
                else:
                    value = [v.strip() for v in value.split(',')]
                medical[key.lower().replace(' ', '_')] = value
        structured_data['medical'] = medical
    
    # Extract SDOH resources
    sdoh_text = extract_section(ai_text, "Social Determinants of Health")
    if sdoh_text:
        sdoh_resources = []
        resource = {}
        lines = sdoh_text.split('\n')
        
        for i, line in enumerate(lines):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.replace('**', '').replace('-', '').strip()
                value = value.strip()
                
                # Create keys that match your UI's expected format
                if key == "Resource Type":
                    resource['resource_type'] = value
                elif key == "Provider":
                    resource['provider'] = value
                elif key == "Referral Date":
                    resource['referral_date'] = value
                elif key == "Status":
                    resource['status'] = value
                    
                # If this is the last line of the resource or the last line overall,
                # add the resource to the list and reset
                if i == len(lines) - 1 or (i + 1 < len(lines) and "Resource Type" in lines[i + 1]):
                    sdoh_resources.append(resource)
                    resource = {}
        
        structured_data['sdoh_resources'] = sdoh_resources
    
    return structured_data
# Display header
st.markdown('<h1 class="main-header">Care Navigator Dashboard</h1>', unsafe_allow_html=True)

# Create sidebar for patient search
st.sidebar.markdown('<h2 class="section-header">Patient Search</h2>', unsafe_allow_html=True)

# Patient search form
with st.sidebar.form("patient_search_form"):
    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    dob = st.date_input("Date of Birth", min_value=datetime(1900, 1, 1))
    
    # Format the date as YYYY-MM-DD
    dob_str = dob.strftime("%Y-%m-%d")
    
    search_submitted = st.form_submit_button("Search Patient")

# Initialize session state for storing patient data
if 'patient_data' not in st.session_state:
    st.session_state.patient_data = None
    
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "Dashboard"

# If search button is clicked, fetch patient data
if search_submitted and first_name and last_name and dob_str:
    with st.spinner("Searching for patient..."):
        # Get complete patient data
        result = asyncio.run(query_mcp(f"Get complete information about patient {first_name} {last_name} with DOB {dob_str}"))
        if "error" in result:
            st.error(result["error"])
        else:
            st.session_state.patient_data = get_ai_message(result)
            st.success(f"Found patient: {first_name} {last_name}")

# Sidebar navigation
st.sidebar.markdown('<h2 class="section-header">Navigation</h2>', unsafe_allow_html=True)
tab_options = ["Dashboard", "Demographics", "Medical", "Engagement", "HRA Status", "SDOH Resources", "Free-text Query"]
active_tab = st.sidebar.radio("Select Section", tab_options)
st.session_state.active_tab = active_tab

# Check if patient data is available
if st.session_state.patient_data:
    # Display patient banner
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"<h2>{first_name} {last_name}</h2>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<p>DOB: {dob_str}</p>", unsafe_allow_html=True)
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Dashboard tab
    if st.session_state.active_tab == "Dashboard":
        st.markdown('<h2 class="section-header">Patient Dashboard</h2>', unsafe_allow_html=True)
        
        # Create columns for key metrics
        col1, col2, col3 = st.columns(3)
        
        # Display patient summary information
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown("### Demographics")
            st.write(f"Age: {st.session_state.patient_data.get('demographics', {}).get('age', 'N/A')}")
            st.write(f"Gender: {st.session_state.patient_data.get('demographics', {}).get('gender', 'N/A')}")
            st.write(f"Insurance: {st.session_state.patient_data.get('demographics', {}).get('insurance_provider', 'N/A')}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown("### Health Risk")
            hra_status = st.session_state.patient_data.get('hra_status', {})
            status = hra_status.get('status', 'Unknown')
            risk_level = hra_status.get('risk_level', 'N/A')
            
            st.write(f"HRA Status: {status}")
            if risk_level != 'N/A':
                st.write(f"Risk Level: {risk_level}")
            st.write(f"Next Assessment: {hra_status.get('next_assessment_due', 'N/A')}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown("### Engagement")
            engagement = st.session_state.patient_data.get('engagement', {})
            st.write(f"Start Date: {engagement.get('start_date', 'N/A')}")
            st.write(f"End Date: {engagement.get('end_date', 'N/A')}")
            st.write(f"Last Visit: {engagement.get('last_visit', 'N/A')}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Medical summary
        st.markdown('<h3 class="section-header">Medical Summary</h3>', unsafe_allow_html=True)
        medical = st.session_state.patient_data.get('medical', {})
        
        if medical:
            conditions = medical.get('conditions', [])
            medications = medical.get('medications', [])
            allergies = medical.get('allergies', [])
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Conditions")
                if conditions and len(conditions) > 0 and conditions[0] != 'None':
                    for condition in conditions:
                        st.write(f"- {condition}")
                else:
                    st.write("No conditions reported")
                
                st.markdown("#### Allergies")
                if allergies and len(allergies) > 0 and allergies[0] != 'None':
                    for allergy in allergies:
                        st.write(f"- {allergy}")
                else:
                    st.write("No allergies reported")
            
            with col2:
                st.markdown("#### Medications")
                if medications and len(medications) > 0 and medications[0] != 'None':
                    for medication in medications:
                        st.write(f"- {medication}")
                else:
                    st.write("No medications reported")
        
        # SDOH resources
        st.markdown('<h3 class="section-header">SDOH Resources</h3>', unsafe_allow_html=True)
        sdoh_resources = st.session_state.patient_data.get('sdoh_resources', [])
        
        if sdoh_resources and len(sdoh_resources) > 0:
            df = pd.DataFrame(sdoh_resources)
            st.dataframe(df[['resource_type', 'provider', 'status', 'referral_date']], use_container_width=True)
        else:
            st.info("No SDOH resources found for this patient")
    
    # Demographics tab
    elif st.session_state.active_tab == "Demographics":
        st.markdown('<h2 class="section-header">Patient Demographics</h2>', unsafe_allow_html=True)
        
        demographics = st.session_state.patient_data.get('demographics', {})
        
        if demographics:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Personal Information")
                st.write(f"**Full Name:** {demographics.get('full_name', 'N/A')}")
                st.write(f"**Gender:** {demographics.get('gender', 'N/A')}")
                st.write(f"**Age:** {demographics.get('age', 'N/A')}")
                st.write(f"**Date of Birth:** {demographics.get('date_of_birth', 'N/A')}")
                st.write(f"**SSN:** {demographics.get('ssn', 'N/A')}")
                st.write(f"**Marital Status:** {demographics.get('marital_status', 'N/A')}")
                st.write(f"**Ethnicity:** {demographics.get('ethnicity', 'N/A')}")
                st.write(f"**Blood Type:** {demographics.get('blood_type', 'N/A')}")
            
            with col2:
                st.markdown("### Contact Information")
                st.write(f"**Email:** {demographics.get('email', 'N/A')}")
                st.write(f"**Phone:** {demographics.get('phone', 'N/A')}")
                st.write(f"**Address:** {demographics.get('address', 'N/A')}")
                
                st.markdown("### Insurance Information")
                st.write(f"**Provider:** {demographics.get('insurance_provider', 'N/A')}")
                st.write(f"**Policy Number:** {demographics.get('policy_number', 'N/A')}")
                st.write(f"**Group Number:** {demographics.get('group_number', 'N/A')}")
        else:
            st.info("No demographic information available for this patient")
    
    # Medical tab
    elif st.session_state.active_tab == "Medical":
        st.markdown('<h2 class="section-header">Medical Information</h2>', unsafe_allow_html=True)
        
        medical = st.session_state.patient_data.get('medical', {})
        
        if medical:
            conditions = medical.get('conditions', [])
            medications = medical.get('medications', [])
            allergies = medical.get('allergies', [])
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="info-box info-box-warning">', unsafe_allow_html=True)
                st.markdown("### Conditions")
                if conditions and len(conditions) > 0 and conditions[0] != 'None':
                    for condition in conditions:
                        st.write(f"- {condition}")
                else:
                    st.write("No conditions reported")
                st.markdown('</div>', unsafe_allow_html=True)
                
                st.markdown('<div class="info-box info-box-error">', unsafe_allow_html=True)
                st.markdown("### Allergies")
                if allergies and len(allergies) > 0 and allergies[0] != 'None':
                    for allergy in allergies:
                        st.write(f"- {allergy}")
                else:
                    st.write("No allergies reported")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="info-box info-box-success">', unsafe_allow_html=True)
                st.markdown("### Medications")
                if medications and len(medications) > 0 and medications[0] != 'None':
                    for medication in medications:
                        st.write(f"- {medication}")
                else:
                    st.write("No medications reported")
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No medical information available for this patient")
    
    # Engagement tab
    elif st.session_state.active_tab == "Engagement":
        st.markdown('<h2 class="section-header">Patient Engagement</h2>', unsafe_allow_html=True)
        
        engagement = st.session_state.patient_data.get('engagement', {})
        
        if engagement:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Engagement Dates")
                st.write(f"**Start Date:** {engagement.get('start_date', 'N/A')}")
                st.write(f"**End Date:** {engagement.get('end_date', 'N/A')}")
                st.write(f"**Last Visit:** {engagement.get('last_visit', 'N/A')}")
            
            with col2:
                st.markdown("### Engagement Timeline")
                
                # Create a dataframe for timeline visualization
                engagement_dates = {
                    'Event': ['Start', 'Last Visit', 'End'],
                    'Date': [
                        engagement.get('start_date', 'N/A'),
                        engagement.get('last_visit', 'N/A'),
                        engagement.get('end_date', 'N/A')
                    ]
                }
                
                # Only include valid dates
                valid_dates = []
                valid_events = []
                for i, date in enumerate(engagement_dates['Date']):
                    if date != 'N/A':
                        try:
                            # Try to parse the date to ensure it's valid
                            valid_dates.append(datetime.strptime(date, '%Y-%m-%d'))
                            valid_events.append(engagement_dates['Event'][i])
                        except:
                            pass
                
                if valid_dates:
                    # Create a proper dataframe with valid dates
                    chart_df = pd.DataFrame({
                        'Event': valid_events,
                        'Date': valid_dates
                    })
                    # Sort by date
                    chart_df = chart_df.sort_values('Date')
                    
                    # Create a simple timeline chart
                    st.markdown("#### Timeline")
                    st.line_chart(chart_df.set_index('Date').reset_index().index)
                    
                    # Create a table with the dates
                    st.markdown("#### Engagement Dates")
                    st.dataframe(chart_df, use_container_width=True)
        else:
            st.info("No engagement information available for this patient")
    
    # HRA Status tab
    elif st.session_state.active_tab == "HRA Status":
        st.markdown('<h2 class="section-header">Health Risk Assessment Status</h2>', unsafe_allow_html=True)
        
        hra_status = st.session_state.patient_data.get('hra_status', {})
        
        if hra_status:
            status = hra_status.get('status', 'Unknown')
            
            # Display a different UI based on HRA status
            if status == 'Completed':
                st.markdown('<div class="info-box info-box-success">', unsafe_allow_html=True)
                st.markdown(f"### Status: {status}")
                st.write(f"**Completion Date:** {hra_status.get('completion_date', 'N/A')}")
                st.write(f"**Risk Score:** {hra_status.get('risk_score', 'N/A')}")
                st.write(f"**Risk Level:** {hra_status.get('risk_level', 'N/A')}")
                st.write(f"**Next Assessment Due:** {hra_status.get('next_assessment_due', 'N/A')}")
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Display risk score as a gauge
                risk_score = int(hra_status.get('risk_score', 0))
                st.markdown("### Risk Score")
                st.progress(risk_score/100)
                
            elif status == 'Pending':
                st.markdown('<div class="info-box info-box-warning">', unsafe_allow_html=True)
                st.markdown(f"### Status: {status}")
                st.write("This patient's Health Risk Assessment is pending completion.")
                st.write(f"**Next Assessment Due:** {hra_status.get('next_assessment_due', 'N/A')}")
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Add a button to simulate sending a reminder
                if st.button("Send HRA Reminder"):
                    st.success("Reminder sent to patient!")
                    
            elif status == 'Not Started':
                st.markdown('<div class="info-box info-box-error">', unsafe_allow_html=True)
                st.markdown(f"### Status: {status}")
                st.write("This patient has not started their Health Risk Assessment.")
                st.write(f"**Next Assessment Due:** {hra_status.get('next_assessment_due', 'N/A')}")
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Add a button to simulate scheduling an assessment
                if st.button("Schedule HRA"):
                    st.success("Health Risk Assessment scheduled!")
                    
            else:  # Expired or other
                st.markdown('<div class="info-box info-box-error">', unsafe_allow_html=True)
                st.markdown(f"### Status: {status}")
                st.write("This patient's Health Risk Assessment has expired or has an unknown status.")
                st.write(f"**Next Assessment Due:** {hra_status.get('next_assessment_due', 'N/A')}")
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No HRA status information available for this patient")
    
    # SDOH Resources tab
    elif st.session_state.active_tab == "SDOH Resources":
        st.markdown('<h2 class="section-header">Social Determinants of Health Resources</h2>', unsafe_allow_html=True)
        
        # Get patient's demographics to extract zip code
        demographics = st.session_state.patient_data.get('demographics', {})
        patient_address = demographics.get('address', '')
        
        # Extract zip code from address (assuming US format where zip code is last 5 digits)
        patient_zipcode = None
        if patient_address:
            # Try to extract zipcode from address using regex
            zip_match = re.search(r'(\d{5}(?:-\d{4})?)', patient_address)
            if zip_match:
                patient_zipcode = zip_match.group(1)[:5]  # Take only first 5 digits
        
        # Display patient address and zip code if available
        if patient_address:
            st.markdown("### Patient Location")
            st.write(f"**Address:** {patient_address}")
            if patient_zipcode:
                st.write(f"**ZIP Code:** {patient_zipcode}")
        
        # Display existing SDOH resources
        sdoh_resources = st.session_state.patient_data.get('sdoh_resources', [])
        
        if sdoh_resources and len(sdoh_resources) > 0:
            # Create a DataFrame for the resources
            df = pd.DataFrame(sdoh_resources)
            
            # Display a filterable table
            st.markdown("### Patient Resources")
            st.dataframe(df, use_container_width=True)
            
            # Show distribution of resource types if the column exists
            if 'resource_type' in df.columns:
                st.markdown("### Resource Types Distribution")
                resource_types = df['resource_type'].value_counts().reset_index()
                resource_types.columns = ['Resource Type', 'Count']
                st.bar_chart(resource_types.set_index('Resource Type'))
                
                # Show referral status distribution if the column exists
                if 'status' in df.columns:
                    st.markdown("### Referral Status")
                    status_counts = df['status'].value_counts().reset_index()
                    status_counts.columns = ['Status', 'Count']
                    st.bar_chart(status_counts.set_index('Status'))
        
        # Add the "Add New Resource Referral" section
        st.markdown("### Add New Resource Referral")
        col1, col2 = st.columns(2)
        
        # Initialize session state for provider and notes if they don't exist
        if 'provider' not in st.session_state:
            st.session_state.provider = ""
        if 'notes' not in st.session_state:
            st.session_state.notes = ""
            
        with col1:
            resource_type = st.selectbox(
                "Resource Type",
                ["Housing", "Food", "Transportation", "Utilities", "Education", "Employment", "Financial", "Healthcare Access", "Social Support"]
            )
            provider = st.text_input("Provider Name", value=st.session_state.provider)
        with col2:
            notes = st.text_area("Notes", value=st.session_state.notes)
        
        # Search for community services if we have a zip code
        if patient_zipcode:
            st.markdown(f"### Available {resource_type} Resources Near {patient_zipcode}")
            
            # Import required modules if not already imported
            from geopy.geocoders import Nominatim
            import time
            import random
            
            with st.spinner(f"Finding {resource_type} resources near {patient_zipcode}..."):
                # Get community services for the selected resource type and patient's zip code
                services_result = get_community_services(resource_type.lower(), patient_zipcode)
                
                if "error" in services_result:
                    st.error(f"Error finding resources: {services_result['error']}")
                else:
                    services = services_result.get("services", [])
                    location = services_result.get("location", {})
                    
                    if services:
                        # Sort services by distance (assuming distance is in format "X.Y miles")
                        def extract_distance(distance_str):
                            try:
                                return float(distance_str.split()[0])
                            except:
                                return float('inf')  # If parsing fails, place at end
                        
                        services.sort(key=lambda x: extract_distance(x['distance']))
                        closest_service = services[0]  # Get the closest service
                        
                        # Create a dataframe to display all services
                        services_df = pd.DataFrame(services)
                        st.markdown("#### All Available Resources (Sorted by Distance)")
                        st.dataframe(services_df, use_container_width=True)
                        
                        # Show the closest service with visual highlight
                        st.markdown("#### Closest Resource (Auto-selected)")
                        st.markdown(f"""
                        <div style="padding: 1rem; background-color: #E8F5E9; border-left: 5px solid #4CAF50; border-radius: 0.5rem; margin-bottom: 1rem;">
                            <h5 style="color: #2E7D32;">{closest_service['name']}</h5>
                            <p><strong>Address:</strong> {closest_service['address']}<br>
                            <strong>Phone:</strong> {closest_service['phone']}<br>
                            <strong>Distance:</strong> {closest_service['distance']}<br>
                            <strong>Website:</strong> {closest_service.get('website', 'N/A')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Auto-populate the provider and notes fields with the closest service
                        st.session_state.provider = closest_service['name']
                        st.session_state.notes = f"Address: {closest_service['address']}\nPhone: {closest_service['phone']}\nWebsite: {closest_service.get('website', 'N/A')}\nDistance: {closest_service['distance']}"
                        
                        # Update the form fields
                        provider = closest_service['name']
                        notes = st.session_state.notes
                        
                        # Show a map if we have location data
                        if location:
                            st.markdown("#### Map of Resources")
                            map_data = pd.DataFrame({
                                'name': [s['name'] for s in services],
                                'lat': [s['lat'] for s in services],
                                'lon': [s['lon'] for s in services]
                            })
                            st.map(map_data)
                            
                        # Option to choose a different service
                        st.markdown("#### Select Different Resource")
                        selected_service_index = st.selectbox(
                            "Select a different resource if preferred:",
                            range(len(services)),
                            format_func=lambda i: f"{services[i]['name']} - {services[i]['distance']}",
                            key="service_selector"
                        )
                        
                        if st.button("Use Selected Resource"):
                            selected_service = services[selected_service_index]
                            st.session_state.provider = selected_service['name']
                            st.session_state.notes = f"Address: {selected_service['address']}\nPhone: {selected_service['phone']}\nWebsite: {selected_service.get('website', 'N/A')}\nDistance: {selected_service['distance']}"
                            #st.experimental_rerun()
                    else:
                        st.info(f"No {resource_type.lower()} resources found near ZIP {patient_zipcode}")
        else:
            st.warning("Patient's ZIP code could not be detected. Please update the patient's address information.")
        
        # Add referral button
        if st.button("Add Referral"):
            if not provider:
                st.error("Please enter a provider name")
            else:
                with st.spinner("Adding referral..."):
                    # Simulate API call to add the referral
                    st.success(f"Referral added for {resource_type} services with provider {provider}!")
                    
                    # Reset the form fields
                    st.session_state.provider = ""
                    st.session_state.notes = ""
    
    # Free-text Query tab
    elif st.session_state.active_tab == "Free-text Query":
        st.markdown('<h2 class="section-header">Free-text Patient Information Query</h2>', unsafe_allow_html=True)
        
        st.markdown("""
        Enter your question about the patient in natural language. For example:
        - What is the patient's latest HRA status?
        - Does the patient have any allergies?
        - When was the patient's last visit?
        - What social support resources have been referred to the patient?
        """)
        
        query = st.text_input("Your Question", key="free_text_query")
        
        if st.button("Ask"):
            if query:
                with st.spinner("Processing your question..."):
                    # Send the query to the MCP server
                    result = asyncio.run(query_mcp(query))
                    if "error" in result:
                        st.error(result["error"])
                    else:
                        st.markdown('<div class="info-box info-box-success">', unsafe_allow_html=True)
                        st.markdown("### Answer")
                        st.write(result.get("answer", "No answer found"))
                        st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.warning("Please enter a question")

else:
    # No patient data available, show welcome screen
    st.markdown("""
    # Welcome to Care Navigator
    
    Use the search form in the sidebar to find a patient by name and date of birth.
    
    Once you've found a patient, you can:
    - View their demographic information
    - Check their medical conditions and medications
    - Monitor their engagement with healthcare services
    - Review their Health Risk Assessment (HRA) status
    - Manage Social Determinants of Health (SDOH) resources
    - Ask free-text questions about the patient
    
    **Get started by searching for a patient.**
    """)

    # Display a sample patient card
    st.markdown("""
    ## Sample Patient
    """)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### Michael Brown")
        st.write("DOB: 1997-09-15")
        st.write("Age: 28")
        st.write("Insurance: UnitedHealth")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### Elizabeth Anderson")
        st.write("DOB: 1936-07-21")
        st.write("Age: 89")
        st.write("Insurance: Kaiser")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### David Miller")
        st.write("DOB: 1961-11-24")
        st.write("Age: 64")
        st.write("Insurance: Humana")
        st.markdown('</div>', unsafe_allow_html=True)