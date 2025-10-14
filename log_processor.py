"""
Log Processor Module
--------------------
Handles all background processing for IPE log files including:
- Token counting and chunking
- Metric extraction
- Content filtering
- Log file parsing with ID code interpretation
- Cost calculation
"""

import re
import tiktoken
from datetime import datetime
from collections import defaultdict
from typing import List, Tuple, Dict, Any, Optional

# OpenAI Pricing (as of 2025) - USD per 1M tokens
# Custom pricing for GPT-4.1 and GPT-5 models
PRICING = {
    'gpt-4.1': {
        'input': 1.50,        # $1.50 per 1M input tokens
        'output': 6.00        # $6.00 per 1M output tokens
    },
    'gpt-5': {
        'input': 5.00,        # $5.00 per 1M input tokens
        'output': 15.00       # $15.00 per 1M output tokens
    }
}

# ID Code Mappings from ids.txt - Key critical codes
CRITICAL_IDS = {
    '0x00000485': 'Measurement start',
    '0x000003FA': 'StopDateTime',
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
    '0x000003F9': 'StartDateTime',
}

# Status message codes that can be filtered out
STATUS_IDS = {
    '0x00000530': 'System Status',
    '0x00000640': 'Medium Status',
    '0x00000641': 'Transfer Status',
}


class LogMetrics:
    """Data class to hold extracted log metrics"""
    
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
        self.protocol_timeouts: List[str] = []
        self.power_events: List[str] = []


def count_tokens(text: str, model: str = "gpt-4.1") -> int:
    """
    Count the number of tokens in a text string.
    
    Args:
        text: The text to count tokens for
        model: The model name to use for tokenization (default: gpt-4.1)
        
    Returns:
        Number of tokens in the text
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        # Use cl100k_base encoding for GPT-4.1 and GPT-5 models
        encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))


def calculate_cost(input_tokens: int, output_tokens: int, model: str = "gpt-4.1") -> Dict[str, float]:
    """
    Calculate the cost of an API call based on latest OpenAI pricing (per 1M tokens).
    
    Args:
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        model: Model name (default: gpt-4.1)
        
    Returns:
        Dictionary with cost breakdown including:
        - input_tokens: Number of input tokens
        - output_tokens: Number of output tokens
        - input_cost: Cost for input tokens (USD)
        - output_cost: Cost for output tokens (USD)
        - total_cost: Total cost (USD)
        - model: Model name used for calculation
    """
    if model not in PRICING:
        model = 'gpt-4.1'  # Default to gpt-4.1 pricing
    
    # Calculate cost based on per 1M token pricing
    input_cost = (input_tokens / 1_000_000) * PRICING[model]['input']
    output_cost = (output_tokens / 1_000_000) * PRICING[model]['output']
    total_cost = input_cost + output_cost
    
    return {
        'input_tokens': input_tokens,
        'output_tokens': output_tokens,
        'input_cost': input_cost,
        'output_cost': output_cost,
        'total_cost': total_cost,
        'model': model
    }


def chunk_text_by_tokens(text: str, max_tokens: int = 100000, model: str = "gpt-4.1") -> List[str]:
    """
    Split text into chunks based on token count.
    
    Args:
        text: The text to chunk
        max_tokens: Maximum tokens per chunk (default: 100000)
        model: Model name for tokenization (default: gpt-4.1)
        
    Returns:
        List of text chunks
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    
    lines = text.split('\n')
    chunks = []
    current_chunk = []
    current_tokens = 0
    
    for line in lines:
        line_tokens = len(encoding.encode(line + '\n'))
        
        # If adding this line exceeds max_tokens, save current chunk and start new one
        if current_tokens + line_tokens > max_tokens and current_chunk:
            chunks.append('\n'.join(current_chunk))
            current_chunk = [line]
            current_tokens = line_tokens
        else:
            current_chunk.append(line)
            current_tokens += line_tokens
    
    # Add the last chunk
    if current_chunk:
        chunks.append('\n'.join(current_chunk))
    
    return chunks


