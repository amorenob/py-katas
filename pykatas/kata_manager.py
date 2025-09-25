"""
Kata management functionality
"""

import yaml
from pathlib import Path
from .models import Kata


def load_katas():
    """Load katas from YAML files in the katas directory"""
    katas = []
    katas_dir = Path("katas")

    if not katas_dir.exists():
        return katas

    for kata_file in katas_dir.glob("*.yaml"):
        try:
            with open(kata_file, 'r') as f:
                kata_data = yaml.safe_load(f)

            # Validate required fields
            required_fields = ['id', 'title', 'description', 'starter_code']
            if all(field in kata_data for field in required_fields):
                kata = Kata(
                    id=kata_data['id'],
                    title=kata_data['title'],
                    description=kata_data['description'],
                    starter_code=kata_data['starter_code']
                )
                katas.append(kata)
            else:
                print(f"Missing required fields in {kata_file}")

        except Exception as e:
            print(f"Error loading kata {kata_file}: {e}")

    return katas


# Load available katas
KATAS = load_katas()