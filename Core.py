import os

import datetime

import string

import subprocess

from itertools import *

from threading import Thread

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import messagebox as msgbox


class FuzzerGUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.bSignal = False

        self.title("FUZZING TOOL")
        self.resizable(False, False)

        selectorGroup = tk.LabelFrame(self, padx=5, pady=5, text="Выбор файла")
        selectorGroup.pack(padx=10, pady=5)

        self.FilePath = tk.Entry(selectorGroup, width = 80)
        self.FilePath.grid(row=0)

        tk.Button(selectorGroup, text = "...", command = self.FileSelectHandler).grid(row=0, column=1, sticky=tk.W)

        settingsGroup = tk.LabelFrame(self, padx=5, pady=5, text="Параметры")
        settingsGroup.pack(padx=10, pady=5)

        tk.Label(settingsGroup, text = "Максимальная длина: ").grid(row=0)

        self.Lim = tk.Spinbox(settingsGroup, from_=1, to=10000)
        self.Lim.grid(row=0, column=1, sticky=tk.W)
        self.Lim.insert(0, 1)

        tk.Label(settingsGroup, text = "Режим перебора: ").grid(row=1)

        self.box_mode = ttk.Combobox(settingsGroup, 
                                     values=[
                                        "1 -> N", 
                                            "ВСЕ СРАЗУ",
                                            "1 <- N"],
                                    state="readonly")
        self.box_mode.grid(row=1, column=1, sticky=tk.W)
        self.box_mode.current(0)

        tk.Label(settingsGroup, text = "Таймаут (сек.): ").grid(row=2)

        self.Timeout = tk.Spinbox(settingsGroup, from_=1, to=10000)
        self.Timeout.grid(row=2, column=1, sticky=tk.W)


        genGroup = tk.LabelFrame(self, padx=5, pady=5, text="Генератор")
        genGroup.pack(padx=10, pady=5)

        tk.Label(genGroup, text = "Длина: ").grid(row=0)

        self.GenLen = tk.Spinbox(genGroup, from_=1, to=10000)
        self.GenLen.grid(row=0, column=1, sticky=tk.W)
        self.GenLen.insert(0, 1)

        self.btn_gen = tk.Button(genGroup, text="СКОПИРОВАТЬ")
        self.btn_gen.configure(command = lambda: self.GenArgHandler(int(self.GenLen.get())))
        self.btn_gen.grid(row=0, column=2, sticky=tk.W)


        resGroup = tk.LabelFrame(self, width=500, padx=5, pady=5, text="Результаты")
        resGroup.pack(padx=10, pady=5)

        self.label_status = tk.Label(resGroup, text="N/A")
        self.label_status.grid(row=0, column=0, sticky=tk.W)


        self.argsGroup = tk.LabelFrame(self, padx = 5, pady = 5, text = "Аргументы")
        self.argsGroup.pack(padx=10, pady=5)

        self.Args = 0
        self.NumLabels = list()
        self.PrefixEdits = list()
        self.ArgEdits = list()
        self.QuoteBoxes = list()
        self.FuzzBoxes = list()

        self.QuoteVars = list()
        self.FuzzVars = list()

        self.btn_add = tk.Button(self, text="Добавить аргумент", command=self.AddArgHandler)
        self.btn_add.pack(padx=10, pady=10, side=tk.RIGHT)

        self.btn_rem = tk.Button(self, text="Удалить аргумент", command=self.RemArgHandler)
        self.btn_rem.pack(padx=10, pady=10, side=tk.RIGHT)
        self.btn_rem["state"] = "disabled"

        self.btn_work = tk.Button(self, text="ПУСК", background="#0f0", command=self.WorkHandler)
        self.btn_work.pack(padx=10, pady=10, side=tk.LEFT)

        self.btn_stop = tk.Button(self, text="СТОП", background="#f00", command=self.StopHandler)
        self.btn_stop.pack(padx=1, pady=5, side=tk.LEFT)
        self.btn_stop["state"] = "disabled"

        self.AddArgHandler()

        self.Centerpoint()

    def Centerpoint(self):
        self.eval('tk::PlaceWindow . center')

        #self.update_idletasks()
        #width = self.winfo_width()
        #frm_width = self.winfo_rootx() - self.winfo_x()
        #win_width = width + 2 * frm_width
        #height = self.winfo_height()
        #titlebar_height = self.winfo_rooty() - self.winfo_y()
        #win_height = height + titlebar_height + frm_width
        #x = self.winfo_screenwidth() // 2 - win_width // 2
        #y = self.winfo_screenheight() // 2 - win_height // 2
        #self.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        #self.deiconify()

        return

    def FileSelectHandler(self):
        file_name = fd.askopenfilename()
        self.FilePath.insert(0, file_name)
        return

    def CheckChanged(self, inst):
        ind = self.FuzzBoxes.index(inst)

        if (self.FuzzVars[ind] == 0):
            self.FuzzVars[ind] = 1
        else:
            self.FuzzVars[ind] = 0

        if (self.FuzzVars[ind] == 1):
            self.ArgEdits[ind]["state"] = "disabled"
        else:
            self.ArgEdits[ind]["state"] = "normal"

        return

    def GenArgHandler(self, iLen):
        self.SetClipBoard(str(self.GenSeq(iLen)))
        return

    def AddArgHandler(self):
        tmp = tk.Label(self.argsGroup, text = str(self.Args + 1) + ":")
        tmp.grid(row=self.Args)
        self.NumLabels.append(tmp)

        tmp = tk.Entry(self.argsGroup, width = 10)
        tmp.grid(row=self.Args, column=1, sticky=tk.W)
        self.PrefixEdits.append(tmp)

        tmp = tk.Entry(self.argsGroup, width = 50)
        tmp.grid(row=self.Args, column=2, sticky=tk.W)
        self.ArgEdits.append(tmp)

        self.QuoteVars.append(tk.IntVar())

        tmp = tk.Checkbutton(self.argsGroup, text = "QUOTE", onvalue = 1, offvalue = 0, variable = self.QuoteVars[-1])
        tmp.grid(row=self.Args, column=3, sticky=tk.W)
        self.QuoteBoxes.append(tmp)

        self.FuzzVars.append(0)

        tmp = tk.Checkbutton(self.argsGroup, text = "FUZZ", onvalue = 1, offvalue = 0)
        tmp.grid(row=self.Args, column=4, sticky=tk.W)
        self.FuzzBoxes.append(tmp)
        tmp.configure(command = lambda: self.CheckChanged(tmp))

        self.Args += 1

        if (self.Args > 1):
            self.btn_rem["state"] = "active"

        return

    def SetClipBoard(self, text):
        command = 'echo | set /p nul=' + text.strip() + '| clip'
        os.system(command)

        return

    def RemArgHandler(self):
        self.NumLabels.pop().grid_forget()
        self.PrefixEdits.pop().grid_forget()
        self.ArgEdits.pop().grid_forget()
        self.QuoteBoxes.pop().grid_forget()
        self.FuzzBoxes.pop().grid_forget()
        self.FuzzVars.pop()

        self.Args -= 1

        if (self.Args == 1):
            self.btn_rem["state"] = "disabled"

        return

    def InitArgs(self):
        aResult = list()
        aIndexMap = list()

        aResult.append(self.FilePath.get())

        for i in range(len(self.NumLabels)):
            if (self.PrefixEdits[i].get()):
                aResult.append(self.PrefixEdits[i].get())

            if (self.FuzzVars[i] == 0): # NOT FUZZ
                aResult.append(self.ArgEdits[i].get() if (self.QuoteVars[i].get() == 0) else "\"" + self.ArgEdits[i].get() + "\"")
            else: # FUZZ
                aIndexMap.append(len(aResult))
                aResult.append("")

        if (len(aIndexMap) > 0):
            self.thread = Thread(target=self.Worker, args=(self.box_mode.current(), self.Timeout.get(), self.Lim.get(), aResult, aIndexMap,))
            self.thread.start()
        else:
            try:
                sResult = subprocess.run(aResult, timeout=int(self.Timeout.get()))
            except subprocess.TimeoutExpired:
                self.label_status.config(text = "Время выполнения истекло.")            
            except OSError as error :
                self.label_status.config(text = error)
            except Exception as error:
                if (sResult == None):
                    self.label_status.config(text = "Исключение: " + error)
                else:
                    self.label_status.config(text = error)

                return
            else:
                self.label_status.config(text = "Програма завершилась успешно!\nReturn code: " + str(sResult.returncode))

            self.btn_work["state"] = "normal"
            self.btn_stop["state"] = "disabled"            

    def Worker(self, mode, delay, lim, args, indexMap):
        now = datetime.datetime.now()
        
        f = open(now.strftime("%d-%m-%Y (%H.%M)") + ".log", 'w')
        
        f.write(".:[FUZZING TOOL]:.\nФормат записи. Строки экранированы. Ординарные кавычки НЕ ЯВЛЯЮТСЯ частью аргумента!\n['Приложение', 'Аргумент 1', 'Аргумент 2', 'Аргумент 3', ..., 'Аргумент N']\n\n")
        
        if (mode == 0): # 1 -> N
            for tCombination in combinations_with_replacement(range(1, int(lim) + 1), len(indexMap)):
                iAppend = 0

                for i in range(0, len(indexMap)):
                    args[indexMap[i]] = self.GenSeq(tCombination[::-1][i], iAppend)
                    iAppend += tCombination[::-1][i]

                f.write(str(args) + '\n')

                sResult = None

                try:
                    sResult = subprocess.run(args, timeout=int(delay))
                except subprocess.TimeoutExpired:
                    if (sResult == None):
                        self.label_status.config(text = "Перебор: (" + str(tCombination) + ")\nВремя выполнения истекло.")
                        f.write("Время выполнения истекло"  + '\n')
                    else:
                        self.label_status.config(text = "Перебор: (" + str(tCombination) + ")\nВремя выполнения истекло.\nReturn code: " + str(sResult.returncode))
                        f.write("Время выполнения истекло. Return code: " + str(sResult.returncode)  + '\n')
                        if (sResult.returncode != 0):
                            self.btn_work["state"] = "normal"
                            self.btn_stop["state"] = "disabled"

                            self.SetClipBoard(str(args))
                            
                            f.close()
                            return
                except OSError as error :
                    self.label_status.config(text = error)
                    f.write("OSError. " + str(error) + '\n')
                    self.btn_work["state"] = "normal"
                    self.btn_stop["state"] = "disabled"
                    f.close()
                    return
                except Exception as error:
                    f.write("Исключение: " + str(error) + '\n')
                    if (sResult == None):
                        self.label_status.config(text = "Исключение: " + error)
                    else:
                        self.label_status.config(text = error)

                    self.btn_work["state"] = "normal"
                    self.btn_stop["state"] = "disabled"
                    
                    f.close()
                    return
                else:
                    self.label_status.config(text = "Перебор: (" + str(tCombination) + ")\nReturn code: " + str(sResult.returncode))
                    f.write("Return code: " + str(sResult.returncode) + '\n')

                    if (sResult.returncode != 0):
                        self.btn_work["state"] = "normal"
                        self.btn_stop["state"] = "disabled"

                        self.SetClipBoard(str(args))
                        
                        f.close()
                        return

                if (self.bSignal):
                    self.bSignal = False
                    self.label_status.config(text = "ПЕРЕБОР ОСТАНОВЛЕН ПОЛЬЗОВАТЕЛЕМ...")
                    f.close()
                    return

        elif (mode == 1): # ВСЁ СРАЗУ
            for l in range(1, int(lim) + 1):
                iAppend = 0

                for i in range(0, len(indexMap)):
                    args[indexMap[i]] = self.GenSeq(l, iAppend)
                    iAppend += l

                f.write(str(args) + '\n')

                sResult = None

                try:
                    sResult = subprocess.run(args, timeout=int(delay))
                except subprocess.TimeoutExpired:
                    if (sResult == None):
                        self.label_status.config(text = "Перебор: (" + str(l) + ")\nВремя выполнения истекло.")
                        f.write("Время выполнения истекло" + '\n')
                    else:
                        self.label_status.config(text = "Перебор: (" + str(l) + ")\nВремя выполнения истекло.\nReturn code: " + str(sResult.returncode))
                        f.write("Время выполнения истекло. Return code: " + str(sResult.returncode) + '\n')
                        if (sResult.returncode != 0):
                            self.btn_work["state"] = "normal"
                            self.btn_stop["state"] = "disabled"

                            self.SetClipBoard(str(args))
                            
                            f.close()
                            return
                except OSError as error :
                    self.label_status.config(text = error)
                    f.write("OSError. " + str(error) + '\n')
                    self.btn_work["state"] = "normal"
                    self.btn_stop["state"] = "disabled"
                    f.close()
                    return
                except Exception as error:
                    f.write("Исключение: " + str(error) + '\n')
                    if (sResult == None):
                        self.label_status.config(text = "Исключение: " + error)
                    else:
                        self.label_status.config(text = error)

                    self.btn_work["state"] = "normal"
                    self.btn_stop["state"] = "disabled"
                    
                    f.close()
                    return
                else:
                    self.label_status.config(text = "Перебор: (" + str(l) + ")\nReturn code: " + str(sResult.returncode))
                    f.write("Return code: " + str(sResult.returncode) + '\n')

                    if (sResult.returncode != 0):
                        self.btn_work["state"] = "normal"
                        self.btn_stop["state"] = "disabled"

                        self.SetClipBoard(str(args))
                        
                        f.close()
                        return

                if (self.bSignal):
                    self.bSignal = False
                    self.label_status.config(text = "ПЕРЕБОР ОСТАНОВЛЕН ПОЛЬЗОВАТЕЛЕМ...")
                    f.close()
                    return

        else: # 1 <- N
            for tCombination in combinations_with_replacement(range(1, int(lim) + 1), len(indexMap)):
                iAppend = 0

                for i in range(0, len(indexMap)):
                    args[indexMap[i]] = self.GenSeq(tCombination[i], iAppend)
                    iAppend += tCombination[i]

                f.write(str(args) + '\n')

                sResult = None

                try:
                    sResult = subprocess.run(args, timeout=int(delay))
                except subprocess.TimeoutExpired:
                    if (sResult == None):
                        self.label_status.config(text = "Перебор: (" + str(tCombination) + ")\nВремя выполнения истекло.")
                        f.write("Время выполнения истекло" + '\n')
                    else:
                        self.label_status.config(text = "Перебор: (" + str(tCombination) + ")\nВремя выполнения истекло.\nReturn code: " + str(sResult.returncode))
                        f.write("Время выполнения истекло. Return code: " + str(sResult.returncode) + '\n')
                        if (sResult.returncode != 0):
                            self.btn_work["state"] = "normal"
                            self.btn_stop["state"] = "disabled"

                            self.SetClipBoard(str(args))
                            
                            f.close()
                            return
                except OSError as error :
                    self.label_status.config(text = error)
                    f.write("OSError. " + str(error) + '\n')
                    self.btn_work["state"] = "normal"
                    self.btn_stop["state"] = "disabled"
                    f.close()
                    return
                except Exception as error:
                    f.write("Исключение: " + str(error) + '\n')
                    if (sResult == None):
                        self.label_status.config(text = "Исключение: " + error)
                    else:
                        self.label_status.config(text = error)

                    self.btn_work["state"] = "normal"
                    self.btn_stop["state"] = "disabled"
                    
                    f.close()
                    return
                else:
                    self.label_status.config(text = "Перебор: (" + str(tCombination) + ")\nReturn code: " + str(sResult.returncode))
                    f.write("Return code: " + str(sResult.returncode) + '\n')

                    if (sResult.returncode != 0):
                        self.btn_work["state"] = "normal"
                        self.btn_stop["state"] = "disabled"

                        self.SetClipBoard(str(args))
                        
                        f.close()
                        return

                if (self.bSignal):
                    self.bSignal = False
                    self.label_status.config(text = "ПЕРЕБОР ОСТАНОВЛЕН ПОЛЬЗОВАТЕЛЕМ...")
                    f.close()
                    return

        self.label_status.config(text = "ПЕРЕБОР ЗАВЕРШЁН...")

        self.btn_work["state"] = "normal"
        self.btn_stop["state"] = "disabled"
        f.close()
        return

    def WorkHandler(self):
        if(not os.path.isfile(self.FilePath.get()) or not os.access(self.FilePath.get(), os.X_OK)):
            msgbox.showerror("Eггoг", "Файл не существует или не является исполняемым!")
            return -1

        self.btn_work["state"] = "disabled"
        self.btn_stop["state"] = "normal"

        self.InitArgs()
        return

    def StopHandler(self):
        self.btn_stop["state"] = "disabled"
        self.btn_work["state"] = "normal"
        self.bSignal = True
        return

    def GenSeq(self, iLen, iSled = 0):
        iGen = 0

        sRes = ""

        for U in string.ascii_uppercase:
            for L in string.ascii_lowercase:
                for N in range(10):
                    iGen += 1
                    if (iGen > iSled):
                        sRes += U

                    if (iGen == (iLen + iSled)):
                        return sRes

                    iGen += 1
                    if (iGen > iSled):
                        sRes += L

                    if (iGen == (iLen + iSled)):
                        return sRes

                    iGen += 1
                    if (iGen > iSled):
                        sRes += str(N)

                    if (iGen == (iLen + iSled)):
                        return sRes

        return sRes

if __name__ == "__main__": # EP
    app = FuzzerGUI()
    app.mainloop()
