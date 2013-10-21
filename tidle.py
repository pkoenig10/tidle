# -*- coding: utf-8 -*-

# Patrick Kooenig
# TIDLE: TI-BASIC Editor

from Tkinter import *
from tkFileDialog import *
from tkFont import *
from tkColorChooser import *
import tkMessageBox
from collections import *
import string
import os
import datetime
import webbrowser
from math import *
from fractions import gcd
from random import *

class Stop(Exception): pass

class Editor(object):   
    def __init__(self, commandColor='#0066FF', stringColor = '#FF0055', syntaxColoring=True):
        self.root = Tk()
        # set the program title and icon
        self.programTitle = "TIDLE: TI-BASIC Editor"
        self.programIcon = 'icon.ico'
        # create the commands
        self.createCommands()
        # create the interpret code
        self.createInterpretCode()
        # set the file values
        self.defaultExtension = '.8xp'
        self.fileTypes = [("All Files", '.*'), ("TI-83+ Program Files", '.8xp')]
        self.fileName = "Untitled"
        self.isFileModified = 0
        # create the Tkinter variables
        self.createVariables(commandColor, stringColor, syntaxColoring)
        # create the editor window
        self.createWindow()

    def run(self):
        # set up events
        self.text.bind('<ButtonRelease-1>', self.textLeftMouseReleased)        
        self.text.bind('<Button-3>', self.textRightMousePressed)
        self.root.bind('<KeyPress>', self.keyPress)
        self.root.bind('<KeyRelease>', self.keyReleased)
        self.root.bind('<Control-n>', lambda(event): self.newFile())
        self.root.bind('<Control-o>', lambda(event): self.openFile())
        self.root.bind('<Control-s>', lambda(event): self.saveFile())
        self.root.bind('<Control-q>', lambda(event): self.exitFile())
        self.root.bind('<Control-a>', lambda(event): self.selectAll())
        self.root.bind('<Control-f>', lambda(event): self.find())
        self.root.bind('<Control-h>', lambda(event): self.replace())
        self.root.bind('<F3>', lambda(event): self.findNext())
        self.root.bind('<F5>', lambda(event): self.interpretFile())
        self.root.protocol('WM_DELETE_WINDOW', self.exitFile)
        self.findDialog.protocol('WM_DELETE_WINDOW', self.findDialog.cancel)
        self.findDialog.bind('<Return>', lambda(event): self.findDialog.findNext(self))
        self.replaceDialog.protocol('WM_DELETE_WINDOW', self.replaceDialog.cancel)
        self.replaceDialog.bind('<Return>', lambda(event): self.replaceDialog.replaceNext(Self))
        # launch the program
        self.root.mainloop()

    def textLeftMouseReleased(self, event):
        self.text.tag_delete('find') # delete the find tag
        self.updateWindow() # update the window
        
    def textRightMousePressed(self, event):
        self.text.tag_delete('find') # delete the find tag
        self.updateWindow() # update the window
        self.contextMenu.post(event.x_root, event.y_root) # display the context menu

    def keyPress(self, event):
        self.text.tag_delete('find') # delete the find tag
        
    def keyReleased(self, event):
        self.updateWindow() # update the window

    def createCommands(self):
        # create the command dictionaries
        self.keypad = OrderedDict([(u"⁻", (0xB0,)), (u"→", (0x04,)), (u"θ", (0x5B,)), (u"√(", (0xBC,)),
                                   (u"π", (0xAC,)), (u"²", (0x0D,)), (u"⁻¹", (0x0C,)), (u"ᴇ", (0x3B,)),
                                   ("sin(", (0xC2,)), ("cos(", (0xC4,)), ("tan(", (0xC6,)), (u"sin⁻¹(", (0xC3,)),
                                   (u"cos⁻¹(", (0xC5,)), (u"tan⁻¹(", (0xC7,)), ("log(", (0xC0,)), ("ln(", (0xBE,)),
                                   ("10^(", (0xC1,)), ("e^(", (0xBF,)), ("u", (0x5E, 0x80)), ("v", (0x5E, 0x81)),
                                   ("w", (0x5E, 0x82)), ("e", (0xBB, 0x31)), ("i", (0x2C,)), ("Ans", (0x72,)),
                                   ("Trace", (0x84,))])
        self.angle = OrderedDict([(u"°", (0x0B,)), ("'", (0xAE,)), (u"ʳ", (0x0A,)), (u"►DMS", (0x01,)),
                                  (u"R►Pr(", (0x1B,)), (u"R►Pθ(", (0x1C,)), (u"P►Rx(", (0x1D,)), (u"P►Ry", (0x1E,))])
        self.drawDraw = OrderedDict([("ClrDraw", (0x85,)), ("Line(", (0x9C,)), ("Horizontal ", (0xA6,)), ("Vertical ", (0x9D,)),
                                     ("Tangent(", (0xA7,)), ("DrawF ", (0xA9,)), ("Shade(", (0xA4,)), ("DrawInv ", (0xA8,)),
                                     ("Circle(", (0xA5,)), ("Text(", (0x93,))])
        self.drawPoints = OrderedDict([("Pt-On(", (0x9E,)), ("Pt-Off(", (0x9F,)), ("Pt-Change(", (0xA0,)), ("Pxl-On(", (0xA1,)),
                                       ("Pxl-Off(", (0xA2,)), ("Pxl-Change(", (0xA3,)), ("pxl-Test(", (0x13,))])
        self.drawSto = OrderedDict([("StorePic", (0x98,)), ("RecallPic", (0x99,)), ("StoreGDB", (0x9A,)), ("RecallGDB", (0x9B,))])
        self.draw = OrderedDict([("Draw", self.drawDraw), ("Points", self.drawPoints), ("Sto", self.drawSto)])
        self.format = OrderedDict([("RectGC", (0x7E, 0x03)), ("PolarGC", (0x7E, 0x02)), ("CoordOn", (0x7E, 0x04)),
                                   ("CoordOff", (0x7E, 0x05)), ("GridOn", (0x7E, 0x0A)), ("GridOff", (0x7E, 0x0B)),
                                   ("AxesOn", (0x7E, 0x08)), ("AxesOff", (0x7E, 0x09)),  ("LabelOn", (0x7E, 0x0C)),
                                   ("LabelOff", (0x7E, 0x0D)), ("ExprOn", (0xBB, 0x50)), ("ExprOff", (0xBB, 0x51)),
                                   ("Time", (0x7E, 0x0F)), ("Web", (0x7E, 0x0E)), ("uvAxes", (0x7E, 0x10)), ("vwAxes", (0x7E, 0x11)),
                                   ("uwAxes", (0x7E, 0x12)),("PlotsOn", (0xE9,)), ("PlotsOff", (0xEA,))])
        self.hyperbolic = OrderedDict([(u"sinh(", (0xC8,)), (u"cosh(", (0xCA,)), (u"tanh(", (0xCC,)),
                                       (u"sinh⁻¹(", (0xC9,)), (u"cosh⁻¹(", (0xCB,)), (u"tanh⁻¹(", (0xCD,))])
        self.listNames = OrderedDict([(u"∟1", (0x5D, 0x00)), (u"∟2", (0x5D, 0x01)), (u"∟3", (0x5D, 0x02)),
                                      (u"∟4", (0x5D, 0x03)), (u"∟5", (0x5D, 0x04)), (u"∟6", (0x5D, 0x05))])
        self.listOps = OrderedDict([("SortA(", (0xE3,)), ("SortD(", (0xE4,)), ("dim(", (0xB5,)), ("Fill(", (0xE2,)),
                                    ("seq(", (0x23,)), ("cumSum(", (0xBB, 0x29)), (u"ΔList(", (0xBB, 0x2C)), ("augment(", (0x14,)),
                                    (u"List►matr(", (0xBB, 0x3A)), (u"Matr►list(", (0xBB, 0x39)), (u"∟", (0xEB,))])
        self.listMath = OrderedDict([("min(", (0x1A,)), ("max(", (0x19,)), ("mean(", (0x21,)), ("median(", (0x1F,)),
                                     ("sum(", (0xB6,)), ("prod(", (0xB7,)), ("stdDev(", (0xBB, 0x0D)), ("variance(", (0xBB, 0x0E))])
        self.list = OrderedDict([("Names", self.listNames), ("Ops", self.listOps), ("Math", self.listMath)])
        self.mathMath = OrderedDict([(u"►Frac", (0x03,)), (u"►Dec", (0x02,)), (u"³", (0x0F,)), (u"³√(", (0xBD,)),
                                    (u"ˣ√(", (0xF1,)), ("fMin(", (0x27,)), ("fMax(", (0x28,)), ("nDeriv(", (0x25,)),
                                    ("fnInt(", (0x24,)), ("solve(", (0x22,))])
        self.mathNum = OrderedDict([("abs(", (0xB2,)), ("round(", (0x12,)), ("iPart(", (0xB9,)), ("fPart(", (0xBA,)),
                                    ("int(", (0xB1,)), ("min(", (0x1A,)), ("max(", (0x19,)), ("lcm(", (0xBB, 0x08)),
                                    ("gcd(", (0xBB, 0x09))])
        self.mathCpx = OrderedDict([("conj(", (0xBB, 0x25)), ("real(", (0xBB, 0x26)), ("imag(", (0xBB, 0x27)), ("angle(", (0xBB, 0x28)),
                                    ("abs(", (0xB2,)), (u"►Rect", (0xBB, 0x2F)), (u"►Polar", (0xBB, 0x30))])
        self.mathPrb = OrderedDict([("rand", (0xAB,)), (" nPr ", (0x94,)), (" nCr ", (0x95,)), ("!", (0x2D,)),
                                    ("randInt(", (0xBB, 0x0A)), ("randNorm(", (0xBB, 0x1F)), ("randBin(", (0xBB, 0x0B))])
        self.math = OrderedDict([("Math", self.mathMath), ("Num", self.mathNum), ("Cpx", self.mathCpx), ("Prb", self.mathPrb)])
        self.matrixNames = OrderedDict([("[A]", (0x5C, 0x00)), ("[B]", (0x5C, 0x01)), ("[C]", (0x5C, 0x02)), ("[D]", (0x5C, 0x03)),
                                        ("[E]", (0x5C, 0x04)), ("[F]", (0x5C, 0x05)), ("[G]", (0x5C, 0x06)), ("[H]", (0x5C, 0x07)),
                                        ("[I]", (0x5C, 0x08)), ("[J]", (0x5C, 0x09))])
        self.matrixMath = OrderedDict([("det(", (0xB3,)), (u"ᵀ", (0x0E,)), ("dim(", (0xB5,)), ("Fill(", (0xE2,)), ("identity(", (0xB4,)),
                                       ("randM(", (0x20,)), ("augment(", (0x14,)), (u"Matr►list(", (0xBB, 0x39)), (u"List►matr(", (0xBB, 0x3A)),
                                       ("cumSum(", (0xBB, 0x29)), ("rowSwap(", (0x15,)), ("ref(", (0xBB, 0x2D)), ("rref(", (0xBB, 0x2E)), 
                                       ("row+(", (0x16,)), ("*row(", (0x17,)), ("*row+(", (0x18,))])
        self.matrix = OrderedDict([("Names", self.matrixNames), ("Math", self.matrixMath)])
        self.memory = OrderedDict([("Archive", (0xBB, 0x68)), ("UnArchive", (0xBB, 0x69)), ("GarbageCollect", (0xBB, 0xCE)),
                                   ("Clear Entries", (0xBB, 0x57)), ("ClrAllLists", (0xBB, 0x52))]) 
        self.mode = OrderedDict([("Normal", (0x66,)), ("Sci", (0x67,)), ("Eng", (0x68,)), ("Float", (0x69,)),
                                 ("Fix", (0x73,)), ("Radian", (0x64,)), ("Degree", (0x65,)), ("Func", (0x76,)),
                                 ("Param", (0x77,)), ("Polar", (0x78,)), ("Seq", (0x79,)), ("Connected", (0x7E, 0x06)),
                                 ("Dot", (0x7E, 0x07)), ("Sequential", (0x7E, 0x00)), ("Simul", (0x7E, 0x01)),
                                 ("Real", (0xBB, 0x4D)), ("a+bi", (0xBB, 0x4F)), (u"re^θi", (0xBB, 0x4E)), ("Full", (0x75,)),
                                 ("Horiz", (0x74,)), ("G-T", (0xBB, 0x64)),("DiagnosticOn", (0xBB, 0x66)), ("DiagnosticOff", (0xBB, 0x67))])
        self.prgmCtl = OrderedDict([("If ", (0xCE,)), ("Then", (0xCF,)), ("Else", (0xD0,)), ("For(", (0xD3,)),
                                    ("While ", (0xD1,)), ("Repeat ", (0xD2,)), ("End", (0xD4,)), ("Pause ", (0xD8,)),
                                    ("Lbl ", (0xD6,)), ("Goto ", (0xD7,)), ("IS>(", (0xDA,)), ("DS<(", (0xDB,)),
                                    ("Menu(", (0xE6,)), ("prgm", (0x5F,)), ("Return", (0xD5,)), ("Stop", (0xD9,)),
                                    ("DelVar ", (0xBB, 0x54)), ("GraphStyle(", (0xBB, 0x45))])
        self.prgmIO = OrderedDict([("Input ", (0xDC,)), ("Prompt ", (0xDD,)), ("Disp ", (0xDE,)), ("DispGraph", (0xDF,)),
                                   ("DispTable", (0xE5,)), ("Output(", (0xE0,)), ("getKey", (0xAD,)), ("ClrHome", (0xE1,)),
                                   ("ClrTable", (0xFB,)), ("GetCalc(", (0xBB, 0x53)), ("Get(", (0xE8,)), ("Send(", (0xE7,))])
        self.prgm = OrderedDict([("Ctl", self.prgmCtl), ("I/O", self.prgmIO)])
        self.statEdit = OrderedDict([("ClrList", (0xFA,)), ("SetUpEditor", (0xBB, 0x4A))])
        self.statCalc = OrderedDict([("1-Var Stats ",(0xF2,)), ("2-Var Stats ",(0xF3,)), ("Med-Med",(0xF8,)),
                                     ("LinReg(ax+b) ",(0xFF,)), ("QuadReg ",(0xF9,)), ("CubicReg ",(0x2E,)),
                                     ("QuartReg  ",(0x2F,)), ("LinReg(a+bx) ",(0xF4,)), ("LnReg ",(0xF6,)),
                                     ("ExpReg ",(0xF5,)), ("PwrReg ",(0xF7,)), ("Logistic ", (0xBB, 0x33)),
                                     ("SinReg ", (0xBB, 0x32))])
        self.stat = OrderedDict([("Edit", self.statEdit), ("Calc", self.statCalc)])
        self.string = OrderedDict([("expr(", (0xBB, 0x2A)), ("inString(", (0xBB, 0x0F)), ("length(", (0xBB, 0x2B)),
                                   ("sub(", (0xBB, 0x0C)), (u"Equ►String(", (0xBB, 0x55)), (u"String►Equ(", (0xBB, 0x56))])
        self.tblSet  = OrderedDict([("IndpntAuto", (0x7A,)), ("IndpntAsk", (0x7B,)), ("DependAuto", (0x7C,)),
                                    ("DependAsk", (0x7D,))]) 
        self.testTest = OrderedDict([("=", (0x6A,)), (u"≠", (0x6F,)), (">", (0x6C,)), (u"≥", (0x6E,)),
                                     ("<", (0x6B,)), (u"≤", (0x6D,))])
        self.testLogic = OrderedDict([(" and ", (0x40,)), (" or ", (0x3C,)), (" xor ", (0x3D,)), ("not(", (0xB8,))])
        self.test = OrderedDict([("Test", self.testTest), ("Logic", self.testLogic)])
        self.time = OrderedDict([("ClockOn", (0xEF, 0x10)), ("ClockOff", (0xEF, 0x0F)), ("isClockOn", (0xEF, 0x0E)), ("startTmr", (0xEF, 0x0B)),
                                 ("checkTmr(", (0xEF, 0x02)), ("timeCnv(", (0xEF, 0x05)), ("dayOfWk(", (0xEF, 0x06)), ("dbd(", (0xBB, 0x07)),
                                 ("getDate", (0xEF, 0x09)), ("getDtFmt", (0xEF, 0x0C)), ("getDtStr(", (0xEF, 0x07)), ("getTime", (0xEF, 0x0A)),
                                 ("getTmFmt", (0xEF, 0x0D)), ("getTmStr(", (0xEF, 0x08)), ("setDate(", (0xEF, 0x00)), ("setDtFmt(", (0xEF, 0x03)),
                                 ("setTime(", (0xEF, 0x01)), ("setTmFmt(", (0xEF, 0x04))])
        self.varsVarsWindowXY = OrderedDict([("Xmin", (0x63, 0x0A)), ("Xmax", (0x63, 0x0B)), ("Xscl", (0x63, 0x02)), ("Ymin", (0x63, 0x0C)),
                                             ("Ymax", (0x63, 0x0D)), ("Yscl", (0x63, 0x03)), ("Xres", (0x63, 0x36)), (u"ΔX", (0x63, 0x26)),
                                             (u"ΔY", (0x63, 0x27)), ("XFact", (0x63, 0x28)), ("YFact", (0x63, 0x0C))])
        self.varsVarsWindowT = OrderedDict([("Tmin", (0x63, 0x0E)), ("Tmax", (0x63, 0x0F)), ("Tstep", (0x63, 0x22)),
                                             (u"θmin", (0x63, 0x10)), (u"θmax", (0x63, 0x11)), (u"θstep", (0x63, 0x23))])
        self.varsVarsWindowUVW = OrderedDict([("u(nMin)", (0x63, 0x04)), ("v(nMin)", (0x63, 0x05)), ("w(nMin)", (0x63, 0x32)), ("nMin", (0x63, 0x1F)),
                                              ("nMax", (0x63, 0x1D)), ("PlotStart", (0x63, 0x1B)), ("PlotStep", (0x63, 0x34))])
        self.varsVarsWindow = OrderedDict([("X/Y", self.varsVarsWindowXY), (u"T/θ", self.varsVarsWindowT), ("U/V/W", self.varsVarsWindowUVW)])
        self.varsVarsZoomZXZY = OrderedDict([("ZXmin", (0x63, 0x12)), ("ZXmax", (0x63, 0x13)), ("ZXscl", (0x63, 0x00)), ("ZYmin", (0x63, 0x14)),
                                             ("ZYmax", (0x63, 0x15)), ("ZYscl", (0x63, 0x01)), ("ZXres", (0x63, 0x37))])
        self.varsVarsZoomZT = OrderedDict([("ZTmin", (0x63, 0x18)), ("ZTmax", (0x63, 0x19)), ("ZTstep", (0x63, 0x24)),
                                             (u"Zθmin", (0x63, 0x16)), (u"Zθmax", (0x63, 0x17)), (u"Zθstep", (0x63, 0x25))])
        self.varsVarsZoomZU = OrderedDict([("Zu(nMin)", (0x63, 0x08)), ("Zv(nMin)", (0x63, 0x09)), ("Zw(nMin)", (0x63, 0x33)), ("ZnMin", (0x63, 0x20)),
                                           ("ZnMax", (0x63, 0x1E)), ("ZPlotStart", (0x63, 0x1C)), ("ZPlotStep", (0x63, 0x35))])
        self.varsVarsZoom = OrderedDict([("ZX/ZY", self.varsVarsZoomZXZY), (u"ZT/Zθ", self.varsVarsZoomZT), ("ZU", self.varsVarsZoomZU)])
        self.varsVarsGDB = OrderedDict([("GDB1", (0x61, 0x00)), ("GDB2", (0x61, 0x01)), ("GDB3", (0x61, 0x02)), ("GDB4", (0x61, 0x03)),
                                       ("GDB5", (0x61, 0x04)), ("GDB6", (0x61, 0x05)), ("GDB7", (0x61, 0x06)), ("GDB8", (0x61, 0x07)),
                                       ("GDB9", (0x61, 0x08)), ("GDB0", (0x61, 0x09))])
        self.varsVarsPicture = OrderedDict([("Pic1", (0x60, 0x00)), ("Pic2", (0x60, 0x01)), ("Pic3", (0x60, 0x02)), ("Pic4", (0x60, 0x03)),
                                            ("Pic5", (0x60, 0x04)), ("Pic6", (0x60, 0x05)), ("Pic7", (0x60, 0x06)), ("Pic8", (0x60, 0x07)),
                                            ("Pic9", (0x60, 0x08)), ("Pic0", (0x60, 0x09))])
        self.varsVarsStatisticsXY = OrderedDict([("n", (0x62, 0x02)), ("minX", (0x62, 0x08)), ("maxX", (0x62, 0x09)), ("minY", (0x62, 0x0A)),
                                                 ("minY", (0x62, 0x0B))])
        self.varsVarsStatisticsEQ = OrderedDict([("RegEQ", (0x62, 0x01)), ("a", (0x62, 0x16)), ("b", (0x62, 0x17)), ("c", (0x62, 0x18)),
                                                 ("d", (0x62, 0x19)), (u"е", (0x62, 0x1A)), ("r", (0x62, 0x12)), ("r²", (0x62, 0x35)),
                                                 ("R²", (0x62, 0x36))])
        self.varsVarsStatisticsPts = OrderedDict([(u"Q₁", (0x62, 0x14)), ("Med", (0x62, 0x13)), (u"Q₃", (0x62, 0x15))])
        self.varsVarsStatistics = OrderedDict([("XY", self.varsVarsStatisticsXY), ("EQ", self.varsVarsStatisticsEQ), ("Pts", self.varsVarsStatisticsPts)])
        self.varsVarsTable = OrderedDict([("TblStart", (0x63, 0x1A)), (u"ΔTbl", (0x63, 0x21)), ("TblInput", (0x63, 0x2A))])
        self.varsVarsString = OrderedDict([("Str1", (0xAA, 0x00)), ("Str2", (0xAA, 0x01)), ("Str3", (0xAA, 0x02)), ("Str4", (0xAA, 0x03)),
                                           ("Str5", (0xAA, 0x04)), ("Str6", (0xAA, 0x05)), ("Str7", (0xAA, 0x06)), ("Str8", (0xAA, 0x07)),
                                           ("Str9", (0xAA, 0x08)), ("Str0", (0xAA, 0x09))])
        self.varsVars = OrderedDict([("Window", self.varsVarsWindow), ("Zoom", self.varsVarsZoom), ("GDB", self.varsVarsGDB), ("Picture", self.varsVarsPicture),
                                     ("Statistics", self.varsVarsStatistics), ("Table", self.varsVarsTable), ("String", self.varsVarsString)])
        self.varsYVarsFunction = OrderedDict([(u"Y₁", (0x5E, 0x10)), (u"Y₂", (0x5E, 0x11)), (u"Y₃", (0x5E, 0x12)), (u"Y₄", (0x5E, 0x13)),
                                              (u"Y₅", (0x5E, 0x14)), (u"Y₆", (0x5E, 0x15)), (u"Y₇", (0x5E, 0x16)), (u"Y₈", (0x5E, 0x17)),
                                              (u"Y₉", (0x5E, 0x18)), (u"Y₀", (0x5E, 0x19))])
        self.varsYVarsParametric = OrderedDict([(u"X₁⊤", (0x5E, 0x20)), (u"Y₁⊤", (0x5E, 0x21)), (u"X₂⊤", (0x5E, 0x22)), (u"Y₂⊤", (0x5E, 0x23)),
                                                (u"X₃⊤", (0x5E, 0x24)), (u"Y₃⊤", (0x5E, 0x25)), (u"X₄⊤", (0x5E, 0x26)), (u"Y₄⊤", (0x5E, 0x27)),
                                                (u"X₅⊤", (0x5E, 0x28)), (u"Y₅⊤", (0x5E, 0x29)), (u"X₆⊤", (0x5E, 0x2A)), (u"Y₆⊤", (0x5E, 0x2B))])
        self.varsYVarsPolar = OrderedDict([(u"r₁ ", (0x5E, 0x40)), (u"r₂ ", (0x5E, 0x41)), (u"r₃ ", (0x5E, 0x42)),
                                           (u"r₄ ", (0x5E, 0x43)), (u"r₅ ", (0x5E, 0x44)), (u"r₆ ", (0x5E, 0x45))])
        self.varsYVarsOnOff = OrderedDict([("FnOn", (0x96,)), ("FnOff", (0x97,))])
        self.varsYVars = OrderedDict([("Function", self.varsYVarsFunction), ("Parametric", self.varsYVarsParametric),
                                      ("Polar", self.varsYVarsPolar), ("On/Off", self.varsYVarsOnOff)])
        self.vars = OrderedDict([("Vars", self.varsVars), ("Y-Vars", self.varsYVars)])
        self.zoomZoom = OrderedDict([("ZBox", (0x88,)), ("Zoom In", (0x89,)), ("Zoom Out", (0x8A,)), ("ZDecimal", (0x8E,)),
                                     ("ZSquare", (0x8B,)), ("ZStandard", (0x86,)), ("ZTrig", (0x87,)), ("ZInteger", (0x8C,)),
                                     ("ZoomStat", (0x8F,)), ("ZoomFit", (0xBB, 0x65))])
        self.zoomMemory = OrderedDict([("ZPrevious", (0x8D,)), ("ZoomSto", (0x92,)), ("ZoomRcl", (0x90,))])
        self.zoom = OrderedDict([("Zoom", self.zoomZoom), ("Memory", self.zoomMemory)])
        self.other = OrderedDict([("[", (0x06,)), ("]", (0x07,)), ("{", (0x08,)), ("}", (0x09,)), ("(", (0x10,)),
                          (")", (0x11,)), (" ", (0x29,)), ("\"", (0x2A,)), (",", (0x2B,)), ("0", (0x30,)),
                          ("1", (0x31,)), ("2", (0x32,)), ("3", (0x33,)), ("4", (0x34,)), ("5", (0x35,)),
                          ("6", (0x36,)), ("7", (0x37,)), ("8", (0x38,)), ("9", (0x39,)), (".", (0x3A,)),
                          (":", (0x3E,)), ("\n", (0x3F,)), ("A", (0x41,)), ("B", (0x42,)), ("C", (0x43,)),
                          ("D", (0x44,)), ("E", (0x45,)), ("F", (0x46,)), ("G", (0x47,)), ("H", (0x48,)),
                          ("I", (0x49,)), ("J", (0x4A,)), ("K", (0x4B,)), ("L", (0x4C,)), ("M", (0x4D,)),
                          ("N", (0x4E,)), ("O", (0x4F,)), ("P", (0x50,)), ("Q", (0x51,)), ("R", (0x52,)),
                          ("S", (0x53,)), ("T", (0x54,)), ("U", (0x55,)), ("V", (0x56,)), ("W", (0x57,)),
                          ("X", (0x58,)), ("Y", (0x59,)), ("Z", (0x5A,)), ("=", (0x6A,)), ("<", (0x6B,)),
                          (">", (0x6C,)), ("+", (0x70,)), ("-", (0x71,)), ("*", (0x82,)), ("/", (0x83,)),
                          ("'", (0xAE,)), ("?", (0xAF,)), ("^", (0xF0,))])
        self.commandsMenu = OrderedDict([("Keypad", self.keypad), ("Angle", self.angle), ("Draw", self.draw),
                                         ("Format", self.format), ("Hyperbolic", self.hyperbolic), ("List", self.list),
                                         ("Math", self.math), ("Matrix", self.matrix), ("Memory", self.memory),
                                         ("Mode", self.mode), ("Prgm", self.prgm), ("Stat", self.stat),
                                         ("String", self.string), ("Tbl Set", self.tblSet), ("Test", self.test),
                                         ("Time", self.time), ("Vars", self.vars), ("Zoom", self.zoom)])
        # create the command dictionary
        self.commands = dict()
        self.createCommandDictionary(dict(self.commandsMenu.items() + self.other.items()))
        # create the reverse command dictionary
        self.revCommands = {value:command for command, value in self.commands.iteritems()}
        # create the list of colored commands
        self.coloredCommands = ["If ", "Then", "Else", "For(", "While ", "Repeat ", "End", "Pause ", "Lbl ", "Goto ", "IS>(",
                                "DS<(", "Menu(", "prgm", "Return", "Stop", "Input ", "Prompt ", "Output(", "Disp ", "getKey",
                                " and ", " or ", " xor ", "not("]
        # create the interpret command dictionary
        self.interpretCommands = dict([("If ", self.interpretIf), ("Then", ""), ("Else", self.interpretElse), ("For(", self.interpretFor),
                                       ("While ", self.interpretWhile), ("Repeat ", self.interpretRepeat), ("End", self.interpretEnd),
                                       ("Pause ", "raw_input()"), ("Return", "raise Stop()"), ("Stop", "raise Stop()"), ("Input ", self.interpretInput),
                                       ("Prompt ", self.interpretPrompt), ("Disp ", "print "),
                                       (" and ", self.interpretAnd), (" or ", self.interpretOr), (" xor ", self.interpretXor), ("not(", "not("),
                                       (u"∟1", "L1"), (u"∟2", "L2"), (u"∟3", "L3"), (u"∟4", "L4"), (u"∟5", "L5"), (u"∟6", "L6"),
                                       (u"∟1(", self.interpretList), (u"∟2(", self.interpretList), (u"∟3(", self.interpretList),
                                       (u"∟4(", self.interpretList), (u"∟5(", self.interpretList), (u"∟6(", self.interpretList),
                                       ("SortA(", "sorted("), ("SortD(", "SortD("), ("dim(", "len("), ("Fill(", "fill("),
                                       ("cumSum(", "cumSum("), (u"ΔList(", "deltaList("), ("augment(", "augment("),
                                       ("min(", "calcMin("), ("max(", "calcMax("), ("mean(", "mean("), ("median(", "median("),
                                       ("sum(", "calcSum("), ("prod(", "prod("), ("stdDev(", "stdDev("), ("variance(", "variance("),
                                       (u"³", "**3"), (u"³√(", "cubeRoot("),
                                       ("abs(", "abs("), ("round(", "calcRound("), ("iPart(", "int("), ("fPart(", "fPart("),
                                       ("int(", "floor("), ("lcm(", "lcm("), ("gcd(", "gcd("),
                                       ("rand", "random()"), ("randInt(", "randint("),
                                       (u"⁻", "-"), (u"→", self.interpretAssign), (u"θ", "theta"), (u"√(", "sqrt("),
                                       (u"π", "pi"), (u"²", "**2"), (u"⁻¹", "**-1"), (u"ᴇ", "*10**"), ("sin(", "sin("),
                                       ("cos(", "cos("), ("tan(", "tan("), ("sin⁻¹(", "asin("), ("cos⁻¹(", "acos("),
                                       ("tan⁻¹(", "atan("), ("log(", "log10("), ("ln(", "log("), ("10^(", "10**("),
                                       ("e^(", "e**("), ("e", "e"), ("sinh(", "sinh("), ("cosh(", "cosh("),
                                       ("tanh(", "tanh("), ("sinh⁻¹(", "asinh("), ("cosh⁻¹(", "acosh("), ("tanh⁻¹(", "atanh("),
                                       ("=", "=="), (u"≠", "!="), (">", ">"), (u"≥", ">="), ("<", "<"), (u"≤", "<="),
                                       ("[", "["), ("]", "]"), ("{", "["), ("}", "]"), ("(", "("), (")", ")"),
                                       (" ", " "), ("\"", "\""), (",", ","), (".", "."), (":", ":"),
                                       ("+", "+"), ("-", "-"), ("*", "*"), ("/", "/"),
                                       ("'", "'"), ("?", "?"), ("^", "**")])

    def createCommandDictionary(self, dictionary):
        # create the command dictionary
        for command, value in dictionary.iteritems():
            # if the value is a command
            if type(value) == tuple:
                # add the command to the command dictionary
                self.commands[command] = value
            # add the commands of the subdictionary to the command dictionary
            else:
                self.createCommandDictionary(value)

    def createInterpretCode(self):
        # create the interpreter code
        self.interpretCode = """from math import *
from fractions import gcd
from random import *

A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W, X, Y, Z = tuple([0] * 26)
L1, L2, L3, L4, L5, L6 = tuple([[]] * 6)

def sortD(a):
    return sorted(a, reverse=True)
    
def fill(n, a):
    # fill a list with a number
    for i in xrange(len(a)): a[i] = n

def cumSum(a):
    # return the cumulative sum of a list
    cumSum = []
    for n in a: cumSum.append(sum(cumSum) + n)
    return cumSum

def deltaList(a):
    # return the change between elememts in a list
    deltaList = []
    for i in xrange(1, len(a)): deltaList.append(a[i] - a[i-1])
    return deltaList

def augment(a1, a2):
    # augments two lists
    return a1 + a2

def calcMin(a, b):
    # return the min of two lists or numbers
    if type(a) == type(b): return min(a, b)
    else:
        args = sorted([a, b])
        minList = []
        for n in args[1]: minList.append(min(n, args[0]))
        return minList

def calcMax(a, b):
    # return the max of two lists or numbers
    if type(a) == type(b): return max(a, b)
    else:
        args = sorted([a, b])
        maxList = []
        for n in args[1]: maxList.append(max(n, args[0]))
        return maxList

def mean(a):
    # return the mean of a list
    mean = float(sum(a)/len(a))
    if mean % 1 == 0: return int(mean)
    else: return mean

def median(a):
    # return the median of a list
    if len(a) % 2 == 0: return mean(a[len(a)/2-1:len(a)/2+1])
    else: return a[len(a)/2]

def calcSum(a, start=1, end=None):
    # return the sum of a list
    start -= 1
    if end == None: end = len(a)
    return sum(a[start: end])

def prod(a, start=1, end=None):
    # return the product of a list
    start -= 1
    if end == None: end = len(a)
    prod = 1
    for n in a: prod *= n
    return prod

def stdDev(a):
    # return the standard deviation of a list
    return variance(a)**0.5

def variance(a):
    # return the variance of a list
    avg = mean(a)
    variance = 0
    for n in a: variance += (n-avg)**2
    return 1.0/(len(a)-1)*variance

def cubeRoot(n):
    # return the cube root of a number
    return n**1.0/3

def calcRound(n, digits=0):
    # return the rounded value of a number
    return int(round(n, digits))

def fPart(n):
    # return the fractional part of a number
    return n-int(n)

def lcm(n, m):
    # return the lcm of two numbers
    return abs(n*m)/gcd(n, m)"""

    def createVariables(self, commandColor, stringColor, syntaxColoring):
        # create the Tkinter variables
        self.line = StringVar(self.root)
        self.col = StringVar(self.root)
        self.protected = IntVar(self.root, value=5)
        # set the defualt syntax colors
        self.syntaxColoring = BooleanVar(self.root, value=syntaxColoring)
        self.commandColor = StringVar(self.root, value=commandColor)
        self.stringColor = StringVar(self.root, value=stringColor)
        
    def createWindow(self):
        self.createTextWindow() # create the editor window
        self.createProgramBar() # create the program bar
        self.createStatusBar() # create the status bar
        self.createMenuBar() # create the menu bar
        self.createContextMenu() # create the context menu
        # configure how the window resizes
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        # update the window initially
        self.updateWindow()
        # create the program title and icon
        try:  self.root.iconbitmap(self.programIcon)
        except: pass
        self.root.title(self.fileName + " - " + self.programTitle)
        # create the find and replace dialogs
        self.findDialog = FindDialog(self)
        self.replaceDialog = ReplaceDialog(self)       

    def createTextWindow(self, width=70, height=35):
        # create the vertical scrollbar
        yScrollbar = Scrollbar(self.root)
        yScrollbar.grid(row=1, column=1, sticky=N+S)
        # create the horizontal scrollbar
        xScrollbar = Scrollbar(self.root, orient=HORIZONTAL)
        xScrollbar.grid(row=2, column=0, sticky=W+E)
        # create the text widget
        self.text = Text(self.root, width=width, height=height, wrap=NONE, undo=True,
                         selectbackground='#BEBEBE', selectforeground='#000000',
                         xscrollcommand=xScrollbar.set, yscrollcommand=yScrollbar.set)
        self.text.grid(row=1, column=0, sticky=W+E+N+S)
        self.text.focus_force()
        # set scrolling to text widget
        yScrollbar.config(command=self.text.yview)
        xScrollbar.config(command=self.text.xview)
                          
    def createProgramBar(self):
        # create the frame for the program bar
        programBar = Frame(self.root)
        programBar.grid(row=0, column=0, sticky=W)
        # create the "Program Name:" label
        nameLabel = Label(programBar, text="Program Name:")
        nameLabel.grid(row=0, column=0, padx=3, pady=3)
        # create the program name entry field
        self.nameEntry = Entry(programBar, validate='key',
                               validatecommand=(self.root.register(self.validateName), '%P'))
        self.nameEntry.grid(row=0, column=1, padx=3, pady=3)
        # create the protected checkbutton
        protected = Checkbutton(programBar, text="Protected", variable=self.protected,
                                offvalue=5, onvalue=6, command=self.fileModified)
        protected.grid(row=0, column=2, padx=3, pady=3)
        # create the command buttons
        Button(programBar, text=u"⁻", width=3, relief=RIDGE, command=lambda: \
               self.insertFromMenu(u"⁻")).grid(row=0, column=3, padx=8, pady=3, )
        Button(programBar, text=u"→", width=3, relief=RIDGE, command=lambda: \
               self.insertFromMenu(u"→")).grid(row=0, column=4, padx=8, pady=3, )
        Button(programBar, text=u"≤", width=3, relief=RIDGE, command=lambda: \
               self.insertFromMenu(u"≤")).grid(row=0, column=5, padx=8, pady=3, )
        Button(programBar, text=u"≥", width=3, relief=RIDGE, command=lambda: \
               self.insertFromMenu(u"≥")).grid(row=0, column=6, padx=8, pady=3, )
        Button(programBar, text=u"≠", width=3, relief=RIDGE, command=lambda: \
               self.insertFromMenu(u"≠")).grid(row=0, column=7, padx=8, pady=3, )
        Button(programBar, text=u"√(", width=3, relief=RIDGE, command=lambda: \
               self.insertFromMenu(u"√(")).grid(row=0, column=8, padx=8, pady=3, )
        Button(programBar, text=u"θ", width=3, relief=RIDGE, command=lambda: \
               self.insertFromMenu(u"θ")).grid(row=0, column=9, padx=8, pady=3, )

    def createStatusBar(self):
        # create the frame for the status bar
        statusBar = Frame(self.root)
        statusBar.grid(row=3, column=0, columnspan=2, sticky=E)
        # create the cursor line label
        self.statusLine = Label(statusBar, textvariable=self.line, bd=1, relief=SUNKEN)
        self.statusLine.grid(row=1, column=0)
        # create the cursor col label
        self.statusCol = Label(statusBar, textvariable=self.col, bd=1, relief=SUNKEN)
        self.statusCol.grid(row=1, column=1)

    def createMenuBar(self):
        self.menuBar = Menu(self.root)
        self.createFileMenu() # create the file menu
        self.createEditMenu() # create the edit menu
        self.createCommandMenu() # create the commands menu
        self.createOptionsMenu() # create the options menu
        self.createHelpMenu() # create the help menu
        self.root.config(menu=self.menuBar)

    def createFileMenu(self):
        # create the file menu
        fileMenu = Menu(self.menuBar, tearoff=False)
        fileMenu.add_command
        fileMenu.add_command(label="New", command=self.newFile, accelerator="Ctrl+N")
        fileMenu.add_command(label="Open...", command=self.openFile, accelerator="Ctrl+O")
        fileMenu.add_command(label="Save", command=self.saveFile, accelerator="Ctrl+S")
        fileMenu.add_command(label="Save As...", command=self.saveAsFile)
        fileMenu.add_separator()
        fileMenu.add_command(label="Run Interpreter", command=self.interpretFile, accelerator="F5")
        fileMenu.add_separator()
        fileMenu.add_command(label="Exit", command=self.exitFile, accelerator="Ctrl+Q")
        self.menuBar.add_cascade(label="File", menu=fileMenu)
        
    def createEditMenu(self):
        # create the edit menu
        editMenu = Menu(self.menuBar, tearoff=False)
        editMenu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        editMenu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        editMenu.add_separator()
        editMenu.add_command(label="Cut", command=self.cut, accelerator="Ctrl+X")
        editMenu.add_command(label="Copy", command=self.copy, accelerator="Ctrl+C")
        editMenu.add_command(label="Paste", command=self.paste, accelerator="Ctrl+V")
        editMenu.add_separator()
        editMenu.add_command(label="Delete", command=self.delete, accelerator="Del")
        editMenu.add_command(label="Select All", command=self.selectAll, accelerator="Ctrl+A")
        editMenu.add_separator()
        editMenu.add_command(label="Find...", command=self.find, accelerator="Ctrl+F")
        editMenu.add_command(label="Replace...", command=self.replace, accelerator="Ctrl+H")
        self.menuBar.add_cascade(label="Edit", menu=editMenu)

    def createCommandMenu(self):
        # create the command menu
        commandMenu = Menu(self.menuBar, tearoff=False)
        self.addCommandMenu(commandMenu, self.commandsMenu)
        self.menuBar.add_cascade(label="Commands", menu=commandMenu)

    def addCommandMenu(self, menu, dictionary):
        # create the commands menu
        for command, value in dictionary.iteritems():
            # if the value is a command
            if type(value) == tuple:
                # add the command to the menu
                self.addCommandMenuItem(menu, command)
            else:
                # create a submenu
                submenu = Menu(menu, tearoff=False)
                self.addCommandMenu(submenu, value)
                menu.add_cascade(label=command, menu=submenu)

    def addCommandMenuItem(self, menu, command):
        # add the command to the menu
        menu.add_command(label=command, command=lambda: self.insertFromMenu(command))

    def insertFromMenu(self, command):
        try: self.text.delete(SEL_FIRST, SEL_LAST) # delete the selection
        except: pass
        self.text.insert(INSERT, command) # insert the command
        self.updateWindow() # update the window

    def createOptionsMenu(self):
        # create the options menu
        optionsMenu = Menu(self.menuBar, tearoff=False)
        optionsMenu.add_checkbutton(label="Syntax Coloring", variable=self.syntaxColoring,
                                    offvalue=False, onvalue=True, command=self.updateSyntaxColoring)
        optionsMenu.add_separator()
        optionsMenu.add_command(label="Command Color...", command=self.selectCommandColor)
        optionsMenu.add_command(label="String Color...", command=self.selectStringColor)
        self.menuBar.add_cascade(label="Options", menu=optionsMenu)

    def selectCommandColor(self):
        # select the command color
        commandColor = askcolor(initialcolor=self.commandColor.get())[1]
        if commandColor != None:
            self.commandColor.set(commandColor)
            self.updateSyntaxColoring() # update the syntax coloring

    def selectStringColor(self):
        # select the string color
        stringColor = askcolor(initialcolor=self.stringColor.get())[1]
        if stringColor != None:
            self.stringColor.set(stringColor)
            self.updateSyntaxColoring() # update the syntax coloring
        
    def createHelpMenu(self):
        # create the help menu
        helpMenu = Menu(self.menuBar, tearoff=False)
        helpMenu.add_command(label="TI-BASIC Guide", command=self.openGuide)
        self.menuBar.add_cascade(label="Help", menu=helpMenu)

    def createContextMenu(self):
        # create the context menu
        self.contextMenu = Menu(self.root, tearoff=False)
        self.contextMenu.add_command(label="Cut", command=self.cut)
        self.contextMenu.add_command(label="Copy", command=self.copy)
        self.contextMenu.add_command(label="Paste", command=self.paste)
        self.contextMenu.add_separator()
        self.contextMenu.add_command(label="Delete", command=self.delete)
        self.contextMenu.add_command(label="Select All", command=self.selectAll)

    def fileModified(self):
        # set the file modified flag to 1
        self.isFileModified = 1
        # update the title modified flag
        self.root.title("*" + str(self.fileName[self.fileName.rfind("/") + 1:]) +
                        " - " + self.programTitle + "*")
    
    def updateWindow(self):
        # get the cursor line and col
        lineCol = self.text.index(INSERT).split(".")
        self.currentLine = int(lineCol[0])
        self.currentCol = int(lineCol[1])
        # update the Tkinter variables for the cursor line and col
        self.line.set("Ln: %d" % self.currentLine)
        self.col.set("Col: %d" % self.currentCol)
        # update the syntax coloring
        self.updateSyntaxColoring()
        # if the text is modified
        if self.text.edit_modified() == 1:
            self.fileModified() # set the file modified flag to 1
            self.text.tag_delete('syntaxError') # delete the syntax error tag            

    def updateSyntaxColoring(self):
        # clear the sytnax coloring tags
        self.text.tag_delete('commands')
        self.text.tag_delete('strings')
        if self.syntaxColoring.get():
            # update the syntax coloring
            self.colorCommands()
            self.colorStrings()

    def colorCommands(self):
        for command in self.coloredCommands:
            # set the initial index
            startIndex = '1.0'
            while True:
                # find the start and end index of each string
                startIndex = self.text.search(command, startIndex, stopindex=END)
                if startIndex == '': break
                endIndex = '%s+%dc' % (startIndex, len(command))
                # add each command to the command tag
                self.text.tag_add('commands', startIndex, endIndex)
                self.text.tag_config('commands', foreground=self.commandColor.get())
                # set the new start index
                startIndex = endIndex

    def colorStrings(self):
        # set the initial start index
        startIndex = '1.0'
        while True:
            # find the start and end index of each string
            startIndex = self.text.search("\"", startIndex, stopindex=END)
            if startIndex == '': break
            endIndex = self.text.search("\"", '%s+1c' % startIndex, stopindex=END)
            if endIndex == '': endIndex = END
            endIndex = '%s+1c' % endIndex
            # add each string to the strings tag
            self.text.tag_add('strings', startIndex, endIndex)
            self.text.tag_config('strings', foreground=self.stringColor.get())
            # set the new start index
            startIndex = endIndex

    def validateName(self, P):
        # return True if the string is empty
        if len(P) == 0:
            self.fileModified() # set the file modified flag to 1
            return True
        # return False if the character is not a letter or number
        elif P[-1] not in string.ascii_letters + string.digits: return False
        # return False if the string is longer than 8 characters
        elif len(P) > 8: return False
        # return False if the first character is not a letter
        elif P[0] not in string.letters: return False
        self.fileModified() # set the file modified flag to 1
        return True
  
    def undo(self):
        # undo the last action
        self.text.edit_undo()

    def redo(self):
        # redo the last action
        self.text.edit_redo()

    def cut(self):
        # simulate pressing 'Control-x' to cut
        self.text.event_generate('<Control-x>')
        
    def copy(self):
        # simulate pressing 'Control-c' to copy
        self.text.event_generate('<Control-c>')

    def paste(self):
        # simulate pressing 'Control-v' to paste
        self.text.event_generate('<Control-v>')

    def delete(self):
        # simulate pressing 'Delete' to delete
        self.text.event_generate('<Delete>')

    def selectAll(self):
        # simulate pressing 'Control-/' to select all
        self.text.event_generate('<Control-/>')
        
    def find(self):
        # set where the dialog is placed
        self.findDialog.geometry('+%d+%d' % (self.root.winfo_rootx()+50, \
                                             self.root.winfo_rooty()+50))
        # bring up the find dialog
        self.findDialog.deiconify()
        self.findDialog.findEntry.focus_force()
        self.findDialog.findEntry.select_range(0, END)
        
    def replace(self):
        # set where the dialog is placed
        self.findDialog.geometry('+%d+%d' % (self.root.winfo_rootx()+50, \
                                             self.root.winfo_rooty()+50))
        # bring up the repalce dialog
        self.replaceDialog.deiconify()
        self.replaceDialog.findEntry.focus_force()
        self.replaceDialog.findEntry.select_range(0, END)

    def findNext(self):
        # set the initial find index
        self.findIndex = self.text.index(INSERT)
        # find the text and return the index
        index = self.text.search(self.findText, self.findIndex)
        if index == "":
            # show the find error dialog
            tkMessageBox.showinfo(parent=self.root, title="Not Found",
                                  message="Cannot find \"%s\"." % self.findText)
            self.text.mark_set(INSERT, self.findIndex)
        else:
            # highlight the found word
            self.text.tag_delete('find')
            self.text.tag_add('find', index, '%s+%dc' % (index, len(self.findText)))
            self.text.tag_config('find', background='#BEBEBE')
            self.text.mark_set(INSERT, '%s+%dc' % (index, len(self.findText)))
        self.text.focus_force()

    def replaceNext(self):
        # set the initial find index
        self.findIndex = self.text.index(INSERT)
        # find the text and return the index
        index = self.text.search(self.findText, self.findIndex)
        if index == "":
            # show the replace error dialog
            tkMessageBox.showinfo(parent=self.root, title="Not Found",
                                  message="Cannot find \"%s\"." % self.findText)
        else:
            # replace and highlight the found word
            self.text.delete(index, '%s+%dc' % (index, len(self.findText)))
            self.text.insert(index, self.replaceText)
            self.text.tag_delete('find')
            self.text.tag_add('find', index, '%s+%dc' % (index, len(self.replaceText)))
            self.text.tag_config('find', background='#BEBEBE')
            self.text.mark_set(INSERT, '%s+%dc' % (index, len(self.replaceText)))
        self.text.focus_force()
        
    def replaceAll(self):
        # set the initial index
        index = '1.0'
        while True:
            # find the text and return the index
            index = self.text.search(self.findText, index, END)
            # break if the word is not found
            if index == "": break
            # replace the found word
            else:
                self.text.delete(index, '%s+%dc' % (index, len(self.findText)))
                self.text.insert(index, self.replaceText)
                index = '%s+%dc' % (index, len(self.replaceText))
        self.text.focus_force()

    def openGuide(self):
        webbrowser.open('http://tibasicdev.wikidot.com/commands', new=2, autoraise=True)

    def newFile(self):
        Editor(self.commandColor.get(), self.stringColor.get(), self.syntaxColoring.get()).run() # create a new window

    def openFile(self):
        # get the file being opened
        if self.fileName == "Untitled":
            openFileName = askopenfilename(defaultextension=self.defaultExtension,
                                           filetypes=self.fileTypes)
        else:
            openFileName = askopenfilename(defaultextension=self.defaultExtension,
                                           filetypes=self.fileTypes,
                                           initialdir=self.fileName[:self.fileName.rfind("/")])
        # if the file is already open or no file was opened do nothing
        if self.fileName == openFileName or openFileName == "": pass
        # if the file being opened is a calculator program
        elif openFileName[-4:] == '.8xp': self.decompileFile(openFileName)
        else:
            # if we have a empty window
            if self.isFileModified == 0 and len(self.text.get('1.0', END)) == 1:
                self.readFile(openFileName) # read the file
            else:
                NewEditor(self, openFileName) # open a new window and read the file
            
    def readFile(self, openFileName):
        try:
            # read the file
            file = open(openFileName, 'r')
            contents = file.read()
            self.text.insert('1.0', contents)
            file.close()
            # update the file
            self.updateFile(openFileName)
        except:
            tkMessageBox.showwarning(parent=self.root, title="Open Error",
                                     message="The file could not be opened.")
    
    def saveFile(self):
        # get the program name
        programName = str(self.nameEntry.get()).upper()
        # if the file has not been saved already run save as
        if self.fileName == "Untitled": self.saveAsFile()
        # if the file is being saved as a calculator program
        elif self.fileName[-4:] == '.8xp': self.compileFile(self.fileName, programName)
        else: self.writeFile(self.fileName, programName) # write the file

    def saveAsFile(self):
        # get the program name
        programName = str(self.nameEntry.get()).upper()
        # set the initial file save name
        initialFileName = programName if self.fileName == "Untitled" \
                          else str(self.fileName[self.fileName.rfind("/") + 1:])
        # get the save file name
        if self.fileName == "Untitled":
            saveFileName = asksaveasfilename(defaultextension=self.defaultExtension,
                                             filetypes=self.fileTypes,
                                             initialfile=initialFileName)
        else:
            saveFileName = asksaveasfilename(defaultextension=self.defaultExtension,
                                             filetypes=self.fileTypes,
                                             initialfile=initialFileName,
                                             initialdir=self.fileName[:self.fileName.rfind("/")])
        # do nothing if no file was saved
        if saveFileName == "": pass
        # if the file is being saved as a calculator program
        elif saveFileName[-4:] == '.8xp': self.compileFile(saveFileName, programName)
        else: self.writeFile(saveFileName, programName) # write the file
        
    def writeFile(self, saveFileName, programName):
        try:
            # write the file
            file = open(saveFileName, 'w')
            contents = self.text.get('1.0', END)
            file.write(contents)
            file.close()
            # update the file
            self.updateFile(saveFileName) 
        except:
            tkMessageBox.showwarning(parent=self.root, title="Save Error",
                                     message="The file could not be saved.")

    def updateFile(self, fileName):
        self.fileName = fileName # update the file name
        self.isFileModified = 0 # set the file modified flag to 0
        self.text.edit_modified(0)  # set the text modified flag to 0
        self.updateSyntaxColoring() # update the syntax coloring
        # update the program title
        self.root.title(str(self.fileName[self.fileName.rfind("/") + 1:]) +
                        " - " + self.programTitle)
        
    def exitFile(self):
        # if the file is modified
        if self.isFileModified == 1:
            self.saveCheck() # show the save check dialog
        else:
            self.root.destroy() # end the program and close the window

    def saveCheck(self):
        # create the save check dialog
        response = tkMessageBox.askquestion(parent=self.root, title=self.programTitle,
                                            message="Do you want to save changes to " + self.fileName + "?",
                                            type='yesnocancel')
        # if the response is cancel do nothing
        if response == "cancel": return
        # if the response is no end the program and close the window
        elif response == "no": self.root.destroy()
        # if the response is yes save the file
        elif response == "yes":
            self.saveFile()
            self.root.destroy()
    
    def compileFile(self, saveFileName, programName):
        # show the program name error dialog if the program name is empty
        if len(programName) == 0:
            tkMessageBox.showwarning(parent=self.root, title="Program Name Error",
                                     message="Please specify a program name.")
        else:
            # if there are no syntax errors
            try:
                # get the data
                data = self.getData(programName)
                # get the checksum
                checksum = self.littleEndian(sum(data))
                # get the header
                header = self.getHeader()
                # get the program file string
                dataLength = self.littleEndian(len(data))
                programFile = header + self.getProgramFile(dataLength + data + checksum)
                self.writeCompiledFile(saveFileName, programName, programFile)
            # if there is a syntax error
            except:
                # set the text modified flag to 0
                self.text.edit_modified(0)
                
    def littleEndian(self, n):
        # convert an integer to little-endian style hex value
        n = n % 0x10000
        return [n % 0x100, n / 0x100]

    def getData(self, programName):
        # get the variable data
        variableData = self.getVariableData()
        # get the length of the variable data
        variableDataLength = self.littleEndian(len(variableData))
        # get the program name
        programName = [ord(c) for c in programName] + [0] * (8 - len(programName))
        # get the data
        return [13, 0] + variableDataLength + [self.protected.get()] + \
               programName + [0, 0] + variableDataLength + variableData
        
    def getVariableData(self):
        # get the actual data
        actualData = self.compileCommand([], self.text.get('1.0', END)[:-1])
        # get the variable data
        return self.littleEndian(len(actualData)) + actualData

    def compileCommand(self, commands, contents):
        length = 14
        while len(contents) > 0:
            # give an error if a command is not found
            if length == 0:
                self.writeSyntaxError(contents)
                raise Exception
            try:
                # add the command of the test string to the list of commands 
                commands.extend(self.commands[contents[:length]])
                # get the next command
                contents = contents[length:]
                length = min(14, len(contents))
            except:
                # shorten the test string by 1
                length -= 1
        return commands # return commands if we have compiled all of the code

    def getHeader(self):
        # get the signature
        signature = "**TI83F*" + chr(26) + chr(10) + chr(0) + "Program file"
        # get the date and time
        date, time = self.getDateTime()
        return signature + " " + date + ", " + time + \
               chr(0) * 14
        
    def getDateTime(self):
        # get the date and time
        now = datetime.datetime.now()
        return now.strftime("%m/%d/%y"), now.strftime("%H:%M")

    def getProgramFile(self, code):
        # get the program file string
        programFile = ""
        for i in code:
            programFile += chr(i)
        return programFile

    def writeCompiledFile(self, saveFileName, programName, programFile):
        try:
            # write the file
            file = open(saveFileName, 'wb')
            file.write(programFile)
            file.close()
            # update the program name
            self.nameEntry.delete(0, END)
            self.nameEntry.insert(0, programName)
            # update the file
            self.updateFile(saveFileName) 
        except: pass

    def writeSyntaxError(self, contents):
        # highlight the syntax error
        index = self.text.search(contents, END, stopindex='1.0', backwards=True)
        self.text.tag_add('syntaxError', '%swordstart' % index, '%swordend' % index)
        self.text.tag_config('syntaxError', background='#FF7777')
        # get the syntax error line and col
        index = index.split(".")
        line = int(index[0])
        col = int(index[1])
        # show the write syntax error dialog
        tkMessageBox.showwarning(parent=self.root, title="Syntax Error", 
                                 message="There was a syntax error in your program:\nLine %d, Column %d" % (line, col))

    def decompileFile(self, openFileName):
        # if there are no syntax errors
        try:
            # read the file
            file = open(openFileName, 'rb')
            programFile = file.read()
            # get the program name
            programName = programFile[60:programFile.find(chr(0), 60)]
            # get the contents
            contents = self.decompileCommand("", programFile[74:-2])
            file.close()
            # if we have a empty window
            if self.isFileModified == 0 and len(self.text.get('1.0', END)) == 1:
                self.readDecompiledFile(openFileName, programName, contents) # read the file
            else:
                NewCalculatorEditor(self, openFileName, programName, contents) # open a new window and read the file
        # if there is a syntax error
        except: pass

    def decompileCommand(self, contents, code):
        length = min(2, len(code))
        while len(code) > 0:
            # give an error if a command is not found
            if length == 0:
                self.readSyntaxError(contents)
                raise Exception
            try:
                # add the command of the test string to the list of commands 
                contents += self.revCommands[tuple([ord(code[c]) for c in xrange(length)])]
                # get the next command
                code = code[length:]
                length = min(2, len(code))
            except:
                # shorten the test string by 1
                length -= 1
        return contents # return cotents if we have decompiled all of the code

    def readDecompiledFile(self, openFileName, programName, contents):
        # read the file
        self.text.insert('1.0', contents)
        # update the program name
        self.nameEntry.delete(0, END)
        self.nameEntry.insert(0, programName)
        # update the file
        self.updateFile(openFileName)

    def readSyntaxError(self, contents):
        # show the write syntax error dialog
        tkMessageBox.showwarning(parent=self.root, title="Invalid File", 
                                 message="The file is invalid.  It cannot be opened.")

    def interpretFile(self):
        # if there are no syntax errors
        try:
            # save the file if it is not saved
            if self.text.edit_modified() != 0:
                # create the save check dialog
                response = tkMessageBox.askquestion(parent=self.root, title=self.programTitle,
                                                    message="File must be saved.  OK to save?",
                                                    type='yesnocancel')
                # if the response is yes interpret the file
                if response == "yes":
                    self.saveFile()
            # if the file was saved
            if self.text.edit_modified() == 0:
                # insert missing parenthesis
                contents = self.insertParenthesis(self.text.get('1.0', END)[:-1])
                self.tab = 0
                # interpret each line of code
                for line in xrange(len(contents)):
                        interpretLine = "\t" * self.tab
                        interpretLine = self.interpretCommand(contents[line], interpretLine, line + 1)
                        contents[line] = interpretLine
                # run the interpreted file
                self.writeInterpretFile("\n".join(contents))
        # if there is a syntax error
        except: pass
            
    def insertParenthesis(self, contents):
        # insert missing parenthesis
        contents = contents.split("\n")
        for line in xrange(len(contents)):
            contents[line] = contents[line]+ ")" * (contents[line].count("(") - contents[line].count(")"))
        return contents
        
    def interpretCommand(self, line, interpretLine, lineNumber=0):
        length = max(14, len(line))
        while len(line) > 0:
            # give an error if a command is not found
            if length == 0:
                self.interpretSyntaxError(lineNumber, line)
                raise Exception
            try:
                # if the command is a varaible or number add it to the line
                if length == 1 and ord(line[:length]) in range(0x30, 0x3A) + range(0x41, 0x5B):
                    interpretLine += line[:length]  
                else:
                    value = self.interpretCommands[line[:length]]
                    # add the command to the line
                    if type(value) == str: interpretLine += value
                    # run the function to interpret the command
                    else: line, interpretLine = value(line, interpretLine)
                # get the next command
                line = line[length:]
                length = max(14, len(line))
            except:
                # shorten the test string by 1
                length -= 1
        return interpretLine # return commands if we have compiled all of the code

    def writeInterpretFile(self, contents):
        try:
            # write the interpreted python file
            file = open(str(self.fileName[:self.fileName.rfind(".") + 1]) + "py", 'w')
            file.write(self.interpretCode + "\n" + contents)
            file.close()
        except: pass
        # run the interpreted python file
        try:
            execfile(str(self.fileName[:self.fileName.rfind(".") + 1]) + "py")
        # stop running if the interpreted python file is exited
        except Stop: pass
        except:
            # show an error if the interpreted file gives an error
            tkMessageBox.showwarning(parent=self.root, title="Interpreter Error",
                                     message="The interpreter could not be run.")
            
    def interpretSyntaxError(self, lineNumber, line):
        # highlight the interpret error
        line = line.rstrip(")")
        index = self.text.search(line, '%s.0' % lineNumber, stopindex='%s.end' % lineNumber)
        self.text.tag_add('interpretError', '%swordstart' % index, '%swordend' % index)
        self.text.tag_config('interpretError', background='#FF7777')
        # get the interpret error line and col
        index = index.split(".")
        line = int(index[0])
        col = int(index[1])
        # show the interpret syntax error dialog
        tkMessageBox.showwarning(parent=self.root, title="Interpreter Error", 
                                 message="Your program could not be interpreted.  The command may not be supported:\nLine %d, Column %d" % (line, col))

    def interpretAssign(self, line, interpretLine):
        # interpret the assign command
        var = self.interpretCommand(line[1:], "")
        interpretLine = "\t" * self.tab + var + "=" + interpretLine[interpretLine.rfind("\t")+1:]
        return "", interpretLine

    def interpretIf(self, line, interpretLine):
        # interpret the If command
        interpretLine += "if " + self.interpretCommand(line[3:], interpretLine) + ":"
        self.tab += 1
        return "", interpretLine

    def interpretElse(self, line, interpretLine):
        # interpret the Else command
        interpretLine = interpretLine[:-1]
        interpretLine += "else:"
        return "", interpretLine

    def interpretFor(self, line, interpretLine):
        # interpret the For command
        args = line[4:-1].split(",")
        args[2] = str(int(args[2])+1)
        args = tuple(args)
        interpretLine += "for %s in xrange(%s,%s):" % args
        self.tab += 1
        return "", interpretLine

    def interpretWhile(self, line, interpretLine):
        # interpret the While command
        interpretLine += "while " + self.interpretCommand(line[6:], interpretLine) + ":"
        self.tab += 1
        return "", interpretLine

    def interpretRepeat(self, line, interpretLine):
        # interpret the Repeat command
        interpretLine += "while not(" + self.interpretCommand(line[7:], interpretLine) + "):"
        self.tab += 1
        return "", interpretLine

    def interpretEnd(self, line, interpretLine):
        # interpret the End command
        self.tab -= 1
        return "", interpretLine

    def interpretInput(self, line, interpretLine):
        # interpret the Input command
        args = line[line.find("\"")+1:].split(",")
        args[0] = args[0][:args[0].rfind("\"")]
        interpretLine += str("%s = int(raw_input(\"%s\"))" % (u'A', u'A'))
        return "", interpretLine

    def interpretPrompt(self, line, interpretLine):
        # interpret the Prompt command
        interpretLine += "%s = int(raw_input(\"%s=?\"))" % (line[7], line[7])
        return "", interpretLine

    def interpretGetLogic(self, line, interpretLine, length):
        # interpret the arguments for logical tests
        var1 = interpretLine[interpretLine.rfind(" ")+1:]
        var2 = line[length:]
        interpretLine = interpretLine[:-len(var1)]
        line = line[length:line.find(" ")]
        return "(" + var1 + "!=0)", "(" + var2 + "!=0)", line, interpretLine

    def interpretAnd(self, line, interpretLine):
        # interpret the and command
        var1, var2, line, interpretLine = self.calcGetLogic(line, interpretLine, 5)
        interpretLine += var1 + " and " + var2
        return line, interpretLine

    def interpretOr(self, line, interpretLine):
        # interpret the or command
        var1, var2, line, interpretLine = self.calcGetLogic(line, interpretLine, 4)
        interpretLine += var1 + " or " + var2
        return line, interpretLine

    def interpretXor(self, line, interpretLine):
        # interpret the xor command
        var1, var2, line, interpretLine = self.calcGetLogic(line, interpretLine, 4)
        interpretLine += var1 + " != " + var2
        return line, interpretLine

    def interpretList(self, line, interpretLine):
        # interpret the lsit index command
        var = self.interpretCommand(line[:2], "")
        index = line[3:line.find(")")]
        line = line[len(index)+4:]
        interpretLine += var + "[" + index + "-1]"
        return line, interpretLine