def filter_log_content(log_content: str, keep_critical: bool = True) -> str:
    """
    Filter log content to keep only important events, reducing token count.
    
    Args:
        log_content: Raw log content
        keep_critical: If True, keep only critical events
        
    Returns:
        Filtered log content
    """
    lines = log_content.split('\n')
    filtered_lines = []
    
    # Always keep file boundary markers and header lines
    in_header = True
    header_count = 0
    
    for line in lines:
        # Keep file boundary markers
        if '=====' in line and 'FILE:' in line:
            filtered_lines.append(line)
            in_header = True
            header_count = 0
            continue
        
        # Keep first 20 lines after each file marker (usually contains system info)
        if in_header:
            filtered_lines.append(line)
            header_count += 1
            if header_count >= 20:
                in_header = False
            continue
        
        # Keep warnings and errors (W or E in log level)
        if re.search(r'\s[WE]\s0x', line):
            filtered_lines.append(line)
            continue
        
        # Keep critical events
        if keep_critical:
            for code in CRITICAL_IDS.keys():
                if code in line:
                    filtered_lines.append(line)
                    break
            else:
                # Skip if not critical
                continue
        else:
            # Skip repetitive status messages
            skip = False
            for status_code in STATUS_IDS.keys():
                if status_code in line:
                    skip = True
                    break
            if not skip:
                filtered_lines.append(line)
    
    return '\n'.join(filtered_lines)


def extract_key_metrics(log_content: str) -> LogMetrics:
    """
    Extract key metrics and events without full LLM processing.
    
    Args:
        log_content: Raw log content
        
    Returns:
        LogMetrics object with extracted information
    """
    metrics = LogMetrics()
    lines = log_content.split('\n')
    
    for line in lines:
        # Extract header info
        if 'IPEmotionRT' in line:
            match = re.search(r'IPEmotionRT\s+(\S+)', line)
            if match:
                metrics.software_version = match.group(1)
        
        if 'Logger type:' in line:
            match = re.search(r'Logger type:\s+(\S+)', line)
            if match:
                metrics.hardware_type = match.group(1)
        
        if 'Serial number:' in line:
            match = re.search(r'Serial number:\s+(\d+)', line)
            if match:
                metrics.serial_number = match.group(1)
        
        if 'Configuration file:' in line:
            match = re.search(r'Configuration file:\s+(.+?)(?:\s+0x|$)', line)
            if match:
                metrics.configuration_file = match.group(1).strip()
        
        # Extract timestamps
        timestamp_match = re.match(r'(\d{2}\.\d{2}\.\d{4}\s+\d{2}:\d{2}:\d{2})', line)
        if timestamp_match:
            timestamp = timestamp_match.group(1)
            if metrics.log_period['start'] is None:
                metrics.log_period['start'] = timestamp
            metrics.log_period['end'] = timestamp
        
        # Extract measurements
        if '0x00000485' in line and 'Measurement start' in line:
            match = re.search(r'Measurement start.*?:\s+(\d+)', line)
            if match and timestamp_match:
                metrics.measurements.append({
                    'id': match.group(1),
                    'time': timestamp_match.group(1)
                })
        
        # Extract errors (E prefix)
        if re.search(r'\sE\s0x', line):
            code_match = re.search(r'E\s(0x[0-9A-F]+)', line)
            if code_match:
                code = code_match.group(1)
                metrics.errors[code].append(line.strip())
        
        # Extract warnings (W prefix)
        if re.search(r'\sW\s0x', line):
            code_match = re.search(r'W\s(0x[0-9A-F]+)', line)
            if code_match:
                code = code_match.group(1)
                metrics.warnings[code].append(line.strip())
        
        # WLAN events
        if '0x00000490' in line or 'WLAN Disconnected' in line:
            if timestamp_match:
                metrics.wlan_events.append({
                    'type': 'disconnect',
                    'time': timestamp_match.group(1),
                    'detail': line.strip()
                })
        
        if '0x0000048F' in line or 'WLAN Connected' in line:
            if timestamp_match:
                metrics.wlan_events.append({
                    'type': 'connect',
                    'time': timestamp_match.group(1),
                    'detail': line.strip()
                })
        
        # Protocol timeouts
        if '0x000004D0' in line or 'timeout' in line.lower():
            metrics.protocol_timeouts.append(line.strip())
        
        # Power events
        if '0x00000466' in line or '0x00000465' in line or 'Power' in line:
            metrics.power_events.append(line.strip())
        
        # Disk information
        if '0x0000000F' in line or 'Free measurement space' in line:
            metrics.disk_info.append(line.strip())
        
        # Extract status info (sampling to avoid overload)
        if '0x00000530' in line and 'Status:' in line:
            if len(metrics.status_summary['cpu']) < 100:  # Limit samples
                cpu_match = re.search(r'CPU:\s+(\d+)%', line)
                mem_match = re.search(r'Used memory:\s+(\d+)\s+MB', line)
                disk_match = re.search(r'Free disk space.*?:\s+(\d+)\s+GB', line)
                
                if cpu_match:
                    metrics.status_summary['cpu'].append(int(cpu_match.group(1)))
                if mem_match:
                    metrics.status_summary['memory'].append(int(mem_match.group(1)))
                if disk_match:
                    metrics.status_summary['disk_space'].append(int(disk_match.group(1)))
    
    return metrics


