from typing import List, Dict, Optional, Tuple
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime
from dataclasses import dataclass

@dataclass
class TransactionPeriod:
    period: str
    cc_volume: float
    cc_count: int
    ach_volume: float
    ach_count: int
    cc_rate: float
    conv_fee: float

class ROIEngine:
    SUBSCRIPTION_COST = 170000  # Cost of platform subscription
    TARGET_PERIODS_TO_ROI = 24  # Expected to achieve ROI within 24 periods
    ACH_COST_PER_TRANSACTION = 0.25  # Fixed cost per ACH transaction
    
    def __init__(self):
        self.periods: List[TransactionPeriod] = []
        
    def add_period(self, period: TransactionPeriod):
        self.periods.append(period)
        
    def get_periods(self) -> List[Dict]:
        """
        Returns all transaction periods as a list of dictionaries.
        Each dictionary contains the period data in a format suitable for API responses.
        """
        return [
            {
                "period": p.period,
                "cc_volume": p.cc_volume,
                "cc_count": p.cc_count,
                "ach_volume": p.ach_volume,
                "ach_count": p.ach_count,
                "cc_rate": p.cc_rate,
                "conv_fee": p.conv_fee,
            }
            for p in self.periods
        ]
    
    def analyze_roi_trajectory(self, current_period: int = None) -> Tuple[bool, Optional[int], Optional[float]]:
        """
        Analyzes the ROI trajectory to determine:
        1. Whether ROI will be achieved within target periods
        2. How many periods until ROI is achieved
        3. The average period-over-period savings increase
        
        Returns:
        - will_achieve_target: bool
        - periods_to_roi: Optional[int]
        - savings_rate: Optional[float]
        """
        results = self.calculate_roi(current_period)
        if len(results) < 2:
            return False, None, None
            
        # Get the last ROI value and the savings trend
        current_roi = results[-1]["roi"]
        
        # Calculate average period-over-period savings increase
        roi_values = [r["roi"] for r in results if r["period"] != "Period 0"]  # Exclude period 0
        savings_rate = (roi_values[-1] - roi_values[0]) / len(roi_values)
        
        if current_roi >= 0:
            return True, 0, savings_rate
            
        # Project how many periods until ROI based on current trend
        if savings_rate <= 0:
            return False, None, savings_rate
            
        periods_to_roi = int(np.ceil(abs(current_roi) / savings_rate))
        will_achieve_target = periods_to_roi <= self.TARGET_PERIODS_TO_ROI
        
        return will_achieve_target, periods_to_roi, savings_rate
        
    def calculate_roi(self, current_period: int = None) -> List[dict]:
        results = []
        
        # Add period 0 with initial subscription cost
        results.append({
            "period": "Period 0",
            "roi": -self.SUBSCRIPTION_COST,
            "forecast": -self.SUBSCRIPTION_COST,
            "raw_numbers": {
                "subscription_cost": self.SUBSCRIPTION_COST,
                "cumulative_savings": 0,
                "period_savings": 0,
                "cc_fee_savings": 0,
                "ach_costs": 0,
            }
        })
        
        if not self.periods:
            return results
            
        cumulative_savings = 0
        roi_values = [-self.SUBSCRIPTION_COST]  # Start with period 0
        
        periods_to_process = self.periods[:current_period] if current_period is not None else self.periods
                
        for period in periods_to_process:
            # Calculate what it would cost if all volume was processed via credit cards
            total_volume = period.cc_volume + period.ach_volume
            potential_cc_cost = total_volume * (period.cc_rate / 100)
            
            # Calculate actual costs for each payment method
            actual_cc_cost = period.cc_volume * (period.conv_fee / 100)  # Using convenience fee rate
            ach_costs = period.ach_count * self.ACH_COST_PER_TRANSACTION  # Fixed cost per ACH transaction
            
            # Calculate savings from each payment method
            cc_fee_savings = (period.cc_volume * (period.cc_rate / 100)) - actual_cc_cost
            ach_savings = (period.ach_volume * (period.cc_rate / 100)) - ach_costs
            
            # Total period savings
            period_savings = cc_fee_savings + ach_savings
            cumulative_savings += period_savings
            
            # Calculate ROI as actual dollar amount saved relative to subscription cost
            roi_amount = cumulative_savings - self.SUBSCRIPTION_COST
            roi_values.append(roi_amount)
            
            results.append({
                "period": period.period,
                "roi": roi_amount,
                "forecast": 0,  # Will be updated with forecasts
                "raw_numbers": {
                    "subscription_cost": self.SUBSCRIPTION_COST,
                    "cumulative_savings": cumulative_savings,
                    "period_savings": period_savings,
                    "cc_fee_savings": cc_fee_savings,
                    "ach_costs": ach_costs,
                    "ach_savings": ach_savings,
                    "potential_cc_cost": potential_cc_cost,
                    "actual_cc_cost": actual_cc_cost
                }
            })
        
        # Calculate forecasts if we have enough data
        if len(periods_to_process) >= 2:
            X = np.array(range(len(roi_values))).reshape(-1, 1)
            y = np.array(roi_values)
            
            model = LinearRegression()
            model.fit(X, y)
            
            all_forecasts = model.predict(X)
            
            for i in range(len(results)):
                results[i]["forecast"] = all_forecasts[i]
                
        return results

    def get_alerts(self, current_period: int = None) -> List[Dict]:
        """Generate alerts based on ROI status and trajectory analysis"""
        alerts = []
        results = self.calculate_roi(current_period)
        
        if len(results) <= 1:  # Only period 0
            return [{
                'type': 'info',
                'message': f'Initial investment: ${self.SUBSCRIPTION_COST:,.2f}',
                'timestamp': datetime.now().isoformat()
            }]
            
        current_roi = results[-1]["roi"]
        will_achieve_target, periods_to_roi, savings_rate = self.analyze_roi_trajectory(current_period)
        
        # Alert for break-even achievement
        if current_roi > 0:
            alerts.append({
                'type': 'success',
                'message': f'Break-even achieved! Current savings: ${current_roi:,.2f} above subscription cost',
                'timestamp': datetime.now().isoformat()
            })
            
            # Add info about monthly savings rate
            if savings_rate:
                alerts.append({
                    'type': 'info',
                    'message': f'Average savings increase per period: ${savings_rate:,.2f}',
                    'timestamp': datetime.now().isoformat()
                })
        else:
            remaining_to_breakeven = abs(current_roi)
            alerts.append({
                'type': 'info',
                'message': f'${remaining_to_breakeven:,.2f} more in savings needed to break even',
                'timestamp': datetime.now().isoformat()
            })
            
            # Alert about ROI trajectory
            if periods_to_roi is not None:
                if will_achieve_target:
                    alerts.append({
                        'type': 'info',
                        'message': f'On track to achieve ROI in {periods_to_roi} periods',
                        'timestamp': datetime.now().isoformat()
                    })
                else:
                    alerts.append({
                        'type': 'warning',
                        'message': f'ROI trajectory concerning - projected to take {periods_to_roi} periods (target: {self.TARGET_PERIODS_TO_ROI})',
                        'timestamp': datetime.now().isoformat()
                    })
            elif savings_rate <= 0:
                alerts.append({
                    'type': 'error',
                    'message': 'Critical: Current trajectory shows decreasing or flat savings rate',
                    'timestamp': datetime.now().isoformat()
                })

        return alerts 