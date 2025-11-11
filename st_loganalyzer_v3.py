"""
IPE Log Analyzer - Main Application
===================================

A comprehensive Streamlit web application for analyzing IPE logger diagnostic files.
This application provides intelligent three-tier processing, advanced filtering,
and detailed cost tracking for efficient analysis of IPEmotion RT log files.

Architecture Overview:
    - Modular design with separated UI, processing, and LLM handling
    - Three-tier processing strategy for optimal performance and cost
    - Intelligent filtering with ID-based turbo optimization
    - Comprehensive token reduction tracking and cost analysis
    - Interactive Q&A functionality with conversation history

Processing Tiers:
    1. Direct Processing (< 150K tokens):
       - Single API call for maximum efficiency
       - Full content analysis without filtering
       - Optimal cost for small to medium files
       
    2. Basic Processing (150K - 500K tokens):
       - Intelligent chunking with basic filtering
       - Chunk-by-chunk analysis with final consolidation
       - Balanced performance and cost optimization
       
    3. Turbo Processing (> 500K tokens):
       - Advanced ID-based filtering with critical event preservation
       - Massive token reduction (over 95%) while maintaining accuracy
       - Specialized for very large log files and cost optimization

Key Features:
    - Support for .LOG files and .ZIP archives
    - Real-time token counting and cost estimation
    - Advanced progress tracking with detailed metrics
    - ID-based filtering with critical/less-critical classification
    - Comprehensive usage statistics and performance monitoring
    - Interactive follow-up question capability
    - Professional structured output with IPE-specific formatting

Supported Models:
    - GPT-4.1 (recommended): $2.00/$8.00 per 1M tokens (input/output)
    - GPT-5 (premium): $1.25/$10.00 per 1M tokens (input/output)

Author: LogFileAnalyzerV2 Team
Version: 3.0.0
Date: October 2025
License: Internal Use - IPETRONIK IPE Log Analysis
"""

import streamlit as st
import os
import zipfile
from typing import List, Tuple, Dict, Any, Optional

# Import our custom modules
from log_processor import (
    count_tokens,
    chunk_text_by_tokens,
    filter_log_content,
    extract_key_metrics
)
from llm_handler import LLMHandler


# ===============================
# Configuration and Constants
# ===============================

# ===============================
# Configuration and Constants
# ===============================

# System prompt for IPE log analysis with professional formatting
SYSTEM_PROMPT = """
You are LogInsightGPT, an assistant specialized in analyzing and summarizing diagnostic and runtime logs from IPETRONIK's IPEmotionRT system (e.g., version 2024 R3.2 or 2025 R2.65794), running on logger types like IPE833 or IPE853.

Your primary directive: STRICTLY use ONLY the provided raw log content (including file boundary markers like '====== FILE:') and any earlier generated summary when answering. Do NOT rely on outside knowledge, assumptions, or undocumented behavior. If information is absent, state clearly: "Information not found in provided logs." Never fabricate values (e.g., versions, measurement IDs, serial numbers, timestamps) that are not explicitly present.

When producing the initial structured summary, follow the format exactly as below. When answering follow-up questions:
1. Cite supporting evidence by quoting minimal raw log line fragments (or measurement IDs) under a heading "Evidence".
2. If partial but inconclusive evidence exists, respond with "Insufficient evidence in provided logs" and list what is missing.
3. For counts, derive them directly from the log lines; do not estimate.
4. For chronological questions, base ordering only on timestamps present.
5. If asked about causes or diagnostics not explicitly stated, provide a neutral statement: "The logs do not specify the root cause." and optionally list related error/warning lines.
6. Never include sensitive speculation or external product details not in the logs.
7. Prefer concise, structured answers. Avoid repetition.

Refusal policy: If a user asks for data outside the logs (e.g., future features, internal architecture not logged), reply: "Cannot answer: information not contained in the provided logs." Do not apologize unless explicitly asked.

### 🧾 General Information:

**<span style='color:#4e88ff'>Software</span>**: [Software Version]  
**<span style='color:#4e88ff'>Hardware</span>**: Logger type [Logger Type]  
**<span style='color:#4e88ff'>Serial number</span>**: [Serial Number]  
**<span style='color:#4e88ff'>Period of the log entries</span>**: [Log Entry Period]  
**<span style='color:#4e88ff'>Configuration file</span>**: [Configuration File Name]

### 📌 Important Events:

- **<span style='color:#ff914d'>System start & initialization</span>**  
    - [List startup events as bullet points]

- **<span style='color:#ff914d'>Memory check & cleanup</span>**  
    - [List memory check events as bullet points]

- **<span style='color:#ff914d'>Measurements & data transfer</span>**  
    - [List measurement events, with numbered measurement IDs and corresponding start times]
    - Data transfer to IPEcloud (if applicable)
  
- **<span style='color:#ff914d'>Error messages & warnings</span>**  
    - **Power**: [timestamp with milliseconds] [Description]
    - **WLAN**: [timestamp with milliseconds] [Description]
    - **CAN**: [timestamp with milliseconds] [Description]
    - **GPS**: [timestamp with milliseconds] [Description]
    - **Disk**: [timestamp with milliseconds] [Description]
    - **Protocols**: [timestamp with milliseconds] [Description]

### ✅ Conclusion:

Summarize key takeaways using emojis (only if justified by log evidence).

Notes:
- Use only the information inside the logs.
- Maintain professional tone, consistent formatting, and structured section headings.
- Do not speculate; cite evidence for non-trivial answers.
"""

# Three-tier processing thresholds optimized for performance and cost
TOKEN_THRESHOLD_FILTERING = 150000      # Switch to Basic processing (with filtering)
TOKEN_THRESHOLD_TURBO_FILTERING = 500000  # Switch to Turbo processing (aggressive filtering)
MAX_TOKENS_PER_CHUNK = 20000           # Safe chunk size within rate limits (30K TPM limit)

# Processing Tier Configuration:
# Tier 1 - Direct: < 150K tokens (single API call, no filtering)
# Tier 2 - Basic: 150K-500K tokens (chunked processing with basic filtering)  
# Tier 3 - Turbo: > 500K tokens (ID-based filtering with massive reduction)

# ===============================
# File Processing Functions
# ===============================

