#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BuiltInExtFunctions.py
4XPath-specific Extension functions
WWW: http://4suite.org/XSLT        e-mail: support@4suite.org

Copyright (c) 2000-2001 Fourthought Inc, USA.   All Rights Reserved.
See  http://4suite.org/COPYRIGHT  for license and copyright information
"""
from __future__ import annotations  # isort:skip
import sys  # isort:skip
import os  # isort:skip
# stdlib

import re
import string
import sys
import urllib.error
import urllib.parse
import urllib.request
from xml.dom import EMPTY_NAMESPACE
from xml.dom import Node
from xml.dom.Text import Text
from xml.utils import boolean
from xml.xpath import Conversions
from xml.xpath import CoreFunctions
from xml.xpath import FT_EXT_NAMESPACE
from xml.xpath import FT_OLD_EXT_NAMESPACE



def Version(context):
    __version__ = "0.1.0"
    try:
        from .__version__ import __version__
    except Exception:
        pass
    return __version__


def NodeSet(context, rtf):
    """Convert a result-tree fragment to a node-set"""
    if type(rtf) == type([]):
        return rtf
    if hasattr(rtf, "nodeType") and rtf.nodeType == Node.DOCUMENT_NODE:
        node_set = list(rtf.childNodes)
    else:
        node_set = [rtf]
    return node_set


def Match(context, pattern, arg=None):
    """Do a regular expression match against the argument"""
    if not arg:
        arg = context.node
    arg = Conversions.StringValue(arg)
    bool = re.match(pattern, arg) and boolean.true or boolean.false
    return bool


def Replace(context, old, new, arg=None):
    """Do a global search and replace of the string contents"""
    if not arg:
        arg = context.node
    arg = Conversions.StringValue(arg)
    old = Conversions.StringValue(old)
    new = Conversions.StringValue(new)
    return string.replace(arg, old, new)


# FIXME: Really only makes sense for XSLT
def SearchRe(context, pattern, arg=None):
    """Do a regular expression search against the argument (i.e. get all matches)"""
    if not arg:
        arg = context.node
    arg = Conversions.StringValue(arg)
    matches = re.findall(pattern, arg)
    proc = context.processor
    matches_nodeset = []
    for groups in matches:
        proc.pushResult()
        proc.writers[-1].startElement("Match", EMPTY_NAMESPACE)
        if type(groups) != type(()):
            groups = (groups,)
        for group in groups:
            proc.writers[-1].startElement("Group", EMPTY_NAMESPACE)
            proc.writers[-1].text(group)
            proc.writers[-1].endElement("Group")
        proc.writers[-1].endElement("Match")
        frag = proc.popResult()
        context.rtfs.append(frag)
        matches_nodeset.append(frag.childNodes[0])
    return matches_nodeset


# This version incorporates a workaround for a Python 2.0 bug in re.findall
# Courtesy alexander smishlajev <alex@ank-sia.com>
# See http://lists.fourthought.com/pipermail/4suite/2001-June/002188.html
def SearchRePy20(context, pattern, arg=None):
    """Do a regular expression search against the argument (i.e. get all matches)"""
    if not arg:
        arg = context.node
    arg = Conversions.StringValue(arg)
    proc = context.processor
    matches_nodeset = []
    _re = re.compile(pattern)
    _match = _re.search(arg)
    while _match:
        proc.pushResult()
        proc.writers[-1].startElement("Match", EMPTY_NAMESPACE)
        _groups = _match.groups()
        # .groups() return empty tuple when the pattern did not do grouping
        if not _groups:
            _groups = tuple(_match.group())
        for group in _groups:
            proc.writers[-1].startElement("Group", EMPTY_NAMESPACE)
            # MatchObject groups return None if unmatched
            # unlike .findall() returning empty strings
            proc.writers[-1].text(group or "")
            proc.writers[-1].endElement("Group")
        proc.writers[-1].endElement("Match")
        frag = proc.popResult()
        context.rtfs.append(frag)
        matches_nodeset.append(frag.childNodes[0])
        _match = _re.search(arg, _match.end())
    return matches_nodeset


# FIXME: Really only makes sense for XSLT (in fact, barely makes sense at all)
def Map(context, funcname, *nodesets):
    """
	Apply the function serially over the given node sets.
	In iteration i, the function is passed N parameters
	where N is the number of argument node sets.  Each
	parameter is a node set of size 1, whose node is
	the ith node of the corresponding argument node set.
	The return value is a node set consisting of a series
	of result-tree nodes, each of which is a text node
	whose value is the string value of the result of the
	ith function invocation.
	Warning: this function uses the implied ordering of the node set
	Based on its implementation as a Python list.  But in reality
	There is no reliable ordering of XPath node sets.
	In other words, this function is voodoo.
	"""
    (prefix, local) = ExpandQName(funcname, namespaces=context.processorNss)
    func = g_extFunctions.get(expanded) or CoreFunctions.CoreFunctions.get(
        expanded, None
    )
    if not func:
        raise Exception("Dynamically invoked function %s not found." % funcname)
    flist = [f] * len(nodesets)
    lf = lambda x, f, *args: f(*args)
    retlist = list(map(*(lf, flist) + nodesets))

    proc = context.processor
    result_nodeset = []
    for ret in retlist:
        proc.pushResult()
        proc.writers[-1].text(Conversions.StringValue(ret))
        frag = proc.popResult()
        context.rtfs.append(frag)
        result_nodeset.append(frag.childNodes[0])
    return result_nodeset


def EscapeUrl(context, url):
    "Escape illegal characters in a URL"
    return urllib.parse.quote(Conversions.StringValue(url))


def BaseUri(context, arg=None):
    """Get the base URI of the argument"""
    # FIXME: Arg must be a node set
    if not arg:
        arg = [context.node]
    if hasattr(arg[0], "baseUri"):
        return arg[0].baseUri
    elif hasattr(arg[0], "refUri"):
        return arg[0].refUri
    return ""


def IsoTime(context):
    import DateTime

    d = DateTime.now()
    return DateTime.ISO.str(d)


def Evaluate(context, expr):
    import xml.xpath

    return xml.xpath.Evaluate(Conversions.StringValue(st), context=context)


def GenerateUuid(context=None):
    from uuid import uuid4

    return str(uuid4())


##
## distinct, split, range if_function and find
## were contributed by Lars Marius Garshol.
## Their namespace URI was originally 'http://garshol.priv.no/symbolic/'
## but has been changed to the 4Suite.org NSRef
## so users don't have to declare yet another namespace.
##


def distinct(context, nodeset):
    if type(nodeset) != type([]):
        raise Exception("'distinct' parameter must be of type node-set!")

    nodes = {}
    for node in nodeset:
        nodes[Conversions.StringValue(node)] = node

    return list(nodes.values())


def split(context, arg, delim=None):
    doc = context.node
    while doc.parentNode:
        doc = doc.parentNode

    nodeset = []
    for token in string.split(Conversions.StringValue(arg), delim):
        nodeset.append(doc.createTextNode(token))

    return nodeset


def join(context, nodeset, delim=None):
    comps = [Conversions.StringValue(x) for x in nodeset]
    if delim:
        return string.joinfields(comps, delim)
    else:
        return string.joinfields(comps)


def range(context, lo, hi):
    doc = context.node
    while doc.parentNode:
        doc = doc.parentNode

    lo = Conversions.NumberValue(lo)
    hi = Conversions.NumberValue(hi)

    nodeset = []
    for number in range(lo, hi):
        nodeset.append(doc.createTextNode(str(number)))

    return nodeset


def if_function(context, cond, v1, v2):
    if Conversions.BooleanValue(cond):
        return v1
    else:
        return v2


def find(context, outer, inner):
    return string.find(Conversions.StringValue(outer), Conversions.StringValue(inner))


ExtFunctions = {
    (FT_EXT_NAMESPACE, "node-set"): NodeSet,
    (FT_EXT_NAMESPACE, "match"): Match,
    (FT_EXT_NAMESPACE, "search-re"): sys.hexversion != 0x20000F1
    and SearchRe
    or SearchRePy20,
    (FT_EXT_NAMESPACE, "base-uri"): BaseUri,
    (FT_EXT_NAMESPACE, "escape-url"): EscapeUrl,
    (FT_EXT_NAMESPACE, "iso-time"): IsoTime,
    (FT_EXT_NAMESPACE, "evaluate"): Evaluate,
    (FT_EXT_NAMESPACE, "distinct"): distinct,
    (FT_EXT_NAMESPACE, "split"): split,
    (FT_EXT_NAMESPACE, "join"): join,
    (FT_EXT_NAMESPACE, "range"): range,
    (FT_EXT_NAMESPACE, "if"): if_function,
    (FT_EXT_NAMESPACE, "find"): find,
    (FT_EXT_NAMESPACE, "map"): Map,
    (FT_EXT_NAMESPACE, "version"): Version,
    (FT_EXT_NAMESPACE, "generate-uuid"): GenerateUuid,
    (FT_EXT_NAMESPACE, "replace"): Replace,
    (FT_OLD_EXT_NAMESPACE, "node-set"): NodeSet,
    (FT_OLD_EXT_NAMESPACE, "match"): Match,
    (FT_OLD_EXT_NAMESPACE, "search-re"): sys.hexversion != 0x20000F1
    and SearchRe
    or SearchRePy20,
    (FT_OLD_EXT_NAMESPACE, "base-uri"): BaseUri,
    (FT_OLD_EXT_NAMESPACE, "escape-url"): EscapeUrl,
    (FT_OLD_EXT_NAMESPACE, "iso-time"): IsoTime,
    (FT_OLD_EXT_NAMESPACE, "evaluate"): Evaluate,
    (FT_OLD_EXT_NAMESPACE, "distinct"): distinct,
    (FT_OLD_EXT_NAMESPACE, "split"): split,
    (FT_OLD_EXT_NAMESPACE, "join"): join,
    (FT_OLD_EXT_NAMESPACE, "range"): range,
    (FT_OLD_EXT_NAMESPACE, "if"): if_function,
    (FT_OLD_EXT_NAMESPACE, "find"): find,
    (FT_OLD_EXT_NAMESPACE, "map"): Map,
    (FT_OLD_EXT_NAMESPACE, "version"): Version,
}
