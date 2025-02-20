import xml.etree.ElementTree
from xml.etree.ElementTree import Element, SubElement, ElementTree
import sys
from pathlib import Path
import os
import re
import inspect
import collections

detailed_errors = "XML_PROCESS_DETAILED_ERRORS" in os.environ

namespace_re = re.compile(r'{([^}]*)}(.*)')


def transform_attribute_name(name, namespaces):
    namespace_match = namespace_re.match(name)
    if namespace_match:
        namespace_full, localkey = namespace_match.groups()
        short = namespaces.get(namespace_full)
        if short:
            return short + localkey
    return name

def parse_child_description(value):
    if value == None:
        return (None, [])
    if (isinstance(value, tuple)):
        return (value[0], [s.strip() for s in value[1].split(",")])
    return (value, [])

def tags(children):
    return [tag for tag, child in children]

def children_by_tag(children, wanted_tag):
    return [child for tag, child in children if wanted_tag == tag]

def register_possible_child_set(xp_instance, func, children):
    children_counter = collections.Counter(children)
    first_time = False
    if func not in xp_instance.possible_children:
        xp_instance.possible_children[func] = {}
        first_time = True
#    print(func.__name__, children_counter, file=sys.stderr)
    for childname, count in children_counter.items():
#        print(childname, count, file=sys.stderr)
        if childname not in xp_instance.possible_children[func]:
            xp_instance.possible_children[func][childname] = {"required":first_time, "single": count == 1}
        else:
            if count > 1:
                xp_instance.possible_children[func][childname]["single"] = False
    for childname in set(xp_instance.possible_children[func].keys()) - set(children_counter.keys()):
        xp_instance.possible_children[func][childname]["required"] = False
#    print(possible_children[func], file=sys.stderr)

def register_possible_attribute_set(xp_instance, func, attributes):
    attributes = set(attributes)
    first_time = False
    if func not in xp_instance.possible_attributes:
        xp_instance.possible_attributes[func] = set()
        xp_instance.possible_attributes_required[func] = set(attributes)
#    print(func.__name__, attributes, file=sys.stderr)
    for attributesname in attributes:
#        print(attributesname, file=sys.stderr)
        xp_instance.possible_attributes[func] |= attributes
        xp_instance.possible_attributes_required[func] &= attributes
#    print(func.__name__, possible_attributes[func], file=sys.stderr)

class XMLProcess:
    def __init__(self):
        self.global_errors = set()
        self.possible_children = {}
        self.possible_attributes = {}
        self.possible_attributes_required = {}
        self.possible_text = set()
        self.func_tagname = {}
    def cleanup(self, signature_output=None):
        XMLProcess_cleanup(self, signature_output)

def xp(**settings):
    child_descriptions = {k:parse_child_description(v) for k, v in settings.get("children", {}).items()}
    namespace_transform = settings.get("namespaces", {})
    text_arg = settings.get("text")
    ignore = settings.get("ignore", False)
    def decorator(func):
        parameters = dict(inspect.signature(func).parameters.items())
        def wrapper(xp_instance, e, **kwargs):
            #xml.etree.ElementTree.dump(e)
            if detailed_errors and e.text:
                xp_instance.possible_text.add(func)
            if detailed_errors:
                register_possible_child_set(xp_instance, func, [child.tag for child in e])
            if detailed_errors:
                register_possible_attribute_set(xp_instance, func, e.attrib.keys())
            xp_instance.func_tagname[func] = e.tag
            if ignore:
                return None
            if e.tail and e.tail.strip():
                xp_instance.global_errors.add((func, e.tag, "unhandled_tail", ()))
            if e.text and e.text.strip() and not text_arg:
                xp_instance.global_errors.add((func, e.tag, "unhandled_text", ()))
#                xml.etree.ElementTree.dump(e)
            children = []
            for child in e:
                child_parse_function, child_parameters = child_descriptions.get(child.tag, (None, []))
                if child_parse_function == None:
                    xp_instance.global_errors.add((func, e.tag, "unhandled_child", (child.tag,)))
#                    xml.etree.ElementTree.dump(e)
                else:
                    children.append((child.tag, child_parse_function(xp_instance, child)))
            for tag, child_description in child_descriptions.items():
                _, child_parameters = child_description
                if "required" in child_parameters:
                    if len(children_by_tag(children, tag)) == 0:
#                        xml.etree.ElementTree.dump(e)
                        xp_instance.global_errors.add((func, e.tag, "required_child_missing", (tag,)))
                if "single" in child_parameters:
                    if len(children_by_tag(children, tag)) > 1:
#                        xml.etree.ElementTree.dump(e)
                        xp_instance.global_errors.add((func, e.tag, "too_many_children", (tag,)))
            if child_descriptions:
                kwargs["children"] = children
            if text_arg:
                kwargs[text_arg] = e.text and e.text.strip()
            if namespace_transform:
                kwargs.update({transform_attribute_name(k, namespace_transform): v for k, v in e.attrib.items()})
            else:
                kwargs.update(e.attrib.items())
            for k in kwargs.keys():
                if k not in parameters:
                    xp_instance.global_errors.add((func, e.tag, "unhandled_attribute", (k,)))
            for k in parameters.keys():
                if k not in kwargs and parameters[k].default == inspect.Parameter.empty:
                    xp_instance.global_errors.add((func, e.tag, "required_attribute_missing", (k,)))
            if xp_instance.global_errors:
                return []
            return func(**kwargs)
        return wrapper
    return decorator

