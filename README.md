# SampLog Parser

A web app for parsing and exporting sample logs from **Hach AS950** portable autosamplers.

**Live at: [brookssj.pythonanywhere.com](https://brookssj.pythonanywhere.com)**

---

## How to Use the Web App

### Step 1 — Download data from the sampler

Follow the steps in the [Downloading Data](#downloading-data-from-the-sampler) section below to export data from each sampler onto a USB flash drive.

Copy the `Data/` folder from the flash drive to your computer. If you have data from multiple samplers or previous downloads, merge them all into one `Data/` folder with this structure:

```
Data/
├── 203250017534/        ← sampler serial number
│   ├── 829175370/       ← Unix timestamp of download
│   │   └── SampLog.bin
│   └── 829754326/
│       └── SampLog.bin
├── 203280017535/
│   └── ...
└── 203280017536/
    └── ...
```

### Step 2 — Open the web app

Go to **[brookssj.pythonanywhere.com](https://brookssj.pythonanywhere.com)**.

### Step 3 — Upload the Data folder

Click **"Click to select your Data/ folder"** and select the `Data/` folder on your computer. The app will find all `SampLog.bin` files inside automatically — you don't need to zip anything.

Choose whether to include only the **most recent download** from each sampler, or **all downloads**.

Click **Parse & View**.

### Step 4 — View and download results

The results page shows each sampler with:
- A summary of total samples, successes, and failures
- A visual pass/fail sequence (✓ = collected, ✗ = missed/failed)
- A **Copy** button to copy the sequence as a tab-separated string of 1s and 0s
- A **Show detail table** button for the full log with timestamps and event types

Use the **Download CSV** or **Download JSON** buttons at the top to export the data.

---

## Sample Results

| Result | Description |
|---|---|
| `Success` | Sample collected successfully |
| `Missed Sample` | Sample not collected, no specific reason recorded |
| `Rinse Error` | Error during rinse cycle |
| `Purge Fail` | Purge cycle failed |
| `Pump Fault` | Pump hardware fault |
| `Pump Low Volt` | Pump voltage too low |
| `Sample Timeout` | Sample collection timed out |
| `User Abort` | Sample aborted by user |
| `Arm Faulty` | Distributor arm fault |
| `Lapse Error` | Lapse timing error |
| `Bottle Full` | Bottle full, sample not collected |

---

## CSV Format

```
Serial Number, Name, Export, 1, 2, 3, ... 36
203250017534, Alvin, 829754326, 1, 1, 1, 0, ...
```

Each column after **Export** is a sample slot — `1` for success, `0` for missed or failed.

---

## Sampler Names

Serial numbers are mapped to names in `app.py`. Update this if your samplers have different serial numbers:

```python
SAMPLER_NAMES = {
    "203250017534": "Alvin",
    "203280017535": "Simon",
    "203280017536": "Theo"
}
```

---

## Command-Line Tool

A command-line version (`samplog.py`) is also available for advanced use. See the usage instructions below.

### Requirements

- Python 3.6 or later

### Usage

```bash
python3 samplog.py -d /path/to/Data -f csv
```

| Argument | Options | Default | Description |
|---|---|---|---|
| `-d`, `--directory` | path | — | Path to the Data folder |
| `-c`, `--choose` | — | — | Open a folder picker dialog |
| `-f`, `--format` | `print` `csv` `json` | `print` | Output format |
| `-e`, `--exports` | `recent` `all` | `recent` | Use only the most recent download, or all |
| `-o`, `--output` | filename | `out.csv` / `out.json` | Output filename |

---

## Downloading Data from the Sampler

You will need a USB flash drive for each download.

1. **Open the menu** — press the **Menu** button on the front of the sampler.

2. **Navigate to Export / Import** — use the arrow keys to highlight **Export / Import** and press **Select**.

   ![Menu screen showing Export / Import option](images/IMG_3024.jpeg)

3. **Connect the flash drive** — the sampler will prompt you to connect a flash drive to the USB port and press **Next**. Insert the flash drive into the USB port on the side of the unit and press **Next**.

   ![Prompt to connect flash drive](images/IMG_3025.jpeg)

   ![USB port on the side of the sampler](images/IMG_3023.jpeg)

4. **Wait for detection** — the sampler will detect the flash drive. Do not remove it during this process.

   ![Detecting USB flash drive screen](images/IMG_3026.jpeg)

5. **Select Export Data** — from the Export / Import menu, highlight **Export Data** and press **Select**.

   ![Export / Import menu with Export Data highlighted](images/IMG_3027.jpeg)

6. **Export completes** — once finished, the screen will show **Export Success** along with the transfer size and time elapsed. Press **OK** and remove the flash drive.

   ![Export Success screen](images/IMG_3022.jpeg)

On the flash drive, the exported files will be located at `AS950/Data/`. The `Data/` folder contains a subfolder named with the sampler's serial number, and inside that a subfolder named with the Unix timestamp of the download. Copy the `Data/` folder from the flash drive to your computer, merging with any existing data.

