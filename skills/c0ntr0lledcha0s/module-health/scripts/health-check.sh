#!/bin/bash
# Module Health Check Script
# Analyzes module structure and calculates health scores

set -e

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SOURCE_DIR="source"
IDEAL_MIN_CLASSES=5
IDEAL_MAX_CLASSES=30
WARNING_MAX_CLASSES=50

echo "🏥 Module Health Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if source directory exists
if [ ! -d "$SOURCE_DIR" ]; then
    echo "❌ Error: $SOURCE_DIR directory not found"
    exit 1
fi

# Function to count items in file
count_items() {
    local file=$1
    local pattern=$2
    if [ -f "$file" ]; then
        grep -c "$pattern" "$file" 2>/dev/null || echo "0"
    else
        echo "0"
    fi
}

# Function to calculate health score
calculate_score() {
    local classes=$1
    local properties=$2
    local has_readme=$3

    local score=0

    # Size Balance (30 points)
    if [ $classes -ge $IDEAL_MIN_CLASSES ] && [ $classes -le $IDEAL_MAX_CLASSES ]; then
        score=$((score + 30))
    elif [ $classes -ge 1 ] && [ $classes -lt $IDEAL_MIN_CLASSES ]; then
        score=$((score + 15))
    elif [ $classes -gt $IDEAL_MAX_CLASSES ] && [ $classes -le $WARNING_MAX_CLASSES ]; then
        score=$((score + 15))
    fi

    # Documentation (20 points)
    if [ "$has_readme" = "true" ]; then
        score=$((score + 20))
    fi

    # Completeness (20 points)
    if [ $classes -gt 0 ] && [ $properties -gt 0 ]; then
        score=$((score + 20))
    elif [ $classes -gt 0 ] || [ $properties -gt 0 ]; then
        score=$((score + 10))
    fi

    # Ratio (20 points) - simplified
    if [ $classes -gt 0 ]; then
        local ratio=$((properties * 10 / classes))
        if [ $ratio -ge 20 ] && [ $ratio -le 80 ]; then
            score=$((score + 20))
        elif [ $ratio -ge 10 ] && [ $ratio -le 120 ]; then
            score=$((score + 10))
        fi
    fi

    # Organization (10 points) - give base points for now
    score=$((score + 10))

    echo $score
}

# Function to get status
get_status() {
    local score=$1
    local classes=$2

    if [ $score -ge 90 ]; then
        echo -e "${GREEN}✅ Great${NC}"
    elif [ $score -ge 80 ]; then
        echo -e "${GREEN}✅ Good${NC}"
    elif [ $score -ge 70 ]; then
        echo -e "${GREEN}✅ OK${NC}"
    elif [ $score -ge 60 ]; then
        echo -e "${YELLOW}⚠️  Fair${NC}"
    elif [ $classes -ge $WARNING_MAX_CLASSES ]; then
        echo -e "${RED}❌ Bloat${NC}"
    else
        echo -e "${YELLOW}⚠️  Small${NC}"
    fi
}

# Initialize counters
total_modules=0
total_classes=0
total_properties=0
total_score=0
healthy_modules=0
warning_modules=0
critical_modules=0

# Header
printf "%-15s | %5s | %5s | %5s | %6s | %s\n" \
    "Module" "Score" "Cls" "Props" "Ratio" "Status"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Analyze each module
