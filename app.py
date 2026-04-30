import streamlit as st
import pandas as pd
import re
from collections import Counter

st.set_page_config(layout="wide")

# -------------------------
# CONFIG
# -------------------------
PASSWORD = "admin123"

# -------------------------
# DEMO TEXT (EMBEDDED)
# -------------------------
demo_text = """(1)В один прекрасный день мы – пять девочек – карабкаемся на Замковую гору. (2)В руках у нас большие пёстрые букеты разноцветных опавших листьев – больше всего кленовых.
(3)Вдруг из-за обломков стены слышен мужской голос, глубокий, странно-певучий, полный страстного чувства.
(4)Мы словно окаменели. (5)Нас захватило дыхание большой любви, о которой почти поёт голос за стеной, читающий письмо Евгения Онегина.
(6)Только мы двинулись – из-за стены опять раздаётся тот же голос. (7)Теперь он читает – я узнаю с первых слов – монолог Чацкого из «Горя от ума». (8)Он читает всё так же певуче – ну совсем поёт! – но с гневом, с яростью оскорблённого чувства…
(9)Не сговариваясь, мы выбегаем из-за стены: мы хотим увидеть того, кто прочитал, почти пропел нам эти отрывки из Пушкина и Грибоедова.
(10)Мы выбежали – смотрим во все глаза: никого! (11)Ни Онегина, ни Чацкого… (12)Нет, впрочем, какой-то человек очень робко и застенчиво жмётся к тому обломку стены, из-за которой мы только что слушали чудный голос. (13)Это юноша лет шестнадцати-семнадцати, на нём старенькая, поношенная ученическая шинель, только пуговицы уже не форменные – значит, бывший ученик.
(14)Мы идём к нему, всё еще заворожённые тем, что слышали; нам не верится, что невидимый чтец – этот нескладный парень в обшарпанной бывшей ученической шинели. (15)Но он смотрит на нас – у него прекрасные глаза, необычно удлинённые к вискам, с глубоким, умным взглядом, – и мы понимаем: да, это он сейчас читал!
(16)Мы протягиваем ему свои пёстрые осенние букеты из листьев всех расцветок.
(17)Юноша очень смущён.
– (18)В-в-вы эт-то м-м-мне? (19)Ч-ч-что вы? (20)З-за что?
(21)Очень странно слышать: тот же голос – и так сильно заикается!
– (22)Нет, нет, пожалуйста, возьмите! – просим мы его хором.
(23)Юноша застенчиво пожимает плечами. (24)Потом берёт наш букет и улыбается нам хорошей, дружелюбной улыбкой:
– С-с-п-п-пасибо!
(25)И, неловко поклонившись, он быстро уходит, прижимая к груди наши смешные букеты из листьев. (26)Вот его шинель мелькнула в густой щётке кустов калины, вот он уже спускается с горы – исчез из виду.
(27)Теперь я знаю: юноша в затасканной ученической шинели был Илларион Певцов. (28)Он был тяжёлый и, как все считали, неизлечимый заика. (29)А он мечтал стать актёром! (30)И у него в самом деле был талант! (31)Он уходил за город, в лес, взбирался на горы; там он декламировал, читал монологи, отрывки из пьес. (32)Над ним насмехались, считали его полоумным. (33)Но он превозмог непреодолимое, он сделал невозможное: через пятнадцать – двадцать лет после этой нашей встречи с ним на Замковой горе он стал одним из самых замечательных русских актёров. (34)Бывали и у него срывы, полосы, когда он не мог играть, потому что лишался силы управлять своей речью и побеждать её недостаток. (35)И всё же он не отчаивался, у него не опускались руки!
(36)Когда я думаю о людях сильной воли, сильной страсти к искусству, я всегда вспоминаю его – чудесного актёра Иллариона Певцова. (37)И мне приятно думать, что наши смешные попугайно-пёстрые букеты из осенних листьев были, может статься, первыми цветами, поднесёнными ему на трудном, но победном пути.
"""

AXIOLOGIES = [
    "жизнь","достоинство","свобода","патриотизм",
    "семья","труд","гуманизм","справедливость"
]

POS_TAGS = ["NOUN","VERB","ADJ","ADV","OTHER"]

# -------------------------
# SESSION STATE
# -------------------------
if "annotations" not in st.session_state:
    st.session_state.annotations = []

