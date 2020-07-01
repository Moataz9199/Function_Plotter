
#Import the Libraries that i need
import numpy as Nump
from sympy import *
import re
from PySide2.QtWidgets import *
import sys
from pyqtgraph import *

#Create Class Window that inherited from class QWidget in PySide2 Library
class Window(QWidget):
    #Define the Constructor Function
    def __init__(self):
        super().__init__()  ##use the same init function of the parent Class (QWidget)

        self.setWindowTitle("Function Plotter")  #Set the Window Title
        self.setGeometry(300, 300, 500, 400)  #Specify the Geometry of the Window
        self.setFixedSize(665,753)  #Set The window as fixed Size
        w = QWidget(self)  #create the widget
        l = QFormLayout(w)  #Choose the Layout of the window

        #Create 3 Text Fields to be filled by the user F(x) , xmin , xmax
        self.txt1 = QLineEdit();
        self.txt2 = QLineEdit();
        self.txt3 = QLineEdit();

        #Create Button.
        self.b1 = QPushButton("Plot")

        #Adding 3 rows in the window each row includes text field to be filled by the user
        l.addRow('F(x)', self.txt1)
        l.addRow('x Minimum Value', self.txt2)
        l.addRow('x Maximum Value', self.txt3)

        #Execute the Function FUNCT when the button pushed
        self.b1.clicked.connect(lambda: self.FUNCT())

        #Create progressbar that will describe how much from the operation done, and set the min and max value of the progressbar
        self.progressbar = QProgressBar()
        self.progressbar.setMinimum(0)
        self.progressbar.setMaximum(100)
        self.progressbar.setValue(0)

        #Create Combobox that the user can choose from several items, we create 2 combo boxes one to background color & curve color.
        self.cb = QComboBox()
        self.cb.addItems(["Black", "White"]) #Adding items that the user will choose from them
        l.addRow('Select Plotting Graph Background', self.cb)

        self.cb2 = QComboBox()
        self.cb2.addItems(["Green", "Red", "Blue"])#Adding items that the user will choose from them
        l.addRow('Select Curve Color', self.cb2) #Create row to the combo box that we create.

        self.cb3 = QComboBox()
        self.cb3.addItems(["Append", "Replace"])#Adding items that the user will choose from them
        l.addRow('Plotting Type', self.cb3) #Create row to the combo box that we create.

        #add the button and the progress bar to the widget
        l.addRow(self.b1)
        l.addRow('Progress:', self.progressbar)

        self.graphWidget = PlotWidget()   #Create Widget for the graph

        self.graphWidget.showGrid(x=True, y=True)  #Showing Grids

        # Set the position, color,font, and name of the labels
        self.graphWidget.setLabel('left', "<span style=\"color:red;font-size:20px\">F(x)</span>")
        self.graphWidget.setLabel('bottom', "<span style=\"color:red;font-size:20px\">x</span>")

        l.addRow(self.graphWidget)  #add the graph widget

    ## Function that will take the string and count how many times operation "^" exist in the string and return the number of occurence.
    def Number_Of_Powers(self, Function):
        counter = 0;
        for Char in Function:
            if Char == "^":
                counter = counter + 1
        return counter

    ##Taking string and replace every "^" by "**", as "^" is not supported by python math. operations.
    def Modifying_Powers(self, Function, Number_Of_Powers):
        return Function.replace("^", "**", Number_Of_Powers)

    #Function looping on the string, and detect any character that not identified by the program and return  list contains flag &characters unidentified.
    def Checking_UnIdentified_Characters(self, Function):
        Identified_Characters = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "*", "^", "/", "+", "-", "x", " " , ")" , "("]
        UnIdentified_Characters = [False]
        for Char in Function:
            if Char in Identified_Characters:
                continue
            else:
                UnIdentified_Characters[0] = True
                if Char not in UnIdentified_Characters:
                    UnIdentified_Characters.append(Char)
        return UnIdentified_Characters

    #Function looping on the string, and detect if any operation has a missing operand and return list contains flag & and terms that include the error
    def Multiply_Divide_By_Nothing_Error(self, Function):
        M_D_Error = [False]
        for index in range(0, len(Function)):
            Last_Char_Index = len(Function[index]) - 1
            if Function[index] == "":
                continue
            elif Function[index][0] == "*" or Function[index][0] == "/" or Function[index][0] == "^" or Function[index][
                Last_Char_Index] == "*" or Function[index][Last_Char_Index] == "/" or Function[index][
                Last_Char_Index] == "^":
                M_D_Error[0] = True
                M_D_Error.append(Function[index])
        return M_D_Error

    #Function Looping on the string, and detect if the number is followed by variable e.g 12x, and return list contains flag & terms that include the error
    def Number_Followed_By_Variable_Error(self,Function):
        Identified_Numbers = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        Idenified_Operations = "*/+-^)"
        N_Vari_Error = [False]
        for index in range(0, len(Function)):
            for Char in Function[index]:
                if Char in Identified_Numbers or Char == ")":
                    Index_Of_Next_Char = Function[index].index(Char) + 1
                    if Index_Of_Next_Char < len(Function[index]):
                        if Function[index][Index_Of_Next_Char] == "x" or ((Function[index][Index_Of_Next_Char] not in Idenified_Operations)):
                            N_Vari_Error[0] = True
                            N_Vari_Error.append(Function[index])
        return N_Vari_Error

    #Function Looping on the string, and detect if any operation repeated more than one time e.g (***,//,+++,--,etc.), and return list contains flag & the operations that repeated
    def Repeated_Operation_Error(self,Function):
        Repeated_Op_Error = [False]
        for index in range(0, len(Function)):
            if "**" in Function[index] or "//" in Function[index] or "^^" in Function[index] or Function[index] == "" or "()" in Function[index] or "xx" in Function[index]:
                Repeated_Op_Error[0] = [True]
                Repeated_Op_Error.append(Function[index])
        return Repeated_Op_Error

    #Function looping on the max and min values string, and detect if there is any invalid characters in the max and min value strings.
    def InValid_Max_Min_Value(self,Max_Value,Min_Value):
        Identified_Numbers = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9" , "-"]
        Flags = [0, 0]
        exist = 0
        for i in range(0,len(Max_Value)):
            for j in range(0,len(Identified_Numbers)):
                if Max_Value[i] == Identified_Numbers[j]:
                    exist = 1

        if exist == 0:
            Flags[0] = 1

        exist = 0

        for i in range(0, len(Min_Value)):
            for j in range(0, len(Identified_Numbers)):
                if Min_Value[i] == Identified_Numbers[j]:
                    exist = 1


        if exist == 0:
            Flags[1] = 1

        return Flags


    #Function checking all types of errors and print error messages, and return flag that indicate if there is an error or not
    def Checking_For_Errors(self,Function, Max_Value, Min_Value):
        Flag = 0
        Splitted_Function_List = re.split("[+-]", Function) #Split the array
        UnIdentified_Error = self.Checking_UnIdentified_Characters(Function) #Checking error of unidentified characters
        Mult_Div_Nothing_Error = self.Multiply_Divide_By_Nothing_Error(Splitted_Function_List) #Checking error of missing operands
        Numb_Vari_Error = self.Number_Followed_By_Variable_Error(Splitted_Function_List) #Checking error of number followed by variable
        Rep_Op_Error = self.Repeated_Operation_Error(Splitted_Function_List) #Checking error of Repeated operations
        Invalid_Max_Min = self.InValid_Max_Min_Value(Max_Value,Min_Value) #Checking if the max and min values entered are valid
        y = 0

        #Checking the return flags to specify the sort of error and print its message
        if Invalid_Max_Min[0] == 1 and Invalid_Max_Min[1] == 0:
            self.error("Invalid Character in x max value, the x max must be numbers only")
            Flag = 1
        elif Invalid_Max_Min[0] == 1 and Invalid_Max_Min[1] == 1:
            self.error("Invalid Character in x max value and min value, the x max and x min must be numbers only")
            Flag = 1
        elif Invalid_Max_Min[0] == 0 and Invalid_Max_Min[1] == 1:
            self.error("Invalid Character in x min value, the x min must be numbers only")
            Flag = 1

        #checking if there is any operation performed in the max and min value text fields , as it's not supported by program example Max_Value = 7-2 -> will give an error
        if (Max_Value.find("-") != 0 and Max_Value.find("-") != -1) or (Min_Value.find("-") != 0 and Min_Value.find("-") != -1):
            self.error("Performing operation in max or min value text fields is not allowed, just put +ve or -ve absolute number and try again")
            Flag = 1

        if Flag == 0:
            # checking if the max value is larger than the min value
            if int(Max_Value) < int(Min_Value):
                self.error("Minimum Value is Larger Than The Maximum Value")
                Flag = 1


        #Checking by the return flag of the function, if there is any Unidentified characters and print the error message if error exist
        if UnIdentified_Error[0]:
            UnIdentified_Error.pop(0)
            self.error("The following Characters or Operations are UnIdentified  " + str(UnIdentified_Error))
            Flag = 1
        #if there is not any unidentified characters, start to inspect for any error in typing the function.
        else:
            #Checking by the return flag of the function, if there is any missing operands and print the error message if error exist
            if Mult_Div_Nothing_Error[0]:
                Mult_Div_Nothing_Error.pop(0)
                self.error("The Following Terms have a missing Operand  " + str(Mult_Div_Nothing_Error))
                Flag = 1
            # Checking by the return flag of the function, if there is any missing number followed by variable and print the error message if error exist
            if Numb_Vari_Error[0]:
                Numb_Vari_Error.pop(0)
                self.error("Unknown operation, there is missing operation in this terms " + str(Numb_Vari_Error))
                Flag = 1
            # Checking by the return flag of the function, if there is any repeated operations and print the error message if error exist
            if Rep_Op_Error[0]:
                Rep_Op_Error.pop(0)
                for Index in range(0, len(Rep_Op_Error)):
                    if Rep_Op_Error[Index] == "" and y == 0:
                        Rep_Op_Error[Index] = "++ or --"
                        y = 1
                self.error("The Following Operation or Variables and Terms have Repeated Operations or Empty Brackets " + str(Rep_Op_Error))
                Flag = 1
        return Flag

    def FUNCT(self):
        #checking if the all text field is filled by data, if not give the user and error message
        if (self.txt1.text() == "") or (self.txt2.text() == "") or (self.txt3.text() == ""):
            self.error("Please Fill The Inputs")
        else:
            #Taking the data from the text fields
            Function_x = self.txt1.text()
            x_Min = self.txt2.text()
            x_Max = self.txt3.text()

            self.progressbar.setValue(20) #set the progressbar to 20

            #removing the spaces from string of the function, as we can detect errors easier
            Function_x_Without_Spacings = Function_x.replace(" ", "")
            Flag = self.Checking_For_Errors(Function_x_Without_Spacings, x_Max, x_Min)  #Checking for errors in the string of the function and max and min value

            #if there is no errors
            if Flag == 0:
                self.progressbar.setValue(40) #set progress bar to 40
                Powers = self.Number_Of_Powers(Function_x) #calculate the number of "^" operation has repeated
                Function_x = self.Modifying_Powers(Function_x, Powers) #Replace every "^" by "**"

                x = symbols("x") #define x as a symbol
                x_Range = Nump.linspace(int(x_Max), int(x_Min), 100) #create 100 points between the x min vaue and x max value to get data that i will use to plot
                x_Range_Float = [] #declare empty list that will be filled by x axis data in type of float
                Function_x = sympify(Function_x) #conver from string to object in sympy class
                y_Float = [] #declare empty list that will be filled by y axis data in type of float

                #looping on the x axis data convert it to float and use function subs in sympy to sub with x values in the function to get y value.
                #and then convert the data of the y axis to float, as we can't plot two data with different types, so i used numpy and sympy to get the data i want
                #and then i convert each of them to float, so i can use the data to plot
                for index in range(0, 100):
                    x_Range_Float.append(float(x_Range[index]))
                    y_Float.append(float(Function_x.subs(x,x_Range_Float[index])))

                self.progressbar.setValue(70)  #set progress bar to 70

                #taking the data from combo box field into variable bgc, and by checking bgc we can specify if the user want the background color is white or black
                if (self.cb.currentText() == "White"):
                    bgc = 'w'
                elif (self.cb.currentText() == "Black"):
                    bgc = 'k'
                else:
                    bgc = 'w'

                self.graphWidget.setBackground(bgc)  # Set the background of the widget to the color specified by the combo box field

                #taking the data from combo box field into variable cc, and by checking cc we can specify if the user want the curve color
                #red or blue or green color
                if (self.cb2.currentText() == "Blue"):
                    cc = 'b'
                elif (self.cb2.currentText() == "Red"):
                    cc = 'r'
                elif (self.cb2.currentText() == "Green"):
                    cc = 'g'
                else:
                    cc = 'g'

                #taking the data from combo box field,if it's append the user can plot several curve on same widget, if replace there is one curve in the widget
                if (self.cb3.currentText() == "Replace"):
                    self.graphWidget.clear() #clear the widget
                    pen = mkPen(color=(cc), width=3) #specify the pen color and font that will be used to plot
                    self.graphWidget.plot(x_Range_Float, y_Float, pen=pen) #plot the function
                elif (self.cb3.currentText() == "Append"):
                    pen = mkPen(color=(cc), width=3)
                    self.graphWidget.plot(x_Range_Float, y_Float, pen=pen)
                else: #the default will be append.
                    pen = mkPen(color=(cc), width=3)
                    self.graphWidget.plot(x_Range_Float, y_Float, pen=pen)

                self.progressbar.setValue(100) #set progress bar to 100

    #function that create the error box that appears when any error occurs and display text that passed to the function
    def error(self, txt):
        msg = QMessageBox() #create message box
        msg.setWindowTitle("ERROR MESSAGE") #Set the message box title
        msg.setIcon(QMessageBox.Warning) #set the icon of the message box to warning icon
        msg.setText("ERROR") #create text error in the box
        msg.setInformativeText("" + txt) #display error message passed to the function, depend on the type of error
        msg.setStandardButtons(QMessageBox.Ok) #create buttn ok.
        msg.exec_() #execute the message box and show it on screen

#execute, show the GUI.
myApp = QApplication(sys.argv)
window = Window()
window.show()
myApp.exec_()
sys.exit(0)






