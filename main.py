"""
Travel Planner - Main CLI Application
An advanced multi-agent travel planning system
"""

import sys
import json
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich import print as rprint

from config import get_settings
from travel_planner.agents.coordinator import CoordinatorAgent
from travel_planner.utils.logger import setup_logger, logger
from travel_planner.utils.formatters import (
    format_currency, format_date, format_itinerary_day,
    format_budget_summary, format_flight_option, format_hotel_option
)
from travel_planner.utils.pdf_generator import TravelPlanPDF


console = Console()


def print_banner():
    """Print welcome banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════╗
    ║                                                       ║
    ║         🌍  TRAVEL PLANNER  -  AI POWERED  ✈️         ║
    ║                                                       ║
    ║     Plan Your Perfect Trip with Multi-Agent AI       ║
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")


def get_trip_details():
    """Get trip details from user"""
    console.print("\n[bold]Let's plan your trip![/bold]\n")
    
    # Destination
    destination = Prompt.ask("[cyan]📍 Destination[/cyan]", default="Paris, France")
    
    # Origin
    origin = Prompt.ask("[cyan]🛫 Departing from[/cyan]", default="New York, USA")
    
    # Dates
    console.print("\n[cyan]📅 When are you traveling?[/cyan]")
    start_date = Prompt.ask(
        "  Start date (YYYY-MM-DD)",
        default="2026-06-01"
    )
    end_date = Prompt.ask(
        "  End date (YYYY-MM-DD)",
        default="2026-06-07"
    )
    
    # Calculate and show duration
    from datetime import datetime
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        duration = (end - start).days
        console.print(f"  [green]✓ Trip duration: {duration} days[/green]")
    except:
        pass
    
    # Travelers
    travelers = int(Prompt.ask("[cyan]👥 Number of travelers[/cyan]", default="2"))
    
    # Budget
    budget = float(Prompt.ask("[cyan]💰 Total budget (USD)[/cyan]", default="3000"))
    
    # Preferences
    console.print("\n[bold]Preferences (optional - press Enter to skip):[/bold]")
    
    interests = Prompt.ask(
        "[cyan]🎯 Interests (e.g., culture, food, adventure)[/cyan]",
        default=""
    )
    
    pace = Prompt.ask(
        "[cyan]⚡ Trip pace (relaxed/moderate/fast)[/cyan]",
        default="moderate"
    )
    
    preferences = {}
    if interests:
        preferences["interests"] = [i.strip() for i in interests.split(",")]
    if pace:
        preferences["pace"] = pace
    
    return {
        "destination": destination,
        "origin": origin,
        "start_date": start_date,
        "end_date": end_date,
        "travelers": travelers,
        "budget": budget,
        "preferences": preferences
    }


def display_trip_summary(plan: dict):
    """Display trip summary"""
    if not plan.get("success"):
        console.print(f"\n[red]❌ Planning failed: {plan.get('error', 'Unknown error')}[/red]")
        if "errors" in plan:
            for error in plan["errors"]:
                console.print(f"  • {error}", style="red")
        return
    
    summary = plan["trip_summary"]
    
    # Trip header
    console.print(f"\n[bold green]✅ Trip Plan Ready![/bold green]\n")
    
    table = Table(show_header=False, box=None)
    table.add_column("Label", style="cyan bold")
    table.add_column("Value", style="white")
    
    table.add_row("🌍 Destination:", summary["destination"])
    table.add_row("🛫 Origin:", summary["origin"])
    table.add_row("📅 Dates:", f"{summary['dates']['start']} to {summary['dates']['end']}")
    table.add_row("⏱️  Duration:", f"{summary['dates']['duration_days']} days")
    table.add_row("👥 Travelers:", str(summary["travelers"]))
    table.add_row("💰 Budget:", format_currency(summary["total_budget"]))
    
    console.print(Panel(table, title="[bold]Trip Summary[/bold]", border_style="green"))


def display_research(research: dict):
    """Display research findings"""
    if not research.get("success"):
        return
    
    console.print(f"\n[bold cyan]📚 Destination Research[/bold cyan]\n")
    console.print(research.get("insights", "No insights available"))


def display_weather(weather: dict):
    """Display weather forecast"""
    if not weather.get("success"):
        return
    
    console.print(f"\n[bold cyan]🌤️  Weather Forecast[/bold cyan]\n")
    
    forecasts = weather.get("forecast", [])
    if forecasts:
        table = Table()
        table.add_column("Date", style="cyan")
        table.add_column("Temperature", style="yellow")
        table.add_column("Condition", style="white")
        table.add_column("Precipitation", style="blue")
        
        for f in forecasts[:7]:  # Show up to 7 days
            table.add_row(
                f.get("date", ""),
                f.get("temperature", ""),
                f.get("condition", ""),
                f.get("precipitation", "")
            )
        
        console.print(table)
    
    console.print(f"\n{weather.get('recommendations', '')}\n")


def display_flights(flights: dict):
    """Display flight options"""
    if not flights.get("success"):
        return
    
    console.print(f"\n[bold cyan]✈️  Flight Options[/bold cyan]\n")
    console.print(flights.get("recommendations", "No recommendations available"))
    
    if flights.get("cheapest_option"):
        cheapest = flights["cheapest_option"]
        console.print(f"\n[green]💡 Cheapest Option: ${cheapest.get('total_price', 0)} per person[/green]")


def display_hotels(hotels: dict):
    """Display hotel options"""
    if not hotels.get("success"):
        return
    
    console.print(f"\n[bold cyan]🏨 Accommodation Options[/bold cyan]\n")
    console.print(hotels.get("recommendations", "No recommendations available"))
    
    if hotels.get("cheapest_option"):
        cheapest = hotels["cheapest_option"]
        console.print(f"\n[green]💡 Cheapest Option: {cheapest['name']} - ${cheapest['price_per_night']}/night[/green]")


def display_budget(budget: dict):
    """Display budget analysis"""
    if not budget.get("success"):
        return
    
    console.print(f"\n[bold cyan]💰 Budget Analysis[/bold cyan]\n")
    
    breakdown = budget.get("breakdown", {})
    if breakdown:
        table = Table()
        table.add_column("Category", style="cyan")
        table.add_column("Amount", style="yellow", justify="right")
        
        table.add_row("✈️  Flights", format_currency(breakdown.get("flights", 0)))
        table.add_row("🏨 Accommodation", format_currency(breakdown.get("accommodation", 0)))
        table.add_row("🍽️  Food", format_currency(breakdown.get("food", 0)))
        table.add_row("🎯 Activities", format_currency(breakdown.get("activities", 0)))
        table.add_row("🚕 Local Transport", format_currency(breakdown.get("local_transport", 0)))
        table.add_row("🎒 Miscellaneous", format_currency(breakdown.get("miscellaneous", 0)))
        table.add_row("", "")
        table.add_row("[bold]Total[/bold]", f"[bold]{format_currency(breakdown.get('total', 0))}[/bold]")
        
        console.print(table)
    
    status = budget.get("status", {})
    status_msg = status.get("message", "")
    status_type = status.get("status", "")
    
    color = "green" if status_type == "comfortable" else "yellow" if status_type == "adequate" else "red"
    console.print(f"\n[{color}]Status: {status_msg}[/{color}]")
    
    console.print(f"\n{budget.get('recommendations', '')}\n")


def display_itinerary(itinerary: dict):
    """Display itinerary"""
    if not itinerary.get("success"):
        return
    
    console.print(f"\n[bold cyan]📅 Detailed Itinerary[/bold cyan]\n")
    
    detailed_plan = itinerary.get("detailed_plan", "")
    
    if detailed_plan:
        # Display the detailed plan
        console.print(detailed_plan)
    else:
        console.print("[yellow]Itinerary is being prepared. Core schedule generated.[/yellow]")
    
    # Show day summary if available
    days = itinerary.get("days", [])
    if days and not detailed_plan:
        console.print("\n[bold]Quick Overview:[/bold]\n")
        for day in days[:7]:  # Show first week
            console.print(f"[cyan]Day {day['day']}[/cyan] ({day['day_of_week']}, {day['date']}):")
            if day.get('weather'):
                weather = day['weather']
                console.print(f"  Weather: {weather.get('temperature')} - {weather.get('condition')}")
            console.print(f"  Budget: ${day.get('estimated_cost', 0):.0f}")
            console.print()


def save_trip_plan(plan: dict, filename: str = None, format: str = 'json'):
    """
    Save trip plan to file
    
    Args:
        plan: Travel plan dictionary
        filename: Optional filename
        format: 'json' or 'pdf'
    """
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        destination = plan["trip_summary"]["destination"].replace(" ", "_").replace(",", "")
        
        if format == 'pdf':
            filename = f"trip_plan_{destination}_{timestamp}.pdf"
        else:
            filename = f"trip_plan_{destination}_{timestamp}.json"
    
    # Create itineraries directory if it doesn't exist
    output_dir = Path("itineraries")
    output_dir.mkdir(exist_ok=True)
    
    filepath = output_dir / filename
    
    if format == 'pdf':
        try:
            pdf_gen = TravelPlanPDF()
            pdf_gen.generate_pdf(plan, str(filepath))
            console.print(f"\n[green]✅ Trip plan saved as PDF: {filepath}[/green]")
        except Exception as e:
            console.print(f"\n[red]❌ Error creating PDF: {e}[/red]")
            console.print("[yellow]Falling back to JSON format...[/yellow]")
            # Fallback to JSON
            json_path = filepath.with_suffix('.json')
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(plan, f, indent=2, ensure_ascii=False)
            console.print(f"[green]✅ Trip plan saved as JSON: {json_path}[/green]")
            return json_path
    else:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(plan, f, indent=2, ensure_ascii=False)
        console.print(f"\n[green]✅ Trip plan saved as JSON: {filepath}[/green]")
    
    return filepath


def main():
    """Main application entry point"""
    try:
        # Setup
        print_banner()
        
        # Check configuration
        try:
            settings = get_settings()
            settings.validate_required_keys()
        except ValueError as e:
            console.print(f"\n[red]❌ Configuration Error:[/red]")
            console.print(f"[yellow]{str(e)}[/yellow]\n")
            console.print("[cyan]Please set up your .env file with required API keys:[/cyan]")
            console.print("1. Copy .env.example to .env")
            console.print("2. Add your API keys")
            console.print("3. Run the application again\n")
            return 1
        
        # Get trip details
        trip_details = get_trip_details()
        
        # Confirm
        console.print("\n[bold yellow]Planning your trip...[/bold yellow]")
        console.print("This may take a minute as we coordinate all agents...\n")
        
        # Initialize coordinator
        with console.status("[bold green]Initializing AI agents...", spinner="dots"):
            coordinator = CoordinatorAgent()
        
        # Plan trip
        with console.status("[bold green]Planning your trip...", spinner="dots"):
            plan = coordinator.plan_trip(**trip_details)
        
        # Display results
        if plan.get("success"):
            display_trip_summary(plan)
            
            # Ask what to display
            console.print("\n[bold]What would you like to see?[/bold]")
            console.print("1. 📚 Research & Attractions")
            console.print("2. 🌤️  Weather Forecast")
            console.print("3. ✈️  Flight Options")
            console.print("4. 🏨 Hotel Options")
            console.print("5. 💰 Budget Analysis")
            console.print("6. 📅 Detailed Itinerary")
            console.print("7. 🎁 All of the above")
            console.print("8. 💾 Save & Exit")
            
            choice = Prompt.ask("\n[cyan]Select option[/cyan]", default="7")
            
            if choice == "1":
                display_research(plan.get("research", {}))
            elif choice == "2":
                display_weather(plan.get("weather", {}))
            elif choice == "3":
                display_flights(plan.get("flights", {}))
            elif choice == "4":
                display_hotels(plan.get("accommodation", {}))
            elif choice == "5":
                display_budget(plan.get("budget_analysis", {}))
            elif choice == "6":
                display_itinerary(plan.get("itinerary", {}))
            elif choice == "7":
                display_research(plan.get("research", {}))
                display_weather(plan.get("weather", {}))
                display_flights(plan.get("flights", {}))
                display_hotels(plan.get("accommodation", {}))
                display_budget(plan.get("budget_analysis", {}))
                display_itinerary(plan.get("itinerary", {}))
            
            # Save option with format choice
            if Confirm.ask("\n[cyan]Would you like to save this trip plan?[/cyan]", default=True):
                console.print("\n[bold]Choose format:[/bold]")
                console.print("1. 📄 PDF (Beautiful document)")
                console.print("2. 📋 JSON (Data format)")
                console.print("3. 📦 Both")
                
                format_choice = Prompt.ask("[cyan]Select format[/cyan]", default="1")
                
                if format_choice == "1":
                    save_trip_plan(plan, format='pdf')
                elif format_choice == "2":
                    save_trip_plan(plan, format='json')
                elif format_choice == "3":
                    save_trip_plan(plan, format='pdf')
                    save_trip_plan(plan, format='json')
                    console.print("[green]✅ Saved in both formats![/green]")
            
            console.print("\n[bold green]✨ Happy travels! ✨[/bold green]\n")
        else:
            display_trip_summary(plan)
        
        return 0
        
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Planning cancelled by user.[/yellow]\n")
        return 130
    except Exception as e:
        console.print(f"\n[red]❌ An error occurred: {str(e)}[/red]\n")
        logger.exception("Application error")
        return 1


if __name__ == "__main__":
    sys.exit(main())
