from google import genai
import json
import re

class Healer:
    """
    Component responsible for self-healing tests using Google's Gemini API (google-genai).
    """
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash"):
        """
        Initialize the Gemini client.
        """
        if not api_key:
            raise ValueError("API Key is required for Gemini Healer")
        
        self.model_name = model_name
        # The new SDK uses genai.Client
        self.client = genai.Client(api_key=api_key)

    def heal(self, page_source: str, failed_selector: dict) -> dict:
        """
        Sends context to LLM and returns new selector parameters.
        Returns: {'by': ..., 'value': ...} or None
        """
        prompt = f"""
        You are an Appium test automation expert. A test failed to find an element.
        
        FAILED SELECTOR: 
        {json.dumps(failed_selector)}

        PAGE SOURCE (XML):
        {page_source[:30000]}  # Truncate to avoid token limits if necessary

        TASK:
        The UI might have changed (e.g., dynamic IDs, text changes). 
        Analyze the XML and find the element that most likely corresponds to the failed selector.
        
        RESPONSE FORMAT:
        Return ONLY a raw JSON object (no markdown formatting, no explanations) with the new strategy and value:
        {{
            "by": "xpath" or "id" or "accessibility_id" or "android_uiautomator",
            "value": "the_new_locator_string"
        }}
        """

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            
            # Clean response text (remove markdown code blocks if present)
            raw_text = response.text
            clean_text = re.sub(r'```json\n|```', '', raw_text).strip()
            
            new_selector = json.loads(clean_text)
            
            # Validate structure
            if 'by' in new_selector and 'value' in new_selector:
                return new_selector
            return None
            
        except Exception as e:
            print(f"Healer failed: {e}")
            return None

