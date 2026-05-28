#!/usr/bin/env python3
"""Competitor Trial Monitor - Competitor Clinical Trial Monitor
Monitor the progress of clinical trials of competing products and provide early warning of market risks."""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import urllib.request
import urllib.parse

# data directory
DATA_DIR = Path.home() / ".openclaw" / "competitor-trial-monitor"
WATCHLIST_FILE = DATA_DIR / "watchlist.json"
HISTORY_DIR = DATA_DIR / "history"
ALERTS_DIR = DATA_DIR / "alerts"
CONFIG_FILE = DATA_DIR / "config.json"

# ClinicalTrials.gov API
CT_API_BASE = "https://clinicaltrials.gov/api/v2/studies"


def init_data_dir():
    """Initialize data directory"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    HISTORY_DIR.mkdir(exist_ok=True)
    ALERTS_DIR.mkdir(exist_ok=True)


def load_watchlist() -> List[Dict]:
    """Load monitoring list"""
    if not WATCHLIST_FILE.exists():
        return []
    with open(WATCHLIST_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_watchlist(watchlist: List[Dict]):
    """Save monitoring list"""
    with open(WATCHLIST_FILE, 'w', encoding='utf-8') as f:
        json.dump(watchlist, f, indent=2, ensure_ascii=False)


def load_config() -> Dict:
    """Load configuration"""
    if not CONFIG_FILE.exists():
        return {
            "alert_channels": ["console"],
            "scan_interval_hours": 24,
            "risk_threshold": "medium"
        }
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def fetch_trial_data(nct_id: str) -> Optional[Dict]:
    """Obtain trial data from ClinicalTrials.gov"""
    url = f"{CT_API_BASE}/{nct_id}"
    headers = {
        "Accept": "application/json"
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"  ⚠️  test {nct_id} not found")
        else:
            print(f"  ❌ HTTPmistake {e.code}: {e.reason}")
        return None
    except Exception as e:
        print(f"  ❌ Failed to get data: {e}")
        return None


def extract_key_info(trial_data: Dict) -> Dict:
    """Extract key test information"""
    protocol = trial_data.get("protocolSection", {})
    
    # Basic information
    identification = protocol.get("identificationModule", {})
    status = protocol.get("statusModule", {})
    design = protocol.get("designModule", {})
    
    return {
        "nct_id": identification.get("nctId", "N/A"),
        "title": identification.get("briefTitle", "N/A"),
        "status": status.get("overallStatus", "Unknown"),
        "phase": design.get("phases", ["Unknown"])[0] if design.get("phases") else "Unknown",
        "enrollment": design.get("enrollmentInfo", {}).get("count", 0),
        "start_date": status.get("startDateStruct", {}).get("date", "N/A"),
        "completion_date": status.get("completionDateStruct", {}).get("date", "N/A"),
        "has_results": trial_data.get("resultsSection", {}) is not None,
        "last_update": status.get("lastUpdatePostDateStruct", {}).get("date", "N/A")
    }


def assess_risk(old_info: Optional[Dict], new_info: Dict) -> Optional[Dict]:
    """Assess changes in risk"""
    if old_info is None:
        return None
    
    alerts = []
    risk_level = None
    
    # Check status changes
    old_status = old_info.get("status", "")
    new_status = new_info.get("status", "")
    
    status_risk_map = {
        "COMPLETED": ("high", "The trial has been completed and the results may be announced soon"),
        "AVAILABLE": ("critical", "Results published"),
        "APPROVED": ("critical", "Approved for listing"),
        "REGULATORY_SUBMISSION": ("high", "Regulatory application submitted")
    }
    
    if old_status != new_status and new_status in status_risk_map:
        risk_level, message = status_risk_map[new_status]
        alerts.append(f"status change: {old_status} → {new_status}")
        alerts.append(message)
    
    # Check if there are any results
    if not old_info.get("has_results") and new_info.get("has_results"):
        risk_level = "high"
        alerts.append("Test results have been released")
    
    if alerts:
        return {
            "risk_level": risk_level or "medium",
            "alerts": alerts,
            "timestamp": datetime.now().isoformat()
        }
    return None


def cmd_add(args):
    """Add monitoring target"""
    watchlist = load_watchlist()
    
    # Check if it already exists
    for item in watchlist:
        if item.get("nct_id") == args.nct:
            print(f"⚠️  NCT {args.nct} Already in the monitoring list")
            return
    
    # Verify test exists
    print(f"🔍 Verification test {args.nct}...")
    trial_data = fetch_trial_data(args.nct)
    if not trial_data:
        print(f"❌ Unable to add: test {args.nct} not found orAPImistake")
        return
    
    info = extract_key_info(trial_data)
    
    watchlist.append({
        "nct_id": args.nct,
        "company": args.company or "Unknown",
        "drug": args.drug or "Unknown",
        "indication": args.indication or "Unknown",
        "added_at": datetime.now().isoformat(),
        "last_check": None,
        "last_data": info
    })
    
    save_watchlist(watchlist)
    print(f"✅ Added: {info['title'][:60]}...")
    print(f"   company: {args.company or 'Unknown'}")
    print(f"   drug: {args.drug or 'Unknown'}")
    print(f"   state: {info['status']}")


def cmd_list(args):
    """List monitoring targets"""
    watchlist = load_watchlist()
    
    if not watchlist:
        print("📭 Monitoring list is empty")
        return
    
    print(f"\n📋 Total monitoring {len(watchlist)} clinical trials:\n")
    print(f"{'NCT ID':<15} {'company':<15} {'drug':<20} {'state':<15} {'final check':<20}")
    print("-" * 90)
    
    for item in watchlist:
        nct = item.get("nct_id", "N/A")
        company = item.get("company", "Unknown")[:14]
        drug = item.get("drug", "Unknown")[:19]
        status = (item.get("last_data", {}) or {}).get("status", "Unknown")[:14]
        last_check = item.get("last_check", "Never")[:19] if item.get("last_check") else "Never"
        
        print(f"{nct:<15} {company:<15} {drug:<20} {status:<15} {last_check:<20}")


def cmd_remove(args):
    """Remove monitoring target"""
    watchlist = load_watchlist()
    
    original_len = len(watchlist)
    watchlist = [item for item in watchlist if item.get("nct_id") != args.nct]
    
    if len(watchlist) == original_len:
        print(f"⚠️  NCT {args.nct} Not in the watch list")
        return
    
    save_watchlist(watchlist)
    print(f"✅ Deleted NCT {args.nct}")


def cmd_scan(args):
    """Scan for updates"""
    watchlist = load_watchlist()
    
    if not watchlist:
        print("📭 Monitoring list is empty")
        return
    
    print(f"🔍 Start scanning {len(watchlist)} trials...\n")
    
    alerts = []
    updated = 0
    
    for item in watchlist:
        nct_id = item.get("nct_id")
        print(f"examine {nct_id} ({item.get('company', 'Unknown')})...")
        
        trial_data = fetch_trial_data(nct_id)
        if not trial_data:
            continue
        
        new_info = extract_key_info(trial_data)
        old_info = item.get("last_data")
        
        # Check risks
        risk = assess_risk(old_info, new_info)
        if risk:
            alert = {
                "nct_id": nct_id,
                "company": item.get("company"),
                "drug": item.get("drug"),
                **risk
            }
            alerts.append(alert)
            print(f"  🚨 Risk warning [{risk['risk_level'].upper()}]")
            for msg in risk['alerts']:
                print(f"     - {msg}")
        
        # Update data
        item["last_data"] = new_info
        item["last_check"] = datetime.now().isoformat()
        updated += 1
        
        if not risk:
            print(f"  ✅ English")
    
    save_watchlist(watchlist)
    
    # Save alert
    if alerts:
        alert_file = ALERTS_DIR / f"alerts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(alert_file, 'w', encoding='utf-8') as f:
            json.dump(alerts, f, indent=2, ensure_ascii=False)
        print(f"\n🚨 Discover {len(alerts)} risk warning")
        print(f"   Alert saved: {alert_file}")
    
    print(f"\n✅ Scan completed，updated {updated} trials")


def cmd_report(args):
    """Generate risk report"""
    watchlist = load_watchlist()
    days = args.days or 30
    
    if not watchlist:
        print("📭 Monitoring list is empty")
        return
    
    cutoff = datetime.now() - timedelta(days=days)
    
    # Collect all warnings
    all_alerts = []
    for alert_file in ALERTS_DIR.glob("alerts_*.json"):
        try:
            with open(alert_file, 'r', encoding='utf-8') as f:
                alerts = json.load(f)
                for alert in alerts:
                    alert_time = datetime.fromisoformat(alert.get("timestamp", ""))
                    if alert_time >= cutoff:
                        all_alerts.append(alert)
        except:
            pass
    
    print(f"\n📊 Competitive product clinical trial risk report (close{days}sky)\n")
    print("=" * 60)
    
    if not all_alerts:
        print("✅ No risk warning found")
        return
    
    # Group by risk level
    critical = [a for a in all_alerts if a.get("risk_level") == "critical"]
    high = [a for a in all_alerts if a.get("risk_level") == "high"]
    medium = [a for a in all_alerts if a.get("risk_level") == "medium"]
    
    print(f"🔴 Critical: {len(critical)}")
    for alert in critical:
        print(f"   [{alert['nct_id']}] {alert.get('company', 'Unknown')} - {alert.get('drug', 'Unknown')}")
        for msg in alert.get("alerts", []):
            print(f"      • {msg}")
    
    print(f"\n🟠 High: {len(high)}")
    for alert in high:
        print(f"   [{alert['nct_id']}] {alert.get('company', 'Unknown')} - {alert.get('drug', 'Unknown')}")
        for msg in alert.get("alerts", []):
            print(f"      • {msg}")
    
    print(f"\n🟡 Medium: {len(medium)}")
    for alert in medium[:5]:  # Only show the first 5
        print(f"   [{alert['nct_id']}] {alert.get('company', 'Unknown')} - {alert.get('drug', 'Unknown')}")
    if len(medium) > 5:
        print(f"   ... English {len(medium) - 5} indivual")
    
    print("\n" + "=" * 60)
    print(f"total: {len(all_alerts)} warning event")


def main():
    parser = argparse.ArgumentParser(
        description="Competitor Trial Monitor - Competitor Clinical Trial Monitor",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # add command
    add_parser = subparsers.add_parser("add", help="Add monitoring target")
    add_parser.add_argument("--nct", required=True, help="ClinicalTrials.gov NCT ID")
    add_parser.add_argument("--company", help="Competing company name")
    add_parser.add_argument("--drug", help="Drug name")
    add_parser.add_argument("--indication", help="Indications")
    add_parser.set_defaults(func=cmd_add)
    
    # list command
    list_parser = subparsers.add_parser("list", help="List monitoring targets")
    list_parser.set_defaults(func=cmd_list)
    
    # remove command
    remove_parser = subparsers.add_parser("remove", help="Remove monitoring target")
    remove_parser.add_argument("--nct", required=True, help="NCT ID to delete")
    remove_parser.set_defaults(func=cmd_remove)
    
    # scan command
    scan_parser = subparsers.add_parser("scan", help="Scan for updates")
    scan_parser.set_defaults(func=cmd_scan)
    
    # report command
    report_parser = subparsers.add_parser("report", help="Generate risk report")
    report_parser.add_argument("--days", type=int, default=30, help="Reporting time range (days)")
    report_parser.set_defaults(func=cmd_report)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    init_data_dir()
    args.func(args)


if __name__ == "__main__":
    main()
