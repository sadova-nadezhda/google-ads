from flask import Flask, render_template, request, send_file
from google.ads.googleads.client import GoogleAdsClient
import io
import openpyxl

app = Flask(__name__)

# City to Geo Target ID mapping

CITY_GEO_MAPPING = {
    "kazakhstan": 2398,          # Whole Kazakhstan
    "almaty": 9063099,          # Алматы
    "astana": 1009806,          # Астана
    "almaty_region": 9070290,   # Алматинская область
    "akmola_region": 9070289,   # Акмолинская область
    "shymkent": 1009809,        # Шымкент
    "taraz": 9063096,           # Тараз
    "aktobe": 9063098,          # Актобе
    "karaganda": 9063097,       # Караганда
    "pavlodar": 1009816,        # Павлодар
    "kyzylorda": 9063094,       # Кызылорда
    "uralsk": 1009815,          # Уральск
    "oskemen": 9063095,         # Оскемен
    "kostanay": 1009813,        # Костанай
    "semey": 1009818,           # Семей
    "taldykorgan": 9063093,     # Талдыкорган
    "aktau": 9198063,           # Актау
    "petropavl": 1009817,       # Петропавл
    "almaty_district": 9195897  # Алматинский район
}


@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    error = None
    
    if request.method == "POST":
        keywords_input = request.form["keywords"]
        city = request.form.get("city", "kazakhstan")  # Default to Kazakhstan if not selected
        keywords = [line.strip() for line in keywords_input.splitlines() if line.strip()]
        
        if keywords:
            try:
                client = GoogleAdsClient.load_from_storage("google-ads.yaml")
                service = client.get_service("KeywordPlanIdeaService")
                keyword_seed = client.get_type("KeywordSeed")
                keyword_seed.keywords.extend(keywords)

                request_obj = client.get_type("GenerateKeywordIdeasRequest")
                request_obj.customer_id = "3567164007"  # Replace with your actual Customer ID
                request_obj.keyword_seed = keyword_seed

                # Set language (English)
                language_service = client.get_service("GoogleAdsService")
                request_obj.language = language_service.language_constant_path(1031)
                
                # Set geo target based on selected city
                geo_id = CITY_GEO_MAPPING.get(city, 2398)  # Default to Kazakhstan
                geo_service = client.get_service("GeoTargetConstantService")
                request_obj.geo_target_constants.append(
                    geo_service.geo_target_constant_path(geo_id)
                )
                response = service.generate_keyword_ideas(request=request_obj)

                for idea in response:
                    metrics = idea.keyword_idea_metrics
                    results.append({
                        "text": idea.text,
                        "avg_monthly_searches": metrics.avg_monthly_searches,
                        "competition": metrics.competition.name,
                        "low_bid": round(metrics.low_top_of_page_bid_micros / 1_000_000, 2),
                        "high_bid": round(metrics.high_top_of_page_bid_micros / 1_000_000, 2)
                    })

                if "download" in request.form:
                    wb = openpyxl.Workbook()
                    ws = wb.active
                    ws.append(["Ключевое слово", "Показов/мес", "Конкуренция", "Ставка (низкая)", "Ставка (высокая)"])
                    for row in results:
                        ws.append([
                            row["text"], 
                            row["avg_monthly_searches"], 
                            row["competition"], 
                            row["low_bid"], 
                            row["high_bid"]
                        ])
                    buffer = io.BytesIO()
                    wb.save(buffer)
                    buffer.seek(0)
                    return send_file(
                        buffer, 
                        as_attachment=True, 
                        download_name="keywords.xlsx", 
                        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

            except Exception as e:
                error = str(e)

    return render_template("index.html", results=results, error=error)

if __name__ == "__main__":
    app.run(debug=True)