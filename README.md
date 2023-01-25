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
	--vos "8. Aufzeichnung vom 25.01.2023" \
	--vos "7. Aufzeichnung vom 19.01.2023" \
	--vos "6. Aufzeichnung vom 18.01.2023" \
	--vos "1. Aufzeichnung vom 07.12.2022" \
	-o output \
	-m medium \
	-l de-DE \
	-v \
	--txt \
	--vtt \
	--srt \
	--pdf \
	--page-numbers
```



