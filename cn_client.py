from typing import Any
import asyncio
import json
import os
import pdb

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from langgraph.prebuilt import create_react_agent

from azure.identity import DefaultAzureCredential

# Get Azure token
default_credential = DefaultAzureCredential()
access_token = default_credential.get_token("https://cognitiveservices.azure.com/.default")

# Set API key from the access token
os.environ['OPENAI_API_KEY'] = access_token.token
os.environ['AZURE_OPENAI_ENDPOINT'] = "https://api.uhg.com/api/cloud/api-management/ai-gateway/1.0"

# Initialize model with Azure-specific parameters
model = AzureChatOpenAI(
    azure_deployment="gpt-4o_2024-05-13",  # The deployment name in Azure
    api_version="2025-01-01-preview",  # Azure API version
    default_headers={
        "projectId": "f440d3f1-df7a-45fb-a62f-5953aaf6bd55",
        "x-idp": "azuread"
    }
)

async def main(query: str):
    """Main function to process queries using the MCP client."""
    client = MultiServerMCPClient({
        "mcpstore": {
            "url": "http://127.0.0.1:8001/mcp",  # Replace with the remote server's URL
            "transport": "streamable_http"
        }
    })
    tools = await client.get_tools()
    pdb.set_trace()
    agent = create_react_agent(model, tools)
    response = await agent.ainvoke({"messages": query})
    return response


def serialize_response(obj: Any) -> Any:
    """Helper function to make the response JSON serializable."""
    if hasattr(obj, 'to_json'):
        return obj.to_json()
    if hasattr(obj, '__dict__'):
        return obj.__dict__
    return str(obj)


def print_tool_calls(response):
    """Print tool calls from the response object."""
    for message in response["messages"]:
        if hasattr(message, "additional_kwargs") and message.additional_kwargs.get("tool_calls"):
            tool_calls = message.tool_calls
            print("\n------------Tool Calls------------")
            for tool_call in tool_calls:
                print(f"Tool Name: {tool_call['name']}")
                print(f"Tool ID: {tool_call['id']}")
                print("Arguments:", json.dumps(tool_call['args'], indent=2))
                print("------------------------")


def print_ai_messages(response):
    """Print all non-empty AI messages from the response."""
    for message in response["messages"]:
        if type(message).__name__ == "AIMessage" and message.content:
            print("\n------------AI Message------------")
            print(f"Content: {message.content}")
            print("--------------------------------")

def process_and_print_response(response):
        """Process and print the response from the agent."""
        #json_response = json.dumps(response, default=serialize_response, indent=2)
        #print("\n------------Json Response------------")
        #print(json_response)
        print_tool_calls(response)   
        print_ai_messages(response)


if __name__ == "__main__":
    patient = "{\"first_name\":\"Patricia\",\"last_name\":\"Smith\", \"dob\":\"2002-12-12\"}"
    response = asyncio.run(main(f'Get demographics for {patient}'))
    print("\n------------Get the patient details------------")
    print(response)
    process_and_print_response(response)

    