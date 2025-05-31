import os
from telethon import TelegramClient, events
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

load_dotenv()

# إعدادات سبوتيفاي
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

client_credentials_manager = SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# إعدادات تيليجرام
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@bot.on(events.NewMessage(pattern=r'^\.اغنية (.+)'))
async def search_song(event):
    query = event.pattern_match.group(1)
    await event.reply(f"🔍 جارٍ البحث عن الأغنية: {query}")

    try:
        results = sp.search(q=query, type='track', limit=1)
        if results['tracks']['items']:
            track = results['tracks']['items'][0]
            name = track['name']
            artist = track['artists'][0]['name']
            album = track['album']['name']
            spotify_url = track['external_urls']['spotify']

            response = (
                f"🎵 **اسم الأغنية:** {name}\n"
                f"👤 **الفنان:** {artist}\n"
                f"💿 **الألبوم:** {album}\n"
                f"🔗 [استمع على Spotify]({spotify_url})"
            )
            await event.reply(response, link_preview=False)
        else:
            await event.reply("⚠️ لم أتمكن من العثور على الأغنية المطلوبة.")
    except Exception as e:
        await event.reply(f"⚠️ حدث خطأ أثناء البحث: {str(e)}")

print("🤖 البوت بدأ العمل...")
bot.run_until_disconnected()
