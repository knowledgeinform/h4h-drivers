# Vision Pipeline

## Overview

This project implements a local vision processing pipeline that:

* Connects to a camera source (webcam, video file, or RTSP stream)
* Runs object detection (YOLO, XATR or external detector)
* Extracts detections
* Serializes detections into JSON
* Sends detections to a downstream framework (COT, TAK)

This pipeline is designed to run **fully offline** and integrate with the external runtime environment **XATR** provided by another development team.

---

## Architecture

```
Camera / RTSP
      ↓
Frame Source
      ↓
Detector (YOLO or external via XATR)
      ↓
Detection Mapping
      ↓
JSON Serialization
      ↓
Framework Sink
```

---

## External Dependency: XATR Runtime

IF you are using XATR, this must be deployed in the XATR runtime environment located at:

```
/opt/XATR
```

This environment provides:

* Compiled C/C++ libraries
* CUDA / TensorRT configuration
* Python modules (via PYTHONPATH)
* Executables and supporting assets

You **must use this environment as-is**. Do not modify its structure.

---

## Installation

### 1. Install XATR Runtime

Follow the instructions provided by the external team to install X at:

```
/opt/XATR
```

Verify the following exists:

```
/opt/XATR/
  bin/
  lib/
  include/
  python_modules/
  packages/Python/
  xatr.env
```

---

### 2. Set Up Python Environment

Create a virtual environment (recommended):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

---

### 3. Activate XATR Environment

Before running the pipeline, you must source the X environment:

```bash
source /opt/XATR/xatr.env
```

This sets:

* `LD_LIBRARY_PATH`
* `PYTHONPATH`
* CUDA / TensorRT paths

---

### 4. Add Vision Pipeline to PYTHONPATH

From the repo root:

```bash
export PYTHONPATH=$(pwd):$PYTHONPATH
```

---

## Running the Pipeline (Option 1)

Run the pipeline inside the X environment:

```bash
source /opt/XATR/xatr.env
export PYTHONPATH=$(pwd):$PYTHONPATH
python3 main.py
```

---

## Recommended Helper Script

To simplify usage, create:

```
scripts/run_with_xatr.sh
```

```bash
#!/usr/bin/env bash
set -e

source /opt/XATR/xatr.env
export PYTHONPATH=$(pwd):$PYTHONPATH

python3 main.py
```

Make executable:

```bash
chmod +x scripts/run_with_xatr.sh
```

Then run:

```bash
./scripts/run_with_xatr.sh
```

---

## Configuration

Configuration files are located in:

```
configs/
```

Example:

```yaml
source:
  type: rtsp
  value: rtsp://localhost:8554/mystream
  source_id: orin_rtsp_cam_01

model:
  path: models/yolo.pt
  confidence: 0.4
  classes_of_interest:
    - sports ball

sink:
  type: mock

runtime:
  display: false
```
---

## XATR Configuration

To import a specific model from a XATR configuration `.matscx` file and generate the required `.atrcfg`, `.cfg`, and `.names` files for loading the model into a XATR pipeline, first make sure make sure `/opt/XATR/` has write permissions in order to create cfg files. Source the XATR env `source /opt/XATR/xatr.env` and then simply call either

```
./mats_manager config import <path/to/xatr_cfg.matscx>
```

or

```
./mats_configuration_import <path/to/xatr_cfg.matscx>
```

If successful, this will output the required config files to `/opt/XATR/config`.

---

## RTSP Testing (Optional)

If using a local RTSP stream on the Orin:

```bash
ffprobe -rtsp_transport tcp rtsp://localhost:8554/mystream
```

---

## Development Notes

* Always run from the **repo root**
* Do not run Python from subdirectories
* Do not modify `/opt/XATR` structure
* Treat XATR as a **black-box runtime dependency**

---

## Troubleshooting

### Import Errors

Check:

```bash
echo $PYTHONPATH
python -c "import sys; print(sys.path)"
```

Ensure `/opt/XATR/python_modules` and `/opt/XATR/packages/Python` are present.

---

### Missing Libraries

Ensure:

```bash
echo $LD_LIBRARY_PATH
```

Includes:

```
/opt/XATR/lib
/usr/local/cuda/lib64
```

---

### RTSP Issues

Verify stream:

```bash
ffprobe -rtsp_transport tcp rtsp://<host>:8554/mystream
```

---

## Future Improvements

* Docker containerization for Orin deployment
* Replace mock sink with framework integration
* Add replay/test harness
* Convert external dependencies into installable packages (long-term)

---

## Summary

To run the system:

```bash
source /opt/XATR/xatr.env
export PYTHONPATH=$(pwd):$PYTHONPATH
python3 main.py
```

That’s it.
