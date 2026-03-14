import os
import requests
from pathlib import Path

# URLs to some mock sample policies. In a real scenario, these would be downloaded via CMS API
# For demonstration, we'll download a couple public PDFs or just create dummy text files pretending to be PDFs
MOCK_POLICIES = {
    "LCD_L35041.pdf": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
    "NCD_220_2.pdf": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
}

def download_policies():
    policies_dir = Path("backend/data/policies")
    policies_dir.mkdir(parents=True, exist_ok=True)
    
    for filename, url in MOCK_POLICIES.items():
        filepath = policies_dir / filename
        if not filepath.exists():
            print(f"Downloading {filename}...")
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                with open(filepath, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
            else:
                print(f"Failed to download {url}")
        else:
            print(f"{filename} already exists.")
            
if __name__ == "__main__":
    download_policies()