parameter_sortorder = {
    "text": 0,
    "children": 1,
}

def generate_parameterlist(l, l_required):
    result = []
    for k in l:
        if k in l_required:
            result.append((0, parameter_sortorder.get(k, 1000), k))
        else:
            result.append((1, 0, k + "=None"))
    result.sort()
    return [v for required, sortorder, v in result]

def print_signature(xp_instance, func, signature_output):
    signature = []
    if func in xp_instance.possible_text:
        signature.append('text="text"')
    has_children = False
    if func in xp_instance.possible_children:
        children = xp_instance.possible_children[func]
        l = []
        for childname, required_single in children.items():
            parameters = []
            if required_single["required"]:
                parameters.append("required")
            if required_single["single"]:
                parameters.append("single")
            l.append('    "%s": (process_%s%s, "%s"),\n' % (childname,xp_instance.func_tagname[func],childname,", ".join(parameters)))
        if l:
            signature.append("children={\n" + "".join(sorted(l)) + "}")
            has_children = True
    if signature_output:
        print("@xp(" + ",".join(signature) + ")", file=signature_output)
        parameterlist = xp_instance.possible_attributes[func]
        parameterlist_required = xp_instance.possible_attributes_required[func]
        if has_children:
            parameterlist.add("children")
            parameterlist_required.add("children")
        if func in xp_instance.possible_text:
            parameterlist.add("text")
            parameterlist_required.add("text")
        print("def", "%s(%s):" % (func.__name__,", ".join(generate_parameterlist(parameterlist, parameterlist_required))), file=signature_output)
        print("    pass", file=signature_output)
        print(file=signature_output)


def XMLProcess_cleanup(xp_instance, signature_output=None):
    if xp_instance.global_errors:
        error_by_tagname = {}
        for (func,tagname,errortype,args) in xp_instance.global_errors:
            error_by_tagname.setdefault((func,tagname), []).append((errortype,args))
        for (func,tagname),errors in sorted(error_by_tagname.items(), key=lambda x: x[0][1]):
            print("=============", tagname, func.__name__, "=============", file=sys.stderr)
            if detailed_errors:
                print_signature(xp_instance, func, sys.stderr)
            error_by_type = {}
            for errortype, args in errors:
                error_by_type.setdefault(errortype, []).append(args)
            argslist_error = False
            for errortype, argslist in sorted(error_by_type.items()):
                for args in argslist:
                    if errortype == "unhandled_child":
                        (child_tag,) = args
#                        print(func.__name__,possible_children[func], file=sys.stderr)
                        if detailed_errors:
                            required_single  = xp_instance.possible_children[func][child_tag]
                        parameters = []
                        if detailed_errors:
                            if required_single["required"]:
                                parameters.append("required")
                            if required_single["single"]:
                                parameters.append("single")
                        msg = "%s har okänt underelement: %s\n" % (tagname,child_tag)
                        msg += '"%s": (process_%s%s, "%s")\n' % (child_tag,tagname,child_tag,", ".join(parameters))
                        msg += "@xp(ignore=True)\n"
                        msg += "def process_%s%s(children):\n" % (tagname,child_tag)
                        msg += "    pass"
                        print(msg, file=sys.stderr)
                    elif errortype == "unhandled_text":
                        print("Ohanterad text i element %s" % (tagname,), file=sys.stderr)
                    elif errortype == "unhandled_tail":
                        print("Ohanterad text efter %s" % (tagname,), file=sys.stderr)
                    elif errortype == "required_child_missing":
                        (child_tag,) = args
                        print("%s har inte något underelement av typen: %s" % (tagname,child_tag), file=sys.stderr)
                    elif errortype == "too_many_children":
                        (child_tag,) = args
                        print("%s har flera underelement av typen: %s" % (tagname,child_tag), file=sys.stderr)
                    elif errortype == "unhandled_attribute":
                        (attr_name,) = args
                        print("%s hanterar inte attributet %s" % (tagname,attr_name), file=sys.stderr)
                        argslist_error = True
                    elif errortype == "required_attribute_missing":
                        (attr_name,) = args
                        print("%s kräver attributet %s som inte finns" % (tagname,attr_name), file=sys.stderr)
                        argslist_error = True
                    else:
                        print("Okänt fel:", errortype, file=sys.stderr)
            if argslist_error and detailed_errors:
                print("def", "%s(%s):" % (func.__name__,", ".join(generate_parameterlist(xp_instance.possible_attributes[func], xp_instance.possible_attributes_required[func]))), file=sys.stderr)
    for func in sorted(xp_instance.possible_children.keys() | xp_instance.possible_attributes, key=lambda x: x.__name__):
        print_signature(xp_instance, func, signature_output)
    if xp_instance.global_errors:
        sys.exit(1)
