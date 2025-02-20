import xml.etree.ElementTree
from xml.etree.ElementTree import Element, SubElement, ElementTree
from xmlprocess import xp, children_by_tag, XMLProcess
import constants

@xp(text="text")
def process_PhoneticAlternate(text, Spec=None, File=""):
    if File:
        File = File.replace("\u00e4", "0344").replace("\u00f6", "0366").replace("\u00e5", "0345")
        File = "http://lexin.nada.kth.se/sound/" + File
    result = {"Content":text, "File":File}
    if Spec is not None:
        result["Spec"] = Spec
    return result

@xp(children={"Alternate": (process_PhoneticAlternate, "")}, text="text")
def process_Phonetic(children, text, File=None):
    if File is None:
        File = ""
    else:
        File = File.replace("\u00e4", "0344").replace("\u00f6", "0366").replace("\u00e5", "0345")
        File = "http://lexin.nada.kth.se/sound/" + File
    return [{"Content":text, "File":File}] + children_by_tag(children, "Alternate")


@xp(text="text")
def process_InflectionAlternate(text, Spec=None):
    result = {"Content":text}
    if Spec is not None:
        result["Spec"] = Spec
    return result


@xp(ignore=True)
def process_InflectionPhonetic(children):
    pass

@xp(text="text", children={
    "Alternate": (process_InflectionAlternate, ""),
    "Phonetic": (process_InflectionPhonetic, "single"),
    })
def process_Inflection(children, text, Spec=None, Form=None):
    result = {"Content": text}
    passon_if_present(result, children, "Alternate")
    if Form:
        result["Form"] = Form
    if Spec:
        result["Spec"] = Spec
    return result

@xp()
def process_LemmaIndex(Value, Type=None):
    return {"Value": Value, "Type": Type}


@xp(text="text")
def process_Definition(text, ID, DoubleID=None, TransTool=None):
    return {"Content": text, "ID": ID}

@xp(text="text")
def process_IdiomDefinition(text, ID, DoubleID=None):
    return {"Content": text, "ID": ID}

@xp(text="text")
def process_IdiomComment(text, ID, Type, DoubleID=None):
    return {"Content": text, "ID": ID}


@xp(text="text", children={
    "Definition": (process_IdiomDefinition, "single"),
    "Comment": (process_IdiomComment, "single"),
    })
def process_Idiom(children, text, ID, OldID=None, DoubleID=None):
    result = {"Content": text, "ID": ID}
    if OldID:
        result["OldID"] = OldID
    definition = children_by_tag(children, "Definition")
    if definition:
        result["Definition"] = definition[0]
    comment = children_by_tag(children, "Comment")
    if comment:
        result["Comment"] = comment[0]
    return result

@xp(text="text")
def process_Compound(text, ID, OldID, DoubleID=None, ArticleID=None):
    result = {"Content": text, "ID":ID}
    if OldID:
        result["OldID"] = OldID
    return result

@xp()
def process_LexemeIndex(Value, Type=None):
    return {"Value": Value, "Type":Type}

@xp(text="text")
def process_Example(text, ID, OldID, DoubleID=None):
    result = {"Content": text, "ID": ID}
    if OldID:
        result["OldID"] = OldID
    return result


@xp()
def process_Illustration(Type, Value, Norlexin=None):
    Value = "https://bildetema.oslomet.no/bildetema/bildetema-html5/bildetema.html?version=swedish&languages=swe&" + Norlexin
    return {"Type":Type, "Value":Value}

@xp()
def process_Theme(Tema):
    return Tema

@xp(text="text")
def process_Graminfo(text, ID, Order):
    return {"Content":text, "ID":ID, "Order":Order}

@xp()
def process_LexemeReference(Type, Value, Lemmano=None, Lexemeno=None, Spec=None):
    if Type == "animation":
        Value = "http://lexin.nada.kth.se/lang/lexinanim/" + Value.replace(".swf", ".mp4")
    result = {"Type": Type, "Value": Value}
    if Lexemeno:
        result["Lexemeno"] = Lexemeno
    if Lemmano:
        result["Lemmano"] = Lemmano
    return result

