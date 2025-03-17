import requests
import time
from typing import Dict, List

AVG_ACH_TX_AMOUNT = 29523
AVG_CC_TX_AMOUNT = 5999
CC_RATE = 3.2
CONV_FEE = 2.5

# Sample data as a list of dictionaries
data = [
    {"period": "Period 1", "cc_volume": 2749080.24, "ach_volume": 1684104.98, "cc_rate": CC_RATE, "conv_fee": CONV_FEE},
    {"period": "Period 2", "cc_volume": 3901428.61, "ach_volume": 2177763.94, "cc_rate": CC_RATE, "conv_fee": CONV_FEE},
    {"period": "Period 3", "cc_volume": 3463987.88, "ach_volume": 1299510.67, "cc_rate": CC_RATE, "conv_fee": CONV_FEE},
    {"period": "Period 4", "cc_volume": 3197316.97, "ach_volume": 1771351.66, "cc_rate": CC_RATE, "conv_fee": CONV_FEE},
    {"period": "Period 5", "cc_volume": 2312037.28, "ach_volume": 1888621.85, "cc_rate": CC_RATE, "conv_fee": CONV_FEE},
    {"period": "Period 6", "cc_volume": 2311989.04, "ach_volume": 1069675.62, "cc_rate": CC_RATE, "conv_fee": CONV_FEE},
    {"period": "Period 7", "cc_volume": 2116167.22, "ach_volume": 1911317.28, "cc_rate": CC_RATE, "conv_fee": CONV_FEE},
    {"period": "Period 8", "cc_volume": 3732352.29, "ach_volume": 1255786.19, "cc_rate": CC_RATE, "conv_fee": CONV_FEE},
    {"period": "Period 9", "cc_volume": 3202230.02, "ach_volume": 1097577.39, "cc_rate": CC_RATE, "conv_fee": CONV_FEE},
    {"period": "Period 10", "cc_volume": 3416145.16, "ach_volume": 2423328.31, "cc_rate": CC_RATE, "conv_fee": CONV_FEE},
    {"period": "Period 11", "cc_volume": 2041168.99, "ach_volume": 2448448.05, "cc_rate": CC_RATE, "conv_fee": CONV_FEE},
    {"period": "Period 12", "cc_volume": 3939819.7, "ach_volume": 2212596.02, "cc_rate": CC_RATE, "conv_fee": CONV_FEE},
    {"period": "Period 13", "cc_volume": 3664885.28, "ach_volume": 1456920.65, "cc_rate": CC_RATE, "conv_fee": CONV_FEE},
    {"period": "Period 14", "cc_volume": 2424678.22, "ach_volume": 1146508.17, "cc_rate": CC_RATE, "conv_fee": CONV_FEE},
    {"period": "Period 15", "cc_volume": 2363649.93, "ach_volume": 2026349.54, "cc_rate": CC_RATE, "conv_fee": CONV_FEE},
    {"period": "Period 16", "cc_volume": 2366809.02, "ach_volume": 1660228.74, "cc_rate": CC_RATE, "conv_fee": CONV_FEE},
    {"period": "Period 17", "cc_volume": 2608484.49, "ach_volume": 1183057.35, "cc_rate": CC_RATE, "conv_fee": CONV_FEE},
    {"period": "Period 18", "cc_volume": 3049512.86, "ach_volume": 1742765.37, "cc_rate": CC_RATE, "conv_fee": CONV_FEE},
    {"period": "Period 19", "cc_volume": 2863890.04, "ach_volume": 1051582.78, "cc_rate": CC_RATE, "conv_fee": CONV_FEE},
    {"period": "Period 20", "cc_volume": 2582458.28, "ach_volume": 2363980.6, "cc_rate": CC_RATE, "conv_fee": CONV_FEE},
    {"period": "Period 21", "cc_volume": 3223705.79, "ach_volume": 1388169.97, "cc_rate": CC_RATE, "conv_fee": CONV_FEE},
    {"period": "Period 22", "cc_volume": 2278987.72, "ach_volume": 1993783.43, "cc_rate": CC_RATE, "conv_fee": CONV_FEE},
    {"period": "Period 23", "cc_volume": 2584289.3, "ach_volume": 1467566.61, "cc_rate": CC_RATE, "conv_fee": CONV_FEE},
    {"period": "Period 24", "cc_volume": 2732723.69, "ach_volume": 1780102.03, "cc_rate": CC_RATE, "conv_fee": CONV_FEE}
]

