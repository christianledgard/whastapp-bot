docker build . -t bot-wa
docker run -d --env-file .env -p 5001:5000 bot-wa