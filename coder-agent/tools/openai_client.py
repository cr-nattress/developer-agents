import os
import logging
import json
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("OpenAI package not found. Please install it with: pip install openai")

class OpenAIClient:
    """
    Client for interacting with the OpenAI API.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the OpenAI client.
        
        Args:
            api_key (Optional[str]): OpenAI API key. If not provided, will try to get from environment.
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI package is not installed. Please install it with: pip install openai")
            
        self.api_key = api_key or os.environ.get('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key not provided and not found in environment variables")
            
        self.client = openai.OpenAI(api_key=self.api_key)
        logger.info("OpenAI client initialized")
    
    def generate_code_changes(self, code_bundle: str, prompt: str, model: str = "gpt-4") -> str:
        """
        Generate code changes based on the provided code bundle and prompt.
        
        Args:
            code_bundle (str): Bundle of code files
            prompt (str): User prompt for code changes
            model (str): OpenAI model to use
            
        Returns:
            str: Generated code changes
        """
        system_prompt = "You are a code editor assistant. You receive source code and instructions for code improvements."
        
        user_message = f"""I need you to modify the following code according to these instructions: {prompt}

Here is the code:

{code_bundle}

Please respond with the modified code for each file. Format your response as follows:

=== FILE: path/to/file.py ===
(modified code for that file)

Only include files that you've modified. Do not include any explanations or comments outside of the code blocks."""
        
        try:
            logger.info(f"Sending request to OpenAI API using model {model}")
            
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.2,  # Lower temperature for more deterministic output
                max_tokens=4096,  # Adjust based on your needs
            )
            
            # Extract the response content
            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content
            else:
                logger.error("No response received from OpenAI API")
                return ""
                
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            raise
