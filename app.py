import io
import os
import re
import csv
import json
import struct
import tempfile
from datetime import datetime, timedelta

from flask import Flask, render_template, request, send_file, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "samplog-brookssj-2024"

SAMPLER_NAMES = {
    "203250017534": "Alvin",
    "203280017535": "Simon",
    "203280017536": "Theo"
}
EPOCH = datetime(2000, 1, 1)


def parse_file(data: bytes) -> list:
    event_types = []
    i = 0x12
    while i < len(data):
        end = data.find(b'\x00', i)
        if end == -1:
            break
        s = data[i:end].decode('latin-1', errors='replace')
        if not s or not all(c.isprintable() or c == ' ' for c in s):
            break
        event_types.append(s)
        i = end + 1

    positions = [m.start() for m in re.finditer(re.escape(b'\xaa\xaa'), data)]
    records = []
    for idx, pos in enumerate(positions):
        rec = data[pos:pos + 16]
        ts = struct.unpack('<I', rec[2:6])[0]
        dt = EPOCH + timedelta(seconds=ts)
        seq = struct.unpack('>H', rec[6:8])[0]
        evt_idx = rec[8]
        b9, b10 = rec[9], rec[10]
        if evt_idx != 0:
            evt_name = event_types[evt_idx] if evt_idx < len(event_types) else f"UNKNOWN_{evt_idx}"
        elif b9 == 0x01 and b10 == 0x00:
            evt_name = 'Success'
        elif 0 < b10 < len(event_types):
            evt_name = event_types[b10]
        else:
            evt_name = 'Missed Sample'
        program = b9
        bottle = rec[11]
        volume = rec[12]
        checksum = struct.unpack('<H', rec[14:16])[0]
        records.append({
            "number": idx + 1,
            "date": dt.strftime("%Y-%m-%d"),
            "time": dt.strftime("%I:%M %p"),
            "sample_number": seq,
            "result": evt_name,
            "category": cat_style(evt_name)[0],
            "bg": cat_style(evt_name)[1],
            "fg": cat_style(evt_name)[2],
            "program": program,
            "bottle": bottle,
            "volume": volume,
            "checksum": checksum,
        })
    return records


def cat_style(evt_name):
    if evt_name == 'Success':
        return 'Successful Sample', 'E2EFDA', '375623'
    elif evt_name == 'Bottle Full':
        return 'Bottle Status', 'DDEBF7', '1F4E79'
    elif evt_name != 'Other':
        return 'Missed Sample', 'FFC7CE', 'C00000'
    else:
        return 'Other', 'F2F2F2', '595959'


def parse_uploaded_files(files, exports_mode: str = "recent") -> dict:
    """Parse a list of werkzeug FileStorage objects uploaded via webkitdirectory."""
    combined = {}
    for f in files:
        # f.filename contains the relative path, e.g. Data/203250017534/829175370/SampLog.bin
        if not f.filename.endswith("SampLog.bin"):
            continue
        parts = [p for p in f.filename.replace("\\", "/").split("/") if p and not p.startswith(".")]
        # Expected: .../<serial>/<timestamp>/SampLog.bin
        if len(parts) < 3:
            continue
        device = parts[-3]
        export = parts[-2]
        combined.setdefault(device, {})[export] = parse_file(f.read())

    if exports_mode == "recent":
        for device in combined:
            if combined[device]:
                latest = max(combined[device].keys())
                combined[device] = {latest: combined[device][latest]}

    return combined


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/parse", methods=["POST"])
def parse():
    files = request.files.getlist("datafiles")
    exports_mode = request.form.get("exports", "recent")
    if not files or not any(f.filename for f in files):
        return render_template("index.html", error="Please select a Data folder.")

    try:
        combined = parse_uploaded_files(files, exports_mode)
    except Exception as e:
        return render_template("index.html", error=f"Failed to parse files: {e}")

    if not combined:
        return render_template("index.html", error="No SampLog.bin files found in the selected folder.")

    # Store parsed data in session via a temp file (data can be large for session cookie)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
    tmp.write(json.dumps(combined).encode())
    tmp.close()
    session["data_path"] = tmp.name
    session["exports_mode"] = exports_mode

    return redirect(url_for("results"))


@app.route("/results")
def results():
    data_path = session.get("data_path")
    if not data_path or not os.path.exists(data_path):
        return redirect(url_for("index"))
    with open(data_path) as f:
        combined = json.load(f)

    # Build display structure: list of (device, name, export, timestamp_label, records, summary)
    devices_data = []
    for device, exports in combined.items():
        name = SAMPLER_NAMES.get(device, device)
        for export, records in exports.items():
            try:
                ts_label = (EPOCH + timedelta(seconds=int(export))).strftime("%Y-%m-%d %I:%M:%S %p")
            except Exception:
                ts_label = export
            success = sum(1 for r in records if r["result"] == "Success")
            missed = len(records) - success
            summary = {"total": len(records), "success": success, "missed": missed}
            devices_data.append({
                "device": device,
                "name": name,
                "export": export,
                "ts_label": ts_label,
                "records": records,
                "summary": summary,
            })

    return render_template("results.html", devices_data=devices_data)


@app.route("/download/<fmt>")
def download(fmt):
    data_path = session.get("data_path")
    if not data_path or not os.path.exists(data_path):
        return redirect(url_for("index"))
    with open(data_path) as f:
        combined = json.load(f)

    if fmt == "json":
        out = io.BytesIO(json.dumps(combined, indent=4).encode())
        return send_file(out, mimetype="application/json", as_attachment=True, download_name="samplog.json")

    elif fmt == "csv":
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["Serial Number", "Name", "Export"] + [str(x) for x in range(1, 37)])
        for device, exports in combined.items():
            name = SAMPLER_NAMES.get(device, device)
            for export, records in exports.items():
                row = [device, name, export] + ["1" if r["result"] == "Success" else "0" for r in records]
                writer.writerow(row)
        out = io.BytesIO(buf.getvalue().encode())
        return send_file(out, mimetype="text/csv", as_attachment=True, download_name="samplog.csv")

    return redirect(url_for("results"))


if __name__ == "__main__":
    app.run(debug=True)
