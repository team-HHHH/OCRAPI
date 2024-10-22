import threading

import bs4
import requests
import random
from datetime import datetime
import MongoDriver

domainId = 2000505
THREAD_COUNT = 25
mongo = MongoDriver.MongoDB()
def getGonmoURL(id=domainId):
    domainUrl = f"https://mediahub.seoul.go.kr/gongmo/{id}"
    return domainUrl


def parse_date_range(date_range_str):
    start_str, end_str = date_range_str.split(" ~ ")
    start_date = datetime.strptime(start_str, "%Y.%m.%d. %H:%M")
    end_date = datetime.strptime(end_str, "%Y.%m.%d. %H:%M")
    return start_date, end_date
def generate_random_korea_coordinates():
    # 대한민국 위도 및 경도 범위
    latitude_min, latitude_max = 37.0, 37.7
    longitude_min, longitude_max = 126.7, 127.3

    # 무작위 위도 및 경도 생성
    latitude = random.uniform(latitude_min, latitude_max)
    longitude = random.uniform(longitude_min, longitude_max)

    exDict = dict()
    exDict["location"] = {
            "type": "Point",
            "coordinates": [longitude, latitude]
    }
    return exDict

def getCrawl(id=domainId):
    url = getGonmoURL(id)

    response = requests.get(url)
    soup = bs4.BeautifulSoup(response.text, "html.parser")

    find_poster = soup.find_all("img")
    mongoQuery = dict()

    for imgs in find_poster:
        src = imgs.get("src")
        if "uploads" in src:
            mongoQuery["images"] = f"https://mediahub.seoul.go.kr{src}"


    errCheck = soup.find("script")
    if "공모전을 찾을 수 없습니다." in errCheck.text:
        print(errCheck.text)
        return False, dict()

    trSec = soup.find_all("tr")

    titleObj = soup.find("meta", property="og:title")



    mongoQuery["uPos"] = generate_random_korea_coordinates()["location"]
    mongoQuery["pPos"] = generate_random_korea_coordinates()["location"]
    mongoQuery["url"] = url
    titleName = titleObj.get("content")
    mongoQuery["title"] = titleName



    for tr in trSec:
        for tds in str(tr).split("</td>"):
            tds += "</td>"

            blocks = bs4.BeautifulSoup(tds, "html.parser")

            title = blocks.find("span", "tit")

            if not title:
                continue

            title = title.text.strip()
            element = blocks.find("td").text.strip()

            if title == "응모대상":
                mongoQuery["participant"] = element

            elif title == "응모기간":
                start, end = parse_date_range(element)
                mongoQuery["startDay"] = start
                mongoQuery["endDay"] = end

            elif title == "응모분야":
                mongoQuery["content"] = element

            else:
                continue
        mongoQuery["id"] = id

    return True, mongoQuery




def threadDummyGo(start=2000000 , end=2000600):
    idList = [i for i in range(start, end+1)]
    chunk_size = len(idList) // THREAD_COUNT

    chunks = [idList[i:i + chunk_size] for i in range(0, len(idList), chunk_size)]

    def process_thread(idVec):
        for id in idVec:
            check, query = getCrawl(id)
            if check:
                mongo.insert_poster_query(query)
                print(query)


    threads = []
    for i in range(THREAD_COUNT):
        thread = threading.Thread(target=process_thread, args=(chunks[i], ))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    print("All Thread Finish")



if __name__ == "__main__":
    print("Crawl Start")
    mongo.___create_location_index___()

    threadDummyGo()



