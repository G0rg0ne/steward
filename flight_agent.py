import os
import schedule
import time
from datetime import datetime
from dotenv import load_dotenv
from amadeus import Client, ResponseError
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

# Load environment variables
load_dotenv()

# Initialize Mistral AI client
mistral_client = MistralClient(api_key=os.getenv("MISTRAL_API_KEY"))

# Initialize Amadeus client
amadeus = Client(
    client_id=os.getenv("AMADEUS_CLIENT_ID"),
    client_secret=os.getenv("AMADEUS_CLIENT_SECRET")
)

def get_cheapest_flights(from_city, to_city, flight_date):
    """
    Get the top 3 cheapest flights using the Amadeus API
    """
    try:
        # Search for flight offers
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=from_city,
            destinationLocationCode=to_city,
            departureDate=flight_date,
            adults=1,
            max=5  # Get top 5 offers to ensure we have enough valid ones
        )
        flights = []
        for offer in response.data:
            # Get the first itinerary (usually the cheapest)
            itinerary = offer['itineraries'][0]
            segments = itinerary['segments']
            
            # Get pricing information
            price = offer['price']['total']
            currency = offer['price']['currency']
            
            # Get airline information
            airline = segments[0]['carrierCode']
            
            # Get departure and arrival times
            departure = segments[0]['departure']['at']
            arrival = segments[-1]['arrival']['at']
            
            flights.append({
                'date': flight_date,
                'departure_time': departure,
                'arrival_time': arrival,
                'price': f"{price} {currency}",
                'airline': airline,
                'stops': len(segments) - 1
            })
        
        # Sort by price and return top 3
        sorted_flights = sorted(flights, key=lambda x: float(x['price'].split()[0]))
        return sorted_flights[:3]
        
    except ResponseError as error:
        print(f"Error fetching flights: {error}")
        return []

def analyze_flights_with_ai(flights, from_city, to_city):
    """
    Use Mistral AI to analyze and format the flight information
    """
    if not flights:
        return "No flights found for the specified route."
    
    flight_info = "\n".join([
        f"Date: {flight['date']}, "
        f"Departure: {flight['departure_time']}, "
        f"Arrival: {flight['arrival_time']}, "
        f"Price: {flight['price']}, "
        f"Airline: {flight['airline']}, "
        f"Stops: {flight['stops']}"
        for flight in flights
    ])
    
    messages = [
        ChatMessage(role="user", content=f"""
        Please analyze these flight options from {from_city} to {to_city} and provide a concise summary:
        {flight_info}
        
        Focus on:
        1. The best deals available
        2. Any notable patterns in pricing
        3. The number of stops for each flight
        4. The time differences between flights
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
        print("Email notification sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

def daily_flight_check():
    """
    Main function to check flights and send notifications
    """
    from_city = os.getenv("FROM_CITY", "NYC")  # Default to NYC
    to_city = os.getenv("TO_CITY", "LAX")      # Default to LAX
    flight_date = os.getenv("FLIGHT_DATE")     # Get the specified flight date
    
    if not flight_date:
        print("Error: FLIGHT_DATE environment variable is not set")
        return
    
    print(f"Checking flights from {from_city} to {to_city} on {flight_date}...")
    flights = get_cheapest_flights(from_city, to_city, flight_date)
    
    if flights:
        analysis = analyze_flights_with_ai(flights, from_city, to_city)
        subject = f"Flight Deals: {from_city} to {to_city} on {flight_date}"
        send_email_notification(subject, analysis)
    else:
        print(f"No flights found for {from_city} to {to_city} on {flight_date}")

def main():
    # Schedule the daily check (runs at 9 AM every day)
    schedule.every().day.at("09:00").do(daily_flight_check)
    
    # Run the check immediately on startup
    daily_flight_check()
    
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main() 