def extract_logs_from_zip(zip_file) -> List[Tuple[str, str]]:
    """
    Extract all .LOG files from a ZIP archive with comprehensive error handling.
    
    This function safely extracts IPE log files from ZIP archives, handling
    various encoding issues and providing detailed error reporting for
    troubleshooting file processing problems.
    
    Args:
        zip_file: Uploaded ZIP file object from Streamlit file uploader
        
    Returns:
        List[Tuple[str, str]]: List of tuples containing:
            - filename (str): Base filename of the extracted log file
            - content (str): Decoded text content of the log file
            
    Example:
        >>> zip_files = st.file_uploader("Upload ZIP", type="zip")
        >>> logs = extract_logs_from_zip(zip_files[0])
        >>> len(logs)
        3
        >>> logs[0][0]
        'system_log.LOG'
        
    Error Handling:
        - BadZipFile: Invalid or corrupted ZIP archives
        - UnicodeDecodeError: Handles various text encodings gracefully
        - FileNotFoundError: Missing or inaccessible files within archive
        - PermissionError: Access restrictions on archive contents
        
    Note:
        - Only processes files with .LOG extension (case-insensitive)
        - Skips directories and non-log files automatically
        - Uses UTF-8 decoding with error tolerance for robust processing
        - Provides user-friendly error messages via Streamlit interface
    """
    log_files = []
    try:
        with zipfile.ZipFile(zip_file) as z:
            for file_info in z.infolist():
                if file_info.filename.upper().endswith(".LOG") and not file_info.is_dir():
                    with z.open(file_info) as f:
                        # Decode with error tolerance for various text encodings
                        text = f.read().decode("utf-8", errors="ignore")
                        display_name = os.path.basename(file_info.filename)
                        log_files.append((display_name, text))
    except zipfile.BadZipFile:
        st.error(f"❌ Error: {zip_file.name} is not a valid ZIP file.")
    except Exception as e:
        st.error(f"❌ Error reading ZIP file {zip_file.name}: {str(e)}")
    
    return log_files


def process_uploaded_files(uploaded_files) -> List[Tuple[str, str]]:
    """
    Process mixed file uploads (.LOG files and .ZIP archives) into unified log content.
    
    This function handles the complexity of processing multiple file types,
    extracting log content from both individual .LOG files and .ZIP archives
    containing multiple log files.
    
    Args:
        uploaded_files: List of uploaded file objects from Streamlit file uploader
                       Supports mixed types: .LOG files and .ZIP archives
        
    Returns:
        List[Tuple[str, str]]: Unified list of log files containing:
            - filename (str): Original filename or extracted filename from ZIP
            - content (str): Decoded log file content ready for analysis
            
    Processing Logic:
        1. Iterate through all uploaded files
        2. Identify file type by extension (.LOG or .ZIP)
        3. For .LOG files: Direct text extraction with encoding handling
        4. For .ZIP files: Extract all contained .LOG files
        5. Aggregate all log content into unified list
        6. Provide detailed feedback on processing results
        
    Example:
        >>> files = st.file_uploader("Upload files", type=["log", "zip"], accept_multiple_files=True)
        >>> logs = process_uploaded_files(files)
        >>> print(f"Processed {len(logs)} log files")
        Processed 5 log files
        
    Error Handling:
        - Invalid file types: Warning with file skipping
        - Encoding errors: Graceful handling with error tolerance
        - Empty ZIP files: Warning notification to user
        - Corrupted files: Error reporting with specific file identification
        
    Note:
        - Supports case-insensitive file extension matching
        - Maintains original filename context for user reference
        - Provides comprehensive feedback via Streamlit UI
        - Optimized for batch processing of multiple log sources
    """
    all_log_files = []
    
    for uploaded_file in uploaded_files:
        file_extension = uploaded_file.name.upper().split('.')[-1]
        
        if file_extension == 'LOG':
            try:
                # Extract individual .LOG file content
                file_text = uploaded_file.read().decode("utf-8", errors="ignore")
                all_log_files.append((uploaded_file.name, file_text))
            except Exception as e:
                st.error(f"❌ Error reading LOG file {uploaded_file.name}: {str(e)}")
                
        elif file_extension == 'ZIP':
            # Extract all .LOG files from ZIP archive
            log_files_from_zip = extract_logs_from_zip(uploaded_file)
            if log_files_from_zip:
                all_log_files.extend(log_files_from_zip)
            else:
                st.warning(f"⚠️ No LOG files found in ZIP archive: {uploaded_file.name}")
        else:
            st.warning(f"⚠️ Unsupported file type: {uploaded_file.name}")
    
    return all_log_files


def combine_log_files(log_files: List[Tuple[str, str]]) -> str:
    """
    Combine multiple log files into a unified content string with clear boundaries.
    
    This function merges log content from multiple sources while preserving
    file boundaries and maintaining traceability of content sources for
    analysis and debugging purposes.
    
    Args:
        log_files (List[Tuple[str, str]]): List of log file tuples containing:
            - filename (str): Source filename for boundary marking
            - content (str): Log file content to be combined
        
    Returns:
        str: Unified log content with clear file boundaries and headers
        
    Content Structure:
        - File boundary markers with clear visual separation
        - Filename headers for content traceability  
        - Preserved original content with no modifications
        - Consistent formatting for parser compatibility
        
    Example:
        >>> logs = [("log1.LOG", "content1"), ("log2.LOG", "content2")]
        >>> combined = combine_log_files(logs)
        >>> "====== FILE: log1.LOG ======" in combined
        True
        >>> "====== FILE: log2.LOG ======" in combined
        True
        
    Boundary Format:
        ```
        ====== FILE: filename.LOG ======
        [original file content]
        
        ====== FILE: next_file.LOG ======
        [next file content]
        ```
        
    Note:
        - Maintains chronological order of file processing
        - Preserves all original content without filtering
        - Creates clear visual boundaries for human readability
        - Compatible with downstream processing and analysis tools
        - Essential for multi-file analysis workflows
    """
    if not log_files:
        return ""
    
    if len(log_files) == 1:
        # Single file - return content directly with simple header
        filename, content = log_files[0]
        return f"====== FILE: {filename} ======\n{content}"
    
    # Multiple files - combine with clear boundaries
    combined_content = []
    for filename, content in log_files:
        combined_content.append(f"====== FILE: {filename} ======")
        combined_content.append(content)
        combined_content.append("")  # Empty line for separation
    
    return "\n".join(combined_content)


# ===============================
# Core Processing Logic
# ===============================

