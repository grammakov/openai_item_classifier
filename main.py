import json
import requests
import csv
import time
from requests.exceptions import ConnectionError, ReadTimeout

with open('_key.json', 'r') as file:
    api_key = json.load(file)['api_key']

with open('_messages_py.json', 'r') as file:
    default_messages = json.load(file)

def generate_chat_completion(item, categories, messages, api_key):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {api_key}"
    }

    # Update the user message with the current item and categories
    messages[-1]["content"] = f"Categorize this item: '{item}' into one of these categories: {categories}"

    body = {
        'model': 'gpt-4',
        'messages': messages,
        'temperature': 0.7
    }

    max_retries = 3
    retries = 0

    while retries < max_retries:
        try:
            response = requests.post(url, headers=headers, json=body)
            if response.status_code == 200:
                response_text = response.json()['choices'][0]['message']['content'].strip()
                return response_text
            else:
                raise Exception(f"Error {response.status_code}: {response.text}")
        except (ConnectionError, ReadTimeout) as e:
            retries += 1
            time.sleep(2 ** retries)  # exponential backoff
        except Exception as e:
            raise Exception(f"Failed after {max_retries} attempts: {str(e)}")

# Load items and categories from files
with open('items.txt', 'r') as file:
    items = [line.strip() for line in file.readlines()]

with open('categories.txt', 'r') as file:
    categories = file.read().strip()

# Initialize the CSV file with headers
with open("output.csv", "w", newline='') as file:
    csv_writer = csv.writer(file)
    csv_writer.writerow(["Item", "Category"])

# Process each item
for i, item in enumerate(items):
    print(f"Categorizing item: {i+1} {item}")
    category = generate_chat_completion(item, categories, default_messages.copy(), api_key)

    # Append the result to the CSV file in append mode
    with open("output.csv", "a", newline='') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow([item, category.lower()])

    print(f"Categorized as: {category}")

    # Wait for 1 second before the next request
    time.sleep(1)
