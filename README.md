### Build Container
```bash
docker build \
	-t vo-transcriber:0.1.0 \
	.
```

### Run Container
Get VOs from link:
```bash
mkdir ouput

docker run -d --name wiki-vos-transcribe \
	vo-transcriber:0.1.0 \
	-p "https://ustream.univie.ac.at/search/episode.json?limit=200&offset=0&sid=761d2c76-498c-4135-980e-add6660f5ca6"

docker logs wiki-vos-transcribe
```


Run transcriber:
> Don't forget to properly escape your url)
```bash
mkdir ouput

docker run -d --name wiki-vos-transcribe \
	-v $(pwd)/output:/usr/src/app/output \
	vo-transcriber:0.1.0 \
	-k "https://ustream.univie.ac.at/search/episode.json?limit=200&offset=0&sid=761d2c76-498c-4135-980e-add6660f5ca6" \
	-vos "2. Aufzeichnung vom 20.12.2022" \
	-o output \
	-m tiny \
	-l de-DE \
	-v \
	--txt \
	--vtt \
	--srt \
	--pdf \
	--page-numbers
```