"""
Il carattere di controllo del codice fiscale (DM 23 dicembre 1976): pesi diversi per le posizioni
dispari e pari, somma modulo 26, una lettera. Serve a scoprire un codice trascritto male prima
che arrivi in un F24 o in un UniEmens.
"""
import random
import string

DISPARI = {
    **dict(zip("0123456789", [1, 0, 5, 7, 9, 13, 15, 17, 19, 21])),
    **dict(zip(string.ascii_uppercase, [1, 0, 5, 7, 9, 13, 15, 17, 19, 21, 2, 4, 18, 20, 11, 3, 6, 8, 12, 14,
                                         16, 10, 22, 25, 24, 23])),
}
PARI = {**{c: int(c) for c in "0123456789"}, **{c: i for i, c in enumerate(string.ascii_uppercase)}}
MESI = "ABCDEHLMPRST"


def carattere_controllo(primi15: str) -> str:
    s = sum(DISPARI[c] if i % 2 == 0 else PARI[c] for i, c in enumerate(primi15.upper()))
    return string.ascii_uppercase[s % 26]


def valido(cf: str) -> bool:
    cf = str(cf).strip().upper()
    if len(cf) != 16 or not cf[:15].isalnum() or cf[15] not in string.ascii_uppercase:
        return False
    try:
        return carattere_controllo(cf[:15]) == cf[15]
    except KeyError:
        return False


def sintetico(rng: random.Random, nascita, donna: bool) -> str:
    """Un codice formalmente valido per una persona inventata: lettere casuali al posto di nome e
    cognome e un comune estero (Z...), così non può coincidere con una persona reale di proposito."""
    lettere = "".join(rng.choice("BCDFGLMNPRSTVZ") for _ in range(6))
    giorno = nascita.day + (40 if donna else 0)
    comune = f"Z{rng.randint(100, 399)}"
    primi15 = f"{lettere}{nascita.year % 100:02d}{MESI[nascita.month - 1]}{giorno:02d}{comune}"
    return primi15 + carattere_controllo(primi15)
