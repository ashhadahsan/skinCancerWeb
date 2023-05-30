import streamlit as st


def header():
    try:
        st.markdown(
            """<h3 style="text-align: center;"></h3>""",
            unsafe_allow_html=True,
        )
    except TypeError:
        pass


def remove_header_footer():
    hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
