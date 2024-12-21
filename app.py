import streamlit as st
import os
import json
import yaml
import bcrypt
from datetime import datetime, timedelta

# (선택) 로컬 환경에서 .env를 로드할 수도 있음
# Streamlit Cloud에서는 보통 secrets 사용
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

################################
# 1. set_page_config
################################
st.set_page_config(page_title="my-minimal-git-journal", layout="wide")

################################
# 2. 환경 변수 or st.secrets 로드
################################
def get_env_value(key: str, default: str = "") -> str:
    """
    로컬 .env 파일에 값이 있으면 우선 사용,
    없으면 st.secrets에서 가져옴,
    마지막으로 없으면 default.
    """
    # 1) .env 파일에서 가져오기
    env_val = os.getenv(key, "")
    if env_val:
        return env_val

    # 2) secrets에서 가져오기
    if key in st.secrets:
        return st.secrets[key]

    # 3) 둘 다 없으면 default
    return default

ADMIN_ID = get_env_value("ADMIN_ID", "admin")   # 디폴트 admin
WORK_ID = get_env_value("WORK_ID", "work")     # 디폴트 work

ADMIN_PW_HASH = get_env_value("ADMIN_PW")  # bcrypt 해시 (예: $2b$12$...)
WORK_PW_HASH = get_env_value("WORK_PW")

DOCS_DIR = "docs"
METADATA_FILE = "metadata.json"
MKDOCS_FILE = "mkdocs.yml"

################################
# 3. Session State
################################
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user_type" not in st.session_state:
    st.session_state["user_type"] = None
if "login_time" not in st.session_state:
    st.session_state["login_time"] = None

################################
# 4. 세션 만료
################################
SESSION_TIMEOUT_MINUTES = 5

def check_session_expiration():
    if st.session_state["logged_in"]:
        login_time = st.session_state["login_time"]
        if login_time is not None:
            elapsed = datetime.now() - login_time
            if elapsed > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
                st.warning("세션 시간이 만료되었습니다. 다시 로그인해 주세요.")
                logout()

def logout():
    st.session_state["logged_in"] = False
    st.session_state["user_type"] = None
    st.session_state["login_time"] = None
    st.rerun()

################################
# 5. bcrypt 검증
################################
def check_password(input_pw: str, stored_hash: str) -> bool:
    if not stored_hash:
        return False
    # bcrypt 해시 여부 판별
    if stored_hash.startswith("$2b$"):
        return bcrypt.checkpw(input_pw.encode("utf-8"), stored_hash.encode("utf-8"))
    else:
        # 평문
        return (input_pw == stored_hash)

