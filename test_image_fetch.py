import urllib.request
import urllib.parse
import json

def get_wikimedia_image(query):
    # Search for page
    search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(query)}&utf8=&format=json"
    req = urllib.request.Request(search_url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            if not data.get('query', {}).get('search'): return None
            title = data['query']['search'][0]['title']
            
            # Get page image
            img_url = f"https://en.wikipedia.org/w/api.php?action=query&titles={urllib.parse.quote(title)}&prop=pageimages&piprop=original&format=json"
            req2 = urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req2) as resp2:
                data2 = json.loads(resp2.read().decode())
                pages = data2.get('query', {}).get('pages', {})
                for page_id, page_info in pages.items():
                    if 'original' in page_info:
                        return page_info['original']['source']
    except Exception as e:
        print(e)
    return None

print(get_wikimedia_image("Royal Enfield Classic 350"))
print(get_wikimedia_image("iPhone 14 Pro"))
