import os
from dotenv import load_dotenv
from jinja2 import Template

load_dotenv()

with open("google-ads.yaml.j2") as f:
    template = Template(f.read())

rendered = template.render(
    GOOGLE_CLIENT_ID=os.environ["GOOGLE_CLIENT_ID"],
    GOOGLE_CLIENT_SECRET=os.environ["GOOGLE_CLIENT_SECRET"],
    GOOGLE_REFRESH_TOKEN=os.environ["GOOGLE_REFRESH_TOKEN"]
)

with open("google-ads.yaml", "w") as f:
    f.write(rendered)

print("✅ google-ads.yaml успешно сгенерирован.")