class NewEditor(Editor):
    def __init__(self, parent, openFileName):
        # open a new window and read the file
        super(NewEditor, self).__init__(parent.commandColor.get(), parent.stringColor.get(), parent.syntaxColoring.get())
        self.fileName = openFileName
        self.readFile(openFileName)
        parent.root.lower(belowThis=None)
        super(NewEditor, self).run()

class NewCalculatorEditor(Editor):
    def __init__(self, parent, openFileName, programName, contents):
        # open a new window and read the file
        super(NewCalculatorEditor, self).__init__(parent.commandColor.get(), parent.stringColor.get(), parent.syntaxColoring.get())
        self.fileName = openFileName
        self.readDecompiledFile(openFileName, programName, contents)
        super(NewCalculatorEditor, self).run()

class FindDialog(Toplevel):
    def __init__(self, parent):
        Toplevel.__init__(self)
        self.withdraw()
        # create the find dialog
        self.createFindDialog(parent)
        # create the dialog title and icon
        self.title("Find")
        try: self.iconbitmap(parent.programIcon)
        except: pass

    def createFindDialog(self, parent):
        # create the dialog font
        font = Font(family='Arial', size = 8)
        # create "Find:" label
        findLabel = Label(self, text="Find:")
        findLabel.grid(row=0, column=0, padx=3, pady=3, sticky=W)
        # create the find entry field
        self.findEntry = Entry(self)
        self.findEntry.grid(row=0, column=1, padx=3, pady=3)
        # create the "Find Next" button
        findNextButton = Button(self, text="Find Next", width=12, font=font,
                                relief=GROOVE, command=lambda: self.findNext(parent))
        findNextButton.grid(row=0, column=2, padx=3, pady=3)
        # create the "Cancel" Button
        cancelButton = Button(self, text="Cancel", width=12, font=font,
                              relief=GROOVE, command=self.cancel)
        cancelButton.grid(row=1, column=2, padx=3, pady=3)

    def findNext(self, parent):
        # find the next occurance of the text
        parent.findText = self.findEntry.get()
        parent.findNext()

    def cancel(self):
        # close the window
        self.withdraw()
        
