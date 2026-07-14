import os
import requests


API_BASE_URL = os.getenv("MIRA_API_BASE_URL", "http://localhost:8000")


def ask_mira(question: str) -> dict:
    response = requests.post(
        f"{API_BASE_URL}/ask",
        json={"question": question},
        timeout=180,
    )
    response.raise_for_status()
    return response.json()


def get_history(limit: int = 25) -> list:
    response = requests.get(
        f"{API_BASE_URL}/history",
        params={"limit": limit},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def get_history_item(item_id: int) -> dict:
    response = requests.get(
        f"{API_BASE_URL}/history/{item_id}",
        timeout=30,
    )
    response.raise_for_status()
    return response.json()