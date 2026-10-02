"""
Binary Ionic Type I / Type II / Nonmetal charge quiz - starred elements only.

Run with:   pip install streamlit
            streamlit run chem_quiz.py
(needs Streamlit 1.27 or newer)
"""
import random
import streamlit as st

st.set_page_config(page_title="Type I / Type II & Charges Quiz", page_icon="⚗️", layout="wide")

# ------------------------------------------------------------------ data
# Every element marked with a star on the "Elements to Commit to Memory" sheet.
# type: "I"  = metal with ONE possible charge      (charge = that charge)
#       "II" = metal with MORE THAN ONE charge     (charges = common ones)
#       "N"  = nonmetal / metalloid / noble gas    (has an anion/common charge)
def I(name, sym, charge):
    return dict(name=name, symbol=sym, type="I", charge=charge, charges=[charge])

def II(name, sym, charges):
    return dict(name=name, symbol=sym, type="II", charge=None, charges=charges)

def N(name, sym, charges):
    return dict(name=name, symbol=sym, type="N", charge=None, charges=charges)

ELEMENTS = [
    # Type I - fixed charge metals
    I("Lithium", "Li", 1), I("Sodium", "Na", 1), I("Potassium", "K", 1),
    I("Rubidium", "Rb", 1), I("Cesium", "Cs", 1), I("Silver", "Ag", 1),
    I("Beryllium", "Be", 2), I("Magnesium", "Mg", 2), I("Calcium", "Ca", 2),
    I("Strontium", "Sr", 2), I("Barium", "Ba", 2), I("Zinc", "Zn", 2),
    I("Cadmium", "Cd", 2),
    I("Aluminum", "Al", 3), I("Gallium", "Ga", 3),
    # Type II - variable charge metals
    II("Titanium", "Ti", [2, 3, 4]), II("Chromium", "Cr", [2, 3]),
    II("Manganese", "Mn", [2, 3, 4, 7]), II("Iron", "Fe", [2, 3]),
    II("Cobalt", "Co", [2, 3]), II("Nickel", "Ni", [2, 3]),
    II("Copper", "Cu", [1, 2]), II("Molybdenum", "Mo", [3, 6]),
    II("Tin", "Sn", [2, 4]), II("Lead", "Pb", [2, 4]),
    II("Platinum", "Pt", [2, 4]), II("Gold", "Au", [1, 3]),
    II("Mercury", "Hg", [1, 2]), II("Antimony", "Sb", [3, 5]),
    II("Bismuth", "Bi", [3, 5]),
    # Nonmetals / others with common charges
    N("Hydrogen", "H", [1, -1]), N("Helium", "He", [0]), N("Boron", "B", [3]), N("Carbon", "C", [4, -4]),
    N("Nitrogen", "N", [-3]), N("Oxygen", "O", [-2]), N("Fluorine", "F", [-1]), N("Neon", "Ne", [0]),
    N("Silicon", "Si", [4]), N("Phosphorus", "P", [-3]), N("Sulfur", "S", [-2]), N("Chlorine", "Cl", [-1]),
    N("Argon", "Ar", [0]), N("Arsenic", "As", [-3]), N("Selenium", "Se", [-2]), N("Bromine", "Br", [-1]),
    N("Krypton", "Kr", [0]), N("Iodine", "I", [-1]), N("Xenon", "Xe", [0]),
]
BY_SYM = {e["symbol"]: e for e in ELEMENTS}
TYPE_LABEL = {"I": "Type I Metal", "II": "Type II Metal", "N": "Nonmetal/Other"}
SUP = {1: "⁺", 2: "²⁺", 3: "³⁺", 4: "⁴⁺", 5: "⁵⁺", 6: "⁶⁺", 7: "⁷⁺"}


def ion(e, c):
    return f"{e['symbol']}{SUP[c]}"


# ------------------------------------------------------------------ state
ss = st.session_state
for k, v in dict(qid=0, current=None, answered=False, feedback=None, warn=None,
                 total=0, correct=0, streak=0, best=0, missed={}, deck=[],
                 sig=None, show_as="Symbol").items():
    ss.setdefault(k, v)