if "selected_words" not in st.session_state:
    st.session_state.selected_words = []

if "user" not in st.session_state:
    st.session_state.user = "anon"

# -------------------------
# HELPERS
# -------------------------

def split_sentences(text):
    sentences = re.split(r"\(\d+\)", text)
    return [s.strip() for s in sentences if s.strip()]


def tokenize(sentence):
    return re.findall(r"\w+", sentence, re.UNICODE)

# -------------------------
# SIDEBAR
# -------------------------
st.sidebar.title("Настройки")
st.session_state.user = st.sidebar.text_input("Аннотатор", "anon")

menu = st.sidebar.radio("Меню", [
    "Разметка",
    "Таблица",
    "Статистика",
    "Просмотр"
])

# -------------------------
# 1. ANNOTATION
# -------------------------
if menu == "Разметка":
    st.title("📝 Разметка текста")

    mode = st.radio("Источник", ["Демо", "Ввод"])

    text = demo_text if mode == "Демо" else st.text_area("Текст")

    sentences = split_sentences(text)

    sent_id = st.selectbox("Предложение", range(len(sentences)), format_func=lambda i: sentences[i][:80])

    current_sentence = sentences[sent_id]
    words = tokenize(current_sentence)

    st.subheader("Клик по словам")

    cols = st.columns(8)
    for i, w in enumerate(words):
        if cols[i % 8].button(w):
            st.session_state.selected_words.append(w)

    st.write("Выбрано:", st.session_state.selected_words)

    # AXIOLOGY MULTI
    axiologies = st.multiselect("Аксиологемы", AXIOLOGIES)

    pos = st.selectbox("Часть речи", POS_TAGS)

    # MORPHEME LEVEL
    st.subheader("Морфемный уровень")
    morph = st.multiselect("Типы морфем", [
        "диминутив",
        "аугментатив",
        "мелиоратив",
        "пейоратив",
        "частичность",
        "недостаточность",
        "чрезмерность",
        "приблизительность"
    ])

    # STYLISTIC
    st.subheader("Стилистика")
    stylistic = st.multiselect("Средства", [
        "метафора","эпитет","сравнение","гипербола",
        "риторический вопрос","анафора"
    ])

    if st.button("Сохранить"):
        for w in st.session_state.selected_words:
            st.session_state.annotations.append({
                "word": w,
                "axiology": ",".join(axiologies),
                "pos": pos,
                "sentence_id": sent_id,
                "sentence": current_sentence,
                "morph": ",".join(morph),
                "stylistic": ",".join(stylistic),
                "annotator": st.session_state.user
            })

        st.session_state.selected_words = []
        st.success("Сохранено")

# -------------------------
# 2. TABLE + ADMIN
# -------------------------
elif menu == "Таблица":
    st.title("📊 Таблица")

    df = pd.DataFrame(st.session_state.annotations)

    if df.empty:
        st.info("Нет данных")
    else:
        st.dataframe(df, use_container_width=True)

        st.subheader("Админ")
        password = st.text_input("Пароль", type="password")

        if password == PASSWORD:
            idx = st.number_input("ID", 0, len(df)-1)

            if st.button("Удалить"):
                st.session_state.annotations.pop(idx)
                st.success("Удалено")

# -------------------------
# 3. STATS
# -------------------------
elif menu == "Статистика":
    st.title("📈 Статистика")

    df = pd.DataFrame(st.session_state.annotations)

    if not df.empty:
        st.bar_chart(df["axiology"].value_counts())
        st.bar_chart(df["pos"].value_counts())

        # annotators
        st.subheader("Аннотаторы")
        st.bar_chart(df["annotator"].value_counts())

# -------------------------
# 4. FILTER VIEW
# -------------------------
elif menu == "Просмотр":
    st.title("🔍 Фильтрация")

    df = pd.DataFrame(st.session_state.annotations)

    if not df.empty:
        ax = st.multiselect("Аксиология", df["axiology"].unique())
        user = st.multiselect("Аннотатор", df["annotator"].unique())

        filtered = df.copy()

        if ax:
            filtered = filtered[filtered["axiology"].isin(ax)]

        if user:
            filtered = filtered[filtered["annotator"].isin(user)]

        st.dataframe(filtered, use_container_width=True)
