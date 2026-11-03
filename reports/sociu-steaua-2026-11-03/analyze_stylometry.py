#!/usr/bin/env python3
"""Descriptive Romanian profile, using the established measurement functions."""
from pathlib import Path
import collections, datetime, hashlib, importlib.util, json, math, re, shutil
ROOT=Path(__file__).resolve().parent
snapshot=ROOT/'established_prose_metrics.py'
if not snapshot.exists():raise FileNotFoundError('Bundled established_prose_metrics.py is required')
spec=importlib.util.spec_from_file_location('established_metrics',snapshot)
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
text=(ROOT/'sociu_body_ro.txt').read_text()
manifest=json.loads((ROOT/'extraction_manifest.json').read_text())
assert hashlib.sha256(text.encode()).hexdigest()==manifest['body_sha256']
# Extend ASCII-only initials to Romanian uppercase; retain the old conventions.
SENT=re.compile(r'''(?<=[.!?])(?:["'’”)]*)\s+(?=[A-ZĂÂÎȘŞȚŢ"'„“])''')
def words(s):return [w.lower().strip('.-') for w in base.WORD_RE.findall(s) if w.strip('.-')]
def describe(v):
 m=sum(v)/len(v)
 return dict(mean=m,median=base.percentile(v,.5),p90=base.percentile(v,.9),min=min(v),max=max(v),sd_population=math.sqrt(sum((x-m)**2 for x in v)/len(v)),cv_population=base.coefficient_of_variation(v))
def profile(s):
 tokens=words(s);counts=collections.Counter(tokens);sentences=[x.strip() for x in SENT.split(s) if x.strip()];lengths=[len(words(x)) for x in sentences];paras=[p for p in re.split(r'\n\s*\n',s) if p.strip()]
 punct={'comma':s.count(','),'semicolon':s.count(';'),'colon':s.count(':'),'parenthetical_open':s.count('('),'question_mark':s.count('?'),'exclamation_mark':s.count('!'),'dash':len(re.findall(r'[—–]|(?<=\s)-(?:\s)',s))}
 return {'whitespace_words':len(s.split()),'word_tokens':len(tokens),'types_lowercase_surface':len(counts),'sentences':len(sentences),'paragraphs':len(paras),'sentence_length_words':describe(lengths),'paragraph_length_words':describe([len(words(p)) for p in paras]),'lexical':{'type_token_ratio':len(counts)/len(tokens),'root_ttr':len(counts)/math.sqrt(len(tokens)),'mtld_bidirectional_threshold_0_72':base.mtld(tokens),'mean_word_length_including_internal_hyphens':sum(map(len,tokens))/len(tokens),'hapax_types':sum(c==1 for c in counts.values()),'hapax_types_fraction':sum(c==1 for c in counts.values())/len(counts)},'punctuation_counts':punct,'punctuation_per_1000_tokens':{k:v*1000/len(tokens) for k,v in punct.items()},'sentence_length_bins':{'1_to_5':sum(1<=n<=5 for n in lengths),'6_to_15':sum(6<=n<=15 for n in lengths),'16_to_30':sum(16<=n<=30 for n in lengths),'31_to_50':sum(31<=n<=50 for n in lengths),'over_50':sum(n>50 for n in lengths)},'repeated_three_word_sentence_openings':{k:v for k,v in collections.Counter(' '.join(words(x)[:3]) for x in sentences).items() if v>1},'surface_function_word_counts':{k:counts[k] for k in ['și','de','în','cu','la','pe','că','un','o','a','din','care','să','se','nu','iar','dar','ca','pentru','prin','era']},'internal_circumflex_tokens':{mark:{w:c for w,c in sorted(counts.items()) if mark in w[1:-1]} for mark in ['î','â']},'sentences_with_lengths':[{'i':i+1,'word_tokens':n,'text':x} for i,(x,n) in enumerate(zip(sentences,lengths))]}
starts=[0]+[text.index(m) for m in ['Se zice că Thom Yorke','Cînd Nick Cave a lansat','În ’81, când Kraftwerk']]+[len(text)]
sections=[]
for i,name in enumerate(['Billie Eilish','Thom Yorke','Nick Cave','Kraftwerk']):
 s=profile(text[starts[i]:starts[i+1]].strip());s.update(name=name,start_char=starts[i],end_char=starts[i+1]);sections.append(s)
