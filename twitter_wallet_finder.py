"""
Twitter Wallet Finder
Analyzes crypto KOL tweets to find wallet addresses
"""

import re
import json
from datetime import datetime

class TwitterWalletFinder:
    def __init__(self):
        self.solana_pattern = r'[1-9A-HJ-NP-Za-km-z]{32,44}'
        self.evm_pattern = r'0x[a-fA-F0-9]{40}'
        self.discovered_wallets = []

    def find_wallets_in_text(self, text, username, tweet_url=''):
        """
        Extract wallet addresses from tweet text
        """
        wallets = {
            'solana': [],
            'evm': []
        }

        # Find Solana addresses
        sol_matches = re.findall(self.solana_pattern, text)
        for match in sol_matches:
            if self._is_valid_solana(match):
                wallets['solana'].append(match)

        # Find EVM addresses
        evm_matches = re.findall(self.evm_pattern, text)
        wallets['evm'].extend(evm_matches)

        # Save discovered wallets
        if wallets['solana'] or wallets['evm']:
            self.discovered_wallets.append({
                'username': username,
                'tweet_url': tweet_url,
                'timestamp': datetime.now().isoformat(),
                'wallets': wallets
            })

        return wallets

    def _is_valid_solana(self, address):
        """
        Basic Solana address validation
        """
        if len(address) < 32 or len(address) > 44:
            return False

        # Exclude common false positives
        blacklist = ['pump', 'token', 'coin']
        for word in blacklist:
            if word.lower() in address.lower():
                return False

        return True

    def analyze_dexscreener_links(self, tweet_text):
        """
        Extract wallet addresses from Dexscreener transaction links
        Example: dexscreener.com/solana/[token_address]?maker=[wallet_address]
        """
        dex_pattern = r'dexscreener\.com/\w+/([1-9A-HJ-NP-Za-km-z]{32,44})(?:\?maker=([1-9A-HJ-NP-Za-km-z]{32,44}))?'

        matches = re.findall(dex_pattern, tweet_text)
        wallets = []

        for token, maker in matches:
            if maker:
                wallets.append({
                    'wallet': maker,
                    'token': token,
                    'source': 'dexscreener'
                })

        return wallets

    def parse_transaction_screenshot(self, tweet_data):
        """
        Parse transaction details from screenshot tweets
        Returns: timestamp, amount, token for verification
        """
        # Extract common patterns from captions
        patterns = {
            'amount': r'\$([0-9,]+(?:\.[0-9]+)?)',
            'token': r'\$([A-Z]{3,10})\b',
            'time': r'(\d{1,2}:\d{2}\s?[AP]M)'
        }

        result = {}
        text = tweet_data.get('text', '')

        for key, pattern in patterns.items():
            match = re.search(pattern, text)
            if match:
                result[key] = match.group(1)

        return result

    def cross_reference_wallet(self, wallet_address, transaction_data):
        """
        Verify wallet by cross-referencing with Dexscreener

        Args:
            wallet_address: Suspected wallet address
            transaction_data: Dict with timestamp, amount, token from tweet

        Returns:
            confidence_score: 0-100 indicating match likelihood
        """
        # In production, this would call Dexscreener API
        # For now, return structure for manual verification

        return {
            'wallet': wallet_address,
            'verification_needed': True,
            'check_url': f'https://dexscreener.com/solana/{transaction_data.get("token", "")}',
            'filters': {
                'timestamp': transaction_data.get('time'),
                'amount': transaction_data.get('amount'),
                'token': transaction_data.get('token')
            },
            'instructions': 'Filter Dexscreener by timestamp, amount, and check if wallet matches'
        }

    def generate_kol_profile(self, username, wallet_addresses, tweets_analyzed=0):
        """
        Create KOL profile from discovered wallets
        """
        profile = {
            'twitter': f'@{username}',
            'wallets': {
                'solana': [],
                'evm': []
            },
            'discovered_date': datetime.now().isoformat(),
            'tweets_analyzed': tweets_analyzed,
            'confidence': 'medium',
            'source': 'twitter_analysis'
        }

        for wallet_data in wallet_addresses:
            if 'solana' in wallet_data['wallets']:
                profile['wallets']['solana'].extend(wallet_data['wallets']['solana'])
            if 'evm' in wallet_data['wallets']:
                profile['wallets']['evm'].extend(wallet_data['wallets']['evm'])

        # Remove duplicates
        profile['wallets']['solana'] = list(set(profile['wallets']['solana']))
        profile['wallets']['evm'] = list(set(profile['wallets']['evm']))

        return profile

    def save_discovered_wallets(self, filename='twitter_discovered_kols.json'):
        """
        Save all discovered wallets
        """
        output = {
            'timestamp': datetime.now().isoformat(),
            'total_discoveries': len(self.discovered_wallets),
            'wallets': self.discovered_wallets
        }

        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)

        print(f"✅ Saved {len(self.discovered_wallets)} discoveries to {filename}")
        return filename

def example_usage():
    """
    Example: How to use TwitterWalletFinder
    """
    finder = TwitterWalletFinder()

    # Example 1: Analyze tweet with wallet address
    tweet1 = """
    Just bought $BONK! 🚀
    Wallet: DYw8jCTfwHNRJhhmFcbXvVDTqWMEVFBX6ZKUmG5CNSKK
    Let's go! 💎
    """

    wallets = finder.find_wallets_in_text(tweet1, 'crypto_whale', 'https://twitter.com/...')
    print(f"Found wallets: {wallets}")

    # Example 2: Parse Dexscreener link
    tweet2 = """
    New entry! Check my tx:
    dexscreener.com/solana/TokenAddr123?maker=WalletAddr456
    """

    dex_wallets = finder.analyze_dexscreener_links(tweet2)
    print(f"Dexscreener wallets: {dex_wallets}")

    # Example 3: Transaction screenshot analysis
    screenshot_tweet = {
        'text': 'Bought $PEPE for $5,000 at 3:45 PM 🔥',
        'has_image': True
    }

    tx_data = finder.parse_transaction_screenshot(screenshot_tweet)
    print(f"Transaction data: {tx_data}")

    # Example 4: Cross-reference for verification
    verification = finder.cross_reference_wallet(
        'DYw8jCTfwHNRJhhmFcbXvVDTqWMEVFBX6ZKUmG5CNSKK',
        {'time': '3:45 PM', 'amount': '5000', 'token': 'PEPE'}
    )
    print(f"\nVerification needed:")
    print(f"Check: {verification['check_url']}")
    print(f"Filters: {verification['filters']}")

if __name__ == "__main__":
    print("="*60)
    print("🐦 TWITTER WALLET FINDER")
    print("="*60)
    print("\nThis tool helps discover KOL wallets from tweets\n")

    example_usage()
