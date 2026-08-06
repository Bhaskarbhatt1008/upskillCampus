import streamlit as st
import pandas as pd
import joblib
import requests
from datetime import datetime
import matplotlib.pyplot as plt
from deep_translator import GoogleTranslator

with st.sidebar:
    st.title("🚗 Smart City")

    st.subheader("🕒 Current Time")
    st.write(datetime.now().strftime("%d %b %Y"))
    st.write(datetime.now().strftime("%I:%M %p"))

    city_placeholder = st.empty()   # 👈 Add this

    st.info("""
AI-Based Traffic Forecasting System

👨‍💻 Developed By:
Bhaskar Bhatt

📅 Year: 2026
""")
    
    with st.sidebar.expander("🌐 APIs Used"):
     st.write("• OpenWeatherMap")
     st.write("• OpenRouteService")

roads_df = pd.read_csv("./data/roads.csv")
road_factor_df = pd.read_csv(
    "./data/road_data.csv"
)

# ==========================
# ROUTE TRANSLATION
# ==========================

@st.cache_data
def translate_route(text, language):

    try:

        translated = GoogleTranslator(
            source="auto",
            target=language
        ).translate(text)

        return translated

    except:

        return text


API_KEY = ""
ORS_API_KEY = ""


# ==========================
# LOAD MODEL
# ==========================

@st.cache_resource
def load_model():

    return joblib.load(
        "models/traffic_model.pkl"
    )


model = load_model()


# ==========================
# LOAD DATA
# ==========================

@st.cache_data
def load_data():

    df = pd.read_csv(
        "data/Metro_Interstate_Traffic_Volume.csv"
    )

    df["date_time"] = pd.to_datetime(
        df["date_time"]
    )

    city_df = pd.read_csv(
        "data/city_data.csv"
    )

    festival_df = pd.read_csv(
        "data/festival_calendar.csv"
    )

    festival_df["date"] = pd.to_datetime(
        festival_df["date"]
    )

    return df, city_df, festival_df

df, city_df, festival_df = load_data()
# ==========================
# CITY REGION
# ==========================

city_region = {

    "Delhi": "North India",
    "Mumbai": "Maharashtra",
    "Chennai": "Tamil Nadu",
    "Kochi": "Kerala",
    "Kolkata": "West Bengal",
    "Guwahati": "Assam",
    "Patna": "Bihar",
    "Amritsar": "Punjab",
    "Jaipur": "Rajasthan",
    "Lucknow": "North India"

}

state_alias = {

    # States
    "Andhra Pradesh": "Vijayawada",
    "Arunachal Pradesh": "Itanagar",
    "Assam": "Guwahati",
    "Bihar": "Patna",
    "Chhattisgarh": "Raipur",
    "Goa": "Panaji",
    "Gujarat": "Ahmedabad",
    "Haryana": "Gurgaon",
    "Himachal Pradesh": "Shimla",
    "Jharkhand": "Ranchi",
    "Karnataka": "Bangalore",
    "Kerala": "Kochi",
    "Madhya Pradesh": "Bhopal",
    "Maharashtra": "Mumbai",
    "Manipur": "Imphal",
    "Meghalaya": "Shillong",
    "Mizoram": "Aizawl",
    "Nagaland": "Kohima",
    "Odisha": "Bhubaneswar",
    "Punjab": "Amritsar",
    "Rajasthan": "Jaipur",
    "Sikkim": "Gangtok",
    "Tamil Nadu": "Chennai",
    "Telangana": "Hyderabad",
    "Tripura": "Agartala",
    "Uttar Pradesh": "Lucknow",
    "Uttarakhand": "Dehradun",
    "West Bengal": "Kolkata",

    # Union Territories
    "Andaman and Nicobar Islands": "Port Blair",
    "Chandigarh": "Chandigarh",
    "Dadra and Nagar Haveli and Daman and Diu": "Daman",
    "Delhi": "New Delhi",
    "Jammu and Kashmir": "Srinagar",
    "Ladakh": "Leh",
    "Lakshadweep": "Kavaratti",
    "Puducherry": "Puducherry"
}

