#! coding=UTF-8

# Copyright 2012 Thomas Bollmeier <tbollmeier@web.de>

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#   http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# ===== Interne Objekte: =====

class Connectable(object):

    def __init__(self):
        pass

    def getSocket(self):
        raise NotImplementedError

class Socket(object):

    def __init__(self):
        pass

    def getSuccessors(self, context):
        raise NotImplementedError

class Pluggable(object):

    def __init__(self):
        pass

    def getPlug(self):
        raise NotImplementedError

class Plug(object):

    def __init__(self):
        pass

    def connectTo(self, socket):
        raise NotImplementedError

class GrammarElement(object):

    def __init__(self):
        pass

    def connect(self, successorElement):
        raise NotImplementedError

# ===== API =====

class Rule(Connectable, Pluggable, GrammarElement):

    def __init__(self, name='', identifier=''):

        if self.__class__ == Rule:
            raise Exception('Rule is an abstract class')

        if not name:
            name = self.__class__.__name__

        Connectable.__init__(self)
        Pluggable.__init__(self)
        GrammarElement.__init__(self)

        self._start = RuleStartNode(self, name, identifier)
        self._end = RuleEndNode(self)
        self._envVars = {}

    def expand(self, start, end, context):

        raise NotImplementedError

    # Knoten in AST ggf. umwandeln:
    def transform(self, astNode):

        return astNode

    def getName(self):

        return self._start.getName()

    def onSuccRequested(self, start, end, context):

        self.expand(start, end, context)

    def getEndNode(self):

        return self._end

    def getEnvVars(self):

        return self._envVars

    def setEnvVar(self, name, value=True):

        self._envVars[name] = value

    def getSocket(self):

        return self._start

    def getPlug(self):

        return self._end

    def connect(self, successorElement):

        self._end.connectTo(successorElement.getSocket())

        return successorElement

def defineRule(name):

    return _RuleFactory(name)

class initialize(object):

    def __init__(self, ruleFactory):

        self._ruleFactory = ruleFactory

    def __call__(self, initFunc):

        self._ruleFactory._initFunc = initFunc

class expand(object):

    def __init__(self, ruleFactory):

        self._ruleFactory = ruleFactory

    def __call__(self, expandFunc):

        self._ruleFactory._expandFunc = expandFunc

class transform(object):

    def __init__(self, ruleFactory):

        self._ruleFactory = ruleFactory

    def __call__(self, transformFunc):

        self._ruleFactory._transformFunc = transformFunc

class Grammar(Rule):

    def __init__(self, tokenTypes):

        Rule.__init__(self)

        self._tokenTypes = tokenTypes

    def getTokenTypes(self):

        return self._tokenTypes

def tokenNode(tokenType, identifier=''):

    if not tokenType:
        raise Exception('Token type not specified')

    return TokenNode(tokenType, identifier)

def connector():

    return PlugNode(Node.TECHNICAL)

def connect(predecessor, successor):

    predecessor.getPlug().connectTo(successor.getSocket())

    return successor

def zeroToOne(element):

    return Multiplier(element, Multiplier.ZERO_TO_ONE)

def zeroToMany(element):

    return Multiplier(element, Multiplier.ZERO_TO_MANY)

def oneToMany(element):

    return Multiplier(element, Multiplier.ONE_TO_MANY)

def sequence(*elements):

    return Sequence(elements)

def fork(*branches):

    return Fork(branches)

class Switch(Connectable, Pluggable, GrammarElement):

    def __init__(self, branches):

        Connectable.__init__(self)
        Pluggable.__init__(self)
        GrammarElement.__init__(self)

        self._end = connector()
        self._start = _SwitchNode(branches, self._end)

    def getSocket(self):

        return self._start

    def getPlug(self):

        return self._end

    def connect(self, successorElement):

        self._end.connectTo(successorElement.getSocket())

        return successorElement

