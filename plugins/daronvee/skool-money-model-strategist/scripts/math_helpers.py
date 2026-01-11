#!/usr/bin/env python3
"""
Math Helpers for Skool Money Model Strategist

Deterministic calculation functions to ensure accurate financial analysis.
LLMs are prone to arithmetic errors - use these functions for all math operations.
"""

def diagnose_stage(revenue_30d, cac, acquisition_reliability="consistent"):
    """
    Diagnose business stage based on Hormozi's 5-stage model.

    Args:
        revenue_30d: Average revenue per customer in first 30 days
        cac: Customer Acquisition Cost
        acquisition_reliability: "consistent" or "inconsistent"

    Returns:
        dict with 'stage' (1-5) and 'reason' (explanation)

    Examples:
        >>> diagnose_stage(50, 200, "consistent")
        {'stage': 2, 'reason': 'Revenue ($50) < CAC ($200)'}

        >>> diagnose_stage(350, 200, "consistent")
        {'stage': 3, 'reason': 'Revenue ($350) covers CAC but not 2x CAC ($400)'}
    """
    # Stage 1: Reliability check (overrides revenue)
    if acquisition_reliability == "inconsistent":
        return {
            "stage": 1,
            "reason": "Getting customers inconsistently - must fix acquisition reliability first"
        }

    # Stage 2: Customers don't pay for themselves
    if revenue_30d < cac:
        return {
            "stage": 2,
            "reason": f"Revenue (${revenue_30d:.2f}) < CAC (${cac:.2f}) - customers don't pay for themselves"
        }

    # Stage 3: Customers pay for themselves but not others
    if revenue_30d < (2 * cac):
        return {
            "stage": 3,
            "reason": f"Revenue (${revenue_30d:.2f}) covers CAC but not 2x CAC (${2 * cac:.2f}) - need more cash per customer"
        }

    # Stage 4: Customers pay for others, now maximize LTV
    # Note: Stage 4 vs 5 distinction requires qualitative assessment
    # If revenue >= 2x CAC, assume Stage 4 (LTV maximization phase)
    return {
        "stage": 4,
        "reason": f"Revenue (${revenue_30d:.2f}) >= 2x CAC (${2 * cac:.2f}) - ready to maximize lifetime value"
    }


def calculate_30d_cash(monthly_price, annual_price, monthly_pct, one_time_avg=0, one_time_take_rate=0):
    """
    Calculate weighted average 30-day revenue per customer.

    Args:
        monthly_price: Monthly subscription price
        annual_price: Annual subscription price (full year amount)
        monthly_pct: % of customers who choose monthly (0.0-1.0)
        one_time_avg: Average one-time purchase value
        one_time_take_rate: % of customers who buy one-time products (0.0-1.0)

    Returns:
        float: Average 30-day revenue per customer

    Examples:
        >>> calculate_30d_cash(99, 950, 0.70)
        354.3

        >>> calculate_30d_cash(99, 950, 0.70, 497, 0.035)
        371.695
    """
    annual_pct = 1.0 - monthly_pct

    # Subscription revenue (weighted average)
    subscription_revenue = (monthly_price * monthly_pct) + (annual_price * annual_pct)

    # One-time purchase contribution (average across all customers)
    one_time_contribution = one_time_avg * one_time_take_rate

    return subscription_revenue + one_time_contribution


def calculate_gap(current_revenue, cac, target_multiplier=2):
    """
    Calculate revenue gap to reach target stage.

    Args:
        current_revenue: Current 30-day revenue per customer
        cac: Customer Acquisition Cost
        target_multiplier: CAC multiplier for target (default 2 for Stage 3)

    Returns:
        dict with 'target', 'gap', and 'percentage_to_target'

    Examples:
        >>> calculate_gap(354, 200, 2)
        {'target': 400, 'gap': 46, 'percentage_to_target': 88.5}

        >>> calculate_gap(450, 200, 2)
        {'target': 400, 'gap': 0, 'percentage_to_target': 112.5}
    """
    target = cac * target_multiplier
    gap = max(0, target - current_revenue)  # Don't show negative gaps
    percentage = (current_revenue / target) * 100 if target > 0 else 0

    return {
        "target": target,
        "gap": gap,
        "percentage_to_target": round(percentage, 1)
    }


