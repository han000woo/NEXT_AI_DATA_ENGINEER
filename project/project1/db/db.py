from pathlib import Path

from dotenv import load_dotenv
from process_bubryune import preprocess_bubryune
from process_bible import preprocess_bible
from process_niche import preprocess_niche
from process_yujin import preprocess_yujin
from process_woonsung import preprocess_woonsung

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[1]
BIBLE_PATH = BASE_DIR / "data" / "bible.json"
NICHE_PATH = BASE_DIR / "data" / "niche.txt"
YUJIN_PATH = BASE_DIR / "data" / "yujin"
WOONSUNG_PATH = BASE_DIR / "data" / "woonsung"
BUBRYUNE_PATH = BASE_DIR / "data" / "bubryune"
VECTOR_DB_PATH = BASE_DIR / "chroma_vector_db"

# preprocess_bible(BIBLE_PATH, VECTOR_DB_PATH)
# preprocess_niche(NICHE_PATH, VECTOR_DB_PATH)
# preprocess_yujin(YUJIN_PATH, VECTOR_DB_PATH)
# preprocess_woonsung(WOONSUNG_PATH, VECTOR_DB_PATH)
preprocess_bubryune(BUBRYUNE_PATH, VECTOR_DB_PATH)