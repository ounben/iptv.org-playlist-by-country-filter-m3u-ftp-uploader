import re
from io import BytesIO
from ftplib import FTP
import requests

# --- CONFIG ---
FTP_SERVER   = "server.com"  # Nur Domain oder IP, ohne ftp://
FTP_USER     = "ftpuser"
FTP_PASSWORD = "passwortn"
DOMAIN_URL   = "https://webseite.com/m3u"
FILE_NAME    = "arab_tv.m3u"
# --------------

COUNTRIES = {
    "dz": "Algerien", "tn": "Tunesien", "eg": "Aegypten", "ma": "Marokko",
    "ly": "Libyen", "sd": "Sudan", "sy": "Syrien", "lb": "Libanon",
    "jo": "Jordanien", "iq": "Irak", "kw": "Kuwait", "sa": "Saudi-Arabien",
    "qa": "Katar", "ae": "Vereinigte Arabische Emirate", "om": "Oman",
    "ye": "Jemen", "bh": "Bahrain", "ps": "Palaestina", "dj": "Dschibuti",
    "mr": "Mauretanien", "so": "Somalia", "km": "Komoren"
}

print("Erstelle IPTV-Liste im Speicher (alphabetisch sortiert)...")

# M3U im Arbeitsspeicher via Listen-Akkumulation aufbauen
m3u_lines = ["#EXTM3U"]

# Sortierung nach echten Ländernamen (A-Z)
sorted_countries = sorted(COUNTRIES.items(), key=lambda item: item[1])

for code, land in sorted_countries:
    url = f"https://iptv-org.github.io/iptv/countries/{code.lower()}.m3u"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            continue
            
        content = response.text
        lines = content.splitlines()
        
        for i in range(len(lines)):
            line = lines[i].strip()
            
            if line.startswith("#EXTINF:"):
                # Entfernt group-title="..." und normalisiert Whitespaces
                current_line = re.sub(r'group-title="[^"]*"', '', line)
                current_line = re.sub(r'\s+', ' ', current_line)
                
                # RegEx extrahiert die ID/Attribute und den Sendernamen am Ende nach dem letzten Komma vor dem Namen
                match = re.match(r'^#EXTINF:\s*(-?\d+)(.*),(.*)$', current_line)
                if match:
                    tvg_data = match.group(2).strip()
                    channel_name = match.group(3).strip()
                    
                    # Generiert das neue standardisierte Format
                    m3u_lines.append(f'#EXTINF:-1 group-title="{land}" {tvg_data},{channel_name}')
                else:
                    # Fallback, falls das Format unerwartet abweicht
                    m3u_lines.append(f'#EXTINF:-1 group-title="{land}",{line}')
                
                # Stream-URL der nächsten Zeile hinzufügen, falls vorhanden
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line and not next_line.startswith("#"):
                        m3u_lines.append(next_line)
                        
    except requests.RequestException:
        # Fehler beim Download einzelner Länder werden wie im Original ignoriert
        pass

# Finale Liste zusammenführen
final_m3u = "\n".join(m3u_lines)

# --- FTP UPLOAD ---
print("Verbinde mit FTP und lade hoch...")

try:
    # Konvertierung des Strings in ein Byte-Objekt für den Upload ohne lokale Datei
    file_bytes = final_m3u.encode('utf-8')
    bio = BytesIO(file_bytes)
    
    with FTP(FTP_SERVER) as ftp:
        ftp.login(user=FTP_USER, passwd=FTP_PASSWORD)
        # Upload im Binärmodus (storbinary)
        ftp.storbinary(f"STOR {FILE_NAME}", bio)
        
    print("Erfolgreich hochgeladen!")
    print("Deine M3U-URL für die App:")
    print(f"{DOMAIN_URL}/{FILE_NAME}")

except Exception as e:
    print(f"FTP-Upload fehlgeschlagen: {e}")
