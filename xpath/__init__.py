########################################################################
#
# File Name:            __init__.py
#
#
"""
WWW: http://4suite.org/4XPath         e-mail: support@4suite.org

Copyright (c) 2000-2001 Fourthought Inc, USA.   All Rights Reserved.
See  http://4suite.org/COPYRIGHT  for license and copyright information
"""

NAMESPACE_NODE = 10000
FT_OLD_EXT_NAMESPACE = "http://xmlns.4suite.org/xpath/extensions"
FT_EXT_NAMESPACE = "http://xmlns.4suite.org/ext"
# Simple trick (thanks Tim Peters) to enable crippled IEEE 754 support
# until ANSI C (or Python) sorts it all out...
Inf = Inf = 1e300 * 1e300
NaN = Inf - Inf

# stdlib

from xml.dom import Node
from .exceptions import FtException, MessageSource, SyntaxException
from .exceptions import CompiletimeException, RuntimeException

# localfolder
# Allow access to the NormalizeNode function

g_xpathRecognizedNodes = [
    Node.ELEMENT_NODE,
    Node.ATTRIBUTE_NODE,
    Node.TEXT_NODE,
    Node.CDATA_SECTION_NODE,
    Node.DOCUMENT_NODE,
    Node.PROCESSING_INSTRUCTION_NODE,
    Node.COMMENT_NODE,
]

g_extFunctions = {}


def Evaluate(expr, contextNode=None, context=None):
    import os
    from xpath import Context

    if "EXTMODULES" in os.environ:
        RegisterExtensionModules(os.environ["EXTMODULES"].split(":"))

    if context:
        con = context
    elif contextNode:
        con = Context.Context(contextNode, 0, 0)
    else:
        raise RuntimeException(RuntimeException.NO_CONTEXT_ERROR)
    retval = parser.new().parse(expr).evaluate(con)
    return retval

def Compile(expr):
    try:
        return parser.new().parse(expr)
    except SyntaxError as error:
        raise CompiletimeException(CompiletimeException.SYNTAX, str(error))
    except:
        import traceback, io

        stream = io.StringIO()
        traceback.print_exc(None, stream)
        raise RuntimeException(RuntimeException.INTERNAL, stream.getvalue())


def CreateContext(contextNode):
    from xpath import Context
    return Context.Context(contextNode, 0, 0)


def RegisterExtensionModules(moduleNames):
    mod_names = moduleNames[:]
    mods = []
    for mod_name in mod_names:
        if mod_name:
            mod = __import__(mod_name, {}, {}, ["ExtFunctions"])
            if hasattr(mod, "ExtFunctions"):
                g_extFunctions.update(mod.ExtFunctions)
                mods.append(mod)
    return mods


from .Util import NormalizeNode

try:
    import xpath.XPathParser
except ImportError:
    # import XPathParser
    # parser = XPathParser
    from xpath.pyxpath import ExprParserFactory

    parser = ExprParserFactory
else:
    parser = XPathParser


def Init():
    from xpath import BuiltInExtFunctions

    g_extFunctions.update(BuiltInExtFunctions.ExtFunctions)


Init()
