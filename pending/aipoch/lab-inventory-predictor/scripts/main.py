#!/usr/bin/env python3
"""
Lab Inventory Predictor
Predicts depletion time of key reagents based on experiment frequency
and automatically generates purchase reminders.

ID: 107
"""

import json
import os
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field


@dataclass
class UsageRecord:
    """Usage record"""
    date: str
    amount: float
    experiment: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'UsageRecord':
        return cls(**data)


@dataclass
class Reagent:
    """Reagent information"""
    name: str
    current_stock: float
    unit: str = "ml"
    safety_stock: float = 0.0
    safety_days: int = 7
    lead_time_days: int = 3
    usage_history: List[UsageRecord] = field(default_factory=list)
    daily_consumption_rate: float = 0.0
    predicted_depletion_date: Optional[str] = None
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "current_stock": self.current_stock,
            "unit": self.unit,
            "safety_stock": self.safety_stock,
            "safety_days": self.safety_days,
            "lead_time_days": self.lead_time_days,
            "usage_history": [u.to_dict() for u in self.usage_history],
            "daily_consumption_rate": self.daily_consumption_rate,
            "predicted_depletion_date": self.predicted_depletion_date,
            "last_updated": self.last_updated
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Reagent':
        data = data.copy()
        data['usage_history'] = [UsageRecord.from_dict(u) for u in data.get('usage_history', [])]
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


