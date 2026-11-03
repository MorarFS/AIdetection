# Dan Sociu and Gemini detector and stylometry case study

Pangram 4.1 classified the published Romanian story as **Mixed**, displaying **66% AI and 34% human**. Its segment labels cover the entire Kraftwerk episode as AI. These observations are consistent with AI involvement, but do not establish which model was used, who wrote particular passages, or how the text was revised.

**Text:** Dan Sociu & Gemini, *La sud de Londra (fragment)*, *Steaua* 10/2026, printed pages 48–49, PDF pages 49–50. The co-credit is disclosed by the magazine. It is a provenance claim rather than independent generation evidence.

**Scan:** 3 November 2026, 8:51 PM, Asia/Hong_Kong. The web interface displayed version 4.1 and counted 1,753 words. The input was the Romanian body alone, excluding the title and author/Gemini credit. No translation was used.

[Read the full report with all 24 Pangram highlights](https://morarfs.github.io/AIdetection/reports/sociu-steaua-2026-11-03/analysis_report.html).

## Pangram labels by episode

These values group the existing whole-document segment labels by episode. They are not independent episode scans. The word units are Unicode word runs, whose total matches the website's displayed count.

| Episode | Words in AI-labeled passages | AI-labeled / total word units |
|---|---:|---:|
| Billie Eilish | 69.2% | 436 / 630 |
| Thom Yorke | 41.6% | 171 / 411 |
| Nick Cave | 49.7% | 153 / 308 |
| Kraftwerk | 100.0% | 404 / 404 |

Across the text, 1,164 of 1,753 word units fall in AI-labeled segments. There are 12 AI-labeled and 12 human-labeled segments of different lengths. No segment is labeled AI-assisted. The 66% document value is the website's rounded display, not a raw API fraction or a measured proportion of actual authorship.

## Observable style patterns

**The same narrative mechanism recurs four times.** Each episode locates the origin of a famous musician's sound in an obscure Romanian encounter. A local noise, body, or setting becomes the explanation of the later music. This regularity is compatible with repeated prompt expansion, but also with a deliberate literary constraint.

**Spelling changes sharply at the Kraftwerk episode.** The first three episodes contain 57 tokens with internal *î* and three with *â*. Kraftwerk contains no internal-*î* tokens and 14 with *â*. Comparable forms include *cînd* versus *când*, and *fîș* versus *fâș*. This suggests inconsistent normalization or separately handled material. Copying, publication editing, and human revision could produce the same seam. Some *â* forms in the earlier episodes occur in a proper name or a quoted song title.

**Explanatory endings make the sonic connections explicit.** *În realitate* occurs twice. The Billie Eilish episode also uses *De asta* and *Era exact*. The narration often states the connection after dramatizing it. This may resemble model-generated explanatory closure, although it also carries the sequence's joke.

**Concrete details create a consistent regional texture.** Places, industrial brands, clothes, food, and bodily sensations recur throughout. Examples include *Singer și Ileana* and *țigări Assos*. Such detail can come from an author's knowledge or from a detailed prompt; specificity does not independently establish human authorship.

**Sentence rhythm varies.** The text contains 70 heuristically segmented sentences, averaging 24.1 word tokens, with a range of 2–68 and a coefficient of variation of 0.549. Six sentences have at most five words. No three-word sentence opening repeats exactly. The measurements do not support a strong claim of monotonous sentence rhythm.

The spelling seam and the fully AI-labeled Kraftwerk section coincide. That does not show which features drove Pangram's prediction. In the first three episodes, 56.3% of word units also fall within AI-labeled spans of this same scan.

## Linguistic measurement

| Measure | Value |
|---|---:|
| Whitespace words | 1,693 |
| Established regex word tokens | 1,690 |
| Unicode word runs matching the website count | 1,753 |
| Paragraphs | 24 |
| Sentences | 70 |
| Mean sentence length | 24.14 word tokens |
| Median sentence length | 24 word tokens |
| Sentence length standard deviation | 13.25 word tokens |
| Sentence length coefficient of variation | 0.549 |
| Lowercase surface word types | 866 |
| Type-token ratio | 0.512 |
| Bidirectional MTLD | 167.9 |

The tokenizer, MTLD, percentiles, and variation calculations come from the established prose-metrics implementation bundled here. The sentence boundary rule was extended to recognize Romanian uppercase initials. The original ASCII-only rule missed eight boundaries and counted 62 sentences.

English readability indices and English stance dictionaries were excluded. No Romanian part-of-speech or dependency parser was run. Without matched comparison texts, lexical diversity values are descriptive measurements rather than AI thresholds.

## Writing rubric

The 20-item rubric remains in its original order. Thirteen transferable judgments were completed before viewing Pangram's result; seven academic-only criteria are marked not applicable. All evidence quotations passed exact-text validation.

The descriptive scores were rhythm uniformity **1/4**, content specificity **4/4**, conceptual density **3/4**, qualification density **1/4**, narrator prominence **0/4**, and explicit discourse connections **3/4**. The narrator item concerns overt narrator actions, not the strength of an omniscient storytelling voice. No overall quality or authorship score was calculated.

This was one detector-score-blind model assessment, aware of the co-credit. The rubric was developed for academic abstracts and is not a validated literary authorship scale. [Inspect all ratings and evidence](rubric_validation.json).

## Interpretation

The disclosed collaboration is plausible and receives a positive detector signal. The repeated episode structure and spelling discontinuity are concrete composition patterns worth investigating. Neither proves that Gemini generated the whole piece. Human-labeled spans are not authenticated human writing, and AI-labeled spans are not generation records.

Drafts or model-generation records would offer stronger evidence about this particular text. A separate stylometric attribution study would require authenticated Sociu prose and matched Romanian fiction from candidate models, controlling for genre, topic, length, and spelling. This single-text case does not support an authorship probability, likelihood ratio, or author-distance estimate.

Pangram's [4.1 model card](https://www.pangram.com/research/model-card/pangram-4-1) lists Romanian and recommends prose samples of at least 50 words. The aggregate accuracy claims in that model card are not transferred to this literary case. Some displayed segments are much shorter than 50 words, including a three-word AI-labeled span with low confidence.

## Evidence and reproducibility

- [Exact submitted Romanian body](sociu_body_ro.txt)
- [Extraction record and source checksum](extraction_manifest.json)
- [All linguistic measurements](stylometry.json)
- [Pangram result metadata](pangram_web/result_summary.json)
- [All 24 mapped segment observations](pangram_web/segments_mapped.json)
- [Episode calculations](pangram_web/episode_breakdown.json)
- [Frozen measurement protocol](protocol.json) and [web-interface addendum](web_protocol_addendum.json)
- [Rubric and exact-quote validation](rubric_validation.json)
- [Validation results](verification.json)

The extraction restored column order and printed paragraphs, joined five words split at line endings, and removed running furniture and the terminal printer ornament. Original spelling and punctuation were preserved. All 24 captured segment texts match the frozen body after whitespace normalization, with complete coverage.

The successful detector readout came from the requested web interface. An API attempt returned HTTP 402 and was not repeated; raw API fractions are unavailable. The bundle contains no API credential and does not perform new detector calls.

Reproduce the local measurements and report from this directory:

```sh
python3 analyze_stylometry.py
python3 build_report.py
```

These commands use the Python standard library and the bundled measurement implementation. They recompute descriptive measurements and reconstruct the report from the saved detector observations. They do not rerun Pangram or provide a new independent style assessment.

The story is attributed to its published co-credit. The full magazine PDF is not included.
