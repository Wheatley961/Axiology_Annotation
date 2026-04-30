import streamlit as st
import pandas as pd
import stanza
import sqlite3
import re
import os
import pymorphy3
from datetime import datetime

# ==========================================
# 1. КОНСТАНТЫ И НАСТРОЙКИ
# ==========================================
AXIOLOGEMES = [
    "жизнь", "достоинство", "права и свободы человека", "патриотизм", "гражданственность",
    "служение Отечеству и ответственность за его судьбу", "высокие нравственные идеалы", "крепкая семья",
    "созидательный труд", "приоритет духовного над материальным", "гуманизм", "милосердие",
    "справедливость", "коллективизм", "взаимопомощь и взаимоуважение",
    "историческая память и преемственность поколений", "единство (народов России)"
]

STYLISTIC_HIERARCHY = {
    "Фонетические": ["ассонанс", "аллитерация", "звукоподражание"],
    "Синтаксические": ["анафора", "эпифора", "антитеза", "градация", "инверсия", "параллелизм",
                       "хиазм", "эллипсис", "умолчание", "риторический вопрос", "риторическое восклицание",
                       "риторическое обращение", "многосоюзие", "бессоюзие", "парцелляция",
                       "синтаксический повтор", "присоединительные конструкции", "именительный темы", "сегментация"],
    "Тропы": ["метафора", "метонимия", "синекдоха", "эпитет", "сравнение", "олицетворение",
              "гипербола", "литота", "ирония", "сарказм", "перифраз", "аллегория", "символ",
              "оксюморон", "эвфемизм", "дисфемизм"]
}

ILLOCUTIONARY_FORCES = [
    "репрезентативы", "директивы", "комиссивы", "экспрессивы", "декларации"
]

DEMO_TEXT = """(1)В один прекрасный день мы – пять девочек – карабкаемся на Замковую гору. (2)В руках у нас большие пёстрые букеты разноцветных опавших листьев – больше всего кленовых.
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
(36)Когда я думаю о людях сильной воли, сильной страсти к искусству, я всегда вспоминаю его – чудесного актёра Иллариона Певцова. (37)И мне приятно думать, что наши смешные попугайно-пёстрые букеты из осенних листьев были, может статься, первыми цветами, поднесёнными ему на трудном, но победном пути."""

