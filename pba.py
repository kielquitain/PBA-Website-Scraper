import requests 
import pandas as pd
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

def get_team_links(): 
    team_links = []
    res = requests.get('https://www.pba.ph/teams')
    soup = BeautifulSoup(res.text, 'html.parser')

    for div in soup.find_all('div', class_='col-lg-3 col-md-3 col-sm-6 col-xs-6 team-page-box'):
        for link in div.find_all('a'):
            team_links += [link['href']]

    team_links = team_links[:-1] # remove last item in the list
    return team_links

def get_team_details(link, to_download = True):
    print(f'Scraping team link: {link}')
    res = requests.get(link)
    soup = BeautifulSoup(res.text, 'html.parser')
    
    values = soup.find_all('h5')
    logo = soup.find_all('img')[4]['src']
    name =  soup.find('h3').text
    img_res = requests.get(logo) 

    if to_download:
        if img_res.status_code:
            fp = open(f'logos/{name}.png', 'wb')
            fp.write(img_res.content)
            fp.close()
        else:
            pass

    team_dict = [{ 
        'url' : link, 
        'image' : logo, 
        'name' : name, 
        'coach' : values[1].text, 
        'manager' : values[3].text, 
    }]

    return team_dict

def get_player_links(): 
    player_links = []
    res = requests.get('https://www.pba.ph/players')
    soup = BeautifulSoup(res.text, 'html.parser')

    for div in soup.find_all('div', class_='col-lg-9 col-md-9 col-sm-12 col-xs-12'):
        for link in div.find_all('a'):
            player_links += [link['href']]

    player_links = [ 'https://www.pba.ph/' + s for s in player_links]
    player_links = player_links[15:]
    return player_links

def get_player_details(link):
    print(f'Scraping player link: {link}')
    res = requests.get(link)
    soup = BeautifulSoup(res.text, 'html.parser')
    name = soup.find('h3').text
    team = soup.find('p', 'team-info color-tmc').text
    num_pos = soup.find('p', 'common-info').text
    img = soup.find('img', 'img-rounded')['src']
    num_pos = num_pos.replace('<br>', '/ ').split(' ')[:5]
    number = num_pos[0]
    position = num_pos[-1] if len(num_pos[-1]) <= 1 else num_pos[-1][:1]
    
    player_dict = [{
        'team': name, 
        'name' : team, 
        'number': number, 
        'position': position, 
        'url': link,
        'mugshot': img
    }]
    return player_dict

if __name__ == '__main__':
    team_links = get_team_links()
    player_links = get_player_links()

    all_team_details = []
    all_player_details = []
    
    # execute function calls asynchronously for faster scraping 
    with ThreadPoolExecutor(max_workers=15) as executor:
        team_futures = {
            executor.submit(get_team_details, team_link)
            for team_link in team_links
        }
        for f in team_futures:
            if f.result():
                all_team_details += f.result()
        
        player_futures = {
            executor.submit(get_player_details, player_link)
            for player_link in player_links
        }
        for f in player_futures:
            if f.result():
                all_player_details += f.result()

    team_df = pd.DataFrame(all_team_details)
    team_df.to_csv('out/teams.csv', index=False)
    player_df = pd.DataFrame(all_player_details)
    player_df.to_csv('out/players.csv', index=False)
    print('Done!')