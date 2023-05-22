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


def img_html(image_url):
    image_html = f"""<button id="showButton">Show Image</button>
<div id="imageContainer" style="display:none; margin:auto;">
  <img src="{image_url}" style="max-width:100%; max-height:100%; display:block;">
  <button id="closeButton" style="position:absolute; top:0; right:0; padding:10px; background-color:white; border:none; font-weight:bold;">X</button>
</div>
<script>
  document.getElementById("showButton").addEventListener("click", function() {{
    document.getElementById("imageContainer").style.display = "block";
  }});
  
  document.getElementById("closeButton").addEventListener("click", function() {{
    document.getElementById("imageContainer").style.display = "none";
  }});
</script>




    """
    return image_html
