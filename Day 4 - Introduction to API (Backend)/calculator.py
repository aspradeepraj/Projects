import streamlit as st
import math

# Sets up a centered page configuration layout.
st.set_page_config(page_title="Compact Grid Calculator", layout="centered")

# Injects direct CSS to constrain the width, remove default padding gaps, and enforce button colors.
st.markdown("""
<style>
    /* Wraps the layout into a strict, compact box to match the second image and prevent screen stretching */
    .block-container {
        max-width: 420px !important;
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }
    
    /* Configures the deep steel-blue display header panel */
    .steel-display {
        background-color: #2e6b9e;
        color: #ffffff;
        font-family: Arial, sans-serif;
        font-size: 28px;
        font-weight: bold;
        text-align: right;
        padding: 12px 15px;
        border-radius: 4px 4px 0 0;
        min-height: 60px;
        line-height: 36px;
        margin-bottom: 8px;
    }
    
    /* Global layout style rule for the standard light-blue functional keys */
    div.stButton > button {
        background-color: #eaf2f8 !important;
        color: #000000 !important;
        border: 1px solid #b9cde3 !important;
        border-radius: 4px !important;
        font-size: 16px !important;
        font-weight: bold !important;
        padding: 4px 0px !important;
        width: 100% !important;
        height: 42px !important;
    }
    
    /* Specific gray-blue background color override for the dedicated number pad keys */
    div.num-pad > div > div > button {
        background-color: #b3cddf !important;
        border: 1px solid #8cb1cd !important;
    }
    
    /* Custom container padding rules for the Row 1 radio selector box alignment */
    .radio-box {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 42px;
        border: 1px solid #b9cde3;
        border-radius: 4px;
        background-color: #eaf2f8;
        padding: 0 5px;
    }
    
    /* Forces columns to sit tightly against each other with minimal horizontal margins */
    [data-testid="stHorizontalBlock"] {
        gap: 6px !important;
        margin-bottom: -6px;
    }
</style>
""", unsafe_allow_html=True)

# Initializes display session memory counters.
if "screen_text" not in st.session_state:
    st.session_state.screen_text = "0"
if "clear_screen" not in st.session_state:
    st.session_state.clear_screen = False

# Functional key router tracking core inputs.
def handle_click(label: str):
    # Determines code branch routes based on the intercepted text token indicator string.
    if label == "AC":
        st.session_state.screen_text = "0"
        st.session_state.clear_screen = False
    elif label == "Back":
        if len(st.session_state.screen_text) <= 1 or st.session_state.screen_text == "Error":
            st.session_state.screen_text = "0"
        else:
            st.session_state.screen_text = st.session_state.screen_text[:-1]
    elif label == "=":
        try:
            # Resolves display characters down to computable mathematical commands.
            parse_str = st.session_state.screen_text.replace("×", "*").replace("÷", "/")
            ans = eval(parse_str)
            st.session_state.screen_text = f"{ans:.9g}" if isinstance(ans, float) else str(ans)
            st.session_state.clear_screen = True
        except Exception:
            st.session_state.screen_text = "Error"
            st.session_state.clear_screen = True
    else:
        if st.session_state.screen_text == "0" or st.session_state.clear_screen:
            st.session_state.screen_text = label
            st.session_state.clear_screen = False
        else:
            st.session_state.screen_text += label

# Renders the exact steel-blue display view banner.
st.markdown(f'<div class="steel-display">{st.session_state.screen_text}</div>', unsafe_allow_html=True)