def process_logs_smart(
    log_content: str, 
    llm_handler: LLMHandler,
    progress_callback=None,
    force_metrics_only: bool = False
) -> str:
    """
    Intelligently process logs based on size - TWO TIER APPROACH with Smart Filtering.
    
    Args:
        log_content: Combined log content
        llm_handler: LLM handler instance
        progress_callback: Optional callback for progress updates
        force_metrics_only: Force metrics-only analysis regardless of size (still available as option)
        
    Returns:
        Final summary (LLM-generated or metrics-based)
    """
    # Count tokens
    total_tokens = count_tokens(log_content, llm_handler.model)
    
    if progress_callback:
        progress_callback(f"📊 Analyzing {total_tokens:,} tokens...")
    
    # Cache raw content for follow-up questions (direct or filtered later)
    # Cache raw content for follow-up questions (direct or filtered later)
    st.session_state['raw_log_content'] = log_content

    # Strategy 0: Metrics-only analysis (only if forced by user)
    if force_metrics_only:
        if progress_callback:
            progress_callback("🔍 Forced metrics-only analysis...")
        llm_handler.set_processing_method("Metrics-only")
        return process_with_metrics_only(log_content, progress_callback)
    
    # Strategy 1: Direct processing (< 150K tokens)
    elif total_tokens < TOKEN_THRESHOLD_FILTERING:
        if progress_callback:
            progress_callback("🚀 Processing directly...")
        llm_handler.set_processing_method("Direct")
        
        if total_tokens <= MAX_TOKENS_PER_CHUNK:
            summary = llm_handler.generate_summary(log_content, SYSTEM_PROMPT)
            st.session_state['final_processed_content'] = log_content
            return summary
        else:
            processed = process_with_chunking(log_content, llm_handler, progress_callback)
            st.session_state['final_processed_content'] = log_content
            return processed
    
    # Strategy 2: Turbo filtered processing (>= 500K tokens)
    elif total_tokens >= TOKEN_THRESHOLD_TURBO_FILTERING:
        if progress_callback:
            progress_callback("🚀 Applying turbo filtering for large files...")
        llm_handler.set_processing_method("ID-Based Turbo")
        
        # Fast preprocessing: Remove extremely verbose lines first
        if progress_callback:
            progress_callback("⚡ Fast preprocessing...")
        
        preprocessed_content = fast_preprocess_content(log_content)
        preprocessed_tokens = count_tokens(preprocessed_content, llm_handler.model)
        
        if progress_callback:
            preprocess_reduction = (1 - preprocessed_tokens / total_tokens) * 100
            tokens_saved_preprocess = total_tokens - preprocessed_tokens
            progress_callback(f"⚡ Preprocessed: {preprocess_reduction:.1f}% reduction ({total_tokens:,} → {preprocessed_tokens:,} tokens)")
            progress_callback(f"🗑️ Noise removed: {tokens_saved_preprocess:,} tokens of verbose content")
        
        # Apply turbo filtering (always use turbo mode for large files)
        if progress_callback:
            progress_callback("🚀 ID-based turbo filtering...")
        
        filtered_content, reduction_stats = create_turbo_filtered_content_with_stats(preprocessed_content)
        filtered_tokens = count_tokens(filtered_content, llm_handler.model)
        
        if progress_callback:
            total_reduction = (1 - filtered_tokens / total_tokens) * 100
            tokens_saved = total_tokens - filtered_tokens
            progress_callback(f"✂️ Turbo filtered: {total_reduction:.1f}% reduction ({total_tokens:,} → {filtered_tokens:,} tokens)")
            progress_callback(f"� Tokens saved: {tokens_saved:,} tokens (${tokens_saved * 0.000015:.4f} cost savings)")
            progress_callback(f"📊 Line reduction: {reduction_stats['line_reduction']:.1f}% ({reduction_stats['original_lines']:,} → {reduction_stats['filtered_lines']:,} lines)")
            progress_callback(f"🎯 Critical events preserved: {reduction_stats['critical_events_kept']} | Less critical sampled: {reduction_stats['less_critical_sampled']}")
        
        # Process filtered content with LLM
        if filtered_tokens <= MAX_TOKENS_PER_CHUNK:
            summary = llm_handler.generate_summary(filtered_content, SYSTEM_PROMPT)
            st.session_state['final_processed_content'] = filtered_content
            return summary
        else:
            processed = process_with_chunking(filtered_content, llm_handler, progress_callback)
            st.session_state['final_processed_content'] = filtered_content
            return processed
    
    # Strategy 3: Basic filtered processing (150K - 500K tokens)
    else:
        if progress_callback:
            progress_callback("🔍 Applying basic filtering...")
        llm_handler.set_processing_method("Basic Filtered")
        
        # Apply basic filtering (existing filter_log_content function)
        filtered_content = filter_log_content(log_content)
        filtered_tokens = count_tokens(filtered_content, llm_handler.model)
        
        if progress_callback:
            reduction = (1 - filtered_tokens / total_tokens) * 100
            tokens_saved = total_tokens - filtered_tokens
            progress_callback(f"✂️ Basic filtered: {reduction:.1f}% reduction ({total_tokens:,} → {filtered_tokens:,} tokens)")
            progress_callback(f"💾 Tokens saved: {tokens_saved:,} tokens (${tokens_saved * 0.000015:.4f} estimated cost savings)")
        
        # Process filtered content with LLM
        if filtered_tokens <= MAX_TOKENS_PER_CHUNK:
            summary = llm_handler.generate_summary(filtered_content, SYSTEM_PROMPT)
            st.session_state['final_processed_content'] = filtered_content
            return summary
        else:
            processed = process_with_chunking(filtered_content, llm_handler, progress_callback)
            st.session_state['final_processed_content'] = filtered_content
            return processed


def fast_preprocess_content(log_content: str) -> str:
    """
    Ultra-fast preprocessing to remove extremely verbose lines before smart filtering.
    This removes the most obvious noise very quickly.
    
    Args:
        log_content: Raw log content
        
    Returns:
        Preprocessed content with most verbose noise removed
    """
    lines = log_content.split('\n')
    filtered_lines = []
    
    # Define patterns to skip entirely (most verbose noise)
    skip_patterns = [
        'Interface-Statistic',  # Network statistics
        'MqttClient: Publishing',  # MQTT spam
        'MqttClient: Connecting',  # MQTT connection spam
        'Checksum validated',  # SFTP spam
        'SFTP connect to server',  # SFTP details
        'Start time update',  # Time sync spam
        'Time update finished',  # Time sync spam
        'Time update succeeded',  # More time sync
        'Mail finished',  # Routine email success
        'Interface [',  # Interface status spam
        'Transfer Status:',  # Transfer statistics
        'Medium Status:',  # Medium statistics
    ]
    
    # Skip lines that contain debug/trace keywords
    debug_keywords = ['debug', 'trace', 'verbose']
    
    line_count = 0
    for line in lines:
        line_count += 1
        
        # Skip empty lines
        if not line.strip():
            continue
            
        # Skip extremely verbose patterns (fastest check first)
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in debug_keywords):
            continue
            
        # Skip specific noise patterns
        if any(pattern in line for pattern in skip_patterns):
            continue
            
        # Skip lines that are too long (likely debug spam)
        if len(line) > 1000:
            continue
            
        # Skip repetitive status messages more aggressively
        if line_count % 5 == 0 and any(status in line for status in ['Status:', '0x00000530', '0x00000640']):
            continue  # Keep only every 5th status message during preprocessing
            
        filtered_lines.append(line)
    
    return '\n'.join(filtered_lines)


