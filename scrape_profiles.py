import os
import time
import random
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# ——————————————————————————
# 1) Ajusta el nombre de tu chromedriver si es necesario.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMEDRIVER_PATH = os.path.join(BASE_DIR, "chromedriver.exe")

# 2) Tu consulta X-Ray en Google (último año, sin personalizar)
SEARCH_URL = (
    'https://www.google.com/search?'
    'q=site:linkedin.com/in+("Gerente+de+Operaciones"+OR+"Operations+Manager"+OR+"Jefe+de+Producción+Minera")'
    '+AND+(litio+OR+cobre)+AND+Chile'
    '+AND+("10+años"+OR+"%2B10+años"+OR+"más+de+10+años"+OR+"5+años"+OR+"más+de+5+años")'
    '+AND+(SAP+OR+Vulcan+OR+"MineSight"+OR+"optimización+de+procesos"+OR+"seguridad+minera")'
    '+AND+("liderazgo"+OR+"toma+de+decisiones"+OR+"gestión+de+equipos"+OR+"comunicación+efectiva"+OR+"mejora+continua")'
    '&tbs=qdr:y&pws=0'
)
MAX_PAGES = 51       # ≈51 páginas de resultados
CHUNK_PAGES = 20     # reiniciar navegador cada 20 para evitar bloqueos
KEYWORDS_MATERIALS = ["litio", "cobre"]

# ——————————————————————————
def make_driver():
    opts = Options()
    opts.add_argument("--incognito")
    opts.add_argument("--start-maximized")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    svc = Service(CHROMEDRIVER_PATH)
    drv = webdriver.Chrome(service=svc, options=opts)
    return drv

driver = make_driver()
driver.get(SEARCH_URL)
time.sleep(random.uniform(4,7))

results = []
page = 1

while True:
    print(f"🔍 Scraping página {page}…")
    soup = BeautifulSoup(driver.page_source, "html.parser")
    blocks = soup.select("div.tF2Cxc")
    if not blocks or page > MAX_PAGES:
        print("✅ No hay más resultados o se alcanzó el límite.")
        break

    for b in blocks:
        title_el   = b.select_one("h3")
        link_el    = b.select_one("div.yuRUbf > a[href*='linkedin.com/in']")
        snippet_el = b.select_one(".VwiC3b")

        title   = title_el.get_text(strip=True) if title_el else ""
        link    = link_el["href"]      if link_el else ""
        snippet = snippet_el.get_text(" ", strip=True) if snippet_el else ""
        text_all = (title + " " + snippet).lower()

        # extraer años de experiencia
        import re
        m = re.search(r"(?:más de\s*|\+)?\s*(\d{1,2})\s+años? de experiencia", text_all)
        if m:
            num = m.group(1)
            raw = m.group(0)
            experience = f"+{num}" if raw.strip().startswith(("más de", "+")) else num
        else:
            experience = ""

        # detectar materiales
        materials = ", ".join([w for w in KEYWORDS_MATERIALS if w in text_all])

        results.append({
            "Título": title,
            "Link LinkedIn": link,
            "Extracto": snippet,
            "Años de experiencia": experience,
            "Materiales": materials
        })

    # fragmentación de sesión
    if page % CHUNK_PAGES == 0:
        driver.quit()
        time.sleep(random.uniform(3,5))
        driver = make_driver()
        driver.get(f"{SEARCH_URL}&start={(page)*10}")
        time.sleep(random.uniform(4,7))
    else:
        # ir a siguiente página
        try:
            nxt = driver.find_element(By.ID, "pnnext")
            driver.execute_script("arguments[0].scrollIntoView();", nxt)
            time.sleep(random.uniform(1,2))
            driver.execute_script("arguments[0].click();", nxt)
            time.sleep(random.uniform(4,7))
        except:
            print("✅ No se pudo avanzar más.")
            break

    page += 1

driver.quit()

# ——————————————————————————
# guardar en Excel
df = pd.DataFrame(results)
df.to_excel("resultados_xray_google.xlsx", index=False)
print(f"✅ Scraping completado: {len(df)} perfiles guardados en 'resultados_xray_google.xlsx'")
