# Web Scraping Agent System

A universal multi-agent web scraping system that can search for products, add them to cart, and complete checkout processes on any e-commerce website.

## Features

- **Multi-Agent Architecture**: Coordinated agents for different tasks
  - **Orchestrator Agent (Agent1)**: Coordinates all other agents
  - **Web Navigator Agent**: Handles browser automation
  - **Product Search Agent**: Finds products based on specifications
  - **Cart/Checkout Agent**: Manages cart and checkout operations

- **Universal Solution**: Works with any website, not limited to specific e-commerce platforms
- **AI-Powered**: Uses OpenAI GPT-4 for intelligent decision-making and element detection
- **Automated Browser Control**: Uses Playwright for reliable web automation

## Installation

1. **Clone or navigate to the project directory**:
   ```bash
   cd WebScrappinAgent
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright browsers**:
   ```bash
   playwright install chromium
   ```

5. **Set up environment variables**:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## Usage

### Basic Usage

Run the agent with a product query:

```bash
python main.py "iPhone 15 Pro 256GB storage white color"
```

Or run interactively:

```bash
python main.py
```

Then enter your query when prompted.

### Example Queries

- `"iPhone 15 Pro 256GB storage white color"`
- `"Samsung Galaxy S24 Ultra 512GB black"`
- `"Nike Air Max shoes size 10"`
- `"MacBook Pro 16 inch M3 Max"`

## Architecture

### Agent System

1. **Orchestrator Agent (Agent1)**
   - Plans the task execution
   - Coordinates all sub-agents
   - Manages the overall workflow

2. **Web Navigator Agent**
   - Initializes and manages browser instances
   - Handles navigation, clicking, and form filling
   - Takes screenshots for debugging

3. **Product Search Agent**
   - Extracts product specifications from user queries
   - Determines target website
   - Finds products matching specifications
   - Uses AI to identify product elements

4. **Cart/Checkout Agent**
   - Adds products to cart
   - Navigates through checkout process
   - Fills checkout forms (when applicable)
   - Handles order placement

## Configuration

Edit `config.py` to customize:

- `BROWSER_HEADLESS`: Set to `True` for headless mode
- `BROWSER_TIMEOUT`: Browser operation timeout
- `OPENAI_MODEL`: OpenAI model to use
- `MAX_RETRIES`: Maximum retry attempts

## Project Structure

```
WebScrappinAgent/
├── agents/
│   ├── __init__.py
│   ├── base_agent.py          # Base class for all agents
│   ├── orchestrator_agent.py  # Agent1 - Main coordinator
│   ├── web_navigator.py       # Browser automation agent
│   ├── product_search_agent.py # Product search agent
│   └── cart_checkout_agent.py # Cart/checkout agent
├── utils/
│   ├── __init__.py
│   └── logger.py              # Logging utility
├── config.py                  # Configuration management
├── main.py                    # Main entry point
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
└── README.md                 # This file
```

## How It Works

1. **User Query Processing**: The orchestrator receives a user query
2. **Task Planning**: AI creates a step-by-step plan
3. **Product Search**: 
   - Extracts product specifications
   - Determines target website
   - Navigates and searches for products
4. **Product Selection**: Identifies matching products
5. **Cart Operations**: Adds product to cart
6. **Checkout**: Navigates through checkout process
7. **Order Placement**: Attempts to place order (may require manual payment info)

## Important Notes

- **Payment Information**: The system can navigate through checkout but typically cannot complete payment without valid payment information
- **Website Variations**: Different websites have different structures; the AI adapts to find elements
- **Rate Limiting**: Be mindful of website rate limits and terms of service
- **Legal Compliance**: Ensure you comply with website terms of service and robots.txt

## Troubleshooting

### Browser Issues
- Ensure Playwright browsers are installed: `playwright install chromium`
- Check browser permissions if running in headless mode

### API Issues
- Verify your OpenAI API key is correct in `.env`
- Check API rate limits and quota

### Element Not Found
- The system uses AI to find elements, but some websites may have complex structures
- Check logs for detailed error messages
- Screenshots are saved for debugging

## Development

To extend the system:

1. **Add New Agents**: Inherit from `BaseAgent` in `agents/base_agent.py`
2. **Customize Search Logic**: Modify `ProductSearchAgent` for specific websites
3. **Add New Actions**: Extend agent `execute` methods with new actions

## License

This is a POC (Proof of Concept) project. Use responsibly and in compliance with website terms of service.

