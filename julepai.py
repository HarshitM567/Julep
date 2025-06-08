# Cell 2: Imports & Keys Setup
from openai import AzureOpenAI
import requests
import json

# Azure OpenAI settings
AZURE_OPENAI_API_KEY = "YourAPIKEY" # e.g., "your-azure-openai-api-key"
AZURE_OPENAI_ENDPOINT = "ENDPOINT"  # e.g., "https://your-resource-name.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME = "gpt-4"

# OpenWeather
OPENWEATHER_API_KEY = "weather api"

client = AzureOpenAI(
    api_version="2024-12-01-preview",
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY
)
# Cell 3: Get weather + recommend indoor/outdoor
def get_weather_and_dining(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    res = requests.get(url).json()

    if "weather" not in res or "main" not in res:
        raise ValueError(f"Error fetching weather for {city}: {res.get('message', 'Unknown error')}")

    weather = res['weather'][0]['main'].lower()
    temp = res['main']['temp']
    dining = "outdoor" if weather in ['clear', 'clouds'] else "indoor"
    return weather, temp, dining


# Cell 4: Get iconic dishes via Azure OpenAI
def get_iconic_dishes(city):
    prompt = f"List 3 iconic local dishes from {city} with short descriptions."

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a culinary travel expert."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=250,
        temperature=0.8
    )

    # Ensure the response structure is correct
    if hasattr(response, 'choices') and len(response.choices) > 0:
        content = response.choices[0].message.content
        dishes = [line.strip(" -•\n") for line in content.split("\n") if line.strip()]
        return dishes[:3]
    else:
        raise ValueError("Unexpected response structure from Azure OpenAI API.")


# Cell 5: Get restaurant recommendation
def find_restaurant_for_dish(city, dish):
    prompt = f"Suggest a top-rated restaurant in {city} that serves {dish}. Include the name, address, and why it's top-rated."

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a food and travel guide."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=250,
        temperature=0.7
    )

    # Ensure the response structure is correct
    if hasattr(response, 'choices') and len(response.choices) > 0:
        content = response.choices[0].message.content
        return content.strip()
    else:
        raise ValueError("Unexpected response structure from Azure OpenAI API.")
# Cell 6: Full tour planner (modified to return output)
def create_foodie_tour(city):
    weather, temp, dining = get_weather_and_dining(city)
    output = f"\n🌤️ Weather in {city}: {weather}, {temp}°C — recommended: **{dining} dining**\n"

    dishes = get_iconic_dishes(city)
    output += f"\n🍽️ Dishes: {dishes}\n"

    meals = ["Breakfast", "Lunch", "Dinner"]
    tour = []

    for meal, dish in zip(meals, dishes):
        rest = find_restaurant_for_dish(city, dish)
        tour.append(f"### {meal} - {dish}\n{rest}\n")

    output += "\n📍 Final Foodie Tour for {city}:\n"
    for step in tour:
        output += step

    return output

# Cell 7: Streamlit dropdown for city selection (updated to display output)
import streamlit as st

st.title("Foodie Tour Planner")

# Dropdown for city selection with unique key
city = st.selectbox(
    "Select a city to plan your foodie tour:",
    ["Rome", "Bangkok", "San Francisco", "Tokyo", "Paris", "New York", "Mumbai", "Cape Town", "Sydney", "Dubai", "Kota"],
    key="city_selection"
)

if st.button("Create Foodie Tour", key="create_tour_button"):
    try:
        tour_output = create_foodie_tour(city)
        st.markdown(tour_output)
    except Exception as e:
        st.error(f"An error occurred: {e}")