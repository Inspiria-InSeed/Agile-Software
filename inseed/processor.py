import math
from typing import List, Dict, Union

def calculate_average_price(prices: List[float]) -> float:
    """
    Calculates the arithmetic mean of a list of prices.

    Args:
        prices: A list of float values representing prices.

    Returns:
        The average price as a float. Returns 0.0 if the input list is empty.
    """
    if not prices:
        return 0.0
    return sum(prices) / len(prices)

def find_price_extremes(prices: List[float]) -> Dict[str, Union[float, None]]:
    """
    Finds the maximum and minimum prices in a list.

    Args:
        prices: A list of float values representing prices.

    Returns:
        A dictionary containing 'max' and 'min' prices.
        Values are None if the list is empty.
    """
    if not prices:
        return {"max": None, "min": None}
    return {"max": max(prices), "min": min(prices)}

def process_inventory_data(data: List[Dict[str, Union[str, float, int]]]) -> Dict[str, Union[float, Dict[str, Union[float, None]]]]:
    """
    Performs computational logic on raw inventory data.

    Processes the data to extract prices, calculate the average price,
    and identify maximum and minimum prices.

    Args:
        data: A list of dictionaries, where each dictionary represents an item
              and must contain a 'price' key with a numeric value.

    Returns:
        A dictionary containing:
        - 'average': The average price (float).
        - 'extremes': A dictionary with 'max' and 'min' prices (float or None).
    """
    # Extract prices, ensuring we can handle data that might lack 'price' key robustly
    prices: List[float] = [float(item['price']) for item in data if 'price' in item]
    
    avg_price: float = calculate_average_price(prices)
    extremes: Dict[str, Union[float, None]] = find_price_extremes(prices)
    
    return {
        "average": avg_price,
        "extremes": extremes
    }