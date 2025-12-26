import httpx
from typing import Set, List
from functools import lru_cache

CAT_API_URL = "https://api.thecatapi.com/v1/breeds"


@lru_cache(maxsize=1)
def get_valid_breeds() -> Set[str]:
    """
    Fetch valid cat breeds from the Cat API and cache the result.
    Returns a set of breed names.
    """
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(CAT_API_URL)
            response.raise_for_status()
            breeds_data = response.json()
            # Extract breed names from the API response
            breed_names = {breed.get("name", "").strip() for breed in breeds_data if breed.get("name")}
            return breed_names
    except httpx.RequestError as e:
        # If API is unavailable, log error but don't fail
        # In production, you might want to handle this differently
        print(f"Warning: Could not fetch breeds from Cat API: {e}")
        return set()
    except httpx.HTTPStatusError as e:
        print(f"Warning: Cat API returned error: {e}")
        return set()


def validate_breed(breed: str) -> bool:
    """
    Validate if a breed exists in the Cat API.
    
    Args:
        breed: The breed name to validate
        
    Returns:
        True if breed is valid, False otherwise
    """
    valid_breeds = get_valid_breeds()
    return breed.strip() in valid_breeds


def get_breed_names() -> List[str]:
    """
    Get a list of all valid breed names.
    Useful for error messages or API responses.
    """
    return sorted(list(get_valid_breeds()))

