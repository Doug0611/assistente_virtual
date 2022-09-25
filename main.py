import json
import os
import re
import sys
import locale
from skills import Skills
from typing import Optional
from time import sleep
import asyncio

from textblob.classifiers import NaiveBayesClassifier
from vosk import KaldiRecognizer, Model, SetLogLevel
import azure.cognitiveservices.speech as speechsdk
from pyaudio import PyAudio, paInt16


SetLogLevel(-1)

locale.setlocale(
    category=locale.LC_ALL,
    locale=locale.getlocale()[0]
)


class VirtualAssist(Skills):
    VIRTUAL_ASSIST_NAME = 'safira'

    def __init__(self) -> None:
        Skills.__init__(self)

    def run(self) -> None:
        while True:
            user_speech = self.__speech_to_text_recognition()
            print(f'\033[1;92m>>>\033[m falou: {user_speech["text"]}')

            if self.__call_virtual_assistant(user_speech['text']):
                self.__text_to_speech('olá')
                user_command = self.__speech_to_text_recognition()
                if len(user_command['text']) > 0:
                    self.__call_skill(user_command['text'])

    def __text_to_speech(self, text: str) -> None:
        try:
            data = self.__get_api_key('m_azure')
            speech_config = speechsdk.SpeechConfig(
                subscription=data['api_key'],
                region=data['region']
            )
        except ValueError:
            sys.exit(1)
        speech_config.set_speech_synthesis_output_format(
            speechsdk.SpeechSynthesisOutputFormat.Riff24Khz16BitMonoPcm
        )
        speech_config.speech_synthesis_language = "pt-BR"
        speech_config.speech_synthesis_voice_name = "pt-BR-FranciscaNeural"

        audio_config = speechsdk.audio.AudioOutputConfig(
            use_default_speaker=True
        )
        synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config,
            audio_config=audio_config
        )
        synthesizer.speak_text_async(text)

    def __get_api_key(self, api_service: str) -> dict:
        with open('auth.json', encoding='utf-8') as key:
            data_key = json.loads(key.read())
            return data_key[api_service]

    def __call_virtual_assistant(self, text: str) -> bool:
        init = re.findall(self.VIRTUAL_ASSIST_NAME, text)
        return True if init else False

    def __classifier_commands(self, command: str) -> str:
        try:
            with open('./cmds.json', mode='r', encoding='utf-8') as file:
                cl = NaiveBayesClassifier(file, format='json')
                return cl.classify(command)
        except FileNotFoundError:
            self.__text_to_speech('''
            eita. não encontrei meu arquivo de comandos, verifique para mim.
            ''')
            sys.exit(1)

    def __mine_search_term(self, text: str, label: Optional[str] = '') -> str:
        try:
            with open('cmds.json', encoding='utf-8') as cmds:
                data = json.loads(cmds.read())
                stopwords = []
                for word in data:
                    if label:
                        if word['label'] == label:
                            stopwords.append(word['text'])
                    else:
                        stopwords.append(word['text'])
        except FileNotFoundError:
            self.__text_to_speech('''
            eita. não encontrei meu arquivo de comandos, verifique para mim.
            ''')
            sys.exit(1)
        else:
            for term in stopwords:
                if re.findall(term, text):
                    remove_stopwords = list(text.partition(term))
                    remove_stopwords.remove('')
                    return remove_stopwords.pop().strip()
            return text

    def __call_skill(self, command: str) -> None:
        start_skill = None
        classifier = self.__classifier_commands(command)

        if classifier == 'time':
            start_skill = self.current_time()
            sleep(0.1)
            self.__text_to_speech(start_skill)
        elif classifier == 'date':
            start_skill = self.current_date()
            sleep(0.1)
            self.__text_to_speech(start_skill)
        elif classifier == 'search':
            self.__text_to_speech('ok, só um estante.')
            quest_term = self.__mine_search_term(command, 'search')
            start_skill = self.quest(quest_term)
            sleep(0.1)
            self.__text_to_speech(start_skill)
        elif classifier == 'news':
            self.__text_to_speech('ok, só um estante.')
            loop = asyncio.get_event_loop()
            query = self.__mine_search_term(command, 'news')
            start_skill = self.get_top_headlines(query)
            run = loop.run_until_complete(start_skill)

            for article in run['articles']:
                self.__text_to_speech(article['title'])
        else:
            self.__text_to_speech('não entendi')

    def __speech_to_text_recognition(self) -> str:
        MODEL_PATH = os.path.join('./language_models/pt_br')
        if not os.path.exists(MODEL_PATH):
            self.__text_to_speech('''
            humm... não encontrei nenhum modelo de reconhecimento de fala, estou disponibilizando no seu terminal uma url para download.
            ''')
            print('\033[1;33mURL: https://alphacephei.com/vosk/models\033[m')
            sys.exit(1)
        try:
            microphone = PyAudio()
            stream = microphone.open(
                format=paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=8000
            )
            stream.start_stream()
        except ValueError:
            self.__text_to_speech('''
            humm... não consigo te ouvir, verifique seu microfone.''')
            sys.exit(1)
        except OSError:
            self.__text_to_speech('''
            humm... não consigo te ouvir, verifique seu microfone.''')
            sys.exit(1)

        model = Model(MODEL_PATH, lang='pt-br')
        recognize = KaldiRecognizer(model, 16000)
        try:
            while True:
                data = stream.read(4000, exception_on_overflow=False)
                if recognize.AcceptWaveform(data):
                    return json.loads(recognize.FinalResult())
        except KeyboardInterrupt:
            print('\033[1;31m>>> encerrando aplicação...\033[m')
            sys.exit(1)


if __name__ == '__main__':
    virtual_assistant = VirtualAssist()
    virtual_assistant.run()
