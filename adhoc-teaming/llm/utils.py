import logging
import yaml
from easydict import EasyDict

from transformers import AutoTokenizer
import tiktoken

OKRED = "\033[91m"
OKBLUE = "\033[94m"
ENDC = "\033[0m"
OKGREEN = "\033[92m"
OKYELLOW = "\033[93m"
OKPINK = "\033[95m"
OKSOMETHING = "\033[96m"


def text_to_logging_level(logging_level: str):
    if logging_level == "NOTSET":
        return logging.NOTSET
    elif logging_level == "DEBUG":
        return logging.DEBUG
    elif logging_level == "INFO":
        return logging.INFO
    elif logging_level == "WARNING":
        return logging.WARNING
    elif logging_level == "CRITICAL":
        return logging.CRITICAL
    else:
        raise ValueError


def load_config(config_name: str):
    with open(f"configs/{config_name}", "r") as yamlfile:
        data = yaml.load(yamlfile, Loader=yaml.FullLoader)
    return EasyDict(data)


def count_tokens(text):
    tokenizer = tiktoken.get_encoding("cl100k_base")
    input_ids = tokenizer.encode(text)
    num_tokens = len(input_ids)
    return num_tokens


def break_up_text_to_chunks(text, chunk_size=2000, overlap=100):
    tokenizer = AutoTokenizer.from_pretrained("gpt2")
    tokens = tokenizer.encode(text)
    num_tokens = len(tokens)

    chunks = []
    for i in range(0, num_tokens, chunk_size - overlap):
        chunk = tokens[i : i + chunk_size]
        chunks.append(chunk)

    return chunks


def python_to_markdown_code(code):
    markdown_code = "```python\n" + code + "\n```"
    return markdown_code