city_alias_location = {

    # Uttarakhand
    "Gadarpur": "Gadarpur Uttarakhand India",
    "Rudrapur": "Rudrapur Uttarakhand India",
    "Haldwani": "Haldwani Uttarakhand India",
    "Kashipur": "Kashipur Uttarakhand India",

    # Uttar Pradesh
    "Rampur": "Rampur Uttar Pradesh India",
    "Bareilly": "Bareilly Uttar Pradesh India",
    "Prayagraj": "Prayagraj Uttar Pradesh India",

    # Chhattisgarh / Himachal duplicate names
    "Bilaspur": "Bilaspur Chhattisgarh India",

    # Maharashtra
    "Aurangabad": "Aurangabad Maharashtra India",
    "Nashik": "Nashik Maharashtra India",

    # Madhya Pradesh
    "Indore": "Indore Madhya Pradesh India",

    # Rajasthan
    "Bharatpur": "Bharatpur Rajasthan India",

    # Punjab / Haryana
    "Ambala": "Ambala Haryana India",
    "Patiala": "Patiala Punjab India",

    # Karnataka
    "Bangalore": "Bangalore Karnataka India",
    "Mysore": "Mysore Karnataka India",

    # Tamil Nadu
    "Madurai": "Madurai Tamil Nadu India",
    "Salem": "Salem Tamil Nadu India",

    # Andhra / Telangana
    "Warangal": "Warangal Telangana India",
    "Vijayawada": "Vijayawada Andhra Pradesh India",

    # West Bengal
    "Durgapur": "Durgapur West Bengal India",

    # Odisha
    "Cuttack": "Cuttack Odisha India"
}

# ==========================
# AUTO INDIA CITY FACTOR
# ==========================

def get_city_factor(city):

    try:

        city_info = city_df[
            city_df["city"].str.lower()
            ==
            city.lower()
        ]


        if len(city_info) > 0:

            # CSV se road_factor lena
            factor = float(
                city_info.iloc[0]["road_factor"]
            )

        else:

            # unknown cities ke liye default
            factor = 1.0


        return factor


    except:

        return 0.6
    
def get_road_factor(city, road):

    try:

        data = road_factor_df[
            (road_factor_df["city"].str.lower() == city.lower())
            &
            (road_factor_df["road_name"] == road)
        ]

        if len(data) > 0:
            return float(
                data.iloc[0]["road_factor"]
            )

        else:
            return 1.0

    except:
        return 1.0   

def get_road_time_factor(city, road, hour):

    try:
        data = road_factor_df[
            (road_factor_df["city"].str.lower() == city.lower())
            &
            (road_factor_df["road_name"] == road)
        ]

        if len(data) > 0:

            morning = float(data.iloc[0]["morning_factor"])
            evening = float(data.iloc[0]["evening_factor"])

            if 7 <= hour <= 10:
                return morning

            elif 17 <= hour <= 20:
                return evening

        return 1.0

    except:
        return 1.0
    
# ==========================
# GET COORDINATES
# ==========================
@st.cache_data
def get_coordinates(place):

    place = place.strip().title()


    if place in state_alias:
        place = state_alias[place]


    if place in city_alias_location:
        place = city_alias_location[place]


    url = "https://api.openrouteservice.org/geocode/search"


    headers = {
        "Authorization": ORS_API_KEY
    }


    params = {
        "text": place,
        "size": 10,
        "boundary.country": "IND"
    }


    try:
        response = requests.get(
        url,
        params=params,
        headers=headers,
        timeout=5
    )
    except requests.exceptions.Timeout:
          return None, None
    except requests.exceptions.RequestException as e:
        st.error(f"Network error: {e}")
        return None, None

    if response.status_code != 200:
        print("Status Code:", response.status_code)
        print("Response:", response.text)
        return None, None

    try:
        data = response.json()
    except Exception:
        print("JSON Error")
        print("Status Code:", response.status_code)
        print("Response:", response.text)
        return None, None

    if "features" in data:
     for feature in data["features"]:
        props = feature["properties"]

        if props.get("country") == "India":
            lon, lat = feature["geometry"]["coordinates"]
            return lat, lon

    return None, None