@xp(text="text")
def process_CycleComment(text, ID, Type, DoubleID=None):
    return {"Content": text, "ID": ID, "Type": Type}

@xp(text="text")
def process_CycleDefinition(text, ID, DoubleID=None):
    return {"Content": text, "ID": ID}

@xp(text="text")
def process_CycleExample(text, ID, OldID, DoubleID=None):
    return {"Content": text, "ID": ID}

@xp(text="text")
def process_CycleGraminfo(text, ID, Order):
    return {"Content": text, "ID": ID, "Order": Order}

@xp(text="text")
def process_CycleCompound(text, ID, OldID, ArticleID=None, DoubleID=None):
    return {"Content": text, "ID": ID}

@xp()
def process_CycleTheme(Tema):
    return Tema

@xp()
def process_CycleReference(Lemmano, Type, Value, Lexemeno=None):
    return {"Lemmano": Lemmano, "Type": Type, "Value": Value}

@xp(text="text")
def process_CycleAbbreviate(text, ID, Spec):
    return {"Content": text, "ID": ID}


@xp(children={
    "Comment": (process_CycleComment, ""),
    "Definition": (process_CycleDefinition, "single"),
    "Example": (process_CycleExample, ""),
    "Graminfo": (process_CycleGraminfo, ""),
    "Compound": (process_CycleCompound, ""),
    "Theme": (process_CycleTheme, "single"),
    "Reference": (process_CycleReference, "single"),
    "Abbreviate": (process_CycleAbbreviate, "single"),
    })
def process_Cycle(children, CycleID, Cycleno):
    result = {}
    for k, v in children:
        if k in ["Abbreviate", "Comment", "Definition", "Theme"]: # XXX Comment is not single, but is treated that way in JSON
            result[k] = v
        else:
            if k == "Idiom":
                k = "Idioms"
            result.setdefault(k, []).append(v)
    result["CycleID"] = CycleID
    return result
    

@xp(text="text")
def process_Comment(text, ID, Type, DoubleID=None):
    return {"Content": text, "ID": ID, "Type": Type}

@xp(text="text")
def process_Explanation(text, ID):
    return {"Content": text, "ID": ID}

@xp(text="text")
def process_Gramcom(text, ID, Type, DoubleID=None):
    return {"Content": text, "ID": ID}

@xp(text="text")
def process_LexemeAbbreviate(text, ID, Spec):
    return {"Content": text, "ID": ID}

@xp(ignore=True)
def process_TargetLangAbbreviate(children):
    pass



@xp(text="text")
def process_TLCycleExample(text, ID, DoubleID=None):
    return {"Content": text, "ID": ID}
@xp(text="text")
def process_TLCycleCompound(text, ID, DoubleID=None):
    return {"Content": text, "ID": ID}
@xp(text="text")
def process_TLCycleTranslation(text, ID):
    return {"Content": text, "ID": ID}
@xp(ignore=True)
def process_TLCycleAbbreviate(children):
    return {}

@xp(children={
    "Example": (process_TLCycleExample, ""),
    "Compound": (process_TLCycleCompound, ""),
    "Translation": (process_TLCycleTranslation, ""),
    "Abbreviate": (process_TLCycleAbbreviate, ""),
})
def process_TargetLangCycle(children, CycleID):
    result = {"CycleID": CycleID}
    passon_if_present(result, children, "Example")
    passon_if_present(result, children, "Translation")
    passon_if_present(result, children, "Compound")
    return result

@xp(text="text")
def process_IdiomTranslation(text, ID, DoubleID=None):
    return {"Content": text, "ID": ID}