# Sample data as a list of dictionaries
# test_negative_data = [
#     {"period": "Period 1", "cc_volume": 27490.24, "ach_volume": 168410.98, "cc_rate": CC_RATE, "conv_fee": CONV_FEE},
#     {"period": "Period 2", "cc_volume": 39014.61, "ach_volume": 217776.94, "cc_rate": CC_RATE, "conv_fee": CONV_FEE},
#     {"period": "Period 3", "cc_volume": 34639.88, "ach_volume": 129951.67, "cc_rate": CC_RATE, "conv_fee": CONV_FEE},
#     {"period": "Period 4", "cc_volume": 31973.97, "ach_volume": 177135.66, "cc_rate": CC_RATE, "conv_fee": CONV_FEE},
#     {"period": "Period 5", "cc_volume": 23120.28, "ach_volume": 188862.85, "cc_rate": CC_RATE, "conv_fee": CONV_FEE},
#     {"period": "Period 6", "cc_volume": 23119.04, "ach_volume": 106967.62, "cc_rate": CC_RATE, "conv_fee": CONV_FEE},
#     {"period": "Period 7", "cc_volume": 21161.22, "ach_volume": 191131.28, "cc_rate": CC_RATE, "conv_fee": CONV_FEE},
#     {"period": "Period 8", "cc_volume": 37323.29, "ach_volume": 125578.19, "cc_rate": CC_RATE, "conv_fee": CONV_FEE},
#     {"period": "Period 9", "cc_volume": 32022.02, "ach_volume": 109757.39, "cc_rate": CC_RATE, "conv_fee": CONV_FEE},
#     {"period": "Period 10", "cc_volume": 34161.16, "ach_volume": 242332.31, "cc_rate": CC_RATE, "conv_fee": CONV_FEE},
#     {"period": "Period 11", "cc_volume": 20411.99, "ach_volume": 244844.05, "cc_rate": CC_RATE, "conv_fee": CONV_FEE},
#     {"period": "Period 12", "cc_volume": 39398.7, "ach_volume": 221259.02, "cc_rate": CC_RATE, "conv_fee": CONV_FEE},
#     {"period": "Period 13", "cc_volume": 36648.28, "ach_volume": 145692.65, "cc_rate": CC_RATE, "conv_fee": CONV_FEE},
#     {"period": "Period 14", "cc_volume": 24246.22, "ach_volume": 114650.17, "cc_rate": CC_RATE, "conv_fee": CONV_FEE},
#     {"period": "Period 15", "cc_volume": 23636.93, "ach_volume": 202634.54, "cc_rate": CC_RATE, "conv_fee": CONV_FEE},
#     {"period": "Period 16", "cc_volume": 23668.02, "ach_volume": 166022.74, "cc_rate": CC_RATE, "conv_fee": CONV_FEE},
#     {"period": "Period 17", "cc_volume": 26084.49, "ach_volume": 118305.35, "cc_rate": CC_RATE, "conv_fee": CONV_FEE},
#     {"period": "Period 18", "cc_volume": 30495.86, "ach_volume": 174276.37, "cc_rate": CC_RATE, "conv_fee": CONV_FEE},
#     {"period": "Period 19", "cc_volume": 28638.04, "ach_volume": 105158.78, "cc_rate": CC_RATE, "conv_fee": CONV_FEE},
#     {"period": "Period 20", "cc_volume": 25824.28, "ach_volume": 236398.6, "cc_rate": CC_RATE, "conv_fee": CONV_FEE},
#     {"period": "Period 21", "cc_volume": 32237.79, "ach_volume": 138816.97, "cc_rate": CC_RATE, "conv_fee": CONV_FEE},
#     {"period": "Period 22", "cc_volume": 22789.72, "ach_volume": 199378.43, "cc_rate": CC_RATE, "conv_fee": CONV_FEE},
#     {"period": "Period 23", "cc_volume": 25842.3, "ach_volume": 146756.61, "cc_rate": CC_RATE, "conv_fee": CONV_FEE},
#     {"period": "Period 24", "cc_volume": 27327.69, "ach_volume": 178010.03, "cc_rate": CC_RATE, "conv_fee": CONV_FEE}
# ]
# data = test_negative_data

def wait_for_backend(url: str, max_retries: int = 30, delay: int = 2) -> bool:
    """Wait for backend to become available"""
    print("Waiting for backend to become available...")
    for i in range(max_retries):
        try:
            response = requests.get(f"{url}/health")
            if response.status_code == 200:
                print("Backend is ready!")
                return True
        except requests.exceptions.RequestException:
            print(f"Backend not ready, attempt {i + 1}/{max_retries}")
            time.sleep(delay)
    return False

def delete_all_periods(base_url: str) -> bool:
    """Delete all existing periods from the API"""
    try:
        response = requests.delete(f"{base_url}/periods")
        if response.status_code == 200:
            print("Successfully deleted all existing periods")
            return True
        else:
            print(f"Failed to delete periods: {response.text}")
            return False
    except Exception as e:
        print(f"Error deleting periods: {str(e)}")
        return False

def load_data(base_url: str = "http://backend:8000") -> None:
    """Load sample transaction data into the ROI tracking API"""
    if not wait_for_backend(base_url):
        print("Backend failed to become available")
        return

    # Delete existing periods first
    print("\nDeleting existing periods...")
    if not delete_all_periods(base_url):
        print("Failed to delete existing periods. Proceeding with data load anyway...")

    api_url = f"{base_url}/period"
    success_count = 0
    error_count = 0

    print("\nStarting to load transaction data...")
    
    for period in data:
        period["ach_count"] = int(period.get("ach_volume") / AVG_ACH_TX_AMOUNT)
        period["cc_count"] = int(period.get("cc_volume") / AVG_CC_TX_AMOUNT)
        try:
            response = requests.post(api_url, json=period)
            if response.status_code == 200:
                print(f"Successfully loaded period {period['period']}")
                success_count += 1
            else:
                print(f"Failed to load period {period['period']}: {response.text}")
                error_count += 1
        except Exception as e:
            print(f"Error loading period {period['period']}: {str(e)}")
            error_count += 1
    
    print(f"\nData loading complete:")
    print(f"Successfully loaded: {success_count} periods")
    print(f"Failed to load: {error_count} periods")

if __name__ == "__main__":
    load_data() 