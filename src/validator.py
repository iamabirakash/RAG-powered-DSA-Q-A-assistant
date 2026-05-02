import ast
import re
import logging

logger = logging.getLogger(__name__)

class ResponseValidator:
    """Validates and formats the response from the LLM."""
    
    @staticmethod
    def extract_code_blocks(text):
        """Extracts code blocks from markdown text."""
        # Regex to find ```language ... ```
        pattern = r"```(?P<language>\w+)?\n(?P<code>.*?)```"
        matches = re.finditer(pattern, text, re.DOTALL)
        
        blocks = []
        for match in matches:
            blocks.append({
                "language": match.group("language") or "unknown",
                "code": match.group("code").strip()
            })
        return blocks

    @staticmethod
    def validate_python_syntax(code):
        """Validates if the provided Python code has correct syntax."""
        try:
            ast.parse(code)
            return True, "Valid Python syntax"
        except SyntaxError as e:
            return False, f"Syntax Error: {e}"
        except Exception as e:
            return False, f"Validation Error: {e}"

    def validate_response(self, response_text):
        """
        Validates the text response for code syntax if Python is detected.
        Returns a dict with validation status.
        """
        code_blocks = self.extract_code_blocks(response_text)
        validation_results = []
        
        for idx, block in enumerate(code_blocks):
            if block["language"].lower() == "python":
                is_valid, msg = self.validate_python_syntax(block["code"])
                validation_results.append({
                    "block_index": idx,
                    "language": "python",
                    "is_valid": is_valid,
                    "message": msg
                })
                
        return {
            "has_code": len(code_blocks) > 0,
            "blocks": code_blocks,
            "validation_results": validation_results
        }
