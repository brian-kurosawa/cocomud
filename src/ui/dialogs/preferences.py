﻿"""Module containing the preferences dialog."""

import wx

class GeneralTab(wx.Panel):

    """General tab."""

    def __init__(self, parent, engine):
        super(GeneralTab, self).__init__(parent)
        self.engine = engine

        self.InitUI()
        self.Fit()

    def InitUI(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)

        # Language selection
        l_languages = wx.StaticText(self, label="Language")
        languages = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        languages.InsertColumn(0, "Name")
        self.languages = languages
        self.PopulateList()

        # Append to the sizer
        sizer.Add(l_languages)
        sizer.Add(languages, proportion=4)

    def PopulateList(self):
        """Add the different languages in the list."""
        supported = self.engine.settings.LANGUAGES
        codes = [lang[0] for lang in supported]
        languages = [lang[1] for lang in supported]
        for language in languages:
            self.languages.Append((language, ))

        default = self.engine.settings.get_language()
        index = codes.index(default)
        self.languages.Select(index)
        self.languages.Focus(index)

    def get_selected_language(self):
        """Return the selected language's code."""
        supported = self.engine.settings.LANGUAGES
        codes = [lang[0] for lang in supported]
        languages = [lang[1] for lang in supported]
        index = self.languages.GetFirstSelected()
        return codes[index]


class TTSTab(wx.Panel):

    """TTS tab."""

    def __init__(self, parent, engine):
        super(TTSTab, self).__init__(parent)
        self.engine = engine

        self.InitUI()
        self.Fit()

    def InitUI(self):
        settings = self.engine.settings
        panel = wx.Panel(self)
        sizer = wx.GridBagSizer(15, 15)
        panel.SetSizer(sizer)

        # TTS preferendces
        self.TTS_on = wx.CheckBox(panel, label="Enable TTS (Text-To Speech)")
        self.TTS_on.SetValue(settings["options.TTS.on"])
        self.TTS_outside = wx.CheckBox(panel, label="Enable TTS when on a different window")
        self.TTS_outside.SetValue(settings["options.TTS.outside"])

        # Append to the sizer
        sizer.Add(self.TTS_on, pos=(0, 0))
        sizer.Add(self.TTS_outside, pos=(0, 1))


class PreferencesTabs(wx.Notebook):

    """Preference tabs."""

    def __init__(self, parent, engine):
        wx.Notebook.__init__(self, parent)

        general_tab = GeneralTab(self, engine)
        TTS_tab = TTSTab(self, engine)
        self.AddPage(general_tab, "General")
        self.AddPage(TTS_tab, "TTS")
        self.general = general_tab
        self.TTS = TTS_tab

class PreferencesDialog(wx.Dialog):

    """Preferences dialog."""

    def __init__(self, engine):
        super(PreferencesDialog, self).__init__(None, title="Preferences")
        self.engine = engine

        self.InitUI()
        self.Maximize()

    def InitUI(self):
        panel = wx.Panel(self)
        sizer = wx.GridBagSizer(15, 15)
        panel.SetSizer(sizer)

        # Add the tabs
        self.tabs = PreferencesTabs(panel, self.engine)
        buttons = self.CreateButtonSizer(wx.OK | wx.CANCEL)

        # Append to the sizer
        sizer.Add(self.tabs, pos=(1, 0), span=( 5, 5))
        sizer.Add(buttons, pos=(8, 0), span=(1, 2))

        # Event binding
        self.Bind(wx.EVT_BUTTON, self.OnOK, id=wx.ID_OK)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, id=wx.ID_CANCEL)

        # Displaying
        self.tabs.general.SetFocus()

    def OnOK(self, e):
        """Save the preferences."""
        settings = self.engine.settings
        general = self.tabs.general
        tts = self.tabs.TTS
        new_language = general.get_selected_language()
        old_language = settings["options.general.language"]
        settings["options.general.language"] = new_language
        settings["options.TTS.on"] = tts.TTS_on.GetValue()
        settings["options.TTS.outside"] = tts.TTS_outside.GetValue()
        settings["options"].write()
        if old_language != new_language:
            wx.MessageBox("You have changed the CocoMUD anguage.  You " \
                    " to restart the application to see these changes.",
                    "Restart", wx.OK | wx.ICON_INFORMATION)
        self.Destroy()

    def OnCancel(self, e):
        """Simply exit the dialog."""
        self.Destroy()