class InventoryPredictor:
    """Main inventory predictor class"""
    
    DEFAULT_DATA_PATH = os.path.expanduser("~/.openclaw/workspace/data/lab-inventory.json")
    DEFAULT_LOOKBACK_DAYS = 30
    
    def __init__(self, data_path: Optional[str] = None):
        self.data_path = data_path or self.DEFAULT_DATA_PATH
        self.data = self._load_data()
    
    def _load_data(self) -> Dict:
        """Load data file"""
        if os.path.exists(self.data_path):
            with open(self.data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "settings": {
                "default_safety_days": 7,
                "default_lead_time_days": 3,
                "prediction_lookback_days": 30
            },
            "reagents": []
        }
    
    def _save_data(self):
        """Save data file"""
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        with open(self.data_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def _get_reagent(self, name: str) -> Optional[Reagent]:
        """Get reagent information"""
        for r in self.data['reagents']:
            if r['name'] == name:
                return Reagent.from_dict(r)
        return None
    
    def _save_reagent(self, reagent: Reagent):
        """Save reagent information"""
        for i, r in enumerate(self.data['reagents']):
            if r['name'] == reagent.name:
                self.data['reagents'][i] = reagent.to_dict()
                break
        else:
            self.data['reagents'].append(reagent.to_dict())
        self._save_data()
    
    def add_reagent(self, name: str, current_stock: float, unit: str = "ml",
                    safety_stock: float = 0.0, safety_days: int = 7, 
                    lead_time_days: int = 3) -> Dict:
        """Add new reagent"""
        if self._get_reagent(name):
            return {"success": False, "error": f"Reagent '{name}' already exists, use update-reagent instead"}
        
        reagent = Reagent(
            name=name,
            current_stock=current_stock,
            unit=unit,
            safety_stock=safety_stock,
            safety_days=safety_days,
            lead_time_days=lead_time_days
        )
        self._save_reagent(reagent)
        return {"success": True, "message": f"Reagent '{name}' added successfully"}
    
    def update_reagent(self, name: str, **kwargs) -> Dict:
        """Update reagent information"""
        reagent = self._get_reagent(name)
        if not reagent:
            return {"success": False, "error": f"Reagent '{name}' not found"}
        
        for key, value in kwargs.items():
            if hasattr(reagent, key) and value is not None:
                setattr(reagent, key, value)
        
        reagent.last_updated = datetime.now().isoformat()
        self._save_reagent(reagent)
        return {"success": True, "message": f"Reagent '{name}' updated successfully"}
    
    def record_usage(self, name: str, amount: float, experiment: str = "") -> Dict:
        """Record reagent usage"""
        reagent = self._get_reagent(name)
        if not reagent:
            return {"success": False, "error": f"Reagent '{name}' not found"}
        
        if amount > reagent.current_stock:
            return {"success": False, "error": f"Usage amount ({amount}) exceeds current stock ({reagent.current_stock})"}
        
        # Add usage record
        record = UsageRecord(
            date=datetime.now().strftime("%Y-%m-%d"),
            amount=amount,
            experiment=experiment
        )
        reagent.usage_history.append(record)
        reagent.current_stock -= amount
        reagent.last_updated = datetime.now().isoformat()
        
        # Recalculate consumption rate and prediction
        self._calculate_consumption_rate(reagent)
        self._predict_depletion(reagent)
        
        self._save_reagent(reagent)
        return {
            "success": True, 
            "message": f"Recorded usage of {amount} {reagent.unit}",
            "current_stock": reagent.current_stock,
            "predicted_depletion": reagent.predicted_depletion_date
        }
    
    def restock(self, name: str, amount: float) -> Dict:
        """Restock reagent"""
        reagent = self._get_reagent(name)
        if not reagent:
            return {"success": False, "error": f"Reagent '{name}' not found"}
        
        reagent.current_stock += amount
        reagent.last_updated = datetime.now().isoformat()
        
        # Re-predict
        self._predict_depletion(reagent)
        
        self._save_reagent(reagent)
        return {
            "success": True,
            "message": f"Restocked {amount} {reagent.unit}",
            "current_stock": reagent.current_stock,
            "predicted_depletion": reagent.predicted_depletion_date
        }
    
    def _calculate_consumption_rate(self, reagent: Reagent):
        """Calculate daily consumption rate"""
        lookback_days = self.data['settings'].get('prediction_lookback_days', 30)
        cutoff_date = datetime.now() - timedelta(days=lookback_days)
        
        recent_usage = [
            u for u in reagent.usage_history 
            if datetime.fromisoformat(u.date) >= cutoff_date
        ]
        
        if len(recent_usage) < 2:
            # Insufficient data, use all historical records
            recent_usage = reagent.usage_history
        
        if len(recent_usage) < 2:
            reagent.daily_consumption_rate = 0.0
            return
        
        total_usage = sum(u.amount for u in recent_usage)
        date_range = (datetime.now() - datetime.fromisoformat(recent_usage[0].date)).days
        date_range = max(date_range, 1)  # At least 1 day
        
        reagent.daily_consumption_rate = total_usage / date_range
    
    def _predict_depletion(self, reagent: Reagent):
        """Predict depletion date"""
        if reagent.daily_consumption_rate <= 0:
            reagent.predicted_depletion_date = None
            return
        
        days_until_depletion = reagent.current_stock / reagent.daily_consumption_rate
        depletion_date = datetime.now() + timedelta(days=days_until_depletion)
        reagent.predicted_depletion_date = depletion_date.strftime("%Y-%m-%d")
    
    def predict_depletion(self, name: str) -> Dict:
        """Get depletion prediction for a specified reagent"""
        reagent = self._get_reagent(name)
        if not reagent:
            return {"success": False, "error": f"Reagent '{name}' not found"}
        
        self._calculate_consumption_rate(reagent)
        self._predict_depletion(reagent)
        
        if reagent.predicted_depletion_date:
            days_left = (datetime.fromisoformat(reagent.predicted_depletion_date) - datetime.now()).days
            return {
                "success": True,
                "reagent": name,
                "current_stock": f"{reagent.current_stock} {reagent.unit}",
                "daily_consumption_rate": f"{reagent.daily_consumption_rate:.2f} {reagent.unit}/day",
                "predicted_depletion_date": reagent.predicted_depletion_date,
                "days_remaining": days_left
            }
        else:
            return {
                "success": True,
                "reagent": name,
                "current_stock": f"{reagent.current_stock} {reagent.unit}",
                "message": "Insufficient data to predict depletion time"
            }
    
    def get_alerts(self) -> Dict:
        """Get purchase reminders"""
        alerts = []
        now = datetime.now()
        
        for r_data in self.data['reagents']:
            reagent = Reagent.from_dict(r_data)
            self._calculate_consumption_rate(reagent)
            self._predict_depletion(reagent)
            
            alert_level = None
            alert_reason = []
            
            # Check safety stock
            if reagent.current_stock <= reagent.safety_stock:
                alert_level = "CRITICAL"
                alert_reason.append(f"Stock below safety level ({reagent.safety_stock} {reagent.unit})")
            
            # Check depletion time
            if reagent.predicted_depletion_date:
                depletion_date = datetime.fromisoformat(reagent.predicted_depletion_date)
                days_until = (depletion_date - now).days
                order_deadline = days_until - reagent.lead_time_days
                
                if days_until <= 0:
                    alert_level = "CRITICAL"
                    alert_reason.append("Stock depleted")
                elif days_until <= reagent.safety_days + reagent.lead_time_days:
                    alert_level = alert_level or "WARNING"
                    alert_reason.append(f"Estimated depletion in {days_until} days")
                
                if order_deadline <= 0:
                    alert_reason.append(f"⚠️ Past purchase deadline ({reagent.lead_time_days} day lead time)")
                elif order_deadline <= 3:
                    alert_reason.append(f"Recommend ordering within {order_deadline} days")
            
            if alert_level:
                alerts.append({
                    "reagent": reagent.name,
                    "level": alert_level,
                    "current_stock": f"{reagent.current_stock} {reagent.unit}",
                    "reason": "; ".join(alert_reason),
                    "predicted_depletion": reagent.predicted_depletion_date
                })
        
        # Sort by urgency
        alerts.sort(key=lambda x: (0 if x['level'] == 'CRITICAL' else 1))
        
        return {
            "success": True,
            "alert_count": len(alerts),
            "alerts": alerts
        }
    
    def get_status(self) -> Dict:
        """Get status of all reagents"""
        status_list = []
        
        for r_data in self.data['reagents']:
            reagent = Reagent.from_dict(r_data)
            self._calculate_consumption_rate(reagent)
            self._predict_depletion(reagent)
            
            status = "normal"
            if reagent.predicted_depletion_date:
                days_left = (datetime.fromisoformat(reagent.predicted_depletion_date) - datetime.now()).days
                if days_left <= reagent.lead_time_days + reagent.safety_days:
                    status = "warning"
                if reagent.current_stock <= reagent.safety_stock:
                    status = "critical"
            
            status_list.append({
                "name": reagent.name,
                "current_stock": f"{reagent.current_stock} {reagent.unit}",
                "daily_consumption": f"{reagent.daily_consumption_rate:.2f} {reagent.unit}/day" if reagent.daily_consumption_rate > 0 else "N/A",
                "predicted_depletion": reagent.predicted_depletion_date or "N/A",
                "status": status
            })
        
        return {
            "success": True,
            "total_reagents": len(status_list),
            "reagents": status_list
        }
    
    def generate_report(self) -> Dict:
        """Generate complete report"""
        status = self.get_status()
        alerts = self.get_alerts()
        
        critical_count = sum(1 for a in alerts['alerts'] if a['level'] == 'CRITICAL')
        warning_count = sum(1 for a in alerts['alerts'] if a['level'] == 'WARNING')
        
        report = {
            "success": True,
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_reagents": status['total_reagents'],
                "critical_alerts": critical_count,
                "warning_alerts": warning_count
            },
            "alerts": alerts['alerts'],
            "inventory_status": status['reagents']
        }
        
        return report
    
    def remove_reagent(self, name: str) -> Dict:
        """Remove reagent"""
        for i, r in enumerate(self.data['reagents']):
            if r['name'] == name:
                del self.data['reagents'][i]
                self._save_data()
                return {"success": True, "message": f"Reagent '{name}' removed"}
        return {"success": False, "error": f"Reagent '{name}' not found"}


