# HR-Project-Web-Scraping-for-headhunting
Headhunting Minería: Automatización de extracción y análisis de perfiles ejecutivos de operaciones mineras (litio y cobre) con Python (Selenium/Pandas) y Excel para generar un shortlist de candidatos.

---

## Contenido y flujos de trabajo

1. **`scripts/scrape_profiles.py`**  
   - Realiza una búsqueda X-Ray en Google para perfiles de “Gerente de Operaciones” (litio/cobre) en Chile.  
   - Usa Selenium en modo incógnito + delays humanos + fragmentación de sesión para evitar bloqueos.  
   - Extrae título, link de LinkedIn, extracto y detecta años de experiencia y materiales.  
   - Guarda en `data/raw/resultados_xray_google.xlsx`.

2. **`scripts/limpiar_perfiles.py`**  
   - Lee `resultados_xray_google.xlsx` y la hoja `Listas` con keywords (cargos, skills, materiales).  
   - Concatena columnas A–E en un único campo interno, aplica regex y funciones `first_match` / `all_matches`.  
   - Genera un DataFrame limpio con columnas normalizadas: Cargo Actual, Años de Experiencia, Materiales, Competencias.  
   - Escribe el resultado en `data/clean/Perfiles_Limpios.xlsx` y actualiza la hoja `Tabla Limpia` del mismo libro.

3. **Dashboard en Excel**  
   - A partir de `Perfiles_Limpios.xlsx` se construyen gráficos de distribución de cargos, materiales, experiencia y herramientas dominadas.  
   - Se añade un filtro dinámico por años de experiencia y se selecciona un Top-20 de candidatos.