# ------------------------------------------------------------------ sidebar
with st.sidebar:
    st.header("Quiz options")
    include_n = st.checkbox("Include nonmetals (answer: Neither)", value=False)
    ask_t2 = st.checkbox("For Type II, also ask for the charges", value=False)
    display = st.radio("Show the element as", ["Symbol", "Name", "Random"], index=2)
    drill = st.checkbox("Only drill elements I've missed", value=False,
                        disabled=not ss.missed)

    if st.button("Reset score & misses"):
        for k in ("total", "correct", "streak", "best"):
            ss[k] = 0
        ss.missed = {}
        ss.deck, ss.sig = [], None
        st.rerun()

    with st.expander("Cheat sheet"):
        rows = []
        for e in ELEMENTS:
            if e["type"] == "N" and not include_n:
                continue
            ch = ", ".join(str(c) if isinstance(c, str) else f"{c}" for c in e["charges"])
            rows.append({"Element": f"{e['symbol']} - {e['name']}", "Type": TYPE_LABEL[e["type"]], "Charge(s)": ch})
        st.dataframe(rows, hide_index=True)
        st.caption("Type I: one charge only. Type II: several possible charges.")

# ------------------------------------------------------------------ question deck
def build_pool():
    pool = [e["symbol"] for e in ELEMENTS if include_n or e["type"] != "N"]
    if drill:
        missed = [s for s in pool if ss.missed.get(s)]
        pool = missed or pool
    return pool


def next_question():
    if not ss.deck:
        ss.deck = random.sample(build_pool(), len(build_pool()))
    sym = ss.deck.pop(0)
    if ss.current and sym == ss.current and ss.deck:
        ss.deck.append(sym)
        sym = ss.deck.pop(0)
    ss.current = sym
    ss.answered, ss.feedback, ss.warn = False, None, None
    ss.show_as = random.choice(["Symbol", "Name"]) if display == "Random" else display
    ss.qid += 1


sig = (include_n, drill)
if ss.sig != sig or ss.current is None:
    ss.sig, ss.deck = sig, []
    next_question()
elif ss.show_as != display and display != "Random" and not ss.answered:
    ss.show_as = display

el = BY_SYM[ss.current]
qid = ss.qid
KT, KC, K2 = f"type_{qid}", f"chg_{qid}", f"t2_{qid}"


# ------------------------------------------------------------------ callbacks
def submit():
    t, c, t2 = ss.get(KT), ss.get(KC), ss.get(K2)
    if t is None:
        ss.warn = "Pick Type I, Type II" + (" or Neither" if include_n else "") + " first."
        return
    if t == "Type I" and c is None:
        ss.warn = "You picked Type I - now choose the charge."
        return
    ss.warn = None

    correct_type = TYPE_LABEL[el["type"]]
    type_ok = t == correct_type
    charge_ok, t2_ok = True, True
    if type_ok and el["type"] == "I":
        charge_ok = c == f"{el['charge']}+"
    if type_ok and el["type"] == "II" and ask_t2:
        t2_ok = set(t2 or []) == {f"{x}+" for x in el["charges"]}

    ok = type_ok and charge_ok and t2_ok
    ss.total += 1
    if ok:
        ss.correct += 1
        ss.streak += 1
        ss.best = max(ss.best, ss.streak)
        if ss.missed.get(el["symbol"]):
            ss.missed[el["symbol"]] -= 1
            if ss.missed[el["symbol"]] <= 0:
                del ss.missed[el["symbol"]]
    else:
        ss.streak = 0
        ss.missed[el["symbol"]] = ss.missed.get(el["symbol"], 0) + 1
        ss.deck.insert(min(len(ss.deck), random.randint(2, 5)), el["symbol"])

    if el["type"] == "I":
        why = (f"**{el['name']} is Type I** - it only forms one ion: **{ion(el, el['charge'])}**.")
    elif el["type"] == "II":
        opts = " or ".join(ion(el, x) for x in el["charges"])
        why = (f"**{el['name']} is Type II** - variable charge ({opts}).")
    else:
        why = f"**{el['name']}** has common charge(s): {el['charges']}."

    if ok:
        msg = "✅ Correct! " + why
    elif not type_ok:
        msg = "❌ Not quite. " + why
    elif not charge_ok:
        msg = f"⚠️ Right type, wrong charge. " + why
    else:
        msg = "⚠️ Right type, but the charges aren't right. " + why
    ss.feedback = (ok, msg)
    ss.answered = True


def go_next():
    next_question()


