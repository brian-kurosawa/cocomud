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

"""This file contains the SharpEditor class."""

import wx

from ytranslate.tools import t

class SharpEditor(wx.Panel):

    """SharpScript editor panel.

    This panel can be added into dialogs that have to support SharpScript
    editing.  On the top, at the left of the panel, is a list of
    SharpScript functions which could be added to the edited SharpScript.
    On the right of this list is a button to add the selected function
    to the action field.

    At the bottom of this panel is the list of functions currently
    used in the selected attribute.

    """

    def __init__(self, dialog, engine, sharp, object, attribute):
        """Creates the frame.

        Arguments:
            dialog: the parent dialog.
            engine: the game engine.
            sharp: the SharpScript engine.
            object: the object containing the field to be edited.
            attribute: the attribute's name of the object to edit.

        If the SharpEditor is to modify a trigger, for instance,
        particularly its "action" attribute, the trigger is the object
        and "action" is the attribute's name.

        """
        wx.Panel.__init__(self, dialog)
        self.engine = engine
        self.sharp_engine = sharp
        self.object = object
        self.attribute = attribute

        # Shape
        self.functions = sorted(sharp.functions.values(),
                key=lambda function: function.name)
        self.functions = [f for f in self.functions if f.description]
        sizer = wx.BoxSizer(wx.VERTICAL)
        top = wx.BoxSizer(wx.HORIZONTAL)
        bottom = wx.BoxSizer(wx.HORIZONTAL)
        self.options = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)

        # List of functions
        self.choices = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.choices.InsertColumn(0, t("common.description"))
        self.populate_list()
        top.Add(self.choices)
        top.Add(self.options, proportion=3)

        # Bottom
        add = wx.Button(self, label=t("ui.button.add_action"))
        bottom.Add(add)

        # List of current functions
        self.existing = wx.ListCtrl(self,
                style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.existing.InsertColumn(0, t("common.action"))
        self.populate_existing()

        # Buttons
        edit = wx.Button(self, label=t("ui.button.edit"))
        remove = wx.Button(self, label=t("ui.button.remove"))
        bottom.Add(self.existing)
        bottom.Add(edit)
        bottom.Add(remove)

        # Event binding
        add.Bind(wx.EVT_BUTTON, self.OnAdd)
        edit.Bind(wx.EVT_BUTTON, self.OnEdit)
        remove.Bind(wx.EVT_BUTTON, self.OnRemove)

    def populate_list(self):
        """Populate the list with function names."""
        self.choices.DeleteAllItems()
        for function in self.functions:
            try:
                description = t("sharp.{name}.description".format(
                        name=function.name))
            except ValueError:
                description = function.description

            self.choices.Append((description, ))

        self.choices.Select(0)
        self.choices.Focus(0)

    def populate_existing(self):
        """Populate the list with existing functions."""
        self.existing.DeleteAllItems()
        script = getattr(self.object, self.attribute)
        lines = self.sharp_engine.format(script, return_str=False)
        for line in lines:
            self.existing.Append((line, ))

        self.existing.Select(0)
        self.existing.Focus(0)

    def OnAdd(self, e):
        """The 'add' button is pressed."""
        index = self.choices.GetFirstSelected()
        try:
            function = self.functions[index]
        except IndexError:
            wx.MessageBox(t("ui.message.sharp.missing"),
                    t("ui.message.error"), wx.OK | wx.ICON_ERROR)
        else:
            dialog = AddEditFunctionDialog(self.engine, self.sharp_engine, function, self.object, self.attribute)
            dialog.ShowModal()
            self.populate_existing()
            self.existing.SetFocus()

    def OnEdit(self, e):
        """The 'edit' button is pressed."""
        index = self.existing.GetFirstSelected()
        script = getattr(self.object, self.attribute)
        lines = self.sharp_engine.format(script, return_str=False)
        try:
            line = lines[index]
        except IndexError:
            wx.MessageBox(t("ui.message.sharp.missing"),
                    t("ui.message.error"), wx.OK | wx.ICON_ERROR)
        else:
            name, arguments, flags = self.sharp_engine.extract_arguments(line)
            function = self.sharp_engine.functions[name[1:]]
            dialog = AddEditFunctionDialog(self.engine, self.sharp_engine,
                    function, self.object, self.attribute, index)
            dialog.ShowModal()
            self.populate_existing()
            self.existing.SetFocus()

    def OnRemove(self, e):
        """The 'remove' button is pressed."""
        index = self.existing.GetFirstSelected()
        script = getattr(self.object, self.attribute)
        lines = self.sharp_engine.format(script, return_str=False)
        try:
            line = lines[index]
        except IndexError:
            wx.MessageBox(t("ui.message.sharp.missing"),
                    t("ui.message.error"), wx.OK | wx.ICON_ERROR)
        else:
            value = wx.MessageBox(t("ui.message.sharp.remove", line=line),
                    t("ui.dialog.confirm"),
                    wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)

            if value == wx.YES:
                del lines[index]
                content = "\n".join(lines)
                setattr(self.object, self.attribute, content)
                self.populate_existing()
                self.existing.SetFocus()


class AddEditFunctionDialog(wx.Dialog):

    """Add or edit a function."""

    def __init__(self, engine, sharp_engine, function, object, attribute,
            index=-1):
        super(AddEditFunctionDialog, self).__init__(None,
                title=t("common.action"))
        self.engine = engine
        self.sharp_engine = sharp_engine
        self.world = sharp_engine.world
        self.function = function
        self.object = object
        self.attribute = attribute
        self.index = index
        arguments = []
        flags = {}
        if index >= 0:
            script = getattr(self.object, self.attribute)
            lines = self.sharp_engine.format(script, return_str=False)
            line = lines[index]
            function, arguments, flags = self.sharp_engine.extract_arguments(line)

        # Dialog
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.top = wx.BoxSizer(wx.VERTICAL)
        buttons = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        self.SetSizer(sizer)

        # Add the function-specific configuration
        sizer.Add(self.top)
        self.function.display(self, *arguments, **flags)
        sizer.Add(buttons)

        # Event binding
        self.Bind(wx.EVT_BUTTON, self.OnOk, id=wx.ID_OK)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, id=wx.ID_CANCEL)

    def OnOk(self, e):
        """The 'OK' button is pressed."""
        arguments = self.function.complete(self)
        if arguments is not None:
            function = "#" + self.function.name
            lines = (((function, ) + arguments), )
            line = self.sharp_engine.format(lines)

            # Add to the entire content
            lines = self.sharp_engine.format(getattr(self.object,
                    self.attribute), return_str=False)
            if self.index >= 0:
                lines[self.index] = line
                content = "\n".join(lines)
            else:
                content = "\n".join(lines)
                if content:
                    content += "\n"

                content += line
            setattr(self.object, self.attribute, content)
            self.Destroy()

    def OnCancel(self, e):
        """The 'cancel' button is pressed."""
        self.Destroy()
