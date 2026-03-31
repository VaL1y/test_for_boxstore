import time
import httpx

_cache = {"rate": None, "ts": 0}
TTL = 3600


async def get_usd_rate():
    now = time.time()

    if _cache["rate"] and now - _cache["ts"] < TTL:
        return _cache["rate"]

    async with httpx.AsyncClient() as client:
        r = await client.get("https://www.cbr-xml-daily.ru/daily_json.js")

    if r.status_code != 200:
        raise RuntimeError("Ошибка получения курса валют")

    data = r.json()
    rate = data["Valute"]["USD"]["Value"]

    _cache["rate"] = rate
    _cache["ts"] = now

    return rate