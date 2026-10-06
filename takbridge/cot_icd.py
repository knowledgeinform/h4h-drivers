import pytak
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from uuid import uuid4


class BaseXMLGenerator:
    def __init__(self, data, uid=None, how=None, event_type=None, stale_in=10):
        self.data = data
        self.uid = uid or str(uuid4())
        self.how = how or "m-g"
        self.event_type = event_type
        self.stale_in = stale_in

        self.root = ET.Element(self.get_root_element())
        self._common_event_attributes()

    def _common_event_attributes(self):
        self.root.set("version", "2.0")
        self.root.set("uid", self.uid)
        self.root.set("type", self.event_type)
        self.root.set("how", self.how)
        self.root.set("time", pytak.cot_time())
        self.root.set("start", pytak.cot_time())
        self.root.set("stale", pytak.cot_time(self.stale_in))

    def get_root_element(self):
        raise NotImplementedError("Subclasses must define the root element")

    def generate_xml(self):
        xml_str = ET.tostring(self.root, encoding="utf-8").decode("utf-8")
        return self.add_xml_declaration(xml_str)

    def add_xml_declaration(self, xml_string):
        return f'<?xml version="1.0" encoding="UTF-8"?>\n{xml_string}'

    def format_time(self, seconds_from_now=0):
        now = datetime.utcnow() + timedelta(seconds=seconds_from_now)
        return now.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'


class ContactCoT(BaseXMLGenerator):
    def __init__(self, data, callsign=None, platform=None, effector=None, priority=0, task_complete="Unknown", target_status=""):
        self.callsign = callsign or "Unknown"
        self.platform = platform or "Null"
        self.effector = effector or "Null"
        self.priority = str(priority)
        self.task_complete = task_complete
        self.target_status = target_status

        super().__init__(
            data=data,
            uid=str(uuid4()),
            how="m-g",
            event_type="a-h-G-U-S-X-O",
            stale_in=100
        )

    def get_root_element(self):
        return "event"

    def _add_point(self):
        pt_attr = {
            "lat": str(self.data["latitude"]),
            "lon": str(self.data["longitude"]),
            "hae": str(self.data["altitude"]),
            "le": "10",
            "ce": "10"
        }
        ET.SubElement(self.root, "point", attrib=pt_attr)

    def _add_details(self):
        detail = ET.SubElement(self.root, "detail")
        ET.SubElement(detail, "contact", attrib={"callsign": self.callsign})
        ET.SubElement(detail, "link", attrib={
            "how": self.how,
            "uid": self.uid,
            "type": self.event_type,
            "callsign": self.callsign,
            "relation": "self"
        })
        ET.SubElement(detail, "remarks", attrib={
            "Platform": self.platform,
            "Effector": self.effector,
            "Priority": self.priority,
            "TaskComplete": self.task_complete,
            "TargetStatus": self.target_status
        })

    def generate_event(self):
        self._add_point()
        self._add_details()
        return self.generate_xml()

import re
import random
class UVPCoT(BaseXMLGenerator):
    def __init__(self, data, update_interval=120):
        self.data = data
        self.callsign = self.validate_callsign(data.get("callsign", ""))
        self.speed = data.get("speed", 0.0)
        self.course = data.get("course", 0.0)
        self.update_interval = update_interval
        self.stale_in = update_interval + 60
        
        uid = data.get("uid")
        if not uid:
            raise ValueError("UVPCoT requires a UID in input data.")
        
        domain = data.get("domain", "ground").lower() 
        if domain == "aerial":
            # list of type names
            possible_cot_types = ["a-f-A-M-H-Q-pdw", "a-f-A-M-H-Q-nib"]
            # choose one random
            cot_type = random.choice(possible_cot_types) 
        else:
            cot_type = "a-f-G-E-V" # UGV
            
    
        super().__init__(
            data=data,
            uid=uid,
            how=data.get("how", "m-g"),
            event_type=cot_type,
            stale_in=self.stale_in
        )
    
    def get_root_element(self):
        return "event"
    
        
    def validate_callsign(self, callsign):
        # pattern = r"^(Husky|V60|GraySeeker|MRZR|C100|MTRS|Traxxas|HarrisT7\d{3})$"
        # norm = callsign.lower()
        # if re.match(pattern, norm):
        #     return f"RLAC_{norm}"
        # return None
        return callsign
            
            
    def add_point(self):
        pt_attr = {
            "lat": str(self.data.get("latitude", "")),
            "lon": str(self.data.get("longitude", "")),
            "hae": str(self.data.get("altitude", "")),
            "ce": str(self.data.get("ce", "")),
            "le": str(self.data.get("le", "")),
        }
        ET.SubElement(self.root, "point", attrib=pt_attr)
        
    def add_detail(self):
        detail = ET.SubElement(self.root, 'detail')
        
        ET.SubElement(detail, "contact", {
            "callsign": self.callsign or "UNKNOWN"

        })
        
        ET.SubElement(detail, "track", {
            "speed": str(self.speed),
            "course": str(self.course)
        })
        
    def get_update_interval(self):
        return self.update_interval
    
    def get_stale_time(self):
        return self.stale_in
    
    def gen_cot(self):
        self.add_point()
        self.add_detail()
        return self.generate_xml()

   
class ZoneCoT(BaseXMLGenerator):
    zone_points = {}
    
    def __init__(self, uid, platform_name="Unknown", zone_type="Surney"):
        self.uid = uid
        self.platforn_name = platform_name
        self.zone_type = zone_type
        self.ce = "10"
        self.le = "10"
        self.alt = 0.0
        
        if uid not in ZoneCoT.zone_points:
            ZoneCoT.zone_points[uid] = []
            
        self.remark_text = f"ZoneType: {self.zone_type} Platform: {self.platforn_name}"
        super().__init__(uid=uid, event_type="u-d-f", how="-", stale_in=86400)
        
    def add_point(self):
        points = ZoneCoT.zone_points[self.uid]
        if points:
            lat, lon = points[0]
            super().add_point(lat, lon, hae=self.alt, ce=self.ce, le=self.le)
            
    def add_detail(self):
        detail = ET.SubElement(self.root, "detail")
        
        ET.SubElement(detail, "fillColor", {"value": "-2147483136"})
        ET.SubElement(detail, "strokeColor", {"value": "-256"})
        ET.SubElement(detail, "strokeWeight", {"value": "4.0"})

        remark = ET.SubElement(detail, "remark")
        remark.text = self.remark_text
        
        points = ZoneCoT.zone_points[self.uid]
        if points and points[0] != points[-1]:
            points.append(points[0])
            
        for lat, lon in points:
            ET.SubElement(detail, "link", {"point": f"{lat}, {lon}"})