from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import requests
import json
import os

app = Flask(__name__)



app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
db = SQLAlchemy(app)

class Weather(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(100), nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"{self.city} - {self.temperature}°C, {self.description}"

def get_weather_data(city_name):
    api_key = os.environ.get("OPENWEATHER_API_KEY")
    if not api_key:
        raise ValueError("OpenWeather API key not set in environment variable OPENWEATHER_API_KEY")

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&units=metric&appid={api_key}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = json.loads(response.text)
        return data
    else:
        return None

@app.route('/add_weather', methods=['POST'])
def add_weather():
    city = request.form['city']
    data = get_weather_data(city)

    if data:
        temperature = data['main']['temp']
        description = data['weather'][0]['description']

        weather_entry = Weather(city=city, temperature=temperature, description=description)
        db.session.add(weather_entry)
        db.session.commit()

    return redirect(url_for('index'))

@app.route('/clear_history', methods=['POST'])
def clear_history():
    Weather.query.delete()
    db.session.commit()
    return redirect('/')

@app.route('/')
def index():
    with app.app_context():
        weather_data = Weather.query.all()
        return render_template('index.html', weather_data=weather_data)

if __name__ == '__main__':
    app.run(debug=True, port=5001)