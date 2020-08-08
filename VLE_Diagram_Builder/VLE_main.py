from urllib.request import urlopen
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import ttk as ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.font_manager as font_manager
import numpy as np

import Compound # Class for creating object for each compound
import ToolTip
# Goal: Draw Dew/Bubble curves for VLE system


class UserInputs(tk.Frame):
    # Class for the frame of user inputs
    def __init__(self, master, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)
        self.master = master
        self.frame = tk.Frame(self.master)
        frm_userIn = tk.Frame(master=master)
        frm_userIn.pack(side="left")

        self.lbl_Name1 = tk.Label(master=frm_userIn, text="Name of Compound 1 : ", font=('Times New Roman', 16))
        self.lbl_Name1.grid(row=0, column=0, sticky='w', pady=5, padx=5)
        self.lbl_Name2 = tk.Label(master=frm_userIn, text="Name of Compound 2 : ", font=('Times New Roman', 16))
        self.lbl_Name2.grid(row=1, column=0, sticky='w', pady=5, padx=5)
        self.lbl_Pres = tk.Label(master=frm_userIn, text="Total Pressure (bar) : ", font=('Times New Roman', 16))
        self.lbl_Pres.grid(row=2, column=0, sticky='w', pady=5, padx=5)
        self.lbl_Temp = tk.Label(master=frm_userIn, text="Starting Temperature (K) : ", font=('Times New Roman', 16))
        self.lbl_Temp.grid(row=3, column=0, sticky='w', pady=5, padx=5)

        self.comp1Text = tk.StringVar()
        self.ent_Name1 = tk.Entry(master=frm_userIn, textvariable=self.comp1Text, font=('Times New Roman', 16))
        self.ent_Name1.grid(row=0, column=1, pady=5, padx=5, columnspan=2)
        self.comp2Text = tk.StringVar()
        self.ent_Name2 = tk.Entry(master=frm_userIn, textvariable=self.comp2Text, font=('Times New Roman', 16))
        self.ent_Name2.grid(row=1, column=1, pady=5, padx=5, columnspan=2)
        self.pText = tk.StringVar()
        self.ent_Pres = tk.Entry(master=frm_userIn, textvariable=self.pText, width=10, font=('Times New Roman', 16))
        self.ent_Pres.grid(row=2, column=1, pady=5, padx=5)
        self.tText = tk.StringVar()
        self.ent_Temp = tk.Entry(master=frm_userIn, textvariable=self.tText, width=10, font=('Times New Roman', 16))
        self.ent_Temp.grid(row=3, column=1, pady=5, padx=5)

        # User choice of units
        self.presUnitVar = tk.StringVar()
        self.presUnitsDropDown = ttk.Combobox(master=frm_userIn, width=6, textvariable=self.presUnitVar,
                                             state='readonly', font=('Times New Roman', 16))
        self.presUnitsDropDown['values'] = ('bar', 'atm', 'mmHg', 'Pa', 'kPa')
        self.presUnitsDropDown.current(0)
        self.presUnitsDropDown.grid(row=2, column=2)
        self.tempUnitVar = tk.StringVar()
        self.tempUnitsDropDown = ttk.Combobox(master=frm_userIn, width=6, textvariable=self.tempUnitVar,
                                              state='readonly', font=('Times New Roman', 16))
        self.tempUnitsDropDown['values'] = ('K', '\u00b0C', '\u00b0F')
        self.tempUnitsDropDown.current(0)
        self.tempUnitsDropDown.grid(row=3, column=2, padx=5)

        # User chooses specificity for calculations: how many points calculated for curve
        self.specLbl = tk.Label(master=frm_userIn, text='Specificity : ', font=('Times New Roman', 16))
        self.specLbl.grid(row=4, column=0, sticky='w', pady=5, padx=5)

        self.specInput = tk.IntVar()
        self.specInput.set(10)
        self.specEnt = tk.Entry(master=frm_userIn, textvariable=self.specInput, width=10, font=('Times New Roman', 16))
        self.specEnt.grid(row=4, column=1, pady=5, padx=5)

class CheckButtons(tk.Frame):
    # checkbuttons for main window, choices;
    def __init__(self, master, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)

        self.master = master

        frm_chk = tk.Frame(master=self.master)
        frm_chk.pack(side="right")
        # grid(row=1, column=0, padx=5, pady=5)
        self.var_idl = tk.BooleanVar()
        self.var_idl.set(True)  # True for ease
        self.cbIdl = tk.Checkbutton(master=frm_chk, text="Use Raoult's Law", variable=self.var_idl,
                                    font=('Times New Roman', 16))
        self.cbIdl.grid(row=0, column=0, sticky='w', pady=2)
        self.var_tRangeIgnore = tk.BooleanVar()
        self.var_tRangeIgnore.set(True)  # True for ease
        self.cbTemp = tk.Checkbutton(master=frm_chk, text="Ignore Antoine Temperature Range",
                                     variable=self.var_tRangeIgnore, font=('Times New Roman', 16))
        self.cbTemp.grid(row=1, column=0, sticky='w', pady=2)
        self.var_comp = tk.BooleanVar()
        self.cbComp = tk.Checkbutton(master=frm_chk, text="Plot Component 2 (Default Component 1)",
                                     variable=self.var_comp, font=('Times New Roman', 16))
        self.cbComp.grid(row=2, column=0, sticky='w', pady=2)

        self.var_IsoBar = tk.BooleanVar()
        self.cbIsoBar = tk.Checkbutton(master=frm_chk, text="Calculate at Constant Pressure", variable=self.var_IsoBar,
                                       command=self.toggleTherm, font=('Times New Roman', 16))
        self.cbIsoBar.grid(row=3, column=0, sticky='w', pady=2)
        self.var_IsoTherm = tk.BooleanVar()
        self.cbIsoTherm = tk.Checkbutton(master=frm_chk, text="Calculate at Constant Temperature",
                                         variable=self.var_IsoTherm,
                                         command=self.toggleBar, font=('Times New Roman', 16))
        self.cbIsoTherm.grid(row=4, column=0, sticky='w', pady=2)
        self.var_IsoTherm.set(True)

    # IsoBar and IsoTherm are mutually exclusive, clicking one toggles the other
    def toggleBar(self):
        self.cbIsoBar.toggle()

    def toggleTherm(self):
        self.cbIsoTherm.toggle()