# ==========================
# GET MULTIPLE ROUTES
# ==========================
def get_routes(start_lat, start_lon, end_lat, end_lon):

    url = "https://api.openrouteservice.org/v2/directions/driving-car"

    headers = {
        "Authorization": ORS_API_KEY,
        "Content-Type": "application/json"
    }

    body = {
    "coordinates": [
        [start_lon, start_lat],
        [end_lon, end_lat]
    ],
    "instructions": True,

    "alternative_routes":{
        "target_count":3,
        "weight_factor":1.6,
        "share_factor":0.6
    }
}

    response = requests.post(
        url,
        json=body,
        headers=headers,
        timeout=15
    )

# 400 error handle
    if response.status_code == 400:
        error = response.json()

        if "100000.0 meters" in error.get("error", {}).get("message", ""):
            body = {
                "coordinates": [
                    [start_lon, start_lat],
                    [end_lon, end_lat]
                ],
                "instructions": True
            }

            # Request again
            response = requests.post(url, json=body, headers=headers)

    # Check final response
    if response.status_code != 200:
        print("Status:", response.status_code)
        print(response.text)
        return []

    data = response.json()
    print(data)
    routes = []
    seen = set()

    if "routes" in data:

     for route in data["routes"]:

        summary = route["summary"]

        steps = []

        for seg in route["segments"]:
            steps.extend(seg["steps"])


        instructions = tuple(
            step["instruction"]
            for step in steps
            if "instruction" in step
        )


        if instructions in seen:
            continue


        seen.add(instructions)


        routes.append({
            "distance": summary["distance"] / 1000,
            "time": summary["duration"] / 60,
            "route_name": steps
        })

    return routes
    
st.title("🚦 Smart City Traffic Forecasting")
st.caption("AI-Powered Traffic Prediction & Route Recommendation System")
if "city_loaded" not in st.session_state:
    st.session_state.city_loaded = False

with st.form(
    "city_form",
    enter_to_submit=False
):

    if "city_input" not in st.session_state:
     st.session_state.city_input = ""

    city = st.text_input(
            "Enter City",
            st.session_state.city_input
        ).strip().title()
    
    if city:
     city_placeholder.metric("📍 Selected City", city)

    load = st.form_submit_button(
        "Load Data"
    )

if load:

    if city.strip() == "":

        st.warning(
            "Please enter a city."
        )
        st.stop()


    st.session_state.city_loaded = True
    st.session_state.city = city
    st.session_state.city_input = city

if not st.session_state.city_loaded:

    st.info(
        "🏙 Enter city and click Load Data."
    )
    st.stop()


city = st.session_state.city
 
if st.button("Change City"):

    st.session_state.city_loaded = False
    st.session_state.city = ""
    st.session_state.city_input = ""

    if "lat" in st.session_state:
        del st.session_state.lat

    if "lon" in st.session_state:
        del st.session_state.lon

    st.rerun()
    
# ==========================
# WEATHER API
# ==========================

temp = 25
rain = 0
snow = 0
clouds = 50


try:

    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={API_KEY}&units=metric"
    )


    response = requests.get(url)

    data = response.json()


    if response.status_code == 200:

        temp = data["main"]["temp"]
        clouds = data["clouds"]["all"]
        
        lat = data["coord"]["lat"]
        lon = data["coord"]["lon"]

        st.session_state.lat = lat
        st.session_state.lon = lon


        if "rain" in data:
            rain = data["rain"].get("1h",0)


        if "snow" in data:
            snow = data["snow"].get("1h",0)



        st.success(
            "🌤 Live Weather Loaded"
        )


        c1,c2,c3 = st.columns(3)


        c1.metric(
            "Temperature",
            f"{temp} °C"
        )


        c2.metric(
            "Clouds",
            f"{clouds}%"
        )


        c3.metric(
            "Rain",
            f"{rain} mm"
        )
        
        if rain == 0:
            rain_status = "☀️ No Rain"

        elif rain < 2:
            rain_status = "🌦️ Light Rain"

        elif rain < 7:
            rain_status = "🌧️ Moderate Rain"

        else:
            rain_status = "⛈️ Heavy Rain"

        st.info(
            f"{rain_status} ({rain} mm)"
        )


    else:

        st.warning(
            "Weather API Error"
        )


