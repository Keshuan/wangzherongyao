import re
import json
import time
import asyncio
import aiohttp
import aiofiles
from feapder.utils.tools import unquote_url, format_seconds
import uvloop

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

async def download_img(session, url, filename):
    async with session.get(url) as response:
        content = await response.read()
        async with aiofiles.open(f"./images/{filename}", "wb") as f:
            await f.write(content)
            print(f"{filename}已下载完成")


async def fetch_url(session, urls, page):
    url = "https://apps.game.qq.com/cgi-bin/ams/module/ishow/V1.0/query/workList_inc.cgi"
    params = {
        "activityId": "2735",
        "sVerifyCode": "ABCD",
        "sDataType": "JSON",
        "iListNum": "20",
        "totalpage": "0",
        "page": page,
        "iOrder": "0",
        "iSortNumClose": "1",
        "jsoncallback": "jQuery1710287609418428602_1656939089867",
        "iAMSActivityId": "51991",
        "_everyRead": "true",
        "iTypeId": "2",
        "iFlowId": "267733",
        "iActId": "2735",
        "iModuleId": "2735",
        "_": "1656939141181"
    }
    async with session.get(url, params=params) as response:
        data = await response.text()
        data = json.loads(re.findall("\((.*?)\)", data)[0])
        keys = [f"sProdImgNo_{i}" for i in range(2, 9)]
        sizes = ["1024x768", "1280x720", "1280x1024", "1440x900", "1920x1080", "1920x1200", "1920x1440"]
        urls.extend([
            (unquote_url(i[key])[:-3] + "0", unquote_url(i["sProdName"]) + "_" + sizes[_] + ".jpg")
            for _, key in enumerate(keys)
            for i in data["List"]
        ])


async def main():
    start = time.time()
    async with aiohttp.ClientSession() as session:
        urls = []
        tasks = [asyncio.ensure_future(fetch_url(session, urls, page)) for page in range(31)]
        await asyncio.wait(tasks)
        tasks = [asyncio.ensure_future(download_img(session, *url)) for url in urls]
        await asyncio.wait(tasks)
    print(f"\n共计 {len(urls)} 张壁纸下载完成，耗时：%s" % format_seconds(time.time() - start))


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
