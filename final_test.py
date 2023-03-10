import asyncio
from datetime import date
import httpx
from bs4 import BeautifulSoup as BS
import requests
from urllib.parse import parse_qs, unquote, urlsplit
from decimal import Decimal
import traceback
import pandas as pd
import aiohttp
from itertools import islice
import sys
import ast

import io

 

# Reconfigure stdout to use utf-8 encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')



dic = ast.literal_eval(sys.argv[1])
max_retries=int(sys.argv[2])
max_sites=int(sys.argv[3])
csv_file =sys.argv[4]



def batched(iterable, n):
      "Batch data into lists of length n. The last batch may be shorter."
      # batched('ABCDEFG', 3) --> ABC DEF G
      if n < 1:
          raise ValueError('n must be >= 1')
      it = iter(iterable)
      while (batch := list(islice(it, n))):
          yield batch


def get_or_create_eventloop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return asyncio.get_event_loop()



def rd(m_s):
    
    rd_links = []
    big_all = []

    try:

        headers = {
            "User-Agent": "PostmanRuntime/7.30.0",
            "Host": "www.real.discount",
            "Connection": "Keep-Alive",
        }
        print('Requesting to --REAL_DISCOUNT--\n',flush=True)
        for i in range(max_retries):
            try:
                r = requests.get(
                    f"https://www.real.discount/api-web/all-courses/?store=Udemy&page=1&per_page={m_s}&orderby=date&free=1&editorschoices=0",
                    headers=headers,
                    timeout=5,
                ).json()

                break

            except :
                print('Connection Timeout --RETRYING--\n',flush=True)
 
                continue

        big_all.extend(r["results"])
        print('Scrapping initiated\n',flush=True)

        rd_length = len(big_all)
        
        for index, item in enumerate(big_all):
            rd_progress = index
            title = item["name"]
            link = item["url"]
            if link.startswith("https://click.linksynergy.com") or link.startswith("http://click.linksynergy.com"):
                try:
                    link = link.split("_PARM1=")[1]
                except:
                    continue
            print(f'Scrapped link for: {title}\n',flush=True)
            rd_links.append([title, link])

    except:
        rd_error = traceback.format_exc()
        rd_length = -1
        rd_done = True
        # print(rd_error,flush=True)



    print('Scrapping for REAL_DISCOUNT: --COMPLETED-- \n',flush=True)

    return rd_links


