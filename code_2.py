## 2021.Mar-07: originated
## 2021.Aug-13: metric conversion, improved error handling
## 2021,Nov.05: swith to NWS api
## 2022 Jan 04: error handling. large font
## 2022 Feb 08: CircuitPython 7.1, Added watchdog
## 2022 Nov 16: updated for 2023
##              - Reflect TZ uifo Pacific Time zone
##              - text computed on web
## 2022 Nov 26: major rewrite


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

## Couple of macro flags:
dystopian_glitch = True  #glitches time display 
watchdog_flag = True     #watchdog timer for automatic reboot on fault
louis_and_leslie = False #Louis and Leslie" displays

##
## GRAB SECRETS AND ASSIGN VARIABLES
##
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

### Initialize Display

BITPLANES = 4
MATRIX = Matrix(bit_depth=BITPLANES)
DISPLAY = MATRIX.display

FONT = bitmap_font.load_font('/fonts/helvR10.bdf')
#LARGE_FONT = bitmap_font.load_font('/fonts/helvB12.bdf')
LARGE_FONT = bitmap_font.load_font('/fonts/helvB14.bdf') #need to update font library

DISPLAY.rotation = 0

### Connect to Network

NETWORK = Network(status_neopixel=board.NEOPIXEL, debug=False)
NETWORK.connect()

### Define functions

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
            time.sleep(1)

    time_date = fetched_data['pacific_time']
    print(time_date)
    y_m_d_h_m_s = time_date.split('T')[0].split('-')+ time_date.split('T')[1].split('-')[0].split(':')

    y_m_d_h_m_s = [int(i) for i in y_m_d_h_m_s + ['30', 0, '-1','-1']]
    y_m_d_h_m_s = tuple(y_m_d_h_m_s)
    print("RTC = ", y_m_d_h_m_s)
    ## set RTC
    RTC().datetime = time.struct_time(y_m_d_h_m_s)
    print("url", url, "  cycle = ",cycle)
    return

def sensors():
    url="https://bachelorapi.azurewebsites.net/sensors2023"

    retry = True
    cycle = 1

    while (retry == True and cycle <5):
        try:
            text = json.loads(NETWORK.fetch_data(url))
            retry = False
        except:
            print("Sensor error")
            text = {"base": "0 m base","temp":"Temperature 5 C","wind":"winds 24 to 34 kph"}
            retry = True
            cycle += 1
            time.sleep(2)

    return text

def weather():
    url="https://bachelorapi.azurewebsites.net/weather2023"
    #print(url)
    retry = True
    cycle = 1

    while (retry == True and cycle <5):
        try:
            text = json.loads(NETWORK.fetch_data(url))
            retry = False
        except:
            print('Report Error')
            cycle += 1
            retry = True
            time.sleep(2)
            text = {"cycle": cycle,"weather1":"unavail","weather2":"unavail","weather3":"Pray for *Snow*"}

    #print("/weather ", text)
    print("url", url, "  API_cycle = ",text['cycle'], "web_cycle = ", cycle)
    return text

def report():
    url="https://bachelorapi.azurewebsites.net/report2023"
    print("report: ",time.time())
    #print(url)
    retry = True
    cycle = 1

    while (retry == True and cycle <5):
        try:
            text = json.loads(NETWORK.fetch_data(url))
            retry = False
        except:
            cycle += 1
            text = {"season_total": "unavail", "snow_report":"*Pray for Snow*"}
            retry = True
            time.sleep(2)
    return text

def init_l1():
    report_json = report()
    sensors_json = sensors()


    text_l1_0 = sensors_json["temp"]
    text_l1_1 = sensors_json["wind"]
    text_l1_2 = sensors_json["base"]

    text_l1_3 = report_json['snow_report']
    text_l1_4 = report_json['season_total']
    text_l1_5 = " " ## currently a dummy placeholder for report_json['powday']
    if louis_and_leslie:
        text_l1_5 = "* Louis and Leslie *"
    return (text_l1_0, text_l1_1, text_l1_2, text_l1_3, text_l1_4, text_l1_5)


def init_l3():
    weather_text = weather()
    text_l3_0 = weather_text['weather1']
    text_l3_1 = weather_text['weather2']
    text_l3_2 = weather_text['weather3']

    return(text_l3_0,text_l3_1, text_l3_2)


## Set up WatchDogMode

if watchdog_flag:
    w.timeout =  10 # seconds until watchdog timeout
    w.mode = WatchDogMode.RESET  # reset system upon timeout
    w.feed() #feed watchdog


## initialize counters and timers

set_rtc()
big_time = int(time.time())
l1_time = big_time
l3_time = big_time



len_l1 = 1
len_l2 = 1
len_l3 = 1

l1_x = -1000
toggle_l1 = 0
l3_x = -1000
toggle_l3 = 0


i = 1
j = 1
k = 1

set_rtc()
first_pass = True