def format_metrics_for_llm(metrics: LogMetrics) -> str:
    """
    Format extracted metrics into a concise prompt for LLM.
    
    Args:
        metrics: LogMetrics object with extracted data
        
    Returns:
        Formatted string for LLM input
    """
    prompt = f"""# IPE Log Analysis - Extracted Metrics

## System Information
- **Software**: {metrics.software_version or 'Unknown'}
- **Hardware**: {metrics.hardware_type or 'Unknown'}
- **Serial Number**: {metrics.serial_number or 'Unknown'}
- **Configuration File**: {metrics.configuration_file or 'Unknown'}
- **Log Period**: {metrics.log_period['start']} to {metrics.log_period['end']}

## Measurements ({len(metrics.measurements)} total)
"""
    
    # Show first 10 and last 10 measurements
    if metrics.measurements:
        for i, m in enumerate(metrics.measurements[:10]):
            prompt += f"{i+1}. Measurement {m['id']} started at {m['time']}\n"
        
        if len(metrics.measurements) > 20:
            prompt += f"... ({len(metrics.measurements) - 20} more measurements) ...\n"
            for i, m in enumerate(metrics.measurements[-10:], start=len(metrics.measurements)-9):
                prompt += f"{i}. Measurement {m['id']} started at {m['time']}\n"
    else:
        prompt += "No measurements found.\n"
    
    # Errors summary
    if metrics.errors:
        total_errors = sum(len(v) for v in metrics.errors.values())
        prompt += f"\n## Errors ({total_errors} total)\n"
        for code, lines in list(metrics.errors.items())[:10]:
            event_name = CRITICAL_IDS.get(code, 'Unknown')
            prompt += f"- **{code}** ({event_name}): {len(lines)} occurrence(s)\n"
            prompt += f"  First: {lines[0][:150]}...\n"
            if len(lines) > 1:
                prompt += f"  Last: {lines[-1][:150]}...\n"
    else:
        prompt += "\n## Errors\nNo errors found.\n"
    
    # Warnings summary
    if metrics.warnings:
        total_warnings = sum(len(v) for v in metrics.warnings.values())
        prompt += f"\n## Warnings ({total_warnings} total)\n"
        for code, lines in list(metrics.warnings.items())[:10]:
            event_name = CRITICAL_IDS.get(code, 'Unknown')
            prompt += f"- **{code}** ({event_name}): {len(lines)} occurrence(s)\n"
            prompt += f"  First: {lines[0][:150]}...\n"
    else:
        prompt += "\n## Warnings\nNo warnings found.\n"
    
    # WLAN events
    if metrics.wlan_events:
        prompt += f"\n## WLAN Events ({len(metrics.wlan_events)} total)\n"
        disconnects = [e for e in metrics.wlan_events if e['type'] == 'disconnect']
        connects = [e for e in metrics.wlan_events if e['type'] == 'connect']
        prompt += f"- Disconnections: {len(disconnects)}\n"
        prompt += f"- Connections: {len(connects)}\n"
        if disconnects:
            prompt += f"  First disconnect: {disconnects[0]['time']}\n"
            prompt += f"  Last disconnect: {disconnects[-1]['time']}\n"
    
    # Protocol timeouts
    if metrics.protocol_timeouts:
        prompt += f"\n## Protocol Timeouts ({len(metrics.protocol_timeouts)} occurrences)\n"
        for timeout in metrics.protocol_timeouts[:5]:
            prompt += f"- {timeout[:150]}...\n"
    
    # Power events
    if metrics.power_events:
        prompt += f"\n## Power Events ({len(metrics.power_events)} occurrences)\n"
        for event in metrics.power_events[:5]:
            prompt += f"- {event[:150]}...\n"
    
    # Disk information
    if metrics.disk_info:
        prompt += f"\n## Disk Information\n"
        prompt += f"{metrics.disk_info[-1]}\n"  # Show most recent
    
    # System health
    if metrics.status_summary['cpu']:
        avg_cpu = sum(metrics.status_summary['cpu']) / len(metrics.status_summary['cpu'])
        max_cpu = max(metrics.status_summary['cpu'])
        prompt += f"\n## System Health\n"
        prompt += f"- CPU Usage: Average {avg_cpu:.1f}%, Peak {max_cpu}%\n"
        
        if metrics.status_summary['memory']:
            avg_mem = sum(metrics.status_summary['memory']) / len(metrics.status_summary['memory'])
            max_mem = max(metrics.status_summary['memory'])
            prompt += f"- Memory Usage: Average {avg_mem:.0f} MB, Peak {max_mem} MB\n"
        
        if metrics.status_summary['disk_space']:
            min_disk = min(metrics.status_summary['disk_space'])
            prompt += f"- Disk Space: Minimum {min_disk} GB free\n"
    
    prompt += "\n---\nPlease provide a structured summary in the requested format based on this data.\n"
    
    return prompt


