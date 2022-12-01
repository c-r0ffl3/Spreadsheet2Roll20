import wx
import os
import sys
import traceback
from typing import Union
from processor import process


class AppFrame(wx.Frame):
    wildcard = "HTML file (*.html)|*.html|"

    def __init__(self):
        super().__init__(parent=None, title="Spreadsheet2Roll20", size=(550, -1))

        self.filename: Union[str, None] = None

        self.mainPanel = wx.Panel(self)
        self.bottomPanel = wx.Panel(self.mainPanel)

        self.text_description = """
# Spreadsheet2Roll20
github: https://github.com/c-r0ffl3/Spreadsheet2Roll20
        """
        self.text_area = wx.StaticText(self.mainPanel, label=self.text_description)

        # UI in bottom panel
        self.filename_holder = wx.TextCtrl(self.bottomPanel, value="Choose any file...", size=(300, -1))

        self.file_load_button = wx.Button(self.bottomPanel, label="Load file", size=(100, -1))
        self.file_load_button.Bind(wx.EVT_BUTTON, self.open_file)

        self.file_process_button = wx.Button(self.bottomPanel, label="Process", size=(100, -1))
        self.file_process_button.Bind(wx.EVT_BUTTON, self.process_file)

        self.hzBoxSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.hzBoxSizer.Add(self.filename_holder)
        self.hzBoxSizer.Add(self.file_load_button, 0, 5)
        self.hzBoxSizer.Add(self.file_process_button)
        self.bottomPanel.SetSizer(self.hzBoxSizer)

        self.vtBoxSizer = wx.BoxSizer(wx.VERTICAL)
        self.vtBoxSizer.Add(self.text_area, 0, wx.EXPAND | wx.ALL, 5)
        self.vtBoxSizer.Add(self.bottomPanel, 0, wx.ALIGN_CENTER | wx.BOTTOM | wx.LEFT, 5)

        self.mainPanel.SetSizer(self.vtBoxSizer)

        self.Show()

    def open_file(self, event):
        with wx.FileDialog(self, "Choose a file", os.getcwd(), "", wildcard=AppFrame.wildcard,
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            pathname = fileDialog.GetPath()
            self.filename = pathname
            self.filename_holder.SetLabel(pathname)

    def process_file(self, event):
        try:
            if self.filename:
                process(self.filename)
        except Exception as err:
            wx.LogError(f"Unexpected {err=}, {type(err)=}")
            print(traceback.format_exc())
            print(sys.exc_info()[2])
        dlg = wx.MessageDialog(None, message="output file: sheet.html, style.css", caption="Process is done!",
                               style=wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()


if __name__ == '__main__':
    app = wx.App()
    frame = AppFrame()
    app.MainLoop()
