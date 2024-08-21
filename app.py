from flask import Flask, jsonify, request
import requests
import time
import threading

app = Flask(__name__)

# URL of the JSON data
DATA_URL = "https://static.pokebattler.com/raidAttackers.json"

# Global variable to store raid data and the last fetch time
raid_data = None
last_fetch_time = 0
fetch_interval = 3600  # Fetch data every hour (3600 seconds)

def fetch_raid_data():
    global raid_data, last_fetch_time
    try:
        response = requests.get(DATA_URL)
        if response.status_code == 200:
            raid_data = response.json()
            last_fetch_time = time.time()
            print("Raid data updated successfully.")
        else:
            print(f"Failed to fetch data: {response.status_code}")
    except Exception as e:
        print(f"Error fetching data: {str(e)}")

def periodic_data_refresh():
    while True:
        current_time = time.time()
        if current_time - last_fetch_time >= fetch_interval:
            fetch_raid_data()
        time.sleep(60)  # Check every minute if it's time to refresh

@app.route('/search', methods=['GET'])
def search_pokemon():
    global raid_data
    pokemon_id = request.args.get('pokemonId')
    
    if not pokemon_id:
        return jsonify({"error": "pokemonId parameter is required"}), 400
    
    if raid_data is None:
        return jsonify({"error": "Data not yet available"}), 503
    
    # Filter the data by pokemonId and find the best one by points
    filtered_data = [entry for entry in raid_data if entry['pokemonId'] == pokemon_id.upper()]
    
    if not filtered_data:
        return jsonify({"error": "Pokémon not found"}), 404
    
    # Get the entry with the highest points
    best_pokemon = max(filtered_data, key=lambda x: x['points'])
    
    return jsonify({
        "pokemonId": best_pokemon['pokemonId'],
        "points": best_pokemon['points'],
        "move1": best_pokemon['move1'],
        "move2": best_pokemon['move2']
    })

if __name__ == '__main__':
    # Start the periodic data refresh in a background thread
    threading.Thread(target=periodic_data_refresh, daemon=True).start()
    # Fetch data initially
    fetch_raid_data()
    app.run(host='0.0.0.0', port=5000)