# ------------------------------------------------------------------ main UI
def quiz_ui():
    st.title("⚗️ Type I or Type II?")
    st.caption("Starred elements only - is it a Type I (one charge) or Type II (variable charge) binary ionic metal?")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Score", f"{ss.correct}/{ss.total}")
    c2.metric("Accuracy", f"{round(100 * ss.correct / ss.total)}%" if ss.total else "-")
    c3.metric("Streak", ss.streak)
    c4.metric("Best", ss.best)

    shown = el["symbol"] if ss.show_as == "Symbol" else el["name"]
    size = "5rem" if ss.show_as == "Symbol" else "3.2rem"
    st.markdown(
        f"<div style='text-align:center;padding:1.2rem;margin:0.8rem 0;border:2px solid #00c2d1;"
        f"border-radius:14px;font-size:{size};font-weight:800;letter-spacing:2px'>{shown}</div>",
        unsafe_allow_html=True,
    )

    options = ["Type I Metal", "Type II Metal"] + (["Nonmetal/Other"] if include_n else [])
    t_choice = st.radio("Binary ionic type?", options, index=None, key=KT,
                        horizontal=True, disabled=ss.answered)

    if t_choice == "Type I Metal":
        st.radio("What is its charge?", ["1+", "2+", "3+"], index=None, key=KC,
                 horizontal=True, disabled=ss.answered)
    elif t_choice == "Type II Metal" and ask_t2:
        st.multiselect("Which charges can it have?", [f"{i}+" for i in range(1, 8)],
                       key=K2, disabled=ss.answered)

    if ss.warn:
        st.warning(ss.warn)

    if not ss.answered:
        st.button("Check answer", type="primary", on_click=submit)
    else:
        ok, msg = ss.feedback
        (st.success if ok else st.error)(msg)
        st.button("Next question ➜", type="primary", on_click=go_next)

    if ss.missed:
        with st.expander(f"Elements to review ({len(ss.missed)})"):
            for s, n in sorted(ss.missed.items(), key=lambda kv: -kv[1]):
                e = BY_SYM[s]
                label = TYPE_LABEL[e["type"]]
                extra = f" ({ion(e, e['charge'])})" if e["type"] == "I" else ""
                st.write(f"**{e['symbol']}** - {e['name']}: {label}{extra}  ·  missed {n}×")


# ------------------------------------------------------------------ periodic table with charge inputs
SYMS = ("H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn Ga Ge As Se Br Kr "
        "Rb Sr Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I Xe Cs Ba La Ce Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb "
        "Lu Hf Ta W Re Os Ir Pt Au Hg Tl Pb Bi Po At Rn Fr Ra Ac Th Pa U Np Pu Am Cm Bk Cf Es Fm Md No Lr "
        "Unq Unp Unh Uns Uno Une Unn").split()
STARRED = {e["symbol"] for e in ELEMENTS}


def pos(z):
    """(row, column) of element z in the 18-column layout (f-block left out)."""
    if z == 1: return (1, 1)
    if z == 2: return (1, 18)
    if 3 <= z <= 4: return (2, z - 2)
    if 5 <= z <= 10: return (2, z + 8)
    if 11 <= z <= 12: return (3, z - 10)
    if 13 <= z <= 18: return (3, z)
    if 19 <= z <= 36: return (4, z - 18)
    if 37 <= z <= 54: return (5, z - 36)
    if 55 <= z <= 56: return (6, z - 54)
    if 71 <= z <= 86: return (6, z - 68)
    if 87 <= z <= 88: return (7, z - 86)
    if 103 <= z <= 110: return (7, z - 100)
    return None


GRID = {pos(z): z for z in range(1, 111) if pos(z)}


def grid_html(cell):
    out = ["<div style='display:grid;grid-template-columns:repeat(18,1fr);gap:3px;font-family:monospace'>"]
    for r in range(1, 8):
        for c in range(1, 19):
            z = GRID.get((r, c))
            out.append("<div></div>" if z is None else cell(z))
    out.append("</div>")
    return "".join(out)


def box(z, sym_txt, name_txt, charge_txt, bg, fg, border="#888"):
    return (f"<div style='border:1px solid {border};border-radius:4px;padding:2px 1px;text-align:center;"
            f"background:{bg};color:{fg};min-height:55px;line-height:1.15'>"
            f"<div style='font-size:.5rem;opacity:.8'>{z}</div>"
            f"<div style='font-weight:700;font-size:.85rem'>{sym_txt}</div>"
            f"<div style='font-size:.45rem;opacity:.8;white-space:nowrap;overflow:hidden;text-overflow:ellipsis'>{name_txt}</div>"
            f"<div style='font-size:.55rem;font-weight:bold;color:#007acc'>{charge_txt}</div></div>")


