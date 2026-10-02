"""
Binary Ionic Type I / Type II quiz - starred elements only.

Run with:   pip install streamlit
            streamlit run chem_quiz.py
(needs Streamlit 1.27 or newer)
"""
import random
import streamlit as st

st.set_page_config(page_title="Type I / Type II Quiz", page_icon="⚗️", layout="centered")

# ------------------------------------------------------------------ data
# Every element marked with a star on the "Elements to Commit to Memory" sheet.
# type: "I"  = metal with ONE possible charge          (charge = that charge)
#       "II" = metal with MORE THAN ONE charge          (charges = common ones)
#       "N"  = nonmetal / metalloid / noble gas (not a cation in a binary ionic compound)
def I(name, sym, charge):
    return dict(name=name, symbol=sym, type="I", charge=charge, charges=[charge])

def II(name, sym, charges):
    return dict(name=name, symbol=sym, type="II", charge=None, charges=charges)

def N(name, sym):
    return dict(name=name, symbol=sym, type="N", charge=None, charges=[])

ELEMENTS = [
    # Type I - fixed charge
    I("Lithium", "Li", 1), I("Sodium", "Na", 1), I("Potassium", "K", 1),
    I("Rubidium", "Rb", 1), I("Cesium", "Cs", 1), I("Silver", "Ag", 1),
    I("Beryllium", "Be", 2), I("Magnesium", "Mg", 2), I("Calcium", "Ca", 2),
    I("Strontium", "Sr", 2), I("Barium", "Ba", 2), I("Zinc", "Zn", 2),
    I("Cadmium", "Cd", 2),
    I("Aluminum", "Al", 3), I("Gallium", "Ga", 3),
    # Type II - variable charge
    II("Titanium", "Ti", [2, 3, 4]), II("Chromium", "Cr", [2, 3]),
    II("Manganese", "Mn", [2, 3, 4, 7]), II("Iron", "Fe", [2, 3]),
    II("Cobalt", "Co", [2, 3]), II("Nickel", "Ni", [2, 3]),
    II("Copper", "Cu", [1, 2]), II("Molybdenum", "Mo", [3, 6]),
    II("Tin", "Sn", [2, 4]), II("Lead", "Pb", [2, 4]),
    II("Platinum", "Pt", [2, 4]), II("Gold", "Au", [1, 3]),
    II("Mercury", "Hg", [1, 2]), II("Antimony", "Sb", [3, 5]),
    II("Bismuth", "Bi", [3, 5]),
    # Not metals (starred, but no Type I / II)
    N("Hydrogen", "H"), N("Helium", "He"), N("Boron", "B"), N("Carbon", "C"),
    N("Nitrogen", "N"), N("Oxygen", "O"), N("Fluorine", "F"), N("Neon", "Ne"),
    N("Silicon", "Si"), N("Phosphorus", "P"), N("Sulfur", "S"), N("Chlorine", "Cl"),
    N("Argon", "Ar"), N("Arsenic", "As"), N("Selenium", "Se"), N("Bromine", "Br"),
    N("Krypton", "Kr"), N("Iodine", "I"), N("Xenon", "Xe"),
]
BY_SYM = {e["symbol"]: e for e in ELEMENTS}
TYPE_LABEL = {"I": "Type I", "II": "Type II", "N": "Neither"}
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
    st.header("Study options")
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
            if e["type"] == "N":
                continue
            ch = ", ".join(ion(e, c) for c in e["charges"])
            rows.append({"Element": f"{e['symbol']} - {e['name']}", "Type": TYPE_LABEL[e["type"]], "Charge(s)": ch})
        st.dataframe(rows, hide_index=True)
        st.caption("Type I: one charge only. Type II: several possible charges, so the name "
                   "needs a Roman numeral. Hg is Hg₂²⁺ or Hg²⁺; Ni is usually 2+.")

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
    # don't repeat the same element twice in a row if we can avoid it
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
        # see it again soon
        ss.deck.insert(min(len(ss.deck), random.randint(2, 5)), el["symbol"])

    # build feedback message
    if el["type"] == "I":
        why = (f"**{el['name']} is Type I** - it only forms one ion: **{ion(el, el['charge'])}**.")
    elif el["type"] == "II":
        opts = " or ".join(ion(el, x) for x in el["charges"])
        why = (f"**{el['name']} is Type II** - variable charge ({opts}), "
               f"so its name needs a Roman numeral, e.g. {el['name'].lower()}({['', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII'][el['charges'][0]]}).")
    else:
        why = f"**{el['name']} is not a metal cation**, so it isn't Type I or II."

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

options = ["Type I", "Type II"] + (["Neither"] if include_n else [])
t_choice = st.radio("Binary ionic type?", options, index=None, key=KT,
                    horizontal=True, disabled=ss.answered)

if t_choice == "Type I":
    st.radio("What is its charge?", ["1+", "2+", "3+"], index=None, key=KC,
             horizontal=True, disabled=ss.answered)
elif t_choice == "Type II" and ask_t2:
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
