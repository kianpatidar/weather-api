# models.py
from database import db
from datetime import datetime, timezone
 
#---------------------------------
#Task 1b — Create models.py
#--------------------------------- 
 
class Snapshot(db.Model):
    __tablename__ = 'snapshots'
 
    id             = db.Column(db.Integer, primary_key=True)
    fetched_at     = db.Column(db.DateTime, nullable=False)
    city           = db.Column(db.String(100), nullable=False)
    temperature_c  = db.Column(db.Float)
    wind_speed_kmh = db.Column(db.Float)
    weather_code   = db.Column(db.Integer)
    pm10           = db.Column(db.Float)
    pm2_5          = db.Column(db.Float)
    air_quality_index = db.Column(db.Integer)
 
    def to_dict(self):
        return {
            'id':                self.id,
            'fetched_at':        self.fetched_at.isoformat(),
            'city':              self.city,
            'temperature_c':     self.temperature_c,
            'wind_speed_kmh':    self.wind_speed_kmh,
            'weather_code':      self.weather_code,
            'pm10':              self.pm10,
            'pm2_5':             self.pm2_5,
            'air_quality_index': self.air_quality_index,
        }