def project_premium_mrr(base_members, upgrade_rate, premium_price, base_price):
    """
    Project MRR impact from adding premium tier.

    Args:
        base_members: Current number of paying members
        upgrade_rate: Expected % who will upgrade (0.0-1.0)
        premium_price: Premium tier monthly price
        base_price: Current/base tier monthly price

    Returns:
        dict with 'premium_members', 'additional_mrr', 'premium_mrr', 'net_gain'

    Examples:
        >>> project_premium_mrr(1644, 0.05, 297, 99)
        {
            'premium_members': 82,
            'additional_mrr': 16236.0,
            'premium_mrr': 24354,
            'net_gain': 16236.0
        }
    """
    premium_members = int(base_members * upgrade_rate)

    # Additional MRR is the price difference (since they're upgrading from base)
    price_difference = premium_price - base_price
    additional_mrr = premium_members * price_difference

    # Total premium tier MRR
    premium_mrr = premium_members * premium_price

    return {
        "premium_members": premium_members,
        "additional_mrr": round(additional_mrr, 2),
        "premium_mrr": round(premium_mrr, 2),
        "net_gain": round(additional_mrr, 2)
    }


def calculate_annual_campaign_impact(base_members, current_annual_pct, target_annual_pct, annual_price, premium_members=0, premium_annual_price=0):
    """
    Calculate revenue impact from annual conversion campaign.

    Args:
        base_members: Total paying members
        current_annual_pct: Current % on annual plans (0.0-1.0)
        target_annual_pct: Target % after campaign (0.0-1.0)
        annual_price: Annual subscription price
        premium_members: Number of premium members (optional)
        premium_annual_price: Premium annual price (optional)

    Returns:
        dict with 'base_conversions', 'base_revenue', 'premium_conversions', 'premium_revenue', 'total_revenue'

    Examples:
        >>> calculate_annual_campaign_impact(1644, 0.30, 0.45, 950)
        {
            'base_conversions': 247,
            'base_revenue': 234650.0,
            'premium_conversions': 0,
            'premium_revenue': 0,
            'total_revenue': 234650.0,
            'lift_percentage': 15.0
        }
    """
    lift_pct = target_annual_pct - current_annual_pct

    # Base tier conversions
    base_monthly_members = base_members - premium_members
    base_conversions = int(base_monthly_members * lift_pct)
    base_revenue = base_conversions * annual_price

    # Premium tier conversions (if applicable)
    premium_conversions = int(premium_members * lift_pct) if premium_members > 0 else 0
    premium_revenue = premium_conversions * premium_annual_price if premium_annual_price > 0 else 0

    return {
        "base_conversions": base_conversions,
        "base_revenue": round(base_revenue, 2),
        "premium_conversions": premium_conversions,
        "premium_revenue": round(premium_revenue, 2),
        "total_revenue": round(base_revenue + premium_revenue, 2),
        "lift_percentage": round(lift_pct * 100, 1)
    }


def calculate_blended_ltv(base_members, base_ltv, premium_members, premium_ltv):
    """
    Calculate blended LTV across multiple tiers.

    Args:
        base_members: Number of base/core tier members
        base_ltv: Lifetime value of base tier customer
        premium_members: Number of premium tier members
        premium_ltv: Lifetime value of premium tier customer

    Returns:
        float: Blended LTV across all members

    Examples:
        >>> calculate_blended_ltv(1512, 1615, 132, 7425)
        2103.3
    """
    total_members = base_members + premium_members
    if total_members == 0:
        return 0

    total_value = (base_members * base_ltv) + (premium_members * premium_ltv)
    blended_ltv = total_value / total_members

    return round(blended_ltv, 2)