# Row 1: Allocates custom unequal column ratios to fit the buttons and the radio controls side-by-side cleanly.
r1_c1, r1_c2, r1_c3, r1_c4 = st.columns([1, 1, 1, 2])
with r1_c1: st.button("sin", on_click=handle_click, args=("sin(",), key="sin")
with r1_c2: st.button("cos", on_click=handle_click, args=("cos(",), key="cos")
with r1_c3: st.button("tan", on_click=handle_click, args=("tan(",), key="tan")
with r1_c4:
    st.markdown('<div class="radio-box">', unsafe_allow_html=True)
    mode = st.radio("", ["Deg", "Rad"], horizontal=True, label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

# Row 2: Inverse functions
c1, c2, c3, c4, c5 = st.columns(5)
with c1: st.button("sin⁻¹", on_click=handle_click, args=("asin(",))
with c2: st.button("cos⁻¹", on_click=handle_click, args=("acos(",))
with c3: st.button("tan⁻¹", on_click=handle_click, args=("atan(",))
with c4: st.button("π", on_click=handle_click, args=("3.14159265",))
with c5: st.button("e", on_click=handle_click, args=("2.71828182",))

# Row 3: Exponents / Powers
c1, c2, c3, c4, c5 = st.columns(5)
with c1: st.button("xʸ", on_click=handle_click, args=("**",))
with c2: st.button("x³", on_click=handle_click, args=("**3",))
with c3: st.button("x²", on_click=handle_click, args=("**2",))
with c4: st.button("e\u02e3", on_click=handle_click, args=("2.71828182**",))
with c5: st.button("10\u02e3", on_click=handle_click, args=("10**",))

# Row 4: Radicals / Roots / Logs
c1, c2, c3, c4, c5 = st.columns(5)
with c1: st.button("ʸ√x", on_click=handle_click, args=("",))
with c2: st.button("³√x", on_click=handle_click, args=("**(1/3)",))
with c3: st.button("√x", on_click=handle_click, args=("**(1/2)",))
with c4: st.button("ln", on_click=handle_click, args=("",))
with c5: st.button("log", on_click=handle_click, args=("",))

# Row 5: Structural Syntax
c1, c2, c3, c4, c5 = st.columns(5)
with c1: st.button("(", on_click=handle_click, args=("(",))
with c2: st.button(")", on_click=handle_click, args=(")",))
with c3: st.button("1/x", on_click=handle_click, args=("1/",))
with c4: st.button("%", on_click=handle_click, args=("%",))
with c5: st.button("n!", on_click=handle_click, args=("",))

# Row 6: Keypad 7, 8, 9, Add, Back
c1, c2, c3, c4, c5 = st.columns(5)
with c1: st.markdown('<div class="num-pad">', unsafe_allow_html=True); st.button("7", on_click=handle_click, args=("7",)); st.markdown('</div>', unsafe_allow_html=True)
with c2: st.markdown('<div class="num-pad">', unsafe_allow_html=True); st.button("8", on_click=handle_click, args=("8",)); st.markdown('</div>', unsafe_allow_html=True)
with c3: st.markdown('<div class="num-pad">', unsafe_allow_html=True); st.button("9", on_click=handle_click, args=("9",)); st.markdown('</div>', unsafe_allow_html=True)
with c4: st.button("+", on_click=handle_click, args=("+",))
with c5: st.button("Back", on_click=handle_click, args=("Back",))

# Row 7: Keypad 4, 5, 6, Subtract, Ans
c1, c2, c3, c4, c5 = st.columns(5)
with c1: st.markdown('<div class="num-pad">', unsafe_allow_html=True); st.button("4", on_click=handle_click, args=("4",)); st.markdown('</div>', unsafe_allow_html=True)
with c2: st.markdown('<div class="num-pad">', unsafe_allow_html=True); st.button("5", on_click=handle_click, args=("5",)); st.markdown('</div>', unsafe_allow_html=True)
with c3: st.markdown('<div class="num-pad">', unsafe_allow_html=True); st.button("6", on_click=handle_click, args=("6",)); st.markdown('</div>', unsafe_allow_html=True)
with c4: st.button("−", on_click=handle_click, args=("-",))
with c5: st.button("Ans", on_click=handle_click, args=("",))

# Row 8: Keypad 1, 2, 3, Multiply, M+
c1, c2, c3, c4, c5 = st.columns(5)
with c1: st.markdown('<div class="num-pad">', unsafe_allow_html=True); st.button("1", on_click=handle_click, args=("1",)); st.markdown('</div>', unsafe_allow_html=True)
with c2: st.markdown('<div class="num-pad">', unsafe_allow_html=True); st.button("2", on_click=handle_click, args=("2",)); st.markdown('</div>', unsafe_allow_html=True)
with c3: st.markdown('<div class="num-pad">', unsafe_allow_html=True); st.button("3", on_click=handle_click, args=("3",)); st.markdown('</div>', unsafe_allow_html=True)
with c4: st.button("×", on_click=handle_click, args=("×",))
with c5: st.button("M+", on_click=handle_click, args=("",))

# Row 9: Keypad 0, Dot, EXP, Divide, M-
c1, c2, c3, c4, c5 = st.columns(5)
with c1: st.markdown('<div class="num-pad">', unsafe_allow_html=True); st.button("0", on_click=handle_click, args=("0",)); st.markdown('</div>', unsafe_allow_html=True)
with c2: st.markdown('<div class="num-pad">', unsafe_allow_html=True); st.button(".", on_click=handle_click, args=(".",)); st.markdown('</div>', unsafe_allow_html=True)
with c3: st.button("EXP", on_click=handle_click, args=("*10**",))
with c4: st.button("÷", on_click=handle_click, args=("÷",))
with c5: st.button("M-", on_click=handle_click, args=("",))

# Row 10: Signs, RND, AC, Equals, MR
c1, c2, c3, c4, c5 = st.columns(5)
with c1: st.button("±", on_click=handle_click, args=("-",))
with c2: st.button("RND", on_click=handle_click, args=("",))
with c3: st.button("AC", on_click=handle_click, args=("AC",))
with c4: st.markdown('<div class="num-pad">', unsafe_allow_html=True); st.button("=", on_click=handle_click, args=("=",)); st.markdown('</div>', unsafe_allow_html=True)
with c5: st.button("MR", on_click=handle_click, args=("",))