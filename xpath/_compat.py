#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" 
$ 
"""

from __future__ import annotations  # isort:skip
import sys  # isort:skip
import os  # isort:skip
import sys,string

def __getattr__(name): raise AttributeError(f'CONFIGURE THIS for {__name__}')

def get_translator(pkg):
    return

def GetAllNs(node):
	"""
	"""
	from xml.dom import XML_NAMESPACE, XMLNS_NAMESPACE, DOMException, Node
	nss = {'xml': XML_NAMESPACE}
	if node.nodeType == Node.ATTRIBUTE_NODE and node.ownerElement:
		return GetAllNs(node.ownerElement)
	if node.nodeType == Node.ELEMENT_NODE:
		if node.namespaceURI:
			nss[node.prefix] = node.namespaceURI
		for attr in node.attributes.values():
			if attr.namespaceURI == XMLNS_NAMESPACE:
				if attr.localName == 'xmlns':
					nss[None] = attr.value
				else:
					nss[attr.localName] = attr.value
			elif attr.namespaceURI:
				nss[attr.prefix] = attr.namespaceURI
	if node.parentNode:
		#Inner NS/Prefix mappings take precedence over outer ones
		parent_nss = GetAllNs(node.parentNode)
		parent_nss.update(nss)
		nss = parent_nss
	return nss

def SplitQName(qname):
    """
    Input a QName according to XML Namespaces 1.0
    http://www.w3.org/TR/REC-xml-names
    Return the name parts according to the spec
    In the case of namespace declarations the tuple returned
    is (prefix, 'xmlns')
    Note that this won't hurt users since prefixes and local parts starting
    with "xml" are reserved, but it makes ns-aware builders easier to write
    """
    #sName = g_splitNames.get(qname)
    sName = None
    if sName == None:
        fields = string.splitfields(qname, ':')
        if len(fields) == 1:
            #Note: we could gain a tad more performance by interning 'xmlns'
            if qname == 'xmlns':
                sName = (None, 'xmlns')
            else:
                sName = (None, qname)
        elif len(fields) == 2:
            if fields[0] == 'xmlns':
                sName = (fields[1], 'xmlns')
            else:
                sName = (fields[0], fields[1])
        else:
            sname = (None, None)
        #g_splitNames[qname] = sName
    return sName

class BooleanType:
	false = False
	true = True

boolean = BooleanType




__all__ = sorted(
		[getattr(v, '__name__', k)
		 for k, v in list(globals().items())  # export
		 if ((callable(v) and getattr(v, "__module__", "") == __name__  # callables from this module
		      or k.isupper()) and  # or CONSTANTS
		     not str(getattr(v, '__name__', k)).startswith('__'))])

if __name__ == '__main__':
	print(__file__)
    