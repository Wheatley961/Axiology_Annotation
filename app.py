import streamlit as st
import pandas as pd
from docx import Document
import plotly.express as px

# -------------------------
# Настройки
# -------------------------
PASSWORD = "admin123"

st.set_page_config(layout="wide")

# -------------------------
# Загрузка docx
# -------------------------
def load_docx(file_path):
    doc = Document(file_path)
    return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])

demo_text = load_docx("Текст для разметки.docx")

# -------------------------
# Состояние
# -------------------------
if "annotations" not in st.session_state:
    st.session_state.annotations = []

if "selected_words" not in st.session_state:
    st.session_state.selected_words = []

# -------------------------
# Навигация
# -------------------------
menu = st.sidebar.radio(
    "Меню",
    ["Разметка", "Таблица", "Статистика", "Просмотр"]
)

# -------------------------
# 1. РАЗМЕТКА
# -------------------------
if menu == "Разметка":
    st.title("📝 Разметка текста")

    mode = st.radio("Источник текста:", ["Демо", "Ввод вручную"])

    if mode == "Демо":
        text = demo_text
    else:
        text = st.text_area("Введите текст")

    # Разбивка на слова
    words = text.split()

    st.subheader("Выберите слова-репрезентанты (клик)")

    cols = st.columns(8)
    for i, word in enumerate(words):
        if cols[i % 8].button(word):
            st.session_state.selected_words.append(word)

    st.write("Выбранные слова:", st.session_state.selected_words)

    # Выбор аксиологемы
    axiology = st.selectbox(
        "Аксиологема",
        [
            "жизнь", "достоинство", "свобода", "патриотизм",
            "семья", "труд", "гуманизм", "справедливость"
        ]
    )

    # Доп. параметры
    pos = st.selectbox("Часть речи", ["NOUN", "VERB", "ADJ", "ADV", "OTHER"])
    sentence_id = st.number_input("Номер предложения", 1)

    if st.button("Сохранить разметку"):
        for w in st.session_state.selected_words:
            st.session_state.annotations.append({
                "word": w,
                "axiology": axiology,
                "pos": pos,
                "sentence": sentence_id
            })
        st.session_state.selected_words = []
        st.success("Сохранено!")

# -------------------------
# 2. ТАБЛИЦА
# -------------------------
elif menu == "Таблица":
    st.title("📊 Таблица разметки")

    df = pd.DataFrame(st.session_state.annotations)

    if df.empty:
        st.info("Нет данных")
    else:
        st.dataframe(df, use_container_width=True)

        st.subheader("Редактирование (требуется пароль)")
        password = st.text_input("Пароль", type="password")

        if password == PASSWORD:
            idx = st.number_input("ID строки", 0, len(df)-1)

            if st.button("Удалить строку"):
                st.session_state.annotations.pop(idx)
                st.success("Удалено")

        else:
            st.warning("Введите пароль для редактирования")

# -------------------------
# 3. СТАТИСТИКА
# -------------------------
elif menu == "Статистика":
    st.title("📈 Статистика")

    df = pd.DataFrame(st.session_state.annotations)

    if df.empty:
        st.info("Нет данных")
    else:
        col1, col2 = st.columns(2)

        with col1:
            fig1 = px.histogram(df, x="axiology", title="Аксиологемы")
            st.plotly_chart(fig1)

        with col2:
            fig2 = px.histogram(df, x="pos", title="Части речи")
            st.plotly_chart(fig2)

        fig3 = px.histogram(df, x="word", title="Частота слов")
        st.plotly_chart(fig3)

# -------------------------
# 4. ПРОСМОТР + ФИЛЬТР
# -------------------------
elif menu == "Просмотр":
    st.title("🔍 Просмотр и фильтрация")

    df = pd.DataFrame(st.session_state.annotations)

    if df.empty:
        st.info("Нет данных")
    else:
        ax_filter = st.multiselect("Аксиологема", df["axiology"].unique())
        word_filter = st.multiselect("Слова", df["word"].unique())

        filtered = df.copy()

        if ax_filter:
            filtered = filtered[filtered["axiology"].isin(ax_filter)]

        if word_filter:
            filtered = filtered[filtered["word"].isin(word_filter)]

        st.dataframe(filtered, use_container_width=True)
