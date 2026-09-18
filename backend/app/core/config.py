from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    excel_file_path: str = 'data/پایش کل درخواست ها MASTER.xlsx'
    excel_sheet_name: str = 'ریز اطلاعات'
    cors_origins: str = 'http://localhost:5173,http://127.0.0.1:5173'
    allowed_hosts: str = 'localhost,127.0.0.1'
    force_https: bool = False
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

settings = Settings()
