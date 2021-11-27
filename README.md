# BachelorSkiSign
Python Repository for Bachelor Ski Sign. This application reads data from https://bachelorapi.azurewebsites.net/ 
It is written in Ciruit Python for the Adafruit M4 controller and display board. 
- (Adafruit Metro M4 Express AirLift (WiFi) - Lite)[https://www.adafruit.com/product/4000]   
- (64x32 RGB LED Matrix - 3mm pitch)[https://www.adafruit.com/product/2279]   



# Code.py
Python code for the sign

Your board will also need the file:
# Secrets.py
A file containing wifi passwords for your local network and your local latitude and longitude
It is of the format

secrets = {
    'ssid'      : 'SSID',
    'password'  : 'Your Password',
    'latitude'  : 43.97942,
    'longitude' : -121.68873,
    'timezone'  : 'America/Los_Angeles'
}