async def tutorial_bar(m_s):
    tb_links = []
    m_page=int(m_s//10)
    print('Requesting to --TUTORIAL_BAR--\n',flush=True)
    try:


        for page in range(1, m_page):
            
            big_all = []
            print(f'Requesting page: {page}',flush=True)

            for i in range(max_retries):
                try:
                    r = requests.get(
                        "https://www.tutorialbar.com/all-courses/page/" + str(page)+"/"
                    )
                    break
                except :
                    print('Connection Timeout --RETRYING--\n',flush=True)
                    continue

            soup = BS(r.content, "lxml")
            small_all = soup.find_all(
                "h3", class_="mb15 mt0 font110 mobfont100 fontnormal lineheight20"
            )
            big_all=small_all


            async with httpx.AsyncClient() as client:
                reqs = [[title.a.string, await client.get(url.a["href"])] for url,title in zip(big_all,big_all)]

                for response in reqs:
                    soup =  BS(response[1].content, "lxml")
                    link = soup.find("a", class_="btn_offer_block re_track_btn")[
                        "href"]
                    if "www.udemy.com" in link:
                        response[1]=link
                        tb_links.append(response)
                        print(f'Scrapped link for: {response[0]}\n',flush=True)
            print(f'page: {page} is --DONE--\n',flush=True)

    except:
        tb_error = traceback.format_exc()
        tb_length = -1
        tb_done = True
        print(tb_error)
    print('Scrapping for TUTORIAL_BAR: --COMPLETED-- \n',flush=True)
    return tb_links


def en_j(m_s):

    en_links = []
    try:
        print('Requesting to --JOBS.e-NEXT--\n',flush=True)
        for i in range(max_retries):
            try:
                r = requests.get(
                    "https://jobs.e-next.in/public/assets/data/udemy.json"
                ).json()
                break
            except :
                    print('Connection Timeout --RETRYING--\n',flush=True)
                    continue
            
        big_all = r
        en_length = len(big_all)
        print('Scrapping initiated\n',flush=True)
        for index, item in enumerate(big_all[:m_s]):
            en_progress = index
            title = item["title"]
            link = item["site"]
            print(f'Scrapped link for: {title}\n',flush=True)
            en_links.append([title, link])

    except:

        en_error = traceback.format_exc()
        en_length = -1
        en_done = True


    print('Scrapping for JOBS.e-NEXT: --COMPLETED-- \n',flush=True)
    return en_links


async def get_id_get_coupon(full_data):
    try:
        for batch in batched(full_data,2):
            links=[]
            for link in batch:
                links.append(link[1])
            async with aiohttp.ClientSession() as client:
                reqs =[[data,await client.get(url)] for data,url in zip(batch,links)]
                
                for response in reqs:
                    response[1]=await response[1].read()
                    soup = BS(response[1].decode('utf-8'), 'lxml')

                    try:
                        course_id = (
                            soup.find("meta", {"itemprop": "image"})["content"]
                            .split("/")[5]
                            .split("_")[0]
                        )
                    except :
                        course_id = ""

                    #extracting coupon id

                    query = urlsplit(response[0][1]).query
                    params = parse_qs(query)
                    try:
                        params = {k: v[0] for k, v in params.items()}
                        coupon_id = params["couponCode"]
                    except KeyError:
                        coupon_id = False
                    
                    response[0].extend([course_id,coupon_id])

                    print(f'Seprated Coupon and fetched Course Id for: {response[0][0]}\n',flush=True)
    except Exception as error:
        # print(error,flush=True)
        return None

    return full_data




async def check_course2(full_data):

        
        for batch in batched(full_data,10):
            checking_urls=[]
            for i in batch:

                url = (
                    "https://www.udemy.com/api-2.0/course-landing-components/"
                    + i[2]
                    + "/me/?components=purchase"
                )
                if i[3]:
                    url += f",redeem_coupon&couponCode={i[3]}"
                
                checking_urls.append(url)

            async with aiohttp.ClientSession() as client:

                reqs = [[data,await client.get(url)] for data,url in zip(batch,checking_urls)]
     
                for index,response in enumerate(reqs):
                    coupon_valid = False
                    expiry_date = None
                    print(f'Checking if COUPON is still valid for course id: {response[0][2]}',flush=True)
                    if response[0][3]:
                        
                        response[1]=await response[1].json()
                        if response[1]["redeem_coupon"]["discount_attempts"][0]["status"] == "applied":
                            coupon_valid = True
                            expiry_date = response[1]["purchase"]["data"]["pricing_result"]["campaign"]["end_time"].split(' ')[0]
                    
                    if not coupon_valid:

                        print(f'{response[0][0]}, --COUPON is expired--\n',flush=True)
                        response[0][3]=False
                        response[0][3]=False
                        response[0][2]=False
                        response[0][3]=False
                    else:

                        print(f'{response[0][0]}, --COUPON is still Available for redemption--\n',flush=True)
                        response[0][2] = expiry_date

        n=len(full_data)
        i=0
        
        while i<n:
            if full_data[i][2]==False:
                
                full_data.pop(i)
                n-=1
                continue
            i+=1
        return full_data


def tb(m_s):
    loop=get_or_create_eventloop()
    links = loop.run_until_complete(tutorial_bar(m_s))
    return links

def al():
    sites={1:rd,2:tb,3:en_j}
    links_title=[]
    count=0
    for i in range(1,4):
        
        if dic[i]:
            count+=max_sites
            links_title.extend(sites[i](max_sites))

    print('Seprating COUPON from link and fetching Course ID\n',flush=True)

    loop=get_or_create_eventloop()
    links_title = loop.run_until_complete(get_id_get_coupon(links_title))
    if links_title==None:
        print("Script --Crashed-- possible Issues Too many requests",flush=True)
        return 'Download Button Doesn\'t Work'

    print('Seprating --DONE--',flush=True)
    loop=get_or_create_eventloop()
    links_title = loop.run_until_complete(check_course2(links_title))


    print('Checking --DONE-- \n',flush=True)

    links_title = pd.DataFrame(links_title, columns=['Couse Name', 'Course URL','Expiry_Date','Coupon'])

    print('Exporting csv of all fetched Coupon Codes',flush=True)
    print('--DONE--\n',flush=True)
    print(f"Total Courses Checked: {count}\nTotal Courses collected: {len(links_title)}\n")
    links_title.to_csv(f"{csv_file}", encoding='utf-8')
    
    

    return links_title


print(al(),flush=True)
