import streamlit as st
import pandas as pd
import sqlite3
import re
import pymorphy3
from datetime import datetime
from collections import defaultdict

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

ILLOCUTIONARY_FORCES = ["репрезентативы", "директивы", "комиссивы", "экспрессивы", "декларации"]

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
# 2. БАЗА ДАННЫХ И АВТОМИГРАЦИЯ
# ==========================================
DB_PATH = "axiology_annotations.db"
EXPECTED_SCHEMA = {
    'annotator_id': 'TEXT', 'annotator_gender': 'TEXT', 'annotator_age': 'INTEGER',
    'is_anonymous': 'BOOLEAN', 'text_source': 'TEXT', 'sentence_id': 'INTEGER',
    'word_form': 'TEXT', 'lemma': 'TEXT', 'pos': 'TEXT', 'morph_features': 'TEXT',
    'syntactic_scheme': 'TEXT', 'selected_axiologeme': 'TEXT', 'morphemes': 'TEXT',
    'stylistic_type': 'TEXT', 'stylistic_subtype': 'TEXT', 'derivatives': 'TEXT',
    'illocutionary_force': 'TEXT', 'is_direct_speech': 'BOOLEAN',
    'sentence_context': 'TEXT', 'justification': 'TEXT', 'timestamp': 'TEXT'
}

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    cols_def = "id INTEGER PRIMARY KEY AUTOINCREMENT, " + ", ".join([f"{k} {v}" for k, v in EXPECTED_SCHEMA.items()])
    c.execute(f"CREATE TABLE IF NOT EXISTS annotations ({cols_def})")
    
    # Автоматическое добавление новых столбцов при обновлении кода
    c.execute("PRAGMA table_info(annotations)")
    existing_cols = {row[1] for row in c.fetchall()}
    for col, col_type in EXPECTED_SCHEMA.items():
        if col not in existing_cols:
            c.execute(f"ALTER TABLE annotations ADD COLUMN {col} {col_type}")
    conn.commit()
    conn.close()

def save_annotation(data):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        cols = ", ".join(EXPECTED_SCHEMA.keys())
        placeholders = ", ".join(["?"] * len(EXPECTED_SCHEMA))
        vals = [data.get(k, None) for k in EXPECTED_SCHEMA.keys()]
        c.execute(f"INSERT INTO annotations ({cols}) VALUES ({placeholders})", vals)
        conn.commit()
        return True
    except sqlite3.Error as e:
        st.error(f"❌ Ошибка БД: {e}")
        return False
    finally:
        conn.close()

def load_annotations():
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query("SELECT * FROM annotations", conn)
    except Exception:
        df = pd.DataFrame()
    conn.close()
    for col in EXPECTED_SCHEMA.keys():
        if col not in df.columns:
            df[col] = None
    return df

init_db()

# ==========================================
# 3. NLP МОДУЛЬ (pymorphy3)
# ==========================================
morph = pymorphy3.MorphAnalyzer()

def analyze_morphology(word):
    parses = morph.parse(word)
    if not parses: return "X-X-X-X-X-X-X-X-X-X-X-X", word, "X"
    p = parses[0]; tag = p.tag
    safe = lambda attr: str(getattr(tag, attr, None) or "X")
    is_short = "кратк" if getattr(tag, 'shortness', False) else ("кратк" if "кратк" in str(tag).lower() else "полн")
    return f"{safe('case')}-{safe('number')}-{safe('gender')}-{safe('animacy')}-{safe('mood')}-{safe('tense')}-{safe('person')}-{safe('voice')}-{safe('aspect')}-{safe('comparative')}-{is_short}-X", p.normal_form, tag.POS or "X"

def is_direct_speech(sentence):
    return bool(re.search(r'^(–|—|"|«|“)|[–—]$', sentence.strip()))

def split_text_sentences(text):
    parts, sentences, current = re.split(r'(\(\d+\))', text), [], ""
    for p in parts:
        if re.match(r'^\(\d+\)$', p):
            if current.strip(): sentences.append(current.strip())
            current = p + " "
        else: current += p
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
if 'axio_counts' not in st.session_state: st.session_state.axio_counts = defaultdict(int)

# --- ШАГ 0: ИНФОРМАЦИЯ О РАЗМЕТЧИКЕ ---
st.header("👤 Шаг 1: Информация о разметчике")
if not st.session_state.annotator_confirmed:
    with st.form("annotator_form"):
        is_anon = st.checkbox("Анонимная разметка", value=True)
        if not is_anon:
            c1, c2 = st.columns(2)
            annot_id = c1.text_input("ID / Логин")
            gender = c2.selectbox("Пол", ["М", "Ж", "Не указан"])
            age = st.number_input("Возраст", min_value=16, max_value=100, value=25)
        else: annot_id, gender, age = "anon", "X", 0
        if st.form_submit_button("✅ Подтвердить и начать"):
            st.session_state.annotator_info = {"id": annot_id, "gender": gender, "age": age, "is_anonymous": is_anon}
            st.session_state.annotator_confirmed = True
            st.rerun()
