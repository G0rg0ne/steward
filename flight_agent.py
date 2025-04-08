import os
import schedule
import time
import yaml
from datetime import datetime
from dotenv import load_dotenv
from amadeus import Client, ResponseError
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from loguru import logger

# Configure loguru
logger.add(
    "logs/flight_agent_{time}.log",
    rotation="1 day",
    retention="7 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)

def load_config():
    """
    Load configuration from config.yaml
    """
    try:
        with open('config.yaml', 'r') as file:
            config = yaml.safe_load(file)
        logger.info("Configuration loaded successfully")
        return config
    except Exception as e:
        logger.error(f"Error loading configuration: {str(e)}")
        raise

# Load environment variables and configuration
load_dotenv()
config = load_config()

# Debug environment variables
logger.info("Checking environment variables...")
logger.info(f"FROM_CITY: {os.getenv('FROM_CITY')}")
logger.info(f"TO_CITY: {os.getenv('TO_CITY')}")
logger.info(f"FLIGHT_DATE: {os.getenv('FLIGHT_DATE')}")
logger.info(f"AMADEUS_CLIENT_ID exists: {bool(os.getenv('AMADEUS_CLIENT_ID'))}")
logger.info(f"AMADEUS_CLIENT_SECRET exists: {bool(os.getenv('AMADEUS_CLIENT_SECRET'))}")

# Initialize Mistral AI client
mistral_client = MistralClient(api_key=os.getenv("MISTRAL_API_KEY"))

# Initialize Amadeus client
try:
    amadeus = Client(
        client_id=os.getenv("AMADEUS_CLIENT_ID"),
        client_secret=os.getenv("AMADEUS_CLIENT_SECRET")
    )
    logger.info("Amadeus client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Amadeus client: {str(e)}")
    raise

def get_cheapest_flights(from_city, to_city, departure_date, return_date=None):
    """
    Get the top 3 cheapest flights using the Amadeus API, including return flights if specified
    """
    try:
        logger.info(f"Searching for flights from {from_city} to {to_city}")
        logger.info(f"Departure date: {departure_date}, Return date: {return_date}")
        
        max_results = config['flight']['search']['max_results']
        adults = config['flight']['search']['adults']
        
        # Search for outbound flight offers
        outbound_response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=from_city,
            destinationLocationCode=to_city,
            departureDate=departure_date,
            adults=adults,
            max=max_results
        )
        
        outbound_flights = []
        return_flights = []
        
        # Process outbound flights
        for offer in outbound_response.data:
            itinerary = offer['itineraries'][0]
            segments = itinerary['segments']
            
            price = offer['price']['total']
            currency = offer['price']['currency']
            airline = segments[0]['carrierCode']
            departure = segments[0]['departure']['at']
            arrival = segments[-1]['arrival']['at']
            
            outbound_flights.append({
                'date': departure_date,
                'departure_time': departure,
                'arrival_time': arrival,
                'price': f"{price} {currency}",
                'airline': airline,
                'stops': len(segments) - 1
            })
        
        # If return date is specified, search for return flights
        if return_date:
            return_response = amadeus.shopping.flight_offers_search.get(
                originLocationCode=to_city,
                destinationLocationCode=from_city,
                departureDate=return_date,
                adults=1,
                max=5
            )
            
            for offer in return_response.data:
                itinerary = offer['itineraries'][0]
                segments = itinerary['segments']
                
                price = offer['price']['total']
                currency = offer['price']['currency']
                airline = segments[0]['carrierCode']
                departure = segments[0]['departure']['at']
                arrival = segments[-1]['arrival']['at']
                
                return_flights.append({
                    'date': return_date,
                    'departure_time': departure,
                    'arrival_time': arrival,
                    'price': f"{price} {currency}",
                    'airline': airline,
                    'stops': len(segments) - 1
                })
        
        # Sort flights by price
        sorted_outbound = sorted(outbound_flights, key=lambda x: float(x['price'].split()[0]))[:3]
        sorted_return = sorted(return_flights, key=lambda x: float(x['price'].split()[0]))[:3] if return_flights else []
        
        logger.info(f"Found {len(sorted_outbound)} outbound flights and {len(sorted_return)} return flights")
        return {
            'outbound': sorted_outbound,
            'return': sorted_return
        }
        
    except ResponseError as error:
        logger.error(f"Amadeus API Error: {error}")
        logger.error(f"Error Code: {error.code}")
        logger.error(f"Error Description: {error.description}")
        logger.error(f"Error Response: {error.response}")
        return {'outbound': [], 'return': []}
    except Exception as e:
        logger.error(f"Unexpected error while fetching flights: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        return {'outbound': [], 'return': []}

def analyze_flights_with_ai(flights, from_city, to_city):
    """
    Use Mistral AI to analyze and format the flight information
    """
    if not flights['outbound']:
        logger.warning("No flights found for analysis")
        return "No flights found for the specified route."
    
    outbound_info = "\nOutbound Flights:\n" + "\n".join([
        f"Date: {flight['date']}, "
        f"Departure: {flight['departure_time']}, "
        f"Arrival: {flight['arrival_time']}, "
        f"Price: {flight['price']}, "
        f"Airline: {flight['airline']}, "
        f"Stops: {flight['stops']}"
        for flight in flights['outbound']
    ])
    
    return_info = ""
    if flights['return']:
        return_info = "\n\nReturn Flights:\n" + "\n".join([
            f"Date: {flight['date']}, "
            f"Departure: {flight['departure_time']}, "
            f"Arrival: {flight['arrival_time']}, "
            f"Price: {flight['price']}, "
            f"Airline: {flight['airline']}, "
            f"Stops: {flight['stops']}"
            for flight in flights['return']
        ])
    
    flight_info = outbound_info + return_info
    
    logger.info("Analyzing flights with Mistral AI")
    messages = [
        ChatMessage(role="user", content=f"""
        Please analyze these flight options between {from_city} and {to_city} and provide a concise summary:
        {flight_info}
        
        Focus on:
        1. The best round-trip combinations (if return flights are available)
        2. The best deals available for each direction
        3. Any notable patterns in pricing
        4. The number of stops for each flight
        5. The time differences between flights
        6. Total cost for the best round-trip combination
        """)
    ]
    
    chat_response = mistral_client.chat(
        model="mistral-medium",
        messages=messages
    )
    
    return chat_response.choices[0].message.content

def send_email_notification(subject, body):
    """
    Send email notification using SMTP
    """
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    recipient_email = os.getenv("RECIPIENT_EMAIL")
    
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg["Subject"] = subject
    
    msg.attach(MIMEText(body, "plain"))
    
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        logger.info("Email notification sent successfully")
    except Exception as e:
        logger.error(f"Error sending email: {e}")

def daily_flight_check():
    """
    Main function to check flights and send notifications
    """
    flight_routes = config['flight']['routes']
    
    for route in flight_routes:
        from_city = route['from_city']
        to_city = route['to_city']
        departure_date = route['departure_date']
        return_date = route.get('return_date')
        
        logger.info(f"Processing route: {route['name']}")
        logger.info(f"Departure date: {departure_date}, Return date: {return_date}")
        
        flights = get_cheapest_flights(from_city, to_city, departure_date, return_date)
        
        if flights['outbound']:
            analysis = analyze_flights_with_ai(flights, from_city, to_city)
            subject = f"Flight Deals: {route['name']} ({departure_date}"
            if return_date:
                subject += f" - {return_date})"
            else:
                subject += ")"
            send_email_notification(subject, analysis)
        else:
            logger.warning(f"No flights found for {route['name']}")

def main():
    logger.info("Starting flight agent application")
    
    # Get schedule configuration
    schedule_time = config['flight']['notification']['schedule']['time']
    
    # Schedule the daily check
    schedule.every().day.at(schedule_time).do(daily_flight_check)
    
    # Run the check immediately on startup
    daily_flight_check()
    
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(120)

if __name__ == "__main__":
    main() 