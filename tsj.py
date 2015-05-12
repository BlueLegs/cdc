#This script is a version of the Sheffiles Pi station code written to include owtwemp.py

import os 
import time

import plotly.plotly as py
import plotly.tools as tls
from plotly.graph_objs import *

#import urllib
#import urllib2

sensor = os.path.join("/","mnt","1wire","28.AF6A9E050000","temperature")

def tempfarenheit(temperature):
    Temp = (float(temperature)*9/5)+32
    return Temp

def Timeformatting(theTime):
    Timenow = time.strftime('%Y-%m-%d %H:%M:%S',theTime)
    Timeformat = Timenow.replace(':','%3A').replace(' ','+')
    return Timeformat,Timenow

#SiteID = "915926001"; AWSKey = "673025"; softwaretype = "my_software"
API_Key = "rxztgsfwjv"; Username = 'CDC'; Stream_ID = "mxds8jzy3z";

#Stream_ID_2 = "o454fbygeg"# This is for reading preasure - which I'm not doing 

py.sign_in(Username,API_Key)

def Plotter():
    trace1 = Scatter(
    x = [],
    y = [],
    name = 'Temperature Readings *C',
    stream = Stream(token = Stream_ID,
        maxpoints = 80)
    )

    my_data = Data([trace1])
    my_layout = Layout(
        title = 'Temperature Readings from cdcPiStation',
        xaxis = {'title':'Date and Time, GMT'},
        yaxis = YAxis(title='Temperature, *C',
                    range = [23,25]
        )
)
    my_fig = Figure(data = my_data,layout = my_layout)
    unique_url = py.plot(my_fig,filename='Weather Data', fileopt='extend')
    s = py.Stream(Stream_ID)
    return s

n = raw_input("No of readings (n for infinite): ")
if float(n)>1 or n == "n":
    frequency = input('Frequency (s): ')


s = Plotter()
s.open()

x=0

while True:
    #file_object=open(sensor,'r')  
    #line=file_object.read()
    #print(line+'C')
    #file_object.close()

    temperature = sensor
    [Timeformat,Timenow] = Timeformatting(time.gmtime())
    print temperature, Timenow
    
    Temp = tempfarenheit(temperature)

    f = open("datafile.txt",'a')
    f.write('%s %7s *C %14s' % (Timenow, temperature))
    f.close

    #url = 'http://wow.metoffice.gov.uk/automaticreading?siteid=%s&siteAuthenticationKey=%s&dateutc=%s&tempf=%s&softwaretype=%s' % (SiteID,AWSKey,Timeformat,Temp,softwaretype)

    request = urllib2.Request(url)
    response = urllib2.urlopen(request).getcode()
    if float(response) == 200:
        print "Data upload OK"
    else:
        print "Data upload error"


    s.write(dict(x=Timenow,y=temperature))

    if n != "n":
            X += 1
            if X >= float(n):
                s.close()
                break

    try:
        time.sleep(frequency)
    except:
        print "Process was terminated"
        s.close()
        break    






#temp = format(os.path.join("/","mnt","1wire","28.AF6A9E050000","temperature")())