except Exception as e:

    st.warning(
        f"Weather API not loaded : {e}"
    )



# ==========================
# DATE TIME
# ==========================

now = datetime.now()


year = now.year
month = now.month
day = now.day
hour = now.hour
weekday = now.weekday()



st.info(
    now.strftime(
        " %d %B %Y |  %I:%M %p"
    )
)

# ==========================
# FESTIVAL CHECK
# ==========================


region = city_region.get(
    city,
    "All India"
)


today = pd.to_datetime(
    now.strftime("%Y-%m-%d")
)



festival = festival_df[
    (festival_df["date"] == today)
    &
    (
        (festival_df["region"] == region)
        |
        (festival_df["region"] == "All India")
    )
]


if len(festival)>0:

    st.warning(
        f"🎉 Festival : {festival.iloc[0]['festival']}"
    )

else:

    st.success(
        "📅 No Festival Today"
    )
    
# ==========================
# ROAD SELECTION
# ==========================

city_roads = roads_df[
    roads_df["city"].str.lower() == city.lower()
]

if len(city_roads) > 0:

    selected_road = st.selectbox(
        "🛣️ Select Road",
        city_roads["road_name"].tolist()
    )

else:

    selected_road = "Overall Traffic"
    st.info("No road data available. Showing city prediction.")


# ==========================
# FORECAST
# ==========================

city_alias = {
    "Bengaluru":"Bangalore"
}

if city in city_alias:
    city = city_alias[city]


st.subheader(
    f"📈 {selected_road} Traffic Forecast"
)


forecast_option = st.radio(
    "Select Forecast",
    [
        "Today Traffic Forecast",
        "Next 24 Hours Forecast"
    ],
    horizontal=True
)


today_date = now.strftime("%d %B %Y")


if forecast_option == "Today Traffic Forecast":

    st.info(f"📅 Today Traffic Forecast : {today_date}")

    forecast_range = range(0,24)


else:

    st.info(
        f"📅 Next 24 Hours Forecast : {today_date} onwards"
    )

    forecast_range = range(hour, hour+24)


forecast_data = []

for h in forecast_range:

    forecast_hour = h % 24

    # date handling
    if forecast_option == "Today Traffic Forecast":
        future_day = day
    else:
        if h >= 24:
            future_day = day + 1
        else:
            future_day = day


    sample = pd.DataFrame(

        [[
            temp,
            rain,
            snow,
            clouds,
            year,
            month,
            future_day,
            forecast_hour,
            weekday
        ]],

        columns=[
            "temp",
            "rain_1h",
            "snow_1h",
            "clouds_all",
            "year",
            "month",
            "day",
            "hour",
            "weekday"
        ]
    )


    prediction = model.predict(sample)[0]


    factor = get_city_factor(city)


    road_factor = get_road_factor(
    city,
    selected_road
    )

    traffic = int(
        prediction * factor * road_factor
    )

    forecast_data.append(
    [
        forecast_hour,
        traffic
    ]
)



forecast_df = pd.DataFrame(
    forecast_data,
    columns=[
        "Hour",
        "Traffic"
    ]
)

# Display time only
forecast_df["Time"] = forecast_df["Hour"].apply(
    lambda x:
    datetime.strptime(
        str(x % 24),
        "%H"
    ).strftime("%I:%M %p")
)

st.line_chart(
    forecast_df.set_index("Hour")["Traffic"]
)

# ==========================
# PEAK ANALYSIS
# ==========================