else:
    info = st.session_state.annotator_info
    st.success(f"✅ Разметчик: {info['id']} | Пол: {info['gender']} | Возраст: {info['age']} | Анонимно: {info['is_anonymous']}")
    st.divider()

    # --- ШАГ 1: ВЫБОР ТЕКСТА И ПРОСМОТР ---
    st.header("📖 Шаг 2: Выбор и чтение текста")
    text_mode = st.radio("Источник текста:", ["Демо-текст (встроенный)", "Ввести вручную"])
    raw_text = DEMO_TEXT if text_mode.startswith("Демо") else st.text_area("Вставьте ваш текст:", height=100)
    
    st.divider()
    st.markdown("📄 **Полный текст для ознакомления:**")
    st.text_area("Текст:", value=raw_text or "", height=250, disabled=True, label_visibility="collapsed")
    st.divider()

    if raw_text:
        # --- ШАГ 2: ВЫБОР АКСИОЛОГЕМ ---
        st.header("🎯 Шаг 3: Выбор аксиологем")
        st.info("Выберите ценности. На каждую аксиологему допускается **не более 5 слов-репрезентантов**.")
        selected_axios = st.multiselect("Аксиологемы (Указ №809):", AXIOLOGEMES)
        
        if selected_axios:
            cols_info = st.columns(min(len(selected_axios), 4))
            for i, ax in enumerate(selected_axios):
                left = max(0, 5 - st.session_state.axio_counts.get(ax, 0))
                cols_info[i % 4].metric(label=ax, value=f"{left} слотов")
        
        if selected_axios:
            st.divider()
            # --- ШАГ 3: КЛИК ПО СЛОВАМ ---
            st.header("🖱️ Шаг 4: Кликните на слово-репрезентант")
            sentences = split_text_sentences(raw_text)
            cols = st.columns(8)
            wc = 0
            for s_idx, sent in enumerate(sentences):
                clean_sent = re.sub(r'\(\d+\)', '', sent)
                words = re.findall(r'\b[а-яА-ЯёЁ\-]+\b', clean_sent)
                for w in words:
                    col = cols[wc % 8]
                    if col.button(w, key=f"btn_{s_idx}_{wc}", use_container_width=True):
                        can = True
                        for ax in selected_axios:
                            if st.session_state.axio_counts.get(ax, 0) >= 5:
                                st.error(f"❌ Лимит (5 слов) для '{ax}' превышен.")
                                can = False; break
                        if can:
                            st.session_state.selected_word_data = {"word": w, "sentence": sent, "sent_id": s_idx}
                            st.rerun()
                    wc += 1

            # --- ШАГ 4: ФОРМА РАЗМЕТКИ (ИСПРАВЛЕНО) ---
            if st.session_state.selected_word_data:
                st.divider()
                wd = st.session_state.selected_word_data
                st.info(f"🔍 **Слово:** `{wd['word']}` | **Предложение №{wd['sent_id']}**")
                st.markdown(f"📖 *{wd['sentence']}*")
                
                auto_morph, lemma, pos = analyze_morphology(wd["word"])
                is_direct = is_direct_speech(wd["sentence"])

                st.subheader("📝 Параметры разметки")
                with st.form("annotation_form"):
                    axio = st.selectbox("Аксиологема:", selected_axios)
                    morphemes = st.multiselect("Морфемы:", ["диминутивные", "аугментативные", "мелиоративные", "пейоративные", "частичности", "недостаточности", "чрезмерности", "приблизительности"])
                    morph_features = st.text_input("Морфология (авто):", value=auto_morph)
                    syntactic_scheme = st.text_input("Синтаксис (структурная схема):", value="X")
                    c1, c2 = st.columns(2)
                    stylistic_type = c1.selectbox("Стилистика (Тип):", list(STYLISTIC_HIERARCHY.keys()))
                    stylistic_subtype = c2.selectbox("Стилистика (Подтип):", STYLISTIC_HIERARCHY.get(stylistic_type, []))
                    derivatives = st.text_input("Производные в тексте:")
                    
                    illoc_force = "Нет (не в прямой речи)"
                    sentence_context = None
                    if is_direct:
                        st.warning("⚠️ Слово в **прямой речи**. Укажите иллокутивную силу (предложение будет сохранено).")
                        illoc_force = st.selectbox("Иллокутивная сила (Дж. Серль):", ILLOCUTIONARY_FORCES)
                        sentence_context = wd["sentence"]
                        st.text_area("Контекст предложения:", value=sentence_context, disabled=True)
                        
                    justification = st.text_area("Обоснование выбора:")
                    
                    if st.form_submit_button("💾 Сохранить аннотацию"):
                        data = {k: None for k in EXPECTED_SCHEMA.keys()}
                        data.update({
                            "annotator_id": info['id'], "annotator_gender": info['gender'],
                            "annotator_age": info['age'], "is_anonymous": info['is_anonymous'],
                            "text_source": "DEMO" if text_mode.startswith("Демо") else "CUSTOM",
                            "sentence_id": wd['sent_id'], "word_form": wd['word'], "lemma": lemma, "pos": pos,
                            "morph_features": morph_features, "syntactic_scheme": syntactic_scheme,
                            "selected_axiologeme": axio, "morphemes": ", ".join(morphemes),
                            "stylistic_type": stylistic_type, "stylistic_subtype": stylistic_subtype,
                            "derivatives": derivatives, "illocutionary_force": illoc_force,
                            "is_direct_speech": is_direct, "sentence_context": sentence_context,
                            "justification": justification, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })
                        if save_annotation(data):
                            st.session_state.axio_counts[axio] = st.session_state.axio_counts.get(axio, 0) + 1
                            st.success("✅ Аннотация сохранена!")
                            st.session_state.selected_word_data = None
                            st.rerun()

                if st.button("❌ Отменить выбор слова"): 
                    st.session_state.selected_word_data = None
                    st.rerun()

