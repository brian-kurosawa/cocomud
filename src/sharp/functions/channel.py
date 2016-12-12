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

"""Module containing the Channel function class."""

from scripting.channel import Channel as ObjChannel
from sharp import Function
from ui.dialogs.channel import ChannelsDialog

class Channel(Function):

    """Function SharpScript 'channel'."""

    description = "Create or display a channel"

    def run(self, name, show=True):
        """Create a channel."""
        if self.world:
            if name not in [ch.name for ch in self.world.channels]:
                channel = ObjChannel(self.world, name)
                self.world.channels.append(channel)
            else:
                if show:
                    dialog = ChannelsDialog(self.world.channels, name)
                    dialog.ShowModal()

    def display(self, dialog, name="", show=True):
        """Display the function's argument."""
        l_name = self.t("name", "Unique name of the channel")
        l_show = self.t("show", "Show this channel in a dialog box")

        # Dialog
        l_name = wx.StaticText(dialog, label=l_name)
        t_name = wx.TextCtrl(dialog, value=name)
        dialog.name = t_name
        dialog.top.Add(l_name)
        dialog.top.Add(t_name)

        # Checkboxes
        options = wx.BoxSizer(wx.HORIZONTAL)
        dialog.cb_show = wx.CheckBox(dialog, label=l_show)
        dialog.cb_show.SetValue(show)
        options.Add(dialog.cb_screen)
        dialog.top.Add(options)

    def complete(self, dialog):
        """The user pressed 'ok' in the dialog."""
        name = dialog.name.GetValue().encode("utf-8", errors="replace")
        empty_name = self.t("empty_name",
                "The channel name is empty.  How do you want to call it?")

        if not name:
            wx.MessageBox(empty_name, t("ui.message.error"),
                    wx.OK | wx.ICON_ERROR)
            dialog.name.SetFocus()
            return None

        arguments = [name]

        # Get the options
        show = dialog.cb_show.GetValue()
        if not show:
            arguments.append("-show")

        return tuple(arguments)
