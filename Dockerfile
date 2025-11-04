# Dockerfile

# 1. Basisimage met geschikte Python versie
FROM python:3.13-slim

# 2. Werkmap instellen
WORKDIR /app

# 3. Systeemvereisten (indien nodig) — kun je toevoegen als je native libs nodig hebt
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     build-essential \
# && rm -rf /var/lib/apt/lists/*

# 4. Kopieer de projectbestanden
COPY . /app

# 5. Installeer Python-dependencies (via jouw pyproject.toml)
RUN pip install --no-cache-dir .

# 6. Verwijder cache/overbodige bestanden (optioneel)
RUN rm -rf /root/.cache/pip

# 7. Exposeer poort indien jouw server een HTTP-endpoint heeft
# EXPOSE 8000

# 8. Definieer de entrypoint/start command
#    Schrijf de credentials naar bestand en stel GOOGLE_APPLICATION_CREDENTIALS in
CMD ["bash", "-lc", "echo \"$GOOGLE_APPLICATION_CREDENTIALS_JSON\" > /app/credentials.json && export GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json && python -m analytics_mcp.server"]
