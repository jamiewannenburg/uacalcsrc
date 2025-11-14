# Java Dependency Graph Generator for UACalc

This tool automatically analyzes Java source files in the `org.uacalc` package and generates comprehensive dependency graphs designed to be LLM-friendly for understanding project structure.

## Features

### 🔍 **Core Analysis**
- Parses 146+ Java files across 20 packages
- Extracts package and class dependencies
- Identifies import relationships
- Builds comprehensive dependency graphs

### 📊 **NetworkX Integration**
- **Graph Statistics**: Density, connectivity, components
- **Centrality Analysis**: PageRank, betweenness, degree centrality
- **Cycle Detection**: Identifies circular dependencies
- **Path Analysis**: Finds longest dependency chains
- **Advanced Algorithms**: Uses NetworkX's robust graph algorithms

### 📈 **Multiple Output Formats**
- **Mermaid Diagrams**: LLM-friendly visual representations
- **Graphviz DOT**: Professional graph visualization
- **JSON Reports**: Complete dependency data with NetworkX analysis
- **Text Summaries**: Human-readable overviews
- **NetworkX Visualizations**: Matplotlib-based graph plots

## Installation

```bash
# Install required dependencies
pip install -r tools/requirements.txt

# Or install individually
pip install networkx matplotlib graphviz
```

## Usage

### Quick Start
```bash
# Generate all analysis outputs
python tools/generate_dependency_graph.py

# Show Mermaid diagrams in console
python tools/generate_dependency_graph.py --show-mermaid

# Custom output directory
python tools/generate_dependency_graph.py --output-dir my_analysis
```

### Advanced Usage
```bash
# Full-featured analyzer
python tools/java_dependency_analyzer.py --source . --output analysis_results

# Specific output formats
python tools/java_dependency_analyzer.py --format mermaid
python tools/java_dependency_analyzer.py --format json
```

## Output Files

### 📄 **Generated Files**
- `package_dependencies.mmd` - Package-level Mermaid diagram
- `class_dependencies.mmd` - Key class relationships
- `dependency_hierarchy.mmd` - Dependency hierarchy visualization
- `dependencies.dot` - Graphviz visualization file
- `dependencies.json` - Complete dependency data + NetworkX analysis
- `summary.txt` - Human-readable summary with graph insights
- `networkx_visualization.png` - Matplotlib-based graph plot

### 🔍 **NetworkX Analysis Features**
- **Graph Density**: 0.184 (moderately connected)
- **Connectivity**: Weakly connected, 9 strongly connected components
- **Centrality**: PageRank identifies most important packages
- **Cycles**: 596 cycles detected (mostly self-references)
- **Longest Paths**: Up to 11-step dependency chains

## Key Insights from UACalc Analysis

### 🏗️ **Package Structure**
- **20 packages** with clear hierarchical organization
- **146 classes** with well-defined relationships
- **510 total dependencies** showing rich interconnections

### 🎯 **Most Central Packages** (PageRank)
1. `org.uacalc.alg` (0.199) - Core algebra functionality
2. `org.uacalc.alg.op` (0.127) - Operation definitions
3. `org.uacalc.alg.conlat` (0.126) - Congruence lattice operations
4. `org.uacalc.ui.tm` (0.107) - UI task management
5. `org.uacalc.ui` (0.101) - Main UI components

### 🔄 **Dependency Patterns**
- **Core packages** (`alg`, `alg.op`, `alg.conlat`) form the foundation
- **UI packages** (`ui`, `ui.table`, `ui.tm`) depend heavily on core
- **Utility packages** (`util`, `terms`) provide supporting functionality
- **Example packages** demonstrate usage patterns

## Dependency Hierarchy Analysis

### 🍃 **Leaves** (depend on nothing else)
- Files with 0 outgoing dependencies
- Safe to modify first in refactoring
- Examples: `IntegerEditor`, `PermutationGenerator`, `PopupListener`

### 🌳 **Roots** (depend on many things)
- Files with many outgoing dependencies
- Complex components that rely on many others
- Examples: `Operation` interface, `OperationSymbol`, `Operations` collection

### 📊 **Hierarchy Levels**
- **Level 0**: 36 items (true leaves - no dependencies)
- **Level 1**: 15 items (minimal dependencies)
- **Level 2**: 25 items (moderate dependencies)
- **Higher levels**: Increasingly complex dependencies

## LLM-Friendly Features

### 📊 **Mermaid Diagrams**
The tool generates clean, readable Mermaid diagrams that LLMs can easily parse:

