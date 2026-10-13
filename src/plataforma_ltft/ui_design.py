"""Sistema visual e pequenos componentes da interface Streamlit."""

import streamlit as st


GLOBAL_CSS = """
<style>
:root {
  --ft-ink: #16332c;
  --ft-muted: #52665f;
  --ft-brand: #0f6b55;
  --ft-brand-dark: #084c3d;
  --ft-surface: #ffffff;
  --ft-border: #cbdcd5;
  --ft-focus: #b45309;
}
.stApp { color: var(--ft-ink); }
[data-testid="stMainBlockContainer"] {
  max-width: 1180px;
  padding-top: 2rem;
  padding-bottom: 4rem;
}
h1, h2, h3 { letter-spacing: -0.02em; }
[data-testid="stMetric"], [data-testid="stVerticalBlockBorderWrapper"] {
  background: var(--ft-surface);
  border-color: var(--ft-border);
  border-radius: 0.8rem;
}
[data-testid="stSidebar"] { border-right: 1px solid var(--ft-border); }
.stButton > button, .stFormSubmitButton > button {
  min-height: 2.75rem;
  border-radius: 0.55rem;
  font-weight: 650;
}
button:focus-visible, input:focus-visible, [role="radio"]:focus-visible,
[role="checkbox"]:focus-visible, [role="combobox"]:focus-visible {
  outline: 3px solid var(--ft-focus) !important;
  outline-offset: 2px;
}
[data-testid="stCaptionContainer"] { color: var(--ft-muted); }
.ft-maturity {
  display: inline-block;
  padding: 0.25rem 0.6rem;
  margin-bottom: 0.45rem;
  border: 1px solid var(--ft-border);
  border-radius: 999px;
  font-size: 0.82rem;
  font-weight: 750;
  letter-spacing: 0.01em;
}
.ft-mathematical { background: #e7f1ff; color: #174a7e; }
.ft-heuristic { background: #fff3cd; color: #6b4b00; border-style: dashed; }
.ft-literature { background: #ede9fe; color: #51368a; }
.ft-experimental { background: #e8f5e9; color: #24632c; }
.ft-calibrated { background: #dff4ee; color: #075c49; border-width: 2px; }
.ft-blocked { background: #fde8e8; color: #8a2020; border-style: double; }
@media (max-width: 700px) {
  [data-testid="stMainBlockContainer"] { padding: 1rem 0.9rem 3rem; }
  h1 { font-size: 2rem !important; }
  h2 { font-size: 1.45rem !important; }
  .stButton > button, .stFormSubmitButton > button { width: 100%; }
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    scroll-behavior: auto !important;
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
</style>
"""


def apply_global_design() -> None:
    """Aplica tokens visuais sem substituir a semântica dos widgets nativos."""
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def section_intro(title: str, description: str) -> None:
    """Cria cabeçalho previsível para uma etapa do fluxo."""
    st.subheader(title)
    st.write(description)


def maturity_card(title: str, status: str, description: str, tone: str) -> None:
    """Exibe maturidade com texto e cor, sem depender apenas da cor."""
    with st.container(border=True):
        st.markdown(f"#### {title}")
        if tone == "success":
            st.success(status)
        elif tone == "warning":
            st.warning(status)
        else:
            st.markdown(f"**Status: {status}**")
        st.write(description)


def maturity_badge(category: str) -> None:
    """Selo textual; a categoria continua legível sem percepção de cor."""
    css_name = {
        "matemático": "mathematical", "heurístico": "heuristic",
        "literatura": "literature", "experimental": "experimental",
        "calibrado": "calibrated", "bloqueado": "blocked",
    }.get(category)
    if css_name is None:
        raise ValueError(f"Categoria de maturidade desconhecida: {category}")
    st.markdown(
        f'<span class="ft-maturity ft-{css_name}">Maturidade: {category}</span>',
        unsafe_allow_html=True,
    )
