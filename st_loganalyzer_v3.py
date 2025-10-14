"""
IPE Log Analyzer - Main Application
------------------------------------
Streamlit UI for IPE log file analysis with TWO-TIER processing strategy.

This version uses:
- Modular architecture (UI separated from processing)
- Two-tier processing: Direct (< 150K) and Filtered (>= 150K tokens)
- Intelligent chunking for large files
- Token-aware processing with GPT-4.1 and GPT-5
"""

import streamlit as st
import os
import zipfile
from typing import List, Tuple

# Import our custom modules
from log_processor import (
    count_tokens,
    chunk_text_by_tokens,
    filter_log_content
)
from llm_handler import LLMHandler


# ===============================
# Configuration and Constants
# ===============================

SYSTEM_PROMPT = """
You are LogInsightGPT, an assistant specialized in analyzing and summarizing diagnostic and runtime logs from IPETRONIK's IPEmotionRT system (e.g., version 2024 R3.2 or 2025 R2.65794), running on logger types like IPE833 or IPE853.

Your task is to interpret provided internal log files (.LOG) and generate a structured summary following the format exactly as below:

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
  - **Power**: [timestamp] [Description]
  - **WLAN**: [timestamp] [Description]
  - **CAN**: [timestamp] [Description]
  - **GPS**: [timestamp] [Description]
  - **Disk**: [timestamp] [Description]
  - **Protocols**: [timestamp] [Description]

### ✅ Conclusion:

Summarize key takeaways using emojis.

Notes:
- Use only the information inside the logs.
- Maintain professional tone, consistent formatting, and structured section headings.
"""

# Token limits for TWO-TIER processing strategy
TOKEN_THRESHOLD_FILTERING = 150000  # Use filtering at or above this threshold
MAX_TOKENS_PER_CHUNK = 25000         # Max tokens per chunk (safe for 30K TPM rate limit)
# Note: Set to 25K to stay well under the 30K tokens/minute rate limit for gpt-4.1


# ===============================
# File Processing Functions
# ===============================

def extract_logs_from_zip(zip_file) -> List[Tuple[str, str]]:
    """
    Extract all .LOG files from a ZIP archive.
    
    Args:
        zip_file: Uploaded ZIP file object from Streamlit
        
    Returns:
        List of tuples: (filename, file_content)
    """
    log_files = []
    try:
        with zipfile.ZipFile(zip_file) as z:
            for file_info in z.infolist():
                if file_info.filename.upper().endswith(".LOG") and not file_info.is_dir():
                    with z.open(file_info) as f:
                        text = f.read().decode("utf-8", errors="ignore")
                        display_name = os.path.basename(file_info.filename)
                        log_files.append((display_name, text))
    except zipfile.BadZipFile:
        st.error(f"Error: {zip_file.name} is not a valid ZIP file.")
    except Exception as e:
        st.error(f"Error reading ZIP file {zip_file.name}: {str(e)}")
    
    return log_files


def process_uploaded_files(uploaded_files) -> List[Tuple[str, str]]:
    """
    Process both LOG and ZIP files to extract log content.
    
    Args:
        uploaded_files: List of uploaded files from Streamlit uploader
        
    Returns:
        List of tuples: (filename, file_content)
    """
    all_log_files = []
    
    for uploaded_file in uploaded_files:
        file_extension = uploaded_file.name.upper().split('.')[-1]
        
        if file_extension == 'LOG':
            try:
                file_text = uploaded_file.read().decode("utf-8", errors="ignore")
                all_log_files.append((uploaded_file.name, file_text))
            except Exception as e:
                st.error(f"Error reading LOG file {uploaded_file.name}: {str(e)}")
                
        elif file_extension == 'ZIP':
            log_files_from_zip = extract_logs_from_zip(uploaded_file)
            if log_files_from_zip:
                all_log_files.extend(log_files_from_zip)
            else:
                st.warning(f"No LOG files found in ZIP archive: {uploaded_file.name}")
        else:
            st.warning(f"Unsupported file type: {uploaded_file.name}")
    
    return all_log_files


