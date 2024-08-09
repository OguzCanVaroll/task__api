from flask import Blueprint, request, jsonify
from app.models import DailyCampaigns, DailyScores, db
from datetime import datetime

main = Blueprint('main', __name__)

# Veri doğrulama fonksiyonları
def is_valid_date(date_text):
    try:
        datetime.strptime(date_text, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def clean_input(input_string):
    return ''.join(char for char in input_string if char.isalnum() or char in "._- ")

@main.route('/campaign-data', methods=['POST'])
def get_campaign_data():
    data = request.get_json()
    campaign_id = clean_input(data.get('campaign_id', ''))
    start_date = data.get('start_date', '')
    end_date = data.get('end_date', '')


    if not (is_valid_date(start_date) and is_valid_date(end_date) and start_date <= end_date):
        return jsonify({"error": "Invalid or improperly formatted date range"}), 400
    

    campaign_query = db.session.query(DailyCampaigns).filter(DailyCampaigns.campaign_id == campaign_id)
    score_query = db.session.query(DailyScores).filter(DailyScores.campaign_id == campaign_id)


    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        campaign_query = campaign_query.filter(DailyCampaigns.date >= start_date)
        score_query = score_query.filter(DailyScores.date >= start_date)

    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        campaign_query = campaign_query.filter(DailyCampaigns.date <= end_date)
        score_query = score_query.filter(DailyScores.date <= end_date)

  
    campaign_data = campaign_query.all()
    score_data = score_query.all()

    result = merge_data(campaign_data, score_data, campaign_id, start_date, end_date)
    return jsonify(result)

def merge_data(campaign_data, score_data, campaign_id, start_date, end_date):
    data = {}
    for c in campaign_data:
        key = (c.campaign_id, c.date)
        if key not in data:
            data[key] = {
                "campaign_id": c.campaign_id,
                "campaign_name": c.campaign_name,
                "date": c.date,
                "views": c.views,
                "impressions": c.impressions,
                "cpm": c.cpm,
                "clicks": c.clicks,
                "effectiveness": 0.0,
                "media": 0.0,
                "creative": 0.0
            }

    for s in score_data:
        key = (s.campaign_id, s.date)
        if key in data:
            data[key].update({
                "media": s.media,
                "creative": s.creative,
                "effectiveness": s.effectiveness
            })

    sorted_data = sorted(data.values(), key=lambda x: x['date'])

    campaign_name = "All" if not campaign_id else sorted_data[0]['campaign_name']
    date_range = f"{start_date.strftime('%d %b')} - {end_date.strftime('%d %b')}"
    total_days = (end_date - start_date).days

    impressions_sum = sum(item['impressions'] for item in sorted_data)
    clicks_sum = sum(item['clicks'] for item in sorted_data)
    views_sum = sum(item['views'] for item in sorted_data)

    impressions_cpm = {str(item['date']): item['impressions'] for item in sorted_data}
    cpm_values = {str(item['date']): item['cpm'] for item in sorted_data}

    start_dates = [str(item['date']) for item in sorted_data]
    end_dates = start_dates[::-1]
    campaign_ids = list({item['campaign_id'] for item in sorted_data})
    campaign_names = list({item['campaign_name'] for item in sorted_data})
    effectiveness_scores = [item['effectiveness'] for item in sorted_data]
    media_scores = [item['media'] for item in sorted_data]
    creative_scores = [item['creative'] for item in sorted_data]

    response = {
        "campaignCard": {
            "campaignName": campaign_name,
            "range": date_range,
            "days": total_days
        },
        "performanceMetrics": {
            "currentMetrics": {
                "impressions": impressions_sum,
                "clicks": clicks_sum,
                "views": views_sum
            }
        },
        "volumeUnitCostTrend": {
            "impressionsCpm": {
                "impression": impressions_cpm,
                "cpm": cpm_values
            }
        },
        "campaignTable": {
            "start_date": start_dates,
            "end_date": end_dates,
            "adin_id": campaign_ids,
            "campaign": campaign_names,
            "effectiveness": effectiveness_scores,
            "media": media_scores,
            "creative": creative_scores
        }
    }
    return response
