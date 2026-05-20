from flask import Flask, render_template, redirect
from database import (
    get_pending,
    approve_offer,
    reject_offer,
    cursor
)

from telegram import Bot
from config import BOT_TOKEN, MAIN_CHANNEL

app = Flask(__name__)

bot = Bot(token=BOT_TOKEN)


@app.route("/")
def home():

    offers = get_pending()

    return render_template(
        "dashboard.html",
        offers=offers
    )


@app.route("/approve/<offer_id>")
def approve(offer_id):

    cursor.execute(
        """
        SELECT text
        FROM offers
        WHERE id=?
        """,
        (offer_id,)
    )

    offer = cursor.fetchone()

    if offer:

        text = offer[0]

        bot.send_message(
            chat_id=MAIN_CHANNEL,
            text=text
        )

        approve_offer(
            offer_id
        )

    return redirect("/")


@app.route("/reject/<offer_id>")
def reject(offer_id):

    reject_offer(
        offer_id
    )

    return redirect("/")


if __name__ == "__main__":

    print("🔥 Dashboard attiva")

    app.run(
        debug=True
    )