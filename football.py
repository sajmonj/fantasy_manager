import streamlit as st
import json

# Wczytanie zasad z pliku
try:
    with open('fantasy.json', 'r') as f:
        content = "".join([line.split("//")[0] for line in f])
        rules = json.loads(content)
except Exception as e:
    st.error(f"Błąd pliku JSON: {e}")
    st.stop()

st.set_page_config(page_title="Fantasy Live Manager", layout="wide")

# Inicjalizacja stanu sesji
if 'players' not in st.session_state:
    st.session_state.players = []
if 'editing_index' not in st.session_state:
    st.session_state.editing_index = None
if 'expander_state' not in st.session_state:
    st.session_state.expander_state = True

def calculate_points(p, r):
    score = 0
    if p['mins'] >= 90: score += r["app_90"]
    elif p['mins'] >= 45: score += r["app_45"]
    elif p['mins'] > 0: score += r["app"]
    
    score += p['goals'] * r["goal"]
    score += p['assists'] * r["assist"]
    score += p['own_goals'] * r["own_goal"]
    score += p['yellow'] * r["yellow"]
    score += p['red'] * r["red"]
    score += p['tackles'] * r["tackle/block"]
    score += p['dribbles'] * r["drybbling"]
    score += p['saves'] * r["save"]
    if p['motm']: score += r["motm"]
    
    if p['pos'] in ["GK", "DF"]:
        score += p['shots_ot'] * r["shots_on_target"]
    else:
        score += (p['shots_ot'] // 2) * r["shots_on_target"]
        
    if p['cs']:
        if p['pos'] == "GK": score += r["clean_sheet_gk"]
        if p['pos'] == "DF": score += r["clean_sheet_df"]
    
    score += p['gc_gk'] * r["goal_conceded_gk"]
    score += p['gc_df'] * r["goal_conceded_df"]
    score += p['p_missed'] * r["missed_penalty"]
    score += p['p_saved'] * r["saved_penalty"]
    score += p['p_goal'] * r["penalty_goal"]
    score += p['p_received'] * r["received_penalty"]
    score += p['p_procured'] * r["procured_penalty"]
    score += p['p_conceded'] * r["conceded_penalty"]
    score += (p['lost_pos'] // 5) * r["lost_posessions"]
    if p['is_cap']: score *= 2
    return score

st.title("⚽ Live Fantasy Manager")

main_pts = sum(calculate_points(p, rules) for p in st.session_state.players if not p['is_bench'])
bench_pts = sum(calculate_points(p, rules) for p in st.session_state.players if p['is_bench'])

c_res1, c_res2, c_res3 = st.columns(3)
c_res1.metric("WYNIK DRUŻYNY", f"{main_pts} pkt")
c_res2.metric("Punkty rezerwowych", f"{bench_pts} pkt")
c_res3.metric("Liczba graczy", f"{len(st.session_state.players)}/16")

st.divider()

# --- FORMULARZ ---
is_editing = st.session_state.editing_index is not None

form_label = "📝 Edytuj dane zawodnika" if is_editing else "➕ Dodaj nowego zawodnika"

# Używamy expandera z kluczem, aby móc go kontrolować
with st.expander(form_label, expanded=st.session_state.expander_state):    
    d = None
    if is_editing:
        if st.session_state.editing_index < len(st.session_state.players):
            d = st.session_state.players[st.session_state.editing_index]
        else:
            st.session_state.editing_index = None
            st.rerun()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        name = st.text_input("Nazwisko", value=d['name'] if d else "")
        pos = st.selectbox("Pozycja", ["GK", "DF", "MD", "FW"], 
                           index=["GK", "DF", "MD", "FW"].index(d['pos']) if d else 0)
        mins = st.number_input("Minuty", 0, 120, d['mins'] if d else 0)
    with c2:
        is_bench = st.checkbox("Ławka", value=d['is_bench'] if d else False)
        is_cap = st.checkbox("Kapitan (x2)", value=d['is_cap'] if d else False)
        motm = st.checkbox("Gracz Meczu (MOTM)", value=d['motm'] if d else False)
        cs = st.checkbox("Czyste konto", value=d['cs'] if d else False)
    with c3:
        goals = st.number_input("Gole (z gry)", 0, 10, d['goals'] if d else 0)
        assists = st.number_input("Asysty", 0, 10, d['assists'] if d else 0)
        own_goals = st.number_input("Samobóje", 0, 5, d['own_goals'] if d else 0)
    with c4:
        yellow = st.number_input("Żółte kartki", 0, 2, d['yellow'] if d else 0)
        red = st.number_input("Czerwona kartka", 0, 1, d['red'] if d else 0)
        lost_pos = st.number_input("Straty piłki", 0, 100, d['lost_pos'] if d else 0)

    st.markdown("### Statystyki szczegółowe i Karne")
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        shots_ot = st.number_input("Strzały celne", 0, 20, d['shots_ot'] if d else 0)
        tackles = st.number_input("Odbiór", 0, 20, d['tackles'] if d else 0)
        dribbles = st.number_input("Dryblingi", 0, 20, d['dribbles'] if d else 0)
    with s2:
        saves = st.number_input("Interwencje bez karnych (GK)", 0, 20, d['saves'] if d else 0)
        gc_gk = st.number_input("Gole stracone bez karnych (GK)", 0, 20, d['gc_gk'] if d else 0)
        gc_df = st.number_input("Gole stracone (DF)", 0, 20, d['gc_df'] if d else 0)
    with s3:
        p_goal = st.number_input("Gol z karnego", 0, 5, d['p_goal'] if d else 0)
        p_missed = st.number_input("Karny niestrzelony", 0, 5, d['p_missed'] if d else 0)
        p_saved = st.number_input("Karny obroniony", 0, 5, d['p_saved'] if d else 0)
    with s4:
        p_rec = st.number_input("Karny wywalczony", 0, 5, d['p_received'] if d else 0)
        p_proc = st.number_input("Karny sprokurowany", 0, 5, d['p_procured'] if d else 0)
        p_conc = st.number_input("Karny nieobroniony", 0, 5, d['p_conceded'] if d else 0)

    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        if st.button("💾 Zapisz", use_container_width=True):
            new_data = {
                "name": name, "pos": pos, "is_bench": is_bench, "is_cap": is_cap, "mins": mins,
                "goals": goals, "assists": assists, "own_goals": own_goals, "yellow": yellow, "red": red,
                "tackles": tackles, "dribbles": dribbles, "saves": saves, "motm": motm, "shots_ot": shots_ot,
                "cs": cs, "gc_gk": gc_gk, "gc_df": gc_df, "lost_pos": lost_pos,
                "p_goal": p_goal, "p_missed": p_missed, "p_saved": p_saved, "p_received": p_rec,
                "p_procured": p_proc, "p_conceded": p_conc
            }
            
            bench_count = sum(1 for p in st.session_state.players if p['is_bench'])
            start_count = sum(1 for p in st.session_state.players if not p['is_bench'])
            gk_count = sum(1 for p in st.session_state.players if not p['is_bench'] and p['pos'] == "GK")
            cap_exists = any(p['is_cap'] for p in st.session_state.players)

            if not name:
                st.error("Podaj nazwisko zawodnika!")
            elif not is_editing and len(st.session_state.players) >= 16:
                st.error("Osiągnięto limit 16 zawodników w całej kadrze!")
            elif not is_editing and is_bench and bench_count >= rules["max_bench"]:
                st.error(f"Limit ławki rezerwowych (max {rules['bench']}) został przekroczony!")
            elif not is_editing and not is_bench and start_count >= 11:
                st.error("Skład podstawowy może liczyć maksymalnie 11 osób!")
            elif not is_editing and not is_bench and pos == "GK" and gk_count >= 1:
                st.error("Możesz mieć tylko jednego bramkarza w składzie podstawowym!")
            elif is_cap and cap_exists and (not is_editing or not st.session_state.players[st.session_state.editing_index]['is_cap']):
                st.error("Drużyna może mieć tylko jednego kapitana!")
            else:
                if is_editing:
                    # ✏️ EDYCJA → zamknij
                    st.session_state.players[st.session_state.editing_index] = new_data
                    st.session_state.editing_index = None
                    st.session_state.expander_state = False
                else:
                    # ➕ DODAWANIE → zostaw otwarty
                    st.session_state.players.append(new_data)
                    st.session_state.expander_state = True

                st.rerun()

    with btn_col2:
        # Przycisk "Anuluj" pokazuje się TYLKO podczas edycji
        if is_editing:
            if st.button("❌ Anuluj edycję", use_container_width=True):
                st.session_state.editing_index = None
                st.session_state.expander_state = False
                st.rerun()


# --- WIDOK SKŁADU ---
if st.session_state.players:
    st.subheader("Aktualny Skład")
    for i, p in enumerate(st.session_state.players):
        pts = calculate_points(p, rules)
        with st.container(border=True):
            cols = st.columns([3, 1, 1, 1])
            with cols[0]:
                prefix = "⭐️" if p['is_cap'] else "👤"
                suffix = " (Ławka)" if p['is_bench'] else ""
                st.write(f"{prefix} **{p['name']}** ({p['pos']}){suffix}")
            with cols[1]:
                st.write(f"**{pts} pkt**")
            with cols[2]:
                if st.button("✏️ Edytuj", key=f"edit_{i}"):
                    st.session_state.editing_index = i
                    st.session_state.expander_state = True
                    st.rerun()
            with cols[3]:
                if st.button("🗑️ Usuń", key=f"del_{i}"):
                    st.session_state.players.pop(i)
                    st.session_state.editing_index = None
                    st.rerun()