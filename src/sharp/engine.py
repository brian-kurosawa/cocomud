﻿# Copyright (c) 2016, LE GOFF Vincent
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.

# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.

# * Neither the name of ytranslate nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""Module containing the SharpEngine class."""

from textwrap import dedent

from sharp import FUNCTIONS

class SharpScript(object):

    """Class representing a SharpScript engine.

    An SharpScript engine is often linked with the game's main engine
    and an individual client, which is itself optionally linked to
    the ui application.

    """

    def __init__(self, engine, client):
        self.engine = engine
        self.client = client
        self.locals = {}
        self.globals = globals()

        # Adding the functions
        for name, function in FUNCTIONS.items():
            function = function(engine, client, self.locals)
            self.globals[name] = function.run

    def execute(self, code):
        """Execute the SharpScript code given as an argument."""
        instructions = self.feed(code)
        globals = self.globals
        locals = self.locals
        for instruction in instructions:
            exec(instruction, globals, locals)

    def feed(self, content):
        """Feed the SharpScript engine with a string content.

        The content is probably a file with several statements in
        SharpScript, or a single statement.  In all cases, this function
        returns the list of Python codes corresponding with
        this suite of statements.

        """
        # First, splits into statements
        statements = self.split_statements(content)
        codes = []
        for statement in statements:
            pycode = self.convert_to_python(statement)
            codes.append(pycode)

        return codes

    def convert_to_python(self, statement):
        """Convert the statement to Python and return the str code.

        The statement given in argument should be a tuple:  The first
        argument of the tuple should be a function (like '#play' or
        '#send').  The remaining arguments should be put in a string,
        except for other Sharp or Python code.

        """
        function_name = statement[0][1:].lower()
        arguments = []
        for argument in statement[1:]:
            if argument.startswith("{+"):
                argument = argument[3:-2]
                code = dedent(argument)
                argument = "compile(" + repr(code) + ", 'SharpScript', 'exec')"
            elif argument.startswith("{"):
                argument = repr(argument[1:-1])
            else:
                argument = repr(argument)

            arguments.append(argument)

        return function_name + "(" + ", ".join(arguments) + ")"

    def split_statements(self, content):
        """Split the given string content into different statements.

        A statement is one-line short at the very least.  It can be
        longer by that, if it's enclosed into braces.

        """
        statements = []
        i = 0
        function_name = ""
        arguments = []
        while True:
            remaining = content[i:]

            # If remaining is empty, saves the statement and exits the loop
            if not remaining or remaining.isspace():
                if function_name:
                    statements.append((function_name, ) + tuple(arguments))

                break

            # If remaining begins with a new line
            if remaining[0] == "\n":
                if function_name:
                    statements.append((function_name, ) + tuple(arguments))
                    function_name = ""
                    arguments = []

                i += 1
                continue

            # If remaining begins with a space
            if remaining[0].isspace():
                remaining = remaining[1:]
                i += 1
                continue

            # If the function_name is not defined, take the first parameter
            if not function_name:
                if remaining.startswith("#"):
                    # This is obviously a function name
                    function_name = remaining.splitlines()[0].split(" ")[0]
                    arguments = []
                    i += len(function_name)
                else:
                    function_name = "#send"
                    argument = remaining.splitlines()[0]
                    i += len(argument)
                    arguments = [argument]
            elif remaining[0] == "{":
                end = self.find_right_brace(remaining)
                argument = remaining[:end + 1]
                arguments.append(argument)
                i += end + 1
            else:
                argument = remaining.splitlines()[0].split(" ")[0]
                i += len(argument)
                arguments.append(argument)

        return statements

    def find_right_brace(self, text):
        """Find the right brace matching the opening one.

        This function doesn't only look for the first right brace (}).
        It looks for a brace that would close the text and return the
        position of this character.  For instance:
            >>> Engine.find_right_brace("{first parameter {with} something} else")
            33

        """
        level = 0
        i = 0
        while i < len(text):
            char = text[i]
            if char == "{":
                level += 1
            elif char == "}":
                level -= 1

            if level == 0:
                return i

            i += 1

        return None
