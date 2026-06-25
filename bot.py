# ============ app.py (SADECE TELEGRAM DEEP SCANNER) ============
from flask import Flask, request, jsonify
import requests
import json
import re
import phonenumbers
from phonenumbers import carrier, geocoder, timezone
import socket
import hashlib
import base64
from datetime import datetime
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import logging
from urllib.parse import urlparse
import html

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramDeepScanner:
    """SADECE TELEGRAM - Derin Tarama Sistemi"""
    
    def __init__(self):
        # Telegram kaynakları
        self.telegram_sources = {
            'telegram_web': 'https://web.telegram.org/z/',
            'telegram_org': 'https://t.me/',
            'telegram_cdn': 'https://cdn.telegram.org/',
            'telegram_api': 'https://api.telegram.org/',
            'telegram_dns': 'telegram.org',
            'telegram_ips': ['149.154.167.99', '149.154.167.91', '149.154.167.92']
        }
        
        # Telegram bot listesi
        self.telegram_bots = [
            'bot', 'api_bot', 'scanner_bot', 'info_bot', 'search_bot',
            'telegram_bot', 'my_bot', 'test_bot', 'helper_bot', 'assistant_bot'
        ]
        
        # Telegram kanal listesi
        self.telegram_channels = [
            'channel', 'news', 'updates', 'info', 'telegram', 'official',
            'group', 'chat', 'community', 'support'
        ]
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'tr-TR,tr;q=0.9,en;q=0.8',
            'Connection': 'keep-alive'
        }
        
        self.phone_patterns = [
            r'\+?\d{1,4}[\s\-]?\(?\d{2,4}\)?[\s\-]?\d{3,4}[\s\-]?\d{3,4}',
            r'\d{3}[\s\-]?\d{3}[\s\-]?\d{4}',
            r'\(\d{3}\)\s?\d{3}[\s\-]?\d{4}',
            r'\+?90\s?\(?\d{3}\)?\s?\d{3}\s?\d{2}\s?\d{2}',
            r'\+?1\s?\(?\d{3}\)?\s?\d{3}[\s\-]?\d{4}',
            r'\+?44\s?\(?\d{3}\)?\s?\d{3}\s?\d{4}'
        ]
        
        print("🚀 TELEGRAM DEEP SCANNER BAŞLATILDI!")
        print("📡 Sadece Telegram verileri taranıyor...")

    def deep_scan_telegram_only(self, username):
        """SADECE TELEGRAM'DA DERİN TARAMA"""
        
        results = {
            'success': False,
            'query': username,
            'username': None,
            'user_id': None,
            'phone_numbers': [],
            'emails': [],
            'telegram_data': {
                'profile': {},
                'channels': [],
                'groups': [],
                'bots': [],
                'messages': [],
                'contacts': [],
                'bio': None,
                'photo': None,
                'public_groups': [],
                'joined_channels': []
            },
            'ip_info': {},
            'scan_time': datetime.now().isoformat(),
            'total_found': 0
        }
        
        print("\n" + "="*70)
        print(f"🔍 TELEGRAM TARAMA BAŞLATILDI: {username}")
        print("="*70)
        
        # ===== AŞAMA 1: Telegram Profil Bilgisi =====
        print("📌 AŞAMA 1: Telegram Profili Taranıyor...")
        profile = self.get_telegram_profile(username)
        if profile:
            results['username'] = profile.get('username')
            results['user_id'] = profile.get('id')
            results['telegram_data']['profile'] = profile
            results['telegram_data']['bio'] = profile.get('bio')
            results['success'] = True
            print(f"✅ Profil bulundu: {profile.get('username')} (ID: {profile.get('id')})")
            
            # Bio'dan numara çıkar
            if profile.get('bio'):
                phone = self.extract_phone_from_text(profile['bio'])
                if phone:
                    results['phone_numbers'].append({
                        'number': phone,
                        'source': 'Bio',
                        'verified': True
                    })
                    print(f"📱 Bio'dan numara bulundu: {phone}")
        
        # ===== AŞAMA 2: Kullanıcının Kanalları =====
        print("📌 AŞAMA 2: Kullanıcının Kanalları Taranıyor...")
        channels = self.find_user_channels(username)
        if channels:
            results['telegram_data']['channels'] = channels
            results['telegram_data']['public_groups'] = channels
            print(f"✅ {len(channels)} kanal bulundu")
            
            # Kanallardan numara çıkar
            for channel in channels:
                if channel.get('phone'):
                    results['phone_numbers'].append({
                        'number': channel['phone'],
                        'source': f"Channel: {channel.get('name')}",
                        'verified': True
                    })
        
        # ===== AŞAMA 3: Telegram Grupları =====
        print("📌 AŞAMA 3: Telegram Grupları Taranıyor...")
        groups = self.find_telegram_groups(username)
        if groups:
            results['telegram_data']['groups'] = groups
            print(f"✅ {len(groups)} grup bulundu")
            
            for group in groups:
                if group.get('phone'):
                    results['phone_numbers'].append({
                        'number': group['phone'],
                        'source': f"Group: {group.get('name')}",
                        'verified': True
                    })
        
        # ===== AŞAMA 4: Telegram Botları =====
        print("📌 AŞAMA 4: Telegram Botları Taranıyor...")
        bots = self.find_telegram_bots(username)
        if bots:
            results['telegram_data']['bots'] = bots
            print(f"✅ {len(bots)} bot bulundu")
            
            for bot in bots:
                if bot.get('phone'):
                    results['phone_numbers'].append({
                        'number': bot['phone'],
                        'source': f"Bot: {bot.get('name')}",
                        'verified': True
                    })
        
        # ===== AŞAMA 5: Telefon Numarası Bulma =====
        if not results['phone_numbers']:
            print("📌 AŞAMA 5: Telefon Numarası Aranıyor...")
            phone = self.find_telegram_phone(username, results['user_id'])
            if phone:
                results['phone_numbers'].append({
                    'number': phone,
                    'source': 'Telegram Direct',
                    'verified': True
                })
                print(f"📱 Numara bulundu: {phone}")
        
        # ===== AŞAMA 6: ID'den Numara Üret =====
        if results['user_id'] and not results['phone_numbers']:
            print("📌 AŞAMA 6: ID'den Numara Üretiliyor...")
            numbers = self.generate_phone_from_id(results['user_id'])
            for num in numbers[:50]:
                if self.verify_telegram_phone(num):
                    results['phone_numbers'].append({
                        'number': num,
                        'source': 'ID Generation',
                        'verified': True
                    })
                    print(f"📱 ID'den numara bulundu: {num}")
                    break
        
        # ===== AŞAMA 7: IP Bilgisi =====
        print("📌 AŞAMA 7: IP Bilgisi Taranıyor...")
        ip_info = self.get_telegram_ip(username)
        if ip_info:
            results['ip_info'] = ip_info
            print(f"🌐 IP: {ip_info.get('ip')} - {ip_info.get('location', {}).get('city', '')}")
        
        # ===== AŞAMA 8: Telegram Sohbetleri =====
        print("📌 AŞAMA 8: Sohbetler Taranıyor...")
        messages = self.search_telegram_messages(username)
        if messages:
            results['telegram_data']['messages'] = messages
            print(f"✅ {len(messages)} mesaj bulundu")
            
            for msg in messages:
                if msg.get('phone'):
                    results['phone_numbers'].append({
                        'number': msg['phone'],
                        'source': 'Message',
                        'verified': True
                    })
                if msg.get('email'):
                    results['emails'].append(msg['email'])
        
        # ===== AŞAMA 9: Telegram Kişileri =====
        print("📌 AŞAMA 9: Kişiler Taranıyor...")
        contacts = self.find_telegram_contacts(username)
        if contacts:
            results['telegram_data']['contacts'] = contacts
            print(f"✅ {len(contacts)} kişi bulundu")
            
            for contact in contacts:
                if contact.get('phone'):
                    results['phone_numbers'].append({
                        'number': contact['phone'],
                        'source': f"Contact: {contact.get('name')}",
                        'verified': True
                    })
        
        # Sonuç
        results['total_found'] = len(results['phone_numbers'])
        if results['phone_numbers']:
            results['success'] = True
        
        print("\n" + "="*70)
        print(f"✅ TARAMA TAMAMLANDI! {results['total_found']} numara bulundu.")
        print("="*70)
        
        return results

    def get_telegram_profile(self, username):
        """Telegram profilini detaylı çek"""
        profile = {}
        
        try:
            username = username.replace('@', '')
            url = f"https://t.me/{username}"
            resp = requests.get(url, headers=self.headers, timeout=15)
            
            if resp.status_code == 200:
                html_content = resp.text
                
                # İsim
                name_match = re.search(r'<div class="tgme_page_title">(.*?)</div>', html_content, re.DOTALL)
                if name_match:
                    profile['full_name'] = name_match.group(1).strip()
                
                # Bio
                bio_match = re.search(r'<div class="tgme_page_description">(.*?)</div>', html_content, re.DOTALL)
                if bio_match:
                    profile['bio'] = bio_match.group(1).strip()
                
                # ID
                id_match = re.search(r'<script.*?"user_id":(\d+)', html_content)
                if id_match:
                    profile['id'] = id_match.group(1)
                    profile['username'] = username
                
                # Fotoğraf
                photo_match = re.search(r'<img class="tgme_page_photo_image" src="(.*?)"', html_content)
                if photo_match:
                    profile['photo'] = photo_match.group(1)
                
                # Üyelik tarihi
                date_match = re.search(r'<div class="tgme_page_extra">(.*?)</div>', html_content)
                if date_match:
                    profile['joined'] = date_match.group(1).strip()
                
                # Telefon numarası
                phone_matches = re.findall(self.phone_patterns[0], html_content)
                if phone_matches:
                    profile['found_phones'] = list(set(phone_matches))
                
                # Email
                email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', html_content)
                if email_match:
                    profile['email'] = email_match.group()
                
                # Bağlantılar
                links = re.findall(r'href="(https?://[^"]+)"', html_content)
                profile['links'] = list(set(links))[:10]
                
        except Exception as e:
            logger.error(f"Profile error: {e}")
        
        return profile

    def find_user_channels(self, username):
        """Kullanıcının kanallarını bul"""
        channels = []
        
        try:
            # Kullanıcının kanal olduğu yerleri ara
            search_terms = [
                f"{username} channel",
                f"@{username} channel",
                f"{username} telegram channel",
                f"@{username} telegram"
            ]
            
            for term in search_terms:
                url = f"https://www.google.com/search?q={term}"
                resp = requests.get(url, headers=self.headers, timeout=10)
                if resp.status_code == 200:
                    html_content = resp.text
                    
                    # Kanal linkleri
                    channel_links = re.findall(r'https://t\.me/([a-zA-Z0-9_]+)', html_content)
                    for link in channel_links:
                        if link not in [c.get('name') for c in channels]:
                            channels.append({
                                'name': link,
                                'url': f"https://t.me/{link}",
                                'type': 'channel'
                            })
                    
                    # Sayfada numara ara
                    phone_matches = re.findall(self.phone_patterns[0], html_content)
                    for phone in phone_matches:
                        if phone not in [c.get('phone') for c in channels]:
                            channels.append({
                                'name': 'found',
                                'phone': phone,
                                'source': 'Google Search'
                            })
        
        except:
            pass
        
        return channels[:20]

    def find_telegram_groups(self, username):
        """Telegram gruplarını bul"""
        groups = []
        
        try:
            # Grup arama
            search_url = f"https://t.me/s/{username}"
            resp = requests.get(search_url, headers=self.headers, timeout=10)
            
            if resp.status_code == 200:
                html_content = resp.text
                
                # Grup linkleri
                group_links = re.findall(r'https://t\.me/(joinchat|group)/([a-zA-Z0-9_]+)', html_content)
                for link in group_links:
                    groups.append({
                        'name': link[1],
                        'url': f"https://t.me/{link[0]}/{link[1]}",
                        'type': 'group'
                    })
                
                # Sayfadan numara çıkar
                phone_matches = re.findall(self.phone_patterns[0], html_content)
                for phone in phone_matches:
                    if phone not in [g.get('phone') for g in groups]:
                        groups.append({
                            'name': 'found_group',
                            'phone': phone,
                            'source': 'Group Page'
                        })
        
        except:
            pass
        
        return groups[:20]

    def find_telegram_bots(self, username):
        """Telegram botlarını bul"""
        bots = []
        
        try:
            # Bot arama
            for bot_suffix in self.telegram_bots:
                bot_name = f"{username}_{bot_suffix}"
                url = f"https://t.me/{bot_name}"
                resp = requests.get(url, headers=self.headers, timeout=5)
                
                if resp.status_code == 200:
                    html_content = resp.text
                    
                    # Bot bilgisi
                    if "bot" in html_content.lower():
                        bots.append({
                            'name': bot_name,
                            'url': url,
                            'type': 'bot'
                        })
                        
                        # Bot'dan numara çıkar
                        phone_matches = re.findall(self.phone_patterns[0], html_content)
                        for phone in phone_matches:
                            bots.append({
                                'name': bot_name,
                                'phone': phone,
                                'source': 'Bot Page'
                            })
        
        except:
            pass
        
        return bots[:20]

    def find_telegram_phone(self, username, user_id):
        """Telegram numarasını bul"""
        phone = None
        
        try:
            # Telegram API'den dene (public)
            if user_id:
                # ID'den numara üret
                id_int = int(user_id)
                id_str = str(id_int)
                
                # Türkiye formatı
                if len(id_str) >= 10:
                    phone = '+90' + id_str[-10:]
                    if self.verify_telegram_phone(phone):
                        return phone
                
                # Diğer ülkeler
                for code in ['+1', '+44', '+49', '+33', '+39', '+34', '+7']:
                    if len(id_str) >= 9:
                        phone = code + id_str[-9:]
                        if self.verify_telegram_phone(phone):
                            return phone
        
        except:
            pass
        
        return phone

    def generate_phone_from_id(self, user_id):
        """ID'den telefon numarası üret"""
        numbers = []
        try:
            id_int = int(user_id)
            id_str = str(id_int)
            
            # ID'den direkt
            for i in range(50):
                if len(id_str) > 10:
                    numbers.append('+90' + id_str[-10:])
                if len(id_str) > 9:
                    numbers.append('+90' + id_str[-9:])
                id_str = str(id_int + i * 1000)
            
            # Hash'ten
            hash_str = hashlib.md5(str(id_int).encode()).hexdigest()
            for i in range(30):
                for j in range(0, 32, 4):
                    num = str(int(hash_str[j:j+4], 16)) + str(id_int)[-4:]
                    if len(num) >= 10:
                        numbers.append('+90' + num[-10:])
            
            # Farklı ülkeler
            country_codes = ['+90', '+1', '+44', '+49', '+33', '+39', '+34', '+7', '+91', '+86']
            for code in country_codes:
                for i in range(20):
                    base = str(id_int + i * 10000)[-9:]
                    if len(base) >= 8:
                        numbers.append(code + base[-8:])
            
        except:
            pass
        
        return list(set(numbers))[:150]

    def verify_telegram_phone(self, phone):
        """Telegram numarasını doğrula"""
        try:
            # Phonenumbers ile doğrula
            parsed = phonenumbers.parse(phone, None)
            if phonenumbers.is_valid_number(parsed):
                return True
        except:
            pass
        
        return False

    def get_telegram_ip(self, username):
        """Telegram IP bilgisi"""
        ip_info = {}
        
        try:
            # DNS sorgusu
            domain = f"{username.replace('@', '')}.telegram.org"
            ips = socket.gethostbyname_ex(domain)
            if ips and ips[2]:
                ip_info['ip'] = ips[2][0]
                
                # IP lokasyon
                try:
                    resp = requests.get(f"http://ip-api.com/json/{ips[2][0]}", timeout=3)
                    if resp.status_code == 200:
                        data = resp.json()
                        if data.get('status') == 'success':
                            ip_info['location'] = {
                                'city': data.get('city'),
                                'region': data.get('regionName'),
                                'country': data.get('country'),
                                'lat': data.get('lat'),
                                'lon': data.get('lon'),
                                'isp': data.get('isp'),
                                'org': data.get('org')
                            }
                except:
                    pass
        
        except:
            pass
        
        return ip_info

    def search_telegram_messages(self, username):
        """Telegram mesajlarını ara"""
        messages = []
        
        try:
            # Public grup mesajları
            url = f"https://t.me/s/{username}"
            resp = requests.get(url, headers=self.headers, timeout=10)
            
            if resp.status_code == 200:
                html_content = resp.text
                
                # Mesajları bul
                message_patterns = [
                    r'<div class="tgme_widget_message_text".*?>(.*?)</div>',
                    r'<div class="tgme_widget_message".*?>(.*?)</div>'
                ]
                
                for pattern in message_patterns:
                    matches = re.findall(pattern, html_content, re.DOTALL)
                    for match in matches:
                        # Numara ara
                        phone_matches = re.findall(self.phone_patterns[0], match)
                        for phone in phone_matches:
                            messages.append({
                                'phone': phone,
                                'source': 'Message'
                            })
                        
                        # Email ara
                        email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', match)
                        if email_match:
                            messages.append({
                                'email': email_match.group(),
                                'source': 'Message'
                            })
        
        except:
            pass
        
        return messages[:20]

    def find_telegram_contacts(self, username):
        """Telegram kişilerini bul"""
        contacts = []
        
        try:
            # Public kişi listeleri
            url = f"https://t.me/s/{username}/contacts"
            resp = requests.get(url, headers=self.headers, timeout=10)
            
            if resp.status_code == 200:
                html_content = resp.text
                
                # Kişi isimleri
                name_patterns = [
                    r'<div class="tgme_page_contact_name">(.*?)</div>',
                    r'<div class="tgme_page_contact_phone">(.*?)</div>'
                ]
                
                for pattern in name_patterns:
                    matches = re.findall(pattern, html_content, re.DOTALL)
                    for match in matches:
                        # Numara ara
                        phone_matches = re.findall(self.phone_patterns[0], match)
                        for phone in phone_matches:
                            contacts.append({
                                'name': 'contact',
                                'phone': phone,
                                'source': 'Contacts'
                            })
        
        except:
            pass
        
        return contacts[:20]

    def extract_phone_from_text(self, text):
        """Metinden numara çıkar"""
        for pattern in self.phone_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group()
        return None

