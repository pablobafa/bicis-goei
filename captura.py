"""Captura la disponibilidad de BiciMAD (Madrid) y Bicicoruna (A Coruna) desde CityBikes y la anade a
data/<ciudad>/AAAA-MM-DD.csv (un fichero por dia, hora de Madrid). Solo libreria estandar.
Si una ciudad falla tras los reintentos se registra en data/<ciudad>/errores.csv: el hueco queda a la vista, no se inventa nada."""
import csv, json, os, sys, time, urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

REDES = {"madrid": "bicimad", "coruna": "bicicorunha"}
CAB = ["timestamp", "id", "bicis_libres", "huecos_libres", "operativa",
       "bicis_normales", "bicis_electricas", "capacidad_nominal", "last_updated"]
RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

def descargar(red, intentos=5):
    url = f"https://api.citybik.es/v2/networks/{red}?fields=stations"
    ultimo = None
    for i in range(intentos):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "GOEI-UIE-proyecto-bicis/1.0"})
            with urllib.request.urlopen(req, timeout=15) as r:
                st = json.load(r)["network"]["stations"]
            if st: return st
            ultimo = "respuesta sin estaciones"
        except Exception as e:
            ultimo = f"{type(e).__name__}: {e}"
        time.sleep(3)
    raise RuntimeError(ultimo)

def anadir(ruta, cabecera, filas):
    nuevo = not os.path.exists(ruta)
    with open(ruta, "a", newline="", encoding="utf8") as f:
        w = csv.writer(f)
        if nuevo: w.writerow(cabecera)
        w.writerows(filas)

def main():
    ahora = datetime.now(ZoneInfo("Europe/Madrid"))
    ts, dia = ahora.strftime("%Y-%m-%d %H:%M:%S"), ahora.strftime("%Y-%m-%d")
    ok = 0
    for ciudad, red in REDES.items():
        carpeta = os.path.join(RAIZ, ciudad); os.makedirs(carpeta, exist_ok=True)
        try:
            st = descargar(red)
        except Exception as e:
            anadir(os.path.join(carpeta, "errores.csv"), ["timestamp", "error"], [[ts, str(e)[:200]]])
            print(f"{ciudad}: ERROR {e}", file=sys.stderr); continue
        filas = []
        for s in st:
            x = s.get("extra") or {}
            sid = x.get("number") or x.get("uid") or s["id"]
            operativa = 0 if (x.get("online") is False or x.get("renting") is False or x.get("returning") is False) else 1
            filas.append([ts, sid, s["free_bikes"], s["empty_slots"], operativa,
                          x.get("normal_bikes", ""), x.get("ebikes", ""), x.get("slots", ""), x.get("last_updated", "")])
        anadir(os.path.join(carpeta, f"{dia}.csv"), CAB, filas)
        meta = os.path.join(carpeta, "estaciones.csv")          # nombres y coordenadas: una vez
        if not os.path.exists(meta):
            anadir(meta, ["id", "nombre", "lat", "lon"],
                   [[(s.get("extra") or {}).get("number") or (s.get("extra") or {}).get("uid") or s["id"],
                     s["name"], s["latitude"], s["longitude"]] for s in st])
        print(f"{ciudad}: {len(filas)} estaciones"); ok += 1
    sys.exit(0 if ok else 1)          # solo falla la ejecucion si no se ha capturado NINGUNA ciudad

if __name__ == "__main__":
    main()