def chunk_by_time_period(log_content: str, hours_per_chunk: int = 6) -> List[Tuple[str, str]]:
    """
    Split log content into chunks based on time periods.
    
    Args:
        log_content: Log content
        hours_per_chunk: Hours per chunk
        
    Returns:
        List of tuples: (time_label, chunk_content)
    """
    from datetime import timedelta
    
    lines = log_content.split('\n')
    chunks = []
    current_chunk = []
    chunk_start_time = None
    
    for line in lines:
        # Extract timestamp
        timestamp_match = re.match(r'(\d{2}\.\d{2}\.\d{4}\s+\d{2}:\d{2}:\d{2})', line)
        
        if timestamp_match:
            try:
                line_time = datetime.strptime(timestamp_match.group(1), '%d.%m.%Y %H:%M:%S')
                
                if chunk_start_time is None:
                    chunk_start_time = line_time
                    current_chunk.append(line)
                elif (line_time - chunk_start_time).total_seconds() > hours_per_chunk * 3600:
                    # Save current chunk
                    time_label = chunk_start_time.strftime('%Y-%m-%d %H:%M')
                    chunks.append((time_label, '\n'.join(current_chunk)))
                    
                    # Start new chunk
                    current_chunk = [line]
                    chunk_start_time = line_time
                else:
                    current_chunk.append(line)
            except:
                current_chunk.append(line)
        else:
            current_chunk.append(line)
    
    # Add last chunk
    if current_chunk:
        time_label = chunk_start_time.strftime('%Y-%m-%d %H:%M') if chunk_start_time else "Unknown"
        chunks.append((time_label, '\n'.join(current_chunk)))
    
    return chunks
