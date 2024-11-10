import streamlit as st

INTAKE_FORM_BUTTON = 'intake_form_button_clicked'

def click_intake_form_button():
    st.session_state.intake_form_button_clicked = not st.session_state.intake_form_button_clicked

def create_user_intake_form():
    if INTAKE_FORM_BUTTON not in st.session_state:
        st.session_state.intake_form_button_clicked = False
    with st.sidebar:
        st.button(label="User Intake Form", on_click=click_intake_form_button)
    
    intake_form()

def intake_form():
    if st.session_state.intake_form_button_clicked:
        st.markdown("## User Intake Form")
        st.text_input("Name")
        st.text_input("Email")
        st.text_input("Phone")
        st.text_input("Address")
        st.text_input("City")
        st.text_input("State")
        st.text_input("Zip")
        st.text_input("Country")
        st.text_input("Date of Birth")