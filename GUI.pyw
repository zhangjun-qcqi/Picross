# coding: utf-8
import wx
from Picross import Picross
from string import hexdigits
from winsound import Beep

class Frame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self,None,title = "Picross",size = (1024,768))
        self.canvas = Canvas(self)
        self.Show()

class Canvas(wx.Window):
    BG = (30,30,30)
    LINE = (127,127,127)
    TEXT = (192,192,192)
    SLINE = (255,128,64)
    NEW = (255,128,192)
    SEL = (20,72,82)
    HINT = (86,156,214)
    ILLEGAL = (255,0,0)

    CELL = 32
    FTSIZE = CELL*3/4
    FTFACE = "FixedSys Excelsior 3.01"

    lookup = {Picross.empty:u'✕', Picross.box:u'█', Picross.init:''}
    left = {Picross.empty:Picross.box,
              Picross.box:Picross.init, Picross.init:Picross.box}
    right = {Picross.empty:Picross.init,
              Picross.box:Picross.empty, Picross.init:Picross.empty}
    hint = {Picross.NORMAL:TEXT, Picross.HINT:HINT, Picross.ILLEGAL:ILLEGAL}
    NONE,GRID,BARS = range(3)

    def __init__(self,parent):
        wx.Window.__init__(self,parent, style = wx.FULL_REPAINT_ON_RESIZE)
        self.SetDoubleBuffered(True)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouse)
        self.Bind(wx.EVT_CHAR, self.OnPress)
        self.picross = Picross(15, 15)
        self.sel, self.bsel = Canvas.BARS, 0
        self.isel,self.jsel = -1,-1
        self.new = []

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        dc.SetBackground(wx.Brush(Canvas.BG))
        dc.Clear()

        R,C = self.picross.RC
        width, height = self.GetSize()

        dc.SetPen(wx.Pen(Canvas.SEL))
        dc.SetBrush(wx.Brush(Canvas.SEL,))
        if self.sel == Canvas.BARS:
            if self.bsel < R:
                dc.DrawRectangle(C*Canvas.CELL, self.bsel*Canvas.CELL,
                                 width, Canvas.CELL)
            else:
                dc.DrawRectangle((self.bsel-R)*Canvas.CELL, R*Canvas.CELL,
                                 Canvas.CELL, height)

        for i in range(R+1):# draw horizontal bars
            pen = Canvas.SLINE if i % 5 == 0 else Canvas.LINE
            dc.SetPen(wx.Pen(pen))
            dc.DrawLine(0,Canvas.CELL*i,C * Canvas.CELL+1,Canvas.CELL*i)
        for j in range(C+1):# draw vertical bars
            pen = Canvas.SLINE if j % 5 == 0 else Canvas.LINE
            dc.SetPen(wx.Pen(pen))
            dc.DrawLine(Canvas.CELL*j,0,Canvas.CELL*j,R * Canvas.CELL+1)

        def DrawCell(i,j,c):
            dc.DrawText(Canvas.lookup[c],j*Canvas.CELL,i*Canvas.CELL)

        dc.SetFont(wx.Font(Canvas.FTSIZE, wx.DEFAULT,wx.NORMAL, wx.NORMAL))
        dc.SetTextForeground(Canvas.TEXT)
        for (i,j),c in self.picross.enumerate():
            DrawCell(i,j,c)
        dc.SetTextForeground(Canvas.NEW)
        for (i,j),c in self.new:
            DrawCell(i,j,c)
        self.new = []

        def DrawHint(i,j,bar):
            if bar >= 10:
                dc.DrawText(str(bar),j*Canvas.CELL,i*Canvas.CELL)
            else:
                dc.DrawText(str(bar),(j+0.25)*Canvas.CELL,i*Canvas.CELL)

        dc.SetFont(wx.Font(Canvas.FTSIZE, wx.DEFAULT,wx.NORMAL, wx.NORMAL,
                           face = Canvas.FTFACE))
        dc.SetTextForeground(Canvas.TEXT)
        for i, bars in enumerate(self.picross.Bars):
            dc.SetTextForeground(Canvas.hint[self.picross.Common(i)[0]])
            if i < R:
                for j, bar in enumerate(bars):
                    DrawHint(i,j+C, bar)
            else:
                for j, bar in enumerate(bars):
                    DrawHint(j+R,i-R, bar)

    def OnMouse(self, event):
        type = event.GetEventType()
        if type in {wx.EVT_MOTION.typeId,
                    wx.EVT_LEFT_DOWN.typeId,wx.EVT_RIGHT_DOWN.typeId}:
            if event.LeftIsDown():
                clickto = self.left
                if type == wx.EVT_LEFT_DOWN.typeId:
                    event.Skip()
            elif event.RightIsDown():
                clickto = self.right
            else:
                return
            self.iold,self.jold = self.isel,self.jsel
            x,y = event.GetPositionTuple()
            self.isel,self.jsel = y//self.CELL, x//self.CELL
            if (type == wx.EVT_MOTION.typeId and self.isel == self.iold
                and self.jsel == self.jold):
                return
            R,C = self.picross.RC
            if self.isel < R:
                if self.jsel < C:
                    self.sel = Canvas.GRID
                    self.picross.Grid[self.isel,self.jsel] = clickto[
                        self.picross.Grid[self.isel,self.jsel]]
                    self.picross.Screen(self.isel)
                    self.picross.Screen(self.jsel+R)
                else:
                    self.sel = Canvas.BARS
                    self.bsel = self.isel
            else:
                if self.jsel < C:
                    self.sel = Canvas.BARS
                    self.bsel = self.jsel+R
                else:
                    self.sel = Canvas.NONE
            self.Refresh()
        elif type == wx.EVT_MOUSEWHEEL.typeId:
            if event.GetWheelRotation() < 0:
                self.new = self.picross.Next()
                if self.new:
                    self.Refresh()
                else:
                    Beep(1000,100)

    def OnPress(self, event):
        c = event.GetKeyCode()
        if self.sel == Canvas.BARS:
            bars = self.picross.Bars[self.bsel]
            if c == wx.WXK_RETURN:
                self.bsel += 1
                if self.bsel >= sum(self.picross.RC):
                    self.sel = Canvas.NONE,
            elif c < 256 and chr(c) in set(hexdigits):
                bars.append(int(chr(c),16))
                self.picross.Candid(self.bsel)
                self.picross.Screen(self.bsel)
            elif c == wx.WXK_BACK and bars:
                bars.pop()
                self.picross.Candid(self.bsel)
                self.picross.Screen(self.bsel)
            else:
                return
            self.Refresh()

app = wx.App(False)
frame = Frame()
app.MainLoop()
