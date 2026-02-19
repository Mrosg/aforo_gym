import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta
import csv
import os
import sys
import time

URL = "https://www.dreamfit.es/centros/aluche"
CSV_FILE = "aforo_dreamfit.csv"

HORA_INICIO = (5, 30)
HORA_FIN = (23, 30)
REINTENTOS = 3
ESPERA_REINTENTO = 10  # segundos entre reintentos

def hora_madrid():
    return datetime.now(timezone(timedelta(hours=1)))

def dentro_de_horario():
    madrid = hora_madrid()
    hora_actual = (madrid.hour, madrid.minute)
    return HORA_INICIO <= hora_actual <= HORA_FIN

def scrape_aforo():
    for intento in range(1, REINTENTOS + 1):
        try:
            response = requests.get(URL, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            section = soup.find("section", {"id": "collapseAforo"})

            if section is None:
                raise ValueError("Sección collapseAforo no encontrada en el HTML")

            porcentaje = section.find("h1").text.strip()
            h3s = section.find_all("h3", class_="cliente")
            personas = h3s[0].contents[0].strip()
            aforo_total = h3s[1].contents[0].strip()
            hora = hora_madrid().strftime("%Y-%m-%d %H:%M:%S")

            return {
                "hora": hora,
                "personas": personas,
                "porcentaje": porcentaje,
                "aforo_total": aforo_total
            }

        except Exception as e:
            print(f"Intento {intento}/{REINTENTOS} fallido: {e}")
            if intento < REINTENTOS:
                time.sleep(ESPERA_REINTENTO)

    print("Todos los reintentos fallaron. Saliendo sin guardar datos.")
    sys.exit(0)  # exit(0) para no marcar el workflow como error

def guardar_csv(datos):
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["hora", "personas", "porcentaje", "aforo_total"])
        if not file_exists:
            writer.writeheader()
        writer.writerow(datos)

if __name__ == "__main__":
    if not dentro_de_horario():
        print("Fuera de horario. Saliendo.")
        sys.exit(0)

    datos = scrape_aforo()
    guardar_csv(datos)
    print(f"[{datos['hora']}] Personas: {datos['personas']} | {datos['porcentaje']} | Aforo total: {datos['aforo_total']}")
