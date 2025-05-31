import requests 
import re
query = input("==>  ")
data = requests.get(f"https://m.soundcloud.com/search?q={query}")

result = []
urls = re.findall(r'data-testid="cell-entity-link" href="([^"]+)', data.text)
photos = re.findall(r'src="(https://i1.sndcdn.com/[^"]+)" data-testid="actual-image"', data.text)
names = re.findall(r'<div class="Information_CellTitle__2KitR">([^<]+)', data.text)
for i in range(len(urls)): result.append({'photo': photos[i], 'title': names[i], 'url': f'https://soundcloud.com{urls[i]}'})
for a in result:
 print(a)
 print("\n\n")
