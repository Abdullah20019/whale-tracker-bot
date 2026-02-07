"""
KOL Integration Script
Automatically adds discovered KOL wallets to your whale tracker bot
"""

import json
from datetime import datetime

class KOLIntegrator:
    def __init__(self, whale_file='whales_tiered_final.json', kol_file='kol_wallets.json'):
        self.whale_file = whale_file
        self.kol_file = kol_file
        self.whales = []
        self.kols = []

    def load_existing_whales(self):
        """
        Load current whale tracker list
        """
        try:
            with open(self.whale_file, 'r') as f:
                self.whales = json.load(f)
            print(f"✅ Loaded {len(self.whales)} existing whales")
            return True
        except FileNotFoundError:
            print(f"⚠️ {self.whale_file} not found, will create new file")
            self.whales = []
            return False

    def load_kol_wallets(self):
        """
        Load scraped KOL wallets
        """
        try:
            with open(self.kol_file, 'r') as f:
                data = json.load(f)
                self.kols = data.get('kols', [])
            print(f"✅ Loaded {len(self.kols)} KOL wallets")
            return True
        except FileNotFoundError:
            print(f"❌ {self.kol_file} not found. Run kol_scraper.py first!")
            return False

    def check_duplicates(self, address):
        """
        Check if wallet already exists
        """
        for whale in self.whales:
            if whale.get('address', '').lower() == address.lower():
                return True
        return False

    def convert_kol_to_whale_format(self, kol):
        """
        Convert KOL data to whale tracker format
        """
        whale_entry = {
            'address': kol['address'],
            'chain': kol['chain'],
            'tier': kol['tier'],
            'name': kol.get('name', 'Unknown KOL'),
            'twitter': kol.get('twitter', ''),
            'type': 'kol',  # Flag as KOL for special handling
            'source': kol.get('source', 'kol_scraper'),
            'added_date': datetime.now().isoformat(),
            # Performance metrics
            'win_rate': kol.get('winrate', 0),
            'win_count': 0,
            'loss_count': 0,
            'total_gain': kol.get('realized_profit', 0),
            'total_calls': kol.get('total_trades', 0),
            'pnl_7d': kol.get('pnl_7d', 0),
            # Tracking metadata
            'last_active': None,
            'avg_gain_per_win': 0
        }

        return whale_entry

    def add_kols_to_tracker(self, min_tier=3, overwrite_duplicates=False):
        """
        Add KOL wallets to whale tracker

        Args:
            min_tier: Only add KOLs with tier <= min_tier (1=best, 4=worst)
            overwrite_duplicates: Update existing entries with KOL data
        """
        print(f"\n🔍 Adding KOLs (Tier 1-{min_tier}) to whale tracker...")

        added = 0
        skipped = 0
        updated = 0

        for kol in self.kols:
            # Filter by tier
            if kol['tier'] > min_tier:
                continue

            address = kol['address']

            # Check for duplicates
            if self.check_duplicates(address):
                if overwrite_duplicates:
                    # Remove old entry
                    self.whales = [w for w in self.whales if w.get('address', '').lower() != address.lower()]
                    # Add updated entry
                    whale_entry = self.convert_kol_to_whale_format(kol)
                    self.whales.append(whale_entry)
                    updated += 1
                    print(f"  🔄 Updated: {kol.get('name', address[:8])} (@{kol.get('twitter', 'unknown')})")
                else:
                    skipped += 1
                    continue
            else:
                # Add new entry
                whale_entry = self.convert_kol_to_whale_format(kol)
                self.whales.append(whale_entry)
                added += 1

                tier_emoji = ['🔥', '⭐', '📊', '💤'][kol['tier'] - 1]
                print(f"  ✅ Added: {tier_emoji} {kol.get('name', address[:8])} | {kol['chain'].upper()} | @{kol.get('twitter', 'unknown')}")

        print(f"\n📊 Integration Results:")
        print(f"  ✅ Added: {added} new KOLs")
        print(f"  🔄 Updated: {updated} existing entries")
        print(f"  ⏭️ Skipped: {skipped} duplicates")
        print(f"  🎯 Total whales: {len(self.whales)}")

        return added, updated, skipped

    def save_updated_whales(self, backup=True):
        """
        Save updated whale list with KOLs
        """
        if backup and len(self.whales) > 0:
            backup_file = f"{self.whale_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            try:
                with open(self.whale_file, 'r') as f:
                    original = f.read()
                with open(backup_file, 'w') as f:
                    f.write(original)
                print(f"\n💾 Backup created: {backup_file}")
            except:
                pass

        with open(self.whale_file, 'w') as f:
            json.dump(self.whales, f, indent=2)

        print(f"✅ Saved {len(self.whales)} whales to {self.whale_file}")
        return self.whale_file

    def generate_report(self):
        """
        Generate integration report
        """
        kol_whales = [w for w in self.whales if w.get('type') == 'kol']
        regular_whales = [w for w in self.whales if w.get('type') != 'kol']

        kol_by_chain = {}
        kol_by_tier = {1: 0, 2: 0, 3: 0, 4: 0}

        for kol in kol_whales:
            chain = kol.get('chain', 'unknown')
            kol_by_chain[chain] = kol_by_chain.get(chain, 0) + 1

            tier = kol.get('tier', 4)
            kol_by_tier[tier] = kol_by_tier.get(tier, 0) + 1

        print("\n" + "="*60)
        print("📊 KOL INTEGRATION REPORT")
        print("="*60)
        print(f"\n🎯 Total Wallets: {len(self.whales)}")
        print(f"  🌟 KOLs: {len(kol_whales)}")
        print(f"  🐋 Regular Whales: {len(regular_whales)}")

        print("\n🔗 KOLs by Chain:")
        for chain, count in kol_by_chain.items():
            print(f"  {chain.upper()}: {count}")

        print("\n🏆 KOLs by Tier:")
        tier_labels = {1: "Elite (30s)", 2: "Active (3m)", 3: "Semi (10m)", 4: "Dormant (24h)"}
        for tier, count in sorted(kol_by_tier.items()):
            if count > 0:
                print(f"  Tier {tier} - {tier_labels[tier]}: {count}")

        print("\n🎯 Top 10 KOLs:")
        sorted_kols = sorted(kol_whales, key=lambda x: (x.get('tier', 4), -x.get('win_rate', 0)))[:10]
        for i, kol in enumerate(sorted_kols, 1):
            tier_emoji = ['🔥', '⭐', '📊', '💤'][kol.get('tier', 4) - 1]
            print(f"  {i}. {tier_emoji} {kol.get('name', 'Unknown')} | {kol.get('chain', '?').upper()} | @{kol.get('twitter', 'unknown')}")

        print("="*60 + "\n")

def main():
    """
    Main execution
    """
    print("="*60)
    print("🔗 KOL INTEGRATION TOOL")
    print("="*60)

    integrator = KOLIntegrator()

    # Load data
    if not integrator.load_kol_wallets():
        print("\n❌ Cannot proceed without KOL data. Run kol_scraper.py first!")
        return

    integrator.load_existing_whales()

    # Add KOLs (only Tier 1-2 for high quality)
    added, updated, skipped = integrator.add_kols_to_tracker(
        min_tier=2,  # Only add Tier 1 (Elite) and Tier 2 (Active)
        overwrite_duplicates=False
    )

    # Save if any changes
    if added > 0 or updated > 0:
        integrator.save_updated_whales(backup=True)
        integrator.generate_report()

        print("\n✅ Integration complete!")
        print("\n🚀 Next steps:")
        print("  1. Review whales_tiered_final.json")
        print("  2. Push to GitHub: git add . && git commit -m 'Added KOL wallets' && git push")
        print("  3. Railway will auto-deploy with new KOLs!")
        print("  4. Check Telegram for KOL alerts 🎯\n")
    else:
        print("\n⚠️ No changes made. All KOLs already in tracker or below quality threshold.")

if __name__ == "__main__":
    main()