class ReplaceDialog(FindDialog):
    def __init__(self, parent):
        Toplevel.__init__(self)
        self.withdraw()
        # create the replace dialog
        self.createReplaceDialog(parent)
        # create the dialog title and icon
        self.title("Replace")
        try: self.iconbitmap(parent.programIcon)
        except: pass

    def createReplaceDialog(self, parent):
        # create the dialog font
        font = Font(family='Arial', size = 8)
        # create "Find:" label
        findLabel = Label(self, text="Find:")
        findLabel.grid(row=0, column=0, padx=3, pady=3, sticky=W)
        # create the find entry field
        self.findEntry = Entry(self)
        self.findEntry.grid(row=0, column=1, padx=3, pady=3)
        # create the "Replace:" button
        replaceLabel = Label(self, text="Replace:")
        replaceLabel.grid(row=1, column=0, padx=3, pady=3, sticky=W)
        # create the replace entry field
        self.replaceEntry = Entry(self)
        self.replaceEntry.grid(row=1, column=1, padx=3, pady=3)
        # create the "Replace Next" button
        replaceNextButton = Button(self, text="Replace Next", width=12, font=font,
                                   relief=GROOVE, command=lambda: self.replaceNext(parent))
        replaceNextButton.grid(row=0, column=2, padx=3, pady=3)
        # create the "Replace All" button
        replaceAllButton = Button(self, text="Replace All", width=12, font=font,
                                  relief=GROOVE, command=lambda: self.replaceAll(parent))
        replaceAllButton.grid(row=1, column=2, padx=3, pady=3)
        # create the "Cancel" button
        cancelButton = Button(self, text="Cancel", width=12, font=font,
                              relief=GROOVE, command=self.cancel)
        cancelButton.grid(row=2, column=2, padx=3, pady=3)

    def replaceNext(self, parent):
        # replace the next occurance of the text
        parent.findText = self.findEntry.get()
        parent.replaceText = self.replaceEntry.get()
        parent.replaceNext()

    def replaceAll(self, parent):
        # replace all occurances of the text
        parent.findText = self.findEntry.get()
        parent.replaceText = self.replaceEntry.get()
        parent.replaceAll()

    def cancel(self):
        # close the window
        self.withdraw()

# Launch the program
app = Editor()
app.run() 