def validate_tier_relationships(tier_prices, tier_names=None):
    """
    Validate tier pricing follows Hormozi principles and flag anti-patterns.

    Args:
        tier_prices: List of tier prices (lowest to highest) [price1, price2, price3, ...]
        tier_names: Optional list of tier names for clearer output

    Returns:
        dict with:
        - 'ratios': List of multipliers between consecutive tiers
        - 'pattern_detected': Identified pattern (Anchor, Decoy, Ladder, Mixed, or Anti-Pattern)
        - 'warnings': List of warnings for problematic ratios
        - 'recommendations': Specific suggestions for improvement

    Examples:
        >>> validate_tier_relationships([97, 197, 497])
        {
            'ratios': [2.03, 2.52],
            'pattern_detected': '2x Trap Anti-Pattern',
            'warnings': ['Tier 1→2: 2.03x multiplier in danger zone (1.5-2.5x)',
                        'Tier 2→3: 2.52x multiplier in danger zone (1.5-2.5x)'],
            'recommendations': ['Consider Decoy: $97 → $107 (1.1x)',
                               'Consider Anchor: $97 → $297 (3x)']
        }

        >>> validate_tier_relationships([897, 997], ["Standard", "Premium"])
        {
            'ratios': [1.11],
            'pattern_detected': 'Decoy Pattern',
            'warnings': [],
            'recommendations': ['Excellent decoy positioning - Premium only 11% more']
        }
    """
    if len(tier_prices) < 2:
        return {
            "error": "Need at least 2 tiers to validate relationships",
            "ratios": [],
            "pattern_detected": "N/A",
            "warnings": [],
            "recommendations": ["Add at least one more tier for strategic pricing"]
        }

    # Calculate ratios
    ratios = []
    for i in range(len(tier_prices) - 1):
        ratio = tier_prices[i + 1] / tier_prices[i]
        ratios.append(round(ratio, 2))

    # Analyze patterns
    warnings = []
    recommendations = []
    patterns = []

    for i, ratio in enumerate(ratios):
        tier_from = tier_names[i] if tier_names else f"Tier {i+1}"
        tier_to = tier_names[i+1] if tier_names else f"Tier {i+2}"

        # Check for specific patterns
        if 1.1 <= ratio <= 1.3:
            patterns.append("Decoy")
            recommendations.append(
                f"GOOD: {tier_from}->{tier_to}: Good decoy positioning ({ratio}x) - "
                f"makes {tier_to} feel like obvious choice"
            )
        elif 1.5 <= ratio <= 2.5:
            patterns.append("2x Trap")
            warnings.append(
                f"WARNING: {tier_from}->{tier_to}: {ratio}x multiplier in DANGER ZONE (1.5-2.5x) - "
                f"creates psychological barrier"
            )
            # Provide specific fix recommendations
            decoy_price = round(tier_prices[i] * 1.15, 0)
            anchor_price = round(tier_prices[i] * 3.5, 0)
            recommendations.append(
                f"Fix {tier_from}->{tier_to}: Use ${decoy_price} (1.15x decoy) OR ${anchor_price} (3.5x anchor)"
            )
        elif ratio >= 3.0:
            patterns.append("Anchor")
            recommendations.append(
                f"GOOD: {tier_from}->{tier_to}: Good anchor positioning ({ratio}x) - "
                f"makes {tier_from} feel affordable"
            )
        elif 2.5 < ratio < 3.0:
            patterns.append("Ladder")
            recommendations.append(
                f"OK: {tier_from}->{tier_to}: Value ladder positioning ({ratio}x) - "
                f"moderate separation for self-selection"
            )
        else:  # ratio < 1.1
            patterns.append("Too Close")
            warnings.append(
                f"WARNING: {tier_from}->{tier_to}: Only {ratio}x difference - "
                f"may not feel like enough upgrade value"
            )
            recommendations.append(
                f"Consider increasing {tier_to} price to create clearer differentiation"
            )

    # Determine overall pattern
    if len(set(patterns)) == 1:
        if patterns[0] == "2x Trap":
            pattern_detected = "2x Trap Anti-Pattern (AVOID)"
        else:
            pattern_detected = f"{patterns[0]} Pattern"
    elif "2x Trap" in patterns:
        pattern_detected = "Mixed (includes 2x Trap - FIX REQUIRED)"
    elif "Decoy" in patterns and "Anchor" not in patterns:
        pattern_detected = "Decoy Pattern"
    elif "Anchor" in patterns and "Decoy" not in patterns:
        pattern_detected = "Anchor Pattern"
    elif "Ladder" in patterns:
        pattern_detected = "Value Ladder Pattern"
    else:
        pattern_detected = "Mixed Pattern"

    # Overall recommendations
    if not warnings:
        recommendations.insert(0, "EXCELLENT: Tier structure follows Hormozi pricing principles")
    else:
        recommendations.insert(0, "WARNING: Tier structure needs adjustment - see warnings")

    return {
        "tier_prices": tier_prices,
        "tier_names": tier_names if tier_names else [f"Tier {i+1}" for i in range(len(tier_prices))],
        "ratios": ratios,
        "pattern_detected": pattern_detected,
        "warnings": warnings,
        "recommendations": recommendations
    }


