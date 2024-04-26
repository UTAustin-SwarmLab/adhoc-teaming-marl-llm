import abc
from typing import *
import openai
import re
import logging
import os
import requests
import pandas as pd
import seaborn as sns
from loguru import logger
import abc
import os

import cv2
import numpy as np
from llm.utils import (
    OKRED,
    OKBLUE,
    OKYELLOW,
    OKGREEN,
    OKPINK,
    OKSOMETHING,
    ENDC,
    count_tokens,
    python_to_markdown_code,
)

import requests
import os
import json
from typing import Tuple


TOGETHER_KEY = os.getenv("TOGETHER_KEY")


class Together:
    def __init__(self, model: str = "CodeLlama-34b-Instruct") -> None:
        self.model = model

    def start_model(self):
        url = f"https://api.together.xyz/instances/start?model=togethercomputer%2F{self.model}"
        headers = {"accept": "application/json", "Authorization": f"Bearer {TOGETHER_KEY}"}
        response = requests.post(url, headers=headers)
        print(response.text)

    def stop_model(self):
        url = f"https://api.together.xyz/instances/stop?model=togethercomputer%2F{self.model}"
        headers = {"accept": "application/json", "Authorization": f"Bearer {TOGETHER_KEY}"}
        response = requests.post(url, headers=headers)
        print(response.text)

    def query_model(self, history_prompt: Tuple[str]):
        url = "https://api.together.xyz/inference"
        
        format_string, prompt = history_prompt

        payload = {
            "model": f"togethercomputer/{self.model}",
            "prompt": prompt,
            "max_tokens": 4000,
            "request_type": "language-model-inference",
            "temperature": 0.0,
            "top_p": 0.7,
            "top_k": 50,
            "repetition_penalty": 1,
            "type": "chat",
            "temperature": 0.7,
            "top_p": 0.7,
            "top_k": 50,
            "repetition_penalty": 1,
            "stop": ["</s>", "[INST]"],
            "prompt_format_string": format_string,
        }

        # headers = {
        #     "accept": "application/json",
        #     "content-type": "application/json",
        #     "Authorization": f"Bearer {TOGETHER_KEY}"
        # }
        headers = {"Authorization": f"Bearer {TOGETHER_KEY}"}

        response = requests.post(url, json=payload, headers=headers)
        response = json.loads(response.text)
        return response["output"]["choices"][0]["text"]

    def gpt_history_to_together(self, gpt_history):
        together_history = """\n<human>: Hi!\n<bot>: My name is Bot, model version is 0.16, part of an open-source kit for fine-tuning new bots! I was created by Together, LAION, Ontocord and the open-source community. I am not human, not evil and not alive, and thus have no thoughts and feelings, but I am programmed to be helpful, polite, honest, and friendly.\n"""
        for message in gpt_history[:-1]:
            if message["role"] == "user":
                together_history += f"[INST] {message['content']}\n [/INST]"
            if message["role"] == "assistant":
                together_history += f" {message['content']}\n"
        together_history += "[INST]  {prompt}\n [/INST]"
        prompt = gpt_history[-1]["content"]
        return (together_history, prompt)


class GPTConversation:

    
    def __init__(self, config) -> None:
        super().__init__()
        self.prompt = ""
        self.detection_list = []
        self.ltl_info = None
        self.config = config
        self.specification_prompt = '''
        Now list all the frames which satisfy the task following the example specified in the task description. The output must meet the following specifications:
        1. Frame outputs must be a list of frames that satisfy the condition or [None] if no such frames exist . For  example [1,13,100] where condition is met. Refer to the task example. 
        2. No duplicates Example : [100,100,120,120].
        3. Output must not have other information or text or statement. Only a list starting and ending with [].
        Response must be only the list of frame numbers eg [1,13,100]. Must return [None] if no such frames or detections exist. 

        '''

    def add_specificaton(self, proposition: str) -> None:
        ltl_info = {}
        if "!" in proposition:
            avoid_proposition = proposition.split("ß!")[-1][1:].split('"')[0]  # [1:-2].replace('"', "")
            ltl_info["avoid_proposition"] = avoid_proposition
        else:
            ltl_info["avoid_proposition"] = None
        return ltl_info
    
    def get_prompt(self) -> str:
        pass

    def process_response(self, response: str) -> None:
        response_find = re.findall(r'\[(.*?)\]', response)
        
        if isinstance(response_find, list) and len(response_find) > 0:
            ranges = response_find[-1].strip("[]").split(',')
        else:
            ranges = response.strip("[]").split(',')

        if isinstance(ranges, str):
            raise ValueError("Output must be a list of frames or [None] if no such frames exist")
        
        # Splitting each range by '-' to get the individual elements and converting them to tuples
        ranges = [r.split("-") for r in ranges]
        list_ranges = [[] for _ in range(len(ranges))]
        try:
            for j,range_ in enumerate(ranges):
                list_ = []
                if range_[0] == "None":
                    continue
                elif len(range_) == 1 and range_[0] != "":
                        list_ = [int(range_[0].strip())]
                else:
                    for i in range(int(range_[0].strip()), int(range_[1].strip()) + 1):
                        list_.append(i)
                list_ranges[j] = list_
        except:
            print("NO OUTPUT FROM THE MODEL")
        return list_ranges

    def add_detections(self, detections: List[str]) -> None:
        self.detections = detections

    def obtain_initial_message(self):
        pass

