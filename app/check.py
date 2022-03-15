from flask import redirect, url_for, redirect
import pandas as pd
import language_tool_python
import openpyxl
import os
import pathlib
import re
from datetime import datetime
import time


def print_time(position):
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print(f"Current time at {position} is {current_time}")


def process_marksbook(xlsx):
    print_time("20")
    tool = language_tool_python.LanguageTool("en-AU")
    header_list = [
        "Calc %",
        "Calc Gd",
        "Rank",
        "Mod %",
        "Mod Gd",
        "School Examination",
        "Participates fully",
        "Behaves appropriately",
        "Is well organised",
        "Meets deadlines",
        "Works autonomously",
        "Parent/Guardian interview requested",
        "Comment",
        "Works to the best of his/her ability",
        "Shows self respect and care",
        "Shows courtesy and respect for the rights of others",
        "Participates responsibly in social and civic activities",
        "Cooperates productively and builds positive relationships with others",
        "Is enthusiastic about learning",
        "Sets goals and works towards them with perseverance",
        "Shows confidence in making positive choices and decisions",
    ]
    header_dict = {}  # indices of each of the above items in the datafile
    student_list = pathlib.Path.cwd() / "app" / "data" / "student_list.csv"
    extra_info = (
        pathlib.Path.cwd()
        / "app"
        / "data"
        / "Students not Receiving Grade_Mark in Report and Gender Usage - 2021.csv"
    )
    df = pd.read_excel(xlsx)
    df2 = pd.read_csv(student_list)
    # this is the Google sheets data for gender usage, students not receiving grade and extra
    df3 = pd.read_csv(extra_info)
    df3.columns = [
        "name",
        "preferred",
        "year",
        "code",
        "no_grade",
        "male",
        "female",
        "neutral",
        "additional",
    ]
    cols = df.columns
    error_messages = []

    error_check_path = pathlib.Path.cwd() / "app" / "data" / "comment_check.txt"
    with open(error_check_path) as f:
        # read the error check words into a list, strip out \n
        check_terms = [line.rstrip("\n") for line in f]

    acceptedWordsPath = pathlib.Path.cwd() / "app" / "data" / "accepted_words.txt"
    with open(acceptedWordsPath) as f:
        # read the accepted words into a list, strip out \n
        accepted_words_list = [line.rstrip("\n") for line in f]

    subjects_with_scores_path = (
        pathlib.Path.cwd() / "app" / "data" / "subjects_with_scores.txt"
    )
    with open(subjects_with_scores_path) as f:
        # read the subjects with scores into a list, strip out \n
        subjects_with_scores_list = [line.rstrip("\n") for line in f]

    def get_title(subject):
        current_time = time.ctime()
        pos = subject.find("[")
        title = subject[:pos]
        title = title + "  " + current_time
        return title

    print_time("95")

    def get_names(name):
        # Split the student name into 3 item list: last name, first name, preferred name
        name_list1 = name.split(", ")
        name_list1.append(name_list1[1])
        if "(" in name_list1[1]:
            name_list2 = name_list1[1].split(" (")
            nm = name_list2[1].replace(")", "")
            name_list1[1] = name_list2[0]
            name_list1[2] = nm
        return name_list1

    print_time("108")

    def get_gender(student_id):
        # [gender, no grade, neutral, additional info]
        gender_and_extra = ["", "f,", "f", "f"]
        for i in range(len(df2.Code)):
            if student_id == (df2.Code[i]):
                gender_and_extra[0] = df2["Gender"][i]
        # Check other gender cases, also add students not receiving grades and additional notes
        for i in range(len(df3.code)):
            try:
                code = str(int(df3.code[i]))
            except ValueError:  # df3.code may not be an integer, e.g. NaN
                code = df3.code[i]
            if student_id == code:
                if df3.no_grade[i] == "TRUE":
                    gender_and_extra[0] = "t"
                if df3.male[i] == "TRUE":
                    gender_and_extra[0] = "m"
                if df3.female[i] == "TRUE":
                    gender_and_extra[0] = "f"
                if df3.neutral[i] == "TRUE":
                    gender_and_extra[2] = "t"
                additional = str(df3.additional[i])
                additional = additional.lower()
                if additional != "nan":
                    gender_and_extra[3] = additional
        return gender_and_extra

    print_time("137")

    def get_headers():
        # Get dictionary of headers and their column numbers starting with Calc%
        for index, row in df.iterrows():
            row_list = []
            max_col = len(row)
            i = 0
            while i < (max_col):
                if row[i] == "Calc %" and row[i + 1] == "Calc Gd":
                    # Find the row with 'Mod Gd'
                    while i < (max_col):
                        row_list.append(row[i])
                        header_dict[row[i]] = i
                        i += 1
                    break
                i += 1
            # break out of the for loop if row_list has been filled
            if len(row_list) > 0:
                break
        return header_dict

    print_time("158")

    def check_name_in_comment(fname, pname, comment):
        if str(comment) == "nan":
            comment = ""
        if fname in comment and fname != pname:
            # message = 'Subject: ' + student_dict.get('subject') + '  Student: ' + student_dict.get('first name') + ' ' + student_dict.get('last name') + 'First name (' + fname + ') used in comment when preferred name is ' + pname + '.'
            stud_name = (
                student_dict.get("first name") + " " + student_dict.get("last name")
            )
            error_msg = (
                "First name ("
                + fname
                + ") used in comment when preferred name is "
                + pname
                + "."
            )
            # msg_list is a list wrapped in a tuple, remove it out of the tuple:
            msg_list = ([stud_name, error_msg],)
            error_messages.append(msg_list[0])
        else:
            pass

    print_time("180")

    def comment_check(comment):
        # Check comment for any of the terms in comment_check.txt
        for term in check_terms:
            if (term != "") and (str(comment) != "nan"):
                if term in comment:
                    error_details = f"Style Error: {term}"
                    msg_list = [stud_name, error_details]
                    error_messages.append(msg_list)

    # Use language_tool_python for spell and grammar checking
    print_time("191")

    def spell_grammar(comment, first_name, pref_name):
        matches = tool.check(comment)
        k = 0
        for match in matches:
            k += 1
            mess = match.message
            cont = match.context
            repl = match.replacements
            is_error = True
            # Check repl is not an empty list
            if not repl:
                error_mess = mess + "\n" + "Context: " + cont
            else:
                if mess == "Possible spelling mistake found.":
                    spell_error = match.matchedText
                    if spell_error in accepted_words_list:
                        is_error = False
                    # First name may be more than one word, check spell error is not any of them
                    name_list = pref_name.split() + first_name.split()
                    if spell_error in name_list:
                        is_error = False
                    if spell_error == "nan":
                        is_error = False
                    if is_error:
                        error_mess = (
                            'Is "'
                            + spell_error
                            + '" a spelling mistake? You may have meant "'
                            + repl[0]
                            + '".'
                            + "\n"
                            + "Context: "
                            + cont
                        )
                else:
                    error_mess = (
                        mess
                        + "\n"
                        + "Context: "
                        + cont
                        + "\n"
                        + "Possible replacement: "
                        + repl[0]
                    )
                if is_error:
                    # replace this non-unicode character
                    error_mess = error_mess.replace("‘", "'")
                    # replace this non-unicode character
                    error_mess = error_mess.replace("“", '"')
                    # replace this non-unicode character
                    error_mess = error_mess.replace("’", "'")
                    # replace this non-unicode character
                    error_mess = error_mess.replace("”", '"')
                    msg_list = [name, error_mess]
                    error_messages.append(msg_list)

    # Loop through the rows of df1 (AcademicSummary.xlsx) and check for errors
    print_time("249")
    row_count = 0
    error_col_location = []
    # Get row numbers for first and last student name
    for row in df.itertuples():
        if (
            str(df.iat[row_count, 0]) == "nan"
            and str(df.iat[row_count + 1, 0]) != "nan"
        ):
            first_student_row = row_count + 1
        if df.iat[row_count, 0] == "Count":
            last_student_row = row_count
        row_count += 1
    i = 0
    # Get title header for pdf
    sub_name = cols[0]
    title = get_title(sub_name)
    print_time("266")
    for row in df.itertuples():
        if first_student_row <= i <= (last_student_row - 1):
            # name_list = lastname, firstname, preferred name
            name = df.iat[i, 0]
            student_code = df.iat[i, 2]
            student_code = int(student_code)
            student_code = str(student_code)
            extra_info = get_gender(student_code)
            gender = extra_info[0]
            name_list = get_names(name)
            student_dict = {
                "subject": title,
                "student_code": student_code,
                "last name": name_list[0],
                "first name": name_list[1],
                "preferred name": name_list[2],
                "gender": gender,
                "additional": extra_info[3],
            }
            stud_name = (
                student_dict.get("first name") + " " + student_dict.get("last name")
            )
            print_time("291")
            header_dict = get_headers()
            for x in header_dict:
                col_num = header_dict.get(x)
                value = row[col_num + 1]
                student_dict[x] = value
            for x in student_dict:
                # Check for missing data except interview requested
                val = str(student_dict.get(x))
                if val == "nan" and x != "Parent/Guardian interview requested":
                    if x != "additional":
                        message = (
                            "Subject: "
                            + student_dict.get("subject")
                            + "  Student: "
                            + student_dict.get("first name")
                            + " "
                            + student_dict.get("last name")
                            + "Warning - missing value for "
                            + x
                        )
                        stud_name = (
                            student_dict.get("first name")
                            + " "
                            + student_dict.get("last name")
                        )
                        error_msg = "Warning - missing value for " + x
                        msg_list = ([stud_name, error_msg],)
                        # msg_list is a list wrapped in a tuple, remove it out of the tuple:
                        error_messages.append(msg_list[0])
            print_time("321")
            fname = name_list[1]
            pname = name_list[2]
            comment = student_dict["Comment"]
            check_name_in_comment(fname, pname, comment)
            comment_check(comment)
            spell_grammar(comment, fname, pname)
            print_time("328")

        i += 1

    print_time("332")
    blank_list = ["", ""]
    for x in range(0, (2 * len(error_messages)) + 2):
        if x % 2 != 0:
            error_messages.insert(x, blank_list)

    # table_headers = (["STUDENT", "MESSAGE"],)
    if len(error_messages) == 0:
        error_messages.append("No errors found")
    print_time("344")
    print("FINISHED")
    return error_messages
