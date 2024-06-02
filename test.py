import json

from llamaapi import LlamaAPI

# Replace 'Your_API_Token' with your actual API token
llama_api_key = "LL-TnlQ4ydSzAsYrKLeoNTWccqQwICK0wcLj8T6hIhuf8N5Cp72lzTnHnAph4475HvK"
llama = LlamaAPI(llama_api_key)
# API Request JSON Cell
api_request_json = {
  "model": "llama3-70b",
  "messages": [
    {"role": "system", "content": "Hola, ¿estás ahi?"},
  ]
}

# Make your request and handle the response
response = llama.run(api_request_json)
print(json.dumps(response.json(), indent=2))
