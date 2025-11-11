# 🏗️ Architecture Overview - LogFileAnalyzerV2

## Quick Reference for Developers

This document provides a high-level overview of the LogFileAnalyzerV2 architecture for developers who need to quickly understand the system structure.

## 📁 Project Structure

```
LogFileAnalyzerV2/
├── 🎯 Core Application Files
│   ├── st_loganalyzer_v3.py      # Main Streamlit app (UI + orchestration)
│   ├── log_processor.py          # Log processing engine
│   ├── llm_handler.py            # OpenAI API integration
│   └── log_file_reader.py        # Legacy file utilities
│
├── 🔧 Configuration
│   ├── requirements.txt          # Python dependencies
│   ├── .streamlit/
│   │   ├── config.toml           # UI configuration
│   │   ├── secrets.toml          # API keys (not in repo)
│   │   └── Ids.txt               # IPE message ID mappings
│   ├── .env.example              # Environment template
│   └── packages.txt              # System packages (empty)
│
├── 📚 Documentation
│   ├── README.md                 # User guide & setup
│   ├── DESIGN_DOCUMENT.md        # Detailed architecture
│   └── ARCHITECTURE_OVERVIEW.md  # This file
│
└── 🔐 Security
    ├── .gitignore                # Exclude sensitive files
    └── .gitattributes            # Git settings
```

## 🔄 Application Flow

### 1. Entry Point
**File**: `st_loganalyzer_v3.py`
**Function**: `main()`

```python
def main():
    # 1. Initialize Streamlit UI
    # 2. Handle file uploads (.LOG/.ZIP)
    # 3. Route to processing strategy
    # 4. Display results + chat interface
```

### 2. Processing Router
**Function**: `process_logs_smart()`

```python
def process_logs_smart(log_content, llm_handler, progress_callback, force_metrics_only):
    tokens = count_tokens(log_content)
    
    if force_metrics_only:
        return process_with_metrics_only()
    elif tokens < 150K:
        return direct_llm_processing()
    elif tokens < 500K:
        return basic_filtered_processing()
    else:
        return smart_filtered_processing()
```

### 3. Processing Strategies

| Strategy | Token Range | Description | Cost |
|----------|-------------|-------------|------|
| **Direct** | < 150K | Single LLM call | Low |
| **Basic Filtered** | 150K-500K | Remove routine logs + LLM | Medium |
| **Smart Filtered** | > 500K | AI noise reduction + LLM | Optimized |
| **Metrics Only** | Any size | Extract key data only | $0 |

## 🧩 Module Breakdown

### `st_loganalyzer_v3.py` - Main Application
**Role**: UI Controller & Orchestrator

**Key Responsibilities**:
- Streamlit UI management
- File upload handling (.LOG and .ZIP)
- Progress tracking and user feedback
- Session state management
- Cost display and tracking

**Important Functions**:
```python
main()                          # Application entry point
process_uploaded_files()        # Handle file uploads
extract_logs_from_zip()        # ZIP file processing
combine_log_files()            # Merge multiple logs
process_logs_smart()           # Processing strategy router
```

### `log_processor.py` - Processing Engine  
**Role**: Core Log Processing Logic

**Key Responsibilities**:
- Token counting and text chunking
- Content filtering (basic and smart)
- Metrics extraction without LLM
- Cost calculation
- IPE message ID interpretation

**Key Classes**:
```python
class LogMetrics:               # Data structure for extracted metrics
    software_version: str
    hardware_type: str
    measurements: List[Dict]
    errors: Dict[str, List]
    # ... more fields
```

**Key Functions**:
```python
count_tokens()                  # Token counting for GPT models
create_smart_filtered_content() # Advanced noise reduction
extract_key_metrics()          # Zero-cost metrics extraction
calculate_cost()               # OpenAI pricing calculation
```

### `llm_handler.py` - API Integration
**Role**: OpenAI API Management

**Key Responsibilities**:
- OpenAI API calls with error handling
- Token usage tracking
- Cost monitoring
- Response processing

**Main Class**:
```python
class LLMHandler:
    def __init__(api_key, model="gpt-4.1")
    def summarize_chunk()       # Process log chunks
    def combine_summaries()     # Merge chunk results
    def generate_summary()      # Single-pass processing
    def answer_question()       # Chat functionality
    def get_usage_stats()       # Cost and usage data
```

## 🎯 Smart Filtering Algorithm

The smart filtering removes 60-70% of routine noise while preserving critical events:

### ✅ Always Keep
- **Errors**: Lines with `E 0x` pattern
- **Warnings**: Critical timeouts and failures
- **Measurements**: Start/stop events with measurement IDs
- **WLAN Events**: Connection/disconnection events
- **System Events**: Startup, shutdown, configuration changes
- **Disk Issues**: Space warnings, CheckDisk operations

### ❌ Filter Out
- **Routine Updates**: Regular time synchronization
- **Status Spam**: Normal CPU usage reports
- **Network Stats**: Interface statistics
- **Successful Operations**: Routine email notifications
- **SFTP Details**: Verbose transfer logs (keep summaries)

