import requests
import os

# AWS Bedrock Configuration
LLM_API_URL = os.getenv("BEDROCK_BASE_URL")

#CallLLM Class for getting responses from LLMs using API
class CallLLM:
    def __init__(
        self,
        DEFAULT_MODEL="apac.anthropic.claude-sonnet-4-20250514-v1:0",
        base_url=LLM_API_URL,
        user_token=None
    ):
        self.base_url = base_url
        self.llm_model = DEFAULT_MODEL
        self.user_token = user_token

    def call_llm(self, body, headers=None, user_token=None):
        """
        Call LLM API
        
        Args:
            body: Request body containing messages, engine/model, and other parameters
            headers: Request headers (optional)
            user_token: User token for authorization (optional, uses the token set during initialization if not provided)
        
        Returns:
            Response content from the LLM
        """
        try:
            # Extract model from body (check both 'engine' and 'model' keys)
            model = body.get('engine') or body.get('model', self.llm_model)
            
            # Extract messages from body
            messages = body.get('messages', [])
            
            # Convert messages to Bedrock format if needed
            bedrock_messages = []
            system_message = None
            
            for msg in messages:
                # Handle system messages separately (Bedrock doesn't support system role in messages)
                if msg.get("role") == "system":
                    if isinstance(msg.get("content"), str):
                        system_message = msg["content"]
                    elif isinstance(msg.get("content"), list):
                        system_message = msg["content"][0].get("text", "")
                    continue
                
                # Only process user and assistant messages
                if msg.get("role") not in ["user", "assistant"]:
                    continue
                    
                if isinstance(msg.get("content"), str):
                    # Convert string content to Bedrock format
                    bedrock_msg = {
                        "role": msg["role"],
                        "content": [{"text": msg["content"]}]
                    }
                else:
                    # Assume it's already in correct format or handle list format
                    if isinstance(msg.get("content"), list):
                        bedrock_msg = msg
                    else:
                        bedrock_msg = {
                            "role": msg["role"],
                            "content": [{"text": str(msg.get("content", ""))}]
                        }
                bedrock_messages.append(bedrock_msg)
            
            # Build the API URL
            api_url = f"{self.base_url}/model/{model}/converse"
            
            # Prepare headers
            token = user_token or self.user_token
            request_headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }
            
            # Prepare the request body for Bedrock
            bedrock_body = {
                "messages": bedrock_messages
            }
            
            # Add system message if present (as system parameter in Bedrock)
            if system_message:
                bedrock_body["system"] = [{"text": system_message}]
            
            # Add temperature if present in original body
            if 'temperature' in body:
                bedrock_body['inferenceConfig'] = {
                    'temperature': body['temperature']
                }
            
            response = requests.post(
                url=api_url,
                headers=request_headers,
                json=bedrock_body,
                verify=False,
            )

            if response.status_code == 200:
                try:
                    res = response.json()
                    # Extract content from Bedrock response format
                    return res["output"]["message"]["content"][0]["text"]
                        
                except Exception as e:
                    return f"Error parsing response: {str(e)}"
            else:
                raise Exception(f"API call failed with status {response.status_code}: {response.text}")
                
        except Exception as e:
            return f"Error calling Bedrock API: {str(e)}"

    def call_bedrock_direct(self, messages, model=None, headers=None, user_token=None):
        """
        Direct method for calling Bedrock with pre-formatted messages
        
        Args:
            messages: List of message objects already in Bedrock format
            model: Model ID to use (optional, uses default if not provided)
            headers: Additional headers (optional)
        
        Returns:
            Response content from the LLM
        """
        if model is None:
            model = self.llm_model
            
        # Build the API URL
        api_url = f"{self.base_url}/model/{model}/converse"
        
        # Prepare headers
        token = user_token or self.user_token
        request_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
        # Add any additional headers
        if headers:
            request_headers.update(headers)
        
        # Prepare the request body
        body = {
            "messages": messages
        }
        
        try:
            response = requests.post(
                url=api_url,
                headers=request_headers,
                json=body,
                verify=False,
            )

            if response.status_code == 200:
                try:
                    res = response.json()
                    # Extract content from Bedrock response format
                    return res["output"]["message"]["content"][0]["text"]
                        
                except Exception as e:
                    return f"Error parsing response: {str(e)}"
            else:
                raise Exception(f"API call failed with status {response.status_code}: {response.text}")
                
        except Exception as e:
            return f"Error calling Bedrock API: {str(e)}"


