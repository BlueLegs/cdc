# cdc
Python code for the CDC Pi Weather Station Project

Sheffield Pi Station created a brillaint Pythond Script to publish sensor data from the BMP180 to the MET office and Plot.ly

I'm now trying to edit the code to work with the 1wire DS18B20 sensor - with no luck! 

Thermo_Station.py is the original code that works with the Bosch BMP180

owtemp.py reads the data from the DS18B20 sensor via the Pi's ROM. 

tsj.py is my version of the Thermo Station code. 

There's potentially an issue with the DS18B20 and the number of decimial places it uses, which isn't compatible with the conversion being used by the original script. 
