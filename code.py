## 2021.Mar-07: originated
## 2021.Aug-13: updated with metric conversion, improved error handling for web requests
## 2021,Nov.05: weather uses NWS api results
## 2022 Jan 04: error handling. weather updates. large font


## IMPORT LIBRARIES
import json, board, time, gc
import busio
import displayio
from rtc import RTC
from adafruit_matrixportal.network import Network
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
    url = "http://worldclockapi.com/api/json/pst/now"
    #print(url_time)
    retry = True
    cycle = 1
   
    while (retry == True or cycle >5):
        try:
            fetched_data = json.loads(NETWORK.fetch_data(url))
            retry = False
        except:
            fetched_data = {"$id":"1","currentDateTime":"2021-08-31T12:43-07:00","utcOffset":"-07:00:00","isDayLightSavingsTime":true,"dayOfTheWeek":"Tuesday","timeZoneName":"Pacific Standard Time","currentFileTime":132748873890339258,"ordinalDate":"2021-243","serviceResponse":null}
            cycle += 1
            time.sleep(1.0*cycle)
            
    time_date = fetched_data['currentDateTime']
    y_m_d_h_m_s = time_date.split('T')[0].split('-')+ time_date.split('T')[1].split('-')[0].split(':')
    y_m_d_h_m_s = [int(i) for i in y_m_d_h_m_s + ['0', 0, '-1','-1']]
    y_m_d_h_m_s = tuple(y_m_d_h_m_s)
    #print("RTC = ", y_m_d_h_m_s)
    ## set RTC
    RTC().datetime = time.struct_time(y_m_d_h_m_s)
    print("url", url, "  cycle = ",cycle)
    return

def sensors():
    url="https://bachelorapi.azurewebsites.net/sensors2"
    #print(url)
    retry = True
    cycle = 1
   
    while (retry == True or cycle >5):
        try:
            fetched_data = json.loads(NETWORK.fetch_data(url))
            text = fetched_data
            retry = False
        except:
            text = {"cycle": cycle, "pine_gust":00,"pine_temp":00,"pine_wind":00,"snow_depth":00}
            cycle += 1
            time.sleep(.75)


    print("url", url, "  API_cycle = ",text["cycle"], " display_cycle = ", cycle)
    return text

def weather():
    url="https://bachelorapi.azurewebsites.net/weather2"
    #print(url)
    retry = True
    cycle = 1
   
    while (retry == True or cycle >5):
        try:
            fetched_data = json.loads(NETWORK.fetch_data(url))
            text = fetched_data
            retry = False
        except:
            print('Decoding JSON has failed')
            cycle += 1
            time.sleep(.75)
            text = {"cycle": cycle,"shortforecast_even_later":"Light Snow","shortforecast_later":"Light Snow","shortforecast_now":"Snow","when_even_later":"Saturday","when_later":"Tonight","when_now":"Today"}
    
    #print("/weather ", text)
    print("url", url, "  API_cycle = ",text['cycle'], "web_cycle = ", cycle)
    return text

def report():
    url="https://bachelorapi.azurewebsites.net/report2"
    print("report: ",time.time())
    #print(url)
    retry = True
    cycle = 1
   
    while (retry == True or cycle >5):
        try:
            fetched_data = json.loads(NETWORK.fetch_data(url))
            retry = False
            text = fetched_data
        except:
            cycle += 1
            text = {"cycle": cycle,"snow_24h":5.2,"snow_48h":5.2,"snow_overnight":5.2}
            time.sleep(.75)

    print("url", url, "  API_cycle = ",text['cycle'], "web_cycle = ", cycle)
    return text

def sun():
    ## pick appropriate url for location
    url="https://bachelorapi.azurewebsites.net/sunrise/bachelor"
    #url="https://bachelorapi.azurewebsites.net/sunrise/seattle"
    #url="https://bachelorapi.azurewebsites.net/sunrise/sisters"
    #url="https://bachelorapi.azurewebsites.net/sunrise/louis"
    #url="https://bachelorapi.azurewebsites.net/sunrise/hillsboro"
    #url="https://bachelorapi.azurewebsites.net/sunrise/portland"
    try:
        fetched_data = json.loads(NETWORK.fetch_data(url))
        text = fetched_data["sun"]
    except:
        text = {"name":"error","sun":"00:01  -  23:59"}
    return text