peak = forecast_df.loc[
    forecast_df["Traffic"].idxmax()
]


c1,c2 = st.columns(2)


c1.metric(
    "Peak Time",
    peak["Time"]
)


c2.metric(
    "Maximum Traffic",
    int(peak["Traffic"])
)

# ==========================
# AI ROUTE RECOMMENDATION
# ==========================

st.subheader("🛣️ AI Route Recommendation")


if "route_found" not in st.session_state:
    st.session_state.route_found = False

if "routes" not in st.session_state:
    st.session_state.routes = []


source = st.text_input(
    "📍 Source"
)

destination = st.text_input(
    "🎯 Destination"
)


find_route = st.button(
    "Find Best Route"
)



# ==========================
# FIND ROUTE BUTTON
# ==========================

if find_route:

    if source.strip() == "" and destination.strip() == "":
        st.warning("⚠️ Please enter Source and Destination.")

    elif source.strip() == "":
        st.warning("⚠️ Please enter Source.")

    elif destination.strip() == "":
        st.warning("⚠️ Please enter Destination.")

    elif source.strip().lower() == destination.strip().lower():
        st.warning("⚠️ Source and Destination cannot be the same.")

    else:
        with st.spinner("Finding best route..."):

            s_lat, s_lon = get_coordinates(source)
            d_lat, d_lon = get_coordinates(destination)

        if s_lat is None and d_lat is None:
            st.error("❌ Both Source and Destination are invalid.")
            st.session_state.route_found = False

        elif s_lat is None:
            st.error("❌ Source location not found.")
            st.session_state.route_found = False

        elif d_lat is None:
            st.error("❌ Destination location not found.")
            st.session_state.route_found = False

        else:

            routes = get_routes(
                s_lat,
                s_lon,
                d_lat,
                d_lon
            )


            st.session_state.routes = routes
            st.session_state.route_found = True


            if len(routes) == 1:

                st.info(
                    "Only one optimized route found."
                )

            else:

                st.info(
                    f"{len(routes)} alternative routes found."
                )



# ==========================
# DISPLAY ROUTES
# ==========================

if st.session_state.route_found:


    routes = st.session_state.routes


    if len(routes) > 0:


        st.subheader(
            "🛣️ Available Routes"
        )


        scores = []


        for i,r in enumerate(routes):


            traffic_level = forecast_df["Traffic"].mean()


            score = (
                -(r["time"] * 0.5)
                -(r["distance"] * 0.2)
                +(traffic_level * 0.3)
            )


            scores.append(score)


            total_minutes = int(
                r["time"]
            )


            hours = total_minutes // 60

            minutes = total_minutes % 60


            eta_text = (
                f"{hours} hr {minutes} min"
            )


            route_text = (
                "Road details not available"
            )


            try:

                roads = []


                for step in r["route_name"]:


                    if "instruction" in step:


                        text = step["instruction"]


                        roads.append(
                            text
                        )


                route_text = "\n\n".join(
                    [
                        f"➡️ {road}"
                        for road in roads
                    ]
                )


            except:

                pass



            st.write(
                f"""
### Route {i+1}

📏 Distance : {r['distance']:.1f} km

⏱ ETA : {eta_text}
"""
            )



            with st.expander(
                f"🛣️ Full Route {i+1} Details"
            ):


                lang_options = {

                    "English":"en",
                    "Hindi":"hi",
                    "French":"fr",
                    "Spanish":"es",
                    "German":"de"

                }


                selected_lang = st.selectbox(

                    "🌐 Translate Route",

                    lang_options.keys(),

                    key=f"lang_{i}"

                )


                if selected_lang == "English":

                    st.text(
                        route_text
                    )
                    
                else:

                    translated_route = translate_route(
                        route_text.replace("➡️",""),
                        lang_options[selected_lang]
                    )

                    st.text(translated_route)


        best_route = scores.index(
            max(scores)
        )


        st.success(
            f"""
🤖 AI Recommended Route

✅ Route {best_route+1}

Reason:
- Short travel distance
- Optimized route generated by OpenRouteService
"""
        )


    else:

        st.error(
            "No routes found"
        )
