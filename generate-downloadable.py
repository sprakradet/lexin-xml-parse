#!/usr/bin/python3

import json
import xml.etree.ElementTree
from xml.etree.ElementTree import Element, SubElement, ElementTree
import sys
from pathlib import Path
import os
import re
from xmlprocess import xp, children_by_tag
from lsl4parse import readxml_lsl4
from lsl3parse import readxml_lsl3
from glob import glob
from xmlprocess import XMLProcess
from urllib.parse import urlparse, parse_qs, urlencode, quote
import collections

p = Path(sys.argv[1])

lsl3languages = ["fin","tir","gre","amh","tur","som","alb","bos","hrv","per","pus","rus","sdh","spa", "azj", "srp", "srp_cyrillic", "kmr", "ukr"]
lsl4languages = ["swe", "ara"]

all_languages = lsl3languages + lsl4languages

lang_to_lsl = {lang:"LSL4" if lang in lsl4languages else "LSL3" for lang in all_languages}

bildtema_languages = {
    "gre": "ell",
    "alb": "sqi",
    "hrv": None,
    "per": "fas",
    "pus": None,
    "ukr": None,
    "srp": None,
    "srp_cyrillic": None,
    "azj": None,
}

xmlentries = {}

def rename_bildtema_links(tree, lang):
    if isinstance(tree, list):
        for e in tree:
            rename_bildtema_links(e, lang)
    elif isinstance(tree, dict):
        if "Value" in tree:
            v = tree["Value"]
            if isinstance(v, (str)) and v.startswith("https://bildetema.oslomet.no/"):
                url = urlparse(v)
                query = parse_qs(url.query)
                query["languages"] = ",".join(["swe", lang])
                url = url._replace(query=urlencode(query, safe=",", quote_via=quote, doseq=True))
                url = url._replace(netloc="bildtema.isof.se")
                v = url.geturl()
                tree["Value"] = v
        
        for k, v in tree.items():
            rename_bildtema_links(v, lang)


xmlprocess = XMLProcess()
for langname in lsl3languages:
    if langname == "srp":
        filename = glob(str(p / "*/swe_srp_latin.xml"))[0]
    else:
        filename = glob(str(p / ("*/swe_%s.xml" % (langname,))))[0]
    print("Reading swe_%s dictionary at %s" % (langname,filename), file=sys.stderr)
    xmlentries[langname] = {entry["VariantID"]: entry for entry in readxml_lsl3(filename, xmlprocess)}
    for entry in xmlentries[langname].values():
        bildtema_lang = bildtema_languages.get(langname, langname)
        if bildtema_lang is not None:
            rename_bildtema_links(entry, bildtema_languages.get(langname, langname))
xmlprocess.cleanup(open("/tmp/lsl3-combined-signature.txt", "wt"))

lsl4filenames = {
    "swe": "svenska/swe_swe.xml",
    "ara": "arabiska/swe_ara2.xml",
}

for langname in lsl4languages:
    print("Reading swe_%s dictionary" % (langname,), file=sys.stderr)
    xmlentries[langname] = {entry["ID"]: entry for entry in readxml_lsl4(p / lsl4filenames[langname])}
    for entry in xmlentries[langname].values():
        bildtema_lang = bildtema_languages.get(langname, langname)
        if bildtema_lang is not None:
            rename_bildtema_links(entry, bildtema_languages.get(langname, langname))

resultlist = []

os.makedirs("output", exist_ok=True)

for lang in xmlentries:
    if lang in lsl4languages:
        lslversion = "LSL4"
    else:
        lslversion = "LSL3"
    with open("output/lexin-entries-%s.json" % (lang,), "wt") as entries_file:
        json.dump({"entries": xmlentries[lang], "WordBase": lslversion}, entries_file, ensure_ascii=False, separators=(',', ':'))