@xp(children={
    "Translation": (process_IdiomTranslation, "")
})
def process_TargetLangIdiom(children, ID):
    result = {"ID": ID}
    passon_if_present(result, children, "Translation")
    return result

@xp(text="text")
def process_TargetLangTranslation(text, ID):
    return {"Content": text, "ID": ID}

@xp(text="text")
def process_TargetLangCompound(text, ID, DoubleID=None):
    return {"Content": text, "ID": ID}
@xp(ignore=True)
def process_TargetLangDefinition(children):
    return {}
@xp(text="text")
def process_TargetLangExample(text, ID, DoubleID=None):
    return {"Content": text, "ID": ID}
@xp(ignore=True)
def process_TargetLangExplanation(children):
    return {}

def passon_if_present(result, children, tag, new_tag=None):
    if new_tag is None:
        new_tag = tag
    children_result = children_by_tag(children, tag)
    if children_result:
        result[new_tag] = children_result

@xp(children={
    "Abbreviate": (process_TargetLangAbbreviate, "single"),
    "Cycle": (process_TargetLangCycle, ""),
    "Idiom": (process_TargetLangIdiom, ""),
    "Translation": (process_TargetLangTranslation, "required"),
    "Compound": (process_TargetLangCompound, ""),
    "Definition": (process_TargetLangDefinition, "single"),
    "Example": (process_TargetLangExample, ""),
    "Explanation": (process_TargetLangExplanation, "single"),
})
def process_LexemeTargetLang(children):
    result = {"Translation": children_by_tag(children, "Translation")}
    passon_if_present(result, children, "Cycle")
    passon_if_present(result, children, "Example")
    passon_if_present(result, children, "Idiom", "Idioms")
    passon_if_present(result, children, "Compound")
    return result

@xp(children={
    "Definition": (process_Definition, "single"),
    "Idiom": (process_Idiom, ""),
    "Compound": (process_Compound, ""),
    "Index": (process_LexemeIndex, ""),
    "Example": (process_Example, ""),
    "Illustration": (process_Illustration, ""),
    "Theme": (process_Theme, "single"),
    "Graminfo": (process_Graminfo, ""),
    "Reference": (process_LexemeReference, ""),
    "Cycle": (process_Cycle, ""),
    "Comment": (process_Comment, ""),
    "Explanation": (process_Explanation, "single"),
    "Gramcom": (process_Gramcom, "single"),
    "Abbreviate": (process_LexemeAbbreviate, "single"),
    "TargetLang": (process_LexemeTargetLang, ""),
})
def process_Lexeme(children, ID, Lexemeno, VariantID, LexemeID=None):
    result = {}
    for k, v in children:
        if k in ["Gramcom", "Definition", "Theme", "Explanation", "Comment", "TargetLang"]:
            result[k] = v
        else:
            if k == "Idiom":
                k = "Idioms"
            result.setdefault(k, []).append(v)
    result["ID"] = ID
    result["VariantID"] = VariantID
    result["Lexemeno"] = Lexemeno
    return result

@xp(ignore=True)
def process_AlternatePhoneticAlternate(children):
    pass

@xp(text="text",children={
    "Alternate": (process_AlternatePhoneticAlternate, "single"),
})
def process_AlternatePhonetic(text, children, File=None):
    result = {"Content": text}
    if File:
        result["File"] = "http://lexin.nada.kth.se/sound/" + File
    else:
        result["File"] = ""
    return result

@xp(text="text", children={
    "Phonetic": (process_AlternatePhonetic, "single"),
    })
def process_LemmaAlternate(text, children, Spec):
    result = {"Content": text, "Spec": Spec}
    passon_if_present(result, children, "Phonetic")
    return result

@xp()
def process_LemmaReference(Type, Value, Lemmano=None, Spec=None):
    result = {}
    if Type:
        result["Type"] = Type
    if Value:
        result["Value"] = Value
    if Spec:
        result["Spec"] = Spec
    if Lemmano:
        result["Lemmano"] = Lemmano
    return result

