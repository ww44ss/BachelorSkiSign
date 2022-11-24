## 2021.Mar-07: originated
## 2021.Aug-13: metric conversion, improved error handling
## 2021,Nov.05: swith to NWS api
## 2022 Jan 04: error handling. large font
## 2022 Feb 08: CircuitPython 7.1, Added watchdog
## 2022 Nov 16: updated for 2023
##              - Reflect TZ uifo Pacific Time zone
##              - text computed on web


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

NETWORK = Network(status_neopixel=board.NEOPIXEL, debug=False)
NETWORK.connect()


def set_rtc():
    url = "https://bachelorapi.azurewebsites.net/time"
    print(url)
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

    y_m_d_h_m_s = [int(i) for i in y_m_d_h_m_s + ['45', 0, '-1','-1']]
    y_m_d_h_m_s = tuple(y_m_d_h_m_s)
    print("RTC = ", y_m_d_h_m_s)
    ## set RTC
    RTC().datetime = time.struct_time(y_m_d_h_m_s)
    print("url", url, "  cycle = ",cycle)
    return

def sensors():
    url="https://bachelorapi.azurewebsites.net/sensors2023"
    #print(url)
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

    while (retry == True or cycle >5):
        try:
            text = json.loads(NETWORK.fetch_data(url))
            retry = False
        except:
            cycle += 1
            text = {"season_total": "unavail", "snow_report":"*Pray for Snow*"}
            retry = True
            time.sleep(2)
    return text


## Set up WatchDogMode
w.timeout = 16 # seconds until watchdog timeout
w.mode = WatchDogMode.RESET  # reset system upon timeout
w.feed() #feed watchdog

while True:

    ## big loop checks weather, sun, report every ~2.8 hours

    set_rtc()

    big_time = time.time()

    mem_last = 0
   
    ## loop 1 initialize

    l1_x = "0"
    l2_x = "0"
    l3_x = "0"
    len_l1 = 1
    len_l2 = 1
    len_l3 = 1
    i = 1
    l1_x = -1000
   
    ## loop 2 initialize

    k = 1
    k_eff=1

    ## loop 3 initialize
    j = 1
    l3_x = -1000
    toggle_l1=3
    toggle_l3=3

    # make web calls pseudorandom
    rando1 = 1. + .05*(time.time()%11 - 5)  # in hours
    print("rando1 = ", rando1, " hours")
    gc.collect()
    mem_last_1 = gc.mem_free()
    print(mem_last_1)

    while time.time()-big_time < rando1*60*60:
        print("big loop - refreshing data")

        w.feed() #feed watchdog

        # Get data
        report_json = report()
        sensors_json = sensors()
        weather_text = weather()


        text_l1_0 = sensors_json["temp"]
        text_l1_1 = sensors_json["wind"]
        text_l1_2 = sensors_json["base"]

        text_l1_3 = report_json['snow_report']
        text_l1_4 = report_json['season_total']
        text_l1_5 = "* Louis  &  Leslie *" ## currently a dummy placeholder for report_json['powday']

        ## toggle control parameter
        n_l1 = 6  # this is a count of the number of lines above

        text_l3_0 = weather_text['weather1']
        text_l3_1 = weather_text['weather2']
        text_l3_2 = weather_text['weather3']

        ## toggle control parameter
        n_l3 = 3  # this is a count of the number of lines above

        flip_l2 = True

        i = 1

        len_l1 = max(len(text_l1_0), len(text_l1_1), len(text_l1_2), len(text_l1_3), len(text_l1_4), len(text_l1_5))

        k = 1
        k_eff=1
        start_time = time.time()
        last_scroll = 0

        len_l2 = 5

        #l_3
        j = 0
        len_l3 = max(len(text_l3_0), len(text_l3_1), len(text_l3_2))

        rando2 = .2*(int(1000*(time.time())%4919)-1000)/1E4 + .25  #in hours
        print("rando2 = ", rando2, " hours")

        mem_last_2 = gc.mem_free()

        time_struct = time.localtime()
        hour = '{0:0>2}'.format(time_struct.tm_hour)
        int_hour = int(hour)
        #print(int_hour)
        print("...rip!")

        color_x = 0x979797
        color_x_l1_blue = 0x9797B7
        color_x_l1_red = 0xB79797
        clock_color = 0x45B466
        color_l3 = 0x3B66BF

        ## Nightime dimming
        if int_hour > 21 or int_hour < 6:
            color_x = 0x100000
            color_x_l1_blue = 0x100010
            color_x_l1_red = 0x100000
            clock_color = 0x101000
            color_l3 = 0x100000

        #print("entering small loop")
        while time.time()-start_time < rando2*60*60:
            if (i == 1 or k == 1 or j == 1):
                print("starting small loop")

            w.feed()  # feed Watchdog

            #print("here")
            if l1_x < -4.5*(len_l1-2):
                i = 1
                toggle_l1 = (toggle_l1 + 1)%(n_l1)

            if toggle_l1 == 0:
                text_l1 = text_l1_0

            if toggle_l1 == 1:
                text_l1 = text_l1_1

            if toggle_l1 == 2:
                text_l1 = text_l1_2

            if toggle_l1 == 3:
                text_l1 = text_l1_3

            if toggle_l1 == 4:
                text_l1 = text_l1_4

            if toggle_l1 == 5:
                text_l1 = text_l1_5

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

            time_scroll_since = time.time() - last_scroll
            l2_x = (-k_eff*4.5)%(64+7*len_l2)-7*len_l2

            text_l2 = time_now
            color_2 = clock_color

            ## Glitch Time Display
            if (k+2*i+3*j)%312 == 0:
                line2.x = 9
                line2.y = 12
                color_2 = color_2 + 0x000020
               
            if (k+2*i+3*j)%312 == 6:
                line2.x = 10
                line2.y = 12
                color_2 = color_2 + 0x100020

            if (2*k+i+3*j)%363 == 6:
                line2.y = 15
                line2.x = 13
                color_2 = color_2 + 0x002000

            if (k+2*i+2*j)%312 == 6:
                line2.x = 11
                line2.y = 15
                color_2 = 0x001000

            if (k+2*i+2*j)%363 == 14:
                line2.x = 10
                line2.y = 14
                color_2 = 0x000010

            line2 = adafruit_display_text.label.Label(
                    LARGE_FONT,
                    color=color_2,
                    text=text_l2)
            line2.x = 10
            line2.y = 14


            ## TEXT 3

            if l3_x < -4*(len_l3-3):
                j = 1
                toggle_l3 = (toggle_l3 + 1)%(n_l3 + 1)  # adds a blank line

            if toggle_l3 == 0:
                text_l3 = text_l3_0

            if toggle_l3 == 1:
                text_l3 = text_l3_1

            if toggle_l3 == 2:
                text_l3 = text_l3_2

            if toggle_l3 == 3:
                text_l3 = "     "

            l3_x = (-j*2)%(64+5*len_l3)-5*len_l3

            color3 = color_l3

            # glitch
            if (k+i+3*j)%218 == 0:
                line3.x = int(l3_x+2)
                line3.y = 2
                color3 = color_l3 + 0X000030

            gc.collect()
            #print(mem_last_2, "  ", gc.mem_free(),text_l1, "  ", text_l2, "  ",text_l3 )
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
            gc.collect()
            time.sleep(.05)
            # scroll counters
            k += 1
            j += 1
            i += 1
            #print(mem_last_1,mem_last_2, gc.mem_free())
        else:
            print("short loop expired", time.now())
        gc.collect()