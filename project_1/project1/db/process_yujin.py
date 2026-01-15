from pathlib import Path
import fitz
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

def preprocess_yujin(pdf_dir, persist_directory) :
    documents = load_yujin_pdf(pdf_dir)

    text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1500, 
    chunk_overlap=200,
    separators=["\n\n", "\n", " ", ""] # 문단 단위로 먼저 자르도록 유도
    )

    split_docs = text_splitter.split_documents(documents)
    print(f"\n✂️ 총 {len(documents)}개의 설교를 {len(split_docs)}개의 청크(조각)로 분할했습니다.")

    if split_docs:
        print("💾 ChromaDB에 저장 중...")

        # 임베딩 모델 명시 (검색 때와 동일하게!)
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

        vectorstore = Chroma.from_documents(
            documents=split_docs,
            embedding=embeddings,
            persist_directory=persist_directory,
            collection_name="yujin_works" # "pastor_sermons"
        )
        print("✅ 저장 완료! DB가 업데이트되었습니다.")
    else:
        print("❌ 저장할 문서가 없습니다.")


def load_yujin_pdf(pdf_dir) : 
    print("📂 PDF 처리 시작...")
    documents = [] # LangChain Document 객체를 담을 리스트
    
    if pdf_dir.exists():
        for pdf_path in pdf_dir.glob("*.pdf"):
            title, content = extract_core_sermon(pdf_path)

            if content:
                
                print(f" - [{title}] 로드 완료 ({len(content)}자)")
                print(f" 🔍 메타데이터 추출 중: {pdf_path.name}")

                doc = Document(
                    page_content=content,
                    metadata={
                        "source": pdf_path.name, # 파일명
                        "title": title,          # 설교 제목 (답변 출처 표기에 사용됨)
                        "author": "김유진 목사",  # 필터링용
                        "category": "sermon",
                    }
                )
                documents.append(doc)
            else:
                print(f" ⚠️ 스킵: {pdf_path.name} (서론/축도 패턴 미발견)")

    return documents

        
def extract_core_sermon(pdf_path):
    doc = fitz.open(pdf_path)
    
    # [최적화 1] 제목 추출: 전체를 읽지 않고 '첫 페이지'만 읽어서 해결
    title = ""
    try:
        if len(doc) > 0:
            first_page_text = doc[0].get_text("text")
            # 첫 페이지 텍스트 중 공백이 아닌 첫 줄을 제목으로 간주
            for line in first_page_text.splitlines():
                if line.strip():
                    title = line.strip()
                    break
    except Exception as e:
        print(f"제목 추출 중 오류: {e}")
        title = "제목 없음"

    # 1. 전체 텍스트 병합 (본문 추출용)
    full_text = ""
    for page in doc:
        full_text += page.get_text("text") + "\n"
    
    doc.close() # 다 썼으니 닫기

    if not full_text : 
        return None, None 

    # 2. 위치 찾기
    start_keyword = "서론"
    end_keywords = ["축도", "기도"]
    
    start_index = full_text.find(start_keyword)

    # 서론이 없으면 실패
    if start_index == -1:
        return None, None

    # [최적화 2] 끝 위치 찾기
    # 전체에서 찾는 게 아니라, '서론'이 나온 위치(start_index) '이후'부터 찾습니다.
    # 이렇게 해야 서론보다 앞에 있는(예: 예배순서지의 '기도') 단어에 낚이지 않습니다.
    found_end_indices = []
    for k in end_keywords:
        idx = full_text.find(k, start_index) # start_index 이후부터 검색
        if idx != -1:
            found_end_indices.append(idx)

    # 끝 후보들 중 가장 먼저 나오는 것 선택 (min)
    if found_end_indices:
        end_index = min(found_end_indices)
        
        # 3. 슬라이싱 (제목과 본문 반환)
        # start_index부터 end_index까지
        core_content = full_text[start_index:end_index]
        return title, core_content.strip()
    
    else:
        # 서론은 찾았는데 끝나는 단어가 없는 경우 (문서 끝까지 가져옴)
        # return title, full_text[start_index:].strip()
        return None, None