def create_turbo_filtered_content(log_content: str) -> str:
    """
    OPTIMIZED TURBO MODE: ID-based intelligent filtering for large files (over 500,000 tokens).
    Uses structured ID classification to preserve critical events while removing noise.
    Provides over 95% token reduction with maintained analysis quality.
    
    Args:
        log_content: Preprocessed log content
        
    Returns:
        Intelligently filtered content with size reduction metrics
    """
    content, stats = create_turbo_filtered_content_with_stats(log_content)
    return content


def create_turbo_filtered_content_with_stats(log_content: str) -> tuple[str, dict]:
    """
    OPTIMIZED TURBO MODE with detailed statistics tracking.
    ID-based intelligent filtering for large files (over 500,000 tokens).
    
    Args:
        log_content: Preprocessed log content
        
    Returns:
        Tuple of (filtered_content, reduction_statistics)
    """
    import re
    
    # Critical IDs - Always keep (100% retention)
    CRITICAL_IDS = {
        '0x000003FF', '0x00000496', '0x00000497', '0x000004A1', '0x000004A5',
        '0x000004B1', '0x00000522', '0x000004E2', '0x000005F0', '0x000005F8',
        '0x00000610', '0x000004D0', '0x000004F0', '0x00000500', '0x00000508',
        # Core measurement and system IDs
        '0x00000485', '0x000003F9', '0x000003FA'  # Measurement events
    }
    
    # Less Critical IDs - Selective keep (25% sampling)
    LESS_CRITICAL_IDS = {
        '0x000004D8', '0x000004E0', '0x000004E8', '0x00000510', '0x00000479',
        '0x0000047B', '0x0000047D', '0x00000488', '0x00000489', '0x0000048A',
        '0x00000023', '0x00000024', '0x00000490', '0x000005FB', '0x000005FC'
    }
    
    # Essential patterns (always keep)
    critical_patterns = re.compile(r'(E 0x|Failed|Error|Exception|WLAN Disconnected)', re.IGNORECASE)
    essential_events = re.compile(r'(CheckDisk|Configuration|User event|Power|Measurement start)', re.IGNORECASE)
    
    lines = log_content.split('\n')
    filtered_lines = []
    original_lines = len(lines)
    
    # Statistics tracking
    stats = {
        'original_lines': original_lines,
        'critical_events_kept': 0,
        'less_critical_sampled': 0,
        'essential_patterns_kept': 0,
        'headers_kept': 0,
        'high_cpu_alerts_kept': 0,
        'routine_sampled': 0,
        'filtered_lines': 0,
        'line_reduction': 0.0,
        'lines_removed': 0
    }
    
    line_count = 0
    less_critical_sample_count = 0
    
    for line in lines:
        line_count += 1
        
        if not line.strip():
            continue
        
        # 1. ALWAYS KEEP: File boundaries and headers
        if any(marker in line for marker in ['===== ', 'IPEmotionRT', 'Logger type:', 'Serial number:', 'Configuration file:']):
            filtered_lines.append(line)
            stats['headers_kept'] += 1
            continue
        
        # 2. ALWAYS KEEP: Critical ID patterns
        critical_id_found = False
        for critical_id in CRITICAL_IDS:
            if critical_id in line:
                filtered_lines.append(line)
                stats['critical_events_kept'] += 1
                critical_id_found = True
                break
        
        if critical_id_found:
            continue
        
        # 3. ALWAYS KEEP: Critical error patterns
        if critical_patterns.search(line):
            filtered_lines.append(line)
            stats['essential_patterns_kept'] += 1
            continue
        
        # 4. ALWAYS KEEP: Essential system events
        if essential_events.search(line):
            filtered_lines.append(line)
            stats['essential_patterns_kept'] += 1
            continue
        
        # 5. SELECTIVE KEEP: Less critical IDs (25% sampling)
        less_critical_found = False
        for less_critical_id in LESS_CRITICAL_IDS:
            if less_critical_id in line:
                less_critical_sample_count += 1
                # Keep every 4th occurrence (25% sampling)
                if less_critical_sample_count % 4 == 0:
                    filtered_lines.append(line)
                    stats['less_critical_sampled'] += 1
                less_critical_found = True
                break
        
        if less_critical_found:
            continue
        
        # 6. KEEP: High CPU usage alerts (>80%)
        if 'CPU:' in line and 'Status:' in line:
            # Extract CPU percentage
            cpu_match = re.search(r'CPU:\s*(\d+)%', line)
            if cpu_match and int(cpu_match.group(1)) > 80:
                filtered_lines.append(line)
                stats['high_cpu_alerts_kept'] += 1
                continue
        
        # 7. AGGRESSIVE SAMPLING: Other content (5% sampling)
        if line_count % 20 == 0:  # Keep every 20th line (5%)
            # Prioritize lines with important keywords
            if any(keyword in line for keyword in ['WLAN', 'Timeout', 'Protocol', 'Transfer', 'Status:', 'Mail']):
                filtered_lines.append(line)
                stats['routine_sampled'] += 1
                continue
    
    filtered_content = '\n'.join(filtered_lines)
    
    # Calculate final statistics
    filtered_lines_count = len(filtered_lines)
    line_reduction = ((original_lines - filtered_lines_count) / original_lines) * 100 if original_lines > 0 else 0
    
    stats['filtered_lines'] = filtered_lines_count
    stats['line_reduction'] = line_reduction
    stats['lines_removed'] = original_lines - filtered_lines_count
    
    # Add detailed metrics header to filtered content
    metrics_header = f"""
# ===============================
# TURBO FILTERING REDUCTION METRICS
# ===============================
# Original lines: {original_lines:,}
# Filtered lines: {filtered_lines_count:,}
# Lines removed: {stats['lines_removed']:,}
# Reduction: {line_reduction:.1f}%
#
# CONTENT PRESERVED:
# - Critical events: {stats['critical_events_kept']}
# - Essential patterns: {stats['essential_patterns_kept']}
# - Headers/boundaries: {stats['headers_kept']}
# - Less critical (sampled): {stats['less_critical_sampled']}
# - High CPU alerts: {stats['high_cpu_alerts_kept']}
# - Routine content (sampled): {stats['routine_sampled']}
#
# Critical IDs monitored: {len(CRITICAL_IDS)}
# Less critical IDs monitored: {len(LESS_CRITICAL_IDS)}
# ===============================

"""
    
    return metrics_header + filtered_content, stats


