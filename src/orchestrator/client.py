# File: src/orchestrator/client.py
"""LLM Client Adapter supporting Gemini, OpenAI, and Anthropic providers."""

import os
import sys
import logging

# Cleanly bypass system pyOpenSSL/cryptography import conflicts on older platforms
# by forcing downstream network modules to fall back to Python's robust native ssl library.
sys.modules['OpenSSL'] = None
sys.modules['OpenSSL.crypto'] = None
sys.modules['OpenSSL.SSL'] = None

logger = logging.getLogger("orchestrator.client")

class LLMAdapter:
    def __init__(self, provider: str = None, api_key: str = None):
        """
        Initializes the LLM adapter for the specified provider.

        Args:
            provider (str): 'gemini', 'openai', or 'anthropic'. Defaults to environment or 'gemini'.
            api_key (str): Optional API key override.
        """
        self.provider = provider or os.environ.get("LLM_PROVIDER", "gemini").lower()
        self.api_key = api_key
        self.client = None

        if self.provider == "gemini":
            try:
                import google.generativeai as genai
                self.client = genai
                self.client.configure(api_key=self.api_key or os.environ.get("GEMINI_API_KEY"))
                logger.info("Successfully initialized google-generativeai client.")
            except ImportError:
                logger.error("Failed to import 'google-generativeai'. Please run: pip install google-generativeai")
                raise
        elif self.provider == "openai":
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key or os.environ.get("OPENAI_API_KEY"))
                logger.info("Successfully initialized OpenAI client.")
            except ImportError:
                logger.error("Failed to import 'openai'. Please run: pip install openai")
                raise
        elif self.provider == "anthropic":
            try:
                from anthropic import Anthropic
                self.client = Anthropic(api_key=self.api_key or os.environ.get("ANTHROPIC_API_KEY"))
                logger.info("Successfully initialized Anthropic client.")
            except ImportError:
                logger.error("Failed to import 'anthropic'. Please run: pip install anthropic")
                raise
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def generate_text(self, prompt: str, system_instruction: str = None, model: str = None) -> str:
        """
        Generates text using the configured LLM provider.

        Args:
            prompt (str): The main prompt text.
            system_instruction (str): Optional system instruction or role prompt.
            model (str): Optional model name override.

        Returns:
            str: Generated text response.
        """
        if self.provider == "gemini":
            # Default model for general reasoning / coding tasks
            selected_model = model or os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")
            
            # Query google-generativeai
            model_instance = self.client.GenerativeModel(
                model_name=selected_model,
                system_instruction=system_instruction
            )
            response = model_instance.generate_content(prompt)
            return response.text

        elif self.provider == "openai":
            selected_model = model or os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
            
            messages = []
            if system_instruction:
                messages.append({"role": "system", "content": system_instruction})
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                model=selected_model,
                messages=messages
            )
            return response.choices[0].message.content

        elif self.provider == "anthropic":
            selected_model = model or os.environ.get("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
            
            # Anthropic handles system prompt as a separate top-level parameter
            kwargs = {}
            if system_instruction:
                kwargs["system"] = system_instruction
                
            response = self.client.messages.create(
                model=selected_model,
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )
            return response.content[0].text
