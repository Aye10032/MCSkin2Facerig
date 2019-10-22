import cv2
import numpy as np
import wx
import os
import webbrowser


class MainFeamr(wx.Frame):
    def __init__(self, parent, id):
        wx.Frame.__init__(self, parent, id, 'MC皮肤FaceRig转换器@Aye10032', size=(720, 620),
                          style=wx.CAPTION | wx.MINIMIZE_BOX | wx.CLOSE_BOX | wx.SYSTEM_MENU)
        self.Center()

        self.skinSrc = None

        self.skinType = 'N\\A'
        self.hasDouble = 'N\\A'
        self.wantDouble = 'N\\A'
        self.msgstr = '皮肤类型: %s' % self.skinType + '\r\n双层皮肤: %s' % self.hasDouble + '\r\n保留双层皮肤: %s' % self.wantDouble

        self.isAlexflag = True
        self.hasDoubleflag = False
        self.keepDouble = False

        self.skinColor = (255, 255, 255, 255)
        self.leftEyePos = [9, 12, 9, 13]
        self.rightEyePos = [14, 12, 14, 13]
        self.mouthPos = [11, 15, 12, 15]

        self.panel = wx.Panel(self)

        font1 = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, '微软雅黑')

        self.skinLabel = wx.StaticText(self.panel, -1, '皮肤文件位置: ', (10, 17), (100, 20), wx.ALIGN_CENTER)
        self.skinLabel.SetFont(font1)

        self.skinPathCtrl = wx.TextCtrl(self.panel, -1, '', (120, 15), (470, 25))
        self.skinBtn = wx.Button(self.panel, -1, '...', (600, 15), (40, 25))
        self.skinBtn.Bind(wx.EVT_BUTTON, self.openskin)
        self.dlBtn = wx.Button(self.panel, -1, '🔗', (645, 15), (40, 25))
        self.dlBtn.Bind(wx.EVT_BUTTON,self.download)

        self.steamLabel = wx.StaticText(self.panel, -1, 'steam根目录: ', (10, 52), (100, 20), wx.ALIGN_CENTER)
        self.steamLabel.SetFont(font1)

        self.steamPathCtrl = wx.TextCtrl(self.panel, -1, '', (120, 50), (500, 25))
        self.steamBtn = wx.Button(self.panel, -1, '...', (630, 50), (40, 25))
        self.steamBtn.Bind(wx.EVT_BUTTON, self.opensteam)

        wx.StaticText(self.panel, -1, '——————————————————————————————————————————————————————————————————',
                      (0, 85)).SetForegroundColour('gray')

        self.imgTemp = np.zeros((320, 640, 4), np.uint8)
        alphaChannel = cv2.split(self.imgTemp)[3]
        pic = wx.Bitmap.FromBufferAndAlpha(640, 320, self.imgTemp, alphaChannel)
        self.img = wx.StaticBitmap(self.panel, -1, pic, pos=(30, 110), size=(640, 320))
        # self.img.SetBackgroundColour((255, 255, 255))
        self.img.Bind(wx.EVT_LEFT_DOWN, self.onchoosePos)
        self.img.Bind(wx.EVT_RIGHT_DOWN, self.onchoosePos)

        self.loadBtn = wx.Button(self.panel, -1, '加载皮肤', (50, 440), (100, 25))
        self.loadBtn.Bind(wx.EVT_BUTTON, self.loadSkin)

        self.skinMsg = wx.TextCtrl(self.panel, -1, self.msgstr, (20, 480), (160, 70),
                                   style=wx.TE_MULTILINE | wx.NO_BORDER | wx.TE_READONLY)
        self.skinMsg.SetFont(font1)

        self.keppBtn = wx.CheckBox(self.panel, -1, '保留双层皮肤: ', (200, 450), style=wx.ALIGN_RIGHT)
        self.keppBtn.Bind(wx.EVT_CHECKBOX, self.keepDo)
        self.keppBtn.Enable(False)

        typeList = ['纤细', '粗壮']
        self.radiobox1 = wx.RadioBox(self.panel, -1, "皮肤类型", (200, 475), (110, 55), typeList, 2, wx.RA_SPECIFY_COLS)
        self.radiobox1.Enable(False)
        self.radiobox1.Bind(wx.EVT_RADIOBOX, self.AlexConfirm)

        posList = ['肤色', '左眼', '右眼', '嘴巴']
        self.radiobox2 = wx.RadioBox(self.panel, -1, "细节调整", (350, 440), (80, 130), posList, 4, wx.RA_SPECIFY_ROWS)
        self.radiobox2.Enable(False)
        self.radiobox2.Bind(wx.EVT_RADIOBOX, self.poschoose)

        self.startBtn = wx.Button(self.panel, -1, '开始', (215, 540), (80, 25))
        self.startBtn.Enable(False)
        self.startBtn.Bind(wx.EVT_BUTTON, self.start)

        self.posmsgBG = wx.StaticText(self.panel, -1, '', (480, 450), (180, 110))
        self.posmsgBG.SetBackgroundColour((0, 0, 0))
        self.posmsgFG = wx.StaticText(self.panel, -1, '', (481, 451), (178, 108))
        self.posmsgFG.SetBackgroundColour((255, 255, 255))

        self.posmsg = wx.TextCtrl(self.panel, -1, '', (483, 453), (174, 104),
                                  style=wx.TE_MULTILINE | wx.NO_BORDER | wx.TE_READONLY)

    def download(self,event):
        webbrowser.open('https://namemc.com/')

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
        if self.skinPathCtrl.GetValue() == '':
            dlg = wx.MessageDialog(None, '请选择皮肤文件！', '警告', wx.OK | wx.ICON_ERROR)
            if dlg.ShowModal() == wx.ID_OK:
                dlg.Destroy()
        elif self.steamPathCtrl.GetValue() == '':
            dlg = wx.MessageDialog(None, '请选择steam根目录！', '警告', wx.OK | wx.ICON_ERROR)
            if dlg.ShowModal() == wx.ID_OK:
                dlg.Destroy()
        elif not os.path.exists(
                self.steamPathCtrl.GetValue() + '\\steamapps\\common\\FaceRig\\Mod\\VP\\PC_CustomData\\Objects\\minecraft\\minecraft.2048'):
            dlg = wx.MessageDialog(None, '相关路径不存在，请检查是否安装了FaceRig及live2d DLC,同时订阅了创意工坊相关扩展。', '警告',
                                   wx.OK | wx.ICON_ERROR)
            if dlg.ShowModal() == wx.ID_OK:
                dlg.Destroy()
        else:
            self.skinSrc = cv2.imread(self.skinPathCtrl.GetValue(), -1)
            height, width, channel = self.skinSrc.shape
            print(height, width, channel)

            self.radiobox1.Enable(True)
            self.isAlexflag = True
            self.isAlex()
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

            self.skinSrc = self.skinSrc[0:32, 0:64]
            self.bigger(self.skinSrc)

            self.radiobox2.Enable(True)
            self.startBtn.Enable(True)

    def keepDo(self, event):
        self.keepDouble = self.keppBtn.GetValue()
        if self.keepDouble:
            self.wantDouble = '是'
        else:
            self.wantDouble = '否'
        msgstr = '皮肤类型: %s' % self.skinType + '\r\n双层皮肤: %s' % self.hasDouble + '\r\n保留双层皮肤: %s' % self.wantDouble
        self.skinMsg.SetValue(msgstr)

    def isAlex(self):
        for y in range(16, 31):
            if not np.all(self.skinSrc[y, 63] == np.array([0, 0, 0, 0])):
                self.isAlexflag = False

    def AlexConfirm(self, event):
        if self.radiobox1.GetSelection() == 0:
            self.isAlexflag = True
            self.skinType = '纤细'
        else:
            self.isAlexflag = False
            self.skinType = '粗壮'

        msgstr = '皮肤类型: %s' % self.skinType + '\r\n双层皮肤: %s' % self.hasDouble + '\r\n保留双层皮肤: %s' % self.wantDouble
        self.skinMsg.SetValue(msgstr)

    def poschoose(self, event):
        if self.radiobox2.GetSelection() == 1:
            self.drawBorder(self.leftEyePos[0], self.leftEyePos[1], self.leftEyePos[2], self.leftEyePos[3])
        elif self.radiobox2.GetSelection() == 2:
            self.drawBorder(self.rightEyePos[0], self.rightEyePos[1], self.rightEyePos[2], self.rightEyePos[3])
        elif self.radiobox2.GetSelection() == 3:
            self.drawBorder(self.mouthPos[0], self.mouthPos[1], self.mouthPos[2], self.mouthPos[3])

    def onchoosePos(self, event):
        pos = event.GetPosition()
        x = int(pos[0] / 10)
        y = int(pos[1] / 10)
        str = self.posmsg.GetValue()
        if self.radiobox2.GetSelection() == 0:
            self.skinColor = self.skinSrc[y, x]
            print(self.skinColor)
            self.drawBorder(x, y, x, y)
            str = str + '已选择像素(%d' % x + ',%d' % y + ')为皮肤颜色\r\n值为:(%d' % self.skinSrc[y, x][0] + ',%d' % \
                  self.skinSrc[y, x][1] + ',%d' % self.skinSrc[y, x][2] + ',%d' % self.skinSrc[y, x][3] + ')\r\n'
        elif self.radiobox2.GetSelection() == 1:
            if event.LeftIsDown():
                self.leftEyePos[0] = x
                self.leftEyePos[1] = y
                str = str + '已选择第一点:(%d' % x + ',%d' % y + ')\r\n'
            elif event.RightIsDown():
                self.leftEyePos[2] = x
                self.leftEyePos[3] = y
                str = str + '已选择第二点:(%d' % x + ',%d' % y + ')\r\n'
            self.drawBorder(self.leftEyePos[0], self.leftEyePos[1], self.leftEyePos[2], self.leftEyePos[3])
        elif self.radiobox2.GetSelection() == 2:
            if event.LeftIsDown():
                self.rightEyePos[0] = x
                self.rightEyePos[1] = y
                str = str + '已选择第一点:(%d' % x + ',%d' % y + ')\r\n'
            elif event.RightIsDown():
                self.rightEyePos[2] = x
                self.rightEyePos[3] = y
                str = str + '已选择第二点:(%d' % x + ',%d' % y + ')\r\n'
            self.drawBorder(self.rightEyePos[0], self.rightEyePos[1], self.rightEyePos[2], self.rightEyePos[3])
        elif self.radiobox2.GetSelection() == 3:
            if event.LeftIsDown():
                self.mouthPos[0] = x
                self.mouthPos[1] = y
                str = str + '已选择第一点:(%d' % x + ',%d' % y + ')\r\n'
            elif event.RightIsDown():
                self.mouthPos[2] = x
                self.mouthPos[3] = y
                str = str + '已选择第二点:(%d' % x + ',%d' % y + ')\r\n'
            self.drawBorder(self.mouthPos[0], self.mouthPos[1], self.mouthPos[2], self.mouthPos[3])
        self.posmsg.SetValue(str)
        self.posmsg.ShowPosition(self.posmsg.GetLastPosition())

    def start(self, event):
        # 旋转下颚
        print(self.skinSrc[0, 16])
        print(self.skinSrc[7, 23])
        temp = self.skinSrc[0:8, 16:24]
        print(temp.shape)
        temp = cv2.flip(temp, -1, dst=None)
        for x in range(8):
            for y in range(8):
                self.skinSrc[0 + y, 16 + x] = temp[y, x]

        # 左右眼
        # 初始化
        for x in range(8):
            for y in range(8):
                self.skinSrc[0 + y, 0 + x] = (0, 0, 0, 0)
                self.skinSrc[0 + y, 24 + x] = (0, 0, 0, 0)
                self.skinSrc[0 + y, 32 + x] = (0, 0, 0, 0)
                self.skinSrc[0 + y, 56 + x] = (0, 0, 0, 0)
                self.skinSrc[16 + y, 56 + x] = (0, 0, 0, 0)
                self.skinSrc[24 + y, 56 + x] = (0, 0, 0, 0)
        # 左眼50%
        x1 = self.leftEyePos[0] - 8
        y1 = self.leftEyePos[1] - 8
        w1 = self.leftEyePos[2] - self.leftEyePos[0] + 1
        h1 = int((self.leftEyePos[3] - self.leftEyePos[1]) / 2) + 1
        for x in range(x1, x1 + w1):
            for y in range(y1, y1 + h1):
                self.skinSrc[0 + y, 0 + x] = self.skinColor
        # 左眼100%
        x1 = self.leftEyePos[0] - 8
        y1 = self.leftEyePos[1] - 8
        w1 = self.leftEyePos[2] - self.leftEyePos[0] + 1
        h1 = (self.leftEyePos[3] - self.leftEyePos[1]) + 1
        for x in range(x1, x1 + w1):
            for y in range(y1, y1 + h1):
                self.skinSrc[0 + y, 24 + x] = self.skinColor
        # 右眼50%
        x1 = self.rightEyePos[0] - 8
        y1 = self.rightEyePos[1] - 8
        w1 = self.rightEyePos[2] - self.rightEyePos[0] + 1
        h1 = int((self.rightEyePos[3] - self.rightEyePos[1]) / 2) + 1
        for x in range(x1, x1 + w1):
            for y in range(y1, y1 + h1):
                self.skinSrc[0 + y, 32 + x] = self.skinColor
        # 左眼100%
        x1 = self.rightEyePos[0] - 8
        y1 = self.rightEyePos[1] - 8
        w1 = self.rightEyePos[2] - self.rightEyePos[0] + 1
        h1 = (self.rightEyePos[3] - self.rightEyePos[1]) + 1
        for x in range(x1, x1 + w1):
            for y in range(y1, y1 + h1):
                self.skinSrc[0 + y, 56 + x] = self.skinColor

        # 嘴50%
        x1 = self.mouthPos[0] - 8
        y1 = self.mouthPos[1] - 8
        w1 = self.mouthPos[2] - self.mouthPos[0] + 1
        if self.mouthPos[1] == self.mouthPos[3]:
            for x in range(x1, x1 + w1):
                self.skinSrc[16 + y1, 56 + x] = self.skinColor
                self.skinSrc[16 + y1, 56 + x][3] = 112
        else:
            h1 = int((self.mouthPos[3] - self.mouthPos[1]) / 2) + 1
            for x in range(x1, x1 + w1):
                for y in range(y1, y1 + h1):
                    self.skinSrc[16 + y, 56 + x] = self.skinColor

        # 嘴100%
        x1 = self.mouthPos[0] - 8
        y1 = self.mouthPos[1] - 8
        w1 = self.mouthPos[2] - self.mouthPos[0] + 1
        h1 = (self.mouthPos[3] - self.mouthPos[1]) + 1
        for x in range(x1, x1 + w1):
            for y in range(y1, y1 + h1):
                self.skinSrc[24 + y, 56 + x] = self.skinColor

        self.bigger(self.skinSrc)
        self.output()

    def drawBorder(self, x1, y1, x2, y2):
        imgsrc = cv2.imread('bigger.png', -1)
        cv2.rectangle(imgsrc, (x1 * 10, y1 * 10), (x2 * 10 + 9, y2 * 10 + 9), (0, 0, 255, 255), 2)
        cv2.imwrite('temp.png', imgsrc)
        pic = wx.Image('temp.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        self.img.SetBitmap(pic)

    def bigger(self, src):
        width, height, channel = src.shape
        for x in range(width):
            for y in range(height):
                for i in range(10):
                    for j in range(10):
                        self.imgTemp[x * 10 + i, y * 10 + j] = src[x, y]
        cv2.imwrite('bigger.png', self.imgTemp)

        pic = wx.Image('bigger.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        self.img.SetBitmap(pic)

    def output(self):
        width, height, channel = self.skinSrc.shape
        imgTemp = np.zeros((1600, 1600, 4), np.uint8)
        for x in range(width):
            for y in range(height):
                for i in range(25):
                    for j in range(25):
                        imgTemp[x * 25 + i, y * 25 + j] = self.skinSrc[x, y]
        imgFinal = np.zeros((2048, 2048, 4), np.uint8)
        width, height, channel = imgTemp.shape
        for x in range(width):
            for y in range(height):
                imgFinal[x, y] = imgTemp[x, y]

        path = self.steamPathCtrl.GetValue() + '\\steamapps\\common\\FaceRig\\Mod\\VP\\PC_CustomData\\Objects\\minecraft\\minecraft.2048\\texture_00.png'
        print(os.path.exists(path))
        cv2.imwrite(path, imgFinal)
        if os.path.exists('temp.png'):
            os.remove('temp.png')
        if os.path.exists('bigger.png'):
            os.remove('bigger.png')
        strtemp = self.posmsg.GetValue() + '完成\r\n'
        self.posmsg.SetValue(strtemp)
        self.posmsg.ShowPosition(self.posmsg.GetLastPosition())


if __name__ == '__main__':
    app = wx.App()
    frame = MainFeamr(parent=None, id=-1)
    frame.Show()
    app.MainLoop()
