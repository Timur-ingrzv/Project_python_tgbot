import aiohttp
from config import TOKEN_YANDEX


async def upload_to_yandex_disk(file_data, file_name, student_name) -> str:
    url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
    headers = {"Authorization": f"OAuth {TOKEN_YANDEX}"}
    params = {"path": f"/ДЗ/{student_name}/{file_name}", "overwrite": "true"}

    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(ssl=False)
    ) as session:
        async with session.get(
            url, headers=headers, params=params
        ) as response:
            if response.status == 200:
                json_response = await response.json()
                upload_link = json_response.get("href")
                async with session.put(
                    upload_link, headers=headers, data=file_data
                ) as upload_response:
                    if upload_response.status == 201:
                        return "Файл успешно отправлен"
                    else:
                        return f"Ошибка при загрузке файла: {upload_response.status}"
            else:
                return f"Ошибка при получении ссылки для загрузки: {response.status}"
