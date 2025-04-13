from flask import Flask, render_template, request, redirect, url_for, jsonify
import openai

app = Flask(__name__)

@app.route("/")
def home():
    return redirect(url_for("index"))

@app.route('/main', methods=['GET', 'POST'])
def main():
    return render_template("index.html")

# Descriptions for body types
BODY_TYPE_DESCRIPTIONS = {
    "Sedan": "A sedan is a classic car body type known for its comfort, fuel efficiency, and spacious trunk. It's ideal for daily commuting and long trips.",
    "Hatchback": "A hatchback offers a compact design with a versatile cargo area. It's great for city driving and small families.",
    "SUV": "An SUV provides a higher driving position, ample cargo space, and off-road capability. It's perfect for families and outdoor adventures.",
    "Truck": "A truck is designed for heavy-duty tasks like towing and hauling. It's ideal for work-related activities and off-roading.",
    "Coupe": "A coupe is a sporty, two-door car with a sleek design. It's best for individuals or couples who value style and performance.",
    "Wagon": "A wagon combines the comfort of a sedan with the cargo space of an SUV. It's great for families and long trips.",
    "Minivan": "A minivan offers maximum passenger and cargo space. It's perfect for large families and road trips.",
    "Crossover": "A crossover blends the features of an SUV and a sedan. It's versatile, fuel-efficient, and great for urban and suburban driving."
}

# Descriptions for fuel types
FUEL_TYPE_DESCRIPTIONS = {
    "Electric": "Electric cars are eco-friendly, quiet, and cost-effective to run. They're ideal for short to moderate trips and urban driving.",
    "Plug-In Hybrid": "Plug-in hybrids combine electric power with a gasoline engine. They offer flexibility for both short electric trips and long-distance travel.",
    "Hybrid": "Hybrids use both gasoline and electric power for improved fuel efficiency. They're great for city and highway driving.",
    "Diesel": "Diesel engines are fuel-efficient and powerful, making them ideal for long trips and towing.",
    "Gasoline": "Gasoline cars are widely available and offer a balance of performance and affordability. They're suitable for all types of driving."
}

# Image paths for body types
BODY_TYPE_IMAGES = {
    "Sedan": "static/images/sedan.jpg",
    "Hatchback": "static/images/hatchback.jpg",
    "SUV": "static/images/suv.jpg",
    "Truck": "static/images/truck.jpg",
    "Coupe": "static/images/coupe.jpg",
    "Wagon": "static/images/wagon.jpg",
    "Minivan": "static/images/minivan.jpg",
    "Crossover": "static/images/crossover.jpg"
}

# Image paths for fuel types
FUEL_TYPE_IMAGES = {
    "Electric": "static/images/electric.jpg",
    "Plug-In Hybrid": "static/images/plugin_hybrid.jpg",
    "Hybrid": "static/images/hybrid.jpg",
    "Diesel": "static/images/diesel.jpg",
    "Gasoline": "static/images/gasoline.jpg"
}

# Define question sets for different questionnaire lengths
SHORT_QUESTIONS = ["general", "price", "passenger", "efficiency", "towing", "trip_length", "cargo"]
MEDIUM_QUESTIONS = SHORT_QUESTIONS + ["reliability", "running_cost", "maneuverability", "ride_height", "stepin_height", "charging_stations", "at_home_charging"]
LONG_QUESTIONS = MEDIUM_QUESTIONS + ["long_trip_str", "maintenance", "noise", "usability", "battery", "availability", "bed"]


QUESTION_SETS = {
    "short": SHORT_QUESTIONS,
    "medium": MEDIUM_QUESTIONS,
    "long": LONG_QUESTIONS,
}