### 🎛️ Smart Sampling
- **Status Messages**: Keep only high CPU (>80%) or every 30 minutes
- **Disk Space**: Keep only when < 10% free or < 50GB
- **Email Events**: Keep failures, skip routine success

## 💰 Cost Management

### Model Pricing (per 1M tokens)
```python
PRICING = {
    'gpt-4.1': {'input': $1.50, 'output': $6.00},   # Recommended
    'gpt-5':   {'input': $5.00, 'output': $15.00}   # Advanced
}
```

### Cost Optimization Strategies
1. **Tier Selection**: Automatic based on file size
2. **Smart Filtering**: 60-70% token reduction
3. **Chunking**: 25K tokens/chunk (under 30K TPM limit)
4. **Real-time Tracking**: Display costs as they accumulate
5. **Metrics-Only Option**: Zero-cost analysis

## 🔐 Security Architecture

### API Key Management
```toml
# .streamlit/secrets.toml (production)
OPENAI_API_KEY = "sk-proj-..."

# .env (development)
OPENAI_API_KEY=sk-proj-...
```

### Security Best Practices
- ✅ API keys in secrets/environment only
- ✅ `.gitignore` protects sensitive files
- ✅ No secrets in source code
- ✅ Streamlit Cloud secure deployment
- ❌ Never commit API keys to version control

## 🚀 Deployment

### Streamlit Cloud Setup
1. **Push code** to GitHub (without secrets)
2. **Connect repository** to Streamlit Cloud
3. **Add secrets** in Streamlit Cloud dashboard
4. **Deploy** automatically

### Environment Variables
```bash
# Required
OPENAI_API_KEY=sk-proj-...

# Optional
DEFAULT_MODEL=gpt-4.1
```

## 🔧 Development Workflow

### Local Development
```bash
# 1. Clone repository
git clone https://github.com/shivendra-shrivastav/LogFileAnalyzerV2.git

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure API key
cp .env.example .env
# Edit .env with your OpenAI API key

# 5. Run application
streamlit run st_loganalyzer_v3.py
```

### Adding New Features

#### New Processing Strategy
1. Add logic to `process_logs_smart()` in `st_loganalyzer_v3.py`
2. Implement processing function in `log_processor.py`
3. Update UI thresholds and descriptions

#### New Model Support
1. Add model to `PRICING` dict in `log_processor.py`
2. Update model selection in `st_loganalyzer_v3.py`
3. Test with `LLMHandler` class

#### New Filter Algorithm
1. Create function in `log_processor.py`
2. Integrate with `process_logs_smart()`
3. Add UI toggle if needed

## 🐛 Common Development Issues

### Issue: "Module not found"
**Solution**: Ensure virtual environment is activated and dependencies installed
```bash
pip install -r requirements.txt
```

### Issue: "OpenAI API key not found"
**Solution**: Check secrets/environment configuration
```bash
# Check .env file or .streamlit/secrets.toml
```

### Issue: "Rate limit exceeded"
**Solution**: Reduce chunk size or add delays
```python
# In log_processor.py
MAX_TOKENS_PER_CHUNK = 20000  # Reduce from 25000
```

### Issue: "Large file processing fails"
**Solution**: Increase filtering aggressiveness or use metrics-only mode

## 📊 Performance Benchmarks

| File Size | Tokens | Strategy | Processing Time | Typical Cost |
|-----------|--------|----------|-----------------|--------------|
| Small | < 150K | Direct | 5-15 sec | $0.10-0.30 |
| Medium | 150K-500K | Basic Filter | 30-60 sec | $0.20-0.80 |
| Large | > 500K | Smart Filter | 60-180 sec | $0.50-2.00 |
| Any | Any | Metrics Only | < 5 sec | $0.00 |

## 🔮 Extension Points

### Easy to Add
- ✅ New GPT models (update pricing dict)
- ✅ Additional filtering algorithms
- ✅ New metrics extraction rules
- ✅ UI themes and styling

### Moderate Effort
- 🔶 Other LLM providers (Claude, Gemini)
- 🔶 Database integration for log storage
- 🔶 Batch processing capabilities
- 🔶 Advanced analytics and reporting

### Complex Changes
- 🔴 Real-time log streaming
- 🔴 Multi-user authentication
- 🔴 Distributed processing
- 🔴 Custom model training

---

## 🎯 Quick Start for Developers

1. **Read this overview** (you're here! ✅)
2. **Review** `st_loganalyzer_v3.py` main function
3. **Understand** processing strategies in `process_logs_smart()`
4. **Examine** filtering logic in `log_processor.py`
5. **Check** API integration in `llm_handler.py`
6. **Set up** local development environment
7. **Run** with sample log files
8. **Refer to** DESIGN_DOCUMENT.md for deep details

---

**Last Updated**: October 2025  
**Quick Reference**: Always available for developer onboarding