class Condition(Connectable, Pluggable, GrammarElement):

    def __init__(self, conditionFunc):

        Connectable.__init__(self)
        Pluggable.__init__(self)
        GrammarElement.__init__(self)

        self._end = connector()
        self._start = _ConditionalNode(conditionFunc, self._end)

    def getSocket(self):

        return self._start

    def getPlug(self):

        return self._end

    def connect(self, successorElement):

        self._end.connectTo(successorElement.getSocket())

        return successorElement

class SuccessorError(Exception):

    pass

# ===== Interne Objekte: =====

class _CustomRule(Rule):

    def __init__(self,
                 name,
                 ident,
                 initFunc,
                 expandFunc,
                 transformFunc
                 ):

        Rule.__init__(self, name, ident)

        if initFunc:
            initFunc(self)

        self._expandFunc = expandFunc
        self._transformFunc = transformFunc

    def expand(self, start, end, context):

        self._expandFunc(start, end, context)

    def transform(self, astNode):

        if self._transformFunc:
            return self._transformFunc(astNode)
        else:
            return astNode

class _RuleFactory(object):

    def __init__(self, name):

        self._name = name
        self._initFunc = None
        self._expandFunc = None
        self._transformFunc = None

    def __call__(self, ident=''):

        return _CustomRule(self._name,
                           ident,
                           self._initFunc,
                           self._expandFunc,
                           self._transformFunc
                           )

    def getName(self):

        return self._name

    name = property(getName)

class IdNode(object):

    def __init__(self):
        pass

    def getId(self):
        raise NotImplementedError

class Node(Connectable, Socket):

    # Node categories:
    RULE_START = 1
    RULE_END = 2
    TOKEN = 3
    TECHNICAL = 4

    __nextTechId = 1

    def __init__(self, category, tokenType = None):

        Connectable.__init__(self)
        Socket.__init__(self)

        self._catg = category
        self._tokenType = tokenType

        self.__techId = Node.__nextTechId
        Node.__nextTechId += 1

    def getTokenType(self):

        return self._tokenType

    def getTokenTypeId(self):

        return self._tokenType and self._tokenType.getId() or -1

    def isRuleStart(self):

        return self._catg == Node.RULE_START

    def isRuleEnd(self):

        return self._catg == Node.RULE_END

    def isTokenNode(self):

        return self._catg == Node.TOKEN

    def isTechnicalNode(self):

        return self.catg == Node.TECHNICAL

    def getSocket(self):

        return self

    def getTechnicalId(self):

        return self.__techId

class PlugNode(Node, Pluggable, Plug, GrammarElement):

    def __init__(self, category, tokenType = None):

        Node.__init__(self, category, tokenType)
        Pluggable.__init__(self)
        Plug.__init__(self)
        GrammarElement.__init__(self)

        self._successors = []

    def getSuccessors(self, context):

        return self._successors

    def getPlug(self):

        return self

    def connectTo(self, socket):

        if not socket in self._successors:
            self._successors.append(socket)

    def connect(self, successorElement):

        self.connectTo(successorElement.getSocket())

        return successorElement

class RuleStartNode(Node, IdNode):

    def __init__(self, ruleAccess, name, identifier):

        Node.__init__(self, Node.RULE_START)
        IdNode.__init__(self)

        self._ruleAccess = ruleAccess
        self._name = name
        self._id = identifier

    def getSuccessors(self, context):

        start = PlugNode(Node.TECHNICAL)
        end = PlugNode(Node.TECHNICAL)

        self._ruleAccess.onSuccRequested(start, end, context)

        end.connectTo(self._ruleAccess.getEndNode())

        return [start]

    def getEnvVars(self):

        return self._ruleAccess.getEnvVars()

    def getName(self):

        return self._name

    def getId(self):

        return self._id

class RuleEndNode(PlugNode):

    def __init__(self, ruleAccess):

        PlugNode.__init__(self, Node.RULE_END, None)

        self._ruleAccess = ruleAccess

    def transform(self, astNode):

        return self._ruleAccess.transform(astNode)

