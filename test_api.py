import requests

API_KEY = "4ffb18f54c98e469a82cf38b580e9e49"

city = "Delhi"

url = (
    f"https://api.openweathermap.org/data/2.5/weather"
    f"?q={city}&appid={API_KEY}&units=metric"
)

response = requests.get(url)

print(response.status_code)
print(response.json())