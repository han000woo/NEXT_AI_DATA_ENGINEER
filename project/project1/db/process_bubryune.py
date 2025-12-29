from pathlib import Path
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain_core.documents import Document
from openai import OpenAI
from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp
import time
import random


def polite_sleep(min_sec=2.0, max_sec=4.0):
    delay = random.uniform(min_sec, max_sec)
    print(f"😴 {delay:.2f}초 대기")
    time.sleep(delay)


load_dotenv()

client = OpenAI()
# 즉문 즉설 레전드 7편
# playlist_url = "https://www.youtube.com/playlist?list=PLeyE__d-DACMeLChk7JatWNZmMwv3M5f4"
# 즉문 즉설 182편
playlist_url = (
    "https://www.youtube.com/playlist?list=PLeyE__d-DACM8w9c6ZAUiBkOj-B4UE8CB"
)

jukmun_dir = Path("jeukmun_transcripts")


def get_video_ids():
    ydl_opts = {
        "quiet": True,
        "extract_flat": True,  # ❗ 중요 (메타데이터만)
        "skip_download": True,
    }

    video_ids = []

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(playlist_url, download=False)

        for entry in info["entries"]:
            if entry and "id" in entry:
                video_ids.append(entry["id"])

    print(f"총 영상 수: {len(video_ids)}")
    return video_ids


def saving_txts(video_ids):
    jukmun_dir.mkdir(exist_ok=True)

    for idx, video_id in enumerate(video_ids, 1):
        print(f"\n▶ [{idx}/{len(video_ids)}] {video_id}")
        ytt_api = YouTubeTranscriptApi()

        try:
            transcript = ytt_api.fetch(video_id, languages=["ko"])

            text = "\n".join(snippet.text for snippet in transcript)

            file_path = jukmun_dir / f"{idx:03d}_{video_id}.txt"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(text)

            print(f"✅ 저장 완료: {file_path}")

        except Exception as e:
            print(f"❌ 실패: {video_id} / {e}")

            # ❗ 실패 시 더 긴 대기
            polite_sleep(5, 8)
            continue

        # ✅ 정상 처리 후 기본 대기
        polite_sleep(2, 4)

        # ✅ 20개마다 쿨다운
        if idx % 20 == 0:
            print("🧊 쿨다운 타임 (15초)")
            time.sleep(15)


# 법륜스님 유튜브 데이터 크롤링
# video_ids = get_video_ids()
# saving_txts(video_ids)

SYSTEM_PROMPT = """
너는 법륜스님의 즉문즉설 대화를 정리하는 조력자이다.

규칙:
1. 원문 문장을 그대로 복사하지 않는다
2. 법륜스님 같은 어조를 사용한다
"""


def make_user_prompt(transcript: str) -> str:
    return f"""
아래는 법륜스님의 즉문즉설 강연 자막이다.

작업 지시:
- 질문자의 핵심 고민을 1문장으로 요약하라
- 법륜스님의 답변을 '깨달음 중심 요약'으로 3~5문장 정리하라
- 원문 표현은 사용하지 말고 의미만 재구성하라

출력 형식:
Q: (질문의 핵심)
A: (요약된 답변)

자막:
{transcript}
"""


def summarize_jeukmun(transcript: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": make_user_prompt(transcript)},
        ],
        temperature=0.3,  # 창작 최소화, 요약 안정성 ↑
        max_tokens=500,
    )

    return response.choices[0].message.content


def summarize_bubryune_data():
    input_dir = Path("jeukmun_transcripts")
    output_dir = Path("jeukmun_summaries")
    output_dir.mkdir(exist_ok=True)

    for txt_file in input_dir.glob("*.txt"):
        raw_text = txt_file.read_text(encoding="utf-8")

        summary = summarize_jeukmun(raw_text)
        time.sleep(10)

        output_file = output_dir / txt_file.name
        output_file.write_text(summary, encoding="utf-8")

        print(f"✅ 요약 완료: {output_file.name}")


def preprocess_bubryune(bub_dir, persist_directory):
    print(f"📂 '{bub_dir}' 폴더에서 법륜스님 설교 데이터를 로드합니다...")
    # 문서 로드
    # documents = DirectoryLoader(
    #     bub_dir,
    #     glob="*.txt",
    #     loader_cls=TextLoader,
    #     loader_kwargs={"encoding": "utf-8"}, 
    # ).load()
    # print(documents)
    documents = [] 
    files = list(Path(bub_dir).glob("*.txt"))

    # if not documents:
    if not files :
        print("❌ 처리할 문서가 없습니다.")
        return
    
    for file_path in files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # 파일명(확장자 제외)을 제목으로 사용
            title = file_path.stem 
            print("즉문즉설 "+file_path.name[:3]+"강")
            doc = Document(
                page_content=content,
                metadata={
                    "source": "즉문즉설"+file_path.name[:3]+"강",      # 파일명 (예: sermon_01.txt)
                    "title": title,                # 제목 (예: sermon_01)
                    "author": "법륜스님",           # 작성자 고정
                    "category": "sermon"  # 카테고리 구분용
                }
            )
            documents.append(doc)
            
        except Exception as e:
            print(f"⚠️ 파일 로드 실패 ({file_path.name}): {e}")
    
    print(f"✅ 총 {len(documents)}개의 설교 문서를 로드했습니다.")

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
            collection_name="bubryune_works"
        )
        print("✅ 저장 완료! DB가 업데이트되었습니다.")
    else:
        print("❌ 저장할 청크가 없습니다.")