class TokenNode(PlugNode, IdNode):

    def __init__(self, tokenType, identifier = ''):

        PlugNode.__init__(self, Node.TOKEN, tokenType)
        IdNode.__init__(self)

        self._id = identifier
        self._envVarChangeFunc = None
        self._envVarUndoFunc = None

    def getId(self):

        return self._id

    def setEnvChange(self, changeFunc, undoFunc):

        self._envVarChangeFunc = changeFunc
        self._envVarUndoFunc = undoFunc

    def changesEnv(self):

        return ( self._envVarChangeFunc is not None ) and \
          ( self._envVarUndoFunc is not None )

    def changeEnv(self, envVars, token):

        if self._envVarChangeFunc:
            self._envVarChangeFunc(envVars, token, self)

    def undoEnvChange(self, envVars, token):

        if self._envVarUndoFunc:
            self._envVarUndoFunc(envVars, token, self)

class _SwitchNode(Node):

    def __init__(self, branches, end):

        Node.__init__(self, Node.TECHNICAL)

        self._branches = branches
        self._end = end

    def getSuccessors(self, context):

        keyword = context.getCurKeyword()
        if not keyword:
            return []

        try:
            branch = self._branches[keyword]
            start = connector()
            start.connect(branch).connect(self._end)
            return [start]
        except KeyError:
            return []

class _ConditionalNode(Node):

    def __init__(self, conditionFunc, end):

        Node.__init__(self, Node.TECHNICAL)

        self._conditionFunc = conditionFunc
        self._end = end

    def getSuccessors(self, context):

        if self._conditionFunc(context):
            return [self._end]
        else:
            raise SuccessorError

class RuleInternalAccess(object):

    def __init__(self):
        pass

    def getName(self):
        raise NotImplementedError

    def getEndNode(self):
        raise NotImplementedError

    def getEnvVars(self):
        raise NotImplementedError

    def onSuccRequested(self, start, end, context):
        raise NotImplementedError

    def transform(self, astNode):
        raise NotImplementedError

class Multiplier(Connectable, Pluggable, GrammarElement):

    ZERO_TO_ONE = 1
    ZERO_TO_MANY = 2
    ONE_TO_MANY = 3

    def __init__(self, element, mult):

        Connectable.__init__(self)
        Pluggable.__init__(self)
        GrammarElement.__init__(self)

        self._start = connector()
        self._end = connector()

        if mult == Multiplier.ZERO_TO_ONE:

            connect(self._start, self._end)
            connect(self._start, element)
            connect(element, self._end)

        elif mult == Multiplier.ZERO_TO_MANY:

            connect(self._start, self._end)
            connect(self._start, element)
            connect(element, self._start)

        elif mult == Multiplier.ONE_TO_MANY:

            connect(self._start, element)
            connect(element, self._end)
            connect(element, element)

    def getSocket(self):

        return self._start

    def getPlug(self):

        return self._end

    def connect(self, successorElement):

        self._end.connectTo(successorElement.getSocket())

        return successorElement

class Sequence(Connectable, Pluggable, GrammarElement):

    def __init__(self, elements):

        Connectable.__init__(self)
        Pluggable.__init__(self)
        GrammarElement.__init__(self)

        self._start = connector()
        self._end = connector()

        current = self._start
        for elem in elements:
            connect(current, elem)
            current = elem
        connect(current, self._end)

    def getSocket(self):

        return self._start

    def getPlug(self):

        return self._end

    def connect(self, successorElement):

        self._end.connectTo(successorElement.getSocket())

        return successorElement

class Fork(Connectable, Pluggable, GrammarElement):

    def __init__(self, branches):

        Connectable.__init__(self)
        Pluggable.__init__(self)
        GrammarElement.__init__(self)

        self._start = connector()
        self._end = connector()

        for branch in branches:
            self._start.connect(branch).connect(self._end)

    def getSocket(self):

        return self._start

    def getPlug(self):

        return self._end

    def connect(self, successorElement):

        self._end.connectTo(successorElement.getSocket())

        return successorElement
