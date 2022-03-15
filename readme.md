References:
https://pythonise.com/series/learning-flask/building-a-flask-app-with-docker-compose
https://github.com/viveksb007/camscanner_watermark_remover

In the shell set the environment variables for development:
export FLASK_APP=report_check_app
export FLASK_ENV=development

Run the app with flask run

gcloud builds submit --tag gcr.io/schoolops/report-check --project=schoolops

gcloud run deploy report-check --image gcr.io/schoolops/report-check --platform managed --project=schoolops --allow-unauthenticated --region australia-southeast1

gcloud iam service-accounts list --project=schoolops

gcloud iam service-accounts keys create ./keys.json --iam-account report-check@schoolops.iam.gserviceaccount.com

gcloud auth activate-service-account --key-file=keys.json
