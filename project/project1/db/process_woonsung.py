import struct
import zlib
import olefile
from pathlib import Path
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from dotenv import load_dotenv

from backend.service import extract_bible_ref_with_llm

BASE_DIR = Path(__file__).resolve().parents[1]
CONFIG_PATH = BASE_DIR / "config" / ".env"

load_dotenv(CONFIG_PATH)


# --- 1. [핵심] HWP 텍스트 추출 함수 ---
def get_hwp_text(filename):
    f = olefile.OleFileIO(filename)
    dirs = f.listdir()

    if ["FileHeader"] not in dirs or \
            ["\x05HwpSummaryInformation"] not in dirs:
        raise Exception("Not Valid HWP.")

    header = f.openstream("FileHeader")
    header_data = header.read()
    is_compressed = (header_data[36] & 1) == 1

    nums = []
    for d in dirs:
        if d[0] == "BodyText":
            nums.append(int(d[1][len("Section"):]))
    sections = ["BodyText/Section" + str(x) for x in sorted(nums)]

    text = ""
    for section in sections:
        bodytext = f.openstream(section)
        data = bodytext.read()
        if is_compressed:
            unpacked_data = zlib.decompress(data, -15)
        else:
            unpacked_data = data

        section_text = ""
        i = 0
        size = len(unpacked_data)
        while i < size:
            header = struct.unpack_from("<I", unpacked_data, i)[0]
            rec_type = header & 0x3ff
            rec_len = (header >> 20) & 0xfff

            if rec_type in [67]:
                rec_data = unpacked_data[i + 4:i + 4 + rec_len]
                section_text += rec_data.decode('utf-16')
                section_text += "\n"

            i += 4 + rec_len

        text += section_text
        text += "\n"

    return text


# --- 2. 설교 본문 정제 (제목, 서론~축도) ---
def extract_core_sermon(hwp_path):
    
    try:
        full_text = get_hwp_text(hwp_path)
    except Exception as e:
        print(f"❌ 파일 읽기 에러: {hwp_path.name} - {e}")
        return None, None

    if not full_text:
        return None, None

    title = hwp_path.stem # 기본값은 파일명

    return title, full_text.strip()

    
# --- 3. 문서 로드 및 객체 생성 ---
def load_woonsung_hwp(hwf_dir): 
    print(f"📂 HWP 폴더 읽기: {hwf_dir}")
    documents = [] 
    
    if hwf_dir.exists():
        for hwp_path in hwf_dir.glob("*.hwp"): # .hwp 확장자 확인
            
            title, content = extract_core_sermon(hwp_path)

            if content and len(content) > 50: # 너무 짧은 내용은 스킵
                print(f" - [{title}] 로드 완료 ({len(content)}자)")
                print(f" 🔍 메타데이터 추출 중: {hwp_path.name}")
                bible_reference = extract_bible_ref_with_llm(hwp_path.name)
                print(f" LLM 요약 메타데이터 : {bible_reference}")

                doc = Document(
                    page_content=content,
                    metadata={
                        "source": hwp_path.name,
                        "title": title,         
                        "author": "정운성 목사", 
                        "category": "sermon",
                        "bible_ref": bible_reference  # 규격화된 정보 저장 (예: 마:14장)
                    }
                )
                documents.append(doc)
            else:
                print(f" ⚠️ 스킵: {hwp_path.name} (내용 없음 또는 패턴 불일치)")
    else:
        print("❌ 경로가 존재하지 않습니다.")

    return documents

# --- 4. 메인 전처리 함수 ---
def preprocess_woonsung(hwf_dir, persist_directory):
    # 문서 로드
    documents = load_woonsung_hwp(hwf_dir)

    if not documents:
        print("❌ 처리할 문서가 없습니다.")
        return

    # 텍스트 분할
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500, 
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""] 
    )

    split_docs = text_splitter.split_documents(documents)
    print(f"\n✂️ 총 {len(documents)}개의 설교를 {len(split_docs)}개의 청크로 분할했습니다.")

    # 벡터 DB 저장
    if split_docs:
        print("💾 ChromaDB에 저장 중...")

        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

        vectorstore = Chroma.from_documents(
            documents=split_docs,
            embedding=embeddings,
            persist_directory=persist_directory,
            collection_name="woonsung_works" # 컬렉션 이름 구분!
        )
        print("✅ 저장 완료! DB가 업데이트되었습니다.")
    else:
        print("❌ 저장할 청크가 없습니다.")