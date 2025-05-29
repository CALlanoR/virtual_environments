import json

def extract_postman_info(postman_collection_file):
    """
    Reads a Postman collection JSON file and prints the endpoint and parameters
    used for each request.

    Args:
        postman_collection_file (str): Path to the Postman collection JSON file.
    """

    try:
        with open(postman_collection_file, 'r') as f:
            collection_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {postman_collection_file}")
        return
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return

    if 'item' not in collection_data:
        print("Error: 'item' key not found in Postman collection. Invalid format?")
        return

    def process_item(item, indent=0):  # Add indent for nested structures
        if 'request' in item:
            request = item['request']
            method = request.get('method', 'N/A')
            # print(request)
            url = request.get('url', {})
            endpoint_raw = url.get('raw', 'N/A')  # Use raw to get the unparsed URL
            endpoint = endpoint_raw.replace("{{url}}", "").lstrip('/')
            endpoint = endpoint.replace("localhost:8083", "").lstrip('/')

            print("  " * indent + f"{method} {endpoint}")

            # Print Query Parameters
            if 'query' in url:
                print("  " * indent + "  Query Parameters:")
                for param in url['query']:
                     if "value" in param and "key" in param:
                        print("  " * indent + f"    {param['key']}: {param['value']}")

            # Print Request Body Parameters
            if 'body' in request and 'mode' in request['body']:
                if request['body']['mode'] == 'raw' and request['body']['raw'] != 'null':
                    if request['body'].get('raw'):
                        print("  " * indent + f"    {request['body']['raw']}") #Print the full body.
            print()

        # Handle nested items (folders) recursively
        elif 'item' in item:
            print("  " * indent + f"Folder: {item.get('name', 'Unnamed Folder')}")
            for sub_item in item['item']:
                process_item(sub_item, indent + 1)  # Increase indent for the next level of nesting

    # Iterate through the root items
    for item in collection_data['item']:
        process_item(item)

# Example Usage:
if __name__ == "__main__":
    postman_collection_file = '/home/callanor/Downloads/healthnexus_postman_collection_v3.json'  # Replace with your file
    extract_postman_info(postman_collection_file)