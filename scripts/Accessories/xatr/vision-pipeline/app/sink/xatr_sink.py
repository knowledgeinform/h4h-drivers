# app/sink/xatr_sink.py
from __future__ import annotations
import json
import mats               # PyMATS import – assumes XATR_ROOT is set
import mats.cfg           # for loading an ATR configuration if needed

class XatrSink:
    """A sink that converts the YOLO JSON payload into MATS structures
    and calls the XATR core via PyMATS."""
    def __init__(self, cfg_path: str | None = None):
        """
        Parameters
        ----------
        cfg_path: str | None
            Path to an XATR *.atrcfg* file.  If None the default sensor
            configuration is used.
        """
        self.cfg_path = cfg_path
        if cfg_path:
            self.atr_cfg = mats.AtrConfig()
            self.atr_cfg.load(cfg_path)          # load the ATR configuration

    def _json_to_mats(self, payload: dict):
        """Translate the detection dictionary produced by the pipeline
        into a MATS_input object with a list of MATS_contact objects."""
        # -----------------------------------------------------------------
        # 1️⃣  Create the MATS input and fill basic sensor fields
        # -----------------------------------------------------------------
        inp = mats.MATS_input()
        inp.setSensor(payload.get("source_id", "YOLO_CAMERA"))
        inp.setTime(payload["timestamp_utc"])

        # -----------------------------------------------------------------
        # 2️⃣  Build a contact for every detection that YOLO returned
        # -----------------------------------------------------------------
        contacts = []
        for det in payload["detections"]:
            c = mats.MATS_contact()
            c.setClass(det["label"])
            c.setConfidence(float(det["confidence"]))

            # YOLO bbox = {x1, y1, x2, y2}.  XATR expects a centre + size.
            x_center = (det["bbox"]["x1"] + det["bbox"]["x2"]) / 2.0
            y_center = (det["bbox"]["y1"] + det["bbox"]["y2"]) / 2.0
            width   = det["bbox"]["x2"] - det["bbox"]["x1"]
            height  = det["bbox"]["y2"] - det["bbox"]["y1"]

            c.setLocation(x_center, y_center)
            c.setSize(width, height)
            contacts.append(c)

        inp.setContacts(contacts)
        return inp

    def publish(self, json_str: str) -> None:
        """Entry point used by the pipeline (same signature as the other sinks)."""
        # The pipeline currently sends a JSON string; convert it back to dict
        payload = json.loads(json_str)

        # Build the MATS structures
        mats_input = self._json_to_mats(payload)

        # Prepare the containers that will receive the results
        con = mats.MATS_contact_list()
        ecd = mats.MATS_ecdata_list()

        # -----------------------------------------------------------------
        # 3️⃣  Call the XATR core.  The simple form `mats.atr(input, con, ecd)`
        #     runs the ATR with the currently loaded configuration.
        # -----------------------------------------------------------------
        mats.atr(mats_input, con, ecd)

        # (Optional) print a short status line – you can replace this with
        # logging or whatever you need.
        print(f"XATR processed {len(con)} contacts (original {len(payload['detections'])})")