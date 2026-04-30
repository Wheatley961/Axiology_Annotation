import streamlit as st
import pandas as pd
import stanza
import sqlite3
import re
import os
import pymorphy2
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

MORPH_ORDER = ["падеж", "число", "род", "одушевленность", "наклонение/форма", "время", "лицо", "залог", "вид", "степень", "краткость", "прочее"]

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
        annotator_id TEXT,
        annotator_gender TEXT,
        annotator_age INTEGER,
        is_anonymous BOOLEAN,
        text_source TEXT,
        sentence_id INTEGER,
        word_form TEXT,
        lemma TEXT,
        pos TEXT,
        morph_features TEXT,
        syntactic_scheme TEXT,
        selected_axiologeme TEXT,
        morphemes TEXT,
        stylistic_type TEXT,
        stylistic_subtype TEXT,
        derivatives TEXT,
        illocutionary_force TEXT,
        is_direct_speech BOOLEAN,
        justification TEXT,
        timestamp TEXT
    )''')
    conn.commit()
    conn.close()

def save_annotation(data):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT INTO annotations (annotator_id, annotator_gender, annotator_age, is_anonymous,
                text_source, sentence_id, word_form, lemma, pos, morph_features, 
                syntactic_scheme, selected_axiologeme, morphemes, stylistic_type, stylistic_subtype, 
                derivatives, illocutionary_force, is_direct_speech, justification, timestamp) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (data['annotator_id'], data['annotator_gender'], data['annotator_age'], data['is_anonymous'],
               data['text_source'], data['sentence_id'], data['word_form'], data['lemma'], data['pos'], 
               data['morph_features'], data['syntactic_scheme'], data['selected_axiologeme'], data['morphemes'],
               data['stylistic_type'], data['stylistic_subtype'], data['derivatives'], data['illocutionary_force'],
               data['is_direct_speech'], data['justification'], data['timestamp']))
    conn.commit()
    conn.close()

def load_annotations():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM annotations", conn)
    conn.close()
    return df

init_db()

# ==========================================
# 3. NLP МОДУЛЬ
# ==========================================
@st.cache_resource
def load_stanza():
    try:
        stanza.download('ru', verbose=False)
        return stanza.Pipeline('ru', processors='tokenize,pos,lemma,depparse', verbose=False)
    except Exception as e:
        st.warning(f"⚠️ Stanza инициализация не прошла: {e}. Используется pymorphy2 (локально, быстро).")
        return None

def analyze_morphology(word):
    morph = pymorphy2.MorphAnalyzer()
    p = morph.parse(word)[0]
    # Формат: падеж-число-род-одушевленность-наклонение/форма-время-лицо-залог-вид-степень-краткость-прочее
    tags = {
        "падеж": p.tag.case or "X", "число": p.tag.number or "X", "род": p.tag.gender or "X",
        "одушевленность": p.tag.animacy or "X", "наклонение/форма": str(p.tag.mood or p.tag.person or "X"),
        "время": p.tag.tense or "X", "лицо": p.tag.person or "X", "залог": "X",
        "вид": p.tag.aspect or "X", "степень": p.tag.comparative or "X", "краткость": "полн." if not p.tag.shortness else "кратк.",
        "прочее": ""
    }
    return "-".join(tags.values()), p.normal_form, p.tag.POS or "X"

def get_syntax_scheme(word, sentence):
    # Простой fallback на основе pymorphy2 + контекст
    return f"контекст_анализ_{word[:4]}"

def is_direct_speech(sentence):
    return bool(re.search(r'^(–|—|"|«|“)|[–—]$', sentence.strip()))

def split_text_sentences(text):
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

# ==========================================
# 4. UI STREAMLIT
# ==========================================
st.set_page_config(page_title="Разметка Аксиологем", layout="wide")
st.title("📜 Лингвистическая разметка ценностей в тексте")

if 'annotator_confirmed' not in st.session_state: st.session_state.annotator_confirmed = False
if 'selected_word_data' not in st.session_state: st.session_state.selected_word_data = None
if 'admin_logged' not in st.session_state: st.session_state.admin_logged = False

# --- ШАГ 0: ИНФОРМАЦИЯ О РАЗМЕТЧИКЕ ---
st.header("👤 Шаг 1: Информация о разметчике")
if not st.session_state.annotator_confirmed:
    with st.form("annotator_form"):
        is_anon = st.checkbox("Анонимная разметка", value=True)
        if not is_anon:
            col1, col2 = st.columns(2)
            annot_id = col1.text_input("ID / Логин")
            gender = col2.selectbox("Пол", ["М", "Ж", "Не указан"])
            age = st.number_input("Возраст", min_value=16, max_value=100, value=25)
        else:
            annot_id, gender, age = "anon", "X", 0
            
        confirmed = st.form_submit_button("✅ Подтвердить и начать")
        if confirmed:
            st.session_state.annotator_info = {"id": annot_id, "gender": gender, "age": age, "is_anonymous": is_anon}
            st.session_state.annotator_confirmed = True
            st.rerun()
else:
    info = st.session_state.annotator_info
    st.success(f"✅ Разметчик: {info['id']}, Пол: {info['gender']}, Возраст: {info['age']}, Анонимно: {info['is_anonymous']}")
    st.divider()

    # --- ШАГ 1: ВЫБОР ТЕКСТА ---
    st.header("📖 Шаг 2: Выбор текста")
    text_mode = st.radio("Источник текста:", ["Демо-текст (встроенный)", "Ввести вручную"])
    raw_text = DEMO_TEXT if text_mode.startswith("Демо") else st.text_area("Вставьте ваш текст:", height=120)
    st.divider()

    if raw_text:
        # --- ШАГ 2: ВЫБОР АКСИОЛОГЕМ ---
        st.header("🎯 Шаг 3: Выбор аксиологем для разметки")
        st.info("Выберите одну или несколько ценностей, которые присутствуют в тексте. Разметка слов будет привязана к выбранным аксиологемам.")
        selected_axios = st.multiselect("Аксиологемы (Указ №809):", AXIOLOGEMES)
        
        if selected_axios:
            st.divider()
            # --- ШАГ 3: КЛИК ПО СЛОВАМ ---
            st.header("🖱️ Шаг 4: Кликните на слово-репрезентант")
            sentences = split_text_sentences(raw_text)
            
            # Отображение слов в виде кнопок
            cols = st.columns(8)
            word_counter = 0
            for s_idx, sent in enumerate(sentences):
                # Очистка от номеров предложений для клика
                clean_sent = re.sub(r'\(\d+\)', '', sent)
                words = re.findall(r'\b[а-яА-ЯёЁ\-]+\b', clean_sent)
                for w in words:
                    col = cols[word_counter % 8]
                    btn = col.button(w, key=f"btn_{s_idx}_{word_counter}", use_container_width=True)
                    if btn:
                        st.session_state.selected_word_data = {
                            "word": w,
                            "sentence": sent,
                            "sent_id": s_idx
                        }
                        st.rerun()
                    word_counter += 1

            # --- ШАГ 4: ФОРМА РАЗМЕТКИ ---
            if st.session_state.selected_word_data:
                st.divider()
                st.info(f"🔍 **Слово:** `{st.session_state.selected_word_data['word']}` | **Предложение №{st.session_state.selected_word_data['sent_id']}**")
                st.markdown(f"📖 *{st.session_state.selected_word_data['sentence']}*")
                
                w_data = st.session_state.selected_word_data
                auto_morph, lemma, pos = analyze_morphology(w_data["word"])
                syntax_scheme = get_syntax_scheme(w_data["word"], w_data["sentence"])
                is_direct = is_direct_speech(w_data["sentence"])

                st.subheader("📝 Введите параметры разметки")
                # Используем form БЕЗ key, чтобы избежать StreamlitValueAssignmentNotAllowedError
                with st.form("annotation_input_form"):
                    axio = st.selectbox("К какой аксиологеме относится это слово?", selected_axios)
                    
                    st.markdown("🔹 **Морфемный уровень**")
                    morphemes = st.multiselect("Присутствующие морфемы", 
                        ["диминутивные", "аугментативные", "мелиоративные", "пейоративные", 
                         "частичности", "недостаточности", "чрезмерности", "приблизительности"])
                    
                    st.markdown("🔹 **Морфологический уровень** (авто-заполнено, можно править)")
                    morph_features = st.text_input("Формат: падеж-число-род-одуш-накл-время-лицо-залог-вид-степень-кратк-прочее", value=auto_morph)
                    
                    st.markdown("🔹 **Синтаксический уровень**")
                    syntactic_scheme = st.text_input("Структурная схема словосочетания/контекста", value=syntax_scheme)
                    
                    st.markdown("🔹 **Стилистический уровень**")
                    col1, col2 = st.columns(2)
                    stylistic_type = col1.selectbox("Тип", list(STYLISTIC_HIERARCHY.keys()))
                    stylistic_subtype = col2.selectbox("Подтип", STYLISTIC_HIERARCHY.get(stylistic_type, []))
                    
                    st.markdown("🔹 **Деривационный уровень**")
                    derivatives = st.text_input("Производные в тексте (через запятую, если есть)")
                    
                    illoc_force = "Нет (не в прямой речи)"
                    if is_direct:
                        st.warning("⚠️ Слово находится в **прямой речи**. Укажите иллокутивную силу (Дж. Серль).")
                        illoc_force = st.selectbox("Иллокутивная сила", ILLOCUTIONARY_FORCES)
                        
                    justification = st.text_area("Обоснование выбора (кратко)")
                    
                    submitted = st.form_submit_button("💾 Сохранить аннотацию")
                    if submitted:
                        save_data = {
                            "annotator_id": info['id'], "annotator_gender": info['gender'],
                            "annotator_age": info['age'], "is_anonymous": info['is_anonymous'],
                            "text_source": "DEMO" if text_mode.startswith("Демо") else "CUSTOM",
                            "sentence_id": w_data['sent_id'], "word_form": w_data['word'],
                            "lemma": lemma, "pos": pos, "morph_features": morph_features,
                            "syntactic_scheme": syntactic_scheme, "selected_axiologeme": axio,
                            "morphemes": ", ".join(morphemes), "stylistic_type": stylistic_type,
                            "stylistic_subtype": stylistic_subtype, "derivatives": derivatives,
                            "illocutionary_force": illoc_force, "is_direct_speech": is_direct,
                            "justification": justification,
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        save_annotation(save_data)
                        st.success("✅ Аннотация успешно сохранена!")
                        st.session_state.selected_word_data = None
                        st.rerun()

                if st.button("❌ Отменить выбор слова"):
                    st.session_state.selected_word_data = None
                    st.rerun()

# --- TAB 2 & 3: УПРАВЛЕНИЕ И СТАТИСТИКА (внизу) ---
st.divider()
st.caption("Для просмотра данных и статистики обратитесь к панели управления.")
tab_ctrl, tab_stats = st.tabs(["🔐 Управление данными", "📊 Статистика"])

with tab_ctrl:
    st.subheader("📋 Размеченные данные")
    password = st.text_input("🔑 Пароль администратора:", type="password", key="admin_pass")
    if password == "axio2026":
        st.session_state.admin_logged = True
        
    if st.session_state.admin_logged:
        df = load_annotations()
        if df.empty:
            st.info("Пока нет сохраненных аннотаций.")
        else:
            st.dataframe(df, use_container_width=True)
            if st.button("🗑️ Очистить базу данных"):
                conn = sqlite3.connect(DB_PATH)
                conn.execute("DELETE FROM annotations")
                conn.commit()
                conn.close()
                st.success("База очищена.")
                st.rerun()
    else:
        st.info("🔒 Введите пароль для доступа.")

with tab_stats:
    st.subheader("📊 Визуальная аналитика")
    df = load_annotations()
    if df.empty:
        st.warning("Нет данных для отображения статистики.")
    else:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### Распределение аксиологем")
            axio_counts = df["selected_axiologeme"].value_counts().reset_index()
            axio_counts.columns = ["Аксиологема", "Количество"]
            st.bar_chart(axio_counts.set_index("Аксиологема"))
        with c2:
            st.markdown("### Иллокутивные силы (прямая речь)")
            illoc_df = df[df["is_direct_speech"]]
            if not illoc_df.empty:
                illoc_counts = illoc_df["illocutionary_force"].value_counts().reset_index()
                illoc_counts.columns = ["Сила", "Количество"]
                st.bar_chart(illoc_counts.set_index("Сила"))
            else:
                st.info("Нет разметки прямой речи.")
