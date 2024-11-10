import streamlit as st
from toolhouse.models.Stream import ToolhouseStreamStorage, stream_to_chat_completion
from types import SimpleNamespace

def anthropic_stream(response):
    for chunk in response.text_stream:
        yield chunk

def openai_stream(response, completion):
    for chunk in response:
        yield chunk
        completion.add(chunk)

def openai_render_tool_call(message):
    msg = ["**Using tools**"]
    for tool in message["tool_calls"]:
        args = tool["function"]["arguments"] if tool["function"]["arguments"] != "{}" else ""
        msg.append(f'```{tool["function"]["name"]}({args})```')

    return "\n\n".join(msg)

def print_messages(messages, provider):
    for message in messages:
        if provider == "anthropic":
            if isinstance(message["content"], str):
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
            elif isinstance(message["content"], list):
                has_tool = False
                msg = []
                for m in message["content"]:
                    if not hasattr(m, "type"):
                        continue
                    elif m.type == "text":
                        msg.append(m.text)
                    elif m.type == "tool_use":
                        if not has_tool:
                            msg.append("**Using tools**")
                        args = str(m.input) if str(m.input) != "{}" else ""
                        msg.append(f"```{m.name}({args})```")
                        has_tool = True

                if msg:
                    with st.chat_message(message["role"]):
                        st.markdown("\n\n".join(msg))
        else:
            if isinstance(message.get("tool_calls"), list):
                with st.chat_message("assistant"):
                    st.markdown(openai_render_tool_call(message))

            elif message["role"] != "tool":
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

def append_and_print(response, role = "assistant"):
    with st.chat_message(role):
        if st.session_state.provider == 'anthropic':
            if st.session_state.stream:
                r = st.write_stream(anthropic_stream(response))
                st.session_state.messages.append({ "role": role, "content": response.get_final_message().content })
                message = response.get_final_message()
                
                has_tool = False
                msg = []
                for m in message.content:
                    if hasattr(m, "type") and m.type == "tool_use":
                        has_tool = True
                        args = str(m.input) if str(m.input) != "{}" else ""
                        msg.append(f"```{m.name}({args})```")
                
                if has_tool:
                    msg = ["**Using tools**"] + msg
                    st.markdown("\n\n".join(msg))
                        
                return message
            else:
                if response.content is not None:
                    st.session_state.messages.append({"role": role, "content": response.content})
                    text = next((c.text for c in response.content if hasattr(c, "text")), '…')
                    st.markdown(text)

                    has_tool = False
                    msg = []
                    for m in response.content:
                        if hasattr(m, "type") and m.type == "tool_use":
                            has_tool = True
                            args = str(m.input) if str(m.input) != "{}" else ""
                            msg.append(f"```{m.name}({args})```")
                    
                    if has_tool:
                        msg = ["**Using tools**"] + msg
                        st.markdown("\n\n".join(msg))

                return response
        else:
            if st.session_state.stream:
                stream_completion = ToolhouseStreamStorage()
                r = st.write_stream(openai_stream(response, stream_completion))
                completion = stream_to_chat_completion(stream_completion)

                if completion.choices and completion.choices[0].message.tool_calls:
                    st.session_state.messages.append(completion.choices[0].message.model_dump())
                    st.markdown(openai_render_tool_call(completion.choices[0].message.to_dict()))
                else:
                    st.session_state.messages.append({"role": role, "content": r})
                
                return stream_completion
            else:
                st.session_state.messages.append(response.choices[0].message.model_dump())
                if (text := response.choices[0].message.content) is not None:
                    st.markdown(text)
                elif response.choices[0].message.tool_calls:
                    st.markdown(openai_render_tool_call(response.choices[0].message.to_dict()))
                return response
            
import streamlit as st
from toolhouse import Toolhouse
from llms import llms, llm_call
from http_exceptions.client_exceptions import NotFoundException
from utils import print_messages, append_and_print
from toolhouse import Toolhouse
import dotenv
import utils

def configure_togetger_ai():
    dotenv.load_dotenv()

    llm_choice = "Llama 3.1 90B (Together AI)"

    llm = llms.get(llm_choice)
    st.session_state.provider = llm.get("provider")
    model = llm.get("model")

    st.logo("logo.svg")
    return llm_choice, llm, model

def setup_tool_house(llm, user):
    th = Toolhouse(provider=llm.get("provider"))

    if st.session_state.bundle != st.session_state.previous_bundle:
        st.session_state.tools = th.get_tools(bundle=st.session_state.bundle)
        st.session_state.previous_bundle = st.session_state.bundle

    th.set_metadata("timezone", -7)
    if user:
        th.set_metadata("id", user)

    return th


def converse(th, llm_choice, llm, model):
    if prompt := st.chat_input("What is up?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with llm_call(
            provider=llm_choice,
            model=model,
            messages=st.session_state.messages,
            stream=st.session_state.stream,
            max_tokens=4096,
            temperature=0.1,
        ) as response:
            completion = append_and_print(response)
            tool_results = th.run_tools(
                completion, append=False
            )

            while tool_results:
                st.session_state.messages += tool_results
                with llm_call(
                    provider=llm_choice,
                    model=model,
                    messages=st.session_state.messages,
                    stream=st.session_state.stream,
                    max_tokens=4096,
                    temperature=0.1,
                ) as after_tool_response:
                    after_tool_response = append_and_print(after_tool_response)
                    tool_results = th.run_tools(
                        after_tool_response, append=False
                    )

def setup_user_header():
    with st.sidebar:
        st.title("Accessibility Adovcate")
        user = st.text_input("User", "daniele")
        return user
    

def page_config():
    st.set_page_config(
        page_title="Intelligence AI",
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "user" not in st.session_state:
        st.session_state.user = ""

    if "stream" not in st.session_state:
        st.session_state.stream = True

    if "provider" not in st.session_state:
        st.session_state.provider = llms.get(next(iter(llms))).get("provider")
        
    if "bundle" not in st.session_state:
        st.session_state.bundle = "default"

    if "previous_bundle" not in st.session_state:
        st.session_state.previous_bundle = "default"