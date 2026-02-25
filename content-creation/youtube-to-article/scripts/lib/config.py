"""
Configuration management for YouTube to WeChat Article Assistant
"""

import os
from pathlib import Path
from dotenv import load_dotenv

class Config:
    """Configuration class that loads settings from environment variables"""
    
    def __init__(self):
        # Load environment variables from .env file if it exists
        env_path = Path(__file__).parent.parent / '.env'
        if env_path.exists():
            load_dotenv(env_path)
        
        # API Configuration
        self.deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')
        self.deepseek_base_url = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
        
        # WeChat Configuration
        self.wechat_app_id = os.getenv('WECHAT_APP_ID')
        self.wechat_app_secret = os.getenv('WECHAT_APP_SECRET')
        
        # Article Configuration
        self.article_author = os.getenv('ARTICLE_AUTHOR', 'Anonymous')
        
        # Directory Configuration
        base_dir = Path(__file__).parent.parent
        self.project_root = base_dir
        # Default to ~/context/00Inbox/ instead of ./downloads
        default_inbox = Path.home() / 'context' / '00Inbox'
        self.download_dir = Path(os.getenv('DOWNLOAD_DIR', default_inbox))
        self.output_dir = Path(os.getenv('OUTPUT_DIR', default_inbox))
        
        # Processing Configuration
        self.retry_attempts = int(os.getenv('RETRY_ATTEMPTS', '2'))
        self.timeout_seconds = int(os.getenv('TIMEOUT_SECONDS', '30'))

        # yt-dlp Safety Configuration
        self.yt_dlp_limit_rate = os.getenv('YT_DLP_LIMIT_RATE', '50K')
        self.yt_dlp_sleep_interval = int(os.getenv('YT_DLP_SLEEP_INTERVAL', '10'))
        self.yt_dlp_max_sleep_interval = int(os.getenv('YT_DLP_MAX_SLEEP_INTERVAL', '25'))
        self.yt_dlp_user_agent = os.getenv(
            'YT_DLP_USER_AGENT',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
        )
        self.yt_dlp_cookies_from_browser = os.getenv('YT_DLP_COOKIES_FROM_BROWSER', 'chrome')
        
        # Ensure directories exist
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def validate_required_config(self):
        """Validate that all required configuration is present"""
        missing_configs = []
        
        if not self.deepseek_api_key:
            missing_configs.append('DEEPSEEK_API_KEY')
        
        if not self.wechat_app_id:
            missing_configs.append('WECHAT_APP_ID')
            
        if not self.wechat_app_secret:
            missing_configs.append('WECHAT_APP_SECRET')
        
        if missing_configs:
            raise ValueError(
                f"Missing required configuration: {', '.join(missing_configs)}. "
                f"Please check your .env file or environment variables."
            )
    
    def __str__(self):
        """String representation for debugging (without sensitive info)"""
        return f"""Config(
    deepseek_api_key={'***' if self.deepseek_api_key else 'Not set'},
    wechat_app_id={'***' if self.wechat_app_id else 'Not set'},
    article_author='{self.article_author}',
    download_dir='{self.download_dir}',
    retry_attempts={self.retry_attempts}
)"""

# Global config instance
config = Config()