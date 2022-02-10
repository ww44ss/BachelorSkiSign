# BachelorSkiSign
Python Repository for Bachelor Ski Sign. This application reads data from an [api](https://bachelorapi.azurewebsites.net/) curretly running on Azure
It is written in Ciruit Python for the Adafruit M4 controller and display board. 
- [Adafruit Matrix Portal M4](https://www.adafruit.com/product/4745)   
- [64x32 RGB LED Matrix - 3mm pitch](https://www.adafruit.com/product/2279)

You also need to download the most recent version of the [CircuitPython uf2](https://learn.adafruit.com/welcome-to-circuitpython/installing-circuitpython).
To install it press the reset button on your board *twice* to enter the boot loader mode on the board computer. You'll recongize this because a boot loader directory will appear on the screen of your host computer. Just frag the new uf2 into the boot loader directory and you will be good to go!

## files   

*Code.py*     
Python code for the sign

Your board will also need:     
*Secrets.py*   
     
A file containing wifi passwords for your local network and your local latitude and longitude
It is of the format   
`secrets = {
    'ssid'      : 'Your_Local_Wifi_SSID',
    'password'  : 'Your_Password',
    'latitude'  : Your_Latitude,
    'longitude' : Your Longitude,
    'timezone'  : 'America/Los_Angeles'
}`


## Recent changes:
- 2021.Mar-07: originated
- 2021.Aug-13: updated with metric conversion, improved error handling for web requests
- 2021,Nov.05: weather uses NWS api results
- 2022 Jan 04: error handling. weather updates. large font
- 2022 Feb 08: updated for CircuitPython 7.1, updated RTC to use time from Azure. Added watchdog timer to reset upon stall

