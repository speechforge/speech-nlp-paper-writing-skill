# Figure and Table Plan: @@PROJECT_NAME@@

Class **evidence** = numbers (deterministic script only). Class **concept** = idea, pipeline, teaser (diagram tool or image generation; never numeric evidence).

| ID | Class | Role | Single message | Source (data file or spec) | Tool | Caption written | In paper | On website |
|---|---|---|---|---|---|---|---|---|
| Fig. 1 | concept | teaser | The failure of prior work and this work's remedy, readable without the text | diagrams/teaser.json | make_diagram.py | no | no | yes |
| Fig. 2 | concept | method overview | | diagrams/method.json | make_diagram.py | no | no | yes |
| Tab. 1 | evidence | main comparison | | results/main.csv | make_latex_table.py | no | no | yes |
| Fig. 3 | evidence | ablation | | results/ablation.csv | make_plots.py | no | no | yes |
| Fig. 4 | evidence | qualitative (spectrograms or outputs) | | demo/assets | make_audio_figs.py | no | no | yes |
