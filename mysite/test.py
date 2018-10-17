import urllib
import urllib2
url = 'http://umbra.nascom.nasa.gov/cgi-bin/eit-catalog.cgi'
values = {'obs_year':'2011','obs_month':'March',
                             'obs_day':'8','start_year':'2011'
                             ,'start_month':'March','start_day':'8'
                             ,'start_hour':'All Hours','stop_year':'2011'
                             ,'stop_month':'March','stop_day':'8'
                             ,'stop_hour':'All Hours','xsize':'All'
                             ,'ysize':'All','wave':'all'
                             ,'filter':'all','object':'all'
                             ,'xbin':'all','ybin':'all'
                             ,'highc':'all'}
data = urllib.urlencode(values)
print data
req = urllib2.Request(url, data)
response = urllib2.urlopen(req)
the_page = response.read()
print the_page