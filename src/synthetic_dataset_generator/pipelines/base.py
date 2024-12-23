import gradio as gr
from distilabel.llms import InferenceEndpointsLLM, OllamaLLM, OpenAILLM

from synthetic_dataset_generator.constants import (
    API_KEYS,
    HUGGINGFACE_BASE_URL,
    MAGPIE_PRE_QUERY_TEMPLATE,
    MODEL,
    OLLAMA_BASE_URL,
    OPENAI_BASE_URL,
    TOKENIZER_ID,
)

TOKEN_INDEX = 0


def _get_next_api_key():
    global TOKEN_INDEX
    api_key = API_KEYS[TOKEN_INDEX % len(API_KEYS)]
    TOKEN_INDEX += 1
    return api_key


def _get_llm(use_magpie_template=False, **kwargs):
    if OPENAI_BASE_URL:
        llm = OpenAILLM(
            model=MODEL,
            base_url=OPENAI_BASE_URL,
            api_key=_get_next_api_key(),
            **kwargs,
        )
        if "generation_kwargs" in kwargs:
            if "stop_sequences" in kwargs["generation_kwargs"]:
                kwargs["generation_kwargs"]["stop"] = kwargs["generation_kwargs"][
                    "stop_sequences"
                ]
                del kwargs["generation_kwargs"]["stop_sequences"]
            if "do_sample" in kwargs["generation_kwargs"]:
                del kwargs["generation_kwargs"]["do_sample"]
    elif OLLAMA_BASE_URL:
        if "generation_kwargs" in kwargs:
            if "max_new_tokens" in kwargs["generation_kwargs"]:
                kwargs["generation_kwargs"]["num_predict"] = kwargs[
                    "generation_kwargs"
                ]["max_new_tokens"]
                del kwargs["generation_kwargs"]["max_new_tokens"]
            if "stop_sequences" in kwargs["generation_kwargs"]:
                kwargs["generation_kwargs"]["stop"] = kwargs["generation_kwargs"][
                    "stop_sequences"
                ]
                del kwargs["generation_kwargs"]["stop_sequences"]
            if "do_sample" in kwargs["generation_kwargs"]:
                del kwargs["generation_kwargs"]["do_sample"]
            options = kwargs["generation_kwargs"]
            del kwargs["generation_kwargs"]
            kwargs["generation_kwargs"] = {}
            kwargs["generation_kwargs"]["options"] = options
        llm = OllamaLLM(
            model=MODEL,
            host=OLLAMA_BASE_URL,
            tokenizer_id=TOKENIZER_ID or MODEL,
            **kwargs,
        )
    elif HUGGINGFACE_BASE_URL:
        kwargs["generation_kwargs"]["do_sample"] = True
        llm = InferenceEndpointsLLM(
            api_key=_get_next_api_key(),
            base_url=HUGGINGFACE_BASE_URL,
            tokenizer_id=TOKENIZER_ID or MODEL,
            **kwargs,
        )
    else:
        llm = InferenceEndpointsLLM(
            api_key=_get_next_api_key(),
            tokenizer_id=TOKENIZER_ID or MODEL,
            model_id=MODEL,
            magpie_pre_query_template=MAGPIE_PRE_QUERY_TEMPLATE,
            **kwargs,
        )

    return llm


try:
    llm = _get_llm()
    llm.load()
    llm.generate([[{"content": "Hello, world!", "role": "user"}]])
except Exception as e:
    gr.Error(f"Error loading {llm.__class__.__name__}: {e}")
