from mcp import ClientSession, types
from mcp.client.streamable_http import streamablehttp_client
import json
import asyncio

from typing import Optional, List
from pydantic import AnyUrl

# Create server parameters for stdio connection
# server_params = StdioServerParameters(
#     command="python",  # Executable
#     args=["server.py"],  # Server script
# )


class TextResourceContents:
    def __init__(self, uri: AnyUrl, mimeType: str, text: str):
        self.uri = uri
        self.mimeType = mimeType
        self.text = text

class ResponseObject:
    def __init__(self, meta: Optional[None], contents: List[TextResourceContents]):
        self.meta = meta
        self.contents = contents


async def run():
    # Connect to the server using the Streamable HTTP transport.
    # When running in Docker, we use the service name 'server' as the host.
    async with streamablehttp_client("http://server:8000/mcp") as (read, write, _):
        async with ClientSession(
            read, write, sampling_callback=None
        ) as session:
            await session.initialize()

            # A resource MUST be accessed via read_resource.
            print("--- Reading resource conceptgroups://13161 ---")
            try:
                # The result of read_resource is a ReadResourceResult object.
                result_obj = await session.read_resource("conceptgroups://13161")

                if result_obj.contents:
                    text_resource = result_obj.contents[0]
                    json_string = text_resource.text
                    data_as_list_of_dicts = json.loads(json_string)
                    print("Successfully converted to Python list of dictionaries:")
                    print(data_as_list_of_dicts)

            except Exception as e:
                print(f"Error reading resource: {e}")
                import traceback
                traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(run())