def CarPick(answers):
    # Initialize points for body types
    sedan_points = hatchback_points = suv_points = truck_points = coupe_points = wagon_points = minivan_points = crossover_points = 0

    # Initialize points for fuel types
    gasoline_points = diesel_points = electric_points = hybrid_points = plug_in_hybrid_points = 0

    # General Purpose
    general_str = answers.get("general")
    general = int(general_str) if general_str else 0
    if general == 1:
        sedan_points += 1
        hatchback_points += 1
        electric_points += 1
        hybrid_points += 1
        plug_in_hybrid_points += 1
    elif general == 2:
        suv_points += 1
        minivan_points += 1
        wagon_points += 1
        crossover_points += 1
    elif general == 3:
        diesel_points += 1
        hybrid_points += 1
        gasoline_points += 1
    elif general == 4:
        truck_points += 1
        suv_points += 1
        gasoline_points += 1
        diesel_points += 1
    elif general == 5:
        coupe_points += 1
        gasoline_points += 1
        sedan_points += 1
    elif general == 6:
        truck_points += 1
        suv_points += 1
        gasoline_points += 1
        diesel_points += 1
        crossover_points += 1

    # Passenger Space
    passenger_str = answers.get("passenger")
    passenger = int(passenger_str) if passenger_str else 0
    if passenger == 1:
        coupe_points += 1
        sedan_points += 1
        hatchback_points += 1
        truck_points += 1
    elif passenger == 2:
        suv_points += 1
        wagon_points += 1
        minivan_points += 1
        crossover_points += 1
    elif passenger == 3:
        minivan_points += 1
        suv_points += 1

    # Cargo Space
    cargo_str = answers.get("cargo")
    cargo = int(cargo_str) if cargo_str else 0
    if cargo == 1:
        coupe_points += 1
        sedan_points += 1
    elif cargo == 2:
        hatchback_points += 1
        sedan_points += 1
        crossover_points += 1
        wagon_points += 1
    elif cargo == 3:
        suv_points += 1
        wagon_points += 1
        crossover_points += 1
        truck_points += 1
        minivan_points += 1

    # Comfort Level During Long Travels
    travel_str = answers.get("travel")
    travel = int(travel_str) if travel_str else 0
    if travel == 1:
        hatchback_points += 1
        sedan_points += 1
        coupe_points += 1
        truck_points += 1
    elif travel == 2:
        crossover_points += 1
        wagon_points += 1
    elif travel == 3:
        minivan_points += 1
        suv_points += 1

    # Trip Length
    trip_length_str = answers.get("trip_length")
    trip_length = int(trip_length_str) if trip_length_str else 0
    if trip_length == 1:
        electric_points += 1
        plug_in_hybrid_points += 1
        hybrid_points += 1
    elif trip_length == 2:
        diesel_points += 1
        gasoline_points += 1
        hybrid_points += 1

    # Long-Distance Travel Values
    long_trip_str = answers.get("value")
    long_trip = int(long_trip_str) if long_trip_str else 0
    if long_trip == 1:
        diesel_points += 1
        hybrid_points += 1
        plug_in_hybrid_points += 1
        electric_points += 1
        sedan_points += 1
        hatchback_points += 1
    elif long_trip == 2:
        suv_points += 1
        minivan_points += 1
        crossover_points += 1
        wagon_points += 1
    elif long_trip == 3:
        sedan_points += 1
        hatchback_points += 1
        coupe_points += 1
    elif long_trip == 4:
        suv_points += 1
        truck_points += 1
        minivan_points += 1

    # Towing Needs
    towing_str = answers.get("towing")
    towing = int(towing_str) if towing_str else 0
    if towing == 1:
        truck_points += 1
        diesel_points += 1
        suv_points += 1
    elif towing == 2:
        suv_points += 1
        wagon_points += 1
        crossover_points += 1
    elif towing == 3:
        sedan_points += 1
        hatchback_points += 1
        coupe_points += 1

    # Fuel Efficiency
    efficiency_str = answers.get("efficiency")
    efficiency = int(efficiency_str) if efficiency_str else 0
    if efficiency == 1:
        electric_points += 1
        hybrid_points += 1
        plug_in_hybrid_points += 1
        sedan_points += 1
        hatchback_points += 1
    elif efficiency == 2:
        wagon_points += 1
        crossover_points += 1
        diesel_points += 1
    elif efficiency == 3:
        truck_points += 1
        gasoline_points += 1
        suv_points += 1
        minivan_points += 1
        coupe_points += 1

    # Parking and Maneuverability
    maneuverability_str = answers.get("maneuverability")
    maneuverability = int(maneuverability_str) if maneuverability_str else 0
    if maneuverability == 1:
        hatchback_points += 1
        sedan_points += 1
        coupe_points += 1
    elif maneuverability == 2:
        crossover_points += 1
        wagon_points += 1
    elif maneuverability == 3:
        truck_points += 1
        minivan_points += 1
        suv_points += 1

    # Routine Maintenance
    routine_str = answers.get("routine")
    routine = int(routine_str) if routine_str else 0
    if routine == 1:
        electric_points += 1
    elif routine == 2:
        hybrid_points += 1
        plug_in_hybrid_points += 1
    elif routine == 3:
        diesel_points += 1
        gasoline_points += 1

    # Usability When Stopped
    usability_str = answers.get("usability")
    usability = int(usability_str) if usability_str else 0
    if usability == 1:
        plug_in_hybrid_points += 1
        electric_points += 1
    elif usability == 2:
        hybrid_points += 1
        gasoline_points += 1
        diesel_points += 1

    # Mobile Battery
    battery_str = answers.get("battery")
    battery = int(battery_str) if battery_str else 0
    if battery == 1:
        electric_points += 1
    elif battery == 2:
        plug_in_hybrid_points += 1
        gasoline_points += 1
        diesel_points += 1
        hybrid_points += 1

    # Price
    price_str = answers.get("price")
    price = int(price_str) if price_str else 0
    if price == 1:
        sedan_points += 1
        hatchback_points += 1
        gasoline_points += 1
    elif price == 2:
        crossover_points += 1
        wagon_points += 1
        hybrid_points += 1
    elif price == 3:
        electric_points += 1
        plug_in_hybrid_points += 1
        suv_points += 1
        truck_points += 1
        minivan_points += 1
        coupe_points += 1

    # Reliability
    reliability_str = answers.get("reliability")
    reliability = int(reliability_str) if reliability_str else 0
    if reliability == 1:
        sedan_points += 1
        hatchback_points += 1
        electric_points += 1
        crossover_points += 1
        wagon_points += 1
    elif reliability == 2:
        coupe_points += 1
        plug_in_hybrid_points += 1
        hybrid_points += 1
        gasoline_points += 1
        truck_points += 1
        suv_points += 1
        minivan_points += 1
        diesel_points += 1

    # Running Costs
    running_cost_str = answers.get("running_cost")
    running_cost = int(running_cost_str) if running_cost_str else 0
    if running_cost == 1:
        electric_points += 1
    elif running_cost == 2:
        sedan_points += 1
        hatchback_points += 1
        crossover_points += 1
        wagon_points += 1
        plug_in_hybrid_points += 1
        hybrid_points += 1
    elif running_cost == 3:
        truck_points += 1
        suv_points += 1
        minivan_points += 1
        diesel_points += 1
        gasoline_points += 1

    # Availability and Options
    availability_str = answers.get("availability")
    availability = int(availability_str) if availability_str else 0
    if availability == 1:
        sedan_points += 1
        hatchback_points += 1
        crossover_points += 1
        suv_points += 1
        truck_points += 1
        gasoline_points += 1
    elif availability == 2:
        wagon_points += 1
        minivan_points += 1
        plug_in_hybrid_points += 1
        coupe_points += 1
        hybrid_points += 1
    elif availability == 3:
        electric_points += 1
        diesel_points += 1

    # Charging Station Availability
    charging_stations_str = answers.get("charging_stations")
    charging_stations = int(charging_stations_str) if charging_stations_str else 0
    if charging_stations == 1:
        electric_points += 1
        plug_in_hybrid_points += 1
    elif charging_stations == 2:
        gasoline_points += 1
        diesel_points += 1
        hybrid_points += 1

    # Ride Height
    ride_height_str = answers.get("ride_height")
    ride_height = int(ride_height_str) if ride_height_str else 0
    if ride_height == 1:
        sedan_points += 1
        hatchback_points += 1
        coupe_points += 1
        wagon_points += 1
    elif ride_height == 2:
        crossover_points += 1
        suv_points += 1
        truck_points += 1
        minivan_points += 1

        # Step-in Height
        stepin_height_str = answers.get("stepin_height")
        stepin_height = int(stepin_height_str) if stepin_height_str else 0
        if stepin_height == 1:
            minivan_points += 1
            sedan_points += 1
            hatchback_points += 1
            coupe_points += 1
            wagon_points += 1
        elif stepin_height == 2:
            crossover_points += 1
            suv_points += 1
            truck_points += 1

    # At-Home Charging
    at_home_charging_str = answers.get("at_home_charging")
    at_home_charging = int(at_home_charging_str) if at_home_charging_str else 0
    if at_home_charging == 1:
        electric_points += 1
        plug_in_hybrid_points += 1
    elif at_home_charging == 2:
        gasoline_points += 1
        diesel_points += 1
        hybrid_points += 1

    # Noise Levels
    noise_str = answers.get("noise")
    noise = int(noise_str) if noise_str else 0
    if noise == 1:
        electric_points += 1
        plug_in_hybrid_points += 1
    elif noise == 2:
        hybrid_points += 1
        gasoline_points += 1
    elif noise == 3:
        diesel_points += 1

    # Truck Bed
    bed_str = answers.get("bed")
    bed = int(bed_str) if bed_str else 0
    if bed == 1:
        truck_points += 1

    # Determine the recommended body type
    body_type_points = {
        "Sedan": sedan_points,
        "Hatchback": hatchback_points,
        "SUV": suv_points,
        "Truck": truck_points,
        "Coupe": coupe_points,
        "Wagon": wagon_points,
        "Minivan": minivan_points,
        "Crossover": crossover_points
    }

    # Determine the recommended fuel type
    fuel_type_points = {
        "Electric": electric_points,
        "Plug-In Hybrid": plug_in_hybrid_points,
        "Hybrid": hybrid_points,
        "Diesel": diesel_points,
        "Gasoline": gasoline_points
    }

    # Sort body types by points in descending order
    sorted_body_types = sorted(
        body_type_points.items(),
        key=lambda x: x[1],
        reverse=True
    )

    # Sort fuel types by points in descending order
    sorted_fuel_types = sorted(
        fuel_type_points.items(),
        key=lambda x: x[1],
        reverse=True
    )

    # Get the top two fuel types
    top_fuel_types = [k for k, v in sorted_fuel_types[:2]]

    # Get descriptions for the top body types and fuel types
    top_body_types = [item[0] for item in sorted_body_types[:2]]
    body_descriptions = {body: BODY_TYPE_DESCRIPTIONS[body] for body in top_body_types}
    fuel_descriptions = {fuel: FUEL_TYPE_DESCRIPTIONS[fuel] for fuel in top_fuel_types}

    return (
    top_body_types, 
    body_descriptions, 
    top_fuel_types, 
    fuel_descriptions,
    {body: BODY_TYPE_IMAGES[body] for body in top_body_types},
    {fuel: FUEL_TYPE_IMAGES[fuel] for fuel in top_fuel_types}
    )

