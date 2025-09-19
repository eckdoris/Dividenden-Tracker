import yfinance as yf
from datetime import datetime, timedelta

def get_dividends(symbol):
    """
    Holt die Dividendenzahlungen der letzten 12 Monate für ein Symbol.
    Entfernt Zeitzonen aus dem Index, damit Vergleiche fehlerfrei laufen.
    """
    try:
        stock = yf.Ticker(symbol)
        dividends = stock.dividends

        # Debug: falls keine Dividenden vorhanden
        if dividends.empty:
            return []

        # Zeitzone entfernen, falls vorhanden
        if dividends.index.tz is not None:
            dividends.index = dividends.index.tz_localize(None)

        # Filter: nur die letzten 12 Monate
        one_year_ago = datetime.now() - timedelta(days=365)
        dividends = dividends[dividends.index >= one_year_ago]

        # Rückgabe als Liste von (Datum, Betrag)
        return list(dividends.items())

    except Exception as e:
        print(f"⚠️ Fehler bei {symbol}: {e}")
        return []