# ==========================
# ADVANCED TRAFFIC DASHBOARD
# ==========================
with st.expander(
    "📊 Smart Traffic Dashboard",
    expanded=False
):



                # Current traffic safe calculation

                current_data = forecast_df[
                    forecast_df["Hour"] == hour
                ]


                if len(current_data) > 0:

                    current = current_data["Traffic"].values[0]

                else:

                    current = forecast_df["Traffic"].iloc[-1]



                max_traffic = forecast_df["Traffic"].max()


                # Avoid division error

                if max_traffic > 0:

                    congestion = int(
                        (current / max_traffic) * 100
                    )

                else:

                    congestion = 0


               # Next upcoming peak (current time ke baad)

                future = forecast_df[
                    forecast_df["Hour"] > hour
                ]


                if len(future) > 0:

                    next_peak = future.loc[
                        future["Traffic"].idxmax()
                    ]

                else:

                    next_peak = forecast_df.loc[
                        forecast_df["Traffic"].idxmax()
                    ]


                # Traffic Status

                if congestion > 70:

                    status = "🔴 Heavy Traffic"

                elif congestion > 40:

                    status = "🟠 Moderate Traffic"

                else:

                    status = "🟢 Low Traffic"



                # Dashboard Cards

                st.write("Real-Time Traffic Overview")


                c1,c2,c3,c4 = st.columns(4)


                with c1:

                    st.metric(
                        "🚦 Current Status",
                        status
                    )


                with c2:

                    st.metric(
                        "📊 Congestion",
                        f"{congestion}%"
                    )


                with c3:

                    st.metric(
                        "⏰ Upcoming peak",
                        next_peak["Time"]
                    )


                with c4:

                    st.metric(
                        "🚗 Vehicles",
                        int(current)
                    )


                # Live Traffic Indicator

                st.write("🟢 Live Traffic Indicator")

                st.progress(
                    min(congestion/100,1)
                )


                if congestion < 40:
                    traffic_flow = "Smooth Flow 🚗"

                elif congestion < 70:
                    traffic_flow = "Moderate Flow 🚙"

                else:
                    traffic_flow = "Slow Traffic 🚨"


                st.info(
                    f"Traffic Flow : {traffic_flow}"
                )



                # Next 3 hour trend

                st.subheader("📈 Next 3 Hour Traffic Trend")


               # Current hour ka index

                current_row = forecast_df[
                    forecast_df["Hour"] == hour
                ]


                if len(current_row) > 0:

                    current_index = current_row.index[0]

                else:

                    current_index = 0


                # Next 3 hours

                next_hours = forecast_df.iloc[
                    current_index:current_index+3
                ]


                # Midnight cross fix

                if len(next_hours) < 3:

                    remaining = 3 - len(next_hours)

                    next_hours = pd.concat(
                        [
                            next_hours,
                            forecast_df.iloc[:remaining]
                        ]
                    )
                st.dataframe(
                    next_hours[
                        ["Time","Traffic"]
                    ],
                    hide_index=True
                )



                # Weather Impact

                st.subheader("🌧 Weather Impact")


                weather_reason=[]


                if rain>0:

                    weather_reason.append(
                        f"Rain detected ({rain} mm). Vehicle speed may reduce."
                    )


                if clouds>70:

                    weather_reason.append(
                        "Cloudy weather condition."
                    )


                if len(weather_reason)==0:

                    weather_reason.append(
                        "Weather has low impact on traffic."
                    )


                for w in weather_reason:
                    st.write(w)



                # AI Recommendation

                st.subheader("🤖 AI Recommendation")


                # AI Recommendation


                if rain > 0 and congestion > 70:

                    recommendation = (
                        f"🌧🚨 Heavy traffic with rain detected "
                        f"({rain} mm). Avoid travelling now."
                    )


                elif rain > 0:

                    recommendation = (
                        f"🌧 Rain detected ({rain} mm). "
                        "Vehicle speed may reduce. Drive carefully."
                    )


                elif congestion > 70:

                    recommendation = (
                        "🚨 Heavy traffic detected. "
                        "Avoid travelling now."
                    )


                elif next_peak["Traffic"] > current * 1.5:

                    recommendation = (
                        f"⚠️ Traffic will increase around "
                        f"{next_peak['Time']}. "
                        "Travel before this time."
                    )


                else:

                    recommendation = (
                        "✅ Good time to travel. "
                        "Traffic conditions are normal."
                    )
                st.success(
                    recommendation
                )



                # Best Travel Time

                st.subheader("⏳ Best Travel Time")


                best_hours = (
                    forecast_df
                    .sort_values("Traffic")
                    .head(3)
                    .sort_values("Hour")
                )


                best_time = ", ".join(
                    best_hours["Time"].tolist()
                )


                st.info(
                    f"Recommended travel hours: {best_time}"
                )



                # Traffic Level Bar

                st.progress(
                    min(congestion/100,1)
                )


                st.caption(
                    f"Traffic Load : {congestion}%"
                )

