import aiohttp
import config


async def get_youtube_videos(query: str, res_num: int):
    async with aiohttp.ClientSession() as session:
        youtube_url = f'https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=5&q={query}&type=video&key={config.YOUTUBE_API_KEY}'
        
        async with session.get(youtube_url) as response:
            yt_json = await response.json()

        if not yt_json:
            return None
        
        return yt_json


async def get_touhouwiki_query(query: str):
    async with aiohttp.ClientSession() as session:
        touhouwiki_url = f'https://en.touhouwiki.net/api.php?action=query&generator=search&prop=info&inprop=url&format=json&gsrsearch={query}'

        async with session.get(touhouwiki_url) as response:
            thw_json = await response.json()

        if not thw_json:
            return None
        
        return thw_json