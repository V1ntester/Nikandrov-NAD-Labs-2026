# REST Small Modular Reactor Service Catalog

Веб-сервис c бизнес логикой системы для использования в SPA

## Эндпоинты

- GET — **/smrs**
- GET — **/smrs/draft**
- GET — **/smrs/{smr_id}**
- POST — **/smrs**
- PUT — **/smrs/draft/publish**
- DELETE — **/smrs/{smr_id}**
- POST — **/smrs/{smr_id}/like**
- POST — **/users/register**
- POST — **/users/login**
- POST — **/users/logout**

## Таблицы БД

- **smrs:**
id,
name,
manufacturer,
image_url,
video_url,
description,
thermal_power,
electrical_power,
status,
creator_id,
formed_at,
created_at
- **users:**
id,
username,
password_hash
- **likes:**
id,
user_id,
smr_id,
created_at
