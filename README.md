### Build Container
```bash
docker build \
	-t vo-transcriber:0.1.0 \
	.
```

### Run Container
```bash
mkdir ouput

docker run -d --name wiki-vos-transcribe \
	-v $(pwd)/output:/usr/src/app/output \
    -e ARGS="\
	-p https://ustream.univie.ac.at/search/episode.json?limit=200&offset=0&sid=761d2c76-498c-4135-980e-add6660f5ca6 \
	-vos '2. Aufzeichnung vom 20.12.2022' \
	-o output \
	-m tiny \
	-l de \
	-v \
	--txt \
	--vtt \
	--srt \
	--pdf \
	--page-numbers
	" \
	vo-transcriber:0.1.0
```