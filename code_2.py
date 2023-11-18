### *SNOW* BOARD #########
## 2021 Mar-07: originated
## 2024 Nov 17: update 2024

## IMPORT LIBRARIES
import json, board, time, gc
import busio
import displayio
from rtc import RTC
from adafruit_matrixportal.network import Network
from microcontroller import watchdog as w
from watchdog import WatchDogMode
from adafruit_matrixportal.matrix import Matrix
from adafruit_bitmap_font import bitmap_font
import adafruit_display_text.label
import adafruit_requests
#import adafruit_lis3dh

####################################
## Initialize Variables and Screen
print("*Snow*Board")
print("*Skiing S*")
## Flag
dystopian_glitch0 = True
S_N = 6  # serial number

## GRAB SECRETS AND ASSIGN VARIABLES
try:
    from secrets import secrets
except ImportError:
    print('WiFi secrets are kept in secrets.py, please add them there!')

try:
    LATITUDE = secrets['latitude']
    LONGITUDE = secrets['longitude']
    TIMEZONE = secrets['timezone']
    print('Using CACHED geolocation: ', LATITUDE, LONGITUDE)
except:
    LATITUDE = 44.300
    LONGITUDE = -121.608
    TIMEZONE = 'America/Los_Angeles'
    print('Using DEFAULT geolocation: ', LATITUDE, LONGITUDE)

BITPLANES = 4
MATRIX = Matrix(bit_depth=BITPLANES)
DISPLAY = MATRIX.display


## Logo Splash
def splash():

    g = displayio.Group()
    # alternate images
    FILENAME = 'image/MtBLogo.bmp'
    BITMAP = displayio.OnDiskBitmap(FILENAME)
    logo = displayio.TileGrid(BITMAP, pixel_shader=BITMAP.pixel_shader)
    DISPLAY.rotation = 0
    g.append(logo)
    DISPLAY.show(g)
    return()

#startup Impage
splash()

## Load fonts
FONT = bitmap_font.load_font('/fonts/helvR10.bdf')
LARGE_FONT = bitmap_font.load_font('/fonts/helvB14.bdf') #need to update font library

### Connect to Network
NETWORK = Network(status_neopixel=board.NEOPIXEL, debug=False)
NETWORK.connect()

############################
### DEFINE FUNCTIONS   #####

## clock set
def set_rtc():
    url = "https://bachelorapi.azurewebsites.net/time"
    retry = True
    cycle = 1

    while (retry == True and cycle < 5):
        try:
            fetched_data = json.loads(NETWORK.fetch_data(url))
            retry = False
        except:
            fetched_data = '{"time":"2022-02-10T17:00"}'  # Dummy Data
            cycle += 1
            print("t_retry", cycle)
            time.sleep(.5)
    print("time cycle = ", cycle)
    time_date = fetched_data['pacific_time']
    y_m_d_h_m_s = time_date.split('T')[0].split('-')+ time_date.split('T')[1].split('-')[0].split(':')
    y_m_d_h_m_s = [int(i) for i in y_m_d_h_m_s + ['35', 0, '-1','-1']]
    y_m_d_h_m_s = tuple(y_m_d_h_m_s)
    ## set RTC
    RTC().datetime = time.struct_time(y_m_d_h_m_s)
    return

## Get sign data
def get_data2024():
    url="https://bachelorapi.azurewebsites.net/data2024"

    retry = True
    cycle = 1

    while (retry == True and cycle <5):
        try:
            w.feed()
            text = json.loads(NETWORK.fetch_data(url))
            retry = False
        except:
            text = {"comment": "", "snow_base": " 3.5 m Base",
            "snow_fall": "36 cm Fresh *Snow* Overnight",
            "snow_season": " 21-22 Season Total 10.5 m",
            "temp": "Pine Temp -8\u00b0C",
            "weather1": "28 to 43 cm *Snow* Today",
            "weather2": "*Snow* Showers Tonight",
            "weather3": "& *Snow* Showers Sunday",
            "wind": "PMX Wind 45 to 76 kph"}
            retry = True
            cycle += 1
            w.feed()
            time.sleep(2)
        w.feed()
    return text

#########################################
####### INITIALIZE RUNTIME ################
first_pass = True

## Set up WatchDogMode
w.timeout =  13 # seconds until watchdog timeout
w.mode = WatchDogMode.RESET  # reset system upon timeout
w.feed() #feed watchdog

