# Automated French translation of the Lewis and Clark expedition journals using ChatGPT4 Turbo

## \[French\] Presentation

*Ceci est une traduction française du livre "The Journals of Lewis and Clark, 1804-1806" qui contient les récits de voyages de William Clark et Meriwether Lewis lors de leur expédition à travers l'Amérique, après que la Louisiane soit vendue aux États-Unis. Je n'ai pas pu trouver de traduction de ce texte en français, et j'ai donc décidé d'utiliser les outils d'OPENAI pour réaliser une traduction automatique. Bien que le résultat soit de très bonne qualité, je ne peux faire aucune promesse quant à la fidélité de la traduction.*

- [EPUB](https://github.com/Blizarre/lewis_clark_journal_french_translation/raw/master/lewis_and_clark_journal.epub)
- [PDF](https://github.com/Blizarre/lewis_clark_journal_french_translation/raw/master/lewis_and_clark_journal.pdf)
- [Markdown](https://github.com/Blizarre/lewis_clark_journal_french_translation/raw/master/lewis_and_clark_journal.md)

## Introduction

I was talking to my father about the [Lewis and Clark expedition](https://en.wikipedia.org/wiki/Lewis_and_Clark_Expedition) of 1804.

I found the original document (in the public domain) on the [gutenberg project's webpage](https://www.gutenberg.org/ebooks/8419). I translated a couple of entries for him and he looked interested. Unfortunately I couldn't find any French translation of these work for him to read.

Given the simple nature of the medium (cleanly separated entries with a title), we wondered if we could use ChatGPT to perform the translation.
A couple of manual tests showed that the result was very good. We were really surprised by the quality of the translation.

I decided to build a simple script (Python / Async / openai lib) to translate every single entries (~ 1600) and generate a file in markdown. [pandoc](https://pandoc.org) was then used to convert it into epub and pdf.

The model used is GPT4-Turbo (`gpt-4-1106-preview`).

## Original and translation quality

The original document is not perfect, with plenty of abbreviations, old-fashioned words, truncated phrases and OCR errors. But ChatGPT4 handled them pretty well.

> [Clark, May 29, 1804]
>
> Tuesday 29th May Sent out hunters, got a morning obsvtn and one at 12<br/>
> oClock, rained last night, the river rises fast The Musquetors are<br/>
> verry bad, Load the pierogue

Was translated into

> ## Clark, May 29, 1804
> Mardi 29 mai, envoyé des chasseurs, pris une observation le matin et une à 12 heures, il a plu la nuit dernière, la rivière monte rapidement. Les moustiques sont très mauvais, chargez la pirogue.


The only caveat is that the tables were not translated well. They were not formatted very well in the original document, so the output is not very good:

> F        Inch<br/>
> Length from nose to tail                 5        2<br/>
> Circumpherence in largest part--                41/2<br/>
> Number of scuta on belly--221<br/>
> Do. on Tale--53<br/>

was translated into:

> F       Pouces Longueur du nez à la queue                   5        2 Circonférence à la partie la plus large--                4 1/2 Nombre de scutelles sur le ventre--221 Idem sur la queue--53

We decided that for our purpose this wasn't an issue, but that would be a potential improvement.

## Commands

```shell
# Install poetry and the necessary dependencies
pip install poetry
poetry install --no-root

# Run the translation
export OPENAI_API_KEY=$(cat ~/.openai)
poetry run python -u translate.py lewis.txt --start 0 --number 1621 --parallel 5 | tee lewis_and_clark_journal.md

# Convert to pdf
pandoc -f markdown -t pdf -o lewis_and_clark_journal.pdf --metadata title="Journal de l'exploration de la Louisiane par Lewis et Clack" --metadata author="Meriwether Lewis, William Clark" --metadata lang="fr"  --toc-depth 1 lewis_and_clark_journal.md --pdf-engine=xelatex

# Convert to epub
pandoc -f markdown -t epub -o lewis_and_clark_journal.epub --metadata title="Journal de l'exploration de la Louisiane par Lewis et Clack" --metadata author="Meriwether Lewis, William Clark" --metadata lang="fr"  --toc-depth 1 lewis_and_clark_journal.md
```
## Note to self

- The current script load all the translations in memory and then write them to disk. The script died in the middle of a run several times (low battery, API rate limits,...) which lost several hundred entries and hours of work. Write the script so that the input / output of each API call is persisted to the disk. And load existing translations automatically instead of calling the API.
- Having the ability to run the work in chunks (as the script is configured now) is convenient, but require some manual work to merge the files and track indexes. Ideally this should not be necessary. Cleanly separating file loading, translation, and then generation into maybe 3 scripts would have been better
- Costs go up quicky! Set generous limits in place at the beginning instead of raising them after each failures (and wasting the money)



Github repository: https://github.com/Blizarre/lewis_clark_journal_french_translation
