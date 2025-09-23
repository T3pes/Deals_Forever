#!/usr/bin/env python3
# post_bot.py - invia post da JSON a canale Telegram
# ATTENZIONE: inserisci TOKEN e CHAT_ID nel file .env o passali come variabili d'ambiente
import os, json, time, requests, logging
from pathlib import Path
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN') or 'YOUR_BOT_TOKEN'
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID') or '@your_channel_or_id'

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def send_photo_with_caption(photo_url, caption, parse_mode='HTML'):
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
    payload = {'chat_id': CHAT_ID, 'photo': photo_url, 'caption': caption, 'parse_mode': parse_mode}
    r = requests.post(url, data=payload)
    return r.json()

def main():
    data_dir = Path(__file__).resolve().parents[1] / 'data'
    for fname in ['funko.json','tech.json','casa.json']:
        path = data_dir / fname
        if not path.exists(): continue
        items = load_json(path)
        for item in items[:5]:  # invia i primi 5 per test
            caption = f"<b>{item.get('title')}</b>\n{item.get('price')} (prima {item.get('original_price')})\n{item.get('review')}\n{item.get('link')}")
            logging.info('Invio: %s', item.get('title'))
            resp = send_photo_with_caption(item.get('image'), caption)
            logging.info('Risposta Telegram: %s', resp)
            time.sleep(2)
if __name__=='__main__': main()