## initialize varibles and timers
time_struct = time.localtime()
hour = '{0:0>2}'.format(time_struct.tm_hour)
int_hour = int(hour)
mins = '{0:0>2}'.format(time_struct.tm_min)
int_mins = int(mins)
int_mins_old = int_mins
int_erval = 15
int_renew = (int(int_mins/15)*15+S_N)%60
int_mins_old = int_mins

# display variables
len_l1 = 1
len_l2 = 1
len_l3 = 1

l1_x = -1000
toggle_l1 = 5
l3_x = -1000
toggle_l3 = 3

i = 1
j = 1
k = 1
# clean up
gc.collect()

#start
first_pass = True


while True:

    w.feed()  # feed watchdog
    if int_mins == int_renew or first_pass:  # check on renewal
        splash()
        int_renew = (int_renew + int_erval)%60
        print("int_mins= ",int_mins,"  int_renew= ", int_renew, "  int_erval= ",int_erval)
        j = 1
        w.feed()
        set_rtc()
        w.feed()
        data = get_data2024()
        w.feed()
        first_pass = False

        ## form text lines from data
        l1 = [data['snow_fall'], data['snow_base'], data['snow_season'], data['temp'], data['wind'], data['comment']]
        l3 = [data['weather1'], data['weather2'], data['weather3']]

    time_struct = time.localtime()
    hour = '{0:0>2}'.format(time_struct.tm_hour)
    int_hour = int(hour)
    mins = '{0:0>2}'.format(time_struct.tm_min)
    int_mins = int(mins)
    ## Color Control
    ## Nightime dimming between 10pm and 6am
    if int_hour > 21 or int_hour < 6:
        color_x = 0x100000
        clock_color = 0x100000
        color_3 = 0x100000
        dystopian_glitch=False
    else:
        color_x = 0xB7A7A7
        clock_color = 0x80C260
        color_3 = 0x3040D0
        dystopian_glitch = dystopian_glitch0

    ## LINE 1 (REPORT)
    if l1_x < -5*(len_l1)+5:
        i = 1
        toggle_l1 = (toggle_l1 + 1)%len(l1)

        text_l1 = l1[toggle_l1]
        len_l1 = len(text_l1)
        #print(text_l1)

    l1_x = int((-i*3)%(64+5*len_l1)-5*len_l1)

    line1 = adafruit_display_text.label.Label(
        FONT,
        color=color_x,
        text=text_l1)
    line1.x = int(l1_x) #+5*start_text
    line1.y = 25

    ## LINE 2 (CLOCK)
    time_struct = time.localtime()
    time_now = '{0:0>2}'.format(time_struct.tm_hour)+ ':' + '{0:0>2}'.format(time_struct.tm_min)

    text_l2 = time_now
    color_2 = clock_color

    line2_x = 10
    line2_y = 14

    if dystopian_glitch:

        ## Glitch Time Display for dystopian effect
        if (k+2*i+3*j)%312 == 0 or (k+2*i+3*j)%312 == 12 or (k+2*i+3*j)%312 == 48:
            line2_x = 10-i%5+2
            line2_y = 13 - k%3
            color_2 = 0x002000

        if int_mins != int_mins_old:
            int_mins_old = int_mins
            line2_x = 10-i%5+2
            line2_y = 13 - k%3
            color_2 = 0x101000

    line2 = adafruit_display_text.label.Label(
    LARGE_FONT,
    color=color_2,
    text=text_l2)
    line2.x= line2_x
    line2.y= line2_y

    ## LINE 3 (Weather Report)
    if l3_x < -5*len_l3+5 or first_pass:
        j = 1
        toggle_l3 = (toggle_l3 + 1)%len(l3)
        text_l3 = l3[toggle_l3]
        len_l3 = len(text_l3)

    l3_x = int((-j*2)%(64+5*len_l3)-5*len_l3)

    line3 = adafruit_display_text.label.Label(
        FONT,
        color=color_3,
        text=text_l3#[start_text:end_text]
        )
    line3.x = int(l3_x)#+5*start_text
    line3.y = 3
    #splash()
    g = displayio.Group()


    #g.append(logo)
    g.append(line2)
    g.append(line1)
    g.append(line3)

    DISPLAY.show(g)

    # pause
    time.sleep(.02)
    #first_pass = False

    # scroll counters
    k += 1
    j += 1
    i += 1

    # clean up memory
    #print("mem_free = ", gc.mem_free())
    gc.collect()

    pass