class MainApplication(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        self.inputError = 0 # not zero when error occurs in input window

        tk.Frame.__init__(self, master, *args, **kwargs)
        self.master = master
        master.title('VLE Diagram Builder')
        master.minsize(width=1024, height=320)  # Don't want to resize smaller since widgets get cutoff
        master.resizable(False, False)

        # label/description
        self.description = tk.Label(master, text='This application calculates and plots the bubble and dew curves of'
                                                 ' a binary mixture at a given temperature and pressure. The compound'
                                                 ' that is plotted can be changed and the complexity of the calculation'
                                                 ' can also be modified.', wraplength=1024, justify='left',
                                    font=('Times New Roman', 16))
        self.description.pack(side="top", fill="x")

        # Rest of Window GUI goes here
        self.frame = tk.Frame(self.master)
        self.inputs = UserInputs(self)
        self.chkbuttons = CheckButtons(self)

        # geometry
        self.inputs.pack(side="top", fill="x", expand=True)
        self.chkbuttons.pack(side="top", fill="x", expand=True)

        # calculate button
        self.calcBtn = tk.Button(master=self.master, text='Calculate', width=12, command=self.calculate,
                                 activebackground="blue", font=('Times New Roman', 16))
        self.calcBtn.pack(side='bottom', pady=5)
        # Bind Return key to calculate function, allowing user to press key to run program
        master.bind('<Return>', self.calcEnter)

        # set focus
        self.inputs.ent_Name1.focus_set()

        # Hover Tooltip descriptions
        ToolTip.CreateToolTip(self.calcBtn, text='Click this button to create the VLE diagram.')

        ToolTip.CreateToolTip(self.inputs.ent_Name1, text='Enter the name of a chemical compound')
        ToolTip.CreateToolTip(self.inputs.ent_Name2, text='Enter the name of another chemical compound')
        ToolTip.CreateToolTip(self.inputs.ent_Pres, text='Enter the pressure that will\nbe used for calculations')
        ToolTip.CreateToolTip(self.inputs.ent_Temp, text='Enter the temperature that will\nbe used for calculations')

        ToolTip.CreateToolTip(self.chkbuttons.cbIdl, text='If checked, calculations will be done\n'
                                                          'under the assumption that the\n'
                                                          'mixture is ideal')
        ToolTip.CreateToolTip(self.chkbuttons.cbTemp, text='If checked, the temperature ranges\n'
                                                           'will be ignored when looking for\n'
                                                           'Antoine Equation parameters for the\n'
                                                           'compounds. The program will choose\n'
                                                           'the first set of parameters it finds.')
        ToolTip.CreateToolTip(self.chkbuttons.cbComp, text='If checked, calculations and plotting\n'
                                                           'will be done based on the compound\n'
                                                           'entered in "Name of Compound 2"')
        ToolTip.CreateToolTip(self.chkbuttons.cbIsoBar, text='If checked, calculations will be\n'
                                                             'performed with the assumption that\n'
                                                             'the mixture is under Isobaric conditions.\n'
                                                             '(Constant Pressure)')
        ToolTip.CreateToolTip(self.chkbuttons.cbIsoTherm, text='If checked, calculations will be\n'
                                                               'performed with the assumption that\n'
                                                               'the mixture is under Isothermal conditions.\n'
                                                               '(Constant Temperature)')

        ToolTip.CreateToolTip(self.inputs.presUnitsDropDown, text='Click to change the Pressure units')
        ToolTip.CreateToolTip(self.inputs.tempUnitsDropDown, text='Click to change the Temperature units')

        ToolTip.CreateToolTip(self.inputs.specEnt, text='Enter the number of points that should\n'
                                                          'be calculated per curve. The specified\n'
                                                          'number will be the number of points beyond\n'
                                                          'zero.')

    def inputReq(self):
        entries = [self.inputs.ent_Name1, self.inputs.ent_Name2]
        try:
            namesFilled = 0 # initialize
            for i in range(0, len(entries)):
                if entries[i].get():
                    namesFilled = 1
                else:
                    if i == 1: # compound 2 blank, and passed compound 1
                        raise InputError('Compound 2')
                    else: # else compound 1 blank
                        raise InputError('Compound 1')
            if namesFilled == 1:
                userTP = [self.inputs.ent_Pres, self.inputs.ent_Temp]
                filledTP = 0 # initialize
                for i in range(0, len(userTP)):
                    if userTP[i].get():
                        filledTP = 1 # set to 1 if element exists
                    else:
                        filledTP = 0
                        break # breaks, at least one missing
                if filledTP == 1:
                    return True
                else:
                    return False # at least one item doesn't exist, T or P, will later set to default values for calc
        except InputError as e:
            e.__str__()
            self.inputError = 1 # sets sentry for later
            if not self.inputs.ent_Name1.get(): # sets focus to blank box
                entries[0].focus_set()
            else:
                entries[1].focus_set()

    # workaround for key input to continue
    def calcEnter(self, event):
        self.calculate()

    def calculate(self):
        if self.inputReq():  # checks required entries, continues if all filled,
            # convert values to user choice: antoine (calculate normal then convert), graph
            self.presUnitUse = self.inputs.presUnitVar.get()
            self.tempUnitUse = self.inputs.tempUnitVar.get()
            # Sets input constants; floats for decimal values, converts to bar/K for calculations
            if self.presUnitUse != 'bar':
                if self.presUnitUse == 'atm':
                    self.pTot = float(self.inputs.ent_Pres.get()) * 1.01325
                elif self.presUnitUse == 'mmHg':
                    self.pTot = float(self.inputs.ent_Pres.get()) / 760 * 1.01325
                elif self.presUnitUse == 'Pa':
                    self.pTot = float(self.inputs.ent_Pres.get()) / 100000
                elif self.presUnitUse == 'kPa':
                    self.pTot = float(self.inputs.ent_Pres.get()) / 100
            else:
                self.pTot = float(self.inputs.ent_Pres.get())

            if self.tempUnitUse != 'K':
                if self.tempUnitUse == '\u00b0C':
                    self.temp = float(self.inputs.ent_Temp.get()) + 273.15
                elif self.tempUnitUse == '\u00b0F':
                    self.temp = (float(self.inputs.ent_Temp.get()) - 32) * 5/9 + 273.15
            else:
                self.temp = float(self.inputs.ent_Temp.get())
        else:  # sets to STP 273.15K and 1atm
            self.presUnitUse = self.inputs.presUnitVar.get()
            self.tempUnitUse = self.inputs.tempUnitVar.get()
            if not self.inputs.ent_Pres.get():
                self.pTot = 1.01325  # bar
            elif self.presUnitUse != 'bar':
                if self.presUnitUse == 'atm':
                    self.pTot = float(self.inputs.ent_Pres.get()) * 1.01325
                elif self.presUnitUse == 'mmHg':
                    self.pTot = float(self.inputs.ent_Pres.get()) / 760 * 1.01325
                elif self.presUnitUse == 'Pa':
                    self.pTot = float(self.inputs.ent_Pres.get()) / 100000
                elif self.presUnitUse == 'kPa':
                    self.pTot = float(self.inputs.ent_Pres.get()) / 100
            else:
                self.pTot = float(self.inputs.ent_Pres.get())

            if not self.inputs.ent_Temp.get():
                self.temp = 273.15  # K
            elif self.tempUnitUse != 'K': # if top doesn't go through, user has provided temp
                if self.tempUnitUse == '\u00b0C':
                    self.temp = float(self.inputs.ent_Temp.get()) + 273.15
                elif self.tempUnitUse == '\u00b0F':
                    self.temp = (float(self.inputs.ent_Temp.get()) - 32) * 5/9 + 273.15
            else:
                self.temp = float(self.inputs.ent_Temp.get())
        try:
            # not an error case, just doesn't create window if required input is missing
            if self.inputError != 1:
                # Initialized
                compList = []
                compObjList = []
                self.tRangeError = 0 # sentry for antoine range errors

                # changes order based on user choice
                if self.chkbuttons.var_comp.get():
                    names = [self.inputs.ent_Name2.get(), self.inputs.ent_Name1.get()]
                else:
                    names = [self.inputs.ent_Name1.get(), self.inputs.ent_Name2.get()]

                # checks if care about temperature range, if ignore, use first set of parameters
                # Using Range also needs to update while plotting
                if self.chkbuttons.var_tRangeIgnore.get():
                    for j in range(0, 2):  # Creates objects Compound for each input
                        name = names[j]
                        compList.append(name)
                        antList = self.antoineParameters(name)

                        useSet = antList[0] # using first set of data
                        tRange = useSet[0] # no need for range checking
                        aVal = float(useSet[1])
                        bVal = float(useSet[2])
                        cVal = float(useSet[3])
                        boilP = self.boilPoint(name)
                        name = Compound.Compound(name, tRange, aVal, bVal, cVal, boilP)
                        compObjList.append(name)
                else: # Use temperature ranges
                    for j in range(0, 2):
                        name = names[j]
                        compList.append(name)
                        antList = self.antoineParameters(name)
                        useSet = [] # initialize
                        for i in range(0, len(antList)):
                            useSet = antList[i]
                            tRange = useSet[0]
                            tLow = tRange.split(" - ")[0]
                            tHigh = tRange.split(" - ")[1]
                            if float(tLow) <= self.temp and float(tHigh) >= self.temp:
                                break # breaks loop if temp within range
                            else:
                                if i == len(antList) - 1: # happens when currently on last listed antoine set
                                    useSet = []
                        if useSet != []: #if empty, means temperature is out of antoine range ### double error message here
                            aVal = float(useSet[1])  # if error occurs here, temp out of range likely
                            bVal = float(useSet[2])
                            cVal = float(useSet[3])
                            boilP = self.boilPoint(name)
                            name = Compound.Compound(name, tRange, aVal, bVal, cVal, boilP)
                            compObjList.append(name)
                        else:
                            self.tRangeError = 1
                            raise TempRangeError(name, self.temp, self.inputs.tempUnitVar.get())
                # only runs if there is no error in the temperature ranges
                if self.tRangeError != 1:
                    # Pop up window for plot and information
                    self.win2 = tk.Toplevel()
                    self.win2.title('VLE Results')
                    self.win2.minsize(width=1024, height=512)

                    # Code from SO user - xxmbabanexx; sets open position for window based on screen dimensions
                    w = 1024  # width for the Tk root
                    h = 600  # height for the Tk root

                    # get screen width and height
                    ws = self.win2.winfo_screenwidth()  # width of the screen
                    hs = self.win2.winfo_screenheight()  # height of the screen

                    # calculate x and y coordinates for the Tk root window
                    x = (ws / 2) - (w / 2)
                    y = (hs / 2) - (h / 2)

                    # set the dimensions of the screen
                    # and where it is placed
                    self.win2.geometry('%dx%d+%d+%d' % (w, h, x, y))

                    self.win2.resizable(False, False)

                    # Checks if Temperature is in range for both compounds, only continues if true
                    self.strChoices = "Ideal Mixture: \nIgnore Antoine Temperature Range: " \
                                      "\nUsing Component 2 as Basis: \nIsoBaric: \nIsoThermal:"
                    self.strAnswers = "{} \n{} \n{} \n{} \n{}".format(
                        self.chkbuttons.var_idl.get(),
                        self.chkbuttons.var_tRangeIgnore.get(),
                        self.chkbuttons.var_comp.get(), self.chkbuttons.var_IsoBar.get(),
                        self.chkbuttons.var_IsoTherm.get())

                    #display chosen constant variable
                    #color code true/false?
                    if self.chkbuttons.var_IsoBar.get():
                        self.strChoices = self.strChoices + "\nConstant Pressure :"
                        if self.inputs.ent_Pres.get():
                            self.strAnswers = self.strAnswers + "\n{} {}".format(self.inputs.ent_Pres.get(), self.inputs.presUnitVar.get())
                        else:
                            pUse = 0
                            if self.presUnitUse == 'atm':
                                pUse = self.pTot / 1.01325
                            elif self.presUnitUse == 'mmHg':
                                pUse = self.pTot / 1.01325 * 760
                            elif self.presUnitUse == 'Pa':
                                pUse = self.pTot * 100000
                            elif self.presUnitUse == 'kPa':
                                pUse = self.pTot * 100
                            else:
                                pUse = self.pTot
                            self.strAnswers = self.strAnswers + "\n{} {}".format(pUse, self.inputs.presUnitVar.get())
                    elif self.chkbuttons.var_IsoTherm.get():
                        self.strChoices = self.strChoices + "\nConstant Temperature :"
                        if self.inputs.ent_Temp.get():
                            self.strAnswers = self.strAnswers + "\n{} {}".format(self.inputs.ent_Temp.get(), self.inputs.tempUnitVar.get())
                        else:
                            tUse = 0
                            if self.tempUnitUse == '\u00b0C':
                                tUse = self.temp - 273.15
                            elif self.tempUnitUse == '\u00b0F':
                                tUse = (self.temp - 273.15) * 9 / 5 + 32
                            else:
                                tUse = self.temp
                            self.strAnswers = self.strAnswers + "\n{} {}".format(tUse, self.inputs.tempUnitVar.get())

                    # prints data and information about calculation, includes compounds and user choices
                    self.descFrm = tk.Frame(master=self.win2)
                    self.descFrm.pack(side="right", fill='y')
                    self.descTitle = tk.Label(master=self.descFrm, text="Mixture Information :",
                                              font=('Times New Roman', 18, 'bold', 'underline'))
                    self.chkChoices = tk.Label(master=self.descFrm, text=self.strChoices, justify='left',
                                               font=('Times New Roman', 16))
                    self.chkAnswers = tk.Label(master=self.descFrm, text=self.strAnswers, justify='left',
                                               font=('Times New Roman', 16))
                    self.nameComp1 = tk.Label(master=self.descFrm, text=(compObjList[0].name + ' :'),
                                              justify='left', font=('Times New Roman', 18, 'bold', 'underline'))
                    self.nameComp2 = tk.Label(master=self.descFrm, text=(compObjList[1].name + ' :'),
                                              justify='left', font=('Times New Roman', 18, 'bold', 'underline'))
                    self.descComp1 = tk.Label(master=self.descFrm, text=compObjList[0].description(),
                                              justify='left', font=('Times New Roman', 16))
                    self.descComp2 = tk.Label(master=self.descFrm, text=compObjList[1].description(),
                                              justify='left', font=('Times New Roman', 16))

                    self.descTitle.grid(row=0, column=0, sticky='w')

                    self.chkChoices.grid(row=1, column=0, sticky='w')
                    self.chkAnswers.grid(row=1, column=1, sticky='w')

                    self.nameComp1.grid(row=3, column=0, sticky='w')
                    self.descComp1.grid(row=4, column=0, sticky='w')

                    self.nameComp2.grid(row=6, column=0, sticky='w')
                    self.descComp2.grid(row=7, column=0, sticky='w')

                    self.descFrm.rowconfigure((2, 5), minsize=20)

                    self.dataFrm = tk.Frame(master=self.win2)
                    self.dataFrm.pack(side='bottom', fill='x')

                    self.dataTxt = tk.StringVar()
                    self.dataTxt.set('No Data Point Currently Selected')
                    self.pointDisplay = tk.Label(master=self.dataFrm, textvariable=self.dataTxt,
                                                 justify='left', font=('Times New Roman', 16), width=30)
                    self.pointDisplay.grid(row=0, column=1)

                    def data():
                        """Gets all data and displays to user, new window"""
                        # Display x vals, bub, and dew values in table using treeview

                        dataTbl = tk.Toplevel()

                        title = tk.Label(master=dataTbl, text="VLE Data", font=("Times New Roman", 30))
                        title.grid(row=0, columnspan=3)

                        tblFrm = tk.Frame(master=dataTbl)
                        tblFrm.grid(row=1, column=0, columnspan=2, padx=5)

                        # create Treeview with 3 columns
                        cols = ('Mole Fraction : ' + compObjList[0].name, 'Bubble Point', 'Dew Point')
                        listBox = ttk.Treeview(master=tblFrm, columns=cols, show='headings')
                        # set column headings
                        for col in cols:
                            listBox.heading(col, text=col)
                        listBox.pack(side='left')

                        if self.chkbuttons.var_IsoBar.get():
                            for i in range(0, len(self.xVals)):
                                listBox.insert("", "end", values=('%.3f' % (self.xVals[i]),
                                                                  '%.3f' % (self.tLB[i]), '%.3f' % (self.tLD[i])))
                        else: # Else: Isothermal
                            for i in range(0, len(self.xVals)):
                                listBox.insert("", "end", values=('%.3f' % (self.xVals[i]),
                                                                  '%.3f' % (self.pLB[i]), '%.3f' % (self.pLD[i])))

                        yscrollbar = ttk.Scrollbar(master=tblFrm, orient="vertical", command=listBox.yview)
                        yscrollbar.pack(side='right', fill='x')
                        listBox.configure(xscrollcommand=yscrollbar.set)

                        def close():
                            dataTbl.destroy()

                        closeBtn = tk.Button(master=dataTbl, text='Close Window', width=12, command=close)
                        closeBtn.grid(row=2, column=0, columnspan=3) # centered

                        dataTbl.protocol("WM_DELETE_WINDOW", close)  # window close protocol

                        dataTbl.focus_set()  # grabs focus
                        dataTbl.grab_set()  # locks interaction

                        dataTbl.update()

                        # Code from SO user - xxmbabanexx; sets open position for window based on screen dimensions
                        w = dataTbl.winfo_width() # width for the Tk root
                        h = dataTbl.winfo_height() + 5  # height for the Tk root

                        # get screen width and height
                        ws = dataTbl.winfo_screenwidth()  # width of the screen
                        hs = dataTbl.winfo_screenheight()  # height of the screen

                        # calculate x and y coordinates for the Tk root window
                        x = (ws / 2) - (w / 2)
                        y = (hs / 2) - (h / 2)

                        # set the dimensions of the screen
                        # and where it is placed
                        dataTbl.geometry('%dx%d+%d+%d' % (w, h, x, y))

                        dataTbl.wait_window()

                    self.dataBtn = tk.Button(master=self.dataFrm, text='Show All Data',
                                             activebackground="blue", width=12, command=data)
                    self.dataBtn.grid(row=0, column=3) # currently shifting locations based on str len

                    self.dataFrm.columnconfigure((0, 2), minsize=50)

                    # calculations
                    self.xVals = np.linspace(0, 1, self.inputs.specInput.get() + 1)  # add change specificity
                    self.yVals = np.linspace(0, 1, self.inputs.specInput.get() + 1)
                    if self.chkbuttons.var_IsoBar.get():
                        self.tLB = compObjList[0].bubbleIsoBar(self.xVals, compObjList, self.temp, self.pTot)
                        self.tLD = compObjList[0].dewIsoBar(self.yVals, compObjList, self.temp, self.pTot)
                        xPlot1 = self.tLB[0]
                        xPlot2 = self.tLD[0]
                        tempB = []
                        tempD = []
                        # convert calculated temperatures to user units
                        if self.tempUnitUse != 'K':
                            for i in range(0, len(self.tLB[0])):
                                if self.tempUnitUse == 'C':
                                    tempB.append(self.tLB[1][i] - 273.15)
                                elif self.tempUnitUse == 'F':
                                    tempB.append((self.tLB[1][i] - 273.15)*9/5 + 32)

                            for i in range(0, len(self.tLD[0])):
                                if self.tempUnitUse == 'C':
                                    tempD.append(self.tLD[1][i] - 273.15)
                                elif self.tempUnitUse == 'F':
                                    tempD.append((self.tLD[1][i] - 273.15) * 9 / 5 + 32)
                            self.tLB = tempB
                            self.tLD = tempD
                        else:
                            self.tLB = self.tLB[1]
                            self.tLD = self.tLD[1]

                        # plot
                        self.plottingIsoBar(xPlot1, self.tLB, xPlot2, self.tLD, compList)
                    elif self.chkbuttons.var_IsoTherm.get():
                        self.pLB = compObjList[0].bubbleIsoTherm(self.xVals, compObjList, self.temp)
                        self.pLD = compObjList[0].dewIsoTherm(self.yVals, compObjList, self.temp)
                        xPlot1 = self.pLB[0]
                        xPlot2 = self.pLD[0]
                        tempB = []
                        tempD = []

                        # convert calculated pressures to user units
                        if self.presUnitUse != 'bar':
                            for i in range(0, len(self.pLB[0])):
                                if self.presUnitUse == 'atm':
                                    tempB.append(self.pLB[1][i] / 1.01325)
                                elif self.presUnitUse == 'mmHg':
                                    tempB.append(self.pLB[1][i] / 1.01325 * 760)
                                elif self.presUnitUse == 'Pa':
                                    tempB.append(self.pLB[1][i] * 100000)
                                elif self.presUnitUse == 'kPa':
                                    tempB.append(self.pLB[1][i] * 100)

                            for i in range(0, len(self.pLD[0])):
                                if self.presUnitUse == 'atm':
                                    tempD.append(self.pLD[1][i] / 1.01325)
                                elif self.presUnitUse == 'mmHg':
                                    tempD.append(self.pLD[1][i] / 1.01325 * 760)
                                elif self.presUnitUse == 'Pa':
                                    tempD.append(self.pLD[1][i] * 100000)
                                elif self.presUnitUse == 'kPa':
                                    tempD.append(self.pLD[1][i] * 100)
                            self.pLB = tempB
                            self.pLD = tempD
                        else:
                            self.pLB = self.pLB[1]
                            self.pLD = self.pLD[1]

                        # plot
                        self.plottingIsoTherm(xPlot1, self.pLB, xPlot2, self.pLD, compList)

                    # Creates border inbetween text and plot
                    self.borderFrm = tk.Frame(master=self.win2, bg='black', width=2,
                                              height=self.win2.winfo_height()).pack(side="right")

                self.win2.mainloop()
            else:
                self.inputError = 0 # resets input error sentry
        except TempRangeError as e:
            self.tRangeError = 0 # resets error sentry
            e.__str__()
        except Exception as e: # general catch, for debugging
            print(e)


    # Getting Compound Data from NIST Webbook
    def antoineParameters(self, compound):
        link = "https://webbook.nist.gov/cgi/cbook.cgi?Name=" + compound + "&Units=SI"
        page = urlopen(link).read()
        soup = BeautifulSoup(page, features="html.parser")

        # Finds CAS registry number for compound listed
        allLi = soup.find_all('li')
        for i in range(0, len(allLi)):
            if ("CAS Registry Number:" in allLi[i].text):
                strCAS = allLi[i].text
                break
        numCAShyphen = strCAS[21:]  # Removes "CAS Registry Number: " from string
        numCAS = numCAShyphen.replace('-', '')  # Removes hyphens from number

        # Thermo Phase change data
        url = "https://webbook.nist.gov/cgi/cbook.cgi?ID=C" + numCAS + "&Units=SI&Mask=4#Thermo-Phase"
        htmlText = urlopen(url).read()
        soup = BeautifulSoup(htmlText, features="html.parser")
        try:
            Trange = []
            for i in soup.find_all("tr", {"class": "exp"}):
                if ('Antoine Equation Parameters' in i.parent.attrs.values()):
                    children = i.findChildren('td')
                    tabulatedVal = []
                    for j in range(0, len(children)):
                        if (children[j].text[0].isalpha() == False):
                            tabulatedVal.append(children[j].text)
                    Trange.append(tabulatedVal)
            if (Trange == []):
                raise AntoineError(compound)
            else:
                return Trange
        except AntoineError as e:
            e.__str__()

    # Get Boiling Point Data from NIST
    def boilPoint(self, compound):
        link = "https://webbook.nist.gov/cgi/cbook.cgi?Name=" + compound + "&Units=SI"
        page = urlopen(link).read()
        soup = BeautifulSoup(page, features="html.parser")

        # Finds CAS registry number for compound listed
        allLi = soup.find_all('li')
        for i in range(0, len(allLi)):
            if ("CAS Registry Number:" in allLi[i].text):
                strCAS = allLi[i].text
                break
        numCAShyphen = strCAS[21:]  # Removes "CAS Registry Number: " from string
        numCAS = numCAShyphen.replace('-', '')  # Removes hyphens from number

        # Thermo Phase change data
        url = "https://webbook.nist.gov/cgi/cbook.cgi?ID=C" + numCAS + "&Units=SI&Mask=4#Thermo-Phase"
        htmlText = urlopen(url).read()
        soup = BeautifulSoup(htmlText, features="html.parser")

        boilT = 0.0
        try:
            for i in soup.find_all("tr", {"class": "cal"}):
                if ('One dimensional data' in i.parent.attrs.values()):
                    children = i.findChildren('td')
                    for j in range(0, len(children)):
                        if (children[j].text == "Tboil"):
                            if (children[j + 1].text[0].isalpha() == False):
                                boilAll = children[j + 1].text
                                if (" ± " in boilAll):
                                    boilT = boilAll.split(" ± ")[0]
                                else:
                                    boilT = boilAll
            if boilT == 0:
                for i in soup.find_all("tr", {"class": "exp"}):
                    if 'One dimensional data' in i.parent.attrs.values():
                        children = i.findChildren('td')
                        for j in range(0, len(children)):
                            if children[j].text == "Tboil":
                                if children[j + 1].text[0].isalpha() == False:
                                    boilAll = children[j + 1].text
                                    if " ± " in boilAll:
                                        boilT = boilAll.split(" ± ")[0]
                                    else:
                                        boilT = boilAll
                if boilT == 0:
                    raise BoilPointError(compound)
                else:
                    return boilT
            else:
                return boilT
        except BoilPointError as e:
            e.__str__()

    def plottingIsoBar(self, xVals, tempListBub, yVals, tempListDew, compList):
        fig = Figure(figsize=(6, 6))
        a = fig.add_subplot(111)
        a.plot(xVals, tempListBub, linestyle='--', marker='o', color='red', label='Bubble Point Curve', picker=5)
        a.plot(yVals, tempListDew, linestyle='--', marker='o', color='blue', label='Dew Point Curve', picker=5)
        font = font_manager.FontProperties(family='Times New Roman', size=16)
        a.legend(loc='best', prop=font)
        fig.patch.set_facecolor('#F0F0F0')
        a.set_title("Isobaric VLE Diagram for Mixture:\n{} and {}".format(compList[0], compList[1]),
                    fontsize=18, fontname='Times New Roman')
        a.set_ylabel("Temperature ({})".format(self.inputs.tempUnitVar.get()), fontsize=16, fontname='Times New Roman')
        a.set_xlabel("Mole Fraction of Component 1: {}".format(compList[0]), fontsize=16, fontname='Times New Roman')

        canvas = FigureCanvasTkAgg(fig, master=self.win2)
        canvas.get_tk_widget().pack(side="left", fill='y')
        canvas.draw()

        """From matplotlib.org Object Picking example"""
        def onpick(event):
            thisline = event.artist
            xdata = thisline.get_xdata()
            ydata = thisline.get_ydata()
            ind = event.ind
            points = tuple(zip(xdata[ind], ydata[ind]))

            xVal = '%.3f' % (points[0][0])  # Truncates values to 3 decimal places
            yVal = '%.3f' % (points[0][1])

            self.dataTxt.set('Selected Point: (' + xVal + ', ' + yVal + ')')

        fig.canvas.mpl_connect('pick_event', onpick)

    def plottingIsoTherm(self, xVals, presListBub, yVals, presListDew, compList):
        fig = Figure(figsize=(6, 6))
        a = fig.add_subplot(111)
        # apparently deprecated picker
        a.plot(xVals, presListBub, linestyle='--', marker='o', color='red', label='Bubble Point Curve', picker=5)
        a.plot(yVals, presListDew, linestyle='--', marker='o', color='blue', label='Dew Point Curve', picker=5)
        font = font_manager.FontProperties(family='Times New Roman', size=16)
        a.legend(loc='best', prop=font)
        fig.patch.set_facecolor('#F0F0F0')
        a.set_title("Isothermal VLE Diagram for Mixture:\n{} and {}".format(compList[0], compList[1]), fontsize=18,
                    fontname='Times New Roman')
        a.set_ylabel("Pressure ({})".format(self.inputs.presUnitVar.get()), fontsize=16, fontname='Times New Roman')
        a.set_xlabel("Mole Fraction of Component 1: {}".format(compList[0]), fontsize=16, fontname='Times New Roman')

        canvas = FigureCanvasTkAgg(fig, master=self.win2)
        canvas.get_tk_widget().pack(side="left", fill='y')
        canvas.draw()

        """From matplotlib.org Object Picking example""" ## Clicking on line selects connected point, need fix
        def onpick(event):
                thisline = event.artist
                xdata = thisline.get_xdata()
                ydata = thisline.get_ydata()
                ind = event.ind
                points = tuple(zip(xdata[ind], ydata[ind]))

                xVal = '%.3f' % (points[0][0]) # Truncates values to 3 decimal places
                yVal = '%.3f' % (points[0][1])

                self.dataTxt.set('Selected Point: (' + xVal + ', ' + yVal + ')')

        fig.canvas.mpl_connect('pick_event', onpick)


# Custom Errors
class InputError(Exception):
    """ Error Raised when user inputs are missing: Compound names
    Attributes:
        missing -- which compound(s) is/are missing
    """

    def __init__(self, missing):
        self.missing = missing

    def __str__(self):
        message = 'The Following Required User Input is Missing: '
        ErrorPopUp(message, self.missing)
        return


class AntoineError(Exception):
    """ Error raised when an problem occurs in web scrapping for Antoine Equation data
    Attributes:

    """

    def __init__(self, compound):
        self.compound = compound

    def __str__(self):
        message = 'No Antoine Parameter Data Found for the Following Compound: '
        ErrorPopUp(message, self.compound)
        return


class TempRangeError(Exception):
    """ Error raised when the specified temperature is not within the Antoine Data. Only Applicable when "Ignore Antoine
    Range" is NOT selected
    Attributes:
        Compound -- Which Compound caused the error
        Temp -- What temperature wasn't in any Antoine Parameter ranges
        Units -- Units for temperature
    """

    def __init__(self, compound, temp, units):
        self.compound = compound
        self.temp = temp
        self.units = units

    def __str__(self): # add color to user inputs
        message = 'No Antoine Parameters Could Be Found For the Following: '
        errorCombined = self.compound + ' at ' + str(self.temp) + ' ' + self.units
        ErrorPopUp(message, errorCombined)
        return


class BoilPointError(Exception):
    """ Error raised if the boiling point of a compound can't be found ## is this needed anymore?
    Attributes:
        Compound -- Which Compound caused the error
    """

    def __init__(self, compound):
        self.compound = compound

    def __str__(self): # add color to user inputs
        message = 'The Boiling Point for the Following Compound Could Not Be Found: '
        ErrorPopUp(message, self.compound)
        return


# Customs MessageBox for color purposes
class ErrorPopUp:
    def __init__(self, message, compound, *args, **kwargs):
        self.errorBox = tk.Toplevel()

        self.errorBox.title('Error')

        self.errFrame = tk.Frame(master=self.errorBox, bg='#f0f0f0')
        self.errFrame.grid(row=0, column=0)

        self.errorMsgLbl = tk.Label(master=self.errFrame, text=message, font=('Times New Roman', 12), fg='black')
        self.errorMsgLbl.grid(row=0, column=0, padx=5)

        self.errorCompLbl = tk.Label(master=self.errFrame, text=compound, font=('Times New Roman', 12), fg='red')
        self.errorCompLbl.grid(row=1, column=0, padx=5)

        self.btnFrame = tk.Frame(master=self.errorBox, bg='#c0c0c0')
        self.btnFrame.grid(row=1, column=0, sticky='NESW')

        self.okBtn = tk.Button(master=self.btnFrame, text='Ok', command=self.ok, activebackground="blue",
                               font=('Times New Roman', 12))
        self.okBtn.grid(row=0, column=4, sticky='EW', pady=5)

        self.btnFrame.columnconfigure([0, 1, 2, 3, 4, 5], weight=1)
        self.errorBox.rowconfigure(0, weight=2)

        self.errorBox.bind('<Return>', self.okEnt) # binds return/enter key to ok btn

        self.errorBox.protocol("WM_DELETE_WINDOW", self.ok) # window close protocol

        self.errorBox.focus_set() # grabs focus
        self.errorBox.grab_set() # locks interaction to error window

        self.errorMsgLbl.update()

        # Code from SO user - xxmbabanexx; sets open position for window based on screen dimensions
        w = self.errorMsgLbl.winfo_width() + 10  # width for the Tk root, adjusts to size of error message + padding
        h = 128  # height for the Tk root

        # get screen width and height
        ws = self.errorBox.winfo_screenwidth()  # width of the screen
        hs = self.errorBox.winfo_screenheight()  # height of the screen

        # calculate x and y coordinates for the Tk root window
        x = (ws / 2) - (w / 2)
        y = (hs / 2) - (h / 2)

        # set the dimensions of the screen
        # and where it is placed
        self.errorBox.geometry('%dx%d+%d+%d' % (w, h, x, y))

        self.errorBox.wait_window()

    def ok(self):
        self.errorBox.destroy()

    def okEnt(self, event):
        self.ok()


def runApp():
    root = tk.Tk()

    # Code from SO user - xxmbabanexx; sets open position for window based on screen dimensions
    w = 1024  # width for the Tk root
    h = 320  # height for the Tk root

    # get screen width and height
    ws = root.winfo_screenwidth()  # width of the screen
    hs = root.winfo_screenheight()  # height of the screen

    # calculate x and y coordinates for the Tk root window
    x = (ws / 2) - (w / 2)
    y = (hs / 2) - (h / 2)

    # set the dimensions of the screen
    # and where it is placed
    root.geometry('%dx%d+%d+%d' % (w, h, x, y))

    MainApplication(root).pack()
    root.mainloop()

if __name__ == '__main__':
    runApp()


"""
Recent Updates: 
- Now plots dotted lines in between points
- Code cleaned up

Issues:
- Error "local variable 'strCAS' referenced before assignment"; likely when input is not a real compound, happens when error occurs first before retry
- AntoineError - leads to "object of type 'NoneType' has no len()"
^^^ probably fixed by hard resetting after error
- "'StringVar' object has no attriute 'tk'" when running isoTherm
- Clicking on plotted lines displays point values
- plotting: matplotlib picker deprecation warning
"""