# ==========================
# SINGLE PREDICTION
# ==========================

if st.button("Predict Traffic"):

    sample = pd.DataFrame(

        [[
            temp,
            rain,
            snow,
            clouds,
            year,
            month,
            day,
            hour,
            weekday
        ]],

        columns=[

            "temp",
            "rain_1h",
            "snow_1h",
            "clouds_all",
            "year",
            "month",
            "day",
            "hour",
            "weekday"

        ]

    )

    prediction = model.predict(sample)[0]

    city_info = city_df[
        city_df["city"].str.lower()
        ==
        city.lower()
    ]


    factor = 1.0

    factor = get_city_factor(city)

    road_factor = get_road_factor(
        city,
        selected_road
    )

    traffic = int(
        prediction * factor * road_factor
    )

    st.success(
        f"🚗 Predicted Traffic : {traffic}"
    )

    # SAVE HISTORY
    file="data/prediction_history.csv"

    new=pd.DataFrame([{

    "date": now.strftime("%Y-%m-%d"),

    "time": now.strftime("%H:%M"),

    "city": city,

    "road": selected_road,

    "predicted_traffic": traffic

}])

    try:

        old=pd.read_csv(file)

        final=pd.concat(
            [old,new],
            ignore_index=True
        )

    except:

        final=new

    final.to_csv(
        file,
        index=False
    )

    st.info(
        "💾 Prediction Saved"
    )

# ==========================
# VERIFICATION
# ==========================

st.subheader(
    "📊 Prediction Verification"
)


actual = st.number_input(
    "Enter Actual Traffic",
    min_value=0
)

if st.button("Verify Prediction"):

    try:

        history=pd.read_csv(
            "data/prediction_history.csv"
        )

        last=history.iloc[-1]

        predicted=int(
            last["predicted_traffic"]
        )

        if actual>0:

            error=abs(
                predicted-actual
            )

            accuracy = (
            1 -
            abs(predicted-actual)
            /
            max(predicted, actual)
            ) * 100

            accuracy = max(
                0,
                min(100, accuracy)
            )

            st.metric(
                "Predicted",
                predicted
            )

            st.metric(
                "Actual",
                actual
            )

            st.success(
                f"🎯 Accuracy : {accuracy:.2f}%"
            )

        else:

            st.warning(
                "Enter actual traffic"
            )

    except:

        st.warning(
            "No prediction history found"
        )

st.markdown("""
<style>
.footer {
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    background-color: white;
    color: gray;
    text-align: center;
    padding: 10px;
    font-size: 14px;
    border-top: 1px solid #ddd;
    z-index: 999;
}
</style>

<div class="footer">
🚦 <b>Smart City Traffic Forecasting</b> |
AI + Machine Learning |
OpenWeatherMap |
OpenRouteService
</div>
""", unsafe_allow_html=True)