# ==========================================
# 5. ПАНЕЛИ УПРАВЛЕНИЯ И СТАТИСТИКИ
# ==========================================
st.divider()
tab_ctrl, tab_stats = st.tabs(["🔐 Управление данными", "📊 Статистика"])

with tab_ctrl:
    st.subheader("📋 Размеченные данные")
    password = st.text_input("🔑 Пароль администратора:", type="password", key="admin_pass")
    if password == "axio2026": st.session_state.admin_logged = True
        
    if st.session_state.admin_logged:
        df = load_annotations()
        if df.empty:
            st.info("Пока нет сохраненных аннотаций.")
        else:
            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button(label="📥 Скачать итоговую таблицу (CSV)", data=csv_data, file_name="annotations_export.csv", mime="text/csv")
            st.divider()
            st.subheader("✏️ Редактирование и удаление")
            edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True, hide_index=True, key="data_editor")
            
            if st.button("💾 Применить изменения"):
                conn = sqlite3.connect(DB_PATH); cursor = conn.cursor()
                cursor.execute("DELETE FROM annotations")
                for _, row in edited_df.iterrows():
                    cols_list = [c for c in edited_df.columns if c != 'id']
                    vals = [row.get(c, None) for c in cols_list]
                    cursor.execute(f"INSERT INTO annotations ({', '.join(cols_list)}) VALUES ({', '.join(['?']*len(vals))})", vals)
                conn.commit(); conn.close()
                st.success("✅ Изменения сохранены!"); st.rerun()
            if st.button("🗑️ Полностью очистить базу"):
                conn = sqlite3.connect(DB_PATH); conn.execute("DELETE FROM annotations"); conn.commit(); conn.close()
                st.session_state.axio_counts.clear(); st.success("🗑️ База очищена."); st.rerun()
    else: st.info("🔒 Введите пароль для доступа.")

with tab_stats:
    st.subheader("📊 Визуальная аналитика")
    df = load_annotations()
    if df.empty:
        st.warning("Нет данных для отображения статистики.")
    else:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### Распределение аксиологем")
            if 'selected_axiologeme' in df.columns and df['selected_axiologeme'].notna().any():
                axio_counts = df['selected_axiologeme'].value_counts().reset_index()
                axio_counts.columns = ["Аксиологема", "Количество"]
                st.bar_chart(axio_counts.set_index("Аксиологема"))
            else: st.info("Нет данных по аксиологемам.")
        with c2:
            st.markdown("### Иллокутивные силы (прямая речь)")
            if 'is_direct_speech' in df.columns and 'illocutionary_force' in df.columns:
                illoc_df = df[df['is_direct_speech'].astype(bool)]
                if not illoc_df.empty and illoc_df['illocutionary_force'].notna().any():
                    illoc_counts = illoc_df['illocutionary_force'].value_counts().reset_index()
                    illoc_counts.columns = ["Сила", "Количество"]
                    st.bar_chart(illoc_counts.set_index("Сила"))
                else: st.info("Нет разметки прямой речи.")
            else: st.info("Столбцы статистики недоступны.")