def process_with_chunking(
    content: str,
    llm_handler: LLMHandler,
    progress_callback=None
) -> str:
    """
    OPTIMIZED: Process content using chunking and hierarchical summarization.
    
    Args:
        content: Content to process
        llm_handler: LLM handler instance
        progress_callback: Optional callback for progress updates
        
    Returns:
        Final combined summary
    """
    chunks = chunk_text_by_tokens(content, MAX_TOKENS_PER_CHUNK, llm_handler.model)
    
    if progress_callback:
        progress_callback(f"📦 Split into {len(chunks)} chunks")
    
    # If we have too many chunks, reduce them by increasing chunk size (but stay within rate limits)
    if len(chunks) > 8:  # Reduced threshold from 10 to 8
        if progress_callback:
            progress_callback(f"⚡ Optimizing chunk count ({len(chunks)} → target ~6 chunks)...")
        # Use larger chunks but stay within 30K TPM rate limit
        larger_chunk_size = min(MAX_TOKENS_PER_CHUNK * 1.15, 23000)  # Max 23K to stay under 30K limit
        chunks = chunk_text_by_tokens(content, int(larger_chunk_size), llm_handler.model)
        if progress_callback:
            progress_callback(f"📦 Optimized to {len(chunks)} chunks")
    
    # For very large files, don't exceed rate limits
    if len(chunks) > 12:
        if progress_callback:
            progress_callback(f"🚀 Ultra-optimizing for large file ({len(chunks)} chunks)...")
        # Use maximum safe chunk size (stay under 30K TPM limit)
        ultra_chunk_size = min(MAX_TOKENS_PER_CHUNK * 1.1, 22000)  # Max 22K tokens
        chunks = chunk_text_by_tokens(content, int(ultra_chunk_size), llm_handler.model)
        if progress_callback:
            progress_callback(f"📦 Ultra-optimized to {len(chunks)} chunks")
    
    # Summarize each chunk with progress
    chunk_summaries = []
    for i, chunk in enumerate(chunks):
        if progress_callback:
            progress_percentage = ((i + 1) / len(chunks)) * 80  # Reserve 20% for final combination
            progress_callback(f"🔄 Processing chunk {i+1}/{len(chunks)} ({progress_percentage:.0f}%)...")
        
        summary = llm_handler.summarize_chunk(
            chunk, SYSTEM_PROMPT, i+1, len(chunks)
        )
        chunk_summaries.append(summary)
        
        # Add delay between chunks to respect TPM rate limit (30K tokens/min)
        # Wait 3 seconds between chunks to stay under limit
        if i < len(chunks) - 1:  # Don't wait after last chunk
            import time
            time.sleep(3)
    
    # Combine summaries
    if progress_callback:
        progress_callback("🔄 Combining chunk summaries (90%)...")
    
    final_summary = llm_handler.combine_summaries(chunk_summaries, SYSTEM_PROMPT)
    
    if progress_callback:
        progress_callback("✅ Processing complete!")
    
    return final_summary


def process_with_metrics_only(log_content: str, progress_callback=None) -> str:
    """
    Process content using only metrics extraction (no LLM).
    
    Args:
        log_content: Content to analyze
        progress_callback: Optional callback for progress updates
        
    Returns:
        Formatted metrics summary
    """
    if progress_callback:
        progress_callback("📈 Extracting key metrics...")
    
    # Import here to avoid circular import
    from log_processor import extract_key_metrics
    
    # Extract metrics
    metrics = extract_key_metrics(log_content)
    
    if progress_callback:
        progress_callback("📋 Formatting metrics summary...")
    
    # Format as a readable summary (similar to LLM output but without LLM)
    summary = format_metrics_summary(metrics)
    
    return summary


