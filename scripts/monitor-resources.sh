#!/bin/bash
# Real-Time Worktree Resource Monitor
# Monitors disk usage, CPU, memory, git metrics, and file statistics across all worktrees

set -e

# ============================================================================
# CONSTANTS AND GLOBAL VARIABLES
# ============================================================================

PROJECT_ROOT="/workspace"
TREES_DIR="$PROJECT_ROOT/.trees"
CONFIG_FILE="${CONFIG_FILE:-.worktree-monitor.conf}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Status Indicators
STATUS_NORMAL="🟢"
STATUS_WARNING="🟡"
STATUS_CRITICAL="🔴"

# Default Configuration
DEFAULT_REFRESH_INTERVAL=2
DEFAULT_DISK_THRESHOLD_MB=1024
DEFAULT_CPU_THRESHOLD=75.0
DEFAULT_MEMORY_THRESHOLD_MB=1024
DEFAULT_VIEW="table"

# Runtime Variables
REFRESH_INTERVAL=$DEFAULT_REFRESH_INTERVAL
DISK_THRESHOLD_MB=$DEFAULT_DISK_THRESHOLD_MB
CPU_THRESHOLD=$DEFAULT_CPU_THRESHOLD
MEMORY_THRESHOLD_MB=$DEFAULT_MEMORY_THRESHOLD_MB
CURRENT_VIEW=$DEFAULT_VIEW
PAUSED=0
RUNNING=1
DETAILED_INDEX=0

# Activity tracking for adaptive refresh
LAST_ACTIVITY_CHECK=0
IDLE_SECONDS=0
FAST_REFRESH=1
NORMAL_REFRESH=2
SLOW_REFRESH=5
VERY_SLOW_REFRESH=10

# Data cache
declare -A DISK_USAGE_CACHE
declare -A DISK_CACHE_TIME
declare -A PREVIOUS_STATUS
CACHE_TTL=10  # Cache disk usage for 10 seconds

# ============================================================================
# SIGNAL HANDLERS AND CLEANUP
# ============================================================================

cleanup() {
    # Restore cursor and clear screen
    tput cnorm 2>/dev/null || true
    clear
    echo -e "${GREEN}✓ Monitoring stopped${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

# ============================================================================
# CONFIGURATION MANAGEMENT
# ============================================================================

load_config() {
    if [ -f "$CONFIG_FILE" ]; then
        echo -e "${BLUE}Loading configuration from: $CONFIG_FILE${NC}" >&2

        # Parse config file (simple INI format)
        while IFS='=' read -r key value; do
            # Skip comments and empty lines
            [[ "$key" =~ ^#.*$ ]] && continue
            [[ -z "$key" ]] && continue

            # Trim whitespace
            key=$(echo "$key" | xargs)
            value=$(echo "$value" | xargs)

            case "$key" in
                interval_seconds) REFRESH_INTERVAL=$value ;;
                disk_mb) DISK_THRESHOLD_MB=$value ;;
                cpu_percent) CPU_THRESHOLD=$value ;;
                memory_mb) MEMORY_THRESHOLD_MB=$value ;;
                default_view) CURRENT_VIEW=$value ;;
            esac
        done < "$CONFIG_FILE"
    fi
}

create_default_config() {
    cat > "$CONFIG_FILE" << 'EOF'
# Worktree Resource Monitor Configuration

# Refresh interval in seconds (will be adaptive)
interval_seconds=2

# Resource thresholds for alerts
disk_mb=1024
cpu_percent=75.0
memory_mb=1024

# Display settings
default_view=table
show_alerts=true
color_enabled=true

# Monitoring options
track_processes=true
EOF
    echo -e "${GREEN}✓ Created default configuration: $CONFIG_FILE${NC}"
}

# ============================================================================
# ARGUMENT PARSING
# ============================================================================

show_help() {
    cat << EOF
${BOLD}Worktree Resource Monitor${NC}

${BOLD}USAGE:${NC}
    $0 [OPTIONS]

${BOLD}OPTIONS:${NC}
    -h, --help              Show this help message
    -i, --interval SECONDS  Refresh interval (default: 2)
    -v, --view VIEW         Initial view: table|detailed|summary (default: table)
    -c, --config FILE       Configuration file (default: .worktree-monitor.conf)
    --create-config         Create default configuration file
    --export-json FILE      Export current snapshot to JSON
    --export-csv FILE       Export current snapshot to CSV

${BOLD}KEYBOARD CONTROLS:${NC}
    p       Pause/resume monitoring
    q       Quit
    v       Switch view mode
    +/-     Increase/decrease refresh rate
    ↑/↓     Navigate in detailed view

${BOLD}VIEWS:${NC}
    table       Compact table showing all worktrees
    detailed    Full breakdown of single worktree
    summary     System-wide summary and top consumers

${BOLD}EXAMPLES:${NC}
    $0                          # Start with default settings
    $0 -i 5 -v summary          # 5-second refresh, summary view
    $0 --export-json stats.json # Export snapshot and exit
    $0 --create-config          # Create default config file

EOF
}

parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -i|--interval)
                REFRESH_INTERVAL="$2"
                shift 2
                ;;
            -v|--view)
                CURRENT_VIEW="$2"
                shift 2
                ;;
            -c|--config)
                CONFIG_FILE="$2"
                shift 2
                ;;
            --create-config)
                create_default_config
                exit 0
                ;;
            --export-json)
                export_json "$2"
                exit 0
                ;;
            --export-csv)
                export_csv "$2"
                exit 0
                ;;
            *)
                echo -e "${RED}Error: Unknown option: $1${NC}"
                show_help
                exit 1
                ;;
        esac
    done
}

# ============================================================================
# WORKTREE DISCOVERY
# ============================================================================

discover_worktrees() {
    # Find all task worktrees
    local worktrees=()

    while IFS= read -r line; do
        # Extract path (first column)
        local path=$(echo "$line" | awk '{print $1}')

        # Verify path exists and is accessible
        if [ -d "$path" ] && [ -r "$path" ]; then
            worktrees+=("$path")
        fi
    done < <(git -C "$PROJECT_ROOT" worktree list 2>/dev/null | grep -E "\[task/" || true)

    echo "${worktrees[@]}"
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

format_bytes() {
    local bytes=$1
    local mb=$((bytes / 1024 / 1024))
    local gb=$((bytes / 1024 / 1024 / 1024))

    if [ $gb -gt 0 ]; then
        echo "${gb}GB"
    else
        echo "${mb}MB"
    fi
}

get_timestamp() {
    date "+%H:%M:%S"
}

# ============================================================================
# DATA COLLECTION: DISK USAGE
# ============================================================================

get_disk_usage() {
    local path=$1
    local current_time=$(date +%s)

    # Check cache
    if [ -n "${DISK_CACHE_TIME[$path]}" ]; then
        local cache_age=$((current_time - DISK_CACHE_TIME[$path]))
        if [ $cache_age -lt $CACHE_TTL ]; then
            echo "${DISK_USAGE_CACHE[$path]}"
            return
        fi
    fi

    # Calculate disk usage (excluding .git for working tree)
    local total_bytes=$(du -sb "$path" 2>/dev/null | awk '{print $1}')
    local total_mb=$((total_bytes / 1024 / 1024))

    # Cache result
    DISK_USAGE_CACHE[$path]=$total_mb
    DISK_CACHE_TIME[$path]=$current_time

    echo "$total_mb"
}

get_git_dir_size() {
    local path=$1
    local git_dir="$path/.git"

    if [ -d "$git_dir" ]; then
        local git_bytes=$(du -sb "$git_dir" 2>/dev/null | awk '{print $1}')
        echo $((git_bytes / 1024 / 1024))
    else
        echo "0"
    fi
}

# ============================================================================
# DATA COLLECTION: GIT METRICS
# ============================================================================

get_uncommitted_count() {
    local path=$1
    git -C "$path" status --porcelain 2>/dev/null | wc -l
}

get_diff_stats() {
    local path=$1
    local stats=$(git -C "$path" diff --numstat develop/v4.2.0 2>/dev/null | awk '{added+=$1; removed+=$2} END {print added","removed}')
    echo "$stats"
}

get_commits_ahead() {
    local path=$1
    git -C "$path" rev-list --count origin/develop/v4.2.0..HEAD 2>/dev/null || echo "0"
}

get_last_commit_time() {
    local path=$1
    local timestamp=$(git -C "$path" log -1 --format=%ct 2>/dev/null || echo "0")

    if [ "$timestamp" != "0" ]; then
        local current=$(date +%s)
        local diff=$((current - timestamp))
        local hours=$((diff / 3600))

        if [ $hours -lt 1 ]; then
            echo "<1h"
        elif [ $hours -lt 24 ]; then
            echo "${hours}h"
        else
            echo "$((hours / 24))d"
        fi
    else
        echo "N/A"
    fi
}

# ============================================================================
# DATA COLLECTION: FILE STATISTICS
# ============================================================================

count_files() {
    local path=$1
    find "$path" -type f -not -path "*/.git/*" 2>/dev/null | wc -l
}

count_python_files() {
    local path=$1
    find "$path" -type f -name "*.py" -not -path "*/.git/*" 2>/dev/null | wc -l
}

get_lines_of_code() {
    local path=$1

    # Try cloc if available, otherwise fallback to simple wc
    if command -v cloc &> /dev/null; then
        cloc "$path" --quiet --csv 2>/dev/null | tail -1 | cut -d',' -f5 || echo "0"
    else
        # Simple fallback: count lines in Python files
        find "$path" -type f -name "*.py" -not -path "*/.git/*" -exec wc -l {} + 2>/dev/null | tail -1 | awk '{print $1}' || echo "0"
    fi
}

# ============================================================================
# DATA COLLECTION: PROCESS MONITORING
# ============================================================================

get_worktree_processes() {
    local path=$1

    # Find processes with files open in this directory
    if command -v lsof &> /dev/null; then
        lsof +D "$path" 2>/dev/null | awk 'NR>1 {print $2}' | sort -u || echo ""
    else
        echo ""
    fi
}

get_process_stats() {
    local pid=$1

    if [ -n "$pid" ] && ps -p "$pid" > /dev/null 2>&1; then
        ps -p "$pid" -o %cpu,%mem,comm --no-headers 2>/dev/null
    else
        echo ""
    fi
}

aggregate_worktree_cpu() {
    local path=$1
    local pids=($(get_worktree_processes "$path"))

    if [ ${#pids[@]} -eq 0 ]; then
        echo "0.0"
        return
    fi

    local total_cpu=0

    for pid in "${pids[@]}"; do
        local stats=$(get_process_stats "$pid")
        if [ -n "$stats" ]; then
            local cpu=$(echo "$stats" | awk '{print $1}')
            total_cpu=$(awk -v a="$total_cpu" -v b="$cpu" 'BEGIN {printf "%.1f", a + b}')
        fi
    done

    echo "$total_cpu"
}

aggregate_worktree_memory() {
    local path=$1
    local pids=($(get_worktree_processes "$path"))

    if [ ${#pids[@]} -eq 0 ]; then
        echo "0"
        return
    fi

    local total_mem=0
    local total_mem_kb=$(grep MemTotal /proc/meminfo 2>/dev/null | awk '{print $2}')

    for pid in "${pids[@]}"; do
        local stats=$(get_process_stats "$pid")
        if [ -n "$stats" ]; then
            local mem_percent=$(echo "$stats" | awk '{print $2}')
            # Convert percentage to MB (rough estimate based on total system memory)
            if [ -n "$total_mem_kb" ]; then
                local mem_mb=$(awk -v kb="$total_mem_kb" -v pct="$mem_percent" 'BEGIN {printf "%.0f", kb * pct / 100 / 1024}')
                total_mem=$((total_mem + mem_mb))
            fi
        fi
    done

    echo "$total_mem"
}

# ============================================================================
# THRESHOLD CHECKING AND STATUS
# ============================================================================

get_status_for_metrics() {
    local disk_mb=$1
    local cpu_percent=$2
    local mem_mb=$3

    # Convert CPU to integer (multiply by 10 to preserve one decimal place)
    local cpu_int=$(echo "$cpu_percent" | awk '{printf "%.0f", $1 * 10}')

    # Check if any metric exceeds critical threshold (90%)
    local disk_critical=$((DISK_THRESHOLD_MB * 90 / 100))
    local cpu_critical=$(echo "$CPU_THRESHOLD" | awk '{printf "%.0f", $1 * 10 * 0.9}')
    local mem_critical=$((MEMORY_THRESHOLD_MB * 90 / 100))

    if [ "$disk_mb" -gt "$disk_critical" ] || \
       [ "$cpu_int" -gt "$cpu_critical" ] || \
       [ "$mem_mb" -gt "$mem_critical" ]; then
        echo "critical"
        return
    fi

    # Check if any metric exceeds warning threshold (70%)
    local disk_warning=$((DISK_THRESHOLD_MB * 70 / 100))
    local cpu_warning=$(echo "$CPU_THRESHOLD" | awk '{printf "%.0f", $1 * 10 * 0.7}')
    local mem_warning=$((MEMORY_THRESHOLD_MB * 70 / 100))

    if [ "$disk_mb" -gt "$disk_warning" ] || \
       [ "$cpu_int" -gt "$cpu_warning" ] || \
       [ "$mem_mb" -gt "$mem_warning" ]; then
        echo "warning"
        return
    fi

    echo "normal"
}

get_status_indicator() {
    local status=$1

    case "$status" in
        critical) echo "$STATUS_CRITICAL" ;;
        warning) echo "$STATUS_WARNING" ;;
        *) echo "$STATUS_NORMAL" ;;
    esac
}

get_status_text() {
    local status=$1

    case "$status" in
        critical) echo -e "${RED}Critical${NC}" ;;
        warning) echo -e "${YELLOW}Warning${NC}" ;;
        *) echo -e "${GREEN}Normal${NC}" ;;
    esac
}

