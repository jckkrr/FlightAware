def latestAirportLog(url):
    
    from requests import get
    from bs4 import BeautifulSoup
    import pandas as pd
    import re
    
    df = pd.DataFrame()

    # match_timelinedelta
    #from datetime import datetime
    #now = datetime.now().strftime("%Y%m%d%H%M%S")
    #date = datetime.now().strftime("%Y%m%d")
    #print(now)
    
    # scrape
    response = get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    main_table = soup.find_all('table', {'class': "prettyTable fullWidth"})[0]
    
    arrive_depart, airport_name_all = main_table.find('th', {'class': "mainHeader"}).text.split(':')
    
    if 'Sorry. No matching flights found' in str(main_table):
        print(f'{airport_name_all}: Sorry. No matching flights found')
        
    else:
        destination_ICAO = re.findall(r'\[([A-Z]+)\]', airport_name_all)[0]
        destination_airport = airport_name_all.split(' [')[0]
        
        trs = main_table.find_all('tr')

        for tr in trs:

            if 'smallrow' in str(tr):

                tds = tr.find_all('td')
                
                # flight name and code
                flight_code = tds[0].text        
                flight_title_short, flight_title_long = None, None

                try:
                    flight_title_all = tds[0].find('span')['title']
                    flight_title_all = flight_title_all.replace('&', 'and').replace(',', '')
                
                    if '"' in flight_title_all:                        
                        flight_title_short = re.findall(r'\"([A-Za-z0-9 \"\-]+)\"', str(flight_title_all))[0]
                        flight_title_long = flight_title_all.replace(f'"{flight_title_short}"','')
                    elif '(' in flight_title_all:
                        flight_title_short = flight_title_all.split('(')[0].replace('PTY.','').replace('LTD.','').replace('INC.','').replace('PTY','').replace('LTD','').replace('INC','').strip()
                    else:
                        flight_title_short = flight_title_all

                except:
                    flight_title_all = None


                # plane type     
                try:
                    plane_type = tds[1].find('span')['title']
                except:
                    plane_type = None


                # flight origin 

                origin_airport, origin_locale, origin_IATA, origin_ICAO, origin_latitude, origin_longitude = None, None, None, None, None, None

                if 'near' in tds[2].text.lower():
                    origin_locale = tds[2].text            
                    origin_latitude, origin_longitude = tds[2]('span')[0]['title'].replace('L','').strip().split(' ')                                

                else:
                    flight_origin = tds[2].text

                    try:            
                        origin_code = re.findall(r'\(([A-Z \/]+)\)', flight_origin)[0]               
                        origin_airport = flight_origin.replace(f'({origin_code})','').strip()

                        # split if there are two codes / determine code types
                        if '/' in origin_code:

                            origin_code = [x.strip() for x in origin_code.split('/')]

                            for oc in origin_code:
                                if len(oc) == 3:
                                    origin_IATA = oc
                                if len(oc) == 4:
                                    origin_ICAO = oc
                        else:
                            if len(origin_code) == 3:
                                origin_IATA, origin_ICAO = origin_code, None
                            if len(origin_code) == 4:
                                origin_IATA, origin_ICAO = None, origin_code

                    except: 
                        origin_code = flight_origin
                        print('!!!!!')
                        print(origin_code)


                    # get locale 
                    try:
                        origin_locale = tds[2]('span')[0]['title']
                        origin_locale = re.findall(r'\(([A-Za-z0-9 ,\"\-]+)\)', str(origin_locale))[0]
                    except:
                        pass

                    
                #times

                try:
                    departure_tz = tds[3].find('span', {'class': 'tz'}).text
                    departure_day, departure_time = tds[3].text.replace(departure_tz,'').strip().split(' ')
                except:
                    departure_tz, departure_day, departure_time = None, None, None
                
                if "result unknown" in str(tds[4]):
                    try:
                        arrival_tz = tds[4].find('span', {'class': 'tz'}).text
                        arrival_day = None
                        arrival_time = tds[4].text.replace(arrival_tz,'').replace('(?)','').strip()
    
                    except:
                        arrival_tz, arrival_day, arrival_time = None, None, None  
                else:
                    try:
                        arrival_tz = tds[4].find('span', {'class': 'tz'}).text
                        arrival_day, arrival_time = tds[4].text.replace(arrival_tz,'').strip().split(' ')
                    except:
                        arrival_tz, arrival_day, arrival_time = None, None, None
                        
                        
                
                # put it all into a DataFrame
                next_row = df.shape[0]
                df.loc[next_row,'Flight code'] = flight_code
                df.loc[next_row,'Flight title (full)'] = flight_title_all
                df.loc[next_row,'Flight title (long)'] = flight_title_long
                df.loc[next_row,'Flight title (short)'] = flight_title_short
                df.loc[next_row,'Plane type'] = tds[1].find('span')['title']
                df.loc[next_row,'Origin airport'] = origin_airport
                df.loc[next_row,'Origin locale'] = origin_locale
                df.loc[next_row,'Origin ICAO'] = origin_ICAO
                df.loc[next_row,'Origin IATA'] = origin_IATA
                df.loc[next_row,'Origin latitude'] = origin_latitude
                df.loc[next_row,'Origin longitude'] = origin_longitude
                df.loc[next_row,'Destination airport'] = destination_airport
                df.loc[next_row,'Destination ICAO'] = destination_ICAO
                df.loc[next_row,'Departure day'] = departure_day
                df.loc[next_row,'Departure time'] = departure_time
                df.loc[next_row,'Departure time zone'] = departure_tz
                df.loc[next_row,'Arrival day'] = arrival_day
                df.loc[next_row,'Arrival time'] = arrival_time
                df.loc[next_row,'Arrival time zone'] = arrival_tz
                
    #df.to_csv(f'{destination_ICAO}_{now}.csv', index=False)
    
    return df