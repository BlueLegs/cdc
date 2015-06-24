#These are the imports needed to get the data from the sensor.
import time
import Adafruit_BMP.BMP085 as BMP085

# Added from owtemp:
import os

#These access the WOW site to upload data
import urllib
import urllib2

#Import the plot.ly data
import plotly.plotly as py
import plotly.tools as tls
from plotly.graph_objs import *

#Import the config data
import ConfigParser
import sys

#changed variable names here, doubled up on temperature calculation
def airtempfarenheit(AirTemperature,WaterTemperature):
    #WOW requires the temperature to be uploaded in Farenheit, so this will convert our values from Celcius
    AirTemp = (AirTemperature*1.8)+32
    WaterTemp = (float(WaterTemperature)*1.8)+32
    print "Hello %f" %AirTemp

    return AirTemp,WaterTemp

def presinches(pressure):
    #WOW requires the pressure to be uploaded in inches of mercury, so this will convert our values from Pascals
    Pres = float(pressure) * 0.000295333727
    return Pres

def Timeformatting(aTime):
    #returns the time in both normal format and WOW format
    Timenow = time.strftime('%Y-%m-%d %H:%M:%S',aTime)
    Timeformat = Timenow.replace(':','%3A').replace(' ','+')
    return Timeformat,Timenow
            
def addvalue():
    #This is in case the login values have not been added already
    value = raw_input('What is your %s?  ' %name)
    parser.set(section,name,value)


# The plotter code will need fixing to reflect that we don't have any pressure readings, 2x temperature readings, temperature readings have names changed
def Plotter():
    trace1 = Scatter(
    x=[],
    y=[],
    name = 'Air Temperature Readings *C',
    stream = Stream(token = Stream_ID,
        maxpoints=80)
    )
    trace2 = Scatter(
    x=[],
    y=[],
    name = 'Water Temperature Readings *C',
    yaxis = 'y2',
    stream = Stream(token = Stream_ID_2,
        maxpoints=80)
    )
    my_data = Data([trace1, trace2])
    my_layout = Layout(
        title='Weather Readings from CDC Pi Weather Station',
        xaxis={'title':'Date and Time, GMT'},
        yaxis=YAxis(title='Air Temperature, *C',
        ),
        yaxis2=YAxis(
            title = 'Water Temperature, *C',
            titlefont={'color':'rgb(148,103,189'},
            tickfont=Font(
                color='rgb(148,103,189)'
            ),
            side = 'right',
            overlaying = 'y'
        )
    )
    my_fig = Figure(data = my_data,layout = my_layout)
    unique_url = py.plot(my_fig,filename='Weather Data from the Pi Weather Station',auto_open=False,fileopt='extend')
    s = py.Stream(Stream_ID)
    q = py.Stream(Stream_ID_2)
    return s,q

#This checks that user details exist and prompts for them if not
parser = ConfigParser.SafeConfigParser(allow_no_value=True)
parser.read('details.ini')

for section in [ 'MetWOW', 'Plotly' ]:
    for name,value in parser.items(section):
        if value:
            continue
        else:
            addvalue()

#This writes the inputted values (if any) to the file
parser.write(open('details.ini','w'))

#This assigns the values to a format that the code can now access

AWSKey = parser.get('MetWOW','aws_key')
SiteID = parser.get('MetWOW','site_id')
APIKey = parser.get('Plotly','api_key')
Stream_ID = parser.get('Plotly','stream_id')
Username = parser.get('Plotly','username')
Stream_ID_2 = parser.get('Plotly','stream_id_2')

file_name=os.path.join("/","mnt","1wire","28.AF6A9E050000","temperature")


# - This is what caused all the problems! sensor=open(file_name,'r')

X = 0
softwaretype = "Sheffield-Pi-Weather-Station-0.2"

n = raw_input("Would you like to stop after a certain amount of readings? If so, type the amount. If not, type 'Forever': ")
    
if n == 'Forever' or float(n)>1:

    frequency = input('What time period between readings (in seconds) would you like: ')


#Use the functions to format the plot.ly graph and login to the site
py.sign_in(Username,APIKey)
s,q = Plotter()
s.open()
q.open()
#ADD IN NEW VAR HERE
print "Press ctrl-C at any time to cancel the process"

t = 0

sensor1 = BMP085.BMP085()


while True:
    print "%f" %t
    
	#open and read from the 1Wire virtual file 
    sensor=open(file_name,'r')
    airtemp = sensor.read()
    watertemp = sensor.read()

    print airtemp
    print watertemp	

    airtemp1 = float(airtemp)
 
	# commented out pressure reading
    pressure = format(sensor1.read_pressure())
    [Timeformat,Timenow] = Timeformatting(time.gmtime())

    #Get the data in the right units to upload
	
    [AirTemp,WaterTemp] = airtempfarenheit(airtemp1,watertemp)
    WaterTemp = watertempfarenheit(watertemp)
    Pres = presinches(pressure)
    
    #Construct the URL to send the data to WOW
	
    url = 'http://wow.metoffice.gov.uk/automaticreading?siteid=%s&siteAuthenticationKey=%s&dateutc=%s&tempf=%s&baromin=%.2f&softwaretype=%s' % (SiteID,AWSKey,Timeformat,AirTemp,Pres,softwaretype)
        
    #Send the request to WOW and interpret response
    request = urllib2.Request(url)
    response = urllib2.urlopen(request).getcode()
    if float(response) == 200:
		print "Connection is ok, data has been uploaded to Weather Observations Website %s" % SiteID
    else:
		print "Error connecting to WOW site. Data was not uploaded at this time."

    #Write the values to the Plot.ly data stream
	# Change this bit to reflect the different sensors
    s.write(dict(x=Timenow,y=airtemp))
    q.write(dict(x=Timenow,y=watertemp))
    v.write(dict(x=Timenow,y=pressure)) #Remeber to add this 

    #Write the values to a saved file and then close that file
	# This is the bit where the data.txt was reformatted - 2x temp, Temp, 0x pressure, Pres
    f = open("data.txt",'a')
    
    #f.write('%s %7s *C %14s *C\n %26s *F %13.2f *F\n' % (Timenow,airtemp,watertemp,AirTemp,WaterTemp))

    f.write('%s %7s *C %26s *F %13.2f inch Hg\n' % (Timenow,airtemp,AirTemp,Pres))
    f.close
    
    #Prepare the code to run indefinitely or until required number of readings is reached
    if n != "Forever":
		X += 1
		if X >= float(n):
			s.close()
			q.close()
			break

    t += 1
    #Wait for the required time period before repeating
    try:
		time.sleep(frequency)
    except:
		print "Process was terminated"
		s.close()
		q.close()
		break


