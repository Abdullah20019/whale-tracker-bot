"""
Configuration file for Whale Tracker Bot
All settings, filters, and constants
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# API KEYS
# ============================================================

HELIUS_API_KEY = os.getenv('HELIUS_API_KEY')
ALCHEMY_API_KEY = os.getenv('ALCHEMY_API_KEY')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# ============================================================
# ADMIN SETTINGS
# ============================================================

ADMIN_USER_ID = 1930784205

# ============================================================
# CHAT IDS
# ============================================================

PRIVATE_CHAT_ID = "1930784205"
GROUP_CHAT_ID = "-1003704810993"

# ============================================================
# MONITORING SETTINGS
# ============================================================

CHECK_INTERVAL = 180  # seconds (3 minutes)
SELL_CHECK_INTERVAL = 120  # seconds (2 minutes)
PERFORMANCE_CHECK_INTERVAL = 60  # seconds (1 minute)

# ============================================================
# FILTER DEFAULTS
# ============================================================

DEFAULT_FILTERS = {
    'mc_min': 100000,
    'mc_max': 10000000,
    'liq_min': 10000,
    'vol_liq_max': 50,
    'buy_sell_max': 5,
    'min_age_hours': 1,
    'min_txns': 50
}

# ============================================================
# BLACKLISTED TOKENS
# ============================================================

BLACKLIST_TOKENS = {
    'So11111111111111111111111111111111111111112',
    'EPjFWdd5AufqSSqewy3WZaNW1pF3Q8dTMm24FYzJR8o',
    'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB',
    '7vfCXTUXx5WJV5JADk17DUJ4ksgau7utNKj4b963voxs',
    'mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So',
    'DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263',
    '0x4200000000000000000000000000000000000006',
    '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913',
    '0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb',
}

# ============================================================
# API ENDPOINTS
# ============================================================

HELIUS_RPC_URL = f"https://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}"
ALCHEMY_BASE_URL = f"https://base-mainnet.g.alchemy.com/v2/{ALCHEMY_API_KEY}"
DEXSCREENER_API = "https://api.dexscreener.com/latest/dex/tokens"

# ============================================================
# ALERT MILESTONES
# ============================================================

PRICE_MILESTONES = [10, 25, 50, 100, 200]

# ============================================================
# FILE PATHS
# ============================================================

WHALE_LIST_FILE = 'whales_tiered_final.json'
BOT_STATE_FILE = 'bot_state.json'
