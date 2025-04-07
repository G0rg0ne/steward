# Flight Deal Finder AI Agent

This application uses Mistral AI and Amadeus API to find the cheapest flights between two cities for a specific date and sends email notifications.

## Features

- Finds top 3 cheapest flights between specified cities for a specific date
- Uses Mistral AI to analyze and format flight information
- Sends email notifications with flight deals
- Runs in a Docker container
- Provides detailed flight information including stops and timing

## Prerequisites

- Docker installed on your system
- Mistral AI API key
- Amadeus API credentials (Client ID and Client Secret)
- Gmail account (for sending notifications)

## Setup

1. Clone this repository
2. Copy `.env.example` to `.env` and fill in your credentials:
   ```bash
   cp .env.example .env
   ```
3. Edit the `.env` file with your:
   - Mistral AI API key
   - Amadeus API credentials (Client ID and Client Secret)
   - Email credentials
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

## Interacting with the Application

### Checking Flight Status

1. View the logs to see the current status:
   ```bash
   docker logs $(docker ps -q --filter ancestor=flight-agent)
   ```

2. The application will:
   - Check for flights at 9 AM daily
   - Send email notifications with flight deals
   - Show logs of the search process

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

### Checking Email Notifications

1. The application will send emails to the address specified in RECIPIENT_EMAIL
2. Check your email inbox for notifications
3. Each email will contain:
   - Flight prices
   - Departure and arrival times
   - Number of stops
   - AI analysis of the best deals

### Troubleshooting

If you encounter any issues:

1. Check the Docker logs:
   ```bash
   docker logs $(docker ps -q --filter ancestor=flight-agent)
   ```

2. Verify your API keys are correct:
   - Mistral AI API key
   - Amadeus API credentials

3. Check email configuration:
   - Ensure SENDER_EMAIL and SENDER_PASSWORD are correct
   - For Gmail, use an App Password instead of your regular password

4. Verify city codes:
   - Use valid IATA city codes (e.g., NYC for New York, LAX for Los Angeles)
   - Check the Amadeus documentation for supported city codes

5. Check date format:
   - Ensure FLIGHT_DATE is in YYYY-MM-DD format
   - The date should be in the future

6. Monitor API usage:
   - Check your Amadeus API usage limits
   - The free tier includes 2000 API calls per month

## Configuration Options

### Environment Variables

- `MISTRAL_API_KEY`: Your Mistral AI API key
- `AMADEUS_CLIENT_ID`: Your Amadeus API Client ID
- `AMADEUS_CLIENT_SECRET`: Your Amadeus API Client Secret
- `SENDER_EMAIL`: Your Gmail address for sending notifications
- `SENDER_PASSWORD`: Your Gmail App Password
- `RECIPIENT_EMAIL`: Email address to receive notifications
- `FROM_CITY`: Departure city IATA code
- `TO_CITY`: Arrival city IATA code
- `FLIGHT_DATE`: Desired flight date (YYYY-MM-DD)

### Scheduling

- The application checks for flights daily at 9:00 AM
- You can modify the schedule in the `main()` function of `flight_agent.py`
- The application also runs an immediate check on startup

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the Amadeus API documentation
3. Check the Mistral AI documentation
4. Open an issue in the repository