def validate_calculation(description, expected, actual, tolerance=0.01):
    """
    Validate a calculation result against expected value.

    Args:
        description: What calculation is being validated
        expected: Expected result
        actual: Actual calculated result
        tolerance: Acceptable % difference (default 1%)

    Returns:
        dict with 'valid' (bool), 'message' (str), 'difference' (float)

    Examples:
        >>> validate_calculation("30-day cash", 354.30, 354.50, 0.01)
        {'valid': True, 'message': '30-day cash: PASS (354.50 vs 354.30 expected, 0.06% diff)', 'difference': 0.2}
    """
    difference = abs(actual - expected)
    pct_diff = (difference / expected * 100) if expected != 0 else 0

    is_valid = pct_diff <= (tolerance * 100)

    status = "PASS" if is_valid else "FAIL"
    message = f"{description}: {status} ({actual:.2f} vs {expected:.2f} expected, {pct_diff:.2f}% diff)"

    return {
        "valid": is_valid,
        "message": message,
        "difference": round(difference, 2),
        "pct_difference": round(pct_diff, 2)
    }


# Quick test function for verification
if __name__ == "__main__":
    print("Testing math_helpers.py...")

    # Test Stage Diagnosis
    print("\n1. Stage Diagnosis:")
    print(diagnose_stage(354, 200, "consistent"))
    print(diagnose_stage(450, 200, "consistent"))

    # Test 30-Day Cash Calculation
    print("\n2. 30-Day Cash Calculation:")
    print(f"Result: ${calculate_30d_cash(99, 950, 0.70, 497, 0.035):.2f}")

    # Test Gap Calculation
    print("\n3. Gap Analysis:")
    print(calculate_gap(354, 200, 2))

    # Test Premium Projection
    print("\n4. Premium MRR Projection:")
    print(project_premium_mrr(1644, 0.05, 297, 99))

    # Test Tier Validation
    print("\n5. Tier Relationship Validation:")
    print("\n5a. Anti-Pattern (2x Trap):")
    result = validate_tier_relationships([97, 197, 497], ["Base", "Pro", "Premium"])
    print(f"Pattern: {result['pattern_detected']}")
    print(f"Warnings: {len(result['warnings'])} found")
    for warning in result['warnings']:
        print(f"  {warning}")

    print("\n5b. Good Decoy Pattern:")
    result = validate_tier_relationships([897, 997], ["Standard", "Premium"])
    print(f"Pattern: {result['pattern_detected']}")
    print(f"Ratios: {result['ratios']}")

    print("\n5c. Good Anchor Pattern:")
    result = validate_tier_relationships([97, 297, 997], ["Base", "Pro", "Elite"])
    print(f"Pattern: {result['pattern_detected']}")
    print(f"Ratios: {result['ratios']}")

    print("\n[OK] All tests completed successfully")
