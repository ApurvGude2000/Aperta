# ABOUTME: Rich console logging utilities with colorama for orchestrator, router, and agent operations
# ABOUTME: Provides formatted logging with colors, boxes, and structured output

from datetime import datetime
from typing import Dict, List, Optional, Any
import sys


# ANSI color codes
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    # Text colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'


def _get_timestamp() -> str:
    """Get formatted timestamp."""
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


def _print_box(title: str, content: str, color: str = Colors.CYAN) -> None:
    """Print content in a colored box."""
    width = 80
    print(f"\n{color}{'═' * width}{Colors.RESET}")
    print(f"{color}║ {Colors.BOLD}{title}{Colors.RESET}{color}{' ' * (width - len(title) - 3)}║{Colors.RESET}")
    print(f"{color}{'═' * width}{Colors.RESET}")
    
    for line in content.split('\n'):
        if line:
            print(f"{color}║{Colors.RESET} {line}")
    
    print(f"{color}{'═' * width}{Colors.RESET}\n")


def _print_separator(char: str = '─', length: int = 80, color: str = Colors.BRIGHT_BLACK) -> None:
    """Print a separator line."""
    print(f"{color}{char * length}{Colors.RESET}")


def log_orchestrator(message: str) -> None:
    """
    Log orchestrator-level messages.
    
    Args:
        message: Message to log
    """
    timestamp = _get_timestamp()
    print(f"{Colors.BRIGHT_MAGENTA}[{timestamp}] 🎭 ORCHESTRATOR:{Colors.RESET} {message}")


def log_router(
    intent: str,
    agents: List[str],
    confidence: float,
    reasoning: str
) -> None:
    """
    Log router decision with intent, selected agents, and reasoning.
    
    Args:
        intent: Detected user intent
        agents: List of selected agent names
        confidence: Confidence score (0-1)
        reasoning: Reasoning for the routing decision
    """
    timestamp = _get_timestamp()
    
    # Color confidence based on value
    conf_color = Colors.GREEN if confidence > 0.8 else Colors.YELLOW if confidence > 0.5 else Colors.RED
    
    content = f"""Intent: {Colors.BOLD}{intent}{Colors.RESET}
Agents: {Colors.BRIGHT_CYAN}{', '.join(agents)}{Colors.RESET}
Confidence: {conf_color}{confidence:.2%}{Colors.RESET}
Reasoning: {reasoning}"""
    
    _print_box(f"🧭 ROUTER DECISION [{timestamp}]", content, Colors.BRIGHT_BLUE)


def log_agent_start(agent_name: str) -> None:
    """
    Log the start of agent execution.
    
    Args:
        agent_name: Name of the agent starting
    """
    timestamp = _get_timestamp()
    print(f"{Colors.BRIGHT_GREEN}[{timestamp}] ▶  AGENT START:{Colors.RESET} {Colors.BOLD}{agent_name}{Colors.RESET}")


def log_agent_result(
    agent_name: str,
    metrics: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log agent execution result with optional metrics.
    
    Args:
        agent_name: Name of the agent
        metrics: Optional dictionary of metrics (execution_time, tokens, etc.)
    """
    timestamp = _get_timestamp()
    
    metrics_str = ""
    if metrics:
        metrics_parts = []
        for key, value in metrics.items():
            if key == 'execution_time':
                metrics_parts.append(f"⏱️  {value:.2f}s")
            elif key == 'tokens':
                metrics_parts.append(f"🎫 {value} tokens")
            elif key == 'success':
                icon = "✅" if value else "❌"
                metrics_parts.append(f"{icon} {'Success' if value else 'Failed'}")
            else:
                metrics_parts.append(f"{key}: {value}")
        
        if metrics_parts:
            metrics_str = f" [{', '.join(metrics_parts)}]"
    
    print(f"{Colors.BRIGHT_GREEN}[{timestamp}] ■  AGENT COMPLETE:{Colors.RESET} {Colors.BOLD}{agent_name}{Colors.RESET}{metrics_str}")


def log_error(component: str, error: Exception, traceback_info: Optional[str] = None) -> None:
    """
    Log error with component information.
    
    Args:
        component: Component where error occurred (e.g., 'orchestrator', 'agent_name')
        error: The exception object
        traceback_info: Optional traceback information
    """
    timestamp = _get_timestamp()
    
    content = f"""Component: {Colors.BOLD}{component}{Colors.RESET}
Error Type: {type(error).__name__}
Message: {str(error)}"""
    
    if traceback_info:
        content += f"\n\nTraceback:\n{traceback_info}"
    
    _print_box(f"❌ ERROR [{timestamp}]", content, Colors.RED)


def log_execution_summary(
    total_time: float,
    tokens: Optional[int] = None,
    status: str = "success",
    additional_info: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log execution summary at the end of orchestrator run.
    
    Args:
        total_time: Total execution time in seconds
        tokens: Optional total token count
        status: Execution status ('success', 'partial', 'failed')
        additional_info: Optional dictionary with additional information
    """
    timestamp = _get_timestamp()
    
    # Status icon and color
    status_map = {
        'success': ('✅', Colors.GREEN),
        'partial': ('⚠️', Colors.YELLOW),
        'failed': ('❌', Colors.RED)
    }
    icon, color = status_map.get(status.lower(), ('ℹ️', Colors.CYAN))
    
    content = f"""Status: {color}{icon} {status.upper()}{Colors.RESET}
Total Time: {total_time:.2f}s"""
    
    if tokens:
        content += f"\nTotal Tokens: {tokens}"
    
    if additional_info:
        content += "\n\nAdditional Info:"
        for key, value in additional_info.items():
            content += f"\n  • {key}: {value}"
    
    _print_box(f"📊 EXECUTION SUMMARY [{timestamp}]", content, Colors.BRIGHT_CYAN)


def log_info(message: str, component: Optional[str] = None) -> None:
    """
    Log general information message.
    
    Args:
        message: Message to log
        component: Optional component name
    """
    timestamp = _get_timestamp()
    prefix = f"{Colors.BRIGHT_CYAN}[{timestamp}] ℹ️  INFO"
    
    if component:
        prefix += f" [{component}]"
    
    print(f"{prefix}:{Colors.RESET} {message}")


def log_debug(message: str, component: Optional[str] = None) -> None:
    """
    Log debug message.
    
    Args:
        message: Message to log
        component: Optional component name
    """
    timestamp = _get_timestamp()
    prefix = f"{Colors.BRIGHT_BLACK}[{timestamp}] 🐛 DEBUG"
    
    if component:
        prefix += f" [{component}]"
    
    print(f"{prefix}:{Colors.RESET} {message}")


def log_tree(items: List[str], title: Optional[str] = None, color: str = Colors.CYAN) -> None:
    """
    Log items in a tree structure.
    
    Args:
        items: List of items to display
        title: Optional title for the tree
        color: Color for the tree structure
    """
    if title:
        print(f"\n{color}{Colors.BOLD}{title}{Colors.RESET}")
    
    for i, item in enumerate(items):
        is_last = i == len(items) - 1
        branch = "└──" if is_last else "├──"
        print(f"{color}{branch}{Colors.RESET} {item}")
    
    print()


def log_section(title: str) -> None:
    """
    Log a section header.
    
    Args:
        title: Section title
    """
    _print_separator()
    print(f"\n{Colors.BOLD}{Colors.BRIGHT_YELLOW}▼ {title}{Colors.RESET}\n")