@app.route("/", methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
@app.route("/<length>", methods=["GET", "POST"])
def index(length="short"):
    length = request.args.get("length", length)
    questions_to_ask = QUESTION_SETS.get(length, SHORT_QUESTIONS)

    short_question_count = len(SHORT_QUESTIONS)
    medium_question_count = len(MEDIUM_QUESTIONS)
    long_question_count = len(LONG_QUESTIONS)

    if request.method == "POST":
        answers = {q: request.form.get(q) for q in LONG_QUESTIONS}

        top_body_types, body_descriptions, top_fuel_types, fuel_descriptions, body_images, fuel_images = CarPick(answers)

        return render_template(
            "index.html",
            short_question_count=short_question_count,
            medium_question_count=medium_question_count,
            long_question_count=long_question_count,
            top_body_types=top_body_types,
            body_descriptions=BODY_TYPE_DESCRIPTIONS,
            top_fuel_types=top_fuel_types,
            fuel_descriptions=FUEL_TYPE_DESCRIPTIONS,
            body_images=body_images,
            fuel_images=fuel_images,
            show_result=True,
            question_length=length,
            questions=questions_to_ask
        )

    return render_template(
        "index.html",
        short_question_count=short_question_count,
        medium_question_count=medium_question_count,
        long_question_count=long_question_count,
        show_result=False,
        question_length=length,
        questions=questions_to_ask
    )

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")

    try:
        openai.api_key = "xxx"  

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}]
        )
        reply = response["choices"][0]["message"]["content"]
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"})

if __name__ == "__main__":
    app.run(debug=True)
