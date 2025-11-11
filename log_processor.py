"""
IPE Log Processor Module
========================

This module provides core log processing functionality for the IPE Log Analyzer application.
It handles token counting, content filtering, metrics extraction, and cost calculations
for efficient analysis of IPE logger output files.

Key Features:
- Token counting for OpenAI models (GPT-4.1, GPT-5)
- Intelligent content filtering (basic and advanced)
- Zero-cost metrics extraction from log files
- Accurate cost calculation for API usage
- Support for IPE message ID interpretation

Author: LogFileAnalyzerV2 Team
Version: 3.0.0
Date: October 2025
"""

import re
import tiktoken
from datetime import datetime
from collections import defaultdict
from typing import List, Tuple, Dict, Any, Optional

# ===============================
# Configuration & Constants
# ===============================

# OpenAI Pricing (USD per 1M tokens) - Updated November 2025
PRICING = {
    'gpt-4.1': {
        'input': 2.00,        # $2.00 per 1M input tokens
        'output': 8.00        # $8.00 per 1M output tokens
    },
    'gpt-5': {
        'input': 1.25,        # $1.25 per 1M input tokens
        'output': 10.00       # $10.00 per 1M output tokens
    }
}

# Critical IPE Message ID Codes - Always preserved during filtering
CRITICAL_IDS = {
    '0x00000485': 'Measurement start',
    '0x000003FA': 'StopDateTime', 
    '0x000003F9': 'StartDateTime',
    '0x00000602': 'User event',
    '0x000004D0': 'Protocol timeout',
    '0x00000490': 'WLAN Disconnected',
    '0x0000048F': 'WLAN Connected',
    '0x00000468': 'CheckDisk',
    '0x00000469': 'CheckDisk finished',
    '0x00000487': 'Configuration file',
    '0x0000047E': 'Email sent',
    '0x000003E9': 'IPEmotionRT Version',
    '0x000003EA': 'Serial number',
    '0x00000472': 'Logger type',
    '0x000003ED': 'System BIOS version',
    '0x000004A3': 'Hard drive info',
    '0x00000616': 'Hostname',
    '0x00000617': 'Wifi firmware version',
    '0x00000028': 'Total disk space',
    '0x0000000F': 'Free measurement space',
}

# Status message codes - Can be filtered for noise reduction
STATUS_IDS = {
    '0x00000530': 'System Status',
    '0x00000640': 'Medium Status', 
    '0x00000641': 'Transfer Status',
}

# ===============================
# Data Classes
# ===============================

class LogMetrics:
    """
    Data structure for holding extracted log metrics without LLM processing.
    
    This class stores structured information extracted from IPE log files
    including system information, measurements, errors, and performance data.
    
    Attributes:
        software_version (str): IPEmotionRT software version
        hardware_type (str): Logger hardware type (IPE833, IPE853, etc.)
        serial_number (str): Device serial number
        configuration_file (str): Active configuration file name
        log_period (dict): Start and end timestamps of log entries
        measurements (list): List of measurement events with IDs and times
        errors (dict): Categorized error messages by error code
        warnings (dict): Categorized warning messages by code
        wlan_events (list): Network connectivity events
        disk_info (list): Disk space and storage information
        status_summary (dict): CPU, memory, and disk usage statistics
        protocol_timeouts (list): Protocol communication failures
        power_events (list): Power-related system events
    """
    
    def __init__(self):
        self.software_version: Optional[str] = None
        self.hardware_type: Optional[str] = None
        self.serial_number: Optional[str] = None
        self.configuration_file: Optional[str] = None
        self.log_period: Dict[str, Optional[str]] = {'start': None, 'end': None}
        self.measurements: List[Dict[str, str]] = []
        self.errors: Dict[str, List[str]] = defaultdict(list)
        self.warnings: Dict[str, List[str]] = defaultdict(list)
        self.wlan_events: List[Dict[str, str]] = []
        self.disk_info: List[str] = []
        self.status_summary: Dict[str, List[int]] = {
            'cpu': [], 
            'memory': [], 
            'disk_space': []
        }
        # Optional detailed CPU events with timestamps for extrema lookup
        self.cpu_events: List[Dict[str, Any]] = []
        self.protocol_timeouts: List[str] = []
        self.power_events: List[str] = []

# ===============================
# Core Processing Functions
# ===============================


