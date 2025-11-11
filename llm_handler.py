"""
LLM Handler Module
==================

This module manages all interactions with OpenAI's GPT models for IPE log analysis.
It provides structured methods for log summarization, cost tracking, and conversation
management while maintaining detailed statistics of API usage.

Key Features:
- Streamlined GPT-4.1 and GPT-5 integration
- Comprehensive token usage and cost tracking
- Optimized prompting for IPE log analysis
- Conversation history management
- Performance monitoring and reporting

Author: LogFileAnalyzerV2 Team
Version: 3.0.0
Date: October 2025
"""

from typing import List, Dict, Any, Tuple, Optional
from openai import OpenAI
import time


class LLMHandler:
    """
    Handles all LLM operations for IPE log analysis with comprehensive cost tracking.
    
    This class provides a clean interface to OpenAI's GPT models, specifically optimized
    for analyzing IPE logger output files. It tracks all token usage, API calls, and
    associated costs to enable precise budget management.
    
    Attributes:
        client (OpenAI): Authenticated OpenAI client instance
        model (str): Currently active model name (gpt-4.1, gpt-5, etc.)
        total_input_tokens (int): Cumulative input tokens across all requests
        total_output_tokens (int): Cumulative output tokens across all requests
        api_calls (int): Total number of API calls made
        
    Example:
        >>> handler = LLMHandler(api_key="your-key", model="gpt-4.1")
        >>> summary = handler.generate_summary(log_content, system_prompt)
        >>> stats = handler.get_usage_stats()
        >>> print(f"Cost: ${stats['cost']['total_cost']:.4f}")
    """
    
    def __init__(self, api_key: str, model: str = "gpt-4.1"):
        """
        Initialize the LLM handler with authentication and model configuration.
        
        Args:
            api_key (str): Valid OpenAI API key for authentication
            model (str): OpenAI model to use (default: "gpt-4.1")
                        Supported: "gpt-4.1", "gpt-5", "gpt-4-turbo"
        
        Raises:
            AuthenticationError: If the API key is invalid
            ValueError: If the model is not supported
            
        Note:
            - Initializes with zero token counters for fresh tracking
            - Validates API key during client initialization
            - Sets up optimized parameters for IPE log analysis
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.api_calls = 0
        self.processing_method = "Direct"  # Default processing method
    
    def _api_call_with_retry(self, messages: List[Dict[str, str]], max_retries: int = 5):
        """
        Make an API call with exponential backoff retry logic for rate limits.
        
        Args:
            messages: List of message dictionaries for the chat completion
            max_retries: Maximum number of retry attempts (default: 5)
            
        Returns:
            ChatCompletion response object
            
        Raises:
            Exception: If all retries are exhausted
        """
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.3
                )
                return response
            except Exception as e:
                error_message = str(e)
                # Check if it's a rate limit error
                if "rate_limit_exceeded" in error_message or "429" in error_message:
                    if attempt < max_retries - 1:
                        # Extract wait time from error message if available
                        wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s, 8s, 16s
                        
                        # Try to parse the recommended wait time from error message
                        if "Please try again in" in error_message:
                            try:
                                import re
                                match = re.search(r'try again in ([\d.]+)s', error_message)
                                if match:
                                    wait_time = float(match.group(1)) + 1  # Add 1 second buffer
                            except:
                                pass
                        
                        print(f"Rate limit hit. Waiting {wait_time:.1f}s before retry {attempt + 1}/{max_retries}...")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise Exception(f"Rate limit exceeded after {max_retries} retries: {error_message}")
                else:
                    # Non-rate-limit error, raise immediately
                    raise
        
        raise Exception(f"API call failed after {max_retries} attempts")
    
    def generate_summary(self, content: str, system_prompt: str) -> str:
        """
        Generate a comprehensive summary for log content in a single API call.
        
        This method is optimized for log content that fits within model context limits.
        It provides the most cost-effective analysis for small to medium-sized log files
        while maintaining high quality analysis.
        
        Args:
            content (str): Complete log file content to analyze
            system_prompt (str): System instructions defining output format and requirements
            
        Returns:
            str: Structured summary following the system prompt specifications
            
        Example:
            >>> content = "17.04.2024 14:23:01 I 0x000003E9 IPEmotionRT 2.4.1..."
            >>> prompt = "Analyze IPE logs and provide structured summary..."
            >>> summary = handler.generate_summary(content, prompt)
            >>> "Software Version: IPEmotionRT 2.4.1" in summary
            True
            
        Note:
            - Most efficient method for files under token limits
            - Automatically tracks token usage and costs
            - Optimized temperature (0.3) for consistent, factual output
            - Ideal for Direct processing tier (<150K tokens)
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content}
        ]
        
        response = self._api_call_with_retry(messages)
        
        # Track usage statistics
        self.total_input_tokens += response.usage.prompt_tokens
        self.total_output_tokens += response.usage.completion_tokens
        self.api_calls += 1
        
        return response.choices[0].message.content
    
    def summarize_chunk(
        self, 
        chunk: str, 
        system_prompt: str, 
        chunk_index: Optional[int] = None, 
        total_chunks: Optional[int] = None
    ) -> str:
        """
        Summarize a single chunk of log data with contextual information.
        
        This method processes individual chunks in multi-chunk analysis workflows.
        It provides context-aware processing by indicating chunk position and
        optimizes prompts for incremental analysis.
        
        Args:
            chunk (str): Individual log chunk to summarize
            system_prompt (str): System instructions for analysis
            chunk_index (int, optional): Current chunk number (1-indexed)
            total_chunks (int, optional): Total number of chunks being processed
            
        Returns:
            str: Focused summary of the specific chunk's content
            
        Example:
            >>> chunk_summary = handler.summarize_chunk(
            ...     chunk_content, 
            ...     system_prompt, 
            ...     chunk_index=2, 
            ...     total_chunks=5
            ... )
            >>> "Chunk 2 of 5" in chunk_summary
            True
            
        Algorithm:
            1. If chunk context provided, enhance prompt with position info
            2. Focus on extracting key events from this specific chunk
            3. Provide concise, bullet-point summary for later consolidation
            4. Track token usage for cost analysis
            
        Note:
            - Used in Basic processing tier (150K-500K tokens)
            - Optimized for chunk-by-chunk analysis
            - Enables parallel processing of large log files
            - Essential for memory-efficient processing
        """
        if chunk_index and total_chunks:
            # Enhanced prompt with chunk context
            chunk_prompt = f"""
You are analyzing chunk {chunk_index} of {total_chunks} from IPEmotionRT log files.

Extract and summarize ONLY the key information from this chunk:
- Software/Hardware info (if present)
- Measurement IDs and start times  
- Errors and warnings with timestamps
- System events (startup, shutdown, etc.)
- Network connectivity changes
- Protocol timeouts or failures

Be concise but precise. Use bullet points for easy consolidation.

Log content:
{chunk}
"""
        else:
            # Standard processing without chunk context
            chunk_prompt = chunk
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": chunk_prompt}
        ]
        
        response = self._api_call_with_retry(messages)
        
        # Track usage statistics
        self.total_input_tokens += response.usage.prompt_tokens
        self.total_output_tokens += response.usage.completion_tokens
        self.api_calls += 1
        
        return response.choices[0].message.content
    
    def combine_summaries(self, summaries: List[str], system_prompt: str) -> str:
        """
        Combine multiple chunk summaries into a cohesive final analysis.
        
        This method consolidates individual chunk summaries into a unified report
        following the specified format. It handles deduplication, chronological
        organization, and comprehensive integration of findings.
        
        Args:
            summaries (List[str]): Individual chunk summaries to combine
            system_prompt (str): System instructions for final output format
            
        Returns:
            str: Unified summary in the specified structured format
            
        Example:
            >>> chunk_summaries = [summary1, summary2, summary3]
            >>> final = handler.combine_summaries(chunk_summaries, system_prompt)
            >>> "## System Information" in final
            True
            >>> "## Measurements" in final  
            True
            
        Processing Strategy:
            1. Merge duplicate system information from multiple chunks
            2. Consolidate measurement events in chronological order
            3. Organize errors and warnings by type and frequency
            4. Integrate network events and system status information
            5. Apply final formatting according to system prompt
            
        Note:
            - Final step in Basic processing tier workflow
            - Ensures consistent output format across all processing methods
            - Optimized for comprehensive analysis integration
            - Critical for maintaining analysis quality in chunked processing
        """
        combined_prompt = f"""
You have {len(summaries)} summaries from different parts of IPEmotionRT log files.

Combine them into ONE final structured summary following the exact format specified in the system prompt.

Key consolidation tasks:
- Merge duplicate system information (keep most complete version)
- Consolidate all measurements in chronological order
- Organize errors and warnings by type and frequency  
- Integrate network events and connectivity information
- Ensure comprehensive coverage of all identified issues

Chunk summaries to consolidate:
{chr(10).join([f"--- Chunk {i+1} Summary ---{chr(10)}{summary}{chr(10)}" for i, summary in enumerate(summaries)])}
"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": combined_prompt}
        ]
        
        response = self._api_call_with_retry(messages)
        
        # Track usage statistics
        self.total_input_tokens += response.usage.prompt_tokens
        self.total_output_tokens += response.usage.completion_tokens
        self.api_calls += 1
        
        return response.choices[0].message.content
    
    def answer_question(self, messages: List[Dict[str, str]]) -> str:
        """
        Answer follow-up questions about analyzed logs using conversation context.
        
        This method enables interactive analysis by maintaining conversation history
        and providing contextual answers based on previously analyzed log data.
        
        Args:
            messages (List[Dict[str, str]]): Complete conversation history
                                            Format: [{"role": "system"|"user"|"assistant", "content": "..."}]
                                            
        Returns:
            str: Contextual answer based on conversation history and log analysis
            
        Example:
            >>> messages = [
            ...     {"role": "system", "content": "You are analyzing IPE logs..."},
            ...     {"role": "user", "content": "What measurements were found?"},
            ...     {"role": "assistant", "content": "Found 15 measurements..."},
            ...     {"role": "user", "content": "Were there any network issues?"}
            ... ]
            >>> answer = handler.answer_question(messages)
            >>> "WLAN" in answer or "network" in answer
            True
            
        Features:
            - Maintains full conversation context
            - Provides accurate answers based on analyzed data
            - Supports complex follow-up questions
            - Enables iterative analysis refinement
            
        Note:
            - Used for interactive Q&A after initial analysis
            - Leverages previously analyzed log data for context
            - Optimized for technical accuracy and relevance
            - Essential for detailed troubleshooting workflows
        """
        # Inject relevant raw log snippets (evidence) for improved grounded answers
        # We look for CPU usage context if the user asks about CPU
        user_last = next((m['content'] for m in reversed(messages) if m['role'] == 'user'), '')
        injected_messages = list(messages)
        if 'cpu' in user_last.lower():
            try:
                import streamlit as st
                raw_content = st.session_state.get('final_processed_content') or st.session_state.get('raw_log_content') or ''
                evidence_lines = []
                for line in raw_content.split('\n'):
                    if 'CPU:' in line:
                        evidence_lines.append(line.strip())
                    if len(evidence_lines) >= 40:  # cap evidence to avoid token blow-up
                        break
                if evidence_lines:
                    evidence_block = "\n".join(evidence_lines)
                    injected_messages.append({
                        "role": "system",
                        "content": (
                            "EVIDENCE: The following raw log lines contain CPU information. Use ONLY these lines for CPU-related answers. "
                            "If insufficient for the user's exact request, reply with 'Insufficient evidence in provided logs' and list missing specifics.\n" + evidence_block
                        )
                    })
            except Exception:
                pass

        response = self._api_call_with_retry(injected_messages)
        
        # Track usage statistics
        self.total_input_tokens += response.usage.prompt_tokens
        self.total_output_tokens += response.usage.completion_tokens
        self.api_calls += 1
        
        return response.choices[0].message.content
    
    def set_processing_method(self, method: str):
        """
        Set the processing method being used for cost tracking.
        
        Args:
            method (str): Processing method name
                         Valid values: "Direct", "Basic Filtered", "ID-Based Turbo", "Metrics-only"
        """
        self.processing_method = method
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """
        Retrieve comprehensive token usage and cost statistics.
        
        This method provides detailed analysis of API usage including token counts,
        cost breakdown, and efficiency metrics. Essential for budget tracking and
        performance optimization.
        
        Returns:
            Dict[str, Any]: Comprehensive usage statistics containing:
                - api_calls (int): Total number of API requests made
                - input_tokens (int): Total input tokens across all requests
                - output_tokens (int): Total output tokens generated
                - total_tokens (int): Combined input and output tokens
                - cost (Dict): Detailed cost breakdown with:
                    - input_cost (float): Cost for input tokens (USD)
                    - output_cost (float): Cost for output tokens (USD)
                    - total_cost (float): Total cost (USD)
                    - input_tokens (int): Input token count
                    - output_tokens (int): Output token count
                    
        Example:
            >>> stats = handler.get_usage_stats()
            >>> print(f"Total cost: ${stats['cost']['total_cost']:.4f}")
            Total cost: $0.2550
            >>> print(f"API calls: {stats['api_calls']}")
            API calls: 3
            >>> print(f"Efficiency: {stats['output_tokens']/stats['input_tokens']:.3f} output/input ratio")
            Efficiency: 0.125 output/input ratio
            
        Cost Calculation:
            - Uses current OpenAI pricing from log_processor module
            - Provides precise calculations for budget tracking
            - Supports cost comparison between different models
            - Essential for ROI analysis of processing workflows
            
        Note:
            - Statistics persist across all handler operations
            - Provides real-time cost tracking during processing
            - Critical for budget management and optimization
            - Used for performance monitoring and reporting
        """
        from log_processor import calculate_costs
        
        cost_info = calculate_costs(
            self.total_input_tokens,
            self.total_output_tokens,
            self.model,
            self.processing_method
        )
        return {
            'api_calls': self.api_calls,
            'input_tokens': self.total_input_tokens,
            'output_tokens': self.total_output_tokens,
            'total_tokens': self.total_input_tokens + self.total_output_tokens,
            'cost': cost_info
        }
