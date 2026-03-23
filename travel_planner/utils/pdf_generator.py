"""
PDF Generator for Travel Plans
Creates beautiful PDF documents from trip plans
"""

from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether
)
from reportlab.lib.colors import HexColor
from travel_planner.utils.formatters import format_currency, format_date


class TravelPlanPDF:
    """Generator for travel plan PDF documents"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=HexColor('#1e3a8a'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Heading style
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=HexColor('#2563eb'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Subheading style
        self.styles.add(ParagraphStyle(
            name='CustomSubheading',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=HexColor('#3b82f6'),
            spaceAfter=8,
            fontName='Helvetica-Bold'
        ))
        
        # Body text style
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            fontName='Helvetica'
        ))
    
    def generate_pdf(
        self,
        plan: Dict[str, Any],
        output_path: str,
        include_details: bool = True
    ) -> str:
        """
        Generate PDF from travel plan
        
        Args:
            plan: Travel plan dictionary
            output_path: Output file path
            include_details: Include detailed information
            
        Returns:
            Path to generated PDF
        """
        # Create document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        # Build content
        story = []
        
        # Add title page
        story.extend(self._create_title_page(plan))
        
        # Add trip summary
        story.extend(self._create_summary_section(plan))
        
        if include_details:
            # Add weather section
            if plan.get('weather', {}).get('success'):
                story.extend(self._create_weather_section(plan['weather']))
            
            # Add flights section
            if plan.get('flights', {}).get('success'):
                story.extend(self._create_flights_section(plan['flights']))
            
            # Add accommodation section
            if plan.get('accommodation', {}).get('success'):
                story.extend(self._create_accommodation_section(plan['accommodation']))
            
            # Add budget section
            if plan.get('budget_analysis', {}).get('success'):
                story.extend(self._create_budget_section(plan['budget_analysis']))
            
            # Add itinerary section
            if plan.get('itinerary', {}).get('success'):
                story.extend(self._create_itinerary_section(plan['itinerary']))
        
        # Add footer
        story.extend(self._create_footer())
        
        # Build PDF
        doc.build(story)
        
        return output_path
    
    def _create_title_page(self, plan: Dict[str, Any]) -> list:
        """Create title page"""
        elements = []
        
        # Title
        title = Paragraph(
            "✈️ TRAVEL ITINERARY",
            self.styles['CustomTitle']
        )
        elements.append(title)
        elements.append(Spacer(1, 0.3*inch))
        
        # Destination
        summary = plan.get('trip_summary', {})
        destination = Paragraph(
            f"<b>{summary.get('destination', 'Unknown')}</b>",
            self.styles['CustomTitle']
        )
        elements.append(destination)
        elements.append(Spacer(1, 0.5*inch))
        
        # Quick info table
        dates = summary.get('dates', {})
        data = [
            ['📅 Dates:', f"{dates.get('start', '')} to {dates.get('end', '')}"],
            ['⏱️ Duration:', f"{dates.get('duration_days', 0)} days"],
            ['👥 Travelers:', str(summary.get('travelers', 1))],
            ['💰 Budget:', format_currency(summary.get('total_budget', 0))],
            ['🛫 From:', summary.get('origin', 'N/A')]
        ]
        
        table = Table(data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('TEXTCOLOR', (0, 0), (0, -1), HexColor('#2563eb')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(table)
        elements.append(PageBreak())
        
        return elements
    
    def _create_summary_section(self, plan: Dict[str, Any]) -> list:
        """Create trip summary section"""
        elements = []
        
        heading = Paragraph("📋 Trip Overview", self.styles['CustomHeading'])
        elements.append(heading)
        
        summary = plan.get('trip_summary', {})
        text = f"""
        This comprehensive travel plan has been created for your trip to 
        <b>{summary.get('destination', 'your destination')}</b>. 
        The itinerary spans {summary.get('dates', {}).get('duration_days', 0)} days 
        and is designed for {summary.get('travelers', 1)} traveler(s) with a total 
        budget of {format_currency(summary.get('total_budget', 0))}.
        """
        
        elements.append(Paragraph(text, self.styles['CustomBody']))
        elements.append(Spacer(1, 0.3*inch))
        
        return elements
    
    def _create_weather_section(self, weather: Dict[str, Any]) -> list:
        """Create weather section"""
        elements = []
        
        heading = Paragraph("🌤️ Weather Forecast", self.styles['CustomHeading'])
        elements.append(heading)
        
        forecasts = weather.get('forecast', [])[:7]
        
        if forecasts:
            # Create weather table
            data = [['Date', 'Temperature', 'Condition', 'Precipitation']]
            
            for f in forecasts:
                data.append([
                    f.get('date', ''),
                    f.get('temperature', ''),
                    f.get('condition', ''),
                    f.get('precipitation', '')
                ])
            
            table = Table(data, colWidths=[1.5*inch, 1.5*inch, 2*inch, 1.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#3b82f6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('TOPPADDING', (0, 1), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ]))
            
            elements.append(table)
        
        # Add recommendations if available
        recommendations = weather.get('recommendations', '')
        if recommendations and 'Error' not in recommendations:
            elements.append(Spacer(1, 0.2*inch))
            elements.append(Paragraph("<b>Packing Recommendations:</b>", self.styles['CustomSubheading']))
            # Limit text length for PDF
            rec_text = recommendations[:500] + "..." if len(recommendations) > 500 else recommendations
            elements.append(Paragraph(rec_text, self.styles['CustomBody']))
        
        elements.append(Spacer(1, 0.3*inch))
        
        return elements
    
    def _create_flights_section(self, flights: Dict[str, Any]) -> list:
        """Create flights section"""
        elements = []
        
        heading = Paragraph("✈️ Flight Options", self.styles['CustomHeading'])
        elements.append(heading)
        
        # Show cheapest option
        cheapest = flights.get('cheapest_option', {})
        if cheapest.get('success'):
            text = f"""
            <b>Recommended Flight:</b> ${cheapest.get('total_price', 0)} per person<br/>
            Total for {flights.get('travelers', 1)} travelers: 
            {format_currency(flights.get('estimated_cost', 0))}
            """
            elements.append(Paragraph(text, self.styles['CustomBody']))
        
        # Show top flights
        flight_results = flights.get('flight_results', {})
        outbound = flight_results.get('outbound_flights', [])[:3]
        
        if outbound:
            elements.append(Spacer(1, 0.1*inch))
            elements.append(Paragraph("<b>Outbound Flight Options:</b>", self.styles['CustomSubheading']))
            
            data = [['Airline', 'Time', 'Duration', 'Stops', 'Price']]
            
            for flight in outbound:
                data.append([
                    flight.get('airline', '')[:20],
                    f"{flight.get('departure_time', '')} → {flight.get('arrival_time', '')}",
                    flight.get('duration', ''),
                    str(flight.get('stops', 0)),
                    format_currency(flight.get('price', 0))
                ])
            
            table = Table(data, colWidths=[1.7*inch, 1.5*inch, 1*inch, 0.8*inch, 1*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#3b82f6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('TOPPADDING', (0, 1), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
            ]))
            
            elements.append(table)
        
        elements.append(Spacer(1, 0.3*inch))
        
        return elements
    
    def _create_accommodation_section(self, accommodation: Dict[str, Any]) -> list:
        """Create accommodation section"""
        elements = []
        
        heading = Paragraph("🏨 Accommodation Options", self.styles['CustomHeading'])
        elements.append(heading)
        
        # Show cheapest option
        cheapest = accommodation.get('cheapest_option', {})
        if cheapest:
            text = f"""
            <b>Budget Option:</b> {cheapest.get('name', 'N/A')}<br/>
            Price: {format_currency(cheapest.get('price_per_night', 0))} per night<br/>
            Total: {format_currency(cheapest.get('total_cost', 0))} for {accommodation.get('nights', 0)} nights
            """
            elements.append(Paragraph(text, self.styles['CustomBody']))
        
        # Show best rated
        best = accommodation.get('best_rated_option', {})
        if best:
            elements.append(Spacer(1, 0.1*inch))
            stars = '⭐' * best.get('rating', 0)
            text = f"""
            <b>Recommended Hotel:</b> {best.get('name', 'N/A')} {stars}<br/>
            Location: {best.get('location', 'N/A')}<br/>
            Price: {format_currency(best.get('price_per_night', 0))} per night
            """
            elements.append(Paragraph(text, self.styles['CustomBody']))
        
        elements.append(Spacer(1, 0.3*inch))
        
        return elements
    
    def _create_budget_section(self, budget: Dict[str, Any]) -> list:
        """Create budget section"""
        elements = []
        
        heading = Paragraph("💰 Budget Breakdown", self.styles['CustomHeading'])
        elements.append(heading)
        
        breakdown = budget.get('breakdown', {})
        
        if breakdown:
            data = [['Category', 'Amount']]
            categories = [
                ('✈️ Flights', 'flights'),
                ('🏨 Accommodation', 'accommodation'),
                ('🍽️ Food', 'food'),
                ('🎯 Activities', 'activities'),
                ('🚕 Local Transport', 'local_transport'),
                ('🎒 Miscellaneous', 'miscellaneous')
            ]
            
            for label, key in categories:
                amount = breakdown.get(key, 0)
                if amount >= 0:  # Only show positive amounts
                    data.append([label, format_currency(amount)])
            
            data.append(['', ''])
            data.append(['<b>Total</b>', f"<b>{format_currency(breakdown.get('total', 0))}</b>"])
            
            table = Table(data, colWidths=[4*inch, 2*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#3b82f6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
                ('GRID', (0, 0), (-1, -2), 1, colors.grey),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('TOPPADDING', (0, 1), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                ('LINEABOVE', (0, -1), (-1, -1), 2, colors.black),
            ]))
            
            elements.append(table)
        
        # Budget status
        status = budget.get('status', {})
        if status:
            elements.append(Spacer(1, 0.2*inch))
            status_text = f"<b>Budget Status:</b> {status.get('message', '')}"
            elements.append(Paragraph(status_text, self.styles['CustomBody']))
        
        elements.append(Spacer(1, 0.3*inch))
        
        return elements
    
    def _create_itinerary_section(self, itinerary: Dict[str, Any]) -> list:
        """Create itinerary section"""
        elements = []
        
        heading = Paragraph("📅 Detailed Itinerary", self.styles['CustomHeading'])
        elements.append(heading)
        
        detailed_plan = itinerary.get('detailed_plan', '')
        
        if detailed_plan and 'Error' not in detailed_plan:
            # Limit text for PDF
            text = detailed_plan[:2000] + "..." if len(detailed_plan) > 2000 else detailed_plan
            elements.append(Paragraph(text, self.styles['CustomBody']))
        else:
            elements.append(Paragraph(
                "Itinerary details are being finalized. Check back for day-by-day activities.",
                self.styles['CustomBody']
            ))
        
        elements.append(Spacer(1, 0.3*inch))
        
        return elements
    
    def _create_footer(self) -> list:
        """Create footer"""
        elements = []
        
        elements.append(Spacer(1, 0.5*inch))
        
        footer_text = f"""
        <para align=center>
        <font size=8 color="#6b7280">
        Generated by Travel Planner AI • {datetime.now().strftime('%B %d, %Y')}<br/>
        This is an AI-generated travel plan. Please verify all details before booking.
        </font>
        </para>
        """
        
        elements.append(Paragraph(footer_text, self.styles['Normal']))
        
        return elements


__all__ = ["TravelPlanPDF"]