def main():
    """Command line entry point"""
    parser = argparse.ArgumentParser(description='Lab Inventory Predictor - Laboratory inventory prediction tool')
    parser.add_argument('--data-path', help='Data file path')
    parser.add_argument('--action', required=True,
                        choices=['add-reagent', 'update-reagent', 'remove-reagent',
                                'record-usage', 'restock', 'status', 'alerts', 
                                'report', 'predict', 'list'],
                        help='Action to perform')
    
    # Reagent-related parameters
    parser.add_argument('--name', help='Reagent name')
    parser.add_argument('--current-stock', type=float, help='Current stock quantity')
    parser.add_argument('--unit', default='ml', help='Unit (default: ml)')
    parser.add_argument('--safety-stock', type=float, help='Safety stock quantity')
    parser.add_argument('--safety-days', type=int, help='Safety stock days')
    parser.add_argument('--lead-time-days', type=int, help='Purchase lead time (days)')
    
    # Usage record parameters
    parser.add_argument('--amount', type=float, help='Usage or restock amount')
    parser.add_argument('--experiment', default='', help='Experiment name/number')
    
    # Output format
    parser.add_argument('--json', action='store_true', help='Output in JSON format')
    
    args = parser.parse_args()
    
    # Initialize predictor
    predictor = InventoryPredictor(args.data_path)
    
    # Execute action
    result = None
    
    if args.action == 'add-reagent':
        if not args.name or args.current_stock is None:
            result = {"success": False, "error": "Missing required parameters: --name and --current-stock"}
        else:
            result = predictor.add_reagent(
                name=args.name,
                current_stock=args.current_stock,
                unit=args.unit,
                safety_stock=args.safety_stock or 0.0,
                safety_days=args.safety_days or 7,
                lead_time_days=args.lead_time_days or 3
            )
    
    elif args.action == 'update-reagent':
        if not args.name:
            result = {"success": False, "error": "Missing required parameter: --name"}
        else:
            result = predictor.update_reagent(
                name=args.name,
                current_stock=args.current_stock,
                unit=args.unit,
                safety_stock=args.safety_stock,
                safety_days=args.safety_days,
                lead_time_days=args.lead_time_days
            )
    
    elif args.action == 'remove-reagent':
        if not args.name:
            result = {"success": False, "error": "Missing required parameter: --name"}
        else:
            result = predictor.remove_reagent(args.name)
    
    elif args.action == 'record-usage':
        if not args.name or args.amount is None:
            result = {"success": False, "error": "Missing required parameters: --name and --amount"}
        else:
            result = predictor.record_usage(args.name, args.amount, args.experiment)
    
    elif args.action == 'restock':
        if not args.name or args.amount is None:
            result = {"success": False, "error": "Missing required parameters: --name and --amount"}
        else:
            result = predictor.restock(args.name, args.amount)
    
    elif args.action == 'status' or args.action == 'list':
        result = predictor.get_status()
    
    elif args.action == 'alerts':
        result = predictor.get_alerts()
    
    elif args.action == 'report':
        result = predictor.generate_report()
    
    elif args.action == 'predict':
        if not args.name:
            result = {"success": False, "error": "Missing required parameter: --name"}
        else:
            result = predictor.predict_depletion(args.name)
    
    # Output result
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        _print_formatted(result)
    
    # Set exit code based on result
    sys.exit(0 if result.get('success', True) else 1)


