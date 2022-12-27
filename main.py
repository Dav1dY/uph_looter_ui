import base64
import csv
import os
import tkinter as tk
from tkinter import StringVar
from tkinter.filedialog import askdirectory
import windnd
from check_png import img as right_img
from error_png import img as error_img
from christmas_tree_ico import img as app_icon
from enum import Enum
import ctypes
import re

current_version = '1.02'
# v1.02: algorithm improved
# v1.01: add format check
# author: David


class ErrorNum(Enum):  # not used yet
    No_error = 1
    Target_path_not_exist = "Target path not exist"
    Source_path_not_exist = "Source path not exist"
    Source_file_wrong_type = "Source file wrong type"
    Source_file_wrong_format = "Source file wrong format"
    Open_target_file_error = "Open target file error"


def check_path(source_path, target_path):
    if source_path[-4:] == '.csv':
        try:
            open(source_path)
            if os.path.exists(target_path):
                return True
            else:
                # return ErrorNum.Target_path_not_exist
                return False
        except FileNotFoundError:
            # return ErrorNum.Source_file_wrong_format
            return False
    else:
        return False
        # return ErrorNum.Source_file_wrong_type


def check_time_format(time):
    time_format = re.compile(r'^[1-2][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9] hour [0-2][0-9]$')
    if isinstance(time, str):
        if re.match(time_format, time):
            return True
        else:
            return False
    else:
        return False


def make_sum(source_file_name, target_file_path, target_file_name):
    target_file_address = target_file_path + '\\' + target_file_name
    if check_path(source_file_name, target_file_path):
        source_csv_file = csv.reader(open(source_file_name))
        source_data_list = list(source_csv_file)
        csv_length = len(source_data_list)
        target_date_list = []
        target_uph_list = []
        target_date_count = 0
        target_data_list = []
        temp_date_last = ''  # last date
        temp_number_last = 0  # last data
        is_data_calculated = False
        # form date & data list
        for i in range(0, csv_length):
            if not check_time_format(source_data_list[i][0]):
                return False
            temp_date_current = source_data_list[i][0][0:10]  # current date
            try:
                temp_number_current = int(source_data_list[i][1])  # get current uph
            except ValueError:
                return False
            # new day found
            if temp_date_last != temp_date_current:
                temp_date_last = temp_date_current
                target_date_list.append(temp_date_last)  # add new date to target list
                target_date_count += 1
                if i != 0:
                    target_uph_list.append(temp_number_last)
                temp_number_last = temp_number_current
                is_data_compared = False
            # same day
            else:
                temp_number_last = temp_number_current if temp_number_last < temp_number_current else temp_number_last
                is_data_compared = True
            # handle last line situation
            if i == csv_length - 1:
                if is_data_compared:
                    target_uph_list.append(temp_number_last)
                else:
                    target_uph_list.append(temp_number_current)
        # form target list
        for i in range(0, target_date_count):
            temp = [target_date_list[i], target_uph_list[i]]
            target_data_list.append(temp)
        # create target csv
        try:
            with open(target_file_address, 'w', newline='') as file:
                newfile = csv.writer(file)
                for i in range(0, target_date_count):
                    newfile.writerow(target_data_list[i])
            return True
        except Exception as err_result:
            if err_result:
                pass
            # return ErrorNum.Open_target_file_error
            return False
    else:
        # return check_result
        return False


class Window(object):
    def __init__(self):
        myapp_id = 'Max UPH Looter'+current_version
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myapp_id)
        # setup variables
        self.window1 = tk.Tk()
        self.window1.geometry('400x400')
        self.window1.resizable(False, False)
        self.window1.title('Max UPH Looter'+current_version)
        self.source_file_name_list = []
        self.source_file_name = 0
        self.selected_path = StringVar()
        self.target_file_name = StringVar()
        self.inserted_path_ok = False

        # load img
        self.Image_OK = tk.PhotoImage(data=base64.b64decode(right_img))
        self.Image_ERROR = tk.PhotoImage(data=base64.b64decode(error_img))
        self.recover_icon()

        # setup ui modules
        self.Text_Source_Path = tk.Text(self.window1, bg='grey', bd=4, font=('Arial', 12), width=26, height=7)
        self.Text_Source_Path.insert('insert', '\n\n\n            drag raw data here')
        self.Text_Source_Path.place(x=80, y=100, anchor='nw')
        self.Button_Make = tk.Button(self.window1, text='MAKE', command=self.make_button_func,
                                     state=tk.DISABLED)
        self.Button_Locate_Path = tk.Button(self.window1, text='...', command=self.select_path_button_func)
        self.Label_Target_Path = tk.Label(self.window1, text="path:")
        self.Label_Target_Filename = tk.Label(self.window1, text="name:")
        self.Label_CSV_Suffix = tk.Label(self.window1, text=".csv")
        self.Label_Make_Result = tk.Label(self.window1, width=40, height=40)  # png
        self.Entry_Target_Path = tk.Entry(self.window1, textvariable=self.selected_path, width=25)
        self.Entry_Target_Name = tk.Entry(self.window1, textvariable=self.target_file_name, width=25, justify='center')

        # bind drag function
        windnd.hook_dropfiles(self.Text_Source_Path.winfo_id(), self.drag_func)

        # place ui modules
        self.Button_Make.place(x=170, y=310, anchor='nw')
        self.Button_Locate_Path.place(x=295, y=265, anchor='nw')
        self.Label_Target_Path.place(x=67, y=270, anchor='nw')
        self.Label_Target_Filename.place(x=62, y=240, anchor='nw')
        self.Label_CSV_Suffix.place(x=290, y=240, anchor='nw')
        self.Label_Make_Result.place(x=230, y=300, anchor='nw')
        self.Entry_Target_Path.place(x=110, y=270, anchor='nw')
        self.Entry_Target_Name.place(x=110, y=240, anchor='nw')

        self.window1.mainloop()

    def drag_func(self, ls):
        self.Text_Source_Path.delete(0., "end")  # clear
        for i in ls:
            self.Text_Source_Path.insert("end", i.decode("gbk") + '\n')
            msg = '\n'.join((item.decode('gbk') for item in ls))
            self.source_file_name_list.append(msg)
            self.source_file_name = str(self.source_file_name_list[-1])
        if self.source_file_name[-4:] == '.csv':
            self.Text_Source_Path.configure(bg='green')
            self.inserted_path_ok = True
            self.selected_path.set(self.source_file_name[:self.source_file_name.rfind('\\')])

            self.Button_Make.config(state=tk.NORMAL)
            self.target_file_name.set(self.source_file_name.split("\\")[-1][0:-4] + '_sum')
        elif self.source_file_name == 0:
            pass
        else:
            self.Text_Source_Path.configure(bg='red')
            self.Button_Make.config(state=tk.DISABLED)

    def select_path_button_func(self):
        path_ = askdirectory()
        self.selected_path.set(path_)

    def make_button_func(self):
        # target_address = self.Entry_Target_Path.get() + '\\' + self.Entry_Target_Name.get() + '.csv'
        if make_sum(self.source_file_name, self.Entry_Target_Path.get(), self.Entry_Target_Name.get() + '.csv'):
            self.Label_Make_Result.config(image=self.Image_OK)
        else:
            self.Label_Make_Result.config(image=self.Image_ERROR)

    def recover_icon(self):
        tmp = open('tmp.ico', 'wb+')
        tmp.write(base64.b64decode(app_icon))
        tmp.close()
        self.window1.iconbitmap('tmp.ico')
        os.remove('tmp.ico')


if __name__ == '__main__':
    Window()
