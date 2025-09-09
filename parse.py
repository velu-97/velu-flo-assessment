from nemreader import read_nem_file
from datetime import datetime, timezone
import pytz

def parse_nem12_file(file_path):
    readings = []
    
    try:
        nem_data = read_nem_file(file_path)
        
        if not hasattr(nem_data, 'readings'):
            return None, f"Invalid NEM file structure: {type(nem_data).__name__}"
        
        if not nem_data.readings:
            return readings, None
            
        for nmi in nem_data.readings:
            for suffix in nem_data.readings[nmi]:
                for reading in nem_data.readings[nmi][suffix]:
                    timestamp_utc = convert_to_utc(reading.t_start) #the db column does not retain local timestamp, so force utc
                    
                    readings.append((
                        nmi,
                        timestamp_utc,
                        reading.read_value
                    ))
                    
        return readings, None
        
    except AttributeError as e:
        return None, f"NEM file parsing error - missing attribute: {e}"
    except Exception as e:
        return None, str(e)

def convert_to_utc(timestamp):
    if timestamp.tzinfo is None:
        aest = pytz.timezone('Australia/Sydney') #im making the assumption here that NEM files only come from australia's energy sector
        localized = aest.localize(timestamp)
        return localized.astimezone(timezone.utc).replace(tzinfo=None)
    else:
        return timestamp.astimezone(timezone.utc).replace(tzinfo=None)