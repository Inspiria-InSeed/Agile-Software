import os
import csv
from typing import List, Dict, Union

# Define base path, potentially configurable via environment variable
BASE_DATA_DIR = os.getenv("INSEED_DATA_DIR", "D:/inseed")

def load_csv_data(filename: str) -> List[Dict[str, str]]:
    """
    Loads data from a CSV file located in the D:/inseed directory.

    Args:
        filename: The name of the file to load (e.g., 'data.csv').

    Returns:
        A list of dictionaries, where each dictionary represents a row.
        Returns an empty list if file not found or parsing fails.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        csv.Error: If there is an issue parsing the CSV data.
    """
    file_path = os.path.join(BASE_DATA_DIR, filename)
    data = []

    try:
        with open(file_path, mode='r', encoding='utf-8', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                data.append(row)
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found at {BASE_DATA_DIR}.")
    except csv.Error as e:
        print(f"Error: Failed to parse CSV file '{filename}': {e}")
    except Exception as e:
        print(f"An unexpected error occurred while reading '{filename}': {e}")

    return data

def load_text_content(filename: str) -> str:
    """
    Loads raw text content from a file located in the D:/inseed directory.

    Args:
        filename: The name of the file to load (e.g., 'notes.txt').

    Returns:
        The content of the file as a string. Returns empty string if reading fails.
    """
    file_path = os.path.join(BASE_DATA_DIR, filename)
    content = ""

    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            content = file.read()
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found at {BASE_DATA_DIR}.")
    except Exception as e:
        print(f"An unexpected error occurred while reading '{filename}': {e}")

    return content

if __name__ == "__main__":
    # Example usage for testing purposes
    print("Testing data_loader.py...")
    
    # Note: These rely on files actually existing in D:/inseed
    test_csv_filename = "test_data.csv" 
    # To test, create D:/inseed/test_data.csv with:
    # id,name,value
    # 1,test1,100
    # 2,test2,200

    print(f"\nAttempting to load CSV: {test_csv_filename}")
    csv_rows = load_csv_data(test_csv_filename)
    if csv_rows:
        print(f"Successfully loaded {len(csv_rows)} rows.")
        print(csv_row0 := csv_rows[0])
    
    test_txt_filename = "test_data.txt"
    # To test, create D:/inseed/test_data.txt with some content.
    
    print(f"\nAttempting to load text: {test_txt_filename}")
    text_content = load_text_content(test_txt_filename)
    if text_content:
        print(f"Successfully loaded text content, length: {len(text_content)}")
        print(f"Content snippet: {text_content[:20]}...")