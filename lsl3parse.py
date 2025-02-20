import xml.etree.ElementTree
from xml.etree.ElementTree import Element, SubElement, ElementTree
from xmlprocess import xp, children_by_tag
import constants

@xp(text="text")
def process_BaseLangComment(text, MatchingID=None):
    return text

@xp(text="text")
def process_BaseLangExample(text, ID, MatchingID=None):
    return {"Content": text, "ID": ID}

@xp()
def process_BaseLangIndex(Value, type=None):
    return {"Value": Value, "type":type}

@xp(text="text")
def process_BaseLangMeaning(text, MatchingID=None):
    return text

def rewrite_phonetic(text):
    vowels = "eaiu\u00e5o\u00f6"
    text = text.replace("@", "ŋ")
    text = text.replace("+", "‿")
    text = text.replace("c", "ç")
    text = text.replace("$", "ʃ")
    stress = None
    s = ""
    nvowels = 0
    for i, c in enumerate(text):
        if c in vowels:
            nvowels += 1
        if c.isupper():
            stress = True
            s = s + c.lower() + "\u0323"
        else:
            s = s + c
    if stress and vowels == 1:
        s = "'" + s
    return s

@xp(text="text")
def process_BaseLangPhonetic(text, File=None):
    text = rewrite_phonetic(text)
    result = {"Content": text}
    if File:
        File = File.replace("\u00e4", "0344").replace("\u00f6", "0366").replace("\u00e5", "0345")
        result["File"] = "http://lexin.nada.kth.se/sound/" + File
    return result

@xp(text="text")
def process_BaseLangIdiom(text, ID, MatchingID=None):
    return {"Content": text, "ID": ID}

@xp()
def process_BaseLangAntonym(Value):
    return Value

@xp(text="text")
def process_BaseLangExplanation(text, MatchingID=None):
    return text


@xp(text="text")
def process_InflectionVariant(text, Description=None):
    result = {"Content": text}
    if Description:
        result["Description"] = Description
    return result

@xp(text="text", children={
"Variant": (process_InflectionVariant, "")
    })
def process_BaseLangInflection(text, children):
    result = {"Content": text}
    variant = children_by_tag(children, "Variant")
    if variant:
        result["Variant"] = variant
    return result


@xp(text="text")
def process_CompoundInflection(text):
    return text

@xp(text="text", children={
"Inflection": (process_CompoundInflection, "single"),
    })
def process_BaseLangCompound(children, text, ID, MatchingID=None, Description=None):
    result = {"Content": text, "ID": ID}
    inflection = children_by_tag(children, "Inflection")
    if inflection:
        result["Inflection"] = inflection
    return result

@xp()
def process_BaseLangIllustration(TYPE, VALUE, Norlexin):
    Value = "https://bildetema.oslomet.no/bildetema/bildetema-html5/bildetema.html?version=swedish&languages=swe&" + Norlexin
    return {"Type":TYPE, "Value": Value}


@xp(text="text")
def process_DerivationInflection(text):
    return text

@xp(text="text", children={
    "Inflection": (process_DerivationInflection, "single")
    })
def process_BaseLangDerivation(text, children, ID, Description=None):
    result = {"Content": text, "ID": ID}
    inflection = children_by_tag(children, "Inflection")
    if inflection:
        result["Inflection"] = inflection
    return result

@xp(text="text")
def process_BaseLangGraminfo(text):
    return text

@xp()
def process_BaseLangReference(TYPE, VALUE):
    if TYPE == "animation":
        VALUE = "http://lexin.nada.kth.se/lang/lexinanim/" + VALUE.replace(".swf", ".mp4")
    if TYPE == "phonetic":
        VALUE = "http://lexin.nada.kth.se/sound/" + VALUE.replace(".swf", ".mp3")
    return {"Type": TYPE, "Value": VALUE}

@xp(text="text")
def process_BaseLangAlternate(text):
    return text

@xp(text="text")
def process_BaseLangUsage(text, MatchingID=None):
    return text


@xp(children={
    "Comment": (process_BaseLangComment, "single"),
    "Example": (process_BaseLangExample, ""),
    "Index": (process_BaseLangIndex, ""),
    "Meaning": (process_BaseLangMeaning, "single, required"),
    "Phonetic": (process_BaseLangPhonetic, "single"),
    "Idiom": (process_BaseLangIdiom, ""),
    "Antonym": (process_BaseLangAntonym, ""),
    "Explanation": (process_BaseLangExplanation, "single"),
    "Inflection": (process_BaseLangInflection, ""),
    "Compound": (process_BaseLangCompound, ""),
    "Illustration": (process_BaseLangIllustration, ""),
    "Derivation": (process_BaseLangDerivation, ""),
    "Graminfo": (process_BaseLangGraminfo, "single"),
    "Reference": (process_BaseLangReference, ""),
    "Alternate": (process_BaseLangAlternate, "single"),
    "Usage": (process_BaseLangUsage, "single"),
    })
