#probando el .env
from app.config import get_settings

settings = get_settings()
print(settings.FIREBASE_CREDENTIALS)
print(settings.SECRET_KEY)
print(settings.ALGORITHM)
print(settings.ACCESS_TOKEN_EXPIRE_MINUTES)
print(settings.ALLWED_ORIGINS)