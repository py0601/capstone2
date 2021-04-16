# https://findface.netlify.app/ 코드 출처

from __future__ import division

import re
# 종료 키워드를 받기 위해 사용
import sys
# 스트림의 write, flush
import io
from google.cloud import speech

# enums, types은 speech에 포함되어 따로 import하지 않아도됨
# pip install pipwin을 먼저 하고, pipwin install pyaudio하면 오류 발생 안함

import pyaudio
from six.moves import queue

# 오디오 녹음 parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms


class MicrophoneStream(object):
    """chunk,문자를 받아오는 오디오 녹음 스트림 동작"""
    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk

        # 오디오 데이터의 thread-safe 버퍼 만들기
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            # API는 현재 모노(단방향) 오디오만 지원
            channels=1, rate=self._rate,
            input=True, frames_per_buffer=self._chunk,
            # 오디오 스트림을 비동기로 실행하여 버퍼 채움
            # 입력장치의 버퍼가 작동하지 않도록 해야 함
            # 호출 스레드가 네트워크 요청을 만드는 동안 오버플로우 발생
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # 제너레이터에 종료 신호를 보내 클라이언트를 종료
        # streaming_contract 메서드는 프로세스 종료를 차단하지 않음
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """오디오 스트림에서 버퍼로 데이터를 계속 수집"""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            # blocking get()을 사용해 하나 이상의 chunk, 문자가 있는지 확인
            # 데이터 및 chunk가 없음일 경우 반복 중지. 오디오 스트림 끝냄.
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            # 버퍼에 들어온 데이터 사용
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b''.join(data)


def listen_print_loop(responses):
    """서버 응답을 반복하고 인쇄"""


    num_chars_printed = 0
    for response in responses:
        if not response.results:
            continue

        result = response.results[0]
        if not result.alternatives:
            continue

        transcript = result.alternatives[0].transcript

        # 입력할 때마다 임시 결과 표시.

        overwrite_chars = ' ' * (num_chars_printed - len(transcript))

        if not result.is_final:
            sys.stdout.write(transcript + overwrite_chars + '\r')
            sys.stdout.flush()

            num_chars_printed = len(transcript)

        else:
            print(transcript + overwrite_chars)

            # 기록된 문구 중 하나라도 다음과 같을 경우 인식 종료
            if re.search(r'\b(종료|그만)\b', transcript, re.I):
                print('Exiting..')
                break

            num_chars_printed = 0


def main():
    # http://g.co/cloud/speech/docs/languages
    # 지원되는 언어 목록
    language_code = 'ko-KR'  # a BCP-47 language tag

    client = speech.SpeechClient()
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code=language_code)
    streaming_config = speech.StreamingRecognitionConfig(
        config=config,
        interim_results=True)

    with MicrophoneStream(RATE, CHUNK) as stream:
        audio_generator = stream.generator()
        requests = (speech.StreamingRecognizeRequest(audio_content=content)
                    for content in audio_generator)

        responses = client.streaming_recognize(streaming_config, requests)

        listen_print_loop(responses)


if __name__ == '__main__':
    main()