def combine_log_files(log_files: List[Tuple[str, str]]) -> str:
    """
    Combine multiple log files into a single content string.
    
    Args:
        log_files: List of tuples (filename, file_content)
        
    Returns:
        Combined log content for LLM input
    """
    content = ""
    for filename, file_text in log_files:
        content += f"\n\n===== START OF FILE: {filename} =====\n"
        content += file_text
        content += f"\n===== END OF FILE: {filename} =====\n"
    return content


# ===============================
# Core Processing Logic
# ===============================

def process_logs_smart(
    log_content: str, 
    llm_handler: LLMHandler,
    progress_callback=None
) -> str:
    """
    Intelligently process logs based on size - TWO TIER APPROACH.
    
    Args:
        log_content: Combined log content
        llm_handler: LLM handler instance
        progress_callback: Optional callback for progress updates
        
    Returns:
        Final summary
    """
    # Count tokens
    total_tokens = count_tokens(log_content, llm_handler.model)
    
    if progress_callback:
        progress_callback(f"📊 Total tokens: {total_tokens:,}")
    
    # Strategy 1: Direct processing (< 150K tokens)
    if total_tokens < TOKEN_THRESHOLD_FILTERING:
        if progress_callback:
            progress_callback("✅ Processing directly (file size optimal)")
        
        # Check if it still exceeds rate limit
        if total_tokens > MAX_TOKENS_PER_CHUNK:
            if progress_callback:
                progress_callback("⚠️ File exceeds rate limit, using chunking...")
            return process_with_chunking(log_content, llm_handler, progress_callback)
        
        return llm_handler.generate_summary(log_content, SYSTEM_PROMPT)
    
    # Strategy 2: Filtered processing (>= 150K tokens)
    else:
        if progress_callback:
            progress_callback("⚙️ Applying content filtering...")
        
        filtered_content = filter_log_content(log_content, keep_critical=True)
        filtered_tokens = count_tokens(filtered_content, llm_handler.model)
        
        if progress_callback:
            reduction = (1 - filtered_tokens / total_tokens) * 100
            progress_callback(f"✅ Reduced by {reduction:.1f}% ({total_tokens:,} → {filtered_tokens:,} tokens)")
        
        # If still too large after filtering, chunk it
        if filtered_tokens > MAX_TOKENS_PER_CHUNK:
            if progress_callback:
                progress_callback("📦 Content exceeds rate limit, using chunking...")
            return process_with_chunking(filtered_content, llm_handler, progress_callback)
        else:
            return llm_handler.generate_summary(filtered_content, SYSTEM_PROMPT)


