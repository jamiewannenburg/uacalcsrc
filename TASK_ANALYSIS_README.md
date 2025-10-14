# Task Analysis Automation

This directory contains scripts to automatically analyze and update all 85 UACalc translation task files with implementation recommendations.

## Overview

The analysis system provides two approaches:

1. **Simple Analysis** (`analyze_tasks_simple.py`) - No authentication required, provides basic analysis and recommendations
2. **Cursor-Agent Analysis** (`analyze_tasks.py`) - Uses cursor-agent for advanced AI-powered analysis (requires authentication)

## Quick Start

### Option 1: Simple Analysis (Recommended for immediate use)

```bash
# Analyze all tasks
python3 run_full_analysis.py

# Analyze specific tasks
python3 run_full_analysis.py --task-filter "Task 1"

# Custom output directory
python3 run_full_analysis.py --output-dir "my_analysis"
```

### Option 2: Cursor-Agent Analysis (Advanced)

```bash
# First, setup authentication
python3 run_full_analysis.py --setup-auth

# Then run analysis with cursor-agent
python3 run_full_analysis.py --use-cursor-agent

# Parallel processing
python3 run_full_analysis.py --use-cursor-agent --parallel 4
```

## Scripts Overview

### 1. `run_full_analysis.py` - Main Runner
- **Purpose**: Orchestrates the analysis process
- **Features**: 
  - Choose between simple or cursor-agent analysis
  - Handle authentication setup
  - Parallel processing options
  - Task filtering

### 2. `analyze_tasks_simple.py` - Simple Analyzer
- **Purpose**: Basic analysis without authentication
- **Features**:
  - Parses task files and Java files
  - Generates implementation recommendations
  - Creates detailed reports
  - No external dependencies

