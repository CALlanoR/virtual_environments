import yaml
import csv
from collections import defaultdict

def get_endpoints_swagger_yaml(swagger_yaml_file):
    """
    Reads a Swagger (OpenAPI) file in YAML format and lists the endpoints.
    Args:
        swagger_yaml_file (str): local path to the swagger.yaml file.
    Returns:
        None: It prints a list of endpoints extracted from the Swagger file grouped by controller.
    """

    try:
        if swagger_yaml_file:
            with open(swagger_yaml_file, 'r') as file:
                swagger_data = yaml.safe_load(file)
        else:
            raise ValueError("You must enter the swagger path.")

        total_count = 0
        count_for_controller = 0
        get_count = 0
        post_count = 0
        put_count = 0
        delete_count = 0

        endpoints_by_controller_and_method = defaultdict(lambda: defaultdict(list))
        if 'paths' in swagger_data:
            for path, path_data in swagger_data['paths'].items():
                for method in ['get', 'post', 'put', 'delete']:
                    if method in path_data:
                        operation = path_data[method]
                        if 'tags' in operation:
                            tags = operation['tags']
                            for tag in tags:
                                endpoints_by_controller_and_method[tag][method].append(path)
                        else:
                            endpoints_by_controller_and_method['Uncategorized'][method].append(path) 

        with open('output.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["method","endpoint"])
            # print the results, sorted by controller and then by method
            for controller in sorted(endpoints_by_controller_and_method.keys()):
                print(f"Controller: {controller}")
                for method in sorted(endpoints_by_controller_and_method[controller].keys()):
                    print(f"  {method.upper()}:")
                    for endpoint in endpoints_by_controller_and_method[controller][method]:
                        total_count+=1
                        count_for_controller+=1
                        print(f"    - {count_for_controller}. {endpoint}")
                        writer.writerow([method.upper(), endpoint])
                        if method == 'get':
                            get_count += 1
                        if method == 'post':
                            post_count += 1
                        if method == 'put':
                            put_count += 1
                        if method == 'delete':
                            delete_count += 1
                count_for_controller = 0
                print()

        print("============== Summary ==============")
        print(f"GET: {get_count}")
        print(f"POST: {post_count}")
        print(f"PUT: {put_count}")
        print(f"DELETE: {delete_count}\n")
        print(f"Total endpoints: {total_count}")

    except FileNotFoundError:
        print(f"Error: Swagger file '{swagger_yaml_file}' was not found.")
        return None
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

# swagger_yaml_file = "/home/callanor/Documents/sourcemeridian/repositories/codegroups/purplelab-api-codegroups/deploy/api-doc-template.yaml"
swagger_yaml_file = "/home/callanor/Documents/sourcemeridian/repositories/patientgroups/healthnexus-api-patientgroups/deploy/api-doc-template.yaml"
get_endpoints_swagger_yaml(swagger_yaml_file=swagger_yaml_file)