class GPTConversationDetection(GPTConversation):
    def __init__(self, config) -> None:
        '''
        List of objects detected in the video
        '''
        super().__init__(config= config)
    
    def build_query_prompt(self, ltl_formula, proposition_list = None) -> str: 
        self.prompt = "These are list of detected objects in the video specified in the format:\n"
        for j,detections in enumerate(self.detections):
            if len(detections)>0:
                self.prompt += f"{j}: {str(detections)}\n"

        self.prompt += "The condition for frame search is:\n"
        self.prompt += f"{ltl_formula}\n"
        self.prompt += self.specification_prompt

    def add_detections(self, detections: List[str]) -> None:
        self.detections.append(detections)
    
    def obtain_initial_message(self):
        message = ("""You are Language Assistant to enable searching a 
        video frame for objects satisfying a condition.
        
        TASK DESCRIPTION:
        I will be giving you the list of objects detected in the video and a condition from search.
        The list of objects will be specified in this format and include those
        frames where an object is detected:
                   Frame 1: [object1, object2, object3]
                   Frame 2: [object1, object2]
        A condition is of the form: 
                   object1 Until object2
                   object1 Until (object2 and object3),
                   Eventually object 1,
                   Always object 2, etc

        You can use the list of objects detected in the video to help you. You dont have access to the video.
        Your job is to specify the frame numbers where the rule is satisfied. There can 
        be many such sequences. If you cannot find any sequence, you must return output [None]. To clarify you will
        be looking for frames where the rule is satisfied. The output is a list of frame numbers such as
         "[1,20, 25, 50]", specifying the frames where the rule holds
        
        An example of the list of detections per frame is as follows:
        1: ['person', 'car']
        2: ['person', 'car']
        10: ['person', 'car']
        30: ['truck']
        40: ['car']
        44: ['person']
        50: ['car','truck']
        
        'person' until 'truck' gives all frames of 'person' and 'truck' if 'truck' shows up."
        Eventually 'person' gives all frames of 'person' eventually showing up
        Always 'car' should give all frames of 'car' always showing up
        ('car' and 'truck') until 'person' gives all frames of 'car' and 'truck' showing up in the same frame if 'person' shows up; all frames of 'person' included
        'car' and 'truck' should gives all frames of 'car', 'truck' showing up in the same frame
        # """ ) 
        # + "Do not give me an output. Verify that you understand the task by only typing 'I understand the task'.")
        return message
  
    def clear(self):
        self.detections = []
        self.prompt = ""


