from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import requests
import time
import re
import pickle
from datetime import datetime, date
import pandas as pd

driver = webdriver.Chrome()
time.sleep(3)
window = driver.window_handles[0]
base_url = 'https://www.unglobalcompact.org/what-is-gc/participants/search?page={}&search%5Bkeywords%5D=&search%5Borganization_types%5D%5B%5D=5&search%5Bper_page%5D=50&search%5Bsort_direction%5D=asc&search%5Bsort_field%5D=&utf8=✓'
driver.get()

SDG = {'sdg1' : 'No Poverty',
       'sdg2' : 'Zero Hunger',
       'sdg3' : 'Good Health & Well Being',
       'sdg4' : 'Quality Education',
       'sdg5' : 'Gender Equality',
       'sdg6' : 'Clean Water & Sanitation',
       'sdg7' : 'Affordable & Clean Energy',
       'sdg8' : 'Decent Work & Economic Growth',
       'sdg9' : 'Industry Innovation Infrastructure',
       'sdg10' : 'Reduced Inequalities',
       'sdg11' : 'Sustainable Cities & Communities',
       'sdg12' : 'Responsible Consumption & Production',
       'sdg13' : 'Climate Action',
       'sdg14' : 'Life Below Water',
       'sdg15' : 'Life On Land',
       'sdg16' : 'Peace & Justice Strong Institutions',
       'sdg17' : 'Partnerships for the Goals'}

def get_search_pages(browser, url):
    all_links = []
    for i in range(1, 93):
        browser.get(url.format(i))
        time.sleep(3)
        hrefs = BeautifulSoup(browser.page_source, 'lxml').find_all('a')
        all_links += get_gcs(hrefs)
    return all_links

def open_window_and_load_site(site):
    """Opens a selenium webdriver object, opens a page and returns the webdriver
    object."""
    driver_obj = webdriver.Chrome()
    driver_obj.get(site)
    return driver_obj

def get_gcs(links):
    gc = re.compile(r'what-is-gc/participants/\d+')
    list_of_links = []
    for link in links:
        if gc.search(link['href']):
            list_of_links.append(link['href'])
    return list_of_links

def get_details(link, browser):
    details = {}
    browser.get(link)
    time.sleep(1)
    page = BeautifulSoup(browser.page_source, 'lxml')
    # Find Name
    title_part = page.find('span', {'class' : 'title'})
    title_sig = page.find('header', {'class' : 'main-content-header'})
    if title_part:
        details['Name'] = title_part.text
    else:
        details['Name'] = title_sig.h1.text
    # Get Org info
    elems = page.find('section', {'class' : 'column two-12s org-info'})
    overview = page.find('div', {'class' : 'column company-information-overview'})
    if overview:
        for view in zip(overview.find_all('dt'), overview.find_all('dd')):
            details[view[0].text.replace(':', '')] = view[1].text
        details['Type'] = details['Org. Type']
        details.pop('Org. Type', None)
        details['Participant Since'] = ''
    if elems:
        for entry in zip(elems.find_all('dt'), elems.find_all('dd')):
            details[entry[0].text.replace(':', '')] = entry[1].text
    prins = page.find('div', {'class' : 'principles'})
    if prins:
        for a in prins.find_all('a'):
            if len(a['class']) > 1:
                details[a['class'][0]] = a['class'][1]
            else:
                details[a['class'][0]] = 'inactive'
    else:
        details['human-rights'] = 'inactive'
        details['labour'] = 'inactive'
        details['environment'] = 'inactive'
        details['anti-corruption'] = 'inactive'
    sdg = page.find('div', {'class' : 'sdg-icons'})
    if sdg:
        for a in sdg.find_all('a'):
            # print(a['class'])
            if len(a['class']) > 1:
                details[SDG[a['class'][0]]] = a['class'][1]
            else:
                details[SDG[a['class'][0]]] = 'inactive'
    else:
        for key, val in SDG.items():
            details[val] = 'inactive'
    return(details)
# info = get_details('https://www.unglobalcompact.org/what-is-gc/participants/3449-Eskom', driver)
# info
info = get_details('https://www.unglobalcompact.org/what-is-gc/participants/137410-Beihai-Heating-Group-Co-Ltd-', driver)
info

participants = get_search_pages(driver, base_url)
df = pd.DataFrame(participants, columns=['links'])
df.shape
!pwd
df.to_csv('global_participant_links.csv', index=False)

df.head()

pd.DataFrame(pd.Series(get_details('https://www.unglobalcompact.org/what-is-gc/participants/137410-Beihai-Heating-Group-Co-Ltd-', driver))).transpose()

un = pd.DataFrame()
for idx, row in df.loc[0:10].iterrows():
    print(idx, row['links'])
    if idx == 0:
        un = pd.DataFrame(pd.Series(get_details('https://www.unglobalcompact.org' + row['links'], driver))).transpose()
    else:
        un = pd.concat((un, pd.DataFrame(pd.Series(get_details('https://www.unglobalcompact.org' + row['links'], driver))).transpose()), sort=True)
un = un[['Name', 'Type', 'Country', 'Employees', 'Sector', 'Ownership', 'Engagement Tier',
  'Global Compact Status', 'Participant Since', 'human-rights', 'labour', 'environment',
  'anti-corruption', 'No Poverty', 'Zero Hunger', 'Good Health & Well Being',
  'Quality Education', 'Gender Equality', 'Clean Water & Sanitation', 'Affordable & Clean Energy',
  'Decent Work & Economic Growth', 'Industry Innovation Infrastructure', 'Reduced Inequalities',
  'Sustainable Cities & Communities', 'Responsible Consumption & Production', 'Climate Action',
  'Life Below Water', 'Life On Land', 'Peace & Justice Strong Institutions', 'Partnerships for the Goals']]
un.head()
