"""
LLM Handler Module
------------------
Handles all interactions with OpenAI's GPT models for log summarization.
Tracks token usage and costs.
"""

from typing import List, Dict, Any, Tuple
from openai import OpenAI


class LLMHandler:
    """Handles LLM operations for log analysis with cost tracking"""
    
    def __init__(self, api_key: str, model: str = "gpt-4.1"):
        """
        Initialize LLM handler.
        
        Args:
            api_key: OpenAI API key
            model: Model to use (default: gpt-4.1)
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.api_calls = 0
    
    def summarize_chunk(
        self, 
        chunk: str, 
        system_prompt: str, 
        chunk_index: int = None, 
        total_chunks: int = None
    ) -> str:
        """
        Summarize a single chunk of log data.
        
        Args:
            chunk: The log chunk to summarize
            system_prompt: System prompt for the LLM
            chunk_index: Current chunk number (1-indexed)
            total_chunks: Total number of chunks
            
        Returns:
            Summary of the chunk
        """
        if chunk_index and total_chunks:
            chunk_prompt = f"""
You are analyzing chunk {chunk_index} of {total_chunks} from IPEmotionRT log files.

Extract and summarize ONLY the key information from this chunk:
- Software/Hardware info (if present)
- Measurement IDs and start times
- Errors and warnings with timestamps
- System events (startup, shutdown, etc.)

Be concise but precise. Use bullet points.

Log content:
{chunk}
"""
        else:
            chunk_prompt = chunk
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": chunk_prompt}
            ],
            temperature=0.3
        )
        
        # Track usage
        self.total_input_tokens += response.usage.prompt_tokens
        self.total_output_tokens += response.usage.completion_tokens
        self.api_calls += 1
        
        return response.choices[0].message.content
    
    def combine_summaries(
        self, 
        summaries: List[str], 
        system_prompt: str
    ) -> str:
        """
        Combine multiple chunk summaries into a final structured summary.
        
        Args:
            summaries: List of individual chunk summaries
            system_prompt: System prompt for the LLM
            
        Returns:
            Final combined summary in the required format
        """
        combined_prompt = f"""
You have {len(summaries)} summaries from different parts of IPEmotionRT log files.

Combine them into ONE final structured summary following the exact format specified in the system prompt.

Merge duplicate information, consolidate measurements, and organize all errors/warnings chronologically.

Chunk summaries:
{chr(10).join([f"--- Chunk {i+1} Summary ---{chr(10)}{summary}{chr(10)}" for i, summary in enumerate(summaries)])}
"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": combined_prompt}
            ],
            temperature=0.3
        )
        
        # Track usage
        self.total_input_tokens += response.usage.prompt_tokens
        self.total_output_tokens += response.usage.completion_tokens
        self.api_calls += 1
        
        return response.choices[0].message.content
    
    def generate_summary(
        self, 
        content: str, 
        system_prompt: str
    ) -> str:
        """
        Generate a summary for content that fits in a single request.
        
        Args:
            content: Log content to summarize
            system_prompt: System prompt for the LLM
            
        Returns:
            Generated summary
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content}
            ],
            temperature=0.3
        )
        
        # Track usage
        self.total_input_tokens += response.usage.prompt_tokens
        self.total_output_tokens += response.usage.completion_tokens
        self.api_calls += 1
        
        return response.choices[0].message.content
    
    def answer_question(
        self, 
        messages: List[Dict[str, str]]
    ) -> str:
        """
        Answer a follow-up question about the logs.
        
        Args:
            messages: Full conversation history
            
        Returns:
            Answer to the question
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.3
        )
        
        # Track usage
        self.total_input_tokens += response.usage.prompt_tokens
        self.total_output_tokens += response.usage.completion_tokens
        self.api_calls += 1
        
        return response.choices[0].message.content
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """
        Get token usage and cost statistics.
        
        Returns:
            Dictionary with usage statistics
        """
        from log_processor import calculate_cost
        
        cost_info = calculate_cost(
            self.total_input_tokens,
            self.total_output_tokens,
            self.model
        )
        
        return {
            'api_calls': self.api_calls,
            'input_tokens': self.total_input_tokens,
            'output_tokens': self.total_output_tokens,
            'total_tokens': self.total_input_tokens + self.total_output_tokens,
            'cost': cost_info
        }
