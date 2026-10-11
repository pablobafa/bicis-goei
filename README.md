# Captura de bicis compartidas (Madrid y A Coruña)

Proyecto GOEI 2026/27 · caso 18. `captura.py` consulta CityBikes (`bicimad`, `bicicorunha`) cada 15 minutos mediante
GitHub Actions y guarda `data/<ciudad>/AAAA-MM-DD.csv` (hora de Madrid) con: `timestamp, id, bicis_libres, huecos_libres,
operativa, bicis_normales, bicis_electricas, capacidad_nominal, last_updated` (`last_updated` en UTC).
`estaciones.csv` guarda nombre y coordenadas. `errores.csv` registra los huecos de la API; los huecos no se rellenan.

Aviso: las ejecuciones programadas de GitHub pueden retrasarse o saltarse alguna lectura; la cobertura real se mide en el analisis.