features=profile(text);features['sections']=sections
features['source_text_sha256']=manifest['body_sha256'];features['established_measurement_script_sha256']=hashlib.sha256(snapshot.read_bytes()).hexdigest()
features['legacy_ascii_sentence_splitter_sentence_count']=len([s for s in base.SENTENCE_RE.split(text) if s.strip()])
features['excluded_measures']={'English_readability_indices':'Not computed: English syllable heuristics and grade calibrations do not apply to Romanian.','English_hedge_booster_pronoun_dictionaries':'Not computed: English dictionaries would mismeasure Romanian.','POS_and_dependency_ratios':'Not computed: no validated Romanian tagger was run.','author_distance_and_Gemini_attribution':'Not estimated: no authenticated Sociu or matched Gemini comparison corpus supplied.'}
features['method_limits']=['Single literary text; its four episodes are not independent author samples.','Established word regex retains internal hyphenated clitics as single tokens. Billing uses whitespace words.','Sentence splitting is heuristic, extended to Romanian uppercase initials.','Lexical measures use lowercase surface forms, without lemmatization or spelling modernization.','TTR depends on length; MTLD varies with vocabulary and genre. Episode comparisons are descriptive only.','Circumflex spellings may reflect publication editing or text assembly.','No measure here establishes authorship or generator identity.']
concordances={}
for phrase in ['în timp ce','în realitate','se știe că','se zice că','era exact','toată','ca o','ca pe']:
 matches=list(re.finditer(r'(?<!\w)'+re.escape(phrase)+r'(?!\w)',text,re.I))
 concordances[phrase]=[{'start_char':m.start(),'end_char':m.end(),'paragraph':text[:m.start()].count('\n\n')+1,'context':text[max(0,m.start()-55):min(len(text),m.end()+95)]} for m in matches]
features['specified_phrase_concordances']=concordances
assessment={'scores':[0,None,None,None,0,None,0,0,0,0,0,None,1,None,None,4,3,1,0,3],'evidence':[
 {'i':12,'quote':'Doar șoptea.','reason':'A two-token sentence interrupts longer explanatory narration. Sentence rhythm is not strongly uniform.'},
 {'i':12,'quote':'Și astăzi, cînd Billie Eilish umple stadioane la Londra sau Tokyo','reason':'This extended subordinate-clause opening contrasts with the short sentence in the same episode.'},
 {'i':15,'quote':'trei sute de mașini de cusut Singer și Ileana','reason':'Named machines and a quantity give concrete specificity. This fictional detail is not evidence of factual accuracy.'},
 {'i':15,'quote':'un custode pensionar i-a arătat doar niște replici din ghips și i-a cerut un pachet de țigări Assos','reason':'An actor, material, transaction and brand specify the scene.'},
 {'i':16,'quote':'Din cauza reumatismului, doamna Mioara se mișca cu o grație rigidă, aproape spectrală.','reason':'Bodily condition, movement and visual impression form a recoverable relation; clauses across the piece often add such relations or sensory details.'},
 {'i':17,'quote':'ce părea să-i iasă din călcâie','reason':'An occasional appearance qualifier occurs, but most narrative propositions are asserted directly. This rates amount, not empirical adequacy.'},
 {'i':18,'quote':'Ralf s-a întors la Düsseldorf și a programat piesa Das Model.','reason':'Third-person characters act; the narrator does not describe their own actions. This narrow score does not make the storytelling voice neutral.'},
 {'i':19,'quote':'De asta muzica ei are tristețea aia de gară de triaj','reason':'An explicit causal interpretation states the sonic analogy.'},
 {'i':19,'quote':'În realitate, Nick petrecuse trei săptămîni','reason':'The transition explicitly opposes the public story and the narrated alternative.'},
 {'i':19,'quote':'În realitate, ritmul ăla rigid, matematic și rece','reason':'The same transition names the final explanatory reversal in another episode.'}
 ],'limitations':['Rubric v0.2.0 was developed for academic abstracts, whereas this is Romanian literary fiction.','Scope overreach, certainty mismatch, result/interpretation blur, unsupported scholarly ending, inflated evidential evaluation, academic abstract-template strength, and stock academic phrasing are not assessed; their scores are null.','The remaining syntax and style judgments are transferable descriptions, not validated literary scales.','One detector-score-blind model assessment, not an independent human panel; the assessor knows the user-supplied provenance claim.','Intentional sonic repetition and parallel plots are described separately, without assuming they are defects.','Narrator prominence here concerns overt narrator/author actions, not the strength of the omniscient storytelling voice.','No overall quality, human-likeness or authorship score is formed by summing these items.']}
def save(name,value):(ROOT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
save('stylometry.json',features);save('rubric_assessment_score_blind.json',assessment)
protocol=json.loads((ROOT/'protocol.json').read_text())
assert protocol['input_sha256']==manifest['body_sha256']
assert protocol['score_blind_assessment_sha256']==hashlib.sha256((ROOT/'rubric_assessment_score_blind.json').read_bytes()).hexdigest()
brief={k:v for k,v in features.items() if k not in ['sections','sentences_with_lengths','specified_phrase_concordances','internal_circumflex_tokens']}
brief['sections']=[{k:s[k] for k in ['name','whitespace_words','word_tokens','sentences','paragraphs','sentence_length_words','lexical']}|{'internal_circumflex_counts':{m:sum(c.values()) for m,c in s['internal_circumflex_tokens'].items()}} for s in sections]
brief['phrase_counts']={k:len(v) for k,v in concordances.items()}
print(json.dumps(brief,ensure_ascii=False,indent=2))
