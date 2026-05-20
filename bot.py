from telethon import TelegramClient, events
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from config import (
    BOT_TOKEN,
    API_ID,
    API_HASH,
    CIVETTA_CHANNEL,
    MAIN_CHANNEL,
    AFFILIATE_TAG
)

from database import add_offer

import re
import os
import hashlib


bot = Bot(token=BOT_TOKEN)

client = TelegramClient(
    "rosadeals_session",
    API_ID,
    API_HASH
)

source_channels = [
    -1001394573224,
    -1001392634928,
    -1001238009951,
    -1003821845518,
    -1001857419791
]

print("RosaDeals avviato")
print("Canali monitorati:", source_channels)

pending_offers = {}


# =====================================
# LINK AFFILIATO AMAZON
# =====================================
def replace_affiliate(url):

    if not url:
        return ""

    lower = url.lower()

    blacklist = [
        "/deals",
        "/gp/goldbox",
        "/events",
        "offerte",
        "offers"
    ]

    for bad in blacklist:

        if bad in lower:

            print(
                "⚠️ Link generico ignorato:",
                url
            )

            return ""

    url = re.sub(
        r'([?&])(psc|ref|smid|linkcode|camp|creative|creativeasin)=[^&]*',
        '',
        url,
        flags=re.IGNORECASE
    )

    if "tag=" in url:

        url = re.sub(
            r'tag=[^&]+',
            f'tag={AFFILIATE_TAG}',
            url
        )

    else:

        sep = "&" if "?" in url else "?"
        url += f"{sep}tag={AFFILIATE_TAG}"

    return url


# =====================================
# PULIZIA TESTO
# =====================================
def clean_text(text, amazon_url):

    # rimuove VAI ALL'OFFERTA
    text = re.sub(
        r'👉?\s*VAI ALL.?OFFERTA',
        '',
        text,
        flags=re.IGNORECASE
    )

    # rimuove eventuali link Amazon vecchi
    text = re.sub(
        r'https?://(?:www\.)?(amazon\.[^\s]+|amzn\.to[^\s]+)',
        '',
        text,
        flags=re.IGNORECASE
    )

    # rimuove hashtag
    text = re.sub(
        r'#\S+',
        '',
        text
    )

    # pulisce righe vuote multiple
    text = re.sub(
        r'\n{3,}',
        '\n\n',
        text
    )

    lines = text.split("\n")

    nuovo_testo = []

    link_inserito = False

    for line in lines:

        nuovo_testo.append(line)

        # inserisce il link subito dopo la riga prezzo
        if (
            "€" in line
            and not link_inserito
        ):

            nuovo_testo.append(
                f"\n👉 {amazon_url}"
            )

            link_inserito = True


    # sicurezza: se non trova prezzo
    if not link_inserito:

        nuovo_testo.append(
            f"\n👉 {amazon_url}"
        )

    return "\n".join(
        nuovo_testo
    ).strip()


# =====================================
# NUOVA OFFERTA
# =====================================
@client.on(events.NewMessage(chats=source_channels))
async def new_offer(event):

    print("\n🔥 Nuova offerta trovata")

    amazon_url = None

    try:

        text = event.message.message or ""

        # BOTTONI
        if event.message.buttons:

            for row in event.message.buttons:

                for button in row:

                    url = getattr(
                        button,
                        "url",
                        None
                    )

                    if (
                        url and
                        (
                            "amazon" in url.lower()
                            or
                            "amzn.to" in url.lower()
                        )
                    ):

                        amazon_url = url
                        break

                if amazon_url:
                    break


        # ENTITY
        if (
            not amazon_url
            and
            event.message.entities
        ):

            for entity in event.message.entities:

                url = getattr(
                    entity,
                    "url",
                    None
                )

                if (
                    url and
                    (
                        "amazon" in url.lower()
                        or
                        "amzn.to" in url.lower()
                    )
                ):

                    amazon_url = url
                    break


        # TESTO
        if not amazon_url:

            urls = re.findall(
                r'https?://[^\s]+',
                text
            )

            for url in urls:

                if (
                    "amazon" in url.lower()
                    or
                    "amzn.to" in url.lower()
                ):

                    amazon_url = url
                    break


        if not amazon_url:

            print("❌ Nessun link Amazon")
            print("📝 Messaggio:")
            print(text[:300])

            return


        amazon_url = replace_affiliate(
            amazon_url
        )


        if not amazon_url:

            print(
                "❌ Link Amazon scartato"
            )

            return


        # QUI APPLICA PULIZIA TESTO
        text = clean_text(
            text,
            amazon_url
        )


        offer_id = hashlib.md5(
            text.encode()
        ).hexdigest()


        pending_offers[offer_id] = {
            "text": text,
            "url": amazon_url
        }


        keyboard = [
            [
                InlineKeyboardButton(
                    "✅ Pubblica",
                    callback_data=f"publish|{offer_id}"
                ),
                InlineKeyboardButton(
                    "❌ Scarta",
                    callback_data=f"discard|{offer_id}"
                )
            ]
        ]

        reply_markup = InlineKeyboardMarkup(
            keyboard
        )


        # INVIO CIVETTA
        if event.message.media:

            file = await event.download_media()

            if file and os.path.exists(file):

                with open(
                    file,
                    "rb"
                ) as photo:

                    await bot.send_photo(
                        chat_id=CIVETTA_CHANNEL,
                        photo=photo,
                        caption=text,
                        reply_markup=reply_markup
                    )

                os.remove(file)

            else:

                await bot.send_message(
                    chat_id=CIVETTA_CHANNEL,
                    text=text,
                    reply_markup=reply_markup
                )

        else:

            await bot.send_message(
                chat_id=CIVETTA_CHANNEL,
                text=text,
                reply_markup=reply_markup
            )

        print("✅ Inviata al civetta")


    except Exception as e:

        print("❌ ERRORE:")
        print(e)


# =====================================
# BOTTONI
# =====================================
@client.on(events.CallbackQuery)
async def callback_handler(event):

    data = event.data.decode()

    print(
        "\n🔘 Bottone:",
        data
    )

    try:

        action, offer_id = data.split(
            "|",
            1
        )

        offer = pending_offers.get(
            offer_id
        )

        if not offer:

            await event.answer(
                "❌ Offerta non trovata"
            )

            return


        if action == "publish":

            await bot.send_message(
                chat_id=MAIN_CHANNEL,
                text=offer["text"]
            )

            await event.answer(
                "✅ Pubblicata!"
            )

            print(
                "🚀 Pubblicata nel MAIN"
            )


        elif action == "discard":

            await event.answer(
                "❌ Scartata"
            )

            print(
                "🗑 Scartata"
            )


        pending_offers.pop(
            offer_id,
            None
        )


    except Exception as e:

        print(
            "❌ Errore callback:",
            e
        )


client.start()

print("Sistema attivo 🚀")

client.run_until_disconnected()

from flask import Flask
from threading import Thread
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "RosaDeals attivo"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

Thread(target=run_web).start()