def table_ui():
    st.subheader("Periodic Table - Charge Practice")
    st.caption("All starred elements are shown with their symbol and name. Type the expected charge (e.g., `1+`, `2+`, `3+`, `1-`, `2-`, etc.) into the box for each element.")

    st.markdown(
        "<style>div[data-testid='stForm'] input{text-align:center;font-weight:700;padding:2px 2px;}"
        ".tcap{font-size:.55rem;text-align:center;line-height:1.1;opacity:.85;min-height:1.2rem}</style>",
        unsafe_allow_html=True)

    nonce = ss.setdefault("tnonce", 0)
    with st.form("charge_table"):
        for r in range(1, 8):
            cols = st.columns(18, gap="small")
            for c in range(1, 19):
                z = GRID.get((r, c))
                if z is None:
                    continue
                sym = SYMS[z - 1]
                if sym in STARRED:
                    el_data = BY_SYM[sym]
                    cols[c - 1].markdown(f"<div class='tcap'><b>{sym}</b><br>{el_data['name']}</div>", unsafe_allow_html=True)
                    cols[c - 1].text_input(str(z), key=f"charge_cell_{nonce}_{z}", max_chars=4,
                                           placeholder="chg", label_visibility="collapsed")
                else:
                    cols[c - 1].markdown(
                        f"<div class='tcap' style='opacity:.4'><b style='font-size:.8rem'>{sym}</b><br>&nbsp;</div>",
                        unsafe_allow_html=True)
        submitted = st.form_submit_button("Check charges", type="primary")

    if submitted:
        res = {}
        for sym in STARRED:
            z = SYMS.index(sym) + 1
            el_data = BY_SYM[sym]
            typed = (ss.get(f"charge_cell_{nonce}_{z}") or "").strip().lower()
            
            # Normalize user input and valid expected charges format
            # Support formats like "1+", "+1", "1", "2-", "-2", etc.
            valid_strs = set()
            for ch in el_data["charges"]:
                if isinstance(ch, int):
                    if ch == 0:
                    	valid_strs.update(["0", "sel", "none"])
                    else:
                        valid_strs.update([f"{ch}+", f"+{ch}", str(ch)])
                else:
                    valid_strs.add(str(ch).lower())
            # Also handle typical ionic representations like "1+" for fluorine sometimes written as "1-"
            ok = typed in valid_strs
            res[z] = (typed, ok, el_data["charges"])
        ss.tres = res

    def clear():
        ss.tnonce += 1
        ss.tres = None
    st.button("Clear table", on_click=clear)

    res = ss.get("tres")
    if res:
        good = sum(1 for _, ok, _ in res.values() if ok)
        m1, m2 = st.columns(2)
        m1.metric("Correct Charges", f"{good}/{len(res)}")
        m2.metric("Accuracy", f"{round(100 * good / len(res))}%")

        def cell(z):
            sym = SYMS[z - 1]
            if z not in res:
                el_data = BY_SYM.get(sym, {})
                name = el_data.get("name", "")
                return box(z, sym, name, "", "#2a2a35", "#888")
            typed, ok, expected = res[z]
            el_data = BY_SYM[sym]
            exp_str = ", ".join(str(x) for x in expected)
            if ok:
                return box(z, sym, el_data["name"], typed if typed else "0", "#1b7f3b", "#fff", "#2ecc71")
            display_typed = typed if typed else "(blank)"
            return box(z, sym, el_data["name"], f"❌ {display_typed} (exp: {exp_str})", "#a32030", "#fff", "#ff5c6c")

        st.markdown(grid_html(cell), unsafe_allow_html=True)
        wrong = [SYMS[z - 1] for z, (_, ok, _) in sorted(res.items()) if not ok]
        if wrong:
            st.info("Review charges for: " + ", ".join(f"{s} ({BY_SYM[s]['name']})" for s in wrong))
        else:
            st.success("All charges correct! 🎉")


# ------------------------------------------------------------------ layout
tab_quiz, tab_table = st.tabs(["Type I / II quiz", "Periodic table charge quiz"])
with tab_quiz:
    _, mid, _ = st.columns([1, 3, 1])
    with mid:
        quiz_ui()
with tab_table:
    table_ui()
