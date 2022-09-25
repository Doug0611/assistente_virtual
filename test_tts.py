def text_to_speech(text: str) -> None:
    try:
        import azure.cognitiveservices.speech as speechsdk
    except ImportError:
        ...
    speech_config = speechsdk.SpeechConfig(
        subscription=" ******",
        region=" ***** "
    )
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