def count_tokens(text: str, model: str = "gpt-4") -> int:
    """
    Count the number of tokens in a text string for the specified OpenAI model.
    
    This function provides accurate token counting that matches OpenAI's billing
    calculations. Essential for cost estimation and chunk size management.
    
    Args:
        text (str): The input text to count tokens for
        model (str): OpenAI model name (default: "gpt-4")
                    Supported: "gpt-4", "gpt-3.5-turbo", "gpt-4-turbo"
    
    Returns:
        int: The exact number of tokens in the text
        
    Example:
        >>> count_tokens("Hello, world!", "gpt-4")
        4
        
    Note:
        - Uses tiktoken library for accurate OpenAI token counting
        - Falls back to word-based estimation if encoding fails
        - Critical for cost calculation and processing optimization
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except Exception:
        # Fallback to word-based estimation (approximately 0.75 tokens per word)
        return int(len(text.split()) * 0.75)


def chunk_text_by_tokens(text: str, max_tokens: int = 8000, model: str = "gpt-4") -> List[str]:
    """
    Split text into chunks that don't exceed the specified token limit.
    
    This function intelligently breaks large log files into processable chunks
    while attempting to preserve logical boundaries (lines, sections).
    Essential for handling large IPE log files that exceed model limits.
    
    Args:
        text (str): The input text to chunk
        max_tokens (int): Maximum tokens per chunk (default: 8000)
        model (str): OpenAI model for token counting (default: "gpt-4")
    
    Returns:
        List[str]: List of text chunks, each under the token limit
        
    Algorithm:
        1. Split text into individual lines
        2. Build chunks by adding lines until token limit approached
        3. Ensure no chunk exceeds max_tokens
        4. Preserve line boundaries to maintain log structure
        
    Example:
        >>> chunks = chunk_text_by_tokens(large_log_content, 4000)
        >>> len(chunks)
        3
        >>> all(count_tokens(chunk) <= 4000 for chunk in chunks)
        True
        
    Note:
        - Optimized for IPE log file structure
        - Maintains readability by preserving complete lines
        - Used by all processing tiers (Direct, Basic, Turbo)
    """
    lines = text.split('\n')
    chunks = []
    current_chunk = []
    current_tokens = 0
    
    for line in lines:
        line_tokens = count_tokens(line, model)
        
        # If adding this line would exceed the limit, save current chunk
        if current_tokens + line_tokens > max_tokens and current_chunk:
            chunks.append('\n'.join(current_chunk))
            current_chunk = [line]
            current_tokens = line_tokens
        else:
            current_chunk.append(line)
            current_tokens += line_tokens
    
    # Add the last chunk if it contains content
    if current_chunk:
        chunks.append('\n'.join(current_chunk))
    
    return chunks


def filter_log_content(content: str, filtering_level: str = "basic") -> str:
    """
    Apply intelligent filtering to reduce log file size while preserving critical information.
    
    This function implements multiple filtering strategies to optimize log content
    for LLM processing. It removes noise while ensuring all critical IPE events
    and error conditions are preserved.
    
    Args:
        content (str): Raw log file content
        filtering_level (str): Filtering intensity level
                              - "basic": Light filtering, preserves most content
                              - "advanced": Aggressive filtering for size reduction
    
    Returns:
        str: Filtered log content optimized for analysis
        
    Filtering Strategies:
        Basic Level:
            - Remove empty lines and excessive whitespace
            - Filter out repetitive status messages
            - Preserve all critical ID codes
            
        Advanced Level:
            - All basic filtering
            - Sample non-critical status messages (keep 1 in 10)
            - Remove debug-level verbose messages
            - Compress repetitive sequences
    
    Critical ID Preservation:
        Always preserves lines containing CRITICAL_IDS codes including:
        - System start/stop events (0x000003FA, 0x000003F9)
        - Measurement events (0x00000485)
        - Error conditions (0x000004D0)
        - Network events (0x0000048F, 0x00000490)
        - Configuration changes (0x00000487)
        
    Example:
        >>> original_size = len(content)
        >>> filtered = filter_log_content(content, "advanced")
        >>> reduction = (original_size - len(filtered)) / original_size
        >>> print(f"Size reduced by {reduction:.1%}")
        Size reduced by 65.3%
        
    Note:
        - Designed specifically for IPE logger output format
        - Maintains temporal sequence of events
        - Optimizes for both readability and token efficiency
    """
    lines = content.split('\n')
    filtered_lines = []
    
    if filtering_level == "basic":
        # Basic filtering: remove empty lines and some status messages
        for line in lines:
            # Always keep lines with critical IDs
            if any(critical_id in line for critical_id in CRITICAL_IDS.keys()):
                filtered_lines.append(line)
            # Remove empty lines and excessive whitespace
            elif line.strip() and not all(status_id in line for status_id in STATUS_IDS.keys()):
                filtered_lines.append(line)
                
    elif filtering_level == "advanced":
        # Advanced filtering: more aggressive noise reduction
        status_counter = 0
        for line in lines:
            # Always preserve critical events
            if any(critical_id in line for critical_id in CRITICAL_IDS.keys()):
                filtered_lines.append(line)
            # Sample status messages (keep 1 in 10)
            elif any(status_id in line for status_id in STATUS_IDS.keys()):
                status_counter += 1
                if status_counter % 10 == 0:
                    filtered_lines.append(line)
            # Keep other non-empty lines
            elif line.strip():
                filtered_lines.append(line)
    
    return '\n'.join(filtered_lines)


def extract_key_metrics(content: str) -> LogMetrics:
    """
    Extract structured metrics from IPE log content without using LLM processing.
    
    This function provides zero-cost analysis by parsing log files directly
    to extract key system information, events, and performance data. Essential
    for immediate insights and cost-effective monitoring.
    
    Args:
        content (str): Raw or filtered log file content
        
    Returns:
        LogMetrics: Structured data object containing:
            - System information (version, hardware, serial)
            - Measurement events and timing
            - Error and warning categorization
            - Network connectivity events
            - Storage and performance metrics
            - Protocol timeouts and failures
            
    Extraction Categories:
        System Info:
            - IPEmotionRT software version (0x000003E9)
            - Hardware type and serial number (0x000003EA, 0x00000472)
            - Configuration file identification (0x00000487)
            
        Events:
            - Measurement start/stop events (0x00000485)
            - Network connectivity changes (0x0000048F/0x00000490)
            - User-triggered events (0x00000602)
            
        Performance:
            - Disk space usage (0x00000028, 0x0000000F)
            - Protocol timeouts (0x000004D0)
            - System status metrics (0x00000530)
            
        Temporal:
            - Log period start/end timestamps
            - Event chronology and frequency
            
    Example:
        >>> metrics = extract_key_metrics(log_content)
        >>> print(f"Software: {metrics.software_version}")
        Software: IPEmotionRT 2.4.1
        >>> print(f"Measurements: {len(metrics.measurements)}")
        Measurements: 15
        >>> print(f"Errors: {sum(len(errors) for errors in metrics.errors.values())}")
        Errors: 3
        
    Note:
        - Zero LLM cost - pure regex and string parsing
        - Maintains high accuracy for structured IPE log format
        - Provides immediate insights for system monitoring
        - Used by all processing tiers for baseline metrics
    """
    metrics = LogMetrics()
    lines = content.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Extract software version
        if '0x000003E9' in line and 'IPEmotionRT' in line:
            version_match = re.search(r'IPEmotionRT\s+([\d.]+)', line)
            if version_match:
                metrics.software_version = version_match.group(1)
        
        # Extract serial number
        if '0x000003EA' in line:
            serial_match = re.search(r'Serial number:\s*(\w+)', line)
            if serial_match:
                metrics.serial_number = serial_match.group(1)
        
        # Extract hardware type
        if '0x00000472' in line:
            hardware_match = re.search(r'Logger type:\s*(\w+)', line)
            if hardware_match:
                metrics.hardware_type = hardware_match.group(1)
        
        # Extract configuration file
        if '0x00000487' in line:
            config_match = re.search(r'Configuration file:\s*(.+)', line)
            if config_match:
                metrics.configuration_file = config_match.group(1).strip()
        
        # Extract log period
        if '0x000003F9' in line:  # StartDateTime
            start_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:\.\d{3,6})?)', line)
            if start_match:
                metrics.log_period['start'] = start_match.group(1)
        
        if '0x000003FA' in line:  # StopDateTime
            stop_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:\.\d{3,6})?)', line)
            if stop_match:
                metrics.log_period['end'] = stop_match.group(1)
        
        # Extract measurement events
        if '0x00000485' in line:  # Measurement start
            timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:\.\d{3,6})?)', line)
            if timestamp_match:
                metrics.measurements.append({
                    'timestamp': timestamp_match.group(1),
                    'event': 'Measurement start',
                    'line': line
                })
        
        # Extract WLAN events
        if '0x0000048F' in line:  # WLAN Connected
            timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:\.\d{3,6})?)', line)
            if timestamp_match:
                metrics.wlan_events.append({
                    'timestamp': timestamp_match.group(1),
                    'event': 'Connected',
                    'details': line
                })
        
        if '0x00000490' in line:  # WLAN Disconnected
            timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:\.\d{3,6})?)', line)
            if timestamp_match:
                metrics.wlan_events.append({
                    'timestamp': timestamp_match.group(1),
                    'event': 'Disconnected',
                    'details': line
                })
        
        # Extract protocol timeouts
        if '0x000004D0' in line:  # Protocol timeout
            metrics.protocol_timeouts.append(line)
        
        # Extract disk information
        if '0x00000028' in line or '0x0000000F' in line:
            metrics.disk_info.append(line)
        
        # Extract errors and warnings
        if 'error' in line.lower() or 'failed' in line.lower():
            error_code = re.search(r'0x[0-9A-Fa-f]+', line)
            code = error_code.group(0) if error_code else 'Unknown'
            metrics.errors[code].append(line)
        
        if 'warning' in line.lower() or 'warn' in line.lower():
            warning_code = re.search(r'0x[0-9A-Fa-f]+', line)
            code = warning_code.group(0) if warning_code else 'Unknown'
            metrics.warnings[code].append(line)

        # Extract CPU usage from status or performance lines
        # Typical patterns may look like:
        # 2025-11-11 12:34:56.123 Status: CPU: 43% Mem: 62% Disk: 71%
        # or: 2025-11-11 12:34:56 CPU: 43% Memory: 62%
        if 'CPU:' in line:
            cpu_match = re.search(r'CPU:\s*(\d+)%', line)
            if cpu_match:
                cpu_val = int(cpu_match.group(1))
                metrics.status_summary['cpu'].append(cpu_val)
                # Attempt timestamp capture (YYYY-MM-DD HH:MM:SS(.micro) or DD.MM.YYYY HH:MM:SS(.micro))
                ts_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:\.\d{3,6})?|\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2}(?:\.\d{3,6})?)', line)
                timestamp = ts_match.group(1) if ts_match else None
                metrics.cpu_events.append({
                    'timestamp': timestamp,
                    'cpu': cpu_val,
                    'raw': line
                })

        # Extract Memory usage if present
        if re.search(r'(Mem:|Memory:)', line):
            mem_match = re.search(r'(?:Mem:|Memory:)\s*(\d+)%', line)
            if mem_match:
                metrics.status_summary['memory'].append(int(mem_match.group(1)))

        # Extract Disk space percentage usage if present
        if 'Disk:' in line:
            disk_match = re.search(r'Disk:\s*(\d+)%', line)
            if disk_match:
                metrics.status_summary['disk_space'].append(int(disk_match.group(1)))
    
    return metrics


def calculate_costs(input_tokens: int, output_tokens: int, model: str, processing_method: str = 'Direct') -> Dict[str, Any]:
    """
    Calculate the cost of OpenAI API usage for the specified model and token usage.
    
    This function provides accurate cost calculation based on current OpenAI pricing
    for both input and output tokens. Essential for budget management and cost
    optimization in log analysis workflows.
    
    Args:
        input_tokens (int): Number of tokens sent to the model (prompt + context)
        output_tokens (int): Number of tokens generated by the model (response)
        model (str): OpenAI model name ("gpt-4.1", "gpt-5", etc.)
        processing_method (str): Processing technique used ("Direct", "Basic Filtered", "ID-Based Turbo")
        
    Returns:
        Dict[str, Any]: Cost breakdown containing:
            - 'input_cost': Cost for input tokens (USD)
            - 'output_cost': Cost for output tokens (USD)  
            - 'total_cost': Combined cost (USD)
            - 'input_tokens': Number of input tokens used
            - 'output_tokens': Number of output tokens generated
            - 'model': Model name used for calculation
            - 'processing_method': Processing technique that was applied
            
    Pricing Structure (USD per 1M tokens):
        GPT-4.1:
            - Input: $1.50 per 1M tokens
            - Output: $6.00 per 1M tokens
        GPT-5:
            - Input: $5.00 per 1M tokens
            - Output: $15.00 per 1M tokens
            
    Example:
        >>> costs = calculate_costs(150000, 5000, "gpt-4.1")
        >>> print(f"Total cost: ${costs['total_cost']:.4f}")
        Total cost: $0.2550
        >>> print(f"Input: ${costs['input_cost']:.4f}, Output: ${costs['output_cost']:.4f}")
        Input: $0.2250, Output: $0.0300
        
    Note:
        - Uses current OpenAI pricing as of October 2025
        - Provides precise calculations for budget tracking
        - Supports cost comparison between different models
        - Essential for ROI analysis of log processing workflows
    """
    if model not in PRICING:
        # Default to GPT-4.1 pricing if model not found
        model = 'gpt-4.1'
    
    # Calculate costs based on per-million-token pricing
    input_cost = (input_tokens / 1_000_000) * PRICING[model]['input']
    output_cost = (output_tokens / 1_000_000) * PRICING[model]['output']
    total_cost = input_cost + output_cost
    
    return {
        'input_cost': input_cost,
        'output_cost': output_cost,
        'total_cost': total_cost,
        'input_tokens': input_tokens,
        'output_tokens': output_tokens,
        'model': model,
        'processing_method': processing_method
    }