def _print_formatted(result: Dict):
    """Format and print result"""
    if not result.get('success', True):
        print(f"❌ Error: {result.get('error', 'Unknown error')}")
        return
    
    # Add reagent
    if 'message' in result and 'added' in result['message']:
        print(f"✅ {result['message']}")
        return
    
    # Record usage
    if 'current_stock' in result and 'message' in result and 'Recorded' in result['message']:
        print(f"✅ {result['message']}")
        print(f"   Current stock: {result['current_stock']}")
        if 'predicted_depletion' in result:
            print(f"   Predicted depletion: {result['predicted_depletion']}")
        return
    
    # Restock
    if 'message' in result and 'Restocked' in result['message']:
        print(f"✅ {result['message']}")
        print(f"   Current stock: {result['current_stock']}")
        return
    
    # Prediction result
    if 'reagent' in result and 'daily_consumption_rate' in result:
        print(f"\n📊 Reagent: {result['reagent']}")
        print(f"   Current stock: {result['current_stock']}")
        print(f"   Daily consumption: {result['daily_consumption_rate']}")
        if 'predicted_depletion_date' in result:
            print(f"   Predicted depletion: {result['predicted_depletion_date']} ({result['days_remaining']} days remaining)")
        else:
            print(f"   {result.get('message', '')}")
        return
    
    # Alert list
    if 'alerts' in result and 'alert_count' in result:
        print(f"\n🚨 Purchase Reminders ({result['alert_count']} total)\n")
        if result['alert_count'] == 0:
            print("   ✅ All reagents have sufficient stock")
            return
        
        for alert in result['alerts']:
            icon = "🔴" if alert['level'] == 'CRITICAL' else "🟡"
            print(f"{icon} [{alert['level']}] {alert['reagent']}")
            print(f"   Current stock: {alert['current_stock']}")
            print(f"   Reason: {alert['reason']}")
            if alert.get('predicted_depletion'):
                print(f"   Predicted depletion: {alert['predicted_depletion']}")
            print()
        return
    
    # Status list
    if 'reagents' in result:
        print(f"\n📋 Inventory Status ({result['total_reagents']} reagents total)\n")
        print(f"{'Reagent Name':<20} {'Current Stock':<15} {'Daily Consumption':<18} {'Predicted Depletion':<20} {'Status':<10}")
        print("-" * 90)
        
        for r in result['reagents']:
            status_icon = {"normal": "🟢", "warning": "🟡", "critical": "🔴"}.get(r['status'], "⚪")
            print(f"{r['name']:<20} {r['current_stock']:<15} {r['daily_consumption']:<18} {r['predicted_depletion']:<20} {status_icon} {r['status']}")
        return
    
    # Report
    if 'summary' in result:
        print(f"\n📑 Inventory Prediction Report")
        print(f"   Generated at: {result['generated_at']}")
        print(f"\n📊 Summary")
        print(f"   Total reagents: {result['summary']['total_reagents']}")
        print(f"   Critical alerts: {result['summary']['critical_alerts']}")
        print(f"   Warning alerts: {result['summary']['warning_alerts']}")
        
        if result['alerts']:
            print(f"\n🚨 Reagents requiring attention:")
            for alert in result['alerts']:
                icon = "🔴" if alert['level'] == 'CRITICAL' else "🟡"
                print(f"   {icon} {alert['reagent']}: {alert['reason']}")
        return
    
    # Default output
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
