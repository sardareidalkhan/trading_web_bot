import sys
sys.path.append('./pyquotex')  # Add the local pyquotex folder to the Python path

from pyquotex.qxbroker import Quotex
import asyncio

async def main():
    qx = Quotex(email="sardareidalkhan11@gmail.com", password="$$$02450245")

    await qx.connect()
    if not qx.is_connected:
        print("❌ Failed to connect")
        return

    if not qx.is_authenticated:
        print("❌ Login failed, check your credentials.")
        return

    print("✅ Logged in successfully!")

    pairs = await qx.get_all_assets()
    print("Available assets:")
    for pair in pairs:
        print("-", pair)

    await qx.close()

asyncio.run(main())