# --- CONFIG ---
$ftpServer   = "ftp://server.com"
$ftpUser     = "ftpuser"
$ftpPassword = "passwortn"
$domainUrl   = "https://webseite.com/m3u"
# --------------

$countries = @{
    "dz" = "Algerien"; "tn" = "Tunesien"; "eg" = "Aegypten"; "ma" = "Marokko"
    "ly" = "Libyen"; "sd" = "Sudan"; "sy" = "Syrien"; "lb" = "Libanon"
    "jo" = "Jordanien"; "iq" = "Irak"; "kw" = "Kuwait"; "sa" = "Saudi-Arabien"
    "qa" = "Katar"; "ae" = "Vereinigte Arabische Emirate"; "om" = "Oman"
    "ye" = "Jemen"; "bh" = "Bahrain"; "ps" = "Palaestina"; "dj" = "Dschibuti"
    "mr" = "Mauretanien"; "so" = "Somalia"; "km" = "Komoren"
}

Write-Host "Erstelle IPTV-Liste im Speicher (alphabetisch sortiert)..." -ForegroundColor Cyan

# M3U im Arbeitsspeicher aufbauen
$m3u = New-Object System.Text.StringBuilder
[void]$m3u.AppendLine("#EXTM3U")

# Sortierung nach echten Ländernamen (A-Z) vor der Verarbeitung
$countries.Keys | Sort-Object { $countries[$_] } | ForEach-Object {
    $code = $_
    $land = $countries[$code]
    $url = "https://iptv-org.github.io/iptv/countries/$code.m3u"
    
    try {
        $client = New-Object System.Net.WebClient
        $client.Encoding = [System.Text.Encoding]::UTF8
        $content = $client.DownloadString($url)
        $lines = $content -split "`n"
        
        for ($i = 0; $i -lt $lines.Count; $i++) {
            if ($lines[$i] -like "#EXTINF:*") {
                $currentLine = $lines[$i].Trim() -replace 'group-title="[^"]*"', '' -replace '\s+', ' '
                if ($currentLine -match '^#EXTINF:\s*(-?\d+)(.*)$') {
                    $restOfLine = $Matches[2].Trim() -replace '\s*,\s*', ','
                    $parts = $restOfLine -Split ','
                    [void]$m3u.AppendLine("#EXTINF:-1 group-title=`"$land`" $($parts[0]),$($parts[1])")
                }
                if ($i + 1 -lt $lines.Count) {
                    [void]$m3u.AppendLine($lines[$i + 1].Trim())
                }
            }
        }
    } catch {}
}

# --- FTP UPLOAD ---
Write-Host "Verbinde mit FTP und lade hoch..." -ForegroundColor Cyan

$fileName = "arab_tv.m3u"
$ftpUploadUrl = $ftpServer.TrimEnd('/') + "/" + $fileName
$bytes = [System.Text.Encoding]::UTF8.GetBytes($m3u.ToString())

try {
    $request = [System.Net.FtpWebRequest]::Create($ftpUploadUrl)
    $request.Credentials = New-Object System.Net.NetworkCredential($ftpUser, $ftpPassword)
    $request.Method = [System.Net.WebRequestMethods+Ftp]::UploadFile
    $request.ContentLength = $bytes.Length
    $request.UseBinary = $true
    $request.KeepAlive = $false

    $requestStream = $request.GetRequestStream()
    $requestStream.Write($bytes, 0, $bytes.Length)
    $requestStream.Close()
    $requestStream.Dispose()

    Write-Host "Erfolgreich hochgeladen!" -ForegroundColor Green
    Write-Host "Deine M3U-URL für die App:" -ForegroundColor Yellow
    Write-Host "$domainUrl/$fileName" -ForegroundColor Green
} catch {
    Write-Host "FTP-Upload fehlgeschlagen: $_" -ForegroundColor Red
}
