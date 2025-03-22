import random
import string
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

API_KEY = "AIzaSyBUjhH0GoaNk9V9ebIH0ZYeMBSZWS0VZHg" 

# Function to generate a random YouTube video ID of a given length
def genVidID(length=11):
    characters = string.ascii_letters + string.digits + "_-"
    return ''.join(random.choice(characters) for _ in range(length))

# Function to check if a video exists and get its type
def vidCheck(video_id, api_key):
    youtube = build('youtube', 'v3', developerKey=api_key)

    try:
        response = youtube.videos().list(
            part="status",
            id=video_id
        ).execute()

        if response['items']:
            video_status = response['items'][0]['status']['privacyStatus']
            return True, video_status
        else:
            return False, None
    except HttpError as e:
        print("An error occurred:", e)
        return False, None


while True:
    video_id = genVidID()
    print("Checking ID:", video_id)

    exists, status = vidCheck(video_id, API_KEY)

    if exists:
        print(f"✅ Found: ID '{video_id}' exists and its type is: {status}")
        break
    else:
        pass