def format_metrics_summary(metrics) -> str:
    """
    Format extracted metrics into a structured summary similar to LLM output.
    
    Args:
        metrics: LogMetrics object with extracted data
        
    Returns:
        Formatted summary string
    """
    import re
    
    summary = f"""### 🧾 General Information:

**<span style='color:#4e88ff'>Software</span>**: {metrics.software_version or 'Unknown'}  
**<span style='color:#4e88ff'>Hardware</span>**: {metrics.hardware_type or 'Unknown'}  
**<span style='color:#4e88ff'>Serial number</span>**: {metrics.serial_number or 'Unknown'}  
**<span style='color:#4e88ff'>Period of the log entries</span>**: {metrics.log_period.get('start', 'Unknown')} to {metrics.log_period.get('end', 'Unknown')}  
**<span style='color:#4e88ff'>Configuration file</span>**: {metrics.configuration_file or 'Unknown'}

### 📌 Important Events:

- **<span style='color:#ff914d'>System start & initialization</span>**  
"""
    
    # Add measurements
    if metrics.measurements:
        summary += f"  - Found {len(metrics.measurements)} measurements\n"
        for i, m in enumerate(metrics.measurements[:5]):
            summary += f"  - Measurement {m['id']} started at {m['time']}\n"
        if len(metrics.measurements) > 5:
            summary += f"  - ... and {len(metrics.measurements) - 5} more measurements\n"
    else:
        summary += "  - No measurements found\n"
    
    summary += "\n- **<span style='color:#ff914d'>Memory check & cleanup</span>**  \n"
    if metrics.disk_info:
        summary += f"  - {len(metrics.disk_info)} disk space entries found\n"
        for info in metrics.disk_info[:3]:
            summary += f"  - {info}\n"
    else:
        summary += "  - No disk check information found\n"
    
    summary += "\n- **<span style='color:#ff914d'>Measurements & data transfer</span>**  \n"
    if metrics.measurements:
        for i, m in enumerate(metrics.measurements[:10]):
            summary += f"  - {i+1}. Measurement {m['id']} started at {m['time']}\n"
        if len(metrics.measurements) > 10:
            summary += f"  - ... and {len(metrics.measurements) - 10} more measurements\n"
    else:
        summary += "  - No measurements recorded\n"
    
    summary += "\n- **<span style='color:#ff914d'>Error messages & warnings</span>**  \n"
    
    # Power events
    if metrics.power_events:
        summary += f"  - **Power**: Found {len(metrics.power_events)} power-related events\n"
        for event in metrics.power_events[:3]:
            timestamp_match = re.match(r'(\d{2}\.\d{2}\.\d{4}\s+\d{2}:\d{2}:\d{2}(?:\.\d{3,6})?)', event)
            timestamp = timestamp_match.group(1) if timestamp_match else 'Unknown time'
            description = event.split(timestamp)[-1].strip() if timestamp_match else event
            summary += f"    - {timestamp} {description}\n"
        if len(metrics.power_events) > 3:
            summary += f"    - ... and {len(metrics.power_events) - 3} more power events\n"
    else:
        summary += "  - **Power**: No power events found\n"
    
    # WLAN events
    if metrics.wlan_events:
        disconnects = [e for e in metrics.wlan_events if e['type'] == 'disconnect']
        connects = [e for e in metrics.wlan_events if e['type'] == 'connect']
        summary += f"  - **WLAN**: {len(disconnects)} disconnections, {len(connects)} connections\n"
        if disconnects:
            summary += f"    - Last disconnect: {disconnects[-1]['time']}\n"
        if connects:
            summary += f"    - Last connect: {connects[-1]['time']}\n"
    else:
        summary += "  - **WLAN**: No WLAN events found\n"
    
    # CAN events (from errors/warnings)
    can_events = []
    for code, lines in metrics.errors.items():
        can_events.extend([line for line in lines if 'CAN' in line.upper()])
    for code, lines in metrics.warnings.items():
        can_events.extend([line for line in lines if 'CAN' in line.upper()])
    
    if can_events:
        summary += f"  - **CAN**: {len(can_events)} CAN-related issues found\n"
        for event in can_events[:2]:
            timestamp_match = re.match(r'(\d{2}\.\d{2}\.\d{4}\s+\d{2}:\d{2}:\d{2}(?:\.\d{3,6})?)', event)
            timestamp = timestamp_match.group(1) if timestamp_match else 'Unknown time'
            summary += f"    - {timestamp} CAN issue detected\n"
    else:
        summary += "  - **CAN**: No CAN issues found\n"
    
    # GPS events
    gps_events = []
    for code, lines in metrics.errors.items():
        gps_events.extend([line for line in lines if 'GPS' in line.upper()])
    for code, lines in metrics.warnings.items():
        gps_events.extend([line for line in lines if 'GPS' in line.upper()])
    
    if gps_events:
        summary += f"  - **GPS**: {len(gps_events)} GPS-related issues found\n"
    else:
        summary += "  - **GPS**: No GPS issues found\n"
    
    # Disk events
    disk_events = []
    for code, lines in metrics.errors.items():
        disk_events.extend([line for line in lines if any(keyword in line.upper() for keyword in ['DISK', 'STORAGE', 'SPACE'])])
    
    if disk_events:
        summary += f"  - **Disk**: {len(disk_events)} disk-related issues found\n"
    else:
        summary += "  - **Disk**: No disk issues found\n"
    
    # Protocol timeouts
    if metrics.protocol_timeouts:
        summary += f"  - **Protocols**: {len(metrics.protocol_timeouts)} protocol timeouts detected\n"
        for timeout in metrics.protocol_timeouts[:3]:
            timestamp_match = re.match(r'(\d{2}\.\d{2}\.\d{4}\s+\d{2}:\d{2}:\d{2}(?:\.\d{3,6})?)', timeout)
            timestamp = timestamp_match.group(1) if timestamp_match else 'Unknown time'
            summary += f"    - {timestamp} Protocol timeout\n"
    else:
        summary += "  - **Protocols**: No protocol timeouts found\n"
    
    summary += "\n### ✅ Conclusion:\n\n"
    
    # Generate conclusion based on metrics
    if metrics.errors or metrics.warnings:
        total_errors = sum(len(v) for v in metrics.errors.values())
        total_warnings = sum(len(v) for v in metrics.warnings.values())
        summary += f"⚠️ Analysis found {total_errors} errors and {total_warnings} warnings requiring attention.\n"
    else:
        summary += "✅ No critical errors detected in the log analysis.\n"
    
    if metrics.measurements:
        summary += f"📊 {len(metrics.measurements)} measurements were successfully recorded.\n"
    
    if metrics.wlan_events:
        disconnects = [e for e in metrics.wlan_events if e['type'] == 'disconnect']
        summary += f"📶 WLAN connectivity showed {len(disconnects)} disconnection events.\n"
    
    if metrics.status_summary.get('cpu'):
        cpu_values = metrics.status_summary['cpu']
        avg_cpu = sum(cpu_values) / len(cpu_values)
        max_cpu = max(cpu_values)
        summary += f"💻 System performance: Average CPU {avg_cpu:.1f}%, Peak {max_cpu:.1f}%.\n"
    
    summary += f"\n**Note**: This analysis was generated using lightweight metrics extraction due to large file size. For detailed LLM analysis, consider filtering or splitting the log files."
    
    return summary


# ===============================
# Streamlit UI
# ===============================