# ==========================================
# 2. БАЗА ДАННЫХ
# ==========================================
DB_PATH = "axiology_annotations.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS annotations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text_source TEXT,
        sentence_id INTEGER,
        word_form TEXT,
        lemma TEXT,
        pos TEXT,
        morph_features TEXT,
        syntactic_scheme TEXT,
        axiologeme TEXT,
        morphemes TEXT,
        stylistic_type TEXT,
        stylistic_subtype TEXT,
        illocutionary_force TEXT,
        is_direct_speech BOOLEAN,
        timestamp TEXT
    )''')
    conn.commit()
    conn.close()

def save_annotation(data):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT INTO annotations (text_source, sentence_id, word_form, lemma, pos, morph_features, 
                syntactic_scheme, axiologeme, morphemes, stylistic_type, stylistic_subtype, 
                illocutionary_force, is_direct_speech, timestamp) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (data['text_source'], data['sentence_id'], data['word_form'], data['lemma'], data['pos'], 
               data['morph_features'], data['syntactic_scheme'], data['axiologeme'], data['morphemes'],
               data['stylistic_type'], data['stylistic_subtype'], data['illocutionary_force'],
               data['is_direct_speech'], data['timestamp']))
    conn.commit()
    conn.close()

def load_annotations():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM annotations", conn)
    conn.close()
    return df

init_db()

# ==========================================
# 3. NLP МОДУЛЬ (STANZA + FALLBACK)
# ==========================================
@st.cache_resource
def load_stanza():
    try:
        if not os.path.exists("stanza_resources/ru"):
            stanza.download("ru", dir="stanza_resources", verbose=False)
        return stanza.Pipeline('ru', dir='stanza_resources', processors='tokenize,pos,lemma,depparse', verbose=False)
    except Exception as e:
        st.warning(f"Stanza не загрузился: {e}. Используется легковесный fallback (pymorphy3).")
        return None

def analyze_word(word, sentence_text):
    nlp = load_stanza()
    morph = pymorphy3.MorphAnalyzer()
    
    # Fallback if stanza failed
    if nlp is None:
        p = morph.parse(word)[0]
        return {
            "lemma": p.normal_form,
            "pos": p.tag.POS or "X",
            "morph": str(p.tag),
            "syntax": "X"
        }

    try:
        doc = nlp(sentence_text)
        for sent in doc.sentences:
            for token in sent.tokens:
                if token.text.lower() == word.lower():
                    word_obj = token.words[0]
                    head = word_obj.head
                    deprel = word_obj.deprel
                    
                    # Простая структурная схема: HEAD_POS-DEPREL-WORD_POS
                    head_pos = "X"
                    for t in sent.tokens:
                        if t.id == head:
                            head_pos = t.words[0].upos
                            break
                    syntax_scheme = f"{head_pos}_{deprel}_{word_obj.upos}"
                    
                    return {
                        "lemma": word_obj.lemma,
                        "pos": word_obj.upos,
                        "morph": f"Case={word_obj.feats.get('Case','X')}|Num={word_obj.feats.get('Number','X')}|Anim={word_obj.feats.get('Animacy','X')}",
                        "syntax": syntax_scheme
                    }
    except:
        pass
    
    p = morph.parse(word)[0]
    return {"lemma": p.normal_form, "pos": p.tag.POS or "X", "morph": str(p.tag), "syntax": "X"}

# ==========================================
# 4. ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ==========================================
def is_direct_speech(sentence):
    return bool(re.search(r'^(–|—|"|«|“)|[–—]$', sentence.strip()))

def split_text_sentences(text):
    # Простое разбиение с сохранением нумерации (N)
    parts = re.split(r'(\(\d+\))', text)
    sentences = []
    current = ""
    for p in parts:
        if re.match(r'^\(\d+\)$', p):
            if current.strip(): sentences.append(current.strip())
            current = p + " "
        else:
            current += p
    if current.strip(): sentences.append(current.strip())
    return sentences

def get_word_context(text, target_word):
    sentences = split_text_sentences(text)
    for i, sent in enumerate(sentences):
        if target_word.lower() in sent.lower():
            return i, sent
    return 0, text

# ==========================================
# 5. UI STREAMLIT
# ==========================================
st.set_page_config(page_title="Разметка Аксиологем", layout="wide")
st.title("📜 Лингвистическая разметка ценностей в тексте")

if 'selected_word' not in st.session_state: st.session_state.selected_word = None
if 'annotation_form' not in st.session_state: st.session_state.annotation_form = False
if 'admin_logged' not in st.session_state: st.session_state.admin_logged = False

tab1, tab2, tab3 = st.tabs(["📝 Аннотация", "🔐 Управление данными", "📊 Статистика"])

# --- TAB 1: АННОТАЦИЯ ---
with tab1:
    st.subheader("Выбор и подготовка текста")
    text_mode = st.radio("Режим ввода:", ["Демо-текст (встроенный)", "Ввести вручную"])
    if text_mode == "Демо-текст (встроенный)":
        raw_text = DEMO_TEXT
    else:
        raw_text = st.text_area("Вставьте ваш текст:", height=150)

    if raw_text:
        st.subheader("Кликните на слово для разметки")
        sentences = split_text_sentences(raw_text)
        
        # Отрисовка слов как кнопок
        cols = st.columns(8)
        word_idx = 0
        for s_idx, sent in enumerate(sentences):
            words = re.findall(r'\b\w+[\w\-’]*\b', sent)
            for w in words:
                col = cols[word_idx % 8]
                btn = col.button(w, key=f"btn_{s_idx}_{word_idx}", use_container_width=True)
                if btn:
                    st.session_state.selected_word = w
                    st.session_state.selected_sentence = sent
                    st.session_state.selected_sent_id = s_idx
                    st.session_state.annotation_form = True
                word_idx += 1

        if st.session_state.selected_word and st.session_state.annotation_form:
            st.divider()
            st.info(f"🔍 **Слово:** `{st.session_state.selected_word}` | **Предложение №{st.session_state.selected_sent_id}**")
            st.markdown(f"📖 *{st.session_state.selected_sentence}*")

            is_direct = is_direct_speech(st.session_state.selected_sentence)
            auto_data = analyze_word(st.session_state.selected_word, st.session_state.selected_sentence)

            with st.form("annotation_form"):
                axiologeme = st.selectbox("Аксиологема", AXIOLOGEMES)
                
                st.markdown("🔹 **Морфемный уровень** (выберите подходящие)")
                morphemes = st.multiselect("", 
                    ["диминутивные", "аугментативные", "мелиоративные", "пейоративные", 
                     "частичности", "недостаточности", "чрезмерности", "приблизительности"])
                
                st.markdown("🔹 **Стилистический уровень**")
                col1, col2 = st.columns(2)
                stylistic_type = col1.selectbox("Тип", list(STYLISTIC_HIERARCHY.keys()))
                stylistic_subtype = col2.selectbox("Подтип", STYLISTIC_HIERARCHY.get(stylistic_type, []))

                illoc_force = "Нет (не в прямой речи)"
                if is_direct:
                    st.warning("⚠️ Слово находится в прямой речи.")
                    illoc_force = st.selectbox("Иллокутивная сила (Дж. Серль)", ILLOCUTIONARY_FORCES)

                derivatives = st.text_input("Производные в тексте (через запятую)", "")
                notes = st.text_area("Примечания / Обоснование выбора", "")

                submitted = st.form_submit_button("💾 Сохранить разметку")
                if submitted:
                    save_data = {
                        "text_source": "DEMO" if text_mode.startswith("Демо") else "CUSTOM",
                        "sentence_id": st.session_state.selected_sent_id,
                        "word_form": st.session_state.selected_word,
                        "lemma": auto_data["lemma"],
                        "pos": auto_data["pos"],
                        "morph_features": auto_data["morph"],
                        "syntactic_scheme": auto_data["syntax"],
                        "axiologeme": axiologeme,
                        "morphemes": ", ".join(morphemes),
                        "stylistic_type": stylistic_type,
                        "stylistic_subtype": stylistic_subtype,
                        "illocutionary_force": illoc_force,
                        "is_direct_speech": is_direct,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    save_annotation(save_data)
                    st.success("✅ Аннотация сохранена!")
                    st.session_state.annotation_form = False
                    st.rerun()

# --- TAB 2: УПРАВЛЕНИЕ ---
with tab2:
    password = st.text_input("🔑 Введите пароль администратора для доступа к данным:", type="password")
    if password == "axio2026": # В продакшене используйте хеширование!
        st.session_state.admin_logged = True

    if st.session_state.admin_logged:
        st.subheader("📋 Размеченные данные")
        df = load_annotations()
        if df.empty:
            st.info("Пока нет сохраненных аннотаций.")
        else:
            # Фильтрация
            filter_source = st.multiselect("Фильтр по источнику:", df["text_source"].unique().tolist(), default=df["text_source"].unique().tolist())
            df_filtered = df[df["text_source"].isin(filter_source)]
            
            st.dataframe(df_filtered, use_container_width=True)
            
            if st.button("🗑️ Очистить все данные"):
                conn = sqlite3.connect(DB_PATH)
                conn.execute("DELETE FROM annotations")
                conn.commit()
                conn.close()
                st.success("База очищена.")
                st.rerun()
    else:
        st.info("🔒 Доступ закрыт. Введите пароль.")

# --- TAB 3: СТАТИСТИКА ---
with tab3:
    st.subheader("📊 Визуальная аналитика")
    df = load_annotations()
    if df.empty:
        st.warning("Нет данных для отображения статистики.")
    else:
        st.markdown("### Распределение аксиологем")
        axio_counts = df["axiologeme"].value_counts().reset_index()
        axio_counts.columns = ["Аксиологема", "Количество"]
        st.bar_chart(axio_counts.set_index("Аксиологема"))

        st.markdown("### Распределение по частям речи")
        pos_counts = df["pos"].value_counts().reset_index()
        pos_counts.columns = ["Часть речи", "Количество"]
        st.bar_chart(pos_counts.set_index("Часть речи"))

        st.markdown("### Иллокутивные силы (в прямой речи)")
        illoc_df = df[df["is_direct_speech"]]
        if not illoc_df.empty:
            illoc_counts = illoc_df["illocutionary_force"].value_counts().reset_index()
            illoc_counts.columns = ["Иллокутивная сила", "Количество"]
            st.bar_chart(illoc_counts.set_index("Иллокутивная сила"))
        else:
            st.info("Нет разметки для прямой речи.")
