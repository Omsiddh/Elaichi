# 🌍 Travel Planner - AI-Powered Itinerary Agent

> **An advanced multi-agent travel planning system** built with **LangChain** and **Google Gemini API** that creates personalized itineraries with real-time data integration.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/LangChain-Latest-green.svg)](https://python.langchain.com/)
[![Gemini](https://img.shields.io/badge/Gemini-Pro-orange.svg)](https://ai.google.dev/)

---

## ✨ Features

### 🤖 Multi-Agent Architecture
7 specialized AI agents work together to create comprehensive travel plans:
- **Coordinator Agent** - Orchestrates the entire planning process
- **Research Agent** - Gathers destination info, attractions, and local tips
- **Weather Agent** - Real-time forecasts and packing recommendations
- **Flight Agent** - Flight search with price comparisons
- **Hotel Agent** - Accommodation search and filtering
- **Budget Agent** - Cost tracking and optimization
- **Itinerary Agent** - Detailed day-by-day planning

### 🎯 Key Capabilities
- ✅ Real-time weather forecasts
- ✅ Flight search and recommendations
- ✅ Hotel search with ratings and amenities
- ✅ Budget breakdown and optimization
- ✅ Destination research and attractions
- ✅ Day-by-day itinerary creation
- ✅ Export plans as JSON
- ✅ Beautiful CLI interface
- ✅ Input validation
- ✅ Error handling and logging

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Coordinator Agent                      │
│            (Orchestrates all operations)                │
└──────────────────┬──────────────────────────────────────┘
                   │
      ┌────────────┼────────────┐
      │            │            │
      ▼            ▼            ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│Research  │ │ Weather  │ │ Flight   │
│Agent     │ │ Agent    │ │ Agent    │
└──────────┘ └──────────┘ └──────────┘
      │            │            │
      ▼            ▼            ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│ Hotel    │ │ Budget   │ │Itinerary │
│ Agent    │ │ Agent    │ │ Agent    │
└──────────┘ └──────────┘ └──────────┘
      │            │            │
      └────────────┴────────────┘
                   │
                   ▼
           Gemini Pro (LLM)
                   │
      ┌────────────┴────────────┐
      ▼            ▼            ▼
  Weather API  Search API   Data Tools
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or navigate to the project directory
cd travel_planner

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy the example environment file
copy .env.example .env

# Edit .env and add your API keys:
# - GOOGLE_API_KEY: Get from https://makersuite.google.com/app/apikey
# - OPENWEATHER_API_KEY: Get from https://openweathermap.org/api
# - SERPAPI_KEY (optional): Get from https://serpapi.com/
```

### 3. Run

```bash
python main.py
```

## 📖 Usage Example

```python
from travel_planner.agents.coordinator import CoordinatorAgent

# Initialize the coordinator
coordinator = CoordinatorAgent()

# Plan a trip
result = coordinator.plan_trip(
    destination="Tokyo, Japan",
    start_date="2026-09-01",
    end_date="2026-09-07",
    budget=2500,
    travelers=2,
    preferences={
        "interests": ["culture", "food", "temples"],
        "pace": "moderate"
    }
)

print(result.itinerary)
```

## 🔑 API Keys Required

1. **Google Gemini API** (Required)
   - Free tier available
   - Get key: https://makersuite.google.com/app/apikey

2. **OpenWeatherMap API** (Required for weather)
   - Free tier: 1,000 calls/day
   - Get key: https://openweathermap.org/api

3. **SerpAPI** (Optional - for enhanced search)
   - Free tier: 100 searches/month
   - Get key: https://serpapi.com/

## 📁 Project Structure

```
travel_planner/
├── main.py                 # Entry point
├── config.py              # Configuration management
├── requirements.txt       # Dependencies
├── .env.example          # API key template
├── agents/
│   ├── base_agent.py     # Base agent class
│   ├── coordinator.py    # Main orchestrator
│   ├── research_agent.py
│   ├── weather_agent.py
│   ├── flight_agent.py
│   ├── hotel_agent.py
│   ├── budget_agent.py
│   └── itinerary_agent.py
├── tools/
│   ├── weather_tool.py
│   ├── flight_tool.py
│   ├── hotel_tool.py
│   └── search_tool.py
└── utils/
    ├── logger.py
    ├── formatters.py
    └── validators.py
```

## 🛠️ Technologies

- **LangChain**: Agent orchestration and workflows
- **Google Gemini**: AI reasoning and planning
- **OpenWeatherMap**: Weather data
- **Python 3.9+**: Core language
- **Rich**: Beautiful CLI output

## 📝 License

MIT License - feel free to use this project for learning and development!

## 🤝 Contributing

Contributions welcome! Feel free to submit issues or pull requests.

## ⚠️ Note

This is an AI-powered travel planner. Always verify important details (flights, bookings, weather) with official sources before making travel decisions.
