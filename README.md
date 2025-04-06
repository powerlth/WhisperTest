# Whisper 테스트

기본적으로 ffmpeg 라이브러리가 필요
```
pip install ffmpeg
```

whisper 라이브러리 설치
```
pip install openai-whisper
```

모델 선택 - large / turbo

guy.mp3 기준 

large 모델 처리 시간 : 9.3s

turbo 모델 처리 시간 : 1.2s

rtx 4070 8GB 기준

large 모델 vram 사용량 : 9.6GB (7.9GB 전용메모리 + 1.7GB 공유메모리)

turbo 모델 vram 사용량 : 4.9GB

![예시이미지](https://github.com/powerlth/WhisperTest/blob/master/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7%202025-04-06%20183123.png)
