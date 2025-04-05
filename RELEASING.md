# Release Instructions

- follow the instructions in [`workflow.md`](workflow.md) for the download and conversion of Lexibank data
- update the results reported in [`workflow.md`](workflow.md) to make sure they are up to date
- recreate figures

```
$ cldfbench cldfviz.map cldf/phonology-metadata.json --language-properties="LexiCore" --language-properties-colormaps='{"1":"#050505"}'  --markersize 20 --pacific-centered --no-legend --format png --width 30 --height 15 --output plots/basemap.png

$ cldfbench cldfviz.map cldf/phonology-metadata.json --language-properties="LexiCore,ClicsCore,CogCore" --language-properties-colormaps='{"1":"#fde725"},{"1":"#21918c", "0":"#f8f8ff"},{"1":"#440154", "0":"#f8f8ff"}'  --markersize 30 --pacific-centered --width 30 --height 15 --output plots/doculects.png --format png

$ cldfbench cldfviz.map cldf/phonology-metadata.json --language-properties="Forms,Concepts" --language-properties-colormaps="plasma,viridis"  --markersize 30 --pacific-centered --width 30 --height 15 --format png --output plots/coverage.png

$ cldfbench cldfviz.map cldf/phonology-metadata.json --parameters CVQualityRatio --language-filters '{"Name":"^(?!Adyghe|Yorno So|Togo Kan|Karata$).*$", "Glottocode": "^(?!kajt1238)"}' --colormaps plasma --markersize 30 --pacific-centered --format png --width 30 --height 15 --output plots/CVQualityRagio

$ cldfbench cldfviz.map cldf/phonology-metadata.json --parameters VelarNasal --colormaps tol --pacific-centered --markersize 30 --format png --width 30 --height 15 --output plots/VelarNasal.png

$ cldfbench cldfviz.map cldf/lexicon-metadata.json --parameters SkinInBark --pacific-centered --markersize 30 --format png --width 30 --height 15 --output plots/SkinInBark.png

$ cldfbench cldfviz.map cldf/lexicon-metadata.json --parameters ArmAndHand,LegAndFoot --pacific-centered --markersize 30 --format png --width 30 --height 15 --output plots/ArmAndHand-LegAndFoot.png
```