```mermaid
graph TD
    org_uacalc_alg["org.uacalc.alg"]
    org_uacalc_alg_op["org.uacalc.alg.op"]
    org_uacalc_alg_conlat["org.uacalc.alg.conlat"]
    org_uacalc_alg --> org_uacalc_alg_op
    org_uacalc_alg --> org_uacalc_alg_conlat
```

### 📋 **Structured Data**
- JSON format with complete dependency information
- NetworkX centrality measures and graph statistics
- Cycle detection and path analysis results
- Package structure and class hierarchies

## Technical Details

### 🔧 **Architecture**
- **Parser**: Regex-based Java file analysis
- **Graph Builder**: NetworkX DiGraph construction
- **Analyzer**: Centrality, cycle, and path analysis
- **Exporter**: Multiple output format generation

### 📊 **NetworkX Algorithms Used**
- **PageRank**: Package importance ranking
- **Betweenness Centrality**: Bridge identification
- **Cycle Detection**: `simple_cycles()` algorithm
- **Path Analysis**: `all_simple_paths()` with cutoff
- **Connectivity**: Weak/strong component analysis

### 🎨 **Visualization Options**
- **Mermaid**: Text-based diagrams for LLMs
- **Graphviz**: Professional graph layouts
- **Matplotlib**: NetworkX-based plots with centrality coloring
- **Text**: Human-readable summaries

## Use Cases

### 🤖 **For LLMs**
- Understanding project structure and dependencies
- Identifying key packages and classes
- Analyzing architectural patterns
- Finding potential refactoring opportunities

### 👨‍💻 **For Developers**
- Code architecture documentation
- Dependency analysis and optimization
- Refactoring planning
- Onboarding new team members

### 📊 **For Project Management**
- Technical debt assessment
- Architecture evolution tracking
- Complexity metrics
- Dependency risk analysis

## Examples

### Basic Analysis
```bash
python tools/generate_dependency_graph.py
```

### Custom Analysis
```bash
python tools/java_dependency_analyzer.py \
    --source /path/to/java/sources \
    --output custom_analysis \
    --format all
```

### NetworkX Insights
The tool provides deep insights into your codebase:
- **596 cycles** detected (mostly self-references)
- **Longest dependency path**: 11 steps
- **Graph density**: 0.184 (moderately connected)
- **Most central package**: `org.uacalc.alg` (PageRank: 0.199)

## Contributing

The tool is designed to be extensible. Key areas for enhancement:
- Additional graph algorithms
- More visualization formats
- Performance optimizations
- Integration with other analysis tools

## Fine-Grained Call Graph Analysis

### 🔍 **Method-Level Analysis**
For more detailed method-level call graph analysis, use the call graph tools:

#### **Using Ant Build System (Recommended)**
```bash
# Setup call graph tools (first time only)
ant setup-callgraph

# Generate method call graphs
ant callgraph

# Generate both package and method-level analysis
ant dependency-analysis

# Clean up tools and analysis files
ant clean-callgraph
```

#### **Using Python Scripts Directly**
```bash
# Setup call graph tools (first time only)
python tools/setup_call_graph_tools.py

# Generate method call graphs
python tools/generate_call_graph.py

# Quick analysis with setup
python tools/generate_call_graph.py --setup

# Use Ant integration
python tools/generate_call_graph.py --setup --use-ant
```

### 📊 **Call Graph Features**
- **Method-level dependencies**: Shows which methods call which other methods
- **Call frequency analysis**: Identifies most called and most calling methods
- **Call cycles detection**: Finds recursive or circular method calls
- **NetworkX integration**: Advanced graph analysis with centrality measures
- **Multiple output formats**: Mermaid, JSON, and text summaries

### 🛠️ **Required Tools**
The call graph analysis uses off-the-shelf tools:
- **java-callgraph**: Static analysis tool for Java call graphs
- **Java 8+**: Runtime environment
- **Maven**: Build tool for java-callgraph
- **Git**: For cloning repositories
- **Apache Ant**: For integrated build system (optional but recommended)

### 📈 **Call Graph Outputs**
- `call_graph.mmd` - Mermaid diagram of method calls
- `call_graph.json` - Complete call graph data
- `call_graph_summary.txt` - Human-readable summary with statistics

### 🎯 **Use Cases**
- **Performance optimization**: Identify frequently called methods
- **Refactoring planning**: Understand method dependencies
- **Code complexity analysis**: Find complex call patterns
- **Dead code detection**: Identify unused methods

## License

Part of the UACalc project. See main project license for details.
