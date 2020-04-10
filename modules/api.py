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