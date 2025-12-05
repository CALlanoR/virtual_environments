import yaml
from collections import defaultdict

def get_endpoints_swagger_yaml(swagger_yaml_file):
    """
    Reads a Swagger (OpenAPI) file in YAML format and lists the endpoints ordered by path.
    Args:
        swagger_yaml_file (str): local path to the swagger.yaml file.
    Returns:
        None: It prints a list of endpoints with their HTTP methods, ordered by path.
    """

    try:
        if swagger_yaml_file:
            with open(swagger_yaml_file, 'r') as file:
                swagger_data = yaml.safe_load(file)
        else:
            raise ValueError("You must enter the swagger path.")

        # Create a list to store endpoints with their methods
        endpoints = []

        if 'paths' in swagger_data:
            for path, path_data in swagger_data['paths'].items():
                for method in ['get', 'post', 'put', 'delete']:
                    if method in path_data:
                        endpoints.append((path, method.upper()))

        # Sort endpoints by path
        endpoints.sort(key=lambda x: x[0])

        # Print the results
        print("\nEndpoints ordered by path:")
        print("==========================")
        for path, method in endpoints:
            print(f"{method:6}, {path}")

        # Print summary
        method_counts = defaultdict(int)
        for _, method in endpoints:
            method_counts[method] += 1

        print("\n============== Summary ==============")
        print(f"GET:    {method_counts['GET']}")
        print(f"POST:   {method_counts['POST']}")
        print(f"PUT:    {method_counts['PUT']}")
        print(f"DELETE: {method_counts['DELETE']}")
        print(f"\nTotal endpoints: {len(endpoints)}")

    except FileNotFoundError:
        print(f"Error: Swagger file '{swagger_yaml_file}' was not found.")
        return None
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

# Example usage
swagger_yaml_file = "/home/callanor/Documents/sourcemeridian/repositories/report-builder/healthnexus-api-internal-report-builder/deploy/api-doc-template.yaml"
get_endpoints_swagger_yaml(swagger_yaml_file=swagger_yaml_file)