@xp(text="text")
def process_Abbreviate(text, ID, Spec, DoubleID=1):
    return {"Content": text, "ID": ID}

"""
  <Article ArticleID="1025265" Sortkey="dem">
    <Lemma ID="1025265" LemmaID="3537" Rank="99999" Type="bestämd artikel och pron." Value="dem" Variant="" VariantID="3062">
      <Phonetic File="dem.mp3">dem:<Alternate Spec="eller"> dåm:</Alternate>
      </Phonetic>
      <Reference Lemmano="2" Type="see" Value="den" />
    </Lemma>
  </Article>
"""

@xp(children={
    "Phonetic": (process_Phonetic, "single"),
    "Inflection": (process_Inflection, ""),
    "Index": (process_LemmaIndex, ""),
    "Lexeme": (process_Lexeme, ""),
    "Alternate": (process_LemmaAlternate, "single"),
    "Reference": (process_LemmaReference, "single"),
    "Abbreviate": (process_Abbreviate, "single"),
    })
def process_lemma(children, ID, LemmaID, Rank, Type, Value, Variant, VariantID, Hyphenate=None):
    result = {}
    indices = children_by_tag(children, "Index")
    result["indices"] = [("baselang", Value.replace("|", ""))]
    if "|" in Value:
        suffix = "-" + Value[Value.index("|")+1:]
        result["indices"].append(("baselang", suffix))
        prefix = Value[:Value.index("|")] + "-"
        result["indices"].append(("baselang", prefix))
    for index in indices:
        if index["Type"] is None:
            result["indices"].append(("baselang", index["Value"].strip()))
        elif index["Type"] == "suffix":
            result["indices"].append(("baselang", "-" + index["Value"]))
        elif index["Type"] == "prefix":
            result["indices"].append(("baselang", index["Value"] + "-"))
    reference = children_by_tag(children, "Reference")
    if reference:
        result["Reference"] = reference
    result["ID"] = ID
    result["VariantID"] = VariantID
    if Variant:
        result["Variant"] = Variant
    result["Value"] = Value
    result["Type"] = Type
    if Hyphenate:
        result["Hyphenate"] = Hyphenate
    
    passon_if_present(result, children, "Lexeme")
    passon_if_present(result, children, "Alternate")
    abbreviate = children_by_tag(children, "Abbreviate")
    if abbreviate:
        result["Abbreviate"] = abbreviate[0]
        result["indices"].append(("baselang", abbreviate[0]["Content"]))
    for lexeme in result.get("Lexeme", []):
        lexeme_indices = lexeme.pop("Index", [])
        for index in lexeme_indices:
            if index["Type"] is None:
                result["indices"].append(("baselang", index["Value"]))
            elif index["Type"] == "suffix":
                result["indices"].append(("baselang", "-" + index["Value"]))
            elif index["Type"] == "prefix":
                result["indices"].append(("baselang", index["Value"] + "-"))
#        elif k in ["Index"]:
#            pass
    phonetic = children_by_tag(children, "Phonetic")
    if phonetic:
        result["Phonetic"] = phonetic[0]
    passon_if_present(result, children, "Inflection")
    return result

#@xp(children={"lg": (process_lg, "single,required"), "mg": (process_mg_wrapper, "required"), "meta_info": process_meta_info})
@xp(children={"Lemma": (process_lemma, "single,required")})
def process_entry(children, ArticleID, Sortkey):
    result = []
    return children_by_tag(children, "Lemma")


def readxml_lsl4(filename):
    entries = []
    xmlprocess = XMLProcess()
    with open(filename) as f:
        events = xml.etree.ElementTree.iterparse(f)
        for (event, element) in events:
            if element.tag == "Article":
                entries.extend(process_entry(xmlprocess, element))
                element.clear()
    xmlprocess.cleanup(open("/tmp/lsl4-signature.txt", "wt"))
    return entries
