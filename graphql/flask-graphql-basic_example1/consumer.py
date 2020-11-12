import requests
import json

def run_query(query):
    request = requests.post('http://127.0.0.1:5000/graphql', json={'query': query}, headers={'Content-type': 'application/json'})
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))

        
# The GraphQL query (with a few aditional bits included) itself defined as a multi-line string.       
query = """
{
  allPosts{
    edges{
      node{
        title
        body
        author{
          username
        }
      }
    }
  }
}
"""

result = run_query(query)
print(result)
remaining_rate_limit = result["data"]["allPosts"]["edges"][0]["node"]["title"] # Drill down the dictionary
print("Remaining rate limit - {}".format(remaining_rate_limit))