rand_timer = int(time.time())%3 - 1   # random int between -1 and + 1

## Set display colors
#color_x = 0x979797
#color_x_l1_blue = 0x9797B7
#color_x_l1_red = 0xB79797
#clock_color = 0x45B466
#color_l3 = 0x3B56BF



while True:

    if watchdog_flag:
        w.feed()  # feed watchdog

    #reset rtc every 12 +/- 1 hours
    if (int(time.time()) - big_time > 60*60*(12 + rand_timer) ) or first_pass :
        print("reset clock")
        j = 1
        big_time = time.time()               # restart timer
        rand_timer = int(time.time())%3 - 1  # random int between -1 and + 1

        set_rtc()

    # reset l_1 (sensors and report) every 20 minutes
    if (int(time.time()) - l1_time > 60*(20 + rand_timer)) or first_pass :
        print("reset sensors and report")
        i = 1
        l1_time = int(time.time())
        #text_l1_0, text_l1_1, text_l1_2, text_l1_3, text_l1_4, text_l1_5 = init_l1()
        l1 = init_l1()

        print(l1)
       
        n_l1 = len(l1)
        len_l1 = max(tuple(len(itup) for itup in l1))  # get max text length

    # reset l_3 (weather) every 90 minutes
    if (int(time.time()) - l3_time > 60*(60 + 5*rand_timer)) or first_pass:
        print("reset weather")
        k = 1
        l3_time = int(time.time())
        l3 = init_l3()
        
        print(l3)
        
        n_l3 = len(l3)
        len_l3 = max(tuple(len(itup) for itup in l3))  # get max text length

    first_pass = False

    len_l2 = 5

    k_eff=1

    time_struct = time.localtime()
    hour = '{0:0>2}'.format(time_struct.tm_hour)
    int_hour = int(hour)
    #print("ww44ss")

    ## Nightime dimming between 9pm and 6am
    if int_hour > 21 or int_hour < 6:
        color_x = 0x100000
        #color_x_l1_blue = 0x100010
        #color_x_l1_red = 0x100000
        clock_color = 0x101000
        color_l3 = 0x100000
    else:
        color_x = 0xA7A7A7
        #color_x_l1_blue = 0x9797B7
        #color_x_l1_red = 0xB79797
        clock_color = 0x40B070
        color_l3 = 0x3050C0

    #w.feed()  # feed Watchdog

    if l1_x < -4.5*(len_l1-2):
        i = 1
        toggle_l1 = (toggle_l1 + 1)%(n_l1)

    text_l1 = l1[toggle_l1]

    l1_x = (-i*3.2)%(64+5*len_l1)-5*len_l1

    line1 = adafruit_display_text.label.Label(
        FONT,
        color=color_x,
        text=text_l1
        )
    line1.x = int(l1_x)
    line1.y = 26

    ##TEXT 2
    time_struct = time.localtime()
    time_now = '{0:0>2}'.format(time_struct.tm_hour)+ ':' + '{0:0>2}'.format(time_struct.tm_min)

    text_l2 = time_now
    color_2 = clock_color

    line2_x = 10
    line2_y = 14
   
    if dystopian_glitch: 
    
        ## Glitch Time Display for dystopian effect
        ## the more of these lines the less smooth the display appears
        
        if (k+2*i+3*j)%312 == 0 or (k+2*i+3*j)%312 == 6:
            line2_x = 10-i%5+2
            line2_y = 13 - k%3
            color_2 = 0x002000

        if (i+j+k)%126 == 6:
            line2_x = 10 + i%2
            line2_y = 14
            color_2 = color_2 + 0x101010

        if (2*k+i+3*j)%363 == 6:
            line2_y = 15
            line2_x = 15
            color_2 = 0x202000

        #if (k+2*i+2*j)%312 == 6:
        #    line2_x = 11
        #    line2_y = 15
        #    color_2 = 0x003000

        #if (k+2*i+2*j)%363 == 14:
        #    line2_x = 10
        #    line2_y = 8
        #    color_2 = 0x001010
        
    line2 = adafruit_display_text.label.Label(
    LARGE_FONT,
    color=color_2,
    text=text_l2)
    line2.x= line2_x
    line2.y= line2_y

    ## TEXT 3

    if l3_x < -4*(len_l3):
        j = 1
        toggle_l3 = (toggle_l3 + 1)%n_l3

    text_l3 = l3[toggle_l3]

    l3_x = (-j*2)%(64+5*len_l3)-5*len_l3

    color3 = color_l3

    line3 = adafruit_display_text.label.Label(
        FONT,
        color = color3,
        text=text_l3)
    line3.x= int(l3_x)
    line3.y = 3

    g = displayio.Group()
    g.append(line1)
    g.append(line2)
    g.append(line3)


    DISPLAY.show(g)
            # clean up memory and pause
    time.sleep(.05)
            # scroll counters
    k += 1
    j += 1
    i += 1
    gc.collect()

    pass