class OpenAIPrompt:
    def __init__(self, config):
        # Which model to use.
        # davinci is the most powerful, but it's also the slowest and most expensive
        # ada is the fastest and cheapest, but it's also the least powerful
        self.config = config
        self.gpt_history = []
        self.gpt_full_history = []
        self.final_code = None
        self.initial_message = None
        self.retries = 5
        openai.api_key = os.getenv("OPENAI_API_KEY")

        if config.API == "TOGETHER":
            self.together_model = Together(self.config.LLMModel)
            self.together_model.start_model()

    # def init_hugging_face_model(self, init_prompt: str):
    #     self.llm_chain = LLMChain(
    #         prompt=init_prompt,
    #         llm=HuggingFaceHub(repo_id="google/flan-t5-xl", model_kwargs={"temperature": 0, "max_length": -1}),
    #     )

    def initialize_message_history(self, initial_message):
        #logger.info(initial_message)
        if self.initial_message is None:
            self.initial_message = initial_message
        
        if self.config.LLMModel =='gpt-3.5-turbo-instruct':
            self.gpt_history.append({"role": "user", "content": initial_message})
            output = ""
        else:
            self.gpt_history.append({"role": "user", "content": initial_message})
            output = ""
            #output = self.query_model(prompt=initial_message)
        return output

    def summarize_text(self):
        self.gpt_full_history = self.gpt_full_history + self.gpt_history

        summarization_prompt = "Can you summarize the conversation so far."
        self.gpt_history.append({"role": "user", "content": summarization_prompt})
        output = self.ask_gpt("summarize_text")
        self.gpt_history = []
        self.initialize_message_history(
            self.initial_message, use_case="summerize_text"
        )  # Does this typo effect anything?
        self.gpt_history.append({"role": "user", "content": "What have we talked about our Tunnel Flipping alert ?"})
        self.gpt_history.append({"role": "assistant", "content": output})

    def ask_together(self):
        together_history = self.together_model.gpt_history_to_together(self.gpt_history)
        output = self.together_model.query_model(together_history)
        self.gpt_history.append({"role": "assistant", "content": output})
        logger.info(OKYELLOW + output + ENDC)
        return output

    def ask_gpt(self):
        
        if self.config.API == "OPENAI":
            if self.config.LLMModel == "gpt-3.5-turbo-instruct":
                prompt = ""
                for j,history in enumerate(self.gpt_history):
                    if history['role'] == "user":
                        prompt += f"{history['content']}\n"
                logger.info(OKBLUE + prompt + ENDC)  
                completion = openai.Completion.create(
                    model=self.config.LLMModel, 
                    prompt= prompt,
                    temperature=self.config.temperature,
                    stop=None,                  
                    timeout=10,
                    max_tokens= 2048
                )
                output = completion.choices[0].text
            else:
                message = [{'role': "user", 'content': ""}]
                for j,history in enumerate(self.gpt_history):
                    if history['role'] == "user":
                        message[0]['content'] += f"{history['content']}\n"
                logger.info(OKBLUE + message[0]['content'] + ENDC)  
                completion = openai.ChatCompletion.create(
                    model=self.config.LLMModel, 
                    messages=message,
                    temperature=self.config.temperature,
                    stop=None,                  
                    timeout=10
                )
                output = completion.choices[0].message["content"]
        else:
            raise ValueError
        self.gpt_history.append({"role": "assistant", "content": output})
        logger.info(OKYELLOW + output + ENDC)
        return output

    def sanitize_output(self):
        # Remove json.dumps lines
        specifaction_prompt ='''
        The frame outputs must meet the following specifications:
        1. Frame outputs must be a list or [None]. For  example [1, 13, 100] where LTL is met. Refer to the task example. 
        2. No duplicates (Example : [100, 100, 120, 120].
        3. Must be only the list of frame numbers or [None] if there are no satisfactions. Must not have other information/text.
        Do the frame outputs satisfy these specification. If yes respond by saying Yes, 
        If not correct the output to meet these specifications. Must list the frames in the format specified above.
        No other information/text is needed.
        '''
        self.gpt_history.append({"role": "user", "content": specifaction_prompt})
        return self.query_model(prompt=specifaction_prompt)
        

    def query_model(self, prompt) -> str:
        self.gpt_history.append({"role": "user", "content": prompt})
        if self.config.API == "OPENAI":
            output = self.ask_gpt()
        elif self.config.API == "TOGETHER":
            output = self.ask_together()
        else:
            logging.error("Model not defined")
        return output

    def query(self, prompt):
        
        for j in range(self.retries):
            try:
                output = self.query_model(prompt)
                return output
            except Exception as e:
                logger.error(e)
                logger.error("Retrying...")
                continue
        # santised_output = self.sanitize_output()
        # if 'Yes' not in santised_output:
        #     while 'Yes' not in santised_output:
        #         santised_output = self.sanitize_output()
        #     return santised_output
        # else:
        #     return output
        return '[None]'
    
    def clear(self):
        self.gpt_history = []
        self.gpt_full_history = []
