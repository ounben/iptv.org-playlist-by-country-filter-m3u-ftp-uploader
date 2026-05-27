import re
import urllib.request
import ftplib
from io import BytesIO

# --- CONFIG ---
FTP_SERVER   = "server.com"
FTP_USER     = "ftpuser"
FTP_PASSWORD = "passwortn"
DOMAIN_URL   = "https://webseite.com/m3u"
FILE_NAME    = "arab_tv.m3u"
# --------------

countries = {
    "dz": "Algerien", "tn": "Tunesien", "eg": "Aegypten", "ma": "Marokko",
    "ly": "Libyen", "sd": "Sudan", "sy": "Syrien", "lb": "Libanon",
    "jo": "Jordanien", "iq": "Irak", "kw": "Kuwait", "sa": "Saudi-Arabien",
    "qa": "Katar", "ae": "Vereinigte Arabische Emirate", "om": "Oman",
    "ye": "Jemen", "bh": "Bahrain", "ps": "Palaestina", "dj": "Dschibuti",
    "mr": "Mauretanien", "so": "Somalia", "km": "Komoren"
}

print("Erstelle IPTV-Liste im Speicher (alphabetisch sortiert)...")

m3u_lines = ["#EXTM3U"]

# Sortierung nach echten Ländernamen (A-Z)
sorted_country_codes = sorted(countries.keys(), key=lambda k: countries[k])

for code in sorted_country_codes:
    land = countries[code]
    url = f"https://iptv-org.github.io/iptv/countries/{code.m3u}"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            content = response.read().decode('utf-8')
            lines = content.splitlines()
            
            for i in range(len(lines)):
                line = lines[i].strip()
                if line.startswith("#EXTINF:"):
                    # Bereinige alte Gruppen und normalisiere doppelte Leerzeichen
                    current_line = re.sub(r'group-title="[^"]*"', '', line)
                    current_line = re.sub(r'\s+', ' ', current_line).strip()
                    
                    # RegEx: Trennt die Attribute vom Sendernamen am letzten Komma
                    match = re.match(r'^#EXTINF:\s*(-?\d+)(.*),(.*)$', current_line)
                    if match:
                        tvg_data = match.group(2).strip()
                        channel_name = match.group(3).strip()
                        
                        # VLC-optimierter Aufbau: "Land - " wird in den Namen injiziert
                        if tvg_data:
                            m3u_lines.append(f'#EXTINF:-1 group-title="{land}" {tvg_data},{land} - {channel_name}')
                        else:
                            m3u_lines.append(f'#EXTINF:-1 group-title="{land}",{land} - {channel_name}')
                    else:
                        # Fallback für abweichende Zeilenstrukturen (inkl. VLC-Fix)
                        m3u_lines.append(f'#EXTINF:-1 group-title="{land}",{land} - {current_line}')
                    
                    # Stream-URL der Folgezeile hinzufügen
                    if i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        if next_line and not next_line.startswith("#"):
                            m3u_lines.append(next_line)
                            
    except Exception:
        # Fehler beim Download einzelner Ländernamen stumm überspringen
        pass

# Zusammenfügen der Liste
final_m3u_string = "\n".join(m3u_lines) + "\n"

# --- FTP UPLOAD ---
print("Verbinde mit FTP und lade hoch...")

try:
    # FTP-Verbindung initialisieren
    ftp = ftplib.FTP(FTP_SERVER)
    ftp.login(user=FTP_USER, passwd=FTP_PASSWORD)
    
    # String in Bytes konvertieren für den Upload
    m3u_bytes = final_m3u_string.encode('utf-8')
    bio = BytesIO(m3u_bytes)
    
    # Datei hochladen
    ftp.storbinary(f'STOR {FILE_NAME}', bio)
    ftp.quit()
    
    print("Erfolgreich hochgeladen!")
    print("Deine M3U-URL für die App:")
    print(f"{DOMAIN_URL}/{FILE_NAME}")
    
except Exception as e:
    print(f"FTP-Upload fehlgeschlagen: {e}")