################################
# 6. 계정별 UI (배경색 등)
################################
def apply_color_theme(user_type: str):
    if user_type == "admin":
        st.markdown(
            """
            <style>
            body {
                background-color: #ffd6d6;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
    elif user_type == "work":
        st.markdown(
            """
            <style>
            body {
                background-color: #d6dfff;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <style>
            body {
                background-color: #ffffff;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

################################
# 7. JSON 메타데이터 로드/저장
################################
def load_metadata():
    if not os.path.exists(METADATA_FILE):
        return {}
    try:
        with open(METADATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_metadata(metadata):
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=4)

################################
# 8. 문서 생성/삭제/수정
################################
def generate_filename():
    date_str = datetime.now().strftime("%Y-%m-%d")
    counter = 1
    while True:
        fname = f"{date_str}-#{counter}.md"
        if not os.path.exists(os.path.join(DOCS_DIR, fname)):
            return fname
        counter += 1

def ensure_index_md():
    index_file = os.path.join(DOCS_DIR, "index.md")
    if not os.path.exists(index_file):
        os.makedirs(DOCS_DIR, exist_ok=True)
        with open(index_file, "w", encoding="utf-8") as f:
            f.write("# Welcome to My Minimal Git Journal\n\n이곳에 프로젝트 소개를 작성하세요.")

def parse_md_content(md_content: str):
    lines = md_content.splitlines()
    title, major, mid, minor = "", "", "", ""
    tags = []
    access_level = "personal"
    fm_end = 0

    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            line = lines[i].strip()
            if line == "---":
                fm_end = i
                break
            if line.startswith("title:"):
                title = line.split("title:")[1].strip().strip('"').strip()
            elif line.startswith("대분류:"):
                major = line.split("대분류:")[1].strip().strip('"').strip()
            elif line.startswith("중분류:"):
                mid = line.split("중분류:")[1].strip().strip('"').strip()
            elif line.startswith("소분류:"):
                minor = line.split("소분류:")[1].strip().strip('"').strip()
            elif line.startswith("tags:"):
                t_str = line.split("tags:")[1].strip()
                try:
                    tags = json.loads(t_str)
                except:
                    tags = []
            elif line.startswith("access_level:"):
                access_level = line.split("access_level:")[1].strip().strip('"').strip()

    body = "\n".join(lines[fm_end+1:])
    return title, major, mid, minor, tags, access_level, body

def save_document_from_md(md_content: str):
    os.makedirs(DOCS_DIR, exist_ok=True)
    title, major, mid, minor, tags, access, body = parse_md_content(md_content)
    if not title or not major:
        raise ValueError("Front Matter에 title 또는 대분류(대분류:)가 없습니다.")

    fname = generate_filename()
    with open(os.path.join(DOCS_DIR, fname), "w", encoding="utf-8") as f:
        f.write("---\n")
        f.write(f'title: "{title}"\n')
        f.write(f'대분류: "{major}"\n')
        f.write(f'중분류: "{mid}"\n')
        f.write(f'소분류: "{minor}"\n')
        f.write(f'tags: {json.dumps(tags, ensure_ascii=False)}\n')
        f.write(f'access_level: "{access}"\n')
        f.write("---\n\n")
        f.write(body)

    meta = load_metadata()
    meta[fname] = {
        "title": title,
        "대분류": major,
        "중분류": mid,
        "소분류": minor,
        "tags": tags,
        "access_level": access
    }
    save_metadata(meta)

    ensure_index_md()
    return fname, title, access

def delete_document(fname):
    meta = load_metadata()
    if fname in meta:
        del meta[fname]
        save_metadata(meta)
    fpath = os.path.join(DOCS_DIR, fname)
    if os.path.exists(fpath):
        os.remove(fpath)

def edit_document_title_body(fname, new_title, new_body):
    doc_path = os.path.join(DOCS_DIR, fname)
    if not os.path.exists(doc_path):
        raise FileNotFoundError("해당 문서가 존재하지 않습니다.")

    with open(doc_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    fm_open = False
    updated = []
    for line in lines:
        if line.strip() == "---" and not fm_open:
            fm_open = True
            updated.append(line)
            continue
        if line.strip() == "---" and fm_open:
            updated.append(line)
            fm_open = False
            continue
        if fm_open and line.startswith("title:"):
            updated.append(f'title: "{new_title}"\n')
        else:
            updated.append(line)

    idx_end_fm = 0
    for i, ln in enumerate(updated):
        if ln.strip() == "---":
            idx_end_fm = i
    final_lines = updated[: idx_end_fm + 1]
    final_lines.append("\n" + new_body + "\n")

    with open(doc_path, "w", encoding="utf-8") as f:
        f.writelines(final_lines)

    meta = load_metadata()
    if fname in meta:
        meta[fname]["title"] = new_title
        save_metadata(meta)

################################
# (추가) 문서 본문 전체 보기
################################
def get_document_content(fname):
    path = os.path.join(DOCS_DIR, fname)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return None

################################
# 9. mkdocs.yml nav 업데이트
################################
def load_mkdocs_config():
    MKDOCS_FILE = "mkdocs.yml"
    if not os.path.exists(MKDOCS_FILE):
        base_config = {
            "site_name": "My Minimal Git Journal",
            "theme": {"name": "material"},
            "nav": [{"Home": "index.md"}],
            "plugins": ["search"],
            "markdown_extensions": [
                "admonition",
                "codehilite",
                {"toc": {"permalink": True}},
                "footnotes",
                "meta"
            ]
        }
        with open(MKDOCS_FILE, "w", encoding="utf-8") as f:
            yaml.dump(base_config, f, allow_unicode=True)
        return base_config
    else:
        with open(MKDOCS_FILE, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

def save_mkdocs_config(cfg):
    MKDOCS_FILE = "mkdocs.yml"
    with open(MKDOCS_FILE, "w", encoding="utf-8") as f:
        yaml.dump(cfg, f, allow_unicode=True)

def create_filtered_nav(user_type, meta):
    nav_docs = []
    for fname, doc_meta in meta.items():
        lvl = doc_meta.get("access_level", "personal")
        if user_type == "admin":
            nav_docs.append((doc_meta["대분류"], doc_meta["중분류"], doc_meta["소분류"], fname))
        elif user_type == "work":
            if lvl in ["personal", "work"]:
                nav_docs.append((doc_meta["대분류"], doc_meta["중분류"], doc_meta["소분류"], fname))
    return nav_docs

def update_nav_in_mkdocs(nav_docs):
    cfg = load_mkdocs_config()
    cfg["nav"] = [{"Home": "index.md"}]

    def ensure_category(nav_list, cat_name):
        for item in nav_list:
            if isinstance(item, dict) and cat_name in item:
                return item[cat_name]
        new_item = {cat_name: []}
        nav_list.append(new_item)
        return new_item[cat_name]

    for (maj, mid, minr, fname) in nav_docs:
        maj_list = ensure_category(cfg["nav"], maj)
        mid_list = ensure_category(maj_list, mid)
        found = False
        for i, it in enumerate(mid_list):
            if isinstance(it, dict) and minr in it:
                it[minr] = fname
                found = True
                break
        if not found:
            mid_list.append({minr: fname})

    save_mkdocs_config(cfg)

################################
# 10. 빌드 및 배포
################################
def build_and_deploy():
    b_res = os.system("mkdocs build")
    if b_res != 0:
        return "mkdocs build 실패!"
    d_res = os.system("mkdocs gh-deploy")
    if d_res != 0:
        return "mkdocs gh-deploy 실패!"
    return "정적 사이트 빌드 및 배포 완료!"

################################
# 11. Streamlit App 메인
################################
st.title("Minimal Git Journal - Secrets-based Login")

check_session_expiration()

if not st.session_state["logged_in"]:
    st.subheader("로그인")
    input_id = st.text_input("아이디")
    input_pw = st.text_input("비밀번호", type="password")

    if st.button("로그인"):
        if input_id == ADMIN_ID and check_password(input_pw, ADMIN_PW_HASH):
            st.session_state["logged_in"] = True
            st.session_state["user_type"] = "admin"
            st.session_state["login_time"] = datetime.now()
            st.rerun()
        elif input_id == WORK_ID and check_password(input_pw, WORK_PW_HASH):
            st.session_state["logged_in"] = True
            st.session_state["user_type"] = "work"
            st.session_state["login_time"] = datetime.now()
            st.rerun()
        else:
            st.error("아이디 또는 비밀번호가 잘못되었습니다.")
    st.stop()

else:
    user_type = st.session_state["user_type"]
    apply_color_theme(user_type)

    st.sidebar.title(f"현재 사용자: {user_type}")
    if st.sidebar.button("로그아웃"):
        logout()

    # 메뉴명 변경: "정적 사이트 빌드 및 배포(로컬 PC에서만 가능)" 로 수정
    menu_list = [
        "문서 보기",
        "문서 작성(MD 포맷)",
        "문서 삭제/수정",
        "정적 사이트 빌드 및 배포(로컬 PC에서만 가능)"
    ]

    if user_type != "admin":
        menu_list.remove("문서 삭제/수정")

    menu = st.sidebar.selectbox("메뉴", menu_list)
    meta = load_metadata()

    if menu == "문서 보기":
        st.header("문서 목록")
        if user_type == "admin":
            visible_docs = meta
        else:
            # work 사용자는 personal, work 문서만
            visible_docs = {
                k: v for k, v in meta.items()
                if v["access_level"] in ["personal", "work"]
            }
        if visible_docs:
            for fname, doc_meta in visible_docs.items():
                st.subheader(f"{doc_meta.get('title')} ({fname})")
                st.write(f"- 대분류: {doc_meta.get('대분류')}")
                st.write(f"- 중분류: {doc_meta.get('중분류')}")
                st.write(f"- 소분류: {doc_meta.get('소분류')}")
                st.write(f"- 태그: {', '.join(doc_meta.get('tags', []))}")
                st.write(f"- 접근 권한: {doc_meta.get('access_level')}")
                st.markdown("---")
        else:
            st.warning("접근 가능한 문서가 없습니다.")

    elif menu == "문서 작성(MD 포맷)":
        st.header("새 문서 작성")
        st.write("아래 Front Matter 예시를 참고하세요.")
        st.code(
            """---
title: "문서 제목"
대분류: "개인용"
중분류: "학습"
소분류: "Python"
tags: ["태그1", "태그2"]
access_level: "personal"/"work"/"admin"
---
문서 본문 내용...
""",
            language="markdown"
        )
        md_txt = st.text_area("Markdown 전체 입력", height=300)
        if st.button("저장"):
            try:
                fname, doc_title, access = save_document_from_md(md_txt)
                st.success(f"문서 '{fname}' 생성 완료!")
                st.info(f"제목: {doc_title} | 접근 권한: {access}")
                nav_docs = create_filtered_nav(user_type, load_metadata())
                update_nav_in_mkdocs(nav_docs)
            except ValueError as e:
                st.error(f"문서 파싱 오류: {e}")

    elif menu == "문서 삭제/수정":
        st.header("문서 삭제/수정 (admin 전용)")
        if not meta:
            st.info("문서가 없습니다.")
        else:
            sel_file = st.selectbox("수정/삭제할 문서를 선택하세요", list(meta.keys()))
            if sel_file:
                doc_meta = meta[sel_file]
                st.write(f"제목: {doc_meta.get('title')}")
                st.write(f"접근 권한: {doc_meta.get('access_level')}")
                st.write(f"대분류: {doc_meta.get('대분류')}")
                st.write(f"중분류: {doc_meta.get('중분류')}")
                st.write(f"소분류: {doc_meta.get('소분류')}")
                st.write(f"태그: {doc_meta.get('tags')}")

                # (추가) 문서 본문 전체 보기
                if st.button("문서 본문 보기"):
                    content = get_document_content(sel_file)
                    if content is not None:
                        st.code(content, language="markdown")
                    else:
                        st.warning("문서 파일을 찾지 못했습니다.")

                if st.button("문서 삭제"):
                    delete_document(sel_file)
                    st.success("문서가 삭제되었습니다. nav 재생성 후 반영 필요.")
                    nav_docs = create_filtered_nav(user_type, load_metadata())
                    update_nav_in_mkdocs(nav_docs)
                    st.rerun()

                new_title = st.text_input("새 제목", value=doc_meta.get("title", ""))
                new_body = st.text_area("새 본문 내용 (Front Matter 제외)", height=200)

                if st.button("문서 수정"):
                    edit_document_title_body(sel_file, new_title, new_body)
                    st.success("문서 수정 완료! nav 재생성 후 반영 필요.")
                    nav_docs = create_filtered_nav(user_type, load_metadata())
                    update_nav_in_mkdocs(nav_docs)

    elif menu == "정적 사이트 빌드 및 배포(로컬 PC에서만 가능)":
        st.header("정적 사이트 빌드 및 배포(로컬 PC에서만 가능)")
        if st.button("mkdocs gh-deploy"):
            msg = build_and_deploy()
            if "실패" in msg:
                st.error(msg)
            else:
                st.success(msg)
                st.write("→ gh-pages 브랜치로 배포되었습니다.")
