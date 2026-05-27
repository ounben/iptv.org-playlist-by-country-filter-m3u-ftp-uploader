# iptv.org-playlist-by-country-filter-m3u-ftp-uploader

An automated PowerShell script that fetches country-specific M3U playlists from the `iptv-org` repository, consolidates the entries, sorts them by country name, cleans up the group metadata (`group-title`), and automatically uploads the final playlist to an FTP server.

## Features

* **Automated Parsing:** Downloads M3U lists for defined country codes via HTTP request.
* **Dynamic Grouping:** Removes existing `group-title` attributes and overwrites them with the clear name of the respective country.
* **Alphabetical Sorting:** Processing and output are pre-sorted according to the real country names (A-Z).
* **In-Memory Processing:** Utilizes the .NET `StringBuilder` for high-performance assembly of the list in memory without writing temporary local files.
* **Automated Deployment Interface:** Uploads the generated file directly to the web server via FTP upload.

## Prerequisites

* **Operating System:** Windows 10 / Windows 11 or Windows Server
* **Runtime Environment:** PowerShell 5.1 or PowerShell Core (7.x)
* **Network:** Allowed outbound port 21 (FTP) and port 443 (HTTPS)

## Configuration

Adjustments to your environment are made directly in the header section of the script under `# --- CONFIG ---`:

| Variable | Description | Example |
| :--- | :--- | :--- |
| `$ftpServer` | The URL of your FTP server (without trailing slash). | `"ftp://server.com"` |
| `$ftpUser` | The username for FTP access. | `"ftpuser"` |
| `$ftpPassword` | The password for FTP access. | `"passwortn"` |
| `$domainUrl` | The public HTTP URL where the M3U will be accessible later. | `"https://webseite.com/m3u"` |

### Changing Supported Countries

The countries to be loaded are stored in the `$countries` hashtable. You can add or remove ISO two-letter codes as needed:

    $countries = @{
        "dz" = "Algerien"
        "tn" = "Tunesien"
        # Add more countries here
    }

## How the Script Works

1. **Sorting:** The script sorts the keys of the hashtable alphabetically based on the assigned country names.
2. **Download:** For each country, the corresponding M3U file is loaded sequentially from `iptv-org.github.io`.
3. **Cleanup:** Each line with the `#EXTINF` tag is analyzed using regular expressions, old group assignments are deleted, and the new `group-title="Country"` attribute is injected.
4. **Upload:** The entire string is converted into a UTF-8 byte array and pushed to the server as `arab_tv.m3u` via `FtpWebRequest`.

## Usage

1. Open the PowerShell console.
2. Navigate to the directory containing the script.
3. Execute the script:

    .\generate_iptv_list.ps1

## Important Notes

* **Error Handling:** Failed HTTP downloads of individual country lists are silently skipped during the current processing cycle to avoid blocking the overall process.
* **Security:** In production environments, it is ideal not to store credentials in plain text. Instead, use encrypted CLIXML files or environment variables.
