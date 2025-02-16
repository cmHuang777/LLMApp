from fastapi import HTTPException
from openai import OpenAI
from typing import List, Dict, Any
from app.config import settings
from app.models import AuditLog
import re

# Configure the OpenAI client
openai = OpenAI(
    api_key=settings.OPENAI_API_KEY
)

async def get_llm_response(context_messages: List[Dict[str, Any]], convo_id: str) -> str:
    """
    Calls the LLM with the given conversation context.
    The `context_messages` is a list of dictionaries, each with
    { "role": "user" or "assistant", "content": "text" } as needed by OpenAI.
    """
    # Call the OpenAI API
    try:
        response = openai.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[{"role": msg["role"], "content": msg["content"]} for msg in context_messages]
        )
        print("DEBUG:", response)
        llm_reply = response.choices[0].message.content
    except Exception as e:
        print(e)
        raise HTTPException(status_code=502, detail="LLM service error.")
    
    prompt_text = "\n".join([f'{m["role"]}: {m["content"]}' for m in context_messages if m["role"] == "user"])

    # For auditing, store an "anonymized" version. 
    # Mask PII in both the user prompts and the LLM response.
    masked_prompt_text = mask_sensitive_info(prompt_text)
    masked_llm_reply = mask_sensitive_info(llm_reply)

    await AuditLog(
        conversation_id=convo_id,
        prompt=masked_prompt_text[-2000:],  # store up to 2k chars to avoid long fields
        response=masked_llm_reply[:2000]
    ).insert()

    return llm_reply


def mask_sensitive_info(text: str) -> str:
    """
    Masks sensitive information (PII) in the input text.
    
    This function targets common Singapore-specific PII:
      - **NRIC/FIN Numbers:** Formats like S1234567D, T1234567A, etc.
      - **Phone Numbers:** Singapore phone numbers (optionally prefixed with +65).
      - **Email Addresses:** Standard email formats.
      - **Postal Codes:** Singapore postal codes are exactly 6 digits.
      - **Addresses:** A naive approach to mask typical Singapore addresses,
        e.g., block addresses ("Blk 123 Ang Mo Kio Ave 3") or street addresses ("123 Orchard Road").
    
    Note:
      - The address masking uses simple regex patterns and may not cover every possible format.
    
    Parameters:
        text (str): The input text that may contain sensitive information.
    
    Returns:
        str: The text with sensitive information replaced by masked tags.
    """
    text = re.sub(r'\b[STFG]\d{7}[A-Z]\b', '[MASKED_NRIC]', text, flags=re.IGNORECASE)
    text = re.sub(r'\b(?:\+65[- ]?)?(?:6|8|9)\d{7}\b', '[MASKED_PHONE]', text)
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', '[MASKED_EMAIL]', text)
    text = re.sub(r'\b\d{6}\b', '[MASKED_POSTAL]', text)
    # Mask addresses - naive approach:
    # Pattern for block addresses (e.g., "Blk 123 Ang Mo Kio Ave 3")
    address_pattern1 = re.compile(
        r'\b(?:Blk|Block)\s*\d+\w*(?:[\s,]+[A-Za-z0-9]+)*\s+(?:Street|St\.|Road|Rd\.|Avenue|Ave\.|Drive|Dr\.|Lane|Ln\.)\b',
        flags=re.IGNORECASE
    )
    text = address_pattern1.sub('[MASKED_ADDRESS]', text)
    
    # Pattern for street addresses (e.g., "123 Orchard Road")
    address_pattern2 = re.compile(
        r'\b\d+\s+[A-Za-z0-9\s,]*?(?:Street|St\.|Road|Rd\.|Avenue|Ave\.|Drive|Dr\.|Lane|Ln\.)\b',
        flags=re.IGNORECASE
    )
    text = address_pattern2.sub('[MASKED_ADDRESS]', text)
    
    return text
