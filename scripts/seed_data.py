import os
import json

DENIAL_CODES = [
    {"code": "CO-4", "category": "coding_error", "description": "Procedure code inconsistent with modifier or bill type."},
    {"code": "CO-16", "category": "documentation", "description": "Claim lacks information needed for adjudication."},
    {"code": "CO-29", "category": "timely_filing", "description": "Time limit for filing has expired."},
    {"code": "CO-50", "category": "medical_necessity", "description": "Not deemed a medical necessity by payer."},
    {"code": "CO-96", "category": "non_covered", "description": "Non-covered charge(s)."},
    {"code": "CO-97", "category": "coding_error", "description": "Payment adjusted - already adjudicated as part of another service."},
    {"code": "CO-151", "category": "auth_missing", "description": "Prior auth not obtained."},
    {"code": "CO-197", "category": "auth_missing", "description": "Precertification/auth/notification absent."},
    {"code": "PR-1", "category": "deductible", "description": "Deductible amount."},
    {"code": "CO-18", "category": "duplicate", "description": "Exact duplicate claim."}
]

def generate_denial_codes_json():
    data_dir = os.path.join(os.path.dirname(__file__), "..", "backend", "data")
    os.makedirs(data_dir, exist_ok=True)
    file_path = os.path.join(data_dir, "denial_codes.json")
    
    with open(file_path, "w") as f:
        json.dump(DENIAL_CODES, f, indent=4)
        
    print(f"Generated {file_path}")

if __name__ == "__main__":
    generate_denial_codes_json()
