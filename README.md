# Flight Deal Finder AI Agent

This application uses Mistral AI, Amadeus API, and Aviation Stack to find the cheapest flights between two cities for a specific date. It provides multiple notification methods including email and Discord, and offers a web interface for monitoring.

## Features

- Finds top 3 cheapest flights between specified cities for a specific date
- Uses Mistral AI to analyze and format flight information
- Multiple notification methods:
  - Email notifications with flight deals
  - Discord bot integration
  - Webhook support for custom integrations
- Web interface using Streamlit for monitoring and configuration
- Runs in a Docker container
- Provides detailed flight information including stops and timing
- Real-time flight status updates using Aviation Stack API

## Prerequisites

- Docker installed on your system
- Mistral AI API key
- Amadeus API credentials (Client ID and Client Secret)
- Aviation Stack API key
- Gmail account (for sending notifications)
- Discord bot token and channel ID (optional, for Discord notifications)

## Setup

1. Clone this repository
2. Copy `.env.example` to `.env` and fill in your credentials:
   ```bash
   cp .env.example .env
   ```
3. Edit the `.env` file with your:
   - Mistral AI API key
   - Amadeus API credentials (Client ID and Client Secret)
   - Aviation Stack API key
   - Email credentials
   - Discord bot token and channel ID (optional)
   - Webhook secret (for custom integrations)
   - Desired departure and arrival cities (IATA codes)
   - Desired flight date (YYYY-MM-DD format)

## Running the Application

### Method 1: Using Docker (Recommended)

1. Build the Docker image:
   ```bash
   docker build -t flight-agent .
   ```

2. Run the container:
   ```bash
   docker run -d --env-file .env flight-agent
   ```

3. Check the logs:
   ```bash
   docker logs $(docker ps -q --filter ancestor=flight-agent)
   ```

4. Stop the container:
   ```bash
   docker stop $(docker ps -q --filter ancestor=flight-agent)
   ```

### Method 2: Running Directly with Python

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python flight_agent.py
   ```

3. Access the web interface:
   ```bash
   streamlit run app.py
   ```

## Interacting with the Application

### Web Interface

1. Access the Streamlit web interface at `http://localhost:8501`
2. Monitor flight searches in real-time
3. Configure search parameters
4. View historical search results

### Checking Flight Status

1. View the logs to see the current status:
   ```bash
   docker logs $(docker ps -q --filter ancestor=flight-agent)
   ```

2. The application will:
   - Check for flights at 9 AM daily
   - Send notifications through configured channels
   - Show logs of the search process
   - Update the web interface with results

### Notification Methods

1. Email Notifications:
   - Sent to the address specified in RECIPIENT_EMAIL
   - Include flight prices, times, and AI analysis

2. Discord Notifications:
   - Messages sent to configured Discord channel
   - Include flight details and direct booking links

3. Webhook Integration:
   - Custom webhook support for external systems
   - Secure authentication using WEBHOOK_SECRET

### Modifying Flight Search Parameters

1. Stop the current container:
   ```bash
   docker stop $(docker ps -q --filter ancestor=flight-agent)
   ```

2. Edit the `.env` file to change:
   - Departure city (FROM_CITY)
   - Arrival city (TO_CITY)
   - Flight date (FLIGHT_DATE)

3. Restart the container:
   ```bash
   docker run -d --env-file .env flight-agent
   ```

### Troubleshooting

If you encounter any issues:

1. Check the Docker logs:
   ```bash
   docker logs $(docker ps -q --filter ancestor=flight-agent)
   ```

2. Verify your API keys are correct:
   - Mistral AI API key
   - Amadeus API credentials
   - Aviation Stack API key
   - Discord bot token

3. Check notification configurations:
   - Email: Ensure SENDER_EMAIL and SENDER_PASSWORD are correct
   - Discord: Verify BOT_TOKEN and CHANNEL_ID
   - Webhook: Check WEBHOOK_SECRET and endpoint configuration

4. Verify city codes:
   - Use valid IATA city codes (e.g., NYC for New York, LAX for Los Angeles)
   - Check the Amadeus documentation for supported city codes

5. Check date format:
   - Ensure FLIGHT_DATE is in YYYY-MM-DD format
   - The date should be in the future

6. Monitor API usage:
   - Check your Amadeus API usage limits (2000 calls/month on free tier)
   - Monitor Aviation Stack API usage
   - Track Mistral AI API usage

## Configuration Options

### Environment Variables

- `MISTRAL_API_KEY`: Your Mistral AI API key
- `AMADEUS_CLIENT_ID`: Your Amadeus API Client ID
- `AMADEUS_CLIENT_SECRET`: Your Amadeus API Client Secret
- `AVIATION_STACK_API_KEY`: Your Aviation Stack API key
- `SENDER_EMAIL`: Your Gmail address for sending notifications
- `SENDER_PASSWORD`: Your Gmail App Password
- `RECIPIENT_EMAIL`: Email address to receive notifications
- `DISCORD_BOT_TOKEN`: Your Discord bot token
- `DISCORD_CHANNEL_ID`: Discord channel ID for notifications
- `WEBHOOK_SECRET`: Secret for webhook authentication
- `FROM_CITY`: Departure city IATA code
- `TO_CITY`: Arrival city IATA code
- `FLIGHT_DATE`: Desired flight date (YYYY-MM-DD)

### Scheduling

- The application checks for flights daily at 9:00 AM
- You can modify the schedule in the `main()` function of `flight_agent.py`
- The application also runs an immediate check on startup
- Real-time updates through the web interface

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the API documentation:
   - Amadeus API
   - Mistral AI
   - Aviation Stack
3. Open an issue in the repository
4. Check the Documentation/ directory for additional resources