### 3. `analyze_tasks.py` - Cursor-Agent Analyzer
- **Purpose**: Advanced AI-powered analysis using Cursor CLI headless mode
- **Features**:
  - Uses cursor-agent with proper headless syntax (`-p`, `--force`, `--output-format json`)
  - Provides context file (IMPLEMENTATION_PATTERNS.md) to agent
  - Updates task files directly
  - Deep dependency analysis from scratch (doesn't trust existing dependency lists)
  - Usage pattern detection across entire codebase
  - Returns structured JSON output with analysis results

## Analysis Features

### What Each Analysis Provides

1. **Task File Parsing**
   - Extracts Java file paths
   - Identifies dependencies
   - Checks completion status

2. **Java File Analysis**
   - Class type detection (interface/abstract/concrete)
   - Method counting and complexity
   - Import analysis
   - File structure analysis

3. **Implementation Recommendations**
   - Rust construct suggestions (struct/trait/enum)
   - Dispatch strategy (generic/dynamic)
   - Java wrapper suitability
   - Testing strategy recommendations
   - Priority assessment

4. **Dependency Analysis**
   - Cross-references with other tasks
   - Verifies dependency ordering
   - Identifies missing dependencies

5. **Usage Pattern Analysis**
   - Searches codebase for class usage
   - Identifies common patterns
   - Determines instantiation vs abstraction

### For Completed Tasks
- Verifies implementation against criteria
- Checks if all dependencies are listed
- Validates Rust implementation exists
- Confirms Java wrapper is testable
- Unchecks boxes if criteria not met

## Output

### Simple Analysis Output
- **Location**: `analysis_output/` directory
- **Files**: 
  - `report_Task X - ClassName.md` - Individual task reports
  - `analysis_summary.json` - Complete analysis data
  - `task_analysis_simple.log` - Processing log

### Cursor-Agent Analysis Output
- **Location**: Modified task files in place
- **Files**:
  - Updated task files with recommendations
  - `task_analysis_results.json` - Processing results
  - `task_analysis.log` - Processing log

## Usage Examples

### Analyze All Tasks (Simple)
```bash
python3 run_full_analysis.py
```

### Analyze Specific Tasks
```bash
# Single task
python3 run_full_analysis.py --task-filter "Task 1"

# Multiple tasks with pattern
python3 run_full_analysis.py --task-filter "Operation"
```

### Advanced Cursor-Agent Analysis
```bash
# Setup authentication first
python3 run_full_analysis.py --setup-auth

# Run with batched parallel processing (default: 3 workers per batch)
python3 run_full_analysis.py --use-cursor-agent

# Run with custom parallel processing
python3 run_full_analysis.py --use-cursor-agent --parallel 4

# Analyze specific tasks with cursor-agent
python3 run_full_analysis.py --use-cursor-agent --task-filter "Task 1"
```

### Custom Output Directory
```bash
python3 run_full_analysis.py --output-dir "my_custom_analysis"
```

## Authentication Setup for Cursor-Agent

If you want to use the advanced cursor-agent analysis:

1. **Install cursor-agent** (if not already done):
   ```bash
   curl https://cursor.com/install -fsS | bash
   ```

2. **Setup authentication**:
   ```bash
   python3 run_full_analysis.py --setup-auth
   ```

3. **Run analysis**:
   ```bash
   python3 run_full_analysis.py --use-cursor-agent
   ```

## Cursor-Agent Headless Mode

The script uses Cursor CLI's headless mode with the following syntax:

```bash
cursor-agent -p --force --output-format json "prompt with file paths and context"
```

**Key flags:**
- `-p`: Enable print mode for non-interactive execution
- `--force`: Allow file modifications without confirmation
- `--output-format json`: Return structured JSON output

**Important**: The prompt includes file paths and context information since cursor-agent doesn't have separate `--context` or `--file` flags.

The agent performs deep analysis including:
- **Dependency verification**: Analyzes from scratch, doesn't trust existing dependency lists
- **Codebase-wide search**: Finds actual usage patterns across all files
- **Implementation recommendations**: Provides detailed Rust translation guidance
- **Task file updates**: Modifies task files with findings and recommendations
- **Structured output**: Returns JSON with analysis results and success status

## Batched Parallel Processing

The script processes tasks in batches to optimize performance and system resources:

- **Default**: 3 parallel workers per batch
- **Batching**: Tasks are processed in groups to avoid overwhelming the system
- **Progress tracking**: Each batch completion is logged with success/failure counts
- **Inter-batch delay**: 2-second pause between batches to prevent system overload
- **Configurable**: Use `--parallel N` to set custom batch size

**Example with 85 tasks and 3 workers per batch:**
- Batch 1: Tasks 1-3 (parallel)
- Batch 2: Tasks 4-6 (parallel)
- ...
- Batch 29: Task 85 (single task)

This approach provides good performance while maintaining system stability.

## Troubleshooting

### cursor-agent Authentication Issues
- Run `~/.local/bin/cursor-agent status` to check authentication
- Use `~/.local/bin/cursor-agent login` to authenticate manually
- Ensure you have a Cursor account and API access

### Simple Analysis Issues
- Check that all required files exist:
  - `tasks/` directory with task files
  - `org/` directory with Java files
  - `IMPLEMENTATION_PATTERNS.md`
- Verify Python 3 is installed
- Check file permissions

### General Issues
- Check logs in `task_analysis.log` or `task_analysis_simple.log`
- Ensure project root path is correct
- Verify all task files are readable

## File Structure

```
/home/jamie/Documents/uacalcsrc/
├── analyze_tasks.py              # Cursor-agent analyzer
├── analyze_tasks_simple.py      # Simple analyzer
├── run_full_analysis.py         # Main runner script
├── TASK_ANALYSIS_README.md      # This file
├── tasks/                       # Task files to analyze
│   ├── Task 1 - OperationSymbol.md
│   ├── Task 2 - SimilarityType.md
│   └── ...
├── org/                         # Java source files
│   └── uacalc/
└── IMPLEMENTATION_PATTERNS.md  # Implementation guidelines
```

## Next Steps

After running the analysis:

1. **Review Reports**: Check the generated analysis reports
2. **Update Task Files**: For cursor-agent analysis, task files are updated automatically
3. **Implement Recommendations**: Follow the implementation suggestions
4. **Verify Dependencies**: Ensure all dependencies are correctly listed
5. **Test Implementations**: Use the recommended testing strategies

## Support

For issues or questions:
- Check the log files for detailed error messages
- Verify all required files and directories exist
- Ensure proper authentication for cursor-agent analysis
- Review the implementation patterns document for guidance
