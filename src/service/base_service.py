# For adding service common code
from src.config import ApiSettings, api_settings


class BaseService:
    def __init__(self, settings: ApiSettings = api_settings):

        self.settings = settings