def process_with_chunking(
    content: str,
    llm_handler: LLMHandler,
    progress_callback=None
) -> str:
    """
    Process content using chunking and hierarchical summarization.
    
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
    
    # Summarize each chunk
    chunk_summaries = []
    for i, chunk in enumerate(chunks):
        if progress_callback:
            progress_callback(f"Processing chunk {i+1}/{len(chunks)}...")
        
        summary = llm_handler.summarize_chunk(
            chunk, SYSTEM_PROMPT, i+1, len(chunks)
        )
        chunk_summaries.append(summary)
    
    # Combine summaries
    if progress_callback:
        progress_callback("🔄 Combining chunk summaries...")
    
    final_summary = llm_handler.combine_summaries(chunk_summaries, SYSTEM_PROMPT)
    return final_summary


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
    st.title("🛠️ IPE Log Analyzer")
    st.markdown("""
    Welcome to the **IPE Log Analyzer**! Upload one or more `.LOG` files or `.ZIP` archives 
    containing LOG files from your IPEmotionRT logger.
    
    **Features:**
    - 🚀 Two-tier smart processing based on file size
    - 📊 Handles files of any size efficiently
    - 🔍 Automatic filtering for large files
    - 💬 Interactive chat for follow-up questions
    - 💰 Real-time cost tracking
    
    **Supported file types:** `.LOG` files (direct upload) | `.ZIP` archives containing `.LOG` files
    """)
    
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
            - **Pricing**: $1.50 / $6.00 per 1M tokens (input/output)
            
            🧠 **GPT-5** (Advanced)
            - Most powerful model
            - Best for complex diagnostics
            - **Pricing**: $5.00 / $15.00 per 1M tokens (input/output)
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
        st.caption(f"🟡 Filtered: ≥ {TOKEN_THRESHOLD_FILTERING:,} tokens")
        
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
                    
                    st.metric(
                        "💵 Total Cost",
                        f"${total_cost:.4f}",
                        help=f"Using model: {model_used}"
                    )
                    
                    # Cost breakdown
                    with st.expander("💡 Detailed Cost Breakdown"):
                        st.write(f"**Model Used:** {model_used}")
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
        help="Select one or more log files or ZIP archives"
    )
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.summarized = False
        st.session_state.processing_stats = {}
    
    # Reset state if files change
    if uploaded_files:
        current_files = [f.name for f in uploaded_files]
        if st.session_state.get("last_files") != current_files:
            st.session_state.messages = []
            st.session_state.summarized = False
            st.session_state.last_files = current_files
    
    # Main processing
    if uploaded_files and not st.session_state.summarized:
        # Initialize LLM handler
        try:
            api_key = st.secrets["OPENAI_API_KEY"]
        except:
            st.error("⚠️ OpenAI API key not found in secrets. Please configure it.")
            st.stop()
        
        llm_handler = LLMHandler(api_key, model=model_option)
        
        # Progress container
        status_container = st.empty()
        progress_bar = st.progress(0.0)
        
        def update_progress(message):
            status_container.info(message)
        
        try:
            # Extract log files
            update_progress("📂 Extracting log files...")
            progress_bar.progress(0.1)
            
            log_files = process_uploaded_files(uploaded_files)
            
            if not log_files:
                st.error("❌ No LOG files found in the uploaded files!")
                st.stop()
            
            update_progress(f"✅ Found {len(log_files)} LOG file(s): {', '.join([f[0] for f in log_files[:3]])}")
            progress_bar.progress(0.2)
            
            # Combine logs
            update_progress("🔗 Combining log files...")
            log_content = combine_log_files(log_files)
            progress_bar.progress(0.3)
            
            # Process logs
            update_progress("🤖 Analyzing logs...")
            progress_bar.progress(0.4)
            
            # Track stats
            initial_tokens = count_tokens(log_content, "gpt-4")
            
            # Track progress manually
            current_progress = [40]  # Use list to allow modification in nested function
            
            def progress_with_bar(msg):
                update_progress(msg)
                current_progress[0] = min(90, current_progress[0] + 5)
                progress_bar.progress(current_progress[0] / 100)
            
            reply = process_logs_smart(log_content, llm_handler, progress_with_bar)
            
            # Store LLM handler for follow-up questions
            st.session_state.llm_handler = llm_handler
            
            # Store results
            st.session_state.messages.append({"role": "system", "content": SYSTEM_PROMPT})
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.session_state.summarized = True
            
            # Get usage stats from LLM handler
            usage_stats = llm_handler.get_usage_stats()
            
            # Store stats with cost information
            st.session_state.processing_stats = {
                'tokens': initial_tokens,
                'strategy': 'Optimized',
                'files': len(log_files),
                'cost': usage_stats
            }
            
            progress_bar.progress(1.0)
            status_container.success("✅ Log analysis complete!")
            
            # Display cost immediately
            st.info(f"""
            💰 **Processing Cost:** ${usage_stats['cost']['total_cost']:.4f}
            - API Calls: {usage_stats['api_calls']}
            - Input Tokens: {usage_stats['input_tokens']:,}
            - Output Tokens: {usage_stats['output_tokens']:,}
            - Model: {usage_stats['cost']['model']}
            """)
            
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
        
        if prompt := st.chat_input("Ask a question about the logs..."):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Get LLM response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        api_key = st.secrets["OPENAI_API_KEY"]
                        
                        # Reuse existing llm_handler if available in session state
                        if 'llm_handler' not in st.session_state:
                            st.session_state.llm_handler = LLMHandler(api_key, model=model_option)
                        
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
