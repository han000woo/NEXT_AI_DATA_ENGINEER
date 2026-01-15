
import re
from langchain.docstore.document import Document
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

def preprocess_niche(file_path, persist_directory) :
    documents = load_nietzsche_txt(file_path)

    text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1500, 
    chunk_overlap=200,
    separators=["\n\n", "\n", " ", ""] # 문단 단위로 먼저 자르도록 유도
    )

    split_docs = text_splitter.split_documents(documents)
    print(f"\n✂️ 총 {len(documents)}개의 어록을 {len(split_docs)}개의 청크(조각)로 분할했습니다.")

    if split_docs:
        print("💾 ChromaDB에 저장 중...")

        # 임베딩 모델 명시 (검색 때와 동일하게!)
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

        vectorstore = Chroma.from_documents(
            documents=split_docs,
            embedding=embeddings,
            persist_directory=persist_directory,
            collection_name="nietzsche_works" # "pastor_sermons"
        )
        print("✅ 저장 완료! DB가 업데이트되었습니다.")
    else:
        print("❌ 저장할 문서가 없습니다.")

def load_nietzsche_txt(file_path):
    """
    니체 텍스트 파일을 읽어 챕터와 문단(Aphorism)별로 Document를 생성합니다.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        full_text = f.read()

    docs = []

    # 1. 챕터 단위로 분리하기
    # 패턴 설명: 줄의 시작(^)에 "CHAPTER "가 오고 그 뒤에 로마숫자, 점, 그리고 나머지 제목이 오는 경우
    # re.MULTILINE 플래그를 써서 각 줄마다 검사합니다.
    # 이 패턴은 텍스트를 [Intro, (챕터헤더, 내용), (챕터헤더, 내용)...] 순으로 쪼갭니다.
    chapter_pattern = r"(CHAPTER\s+[IVXLCDM]+\.\s+.*)"
    
    # re.split을 쓰면 구분자(챕터헤더)도 리스트에 포함됩니다.
    parts = re.split(chapter_pattern, full_text)

    # parts[0]은 보통 서문(Preface)이나 빈 공간입니다. (필요하면 처리, 여기선 생략 가능)
    # 챕터 헤더와 내용이 번갈아 나오므로 2칸씩 점프하며 돕니다.
    # parts 구조 예상: [서문, 챕터1헤더, 챕터1내용, 챕터2헤더, 챕터2내용 ...]
    
    start_index = 1 if len(parts) > 1 else 0
    
    for i in range(start_index, len(parts) - 1, 2):
        chapter_header = parts[i].strip()   # 예: CHAPTER I. PREJUDICES OF PHILOSOPHERS
        chapter_content = parts[i+1]        # 해당 챕터의 전체 본문
        
        # 1-1. 챕터 제목과 번호 추출 (메타데이터용)
        # 예: "CHAPTER I. PREJUDICES..." 에서 "I"와 "PREJUDICES..." 분리
        header_match = re.match(r"CHAPTER\s+([IVXLCDM]+)\.\s+(.*)", chapter_header)
        chapter_num = header_match.group(1) if header_match else "Unknown"
        chapter_title = header_match.group(2) if header_match else chapter_header

        # 2. 챕터 내부에서 문단(Aphorism) 번호로 2차 분리하기
        # 니체 책은 보통 "1. 내용", "2. 내용" 형식이므로 숫자로 시작하는 문단을 찾습니다.
        # (?m)^\d+\. -> 멀티라인 모드에서 줄 첫머리에 숫자가 오고 점(.)이 찍힌 패턴
        aphorism_pattern = r"(?m)^(\d+)\.\s+"
        
        # 문단 번호를 기준으로 텍스트를 쪼갭니다.
        # 결과: [서론(번호없는앞부분), 번호1, 내용1, 번호2, 내용2...]
        sections = re.split(aphorism_pattern, chapter_content)
        
        # sections[0]은 1번 문단 나오기 전의 서문일 수 있습니다. (내용 있으면 추가)
        if sections[0].strip():
             docs.append(Document(
                page_content=sections[0].strip(),
                metadata={
                    "source": "nietzsche",
                    "chapter_num": chapter_num,
                    "chapter_title": chapter_title,
                    "section_num": "Intro", # 번호 없음
                    "full_ref": f"{chapter_header} - Intro"
                }
            ))

        # 번호와 내용이 쌍으로 나오므로 반복 (1부터 시작, 2칸씩)
        for j in range(1, len(sections) - 1, 2):
            sec_num = sections[j]       # 예: 1
            sec_text = sections[j+1]    # 예: The Will to Truth...
            
            # 3. 최종 Document 생성
            doc = Document(
                page_content=f"{sec_num}. {sec_text.strip()}", # 내용은 "1. The Will..." 형태로 저장
                metadata={
                    "source": "nietzsche",         # 필터링용 태그
                    "chapter_num": chapter_num,    # 예: I
                    "chapter_title": chapter_title,# 예: PREJUDICES OF PHILOSOPHERS
                    "section_num": int(sec_num),   # 예: 1 (숫자로 변환)
                    "full_ref": f"{chapter_header} - §{sec_num}" # 출처 표시용
                }
            )
            docs.append(doc)

    return docs
