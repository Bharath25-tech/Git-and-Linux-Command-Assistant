import time
import html
import streamlit as st

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Git & Linux Command Assistant",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded",
)

DEFAULT_K = 5

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>
    @import url(
        'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap'
    );

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(
                circle at 5% 0%,
                rgba(124, 92, 255, 0.08),
                transparent 30%
            ),
            radial-gradient(
                circle at 95% 10%,
                rgba(0, 194, 255, 0.06),
                transparent 25%
            );
    }

    #MainMenu, footer {
        visibility: hidden;
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }

    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* HERO */

    .hero {
        padding: 2.2rem 2.4rem;
        border-radius: 22px;
        background: linear-gradient(
            120deg,
            #5946D9 0%,
            #7957FF 50%,
            #009FE3 100%
        );
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 12px 35px rgba(89, 70, 217, 0.18);
    }

    .hero-badge {
        display: inline-block;
        padding: 6px 12px;
        margin-bottom: 14px;
        border: 1px solid rgba(255,255,255,0.3);
        border-radius: 30px;
        background: rgba(255,255,255,0.12);
        font-size: 0.73rem;
        font-weight: 600;
        letter-spacing: 1px;
    }

    .hero h1 {
        color: white !important;
        font-size: clamp(1.8rem, 4vw, 2.7rem);
        font-weight: 800;
        letter-spacing: -1.2px;
        margin: 0;
        line-height: 1.25;
    }

    .hero p {
        color: rgba(255,255,255,0.92);
        font-size: 0.98rem;
        line-height: 1.8;
        margin-top: 12px;
        margin-bottom: 0;
        max-width: 720px;
    }

    /* SIDEBAR */

    section[data-testid="stSidebar"] {
        border-right: 1px solid rgba(128,128,128,0.15);
    }

    .sidebar-brand {
        padding: 1rem;
        margin-bottom: 1.2rem;
        border: 1px solid rgba(124,92,255,0.25);
        border-radius: 15px;
        background: rgba(124,92,255,0.07);
    }

    .sidebar-brand h3 {
        margin: 0;
        font-size: 1.05rem;
        font-weight: 800;
    }

    .sidebar-brand p {
        margin: 6px 0 0;
        font-size: 0.8rem;
        opacity: 0.7;
        line-height: 1.6;
    }

    /* SECTION HEADINGS */

    .section-title {
        font-size: 1.3rem;
        font-weight: 750;
        letter-spacing: -0.4px;
        margin-bottom: 0.3rem;
    }

    .section-subtitle {
        font-size: 0.88rem;
        opacity: 0.68;
        margin-bottom: 1.2rem;
        line-height: 1.7;
    }

    /* SUGGESTION CARDS */

    .suggestion-card {
        padding: 1.25rem;
        border: 1px solid rgba(128,128,128,0.20);
        border-radius: 16px;
        background: rgba(128,128,128,0.035);
        min-height: 135px;
        margin-bottom: 0.8rem;
    }

    .suggestion-icon {
        font-size: 1.7rem;
        margin-bottom: 0.65rem;
    }

    .suggestion-card h4 {
        font-size: 0.98rem;
        font-weight: 700;
        margin: 0 0 0.4rem;
    }

    .suggestion-card p {
        font-size: 0.82rem;
        opacity: 0.7;
        line-height: 1.6;
        margin: 0;
    }

    /* BUTTONS */

    div.stButton > button {
        border-radius: 11px;
        border: 1px solid rgba(128,128,128,0.25);
        min-height: 43px;
        font-weight: 600;
        transition: all 0.2s ease;
    }

    div.stButton > button:hover {
        border-color: #7957FF;
        color: #7957FF;
    }

    /* CHAT */

    [data-testid="stChatMessage"] {
        border: 1px solid rgba(128,128,128,0.13);
        border-radius: 16px;
        padding: 1rem;
        margin-bottom: 0.9rem;
        background: rgba(128,128,128,0.025);
    }

    [data-testid="stChatMessage"] p {
        line-height: 1.8;
    }

    [data-testid="stChatInput"] {
        border-radius: 16px;
    }

    /* SOURCE CARDS */

    .source-card {
        padding: 0.9rem 1rem;
        margin: 0.6rem 0;
        border: 1px solid rgba(124,92,255,0.2);
        border-left: 4px solid #7957FF;
        border-radius: 11px;
        background: rgba(124,92,255,0.05);
    }

    .source-name {
        font-size: 0.86rem;
        font-weight: 700;
        margin-bottom: 0.4rem;
        overflow-wrap: anywhere;
    }

    .source-text {
        font-size: 0.83rem;
        line-height: 1.7;
        opacity: 0.78;
        overflow-wrap: anywhere;
    }

    /* FOOTER */

    .app-footer {
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid rgba(128,128,128,0.15);
        text-align: center;
        font-size: 0.78rem;
        opacity: 0.55;
    }

    @media (max-width: 768px) {
        .block-container {
            padding: 1rem;
        }

        .hero {
            padding: 1.5rem;
        }

        .hero h1 {
            font-size: 1.8rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# LOAD RAG
# =========================================================

@st.cache_resource(show_spinner="Loading command knowledge base...")
def load_rag():
    import rag
    return rag


rag = load_rag()

# =========================================================
# SESSION STATE
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "pending" not in st.session_state:
    st.session_state.pending = None

if "show_sources" not in st.session_state:
    st.session_state.show_sources = True

# =========================================================
# HELPER FUNCTIONS
# =========================================================

def set_pending(question):
    st.session_state.pending = question


def render_sources(sources):
    with st.expander(
        f"📚 Reference documents ({len(sources)})",
        expanded=False,
    ):
        if not sources:
            st.caption("No reference documents were retrieved.")
            return

        for index, source in enumerate(sources, start=1):
            name = html.escape(str(source.get("name", "Unknown source")))
            content = html.escape(str(source.get("text", "")))

            st.markdown(
                f"""
                <div class="source-card">
                    <div class="source-name">
                        📄 {index}. {name}
                    </div>
                    <div class="source-text">{content}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        """
        <div class="sidebar-brand">
            <h3>💻 Command Assistant</h3>
            <p>Git & Linux command help, explanations and troubleshooting.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### ⚙️ Settings")

    st.toggle(
        "Show reference documents",
        key="show_sources",
    )

    st.caption(f"Document retrieval: {DEFAULT_K} chunks")

    st.divider()

    if st.button("🗑️ Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_history = []
        st.session_state.pending = None
        st.rerun()

    if st.session_state.messages:

        chat_text = "\n\n".join(
            f"{message['role'].upper()}: {message['content']}"
            for message in st.session_state.messages
        )

        st.download_button(
            "⬇️ Export conversation",
            data=chat_text,
            file_name="git_linux_assistant_chat.txt",
            mime="text/plain",
            use_container_width=True,
        )

    st.divider()

    st.markdown(
        """
        <div style="font-size:0.78rem; opacity:0.65; line-height:1.9;">
            <b>Supported topics</b><br>
            🔀 Git & version control<br>
            🐧 Linux commands<br>
            🛠️ Error troubleshooting<br>
            📖 Command explanations
        </div>
        """,
        unsafe_allow_html=True,
    )

# =========================================================
# HEADER
# =========================================================

st.markdown(
    """
    <div class="hero">
        <div class="hero-badge">DEVELOPER PRODUCTIVITY ASSISTANT</div>
        <h1>Git & Linux Command Assistant</h1>
        <p>
            Find the right command, understand how it works, and
            troubleshoot common errors. Ask questions about Git,
            Linux terminal commands, and developer workflows.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# WELCOME SCREEN
# =========================================================

typed_question = st.chat_input(
    "Ask a Git or Linux question..."
)

question = typed_question or st.session_state.pending
st.session_state.pending = None

if not st.session_state.messages and not question:

    st.markdown(
        '<div class="section-title">What do you need help with?</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="section-subtitle">
            Select a topic to get started, or type your question below.
        </div>
        """,
        unsafe_allow_html=True,
    )

    examples = [
        {
            "icon": "🔀",
            "title": "Git Commands",
            "description": "Learn commits, branches, merging and remote repositories.",
            "question": "Explain the most useful Git commands with examples.",
        },
        {
            "icon": "🐧",
            "title": "Linux Commands",
            "description": "Explore files, directories, permissions and processes.",
            "question": "Explain essential Linux terminal commands with examples.",
        },
        {
            "icon": "🛠️",
            "title": "Fix an Error",
            "description": "Understand command errors and find possible solutions.",
            "question": "How do I troubleshoot common Git errors?",
        },
    ]

    columns = st.columns(3)

    for column, example in zip(columns, examples):

        with column:

            st.markdown(
                f"""
                <div class="suggestion-card">
                    <div class="suggestion-icon">{example['icon']}</div>
                    <h4>{example['title']}</h4>
                    <p>{example['description']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.button(
                "Explore topic →",
                key=f"example_{example['title']}",
                on_click=set_pending,
                args=(example["question"],),
                use_container_width=True,
            )

# =========================================================
# DISPLAY CHAT HISTORY
# =========================================================

for message in st.session_state.messages:

    avatar = "🧑‍💻" if message["role"] == "user" else "🤖"

    with st.chat_message(message["role"], avatar=avatar):

        st.markdown(message["content"])

        if message["role"] == "assistant":

            if message.get("time") is not None:
                st.caption(
                    f"⏱️ Response time: {message['time']:.1f}s"
                )

            if (
                message.get("sources")
                and st.session_state.show_sources
            ):
                render_sources(message["sources"])

# =========================================================
# HANDLE NEW QUESTION
# =========================================================

if question:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(question)

    with st.chat_message("assistant", avatar="🤖"):

        start = time.time()

        try:

            with st.spinner("🔎 Searching the command knowledge base..."):

                search_question = rag.rewrite_question(
                    question,
                    st.session_state.chat_history,
                )

                docs = rag.retrieve(
                    search_question,
                    DEFAULT_K,
                )

            answer = st.write_stream(
                rag.stream_answer(
                    question,
                    docs,
                    st.session_state.chat_history,
                )
            )

            elapsed = time.time() - start

            st.caption(f"⏱️ Response time: {elapsed:.1f}s")

            sources = [
                {
                    "name": document.metadata.get(
                        "source",
                        "Unknown source",
                    ),
                    "text": document.page_content[:250] + (
                        "..."
                        if len(document.page_content) > 250
                        else ""
                    ),
                }
                for document in docs
            ]

            if st.session_state.show_sources:
                render_sources(sources)

            # Update conversational history.

            from langchain_core.messages import HumanMessage, AIMessage

            st.session_state.chat_history.append(
                HumanMessage(content=question)
            )

            st.session_state.chat_history.append(
                AIMessage(content=answer)
            )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                    "sources": sources,
                    "time": elapsed,
                }
            )

        except Exception:

            # Avoid retaining a failed request as a completed exchange.
            if (
                st.session_state.messages
                and st.session_state.messages[-1]["role"] == "user"
                and st.session_state.messages[-1]["content"] == question
            ):
                st.session_state.messages.pop()

            st.error(
                "Unable to process your question. "
                "Check your LLM configuration and document index, "
                "then try again."
            )

# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="app-footer">
        Git & Linux Command Assistant
        <br>
        Built with Streamlit · Retrieval-Augmented Generation
    </div>
    """,
    unsafe_allow_html=True,
)