while True:
    ## big loop checks weather, sun, report every ~2.8 hours
    big_time = time.time()

    sun_text = sun()
    set_rtc()

    mem_last = 0

    l1_x = "0"
    l2_x = "0"
    l3_x = "0"
    len_l1 = 0
    len_l2 = 0
    len_l3 = 0
    i = 1
    l1_x = -1000

    k = 1
    k_eff=1

    ## loop 3 initialize
    j = 1
    l3_x = -1000
    toggle_l1=3
    toggle_l3=3

    # make web calls pseudorandom
    rando1 = .2*(int(1000*(time.time())%5879)-1000)/1E4 + .5

    print("rando1 = ", rando1, " hours")
    gc.collect()
    mem_last_1 = gc.mem_free()

    while time.time()-big_time < rando1*60*60:

        report_json = report()
        sensors_json = sensors()

        ## Metric
        text_l1_0 = "Temperature " + str(round(.556*(sensors_json["pine_temp"]-32)+.05, 1)) + "\u00B0C  "
        text_l1_1 = "winds " + str(int(round(1.6*sensors_json["pine_wind"], 0))) + " to " +str(int(round(1.6*sensors_json["pine_gust"], 0))) + " kph "
        text_l1_2 = str(round(0.0254*sensors_json["snow_depth"]+.05, 1)) + " meter base"
        text_l1_3 = str(round(2.54*report_json['snow_24h']+0.05,1)) + " cm in 24 hours"
        text_l1_4 = str(round(2.54*report_json['snow_48h']+0.05,1)) + " cm in 48 hours"
        text_l1_4_2 = str(round(2.54*report_json['snow_7d']+0.5,2 )) + " cm in 7 days"
        if report_json['snow_7d'] > 2.1 * report_json['snow_48h']:
            text_l1_4 = str(round(2.54*report_json['snow_7d']+0.5,2 )) + " cm in 7 days"
        text_l1_5 = str(round(0.0254*report_json['snow_season']+0.05,1)) + " meters (season) "
        if (sensors_json["pine_temp"] < 25 and report_json['snow_24h'] > 4):
            text_l1_5 = "* * POW  DAY * *"

        ## English
        #text_l1_0 = str(sensors_json["pine_temp"]) + "\u00B0F "
        #text_l1_1 = str(round(sensors_json["pine_wind"], 0)) + " to " +str(round(sensors_json["pine_gust"], 0)) + " mph "
        #text_l1_2 = str(sensors_json["snow_depth"]) + " \""
        #text_l1_3 = str(report_json['snow_overnight']) + " \" fresh "
        #text_l1_4 = str(report_json['snow_24h']) + " \" / 24hours "

        weather_text = weather()
        text_l3_0 = weather_text['when_now']+" : " + weather_text['shortforecast_now']
        #text_l3_1 = weather_text['shortforecast_now']
        text_l3_1 = weather_text['when_later']+" : " + weather_text['shortforecast_later']
        #text_l3_3 = weather_text['shortforecast_later']
        text_l3_2 = "& "+ weather_text['when_even_later']+" : " + weather_text['shortforecast_even_later']
        #text_l3_5 = weather_text['shortforecast_even_later']


        flip_l2 = True

        i = 1

        len_l1 = len(text_l1_0)

        k = 1
        k_eff=1
        start_time = time.time()
        last_scroll = 0

        len_l2 = 5

        #l_3
        j = 0
        len_l3 = len(text_l3_0)

        rando2 = .2*(int(1000*(time.time())%4919)-1000)/1E4 + .25  #in hours
        print("rando2 = ", rando2, " hours")

        mem_last_2 = gc.mem_free()

        time_struct = time.localtime()
        hour = '{0:0>2}'.format(time_struct.tm_hour)
        int_hour = int(hour)

        color_x_l1 = 0x979797
        color_x_l1_blue = 0x9797B7
        color_x_l1_red = 0xB79797
        clock_color = 0x45B466
        color_l3 = 0x3B66BF
        
        ## Nightime dimming
        if int_hour > 20 or int_hour < 7:
            color_x_l1 = 0x151510
            color_x_l1_blue = 0x0D0410
            color_x_l1_red = 0x180505
            clock_color = 0x121003
            color_l3 = 0x20202D
           

        while time.time()-start_time < rando2*60*60:
            if l1_x < -4.5*(len_l1-2):
                i = 1
                toggle_l1 = (toggle_l1 + 1)%5

            if toggle_l1 == 0:
                text_l1 = text_l1_0
                color_x = color_x_l1
                if sensors_json["pine_temp"]<16:
                    color_x = color_x_l1_blue
                if sensors_json["pine_temp"]>31:
                    color_x = color_x_l1_red

            if toggle_l1 == 1:
                text_l1 = text_l1_1
                color_x = color_x_l1
                if sensors_json["pine_gust"] > 40:
                    color_x = color_x_l1_red
              

            if toggle_l1 == 2:
                text_l1 = text_l1_2
                color_x = color_x_l1_red
                if sensors_json["snow_depth"]>48:
                    color_x = color_x_l1

            if toggle_l1 == 3:
                text_l1 = text_l1_3
                color_x = color_x_l1
                if report_json['snow_24h']>8:
                    color_x = color_x_l1_blue
                if report_json['snow_24h'] == 0:
                    text_l1 = text_l1_4
                    if report_json['snow_48h']>11 and sensors_json['pine_temp'] < 30:
                        color_x = color_x_l1_blue
                    if report_json['snow_48h'] == 0:
                        text_l1 = text_l1_4_2
                    
                
            #if toggle_l1 == 4:    # old code
            #    text_l1 = text_l1_4
            #    color_x = color_x_l1
            #    if report_json['snow_48h']>11:
            #        color_x = color_x_l1_blue

            if toggle_l1 == 4:
                text_l1 = text_l1_5
                color_x = color_x_l1
                if (sensors_json["pine_temp"] < 25 and report_json['snow_24h'] > 4):
                    color_x = color_x_l1_blue
            

            len_l1 = len(text_l1)

            l1_x = (-i*3)%(64+5*len_l1)-5*len_l1

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

            if l2_x < -4.5*len_l2:
                k = 1
                k_eff = 1
                flip_l2 = not(flip_l2)

            dl2_y = 0
            if (i+j+k)%91 == 0:
                dl2_y = (i+j+k)%3-1

            if flip_l2:
                text_l2 = time_now
                len_l2 = len(text_l2)
                l2_x = (-k_eff*4.5)%(64+7*len_l2)-7*len_l2
                if l2_x > 18:
                    k_eff = k
                else:
                    if k-k_eff < 600:
                        l2_x = 10
                    else:
                        k_eff = k - 600
                        l2_x = (-k_eff*4.5)%(64+7*len_l2)-7*len_l2

                color_2 = clock_color

                line2 = adafruit_display_text.label.Label(
                        LARGE_FONT,
                        color=color_2,
                        text=text_l2)
                line2.x = int(l2_x)
                line2.y = 14


            else:
                k_eff=k
                text_l2 = sun_text
                len_l2 = len(sun_text)
                l2_x = (-k_eff*4.3)%(64+5*len_l2)-5*len_l2
                line2 = adafruit_display_text.label.Label(
                    FONT,
                    color=clock_color,
                    text=text_l2)
                line2.x = int(l2_x)
                line2.y = 15

            ## TEXT 3

            if l3_x < -4*(len_l3-3):
                j = 1
                toggle_l3 = (toggle_l3 + 1)%3

            if toggle_l3 == 0:
                text_l3 = text_l3_0 

            if toggle_l3 == 1:
                #print(J, text_l3_1, l3_x, -4.7*len_l3)
                text_l3 = text_l3_1

            if toggle_l3 == 2:
                text_l3 = text_l3_2

            if toggle_l3 == 3:
                text_l3 = text_l3_3

            if toggle_l3 == 4:
                text_l3 = text_l3_4+ "  "

            if toggle_l3 == 5:
                text_l3 = text_l3_5+ "  "

            len_l3 = len(text_l3)

            l3_x = (-j*2)%(64+5*len_l3)-5*len_l3

            gc.collect()
            #print(mem_last_2, "  ", gc.mem_free(),text_l1, "  ", text_l2, "  ",text_l3 )

            line3 = adafruit_display_text.label.Label(
                FONT,
                color = color_l3,
                text=text_l3)
            line3.x= int(l3_x)
            #line3.y = 5
            line3.y = 3

            g = 0

            g = displayio.Group(max_size = 3)
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
        gc.collect()