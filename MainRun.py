import cv2
import numpy as np
import wx
import os

hasChoose = False

skinSrc = None


class MainFeamr(wx.Frame):
    def __init__(self, parent, id):
        wx.Frame.__init__(self, parent, id, 'MC皮肤FaceRig转换器', size=(720, 620),
                          style=wx.CAPTION | wx.MINIMIZE_BOX | wx.CLOSE_BOX | wx.SYSTEM_MENU)
        self.Center()

        self.skinType = 'N\\A'
        self.hasDouble = 'N\\A'
        self.wantDouble = 'N\\A'
        self.msgstr = '皮肤类型: %s' % self.skinType + '\r\n双层皮肤: %s' % self.hasDouble + '\r\n保留双层皮肤: %s' % self.wantDouble

        self.isAlexflag = True
        self.hasDoubleflag = False
        self.keepDouble = False

        self.rightEyePos = (9, 12, 9, 13)
        self.leftEyePos = (14, 12, 14, 13)
        self.mouthPos = (11, 15, 12, 15)

        panel = wx.Panel(self)

        font1 = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, '微软雅黑')

        self.skinLabel = wx.StaticText(panel, -1, '皮肤文件位置: ', (10, 17), (100, 20), wx.ALIGN_CENTER)
        self.skinLabel.SetFont(font1)

        self.skinPathCtrl = wx.TextCtrl(panel, -1, '', (120, 15), (500, 25))
        self.skinBtn = wx.Button(panel, -1, '...', (630, 15), (40, 25))
        self.skinBtn.Bind(wx.EVT_BUTTON, self.openskin)

        self.steamLabel = wx.StaticText(panel, -1, 'steam根目录: ', (10, 52), (100, 20), wx.ALIGN_CENTER)
        self.steamLabel.SetFont(font1)

        self.steamPathCtrl = wx.TextCtrl(panel, -1, '', (120, 50), (500, 25))
        self.steamBtn = wx.Button(panel, -1, '...', (630, 50), (40, 25))
        self.steamBtn.Bind(wx.EVT_BUTTON, self.opensteam)

        wx.StaticText(panel, -1, '——————————————————————————————————————————————————————————————————',
                      (0, 85)).SetForegroundColour('gray')

        self.imgTemp = np.zeros((320, 640, 4), np.uint8)
        alphaChannel = cv2.split(self.imgTemp)[3]
        pic = wx.Bitmap.FromBufferAndAlpha(640, 320, self.imgTemp, alphaChannel)
        self.img = wx.StaticBitmap(panel, -1, pic, pos=(30, 110), size=(640, 320))
        # self.img.SetBackgroundColour((255, 255, 255))
        self.img.Bind(wx.EVT_LEFT_DOWN, self.onchoosePos)
        self.img.Bind(wx.EVT_RIGHT_DOWN, self.onchoosePos)

        self.loadBtn = wx.Button(panel, -1, '加载皮肤', (50, 440), (100, 25))
        self.loadBtn.Bind(wx.EVT_BUTTON, self.loadSkin)

        self.skinMsg = wx.TextCtrl(panel, -1, self.msgstr, (20, 480), (160, 70),
                                   style=wx.TE_MULTILINE|wx.NO_BORDER|wx.TE_READONLY)
        self.skinMsg.SetFont(font1)

        self.keppBtn = wx.CheckBox(panel, -1, '保留双层皮肤: ', (200, 450), style=wx.ALIGN_RIGHT)
        self.keppBtn.Bind(wx.EVT_CHECKBOX, self.keepDo)
        self.keppBtn.Enable(False)

        typeList = ['纤细', '粗壮']
        self.radiobox1 = wx.RadioBox(panel, -1, "皮肤类型", (200, 475), (110, 55), typeList, 2, wx.RA_SPECIFY_COLS)
        self.radiobox1.Enable(False)

        posList = ['左眼', '右眼', '嘴巴']
        self.radiobox2 = wx.RadioBox(panel, -1, "细节调整", (350, 450), (80, 110), posList, 3, wx.RA_SPECIFY_ROWS)
        self.radiobox2.Enable(False)

        self.startBtn = wx.Button(panel, -1, '开始', (215, 540), (80, 25))
        self.startBtn.Enable(False)

        self.posmsgBG = wx.StaticText(panel, -1, '', (480, 450), (180, 110))
        self.posmsgBG.SetBackgroundColour((0, 0, 0))
        self.posmsgFG = wx.StaticText(panel, -1, '', (481, 451), (178, 108))
        self.posmsgFG.SetBackgroundColour((255, 255, 255))

        self.posmsg = wx.TextCtrl(panel, -1, '', (483, 453), (174, 104),
                                   style=wx.TE_MULTILINE|wx.NO_BORDER|wx.TE_READONLY)

    def openskin(self, event):
        wildcard = '皮肤文件(*.png)|*.png|所有文件(*.*)|*.*'
        dialog = wx.FileDialog(self, '选择皮肤文件', os.getcwd(), '', wildcard, wx.FD_OPEN)

        if dialog.ShowModal() == wx.ID_OK:
            self.skinPathCtrl.SetValue(dialog.GetPath())
            dialog.Destroy()

    def opensteam(self, event):
        dialog = wx.DirDialog(self, '选择steam根目录', style=wx.DD_DEFAULT_STYLE)
        if dialog.ShowModal() == wx.ID_OK:
            self.steamPathCtrl.SetValue(dialog.GetPath())
            dialog.Destroy()

    def loadSkin(self, event):
        skinSrc = cv2.imread(self.skinPathCtrl.GetValue(), -1)
        height, width, channel = skinSrc.shape
        print(height, width, channel)

        self.radiobox1.Enable(True)
        self.isAlexflag = True
        self.isAlex(skinSrc)
        if self.isAlexflag:
            self.skinType = '纤细'
            self.radiobox1.SetSelection(0)
        else:
            self.skinType = '粗壮'
            self.radiobox1.SetSelection(1)

        if height == 32:
            self.hasDouble = '否'
            self.hasDoubleflag = False
        else:
            self.hasDoubleflag = True
            self.hasDouble = '是'

        if not self.hasDoubleflag:
            self.wantDouble = '否'
            self.keepDouble = False
            self.keppBtn.SetValue(False)
            self.keppBtn.Enable(False)
        else:
            self.wantDouble = '是'
            self.keepDouble = True
            self.keppBtn.SetValue(True)
            self.keppBtn.Enable(True)

        msgstr = '皮肤类型: %s' % self.skinType + '\r\n双层皮肤: %s' % self.hasDouble + '\r\n保留双层皮肤: %s' % self.wantDouble
        self.skinMsg.SetValue(msgstr)

        skinShow = skinSrc[0:32, 0:64]
        self.bigger(skinShow)

        self.radiobox2.Enable(True)

    def keepDo(self, event):
        self.keepDouble = self.keppBtn.GetValue()
        if self.keepDouble:
            self.wantDouble = '是'
        else:
            self.wantDouble = '否'
        msgstr = '皮肤类型: %s' % self.skinType + '\r\n双层皮肤: %s' % self.hasDouble + '\r\n保留双层皮肤: %s' % self.wantDouble
        self.skinMsg.SetValue(msgstr)

    def isAlex(self, skin):
        for y in range(16, 31):
            if not np.all(skin[y, 63] == np.array([0, 0, 0, 0])):
                self.isAlexflag = False

    def onchoosePos(self, event):
        if event.LeftIsDown():
            pos = event.GetPosition()
            x = int(pos[0] / 10)
            y = int(pos[1] / 10)
            print(x, y)
        elif event.RightIsDown():
            pos = event.GetPosition()
            x = int(pos[0] / 10)
            y = int(pos[1] / 10)
            print(x, y)

    def drawBorder(self, x1, y1, x2, y2):
        cv2.rectangle(self.imgTemp, (x1 * 10, y1 * 10), (x2 * 10 + 9, y2 * 10 + 9), (0, 0, 255, 255), 2)
        cv2.imwrite('temp.png', self.imgTemp)
        pic = wx.Image('temp.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        self.img.SetBitmap(pic)

    def bigger(self, src):
        width, height, channel = src.shape
        for x in range(width):
            for y in range(height):
                for i in range(10):
                    for j in range(10):
                        self.imgTemp[x * 10 + i, y * 10 + j] = src[x, y]
        cv2.imwrite('temp.png', self.imgTemp)

        pic = wx.Image('temp.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        self.img.SetBitmap(pic)


def doImg(skinSrc):
    skinL2D = np.zeros((64, 64, 4), np.uint8)

    width, height, channel = skinSrc.shape

    print(width, height, channel)

    for x in range(width):
        for y in range(height):
            print(skinSrc[x, y], end='')
            skinL2D[x, y] = skinSrc[x, y]
        print('\n')

    cv2.imwrite('temp.PNG', skinL2D)


if __name__ == '__main__':
    app = wx.App()
    frame = MainFeamr(parent=None, id=-1)
    frame.Show()
    app.MainLoop()
