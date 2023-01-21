### Build Container
```bash
docker build \
	-t vo-transcriber:0.1.0 \
	.
```

### Run Container
```bash
mkdir input
mkdir ouput

docker run -d --name wiki-vos-transcribe \
	-v $(pwd)/input:/usr/src/app/input \
	-v $(pwd)/output:/usr/src/app/output \
    -e AUDIO_FILES="*" \
	-e LANGUAGE="None" \
	-e WHISPER_MODEL="small" \
	vo-transcriber:0.1.0
```