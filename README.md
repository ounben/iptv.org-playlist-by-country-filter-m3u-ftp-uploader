# iptv.org-playlist-by-country-filter-m3u

An automated script (available in both PowerShell and Python) that fetches country-specific M3U playlists from the `iptv-org` repository, filters and consolidates the entries, groups them by country name using the `group-title` attribute, and automatically uploads the customized playlist to an FTP server.

## Features

* **Automated Parsing:** Downloads M3U lists for defined country codes via HTTP requests.
* **Dynamic Country Grouping:** Removes existing groups and overwrites them with the clear name of the respective country, allowing IPTV players to properly sort channels into country categories.
* **Alphabetical Sorting:** Processing and output are pre-sorted according to the real country names (A-Z).
* **In-Memory Processing:** Assembles the list directly in memory without writing temporary local files before upload.
* **Automated Deployment Interface:** Uploads the generated file directly to the web server via FTP.

## Prerequisites

### For PowerShell
* **Operating System:** Windows 10 / Windows 11 or Windows Server
* **Runtime Environment:** PowerShell 5.1 or PowerShell Core (7.x)

### For Python
* **Runtime Environment:** Python 3.x
* **Dependencies:** `requests` library

## Configuration

Adjustments to your environment are made directly in the header section of the respective script under the config block:

| Variable (PS / Python) | Description | Example |
| :--- | :--- | :--- |
| `$ftpServer` / `FTP_SERVER` | The URL/Host of your FTP server (without protocol prefix for Python). | `"server.com"` |
| `$ftpUser` / `FTP_USER` | The username for FTP access. | `"ftpuser"` |
| `$ftpPassword` / `FTP_PASSWORD` | The password for FTP access. | `"passwortn"` |
| `$domainUrl` / `DOMAIN_URL` | The public HTTP URL where the M3U will be accessible later. | `"https://webseite.com/m3u"` |

### Changing Supported Countries

The countries to be loaded are stored in the `$countries` / `COUNTRIES` hashtable/dictionary. You can add or remove ISO two-letter codes as needed:

    # PowerShell
    $countries = @{ "dz" = "Algerien"; "tn" = "Tunesien" }

    # Python
    COUNTRIES = { "dz": "Algerien", "tn": "Tunesien" }

## How the Script Works

1. **Sorting:** The script sorts the keys alphabetically based on the assigned country names.
2. **Download:** For each country, the corresponding M3U file is loaded sequentially from `iptv-org.github.io`.
3. **Cleanup & Grouping:** Each line with the `#EXTINF` tag is analyzed using regular expressions, old group assignments are deleted, and the new `group-title="Country"` attribute is injected so your IPTV player can generate proper country categories.
4. **Upload:** The entire string is converted into a byte array and pushed to the server as `arab_tv.m3u` via FTP.

## Usage

### Option 1: Running the PowerShell Script
1. Open the PowerShell console.
2. Navigate to the directory containing the script.
3. Execute the script:

    .\generate_iptv_list.ps1

### Option 2: Running the Python Script
1. Open your terminal or command prompt.
2. Install dependencies if not already present:

    pip install requests

3. Navigate to the directory containing the script.
4. Execute the script:

    python generate_iptv_list.py

## Important Notes

* **Error Handling:** Failed HTTP downloads of individual country lists are silently skipped during the current processing cycle to avoid blocking the overall process.
* **Security:** In production environments, it is ideal not to store credentials in plain text. Instead, use environment variables or encrypted configuration storage.
