# SalesMate - AI-Powered Sales Assistant

An intelligent sales chatbot that provides personalized product recommendations through natural conversation using OpenAI's GPT models.

## Overview

SalesMate is an LLM-based sales assistant that simulates a professional salesperson, guiding customers through product catalogs and making personalized recommendations based on their needs, preferences, and budget.

## Features

- **Conversational AI**: Natural dialogue powered by OpenAI GPT models
- **Personalized Recommendations**: Product suggestions based on user personas
- **Product Catalog**: Browse 18+ electronics products across multiple categories
- **User Personas**: 4 distinct customer profiles with different preferences
- **Conversation Logging**: Save and review conversation history
- **Product Comparison**: Compare multiple products side-by-side
- **Smart Filtering**: Search by category, brand, price range, and features

## Requirements

- Python 3.9+
- OpenAI API Key
- pip (Python package manager)

## Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd salesmate
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

## Usage

**Start the application:**
```bash
python run.py
```

**Main Menu Options:**
1. Start New Conversation - Begin chatting with the AI sales assistant
2. View Product Catalog - Browse available products
3. View Conversation History - Review past conversations
4. Settings - View system configuration
5. Exit - Close the application

## User Personas

The system includes 4 pre-configured personas:

1. **Robert Chen** - Senior professional, tech-savvy, premium budget
2. **Marcus Johnson** - Young professional, moderate tech skills, mid-range budget
3. **Emily Rodriguez** - Young adult, beginner tech level, budget-conscious
4. **Sarah Mitchell** - Middle-aged professional, high tech skills, flexible budget

## Product Catalog

18 electronics products across categories:
- Smart TVs
- Laptops
- Smartphones
- Headphones
- Smartwatches
- Cameras
- Speakers

## Conversation Flow

1. **Select Persona** - Choose a customer profile
2. **Greeting** - AI introduces itself
3. **Discovery** - AI asks questions to understand needs
4. **Recommendation** - AI suggests relevant products
5. **Comparison** - Compare products if needed
6. **Closing** - Finalize conversation

## Development

**Run in debug mode:**
```bash
DEBUG=True python run.py
```

**Change log format:**
```bash
LOG_FORMAT=json python run.py
```