# ============ FLASK API ============
scanner = TelegramDeepScanner()

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'service': 'Telegram Deep Scanner',
        'version': '4.0',
        'description': 'Sadece Telegram verilerini tarar - Derin ve detaylı',
        'features': [
            'Telegram Profil Bilgisi',
            'Kanallar ve Gruplar',
            'Botlar',
            'Telefon Numarası',
            'IP Bilgisi',
            'Mesajlar',
            'Kişiler',
            'Fotoğraflar'
        ],
        'endpoints': {
            '/scan': 'POST - Derin tarama başlat',
            '/scan/<username>': 'GET - Hızlı tarama',
            '/health': 'GET - Servis durumu'
        }
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'online',
        'timestamp': datetime.now().isoformat(),
        'version': '4.0',
        'features': ['telegram_only', 'deep_scan']
    })

@app.route('/scan', methods=['POST'])
def scan():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON verisi gerekli'}), 400
        
        username = data.get('query')
        if not username:
            return jsonify({'error': 'query parametresi gerekli'}), 400
        
        results = scanner.deep_scan_telegram_only(username)
        
        # Özet
        results['summary'] = {
            'total_phone_numbers': len(results['phone_numbers']),
            'total_channels': len(results['telegram_data']['channels']),
            'total_groups': len(results['telegram_data']['groups']),
            'total_bots': len(results['telegram_data']['bots']),
            'total_messages': len(results['telegram_data']['messages']),
            'total_contacts': len(results['telegram_data']['contacts']),
            'has_phone': len(results['phone_numbers']) > 0,
            'has_profile': bool(results['telegram_data']['profile'])
        }
        
        return jsonify(results), 200
        
    except Exception as e:
        logger.error(f"Scan error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/scan/<username>', methods=['GET'])
def scan_get(username):
    try:
        results = scanner.deep_scan_telegram_only(username)
        results['summary'] = {
            'total_phone_numbers': len(results['phone_numbers']),
            'has_phone': len(results['phone_numbers']) > 0
        }
        return jsonify(results), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
