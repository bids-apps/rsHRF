from ..misc.status        import Status
from datetime             import datetime
from tkinter              import Toplevel, BOTH, INSERT
from tkinter.scrolledtext import ScrolledText

class LoggingWindow():
    def __init__(self):
        window = Toplevel(bg='white')
        window.title("Logger")
        # get screen width and height
        screen_width  = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        window.geometry("600x400+%d+%d" % (screen_width-600, 0))
        self.lineNum  = 1
        self.text     = ScrolledText(window, background='black')
        self.text.pack(fill=BOTH, expand = 1)

    def putLog(self, plotables=None, data_info=None, status=None):
        # writing current time
        current_time = datetime.now().strftime("%H:%M:%S")

        if status is not None:
            if status.get_state():
                message = status.get_info()
                self.text.insert(INSERT, \
                    ">> " + current_time + "\t SUCCESS " + message + "\n"
                )
                self.text.tag_add("success", str(self.lineNum) + ".12", str(self.lineNum) + ".20")
                self.text.tag_config("success", foreground="green")
                self.text.tag_add("success message", str(self.lineNum) + ".20", str(self.lineNum) + "." + str(21 + len(message)))
                self.text.tag_config("success message", foreground="LightBlue1")
            else:
                message = status.get_error()
                self.text.insert(INSERT, \
                    ">> " + current_time + "\t ERROR " + message + "\n"
                )
                self.text.tag_add("error", str(self.lineNum) + ".12", str(self.lineNum) + ".18")
                self.text.tag_config("error", foreground="red")
                self.text.tag_add("error message", str(self.lineNum) + ".18", str(self.lineNum) + "." + str(19 + len(message)))
                self.text.tag_config("error message", foreground="yellow")    
            self.text.tag_add("time", str(self.lineNum) + ".03", str(self.lineNum) + ".11")
            self.text.tag_config("time", foreground="PeachPuff2")
            self.lineNum += 1

            dic = status.get_dic()
            for each in dic.keys():
                self.text.insert(INSERT, \
                    ">> " + current_time + "\t" + each + str(dic[each]) + "\n"
                )
                self.text.tag_add("time", str(self.lineNum) + ".03", str(self.lineNum) + ".11")
                self.text.tag_config("time", foreground="PeachPuff2")
                self.text.tag_add("dic_label", str(self.lineNum) + ".12", str(self.lineNum) + "." + str(12+len(each)))
                self.text.tag_config("dic_label", foreground="azure")
                self.lineNum += 1
            self.text.insert(INSERT, "\n")
            self.lineNum += 1
            return

        elif plotables is not None:
            self.text.insert(INSERT, \
                ">> " + current_time + "\t Time Series' Information \n\n" + \
                    "TYPE" + "\t\t\t\t\t\t LENGTH" + "\t\t NUMBER OF VOXELS \n\n"
                )
            self.text.tag_add("labels", str(self.lineNum) + ".12", str(self.lineNum) + "." + str(37))
            self.text.tag_config("labels", foreground="PaleTurquoise1")
            self.text.tag_add("titles", str(self.lineNum+2) + ".00", str(self.lineNum+2) + "." + str(37))
            self.text.tag_config("titles", foreground="azure")
            self.text.tag_add("time", str(self.lineNum) + ".03", str(self.lineNum) + ".11")
            self.text.tag_config("time", foreground="PeachPuff2")
            for each in plotables:
                self.text.insert(INSERT, \
                    each[0] + "\t\t\t\t\t\t " + str(each[1].shape[0]) + "\t\t " + str(each[1].shape[1]) + "\n"
                    )
                self.lineNum += 1
            self.text.insert(INSERT, "\n")
            self.lineNum += 5
            return
        
        elif data_info is not None:
            self.text.insert(INSERT, \
                ">> " + current_time + "\t Information \n\n")
            self.text.tag_add("labels", str(self.lineNum) + ".12", str(self.lineNum) + "." + str(37))
            self.text.tag_config("labels", foreground="PaleTurquoise1")
            self.text.tag_add("time", str(self.lineNum) + ".03", str(self.lineNum) + ".11")
            self.text.tag_config("time", foreground="PeachPuff2")
            self.lineNum += 2
            if data_info["Type"] == "BOLD":
                self.text.insert(INSERT, \
                    "   :- " + "Type of Data: BOLD Time Series\n" + 
                    "   :- " + "Subject: " + data_info["Subject"] + "\n"
                    "   :- " + "Input File: " + data_info["Input File"] + "\n"
                    )
                self.lineNum += 1
            elif data_info["Type"] == "Preprocessed-BOLD":
                self.text.insert(INSERT, \
                    "   :- " + "Type of Data: Preprocessed-BOLD Time Series\n" + 
                    "   :- " + "Subject: " + data_info["Subject"] + "\n" +
                    "   :- " + "Mask File: " + data_info["Mask File"] + "\n" + 
                    "   :- " + "Associated Raw BOLD: " + data_info["Associated Raw BOLD"] + "\n"
                    )
                self.lineNum += 2
            elif data_info["Type"] == "HRF":
                self.text.insert(INSERT, \
                    "   :- " + "Type of Data: Hemodynamic Response Function Time Series\n" + 
                    "   :- " + "Associated BOLD: " + data_info["Associated BOLD"] + "\n"
                    )
            elif data_info["Type"] == "Deconvolved-BOLD":
                self.text.insert(INSERT, \
                    "   :- " + "Type of Data: Deconvolved BOLD Time Series\n" + 
                    "   :- " + "Associated HRF: " + data_info["Associated HRF"] + "\n"
                    )
            self.text.tag_config("type", foreground="azure")
            self.text.tag_config("line2", foreground="azure")
            self.lineNum += 2 
            self.text.insert(INSERT, \
                    "   :- " + "\t\t\tAssociated Parameters\n" 
                    )
            self.text.tag_add("ap", str(self.lineNum) + ".03", str(self.lineNum) + ".30")
            self.text.tag_config("ap", foreground="Khaki1")
            self.lineNum += 1
            for each in data_info["Parameters"].keys():
                self.text.insert(INSERT, \
                    "\t\t" + each + "\t\t\t=\t\t" + str(data_info["Parameters"][each]) + "\n")
                self.text.tag_add("pv", str(self.lineNum) + ".00", str(self.lineNum) + "." + str(6+len(each)))
                self.text.tag_config("pv", foreground="LemonChiffon2")
                self.lineNum +=1
            self.text.insert(INSERT, "\n")
            self.lineNum += 1
            return