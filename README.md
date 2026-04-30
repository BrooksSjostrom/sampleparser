# samplog.py

A command-line tool for parsing and exporting sample logs from **Hach AS950** portable autosamplers.

---

## Requirements

- Python 3.6 or later — install from [python.org](https://www.python.org/downloads/) (**do not use the system Python on macOS**)

> **macOS users:** Run this script inside a conda environment or using a Python.org installation. The system Python shipped with macOS has an incompatible Tcl/Tk version that will cause a tkinter error.

---

## Data Folder Structure

The script expects a folder structure like the one the AS950 software creates when downloading data:

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

Point the script at the top-level `Data/` folder using `-d` or `-c`.

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

---

## Usage

```bash
python3 samplog.py -d /path/to/Data -f csv
```

### Arguments

| Argument | Options | Default | Description |
|---|---|---|---|
| `-d`, `--directory` | path | — | Path to the Data folder |
| `-c`, `--choose` | — | — | Open a folder picker dialog |
| `-f`, `--format` | `print` `csv` `json` `xlsx` | `print` | Output format |
| `-e`, `--exports` | `recent` `all` | `recent` | Use only the most recent download, or all downloads |
| `-o`, `--output` | filename | `out.csv` / `out.json` | Output filename (csv and json only) |

> Either `-d` or `-c` is required.

### Examples

Print results to the terminal:
```bash
python3 samplog.py -d ~/Downloads/Data
```

Export the most recent download from each sampler to CSV:
```bash
python3 samplog.py -d ~/Downloads/Data -f csv -o results.csv
```

Export all downloads from all samplers to JSON:
```bash
python3 samplog.py -d ~/Downloads/Data -f json -e all -o results.json
```

Use the folder picker to select the Data folder:
```bash
python3 samplog.py -c -f csv
```

---

## Output

Each sample is recorded as a `1` (success) or `0` (missed/failed). In CSV and JSON output, the full result name is also included.

### Sample results

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

### CSV format

```
Serial number, Name, Export, 1, 2, 3, ... 36
203250017534, Alvin, 829754326, 1, 1, 1, 0, ...
```

---

## Sampler Names

The serial numbers are mapped to names in the `SAMPLER_NAMES` dictionary at the top of the script. Update this if your samplers have different serial numbers or names:

```python
SAMPLER_NAMES = {
    "203250017534": "Alvin",
    "203280017535": "Simon",
    "203280017536": "Theo"
}
```
