"""
Budget Agent - Handles budget tracking and optimization
"""

from typing import Dict, Any, Optional, List
from travel_planner.agents.base_agent import BaseAgent
from travel_planner.utils.logger import logger
from travel_planner.utils.formatters import format_currency


class BudgetAgent(BaseAgent):
    """Agent specialized in budget management and cost optimization"""
    
    def __init__(self):
        super().__init__(
            name="Budget Agent",
            role="budget optimization specialist",
            goal="track expenses, optimize costs, and ensure the trip stays within budget"
        )
    
    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute budget-related task
        
        Args:
            task: Budget task description
            context: Context with trip details and expenses
            
        Returns:
            Budget analysis and recommendations
        """
        try:
            if not context:
                return {"success": False, "error": "No context provided"}
            
            total_budget = context.get("budget")
            if not total_budget:
                return {"success": False, "error": "No budget specified"}
            
            logger.info(f"Analyzing budget: ${total_budget}")
            
            # Extract cost components
            flight_cost = context.get("flight_cost", 0)
            hotel_cost = context.get("hotel_cost", 0)
            travelers = context.get("travelers", 1)
            duration_days = context.get("duration_days", 1)
            
            # Calculate breakdown
            breakdown = self.calculate_budget_breakdown(
                total_budget, flight_cost, hotel_cost, duration_days, travelers
            )
            
            # Generate recommendations
            budget_prompt = f"""
            Budget analysis for trip:
            Total Budget: ${total_budget}
            Travelers: {travelers}
            Duration: {duration_days} days
            
            Current allocations:
            - Flights: ${flight_cost}
            - Accommodation: ${hotel_cost}
            - Remaining: ${total_budget - flight_cost - hotel_cost}
            
            Provide:
            1. Budget assessment (is it adequate?)
            2. Recommendations for the remaining budget allocation
            3. Money-saving tips for this trip
            4. Warning signs if budget seems tight
            
            Be specific and practical.
            """
            
            recommendations = self.generate_response(budget_prompt, context)
            
            # Check budget status
            status = self.assess_budget_status(
                total_budget, flight_cost, hotel_cost, duration_days
            )
            
            return {
                "success": True,
                "total_budget": total_budget,
                "breakdown": breakdown,
                "status": status,
                "recommendations": recommendations,
                "remaining_budget": total_budget - flight_cost - hotel_cost
            }
            
        except Exception as e:
            logger.error(f"Budget agent error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def calculate_budget_breakdown(
        self,
        total_budget: float,
        flight_cost: float,
        hotel_cost: float,
        days: int,
        travelers: int = 1
    ) -> Dict[str, Any]:
        """
        Calculate recommended budget breakdown
        
        Args:
            total_budget: Total available budget
            flight_cost: Actual or estimated flight cost
            hotel_cost: Actual or estimated hotel cost
            days: Trip duration
            travelers: Number of travelers
            
        Returns:
            Budget breakdown dictionary
        """
        # Calculate remaining after flights and hotels
        fixed_costs = flight_cost + hotel_cost
        remaining = total_budget - fixed_costs
        
        # Standard allocation percentages for remaining budget
        # Food: 40%, Activities: 35%, Transportation: 15%, Misc: 10%
        per_day_budget = remaining / days if days > 0 else remaining
        
        food_budget = remaining * 0.40
        activities_budget = remaining * 0.35
        transport_budget = remaining * 0.15
        misc_budget = remaining * 0.10
        
        return {
            "total": total_budget,
            "flights": flight_cost,
            "accommodation": hotel_cost,
            "food": food_budget,
            "activities": activities_budget,
            "local_transport": transport_budget,
            "miscellaneous": misc_budget,
            "per_day_spending": per_day_budget,
            "per_person_total": total_budget / travelers if travelers > 0 else total_budget
        }
    
    def assess_budget_status(
        self,
        total_budget: float,
        flight_cost: float,
        hotel_cost: float,
        days: int
    ) -> Dict[str, Any]:
        """
        Assess if budget is adequate
        
        Args:
            total_budget: Total budget
            flight_cost: Flight costs
            hotel_cost: Hotel costs
            days: Trip duration
            
        Returns:
            Budget status assessment
        """
        fixed_costs = flight_cost + hotel_cost
        remaining = total_budget - fixed_costs
        per_day = remaining / days if days > 0 else 0
        
        # Determine status
        if per_day >= 100:
            status = "comfortable"
            message = "Budget is comfortable with good flexibility"
        elif per_day >= 60:
            status = "adequate"
            message = "Budget is adequate for a moderate trip"
        elif per_day >= 40:
            status = "tight"
            message = "Budget is tight, requires careful planning"
        else:
            status = "insufficient"
            message = "Budget may be insufficient, consider increasing or adjusting plans"
        
        fixed_percentage = (fixed_costs / total_budget * 100) if total_budget > 0 else 0
        
        return {
            "status": status,
            "message": message,
            "remaining_budget": remaining,
            "per_day_budget": per_day,
            "fixed_costs_percentage": round(fixed_percentage, 1),
            "warnings": self._generate_warnings(status, fixed_percentage, per_day)
        }
    
    def _generate_warnings(self, status: str, fixed_percentage: float, per_day: float) -> List[str]:
        """Generate budget warnings"""
        warnings = []
        
        if status == "insufficient":
            warnings.append("⚠️  Daily budget is very low. Consider extending budget or shortening trip.")
        
        if fixed_percentage > 70:
            warnings.append("⚠️  Flights and hotels consume over 70% of budget. Little left for activities.")
        
        if per_day < 50:
            warnings.append("⚠️  Less than $50/day for food, activities, and transport. Very tight budget.")
        
        return warnings
    
    def optimize_budget(
        self,
        current_plan: Dict[str, Any],
        target_budget: float
    ) -> Dict[str, Any]:
        """
        Suggest optimizations to meet budget
        
        Args:
            current_plan: Current trip plan with costs
            target_budget: Target budget
            
        Returns:
            Optimization suggestions
        """
        try:
            optimization_prompt = f"""
            Current trip plan:
            {current_plan}
            
            Target budget: ${target_budget}
            Current total: ${current_plan.get('total_cost', 0)}
            Difference: ${current_plan.get('total_cost', 0) - target_budget}
            
            Provide specific, actionable suggestions to reduce costs:
            1. Flight alternatives or booking strategies
            2. Hotel alternatives or location changes
            3. Activity modifications
            4. General cost-saving tips
            
            Prioritize suggestions by potential savings.
            """
            
            suggestions = self.generate_response(optimization_prompt)
            
            return {
                "success": True,
                "target_budget": target_budget,
                "current_cost": current_plan.get('total_cost', 0),
                "optimization_needed": current_plan.get('total_cost', 0) - target_budget,
                "suggestions": suggestions
            }
            
        except Exception as e:
            logger.error(f"Budget optimization error: {e}")
            return {
                "success": False,
                "error": str(e)
            }


__all__ = ["BudgetAgent"]
