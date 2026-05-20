import re

published = set()

def valid_offer(text):

    if not text:
        return False

    # Cerca percentuali tipo 40%, 55%, ecc.
    sconti = re.findall(r'(\d+)%', text)

    if not sconti:
        return False

    percentuale = max([int(x) for x in sconti])

    if percentuale < 40:
        return False

    # Deve contenere Amazon
    if "amazon" not in text.lower():
        return False

    # Evita duplicati
    if text in published:
        return False

    published.add(text)

    return True