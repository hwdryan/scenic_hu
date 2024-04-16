from flask import Flask, render_template, request
import sqlite3
import subprocess

app = Flask(__name__)

# Function to fetch scenarios from the database
def get_scenarios():
    conn = sqlite3.connect('/home/weidong/Tools/Scenic/scenic_database/TC_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM TCEnhancedConcreteScenario")
    scenarios = cursor.fetchall()
    conn.close()
    return scenarios

# Route for the home page
@app.route('/')
def home():
    scenarios = get_scenarios()
    return render_template('index.html', scenarios=scenarios)

# Route to execute a scenario
@app.route('/run_scenario', methods=['POST'])
def run_scenario():
    scenario_id = request.form['scenario_id']
    conn = sqlite3.connect('/home/weidong/Tools/Scenic/scenic_database/TC_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT concrete_scenario FROM TCEnhancedConcreteScenario WHERE concrete_scenario_id=?", (scenario_id,))
    path = cursor.fetchone()[0]
    conn.close()
    subprocess.run(['python3', path])  # Execute the Python script
    return "Scenario executed successfully"

if __name__ == '__main__':
    app.run(debug=True)