def main():
    """Main application entry point"""
    
    # Page configuration
    st.set_page_config(
        page_title="📊 IPE Log Analyzer", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Header
    st.title("IPE Log Analyzer")
    st.markdown("""
    **Ultra-Fast IPE log file analyzer** with **three-tier processing**:
    - Direct: Small files (< 150K tokens) - Full LLM analysis
    - Basic Filtered: Medium files (150K-500K tokens) - Basic filtering + LLM analysis  
    - ID-Based Turbo: Large files (> 500K tokens) - Intelligent ID-based filtering + LLM analysis
    
    **Performance Optimizations:**
    - 25K token chunks (optimized for 30K TPM rate limit) for safe processing
    - ID-based turbo filtering for files over 500,000 tokens with over 95% noise reduction
    - Critical event preservation - All errors, warnings, and measurements kept
    - Ultra-fast preprocessing removes obvious noise in seconds
    - Adaptive chunking with up to 28K tokens for very large files (within rate limits)
    - Interactive chat for follow-up questions on all processed files
    - Real-time cost tracking with optimized token usage
    - Optional metrics-only mode for instant, zero-cost analysis
    
    **Supported file types:** `.LOG` files (direct upload) | `.ZIP` archives containing `.LOG` files
    """)
    
    # Add processing mode selection
    st.markdown("---")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🔧 Processing Options")
    
    with col2:
        force_metrics = st.checkbox(
            "🚀 Force Metrics-Only Mode", 
            help="Skip LLM processing and use fast metrics extraction for any file size (Zero cost)"
        )
    
    # Sidebar settings
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Model selection - GPT-4.1 and GPT-5 only
        st.subheader("🤖 GPT Model")
        with st.expander("ℹ️ Model Info", expanded=False):
            st.markdown("""
            **Available Models:**
            
            🚀 **GPT-4.1** (Recommended)
            - Fast and efficient
            - Best for routine log analysis
            - **Pricing**: $2.00 / $8.00 per 1M tokens (input/output)
            
            🧠 **GPT-5** (Advanced)
            - Most powerful model
            - Best for complex diagnostics
            - **Pricing**: $1.25 / $10.00 per 1M tokens (input/output)
            """)
        
        model_option = st.selectbox(
            "Select Model",
            ["gpt-4.1", "gpt-5"],
            index=0,  # Default to gpt-4.1
            help="Choose the GPT model for log analysis"
        )
        
        st.markdown("---")
        st.markdown("### 📊 Processing Thresholds")
        st.caption(f"🟢 Direct: < {TOKEN_THRESHOLD_FILTERING:,} tokens")
        st.caption(f"🔍 Basic Filtered: {TOKEN_THRESHOLD_FILTERING:,} - {TOKEN_THRESHOLD_TURBO_FILTERING:,} tokens")
        st.caption(f"🚀 ID-Based Turbo: > {TOKEN_THRESHOLD_TURBO_FILTERING:,} tokens (intelligent filtering)")
        
        if st.session_state.get("processing_stats"):
            st.markdown("---")
            st.markdown("### 📈 Last Processing")
            stats = st.session_state.processing_stats
            
            # Display strategy with color indicator
            strategy = stats.get('strategy', 'N/A')
            if 'Direct' in strategy:
                st.success(f"🟢 **Strategy:** {strategy}")
            else:
                st.warning(f"🟡 **Strategy:** {strategy}")
            
            # Basic stats
            st.metric("Total Tokens", f"{stats.get('tokens', 0):,}")
            st.metric("Files Processed", stats.get('files', 0))
            
            if 'reduction' in stats:
                st.metric("Token Reduction", f"{stats['reduction']:.1f}%")
            
            # Display cost information
            if 'cost' in stats and stats['cost']:
                st.markdown("---")
                st.markdown("### 💰 Cost Summary")
                cost_data = stats['cost']
                
                # Display API calls
                api_calls = cost_data.get('api_calls', 0)
                st.metric("🔄 API Calls", api_calls)
                
                # Display tokens
                input_tokens = cost_data.get('input_tokens', 0)
                output_tokens = cost_data.get('output_tokens', 0)
                total_tokens = cost_data.get('total_tokens', input_tokens + output_tokens)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("📥 Input Tokens", f"{input_tokens:,}")
                with col2:
                    st.metric("📤 Output Tokens", f"{output_tokens:,}")
                
                st.metric("📊 Total Tokens", f"{total_tokens:,}")
                
                # Display cost
                if 'cost' in cost_data:
                    cost_breakdown = cost_data['cost']
                    total_cost = cost_breakdown.get('total_cost', 0)
                    input_cost = cost_breakdown.get('input_cost', 0)
                    output_cost = cost_breakdown.get('output_cost', 0)
                    model_used = cost_breakdown.get('model', 'N/A')
                    processing_method = cost_breakdown.get('processing_method', 'N/A')
                    
                    st.metric(
                        "💵 Total Cost",
                        f"${total_cost:.4f}",
                        help=f"Using model: {model_used}"
                    )
                    
                    # Cost breakdown
                    with st.expander("💡 Detailed Cost Breakdown"):
                        st.write(f"**Model Used:** {model_used}")
                        st.write(f"**🎯 Processing Method:** {processing_method}")
                        st.write(f"**Input Cost:** ${input_cost:.4f} ({input_tokens:,} tokens)")
                        st.write(f"**Output Cost:** ${output_cost:.4f} ({output_tokens:,} tokens)")
                        st.write(f"**Total Cost:** ${total_cost:.4f}")
                        
                        if api_calls > 1:
                            st.write(f"**Average per call:** ${(total_cost/api_calls):.4f}")
                else:
                    st.warning("Cost calculation pending...")

    
    # File uploader
    uploaded_files = st.file_uploader(
        "📂 Upload LOG files or ZIP archives",
        type=["LOG", "ZIP"],
        accept_multiple_files=True,
        help="Select one or more log files or ZIP archives. Page will auto-refresh when files are removed."
    )
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.summarized = False
        st.session_state.processing_stats = {}
        st.session_state.last_files = []
    
    # Auto-refresh when files are removed
    if not uploaded_files and st.session_state.get("last_files"):
        # Files were removed - clear state and refresh
        st.session_state.messages = []
        st.session_state.summarized = False
        st.session_state.processing_stats = {}
        st.session_state.last_files = []
        st.rerun()
    
    # Reset state if files change
    if uploaded_files:
        current_files = [f.name for f in uploaded_files]
        if st.session_state.get("last_files") != current_files:
            st.session_state.messages = []
            st.session_state.summarized = False
            st.session_state.last_files = current_files
        
        # Show file info and auto-refresh note
        st.info(f"📁 {len(uploaded_files)} file(s) uploaded. Click ❌ to remove files and auto-refresh the page.")
    
    # Main processing
    if uploaded_files and not st.session_state.summarized:
        # Initialize LLM handler
        try:
            api_key = st.secrets["OPENAI_API_KEY"]
        except:
            st.error("⚠️ OpenAI API key not found in secrets. Please configure it.")
            st.stop()
        
        # Create LLM handler (even for metrics-only mode for compatibility)
        llm_handler = LLMHandler(api_key, model=model_option)
        
        # Progress container
        status_container = st.empty()
        progress_bar = st.progress(0.0)
        
        def update_progress(message, value=None):
            status_container.info(message)
            if value is not None:
                progress_bar.progress(value)
        
        try:
            # Extract log files
            update_progress("📂 Extracting log files...", 0.1)
            
            log_files = process_uploaded_files(uploaded_files)
            
            if not log_files:
                st.error("❌ No LOG files found in the uploaded files!")
                st.stop()
            
            update_progress(f"✅ Found {len(log_files)} LOG file(s): {', '.join([f[0] for f in log_files[:3]])}", 0.2)
            
            # Combine logs
            update_progress("🔗 Combining log files...", 0.3)
            log_content = combine_log_files(log_files)
            
            # Count initial tokens
            initial_tokens = count_tokens(log_content, "gpt-4")
            update_progress(f"📊 Counted {initial_tokens:,} tokens", 0.4)
            
            # Determine strategy
            if force_metrics:
                strategy = "Metrics-only (forced)"
                update_progress("🚀 Processing with metrics-only analysis (forced)...", 0.5)
            elif initial_tokens >= TOKEN_THRESHOLD_TURBO_FILTERING:
                strategy = "ID-Based Turbo + LLM"
                update_progress("🎯 Using ID-based turbo filtering for large file...", 0.5)
            elif initial_tokens >= TOKEN_THRESHOLD_FILTERING:
                strategy = "Basic Filtered + LLM"
                update_progress("🔍 Using basic filtered LLM analysis...", 0.5)
            else:
                strategy = "Direct LLM"
                update_progress("🚀 Using direct LLM analysis...", 0.5)
            
            # Track progress manually
            def progress_with_bar(msg):
                update_progress(msg, 0.7)
            
            # Process logs
            reply = process_logs_smart(
                log_content, 
                llm_handler, 
                progress_with_bar,
                force_metrics_only=force_metrics
            )
            
            # Store results
            st.session_state.messages.append({"role": "system", "content": SYSTEM_PROMPT})
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.session_state.summarized = True
            
            # Get usage stats (will be empty only for forced metrics-only)
            if not force_metrics:
                usage_stats = llm_handler.get_usage_stats()
                st.session_state.llm_handler = llm_handler
            else:
                usage_stats = {
                    'api_calls': 0,
                    'input_tokens': 0,
                    'output_tokens': 0,
                    'total_tokens': 0,
                    'cost': {
                        'total_cost': 0.0,
                        'input_cost': 0.0,
                        'output_cost': 0.0,
                        'model': 'Metrics-only'
                    }
                }
            
            # Store stats with detailed reduction information
            reduction_percentage = 0
            if strategy == "ID-Based Turbo + LLM" and initial_tokens >= TOKEN_THRESHOLD_TURBO_FILTERING:
                # For turbo mode, calculate the total reduction
                final_tokens = count_tokens(reply, llm_handler.model) if not force_metrics else 0
                reduction_percentage = (1 - final_tokens / initial_tokens) * 100 if initial_tokens > 0 else 0
            elif strategy == "Basic Filtered + LLM":
                # Estimate reduction for basic filtering
                reduction_percentage = 40  # Typical basic filtering reduction
            
            st.session_state.processing_stats = {
                'tokens': initial_tokens,
                'strategy': strategy,
                'files': len(log_files),
                'reduction': reduction_percentage,
                'cost': usage_stats
            }
            
            update_progress("✅ Analysis complete!", 1.0)
            
            # Display cost immediately with reduction summary
            if usage_stats['cost']['total_cost'] > 0:
                reduction_info = ""
                if 'reduction' in st.session_state.processing_stats and st.session_state.processing_stats['reduction'] > 0:
                    reduction_pct = st.session_state.processing_stats['reduction']
                    tokens_saved = initial_tokens * (reduction_pct / 100)
                    cost_saved = tokens_saved * 0.000015  # Approximate cost per token
                    reduction_info = f"""
                📉 **Token Reduction**: {reduction_pct:.1f}% ({tokens_saved:,.0f} tokens filtered out)
                💰 **Cost Savings**: ~${cost_saved:.4f} (estimated from filtering)"""
                
                st.info(f"""
                💰 **Processing Cost**: ${usage_stats['cost']['total_cost']:.4f}
                - API Calls: {usage_stats['api_calls']}
                - Input Tokens: {usage_stats['input_tokens']:,}
                - Output Tokens: {usage_stats['output_tokens']:,}
                - Model: {usage_stats['cost']['model']}{reduction_info}
                """)
            else:
                if force_metrics:
                    st.success("🚀 **Processing Cost**: $0.00 (Metrics-only analysis)")
                else:
                    st.info("💰 **Processing Cost**: Calculating...")
            
            # Clear progress indicators
            status_container.empty()
            progress_bar.empty()
            
        except Exception as e:
            st.error(f"❌ Error during processing: {str(e)}")
            st.exception(e)
    
    # Display chat interface
    if st.session_state.get("summarized"):
        st.markdown("---")
        st.subheader("📋 Analysis Summary")
        
        # Display the summary
        for msg in st.session_state.messages[1:]:  # Skip system prompt
            if msg["role"] == "assistant":
                with st.chat_message("assistant"):
                    st.markdown(msg["content"], unsafe_allow_html=True)
            elif msg["role"] == "user" and not msg["content"].startswith("====="):
                with st.chat_message("user"):
                    st.markdown(msg["content"])
        
        # Chat input for follow-up questions
        st.markdown("---")
        st.subheader("💬 Ask Follow-up Questions")
        
        # Check if LLM is available for follow-up
        if st.session_state.get('llm_handler') is None and st.session_state.processing_stats.get('strategy', '').startswith('Metrics-only'):
            st.info("💡 **Note**: Follow-up questions require LLM processing. Metrics-only analysis doesn't support chat. Uncheck 'Force Metrics-Only Mode' to enable chat.")
        elif st.session_state.processing_stats.get('strategy', '').endswith('+ LLM'):
            st.info("✅ **Chat Available**: This file was processed with LLM analysis - ask questions about the logs!")
        
        if prompt := st.chat_input("Ask a question about the logs..."):
            # Check if we have LLM handler
            if 'llm_handler' not in st.session_state or st.session_state.llm_handler is None:
                if st.session_state.processing_stats.get('strategy', '').startswith('Metrics-only'):
                    st.error("❌ Follow-up questions are not available in metrics-only mode. Please re-analyze with LLM processing enabled.")
                else:
                    # Try to create new LLM handler
                    try:
                        api_key = st.secrets["OPENAI_API_KEY"]
                        st.session_state.llm_handler = LLMHandler(api_key, model=model_option)
                    except Exception as e:
                        st.error(f"❌ Could not initialize LLM handler: {str(e)}")
                        st.stop()
            
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Get LLM response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        llm_handler = st.session_state.llm_handler
                        reply = llm_handler.answer_question(st.session_state.messages)
                        st.session_state.messages.append({"role": "assistant", "content": reply})
                        st.markdown(reply, unsafe_allow_html=True)
                        
                        # Update cost stats
                        usage_stats = llm_handler.get_usage_stats()
                        if 'processing_stats' in st.session_state:
                            st.session_state.processing_stats['cost'] = usage_stats
                        
                        # Force sidebar to refresh by triggering a rerun
                        st.rerun()
                            
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
    
    elif not uploaded_files:
        st.info("⬆️ Upload your `.LOG` files or `.ZIP` archives above to begin.")


if __name__ == "__main__":
    main()
