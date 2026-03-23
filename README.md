# 🤖 Discord Bot — Python (discord.py)

## 📁 Struktura projektu
```
discord-bot/
├── bot.py              # główny plik, uruchamiasz to
├── config.py           # TUTAJ ustawiasz ID kanałów, ról itd.
├── requirements.txt
├── .env                # token bota (NIE commituj tego!)
└── cogs/
    ├── moderacja.py    # kick, ban, mute, clear
    ├── powitanie.py    # welcome / leave
    ├── leveling.py     # XP, rangi, leaderboard
    ├── logi.py         # logi serwera
    ├── autoresponder.py
    ├── reaction_roles.py
    ├── weryfikacja.py
    ├── counting.py
    └── muzyka.py       # YouTube via yt-dlp
```

## 🚀 Instalacja

### 1. Wymagania
- Python 3.10+
- ffmpeg (do muzyki)

### 2. Zainstaluj zależności
```bash
pip install -r requirements.txt
```

### 3. Skonfiguruj token
```bash
cp .env.example .env
# edytuj .env i wklej swój token
```

### 4. Skonfiguruj config.py
Otwórz `config.py` i wypełnij ID kanałów i ról.

### 5. Uruchom
```bash
python bot.py
```

---

## ⚙️ Komendy Slash

| Komenda | Opis |
|---|---|
| `/kick` | Wyrzuca użytkownika |
| `/ban` | Banuje użytkownika |
| `/unban` | Odbanowuje po ID |
| `/mute` | Timeout (minuty) |
| `/unmute` | Zdejmuje timeout |
| `/clear` | Usuwa wiadomości |
| `/rank` | Sprawdź XP i poziom |
| `/leaderboard` | Top 10 serwera |
| `/rr_add` | Dodaj reaction role |
| `/rr_remove` | Usuń reaction role |
| `/weryfikacja_setup` | Wyślij panel weryfikacji |
| `/play` | Odtwórz muzykę z YT |
| `/skip` | Pomiń utwór |
| `/stop` | Zatrzymaj i rozłącz |
| `/queue` | Pokaż kolejkę |
| `/volume` | Zmień głośność |

---

## 📝 ffmpeg (muzyka)
- **Windows:** https://ffmpeg.org/download.html — dodaj do PATH
- **Linux:** `sudo apt install ffmpeg`
- **Mac:** `brew install ffmpeg`
