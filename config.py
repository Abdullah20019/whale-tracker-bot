"""
Configuration file for Whale Tracker Bot
All settings, filters, and tier definitions
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = int(os.getenv('TELEGRAM_CHAT_ID')) if os.getenv('TELEGRAM_CHAT_ID') else None
TELEGRAM_GROUP_ID = int(os.getenv('TELEGRAM_GROUP_ID')) if os.getenv('TELEGRAM_GROUP_ID') else None
ADMIN_USER_ID = int(os.getenv('ADMIN_USER_ID')) if os.getenv('ADMIN_USER_ID') else None

# API Keys
HELIUS_API_KEY = os.getenv('HELIUS_API_KEY')
ALCHEMY_API_KEY = os.getenv('ALCHEMY_API_KEY')

# Token Quality Filters
DEFAULT_FILTERS = {
    'mc_min': 100_000,          # Min market cap: $100K
    'mc_max': 10_000_000,       # Max market cap: $10M
    'liq_min': 10_000,          # Min liquidity: $10K
    'vol_liq_max': 50,          # Max volume/liquidity ratio: 50x
    'min_holders': 50,          # Min holder count
    'min_age_hours': 1          # Min token age in hours
}

# Tier System Configuration
TIER_CONFIG = {
    1: {  # Elite - Top performers
        'name': 'Elite',
        'check_interval': 30,        # Check every 30 seconds
        'requirements': {
            'min_win_rate': 60,      # 60%+ win rate
            'min_avg_gain': 50,      # 50%+ average gain
            'min_calls': 10          # 10+ successful calls
        },
        'emoji': '🔥'
    },
    2: {  # Active - Good performers
        'name': 'Active',
        'check_interval': 180,       # Check every 3 minutes
        'requirements': {
            'min_win_rate': 50,      # 50%+ win rate
            'min_avg_gain': 30,      # 30%+ average gain
            'min_calls': 5           # 5+ successful calls
        },
        'emoji': '⭐'
    },
    3: {  # Semi-Active - Decent performers
        'name': 'Semi-Active',
        'check_interval': 600,       # Check every 10 minutes
        'requirements': {
            'min_win_rate': 40,      # 40%+ win rate
            'min_avg_gain': 10,      # 10%+ average gain
            'min_calls': 2           # 2+ successful calls
        },
        'emoji': '📊'
    },
    4: {  # Dormant - Inactive or poor performers
        'name': 'Dormant',
        'check_interval': 86400,     # Check every 24 hours
        'requirements': {
            'min_win_rate': 0,
            'min_avg_gain': 0,
            'min_calls': 0
        },
        'emoji': '💤'
    }
}

# Performance Tracking
PRICE_MILESTONES = [10, 25, 50, 100, 200, 500, 1000]  # Alert at these % gains

# Sell Detection
SELL_THRESHOLD = 0.3  # Alert when whale sells 30%+ of position

# Multi-Buy Detection
MULTI_BUY_THRESHOLD = 2  # Alert when 2+ whales buy same token

# Rate Limiting
API_RATE_LIMIT_DELAY = 0.5  # Seconds between API calls