# ============================================================================
# DISPLAY: TABLE VIEW
# ============================================================================

display_table_view() {
    local worktrees=("$@")

    clear

    # Header
    echo -e "${BOLD}${BLUE}📊 Worktree Resource Monitor${NC} ${CYAN}(Table View)${NC}"
    echo -e "Last Update: $(get_timestamp) | Refresh: ${REFRESH_INTERVAL}s | ${YELLOW}p${NC}=pause ${YELLOW}q${NC}=quit ${YELLOW}v${NC}=view"
    echo ""

    # Table header
    printf "${CYAN}%-25s %-8s %-6s %-8s %-6s %-8s %s${NC}\n" \
        "WORKTREE" "DISK" "CPU%" "MEM(MB)" "FILES" "CHANGES" "STATUS"
    printf "${CYAN}%-25s %-8s %-6s %-8s %-6s %-8s %s${NC}\n" \
        "─────────" "────" "────" "───────" "─────" "───────" "──────"

    # Collect data for all worktrees
    local total_disk=0
    local total_files=0
    local alert_count=0

    for path in "${worktrees[@]}"; do
        local name=$(basename "$path")
        local disk=$(get_disk_usage "$path")
        local cpu=$(aggregate_worktree_cpu "$path")
        local mem=$(aggregate_worktree_memory "$path")
        local files=$(count_files "$path")
        local changes=$(get_uncommitted_count "$path")

        # Get status
        local status=$(get_status_for_metrics "$disk" "$cpu" "$mem")
        local status_icon=$(get_status_indicator "$status")
        local status_name=""

        case "$status" in
            critical)
                status_name="${RED}Critical${NC}"
                alert_count=$((alert_count + 1))
                ;;
            warning)
                status_name="${YELLOW}Warning${NC}"
                ;;
            *)
                status_name="${GREEN}Normal${NC}"
                ;;
        esac

        # Accumulate totals
        total_disk=$((total_disk + disk))
        total_files=$((total_files + files))

        # Truncate name if too long
        if [ ${#name} -gt 25 ]; then
            name="${name:0:22}..."
        fi

        # Display row
        printf "%-25s %6dMB %5.1f%% %7dMB %6d %8d %s %b\n" \
            "$name" "$disk" "$cpu" "$mem" "$files" "$changes" "$status_icon" "$status_name"
    done

    # Summary row
    echo ""
    printf "${GREEN}SUMMARY: %d worktrees | Total Disk: %dMB | Total Files: %d${NC}\n" \
        "${#worktrees[@]}" "$total_disk" "$total_files"

    # Alerts
    if [ $alert_count -gt 0 ]; then
        echo ""
        echo -e "${RED}🔴 ${alert_count} worktree(s) require attention${NC}"
    fi
}

# ============================================================================
# DISPLAY: DETAILED VIEW
# ============================================================================

display_detailed_view() {
    local worktrees=("$@")
    local total_count=${#worktrees[@]}

    # Bounds check
    if [ $DETAILED_INDEX -ge $total_count ]; then
        DETAILED_INDEX=0
    fi
    if [ $DETAILED_INDEX -lt 0 ]; then
        DETAILED_INDEX=$((total_count - 1))
    fi

    local path="${worktrees[$DETAILED_INDEX]}"
    local name=$(basename "$path")

    clear

    # Header
    echo -e "${BOLD}${BLUE}📊 Worktree Resource Monitor${NC} ${CYAN}(Detailed View)${NC}"
    echo -e "Worktree $((DETAILED_INDEX + 1))/$total_count | ${YELLOW}↑↓${NC}=navigate ${YELLOW}v${NC}=view ${YELLOW}q${NC}=quit"
    echo ""

    # Worktree title
    echo -e "${BOLD}${MAGENTA}$name${NC} ${CYAN}($path)${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    # Disk Usage
    echo -e "${BOLD}Disk Usage${NC}"
    local disk=$(get_disk_usage "$path")
    local git_size=$(get_git_dir_size "$path")
    local work_size=$((disk - git_size))

    echo -e "  Working Tree:  ${GREEN}${work_size}MB${NC}"
    echo -e "  .git Directory: ${BLUE}${git_size}MB${NC}"
    echo -e "  ${BOLD}Total:         ${disk}MB${NC}"
    echo ""

    # Git Metrics
    echo -e "${BOLD}Git Metrics${NC}"
    local uncommitted=$(get_uncommitted_count "$path")
    local ahead=$(get_commits_ahead "$path")
    local last_commit=$(get_last_commit_time "$path")
    local diff_stats=$(get_diff_stats "$path")
    local added=$(echo "$diff_stats" | cut -d',' -f1)
    local removed=$(echo "$diff_stats" | cut -d',' -f2)

    echo -e "  Uncommitted:   ${YELLOW}$uncommitted files${NC}"
    echo -e "  Diff Size:     ${GREEN}+$added${NC} / ${RED}-$removed${NC} lines"
    echo -e "  Commits Ahead: ${CYAN}↑$ahead${NC}"
    echo -e "  Last Commit:   $last_commit ago"
    echo ""

    # File Statistics
    echo -e "${BOLD}File Statistics${NC}"
    local total_files=$(count_files "$path")
    local python_files=$(count_python_files "$path")

    echo -e "  Total Files:   $total_files"
    echo -e "  Python Files:  $python_files"
    echo ""

    # Active Processes
    echo -e "${BOLD}Active Processes${NC}"
    local pids=($(get_worktree_processes "$path"))

    if [ ${#pids[@]} -gt 0 ]; then
        for pid in "${pids[@]}"; do
            local stats=$(get_process_stats "$pid")
            if [ -n "$stats" ]; then
                local cpu=$(echo "$stats" | awk '{print $1}')
                local mem=$(echo "$stats" | awk '{print $2}')
                local cmd=$(echo "$stats" | awk '{print $3}')
                echo -e "  ${GREEN}$cmd${NC} (PID $pid): ${cpu}% CPU, ${mem}% MEM"
            fi
        done
    else
        echo -e "  ${CYAN}No active processes detected${NC}"
    fi

    echo ""

    # Status
    local cpu_total=$(aggregate_worktree_cpu "$path")
    local mem_total=$(aggregate_worktree_memory "$path")
    local status=$(get_status_for_metrics "$disk" "$cpu_total" "$mem_total")
    local status_text=$(get_status_text "$status")

    echo -e "${BOLD}Overall Status:${NC} $status_text"
}

# ============================================================================
# DISPLAY: SUMMARY VIEW
# ============================================================================

display_summary_view() {
    local worktrees=("$@")

    clear

    # Header
    echo -e "${BOLD}${BLUE}📊 Worktree Resource Monitor${NC} ${CYAN}(Summary View)${NC}"
    echo -e "Last Update: $(get_timestamp) | ${YELLOW}v${NC}=view ${YELLOW}q${NC}=quit"
    echo ""

    # Aggregate metrics
    local total_disk=0
    local total_files=0
    local total_changes=0
    local normal_count=0
    local warning_count=0
    local critical_count=0

    declare -A worktree_disk
    declare -A worktree_cpu

    for path in "${worktrees[@]}"; do
        local name=$(basename "$path")
        local disk=$(get_disk_usage "$path")
        local cpu=$(aggregate_worktree_cpu "$path")
        local mem=$(aggregate_worktree_memory "$path")
        local files=$(count_files "$path")
        local changes=$(get_uncommitted_count "$path")

        # Store for top consumers
        worktree_disk[$name]=$disk
        worktree_cpu[$name]=$cpu

        # Accumulate
        total_disk=$((total_disk + disk))
        total_files=$((total_files + files))
        total_changes=$((total_changes + changes))

        # Status counts
        local status=$(get_status_for_metrics "$disk" "$cpu" "$mem")
        case "$status" in
            critical) critical_count=$((critical_count + 1)) ;;
            warning) warning_count=$((warning_count + 1)) ;;
            *) normal_count=$((normal_count + 1)) ;;
        esac
    done

    # System-Wide Summary
    echo -e "${BOLD}${MAGENTA}System-Wide Summary${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "  Total Worktrees:     ${BOLD}${#worktrees[@]}${NC}"
    echo -e "  Total Disk Usage:    ${BOLD}${total_disk}MB${NC}"
    echo -e "  Total Files:         ${BOLD}${total_files}${NC}"
    echo -e "  Uncommitted Changes: ${YELLOW}${total_changes}${NC}"
    echo -e "  Average Disk/WT:     $((total_disk / ${#worktrees[@]}))MB"
    echo ""

    # Status Distribution
    echo -e "${BOLD}Status Distribution${NC}"
    echo -e "  ${GREEN}● Normal:${NC}   $normal_count"
    echo -e "  ${YELLOW}● Warning:${NC}  $warning_count"
    echo -e "  ${RED}● Critical:${NC} $critical_count"
    echo ""

    # Top 5 Disk Consumers
    echo -e "${BOLD}Top 5 Disk Consumers${NC}"
    for name in $(for key in "${!worktree_disk[@]}"; do
        echo "$key ${worktree_disk[$key]}"
    done | sort -k2 -rn | head -5 | awk '{print $1}'); do
        local disk=${worktree_disk[$name]}
        local bar_length=$((disk / 50))  # Scale for visualization
        local bar=$(printf '█%.0s' $(seq 1 $bar_length))
        printf "  %-25s %6dMB ${CYAN}%s${NC}\n" "$name" "$disk" "$bar"
    done
}

# ============================================================================
# ADAPTIVE REFRESH LOGIC
# ============================================================================

calculate_adaptive_interval() {
    # Check for activity (uncommitted files, new processes)
    local activity=0
    local worktrees=($(discover_worktrees))

    for path in "${worktrees[@]}"; do
        local uncommitted=$(get_uncommitted_count "$path")
        if [ "$uncommitted" -gt 0 ]; then
            activity=1
            break
        fi
    done

    # Determine refresh interval based on idle time and activity
    if [ $activity -eq 1 ]; then
        # Activity detected - fast refresh
        IDLE_SECONDS=0
        echo $FAST_REFRESH
    elif [ $IDLE_SECONDS -lt 30 ]; then
        # Recently active - normal refresh
        echo $NORMAL_REFRESH
    elif [ $IDLE_SECONDS -lt 300 ]; then
        # Idle for 30s-5min - slow refresh
        echo $SLOW_REFRESH
    else
        # Very idle - very slow refresh
        echo $VERY_SLOW_REFRESH
    fi
}

# ============================================================================
# MONITORING LOOP
# ============================================================================

monitor_loop() {
    local worktrees=($(discover_worktrees))

    while [ $RUNNING -eq 1 ]; do
        # Skip display if paused
        if [ $PAUSED -eq 0 ]; then
            # Display based on current view
            case "$CURRENT_VIEW" in
                detailed)
                    display_detailed_view "${worktrees[@]}"
                    ;;
                summary)
                    display_summary_view "${worktrees[@]}"
                    ;;
                *)
                    display_table_view "${worktrees[@]}"
                    ;;
            esac

            # Update idle time
            IDLE_SECONDS=$((IDLE_SECONDS + REFRESH_INTERVAL))

            # Adaptive refresh (if enabled)
            # REFRESH_INTERVAL=$(calculate_adaptive_interval)
        else
            echo -e "${YELLOW}⏸  Monitoring paused - press 'p' to resume${NC}"
        fi

        # Sleep for refresh interval
        sleep "$REFRESH_INTERVAL"
    done
}

# ============================================================================
# MAIN INITIALIZATION
# ============================================================================

init_monitor() {
    # Hide cursor
    tput civis 2>/dev/null || true

    # Clear screen
    clear

    # Load configuration
    load_config

    echo -e "${BLUE}🚀 Worktree Resource Monitor${NC}"
    echo -e "${BLUE}================================${NC}"
    echo ""
    echo -e "${GREEN}Initializing...${NC}"
    echo ""

    # Verify worktrees exist
    local worktree_list=($(discover_worktrees))
    if [ ${#worktree_list[@]} -eq 0 ]; then
        echo -e "${RED}Error: No task worktrees found!${NC}"
        echo -e "${YELLOW}Run ./create-worktree-batch.sh first${NC}"
        exit 1
    fi

    echo -e "${GREEN}Found ${#worktree_list[@]} worktrees${NC}"
    echo ""
    sleep 1
}

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

main() {
    parse_arguments "$@"
    init_monitor

    # Start monitoring loop
    monitor_loop
}

# Run main function
main "$@"
