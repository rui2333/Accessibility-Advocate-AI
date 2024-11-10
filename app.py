import streamlit as st
from toolhouse import Toolhouse
from llms import llms, llm_call
from http_exceptions.client_exceptions import NotFoundException
from utils import print_messages, append_and_print
from toolhouse import Toolhouse
import dotenv
import utils
import ui

utils.page_config()

llm_choice, llm, model = utils.configure_togetger_ai()

user = utils.setup_user_header()

ui.create_user_intake_form()

print_messages(st.session_state.messages, st.session_state.provider)
    
th = utils.setup_tool_house(llm, user)

utils.converse(th, llm_choice, llm, model)