for module_dir in "$SOURCE_DIR"/*/ ; do
    if [ ! -d "$module_dir" ]; then
        continue
    fi

    module_name=$(basename "$module_dir")
    total_modules=$((total_modules + 1))

    # Count classes and properties
    classes=$(count_items "${module_dir}classes.edn" ":user.class/")
    properties=$(count_items "${module_dir}properties.edn" ":user.property/")

    # Check for README
    has_readme="false"
    if [ -f "${module_dir}README.md" ]; then
        has_readme="true"
    fi

    # Calculate ratio (properties per class, scaled by 10 for display)
    if [ $classes -gt 0 ]; then
        ratio=$(echo "scale=1; $properties / $classes" | bc)
    else
        ratio="∞"
    fi

    # Calculate health score
    score=$(calculate_score $classes $properties $has_readme)

    # Get status
    status=$(get_status $score $classes)

    # Update counters
    total_classes=$((total_classes + classes))
    total_properties=$((total_properties + properties))
    total_score=$((total_score + score))

    if [ $score -ge 80 ]; then
        healthy_modules=$((healthy_modules + 1))
    elif [ $score -ge 60 ]; then
        warning_modules=$((warning_modules + 1))
    else
        critical_modules=$((critical_modules + 1))
    fi

    # Print module row
    printf "%-15s | %3s/100 | %5s | %5s | %6s | %s\n" \
        "$module_name" "$score" "$classes" "$properties" "$ratio" "$status"
done

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Summary:"
echo "  Total Modules: $total_modules"
echo "  Total Classes: $total_classes"
echo "  Total Properties: $total_properties"
echo ""

# Calculate overall health
if [ $total_modules -gt 0 ]; then
    overall_health=$((total_score / total_modules))
    echo "  Overall Health: $overall_health/100"
    echo ""
    echo "  ${GREEN}✅ Healthy Modules: $healthy_modules/$total_modules${NC}"
    echo "  ${YELLOW}⚠️  Needs Attention: $warning_modules/$total_modules${NC}"
    echo "  ${RED}❌ Critical Issues: $critical_modules/$total_modules${NC}"
    echo ""
fi

# Find issues
echo "Issues Found:"
echo ""

# Check for bloated modules
for module_dir in "$SOURCE_DIR"/*/ ; do
    if [ ! -d "$module_dir" ]; then
        continue
    fi

    module_name=$(basename "$module_dir")
    classes=$(count_items "${module_dir}classes.edn" ":user.class/")

    if [ $classes -ge $WARNING_MAX_CLASSES ]; then
        pct=$((classes * 100 / total_classes))
        echo -e "  ${RED}❌${NC} $module_name is bloated ($classes classes = $pct% of total)"
        echo "     Recommendation: Split into focused modules"
        echo ""
    fi
done

# Check for very small modules
small_modules=""
for module_dir in "$SOURCE_DIR"/*/ ; do
    if [ ! -d "$module_dir" ]; then
        continue
    fi

    module_name=$(basename "$module_dir")
    classes=$(count_items "${module_dir}classes.edn" ":user.class/")
    properties=$(count_items "${module_dir}properties.edn" ":user.property/")

    # Skip common and base modules
    if [ "$module_name" = "common" ] || [ "$module_name" = "base" ]; then
        continue
    fi

    if [ $classes -le 2 ] && [ $classes -gt 0 ]; then
        if [ -z "$small_modules" ]; then
            small_modules="$module_name"
        else
            small_modules="$small_modules, $module_name"
        fi
    fi
done

if [ -n "$small_modules" ]; then
    echo -e "  ${YELLOW}⚠️${NC}  Small modules: $small_modules"
    echo "     Options: Expand with related classes or merge"
    echo ""
fi

# Check for modules without README
no_readme=""
for module_dir in "$SOURCE_DIR"/*/ ; do
    if [ ! -d "$module_dir" ]; then
        continue
    fi

    module_name=$(basename "$module_dir")

    if [ ! -f "${module_dir}README.md" ]; then
        if [ -z "$no_readme" ]; then
            no_readme="$module_name"
        else
            no_readme="$no_readme, $module_name"
        fi
    fi
done

if [ -n "$no_readme" ]; then
    echo -e "  ${YELLOW}⚠️${NC}  Missing README: $no_readme"
    echo "     Recommendation: Add documentation"
    echo ""
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Run 'module-health' skill for detailed analysis and recommendations"
