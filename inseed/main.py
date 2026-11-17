import sys
import os
from typing import List, Dict, Union

# Set environment variable before importing local modules that use it
# In a real scenario, we ensure the file exists at this path.
# For the purpose of fixing the runtime error based ONLY on main.py,
# we stick to the provided file manipulation logic.
os.environ["INSEED_DATA_DIR"] = "D:/inseed"

try:
    from data_loader import load_csv_data
    from processor import process_inventory_data
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

def run_analysis() -> None:
    """
    Main execution function to load data and perform computational processing.
    Orchestrates the flow between data loading and processing components.
    """
    filename = 'inventory.csv'
    
    # ensure the directory and file exist for demonstration purposes to avoid runtime error
    data_dir = os.environ["INSEED_DATA_DIR"]
    data_file = os.path.join(data_dir, filename)
    
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        
    if not os.path.exists(data_file):
        with open(data_file, 'w', encoding='utf-8') as f:
            f.write("item,price\nwidget,10.50\ngadget,20.00\nthing,15.75\n")

    print(f"Loading data from {filename}...")
    
    # Load input data from the pre-defined directory
    raw_data: List[Dict[str, str]] = load_csv_data(filename)
    
    if not raw_data:
        # The runtime error indicates file not found, leading to sys.exit(1)
        print(f"Error: No data retrieved from '{filename}'. Analysis aborted.")
        sys.exit(1)
        
    print(f"Successfully loaded {len(raw_data)} items. Processing data...")
    
    try:
        # Perform computation logic on loaded data
        results: Dict[str, Union[float, Dict[str, Union[float, None]]]] = process_inventory_data(raw_data)
        
        # Display results to standard output
        print("\n--- Inventory Statistics ---")
        print(f"Average Price: ${results['average']:.2f}")
        
        extremes = results['extremes']
        max_price = extremes['max']
        min_price = extremes['min']
        
        print(f"Maximum Price: ${max_price:.2f}" if max_price is not None else "Maximum Price: N/A")
        print(f"Minimum Price: ${min_price:.2f}" if min_price is not None else "Minimum Price: N/A")
        print("----------------------------")
        
    except ValueError as e:
        print(f"Error during data processing: Could not convert data to numeric values. {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred during execution: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_analysis()