def process_WordBaseLang(children):
    result = {}
    for k, v in children:
        if k in ["Comment", "Meaning", "Phonetic", "Graminfo", "Alternate", "Explanation", "Usage"]:
            if v:
                result[k] = v
        else:
            result.setdefault(k, []).append(v)
    return result


@xp(text="text")
def process_TargetLangComment(text):
    return text

@xp(text="text")
def process_TargetLangExample(text, ID):
    return {"Content": text or "", "ID": ID}

@xp(text="text")
def process_TargetLangTranslation(text):
    if text is None:
        text = ""
    return text

@xp(text="text")
def process_TargetLangIdiom(text, ID):
    return {"Content": text, "ID": ID}

@xp(text="text")
def process_TargetLangExplanation(text):
    return text

@xp(text="text")
def process_TargetLangCompound(text, ID, Description=None):
    return {"Content": text or "", "ID": ID}

@xp(text="text")
def process_TargetLangDerivation(text, ID, Description=None):
    result = {"Content": text, "ID": ID}
    return result

@xp(text="text")
def process_TargetLangSynonym(text):
    return text

@xp()
def process_TargetLangAntonym(Value):
    return Value


@xp(children={
    "Comment": (process_TargetLangComment, "single, "),
    "Example": (process_TargetLangExample, ""),
    "Translation": (process_TargetLangTranslation, "single"),
    "Idiom": (process_TargetLangIdiom, ""),
    "Explanation": (process_TargetLangExplanation, "single"),
    "Compound": (process_TargetLangCompound, ""),
    "Derivation": (process_TargetLangDerivation, ""),
    "Synonym": (process_TargetLangSynonym, "single"),
    "Antonym": (process_TargetLangAntonym, ""),
    })
def process_WordTargetLang(children, Comment=None, Type=None, Value=None):
    result = {}
    for k, v in children:
        if k in ["Comment", "Translation", "Explanation"]:
            result[k] = v
        elif k in ["Synonym"]:
            if v and v[0]:
                result.setdefault(k, []).append(v)
        else:
            result.setdefault(k, []).append(v)
    return result


def translation_index(nodevalue):
    nodevalue = nodevalue.split("(")[0]
    for translation in nodevalue.split(","):
        yield ("targetlang", translation.strip())


@xp(children={
    "BaseLang": (process_WordBaseLang, "single"),
    "TargetLang": (process_WordTargetLang, "single"),
})
def process_entry(children, ID, Type, Value, Variant, VariantID, MatchingID=None):
    result = {}
    baselang = children_by_tag(children, "BaseLang")
    result["indices"] = []
    if baselang:
        if "Index" in baselang[0]:
            for index in baselang[0].pop("Index"):
                result["indices"].append(("baselang", index["Value"]))
        result["BaseLang"] = baselang[0]

    targetlang = children_by_tag(children, "TargetLang")
    if targetlang:
        result["TargetLang"] = targetlang[0]
        if "Translation" in targetlang[0] and targetlang[0]["Translation"]:
            result["indices"].extend(translation_index(targetlang[0]["Translation"]))
        if "Synonym" in targetlang[0] and targetlang[0]["Synonym"]:
            for synonym in targetlang[0]["Synonym"][0].split(","):
                result["indices"].append(("targetlang-synonym", synonym.strip()))
    result["ID"] = ID
    result["Type"] = Type
    result["Value"] = Value
    if Variant:
        result["Variant"] = Variant
    result["VariantID"] = VariantID
    return result

"""
<Dictionary BaseLang="Swedish" TargetLang="Finnish" Version="2010-07-07" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://lexin.nada.kth.se/schema/LexinSchema.xsd">
  <Word ID="1" MatchingID="3" Type="prep." Value="à" Variant="1" VariantID="1">
    <BaseLang>
"""

import os.path

def readxml_lsl3(filename, xmlprocess):
    entries = []
    with open(filename) as f:
        events = xml.etree.ElementTree.iterparse(f)
        for (event, element) in events:
            if element.tag == "Word":
                parsednode = process_entry(xmlprocess, element)
                if parsednode == []:
                    continue
                entries.append(parsednode)
                element.clear()
    return entries
