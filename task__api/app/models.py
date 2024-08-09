from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class DailyCampaigns(db.Model):
    __tablename__ = 'tbl_daily_campaigns'
    campaign_id = db.Column(db.String, primary_key=True)
    campaign_name = db.Column(db.String)
    date = db.Column(db.Date, primary_key=True)
    views = db.Column(db.Integer)
    impressions = db.Column(db.Integer)
    cpm = db.Column(db.Float)
    clicks = db.Column(db.Integer)

class DailyScores(db.Model):
    __tablename__ = 'tbl_daily_scores'
    campaign_id = db.Column(db.String, primary_key=True)
    date = db.Column(db.Date, primary_key=True)
    media = db.Column(db.Float)
    creative = db.Column(db.Float)
    effectiveness = db.Column(db.Float)
