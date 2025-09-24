import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from tkinter import *
from tkinter.ttk import Combobox, Treeview
from tkinter.filedialog import askopenfilename, askdirectory
import win32api
from io import BytesIO
from PIL import Image, ImageTk, ImageDraw, ImageFont, ImageOps
import re
import random
import sqlite3
import os
import my_email
from tkinter.scrolledtext import ScrolledText
import threading

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS  # PyInstaller sets this at runtime
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

root = Tk()
root.geometry('500x600')
root.resizable(False, False)
root.iconbitmap(resource_path('images/photo.ico'))
root.title('Student Management and Registration System')

# Defined colors
bg_color = '#273b7a'
white = '#ffffff'

# images
login_student_icon = PhotoImage(file= resource_path('images/login_student_img.png'))
login_admin_icon = PhotoImage(file=resource_path('images/admin_img.png'))
create_student_icon = PhotoImage(file=resource_path('images/add_student_img.png'))
locked_icon = PhotoImage(file=resource_path('images/locked.png'))
unlocked_icon = PhotoImage(file=resource_path('images/unlocked.png'))
add_student_icon = PhotoImage(file=resource_path('images/add_image.png'))

def init_db():
    if os.path.exists('students_account_db'):
        connection = sqlite3.connect('students_account_db')
        cursor = connection.cursor()
        cursor.execute('''select * from Student_Data''')
        connection.commit()
        # print(cursor.fetchall())
        connection.close()
    else:
        connection = sqlite3.connect('students_account_db')
        cursor = connection.cursor()
        cursor.execute('''create table Student_Data(
                       id_number text,
                       password text,
                       name text,
                       age text, 
                       gender text,
                       phone_number text,
                       class text,
                       email text, 
                       image blob
                       )''')

        connection.commit()
        connection.close()

def check_existing_id(id_number):
    connection = sqlite3.connect('students_account_db')
    cursor = connection.cursor()
    cursor.execute(f"""select id_number from Student_Data where id_number == '{id_number}'""")
    connection.commit()
    response = cursor.fetchall()
    connection.close()
    return response

def check_valid_password(id_number, password):
    connection = sqlite3.connect('students_account_db')
    cursor = connection.cursor()
    cursor.execute(f"""select id_number, password from Student_Data where id_number == '{id_number}' and password == '{password}'""")
    connection.commit()
    response = cursor.fetchall()
    connection.close()
    return response

def add_student_data(id_number, password, name, age, gender, 
                     phone_number, student_class, email, pic_data):
     connection = sqlite3.connect('students_account_db')
     cursor = connection.cursor()
     cursor.execute(f"""
     insert into Student_Data values('{id_number}', '{password}', '{name}', '{age}', '{gender}',
     '{phone_number}', '{student_class}', '{email}', ?)              
     """, [pic_data])

     connection.commit()
     connection.close()

def confirmation_box(message):

    answer = BooleanVar()
    answer.set(False)

    def action(ans):
        answer.set(ans)
        con_box_frame.destroy()

    con_box_frame = Frame(root, highlightbackground=bg_color, highlightthickness=3)
    con_box_frame.place(x=100, y=120, width=320, height=220)

    message_label = Label(con_box_frame, text=message, font=('Bold', 15))
    message_label.pack(pady=20)

    cancel_btn = Button(con_box_frame, text='Cancel', bd=0, bg=bg_color, fg=white, font=('Bold', 15), command=lambda: action(False))
    cancel_btn.place(x=50, y=160)

    yes_btn = Button(con_box_frame, text='Yes', bd=0, bg='red', fg=white, font=('Bold', 15), command=lambda: action(True))
    yes_btn.place(x=190, y=160, width=80)
    
    root.wait_window(con_box_frame)
    return answer.get()

def message_box(message):
    message_box_frame = Frame(root, highlightbackground=bg_color, highlightthickness=3)
    message_box_frame.place(x=100, y=120, width=320, height=200)

    close_btn = Button(message_box_frame, text='X', bd=0, font=('Bold', 13), fg=bg_color, command=lambda: message_box_frame.destroy())
    close_btn.place(x=290, y=5)

    message_label = Label(message_box_frame, text=message, font=('Bold', 15))
    message_label.pack(pady=70)

def draw_student_card(student_pic_path, student_data):
    labels = """
    ID Number:
    Name:
    Gender:
    Age:
    Class:
    Contact:
    Email:
    """

    student_card = Image.open(resource_path('images/student_card_frame.png'))
    pic = Image.open(student_pic_path).resize((100,100))
    student_card.paste(pic, (15, 25))
    draw = ImageDraw.Draw(student_card)
    heading_font = ImageFont.truetype('arial', 18)
    label_font = ImageFont.truetype('arial', 15)
    data_font = ImageFont.truetype('arial', 13)
    draw.text(xy=(150, 60), text='Student Card', fill=(0, 0, 0), font=heading_font)
    draw.multiline_text(xy=(15, 120), text=labels, fill=(0 ,0 ,0), font=label_font, spacing=7)
    draw.multiline_text(xy=(110, 122), text=student_data, fill=(0, 0, 0), font=data_font, spacing=10)
    return student_card

def student_card_page(student_card_obj, bypass_login_page=False):

    def save_student_card():
        path = askdirectory()
        if path:
            print(path)
            student_card_obj.save(f'{path}/student_card.png')

    def print_student_card():
        path = askdirectory()
        if path:
            print(path)
            student_card_obj.save(f'{path}/student_card.png')
            win32api.ShellExecute(0, 'print', f'{path}/student_card.png', None, '.', 0)

    def close_page():
        student_card_frame.destroy()
        if not bypass_login_page:
            root.update()
            student_login_page()


    student_card_img = ImageTk.PhotoImage(student_card_obj)

    student_card_frame = Frame(root, highlightbackground=bg_color, highlightthickness=3)
    student_card_frame.place(x=50, y=30, width=400, height=450)

    heading_label = Label(student_card_frame, text='Student Card', bg=bg_color, fg=white, font=('Bold', 18))
    heading_label.place(x=0, y=0, width=400)

    close_btn = Button(student_card_frame, text='X', bd=0, bg=bg_color, fg=white, font=('Bold', 13), command=close_page)
    close_btn.place(x=370, y=0)

    # card_image = ImageTk.PhotoImage(Image.open('Card.png'))

    student_card_label = Label(student_card_frame, image=student_card_img)
    student_card_label.place(x=50, y=50)
    student_card_label.image = student_card_img

    save_student_card_btn = Button(student_card_frame, bd=1, text='Save Student Card', bg=bg_color, fg=white,
                                   font=('Bold', 15), command=save_student_card)
    save_student_card_btn.place(x=80, y=375)

    print_student_card_btn = Button(student_card_frame, bd=1, text='🖨', bg=bg_color, fg=white,
                                   font=('Bold', 15), command=print_student_card)
    print_student_card_btn.place(x=270, y=375)

def welcome_page():

    def forward_to_student_login_page():
        welcome_pg_frame.destroy()
        root.update()
        student_login_page()

    def forward_to_admin_login_page():
        welcome_pg_frame.destroy()
        root.update()
        admin_login_page()

    def forward_to_registration_page():
        welcome_pg_frame.destroy()
        root.update()
        registration_page()

    welcome_pg_frame = Frame(root, highlightbackground=bg_color, highlightthickness=3)
    welcome_pg_frame.pack(pady=30)
    welcome_pg_frame.pack_propagate(False)
    welcome_pg_frame.configure(width=400, height=420)

    heading_label = Label(welcome_pg_frame, text='Welcome to Student Registration\n && Management System',
                        bg=bg_color, fg=white, font=('Bold', 18))
    heading_label.place(x=0, y=0, width=400)

    student_login_btn = Button(welcome_pg_frame, text='Student Login', bg=bg_color, fg=white,
                            font=('Bold', 15), bd=0, command=forward_to_student_login_page)
    student_login_btn.place(x=120, y=125, width=200)

    student_login_img = Button(welcome_pg_frame, image=login_student_icon, bd=0, command=forward_to_student_login_page)
    student_login_img.place(x=60, y=100)

    admin_login_btn = Button(welcome_pg_frame, text='Admin Login', bg=bg_color, fg=white,
                            font=('Bold', 15), bd=0, command=forward_to_admin_login_page)
    admin_login_btn.place(x=120, y=225, width=200)

    admin_login_img = Button(welcome_pg_frame, image=login_admin_icon, bd=0, command=forward_to_admin_login_page)
    admin_login_img.place(x=60, y=200)

    add_student_btn = Button(welcome_pg_frame, text='Create Account', bg=bg_color, fg=white,
                            font=('Bold', 15), bd=0, command=forward_to_registration_page)
    add_student_btn.place(x=120, y=325, width=200)

    add_student_img = Button(welcome_pg_frame, image=create_student_icon, bd=0, command=forward_to_registration_page)
    add_student_img.place(x=60, y=300)

def send_email_to_student(email, message, subject):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587

    username = my_email.email_address
    password = my_email.password

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = username
    msg['To'] = email
    msg.attach(MIMEText(_text=message, _subtype='html'))
    smtp_connection = smtplib.SMTP(host=smtp_server, port=smtp_port)
    smtp_connection.starttls()
    smtp_connection.login(user=username, password=password)
    smtp_connection.sendmail(from_addr=username, to_addrs=email, msg=msg.as_string())
    smtp_connection.quit()

def forgot_password_page():

    def recover_password():
        if check_existing_id(id_number=student_id_entry.get()):
            connection = sqlite3.connect('students_account_db')
            cursor = connection.cursor()
            cursor.execute(f"""
            select password from Student_Data where id_number == '{student_id_entry.get()}'
            """)
            connection.commit()
            recovered_password = cursor.fetchall()[0][0]

            cursor.execute(f"""
            select email from Student_Data where id_number == '{student_id_entry.get()}'
            """)
            connection.commit()
            student_email = cursor.fetchall()[0][0]
            connection.close()

            confirmation = confirmation_box(message=f"""We will send your\nforgotten password
via your email address
{student_email}.
Do you want to continue?""")

            if confirmation:
                msg = f'''<h1>Your Forgotten Password is:</h1>
                <h2>{recovered_password}</h2>
                <p>Once you remember your password, please delete this message<p/>
                '''
                send_email_to_student(email=student_email, message=msg, subject='Password Recovery')

        else:
            message_box('Invalid ID Number')

    forgot_password_frame = Frame(root, highlightbackground=bg_color, highlightthickness=3)
    forgot_password_frame.place(x=75, y=120, width=350, height=250)

    heading_label = Label(forgot_password_frame, text='⚠ Forgot Password', font=('Bold', 15), bg=bg_color, fg=white)
    heading_label.place(x=0, y=0, width=350)

    close_btn = Button(forgot_password_frame, text='X', bd=0, font=('Bold', 13), bg=bg_color, fg=white,
                       command=lambda :forgot_password_frame.destroy())
    close_btn.place(x=320, y=0)

    student_id_label = Label(forgot_password_frame, text='Enter Student ID Number', font=('Bold', 13))
    student_id_label.place(x=70, y=40)

    student_id_entry = Entry(forgot_password_frame, font=('Bold', 13), justify=CENTER)
    student_id_entry.place(x=70, y=70, width=180)

    info_label = Label(forgot_password_frame, text='''Your Forgotten Password will be 
sent to your email address''', justify='left')
    info_label.place(x=70, y=100)

    next_btn = Button(forgot_password_frame, text='Next', font=('Bold', 13), bg=bg_color, fg=white, command=recover_password)
    next_btn.place(x=130, y=200, width=100)

def fetch_student_data(query):
    connection = sqlite3.connect('students_account_db')
    cursor = connection.cursor()
    cursor.execute(query)

    connection.commit()
    response = cursor.fetchall()
    connection.close()
    return response

def student_dashboard(student_id):
    get_student_details = fetch_student_data(f"""
select name, age, gender, class, phone_number, email from Student_Data where id_number == '{student_id}'
""")
    get_student_pic = fetch_student_data(f"""
    select image from Student_Data where id_number == '{student_id}'
    """)

    student_pic = BytesIO(get_student_pic[0][0])

    def logout():
        confirm = confirmation_box(message='Do You Want To Logout?')
        if confirm:
            dashboard_frame.destroy()
            welcome_page()
            root.update()

    def switch(indicator, page):
        home_btn_indicator.config(bg='#c3c3c3')
        student_card_btn_indicator.config(bg='#c3c3c3')
        security_btn_indicator.config(bg='#c3c3c3')
        edit_data_btn_indicator.config(bg='#c3c3c3')
        delete_account_btn_indicator.config(bg='#c3c3c3')
        indicator.config(bg=bg_color)
        for child in pages_frame.winfo_children():
            child.destroy()
            root.update()

        page()

    dashboard_frame = Frame(root, highlightbackground=bg_color, highlightthickness=3)

    options_frame = Frame(dashboard_frame, highlightbackground=bg_color, highlightthickness=2, bg='#c3c3c3')
    options_frame.place(x=0, y=0, width=120, height=575)

    home_btn = Button(options_frame, text='Home', font=('Bold', 15), fg=bg_color, bg='#c3c3c3', bd=0,
                      command=lambda: switch(indicator=home_btn_indicator, page=home_page))
    home_btn.place(x=10, y=50)

    home_btn_indicator = Label(options_frame, bg=bg_color)
    home_btn_indicator.place(x=5, y=48, width=3, height=40)

    student_card_btn = Button(options_frame, text='Student\nCard', font=('Bold', 15),
                              fg=bg_color, bg='#c3c3c3', bd=0, justify='left',
                              command=lambda: switch(indicator=student_card_btn_indicator, page=dashboard_student_card_page))
    student_card_btn.place(x=10, y=100)

    student_card_btn_indicator = Label(options_frame, bg='#c3c3c3')
    student_card_btn_indicator.place(x=5, y=108, width=3, height=40)

    security_btn = Button(options_frame, text='Security', font=('Bold', 15),
                              fg=bg_color, bg='#c3c3c3', bd=0,
                          command=lambda: switch(indicator=security_btn_indicator, page=security_page))
    security_btn.place(x=10, y=170)

    security_btn_indicator = Label(options_frame, bg='#c3c3c3')
    security_btn_indicator.place(x=5, y=170, width=3, height=40)

    edit_data_btn = Button(options_frame, text='Edit Data', font=('Bold', 15),
                          fg=bg_color, bg='#c3c3c3', bd=0,
                           command=lambda: switch(indicator=edit_data_btn_indicator, page=edit_data_page))
    edit_data_btn.place(x=10, y=220)

    edit_data_btn_indicator = Label(options_frame, bg='#c3c3c3')
    edit_data_btn_indicator.place(x=5, y=220, width=3, height=40)

    delete_account_btn = Button(options_frame, text='Delete\nAccount', font=('Bold', 15),
                              fg=bg_color, bg='#c3c3c3', bd=0, justify='left',
                                command=lambda: switch(indicator=delete_account_btn_indicator, page=delete_account_page))
    delete_account_btn.place(x=10, y=270)

    delete_account_btn_indicator = Label(options_frame, bg='#c3c3c3')
    delete_account_btn_indicator.place(x=5, y=280, width=3, height=40)

    logout_btn = Button(options_frame, text='Logout', font=('Bold', 15),
                           fg=bg_color, bg='#c3c3c3', bd=0, command=logout)
    logout_btn.place(x=10, y=340)

    def home_page():
        student_pic_img_obj = Image.open(student_pic)
        size = 100
        mask = Image.new(mode='L', size=(size, size))
        draw_circle = ImageDraw.Draw(im=mask)
        draw_circle.ellipse(xy=(0, 0, size, size), fill=255, outline=True)
        outputt = ImageOps.fit(image=student_pic_img_obj, size=mask.size, centering=(1, 1))
        outputt.putalpha(mask)
        student_picture = ImageTk.PhotoImage(outputt)


        home_page_frame = Frame(pages_frame)
        home_page_frame.pack(fill='both', expand=True)

        student_pic_label = Label(home_page_frame, image=student_picture)
        student_pic_label.image = student_picture
        student_pic_label.place(x=10, y=10)

        hi_label = Label(home_page_frame, text=f'Hi! {get_student_details[0][0]}', font=('Bold', 15))
        hi_label.place(x=130, y=50)

        student_details = f'''
Student ID: {student_id}\n
Name: {get_student_details[0][0]}\n
Age: {get_student_details[0][1]}\n
Gender: {get_student_details[0][2]}\n
Class: {get_student_details[0][3]}\n
Contact: {get_student_details[0][4]}\n
Email: {get_student_details[0][5]}
'''

        student_details_label = Label(home_page_frame, text=student_details, font=('Bold', 13), justify='left')
        student_details_label.place(x=20, y=130)

    def dashboard_student_card_page():
        student_details = f'''
{student_id}
{get_student_details[0][0]}
{get_student_details[0][2]}
{get_student_details[0][1]}
{get_student_details[0][3]}
{get_student_details[0][4]}
{get_student_details[0][5]}
'''
        student_card_img_obj = draw_student_card(student_pic_path=student_pic,
                                                 student_data=student_details)

        def save_student_card():
            path = askdirectory()
            if path:
                print(path)
                student_card_img_obj.save(f'{path}/student_card.png')

        def print_student_card():
            path = askdirectory()
            if path:
                print(path)
                student_card_img_obj.save(f'{path}/student_card.png')
                win32api.ShellExecute(0, 'print', f'{path}/student_card.png', None, '.', 0)

        student_card_img = ImageTk.PhotoImage(student_card_img_obj)
        student_card_page_frame = Frame(pages_frame)
        card_label = Label(student_card_page_frame, image=student_card_img)
        card_label.image = student_card_img
        card_label.place(x=20, y=50)

        student_card_page_frame.pack(fill='both', expand=True)

        save_student_card_btn = Button(student_card_page_frame, text='Save Student Card', font=('Bold', 13),
                                       bd=1, fg=white, bg=bg_color, command=save_student_card)
        save_student_card_btn.place(x=40, y=400)

        print_student_card_btn = Button(student_card_page_frame, text='🖨', font=('Bold', 13),
                                       bd=1, fg=white, bg=bg_color, command=print_student_card)
        print_student_card_btn.place(x=240, y=400)


    def security_page():
        def show_hide_password():
            if current_password_entry['show'] == '*':
                current_password_entry.config(show='')
                show_hide_btn.config(image=unlocked_icon)
            else:
                current_password_entry.config(show='*')
                show_hide_btn.config(image=locked_icon)

        def set_password():
            if new_password_entry.get() != '':
                confirm = confirmation_box(message='Do you want to change\n your password?')
                if confirm:
                    connection = sqlite3.connect('students_account_db')
                    cursor = connection.cursor()
                    cursor.execute(f"""update Student_Data set password = '{new_password_entry.get()}'
                    where id_number == '{student_id}'""")
                    connection.commit()
                    connection.close()
                    message_box(message='Password Updated Successfully')

                    current_password_entry.config(state='normal')
                    current_password_entry.delete(0, END)
                    current_password_entry.insert(0, new_password_entry.get())
                    new_password_entry.delete(0, END)
                    current_password_entry.config(state="readonly")

            else:
                message_box(message='Enter New Password Required')

        security_page_frame = Frame(pages_frame)
        security_page_frame.pack(fill='both', expand=True)

        current_password_label = Label(security_page_frame, text='Your Current Password', font=('Bold', 12))
        current_password_label.place(x=80, y=30)

        current_password_entry = Entry(security_page_frame, font=('Bold', 15), justify='center', show='*')
        current_password_entry.place(x=50, y=80)

        student_current_password = fetch_student_data(f"select password from Student_Data where id_number == '{student_id}'")
        current_password_entry.insert(END, student_current_password[0][0])
        current_password_entry.config(state="readonly")

        show_hide_btn = Button(security_page_frame, image=locked_icon, bd=0, command=show_hide_password)
        show_hide_btn.place(x=280, y=70)

        change_password_label = Label(security_page_frame, text='Change Password', font=('Bold', 15), bg='red', fg=white)
        change_password_label.place(x=30, y=210, width=290)

        new_password_label = Label(security_page_frame, text='Set New Password', font=('Bold', 12))
        new_password_label.place(x=100, y=280)

        new_password_entry = Entry(security_page_frame, font=('Bold', 15), justify='center')
        new_password_entry.place(x=60, y=330)

        change_password_btn = Button(security_page_frame, text='Set Password', font=('Bold', 12),
                                     bg=bg_color, fg=white, command=set_password)
        change_password_btn.place(x=110, y=380)

    def edit_data_page():

        pic_path = StringVar()
        pic_path.set('')

        def open_pic():
            # open image file path
            path = askopenfilename()
            # Check if any image is open
            if path:
                # If found, display image
                img = ImageTk.PhotoImage(Image.open(path).resize((100, 100)))
                pic_path.set(path)

                add_pic_btn.config(image=img)
                add_pic_btn.image = img

        def remove_highlight_warning(entry):
            if entry['highlightbackground'] != 'gray':
                if entry.get() != '':
                    entry.config(highlightcolor=bg_color, highlightbackground='gray')

        def verify_email(email):
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            match = re.match(pattern=pattern, string=email)
            return match

        def check_inputs():
            nonlocal get_student_details, get_student_pic, student_pic
            if student_name_entry.get() == '':
                student_name_entry.config(highlightcolor='red', highlightbackground='red')
                student_name_entry.focus()
                message_box(message='Student Full Name Required')
            elif student_age_entry.get() == '':
                student_age_entry.config(highlightcolor='red', highlightbackground='red')
                student_age_entry.focus()
                message_box(message='Student Age Required')
            elif student_contact_entry.get() == '':
                student_contact_entry.config(highlightcolor='red', highlightbackground='red')
                student_contact_entry.focus()
                message_box(message='Student Contact Required')
            elif student_email_entry.get() == '':
                student_email_entry.config(highlightcolor='red', highlightbackground='red')
                student_email_entry.focus()
                message_box(message='Student Email Address Required')
            elif not verify_email(email=student_email_entry.get()):
                student_email_entry.config(highlightcolor='red', highlightbackground='red')
                student_email_entry.focus()
                message_box(message='Please Enter a Valid\nEmail Address')
            else:
                if pic_path.get() != '':
                    new_student_pic = Image.open(pic_path.get()).resize((100,100))
                    new_student_pic.save('temp_pic.png')

                    with open('temp_pic.png', 'rb') as read_new_pic:
                        new_pic_binary = read_new_pic.read()
                        read_new_pic.close()

                    connection = sqlite3.connect('students_account_db')
                    cursor = connection.cursor()
                    cursor.execute(f"update Student_Data set image=? where id_number == '{student_id}' ",
                                   [new_pic_binary])
                    connection.commit()
                    connection.close()
                    message_box(message='Data Successfully Updated')

                name = student_name_entry.get()
                age = student_age_entry.get()
                selected_class = select_class_btn.get()
                contact_number = student_contact_entry.get()
                email_address = student_email_entry.get()

                connection = sqlite3.connect('students_account_db')
                cursor = connection.cursor()
                cursor.execute(f"""
                update Student_Data set name='{name}', age='{age}', class='{selected_class}', 
                phone_number='{contact_number}', email='{email_address}' where id_number == '{student_id}'
                """)
                connection.commit()
                connection.close()
                get_student_details = fetch_student_data(f"""
                select name, age, gender, class, phone_number, email from Student_Data where id_number == '{student_id}'
                """)
                get_student_pic = fetch_student_data(f"""
                    select image from Student_Data where id_number == '{student_id}'
                    """)
                student_pic = BytesIO(get_student_pic[0][0])
                message_box(message='Data Successfully Updated')

        edit_data_frame = Frame(pages_frame)
        edit_data_frame.pack(fill='both', expand=True)

        student_current_pic = ImageTk.PhotoImage(Image.open(student_pic))

        add_pic_section_frame = Frame(edit_data_frame, highlightbackground=bg_color, highlightthickness=2)
        add_pic_section_frame.place(x=5, y=5, width=105, height=105)

        add_pic_btn = Button(add_pic_section_frame, image=student_current_pic, bd=0, command=open_pic)
        add_pic_btn.pack()
        add_pic_btn.image = student_current_pic

        student_name_label = Label(edit_data_frame, text='Student Full Name', font=('Bold', 12))
        student_name_label.place(x=5, y=130)

        student_name_entry = Entry(edit_data_frame, font=('Bold', 15), highlightcolor=bg_color,
                                   highlightbackground='gray',
                                   highlightthickness=2)
        student_name_entry.place(x=5, y=160, width=180)
        student_name_entry.bind('<KeyRelease>', lambda e: remove_highlight_warning(entry=student_name_entry))
        student_name_entry.insert(END, get_student_details[0][0])

        student_age_label = Label(edit_data_frame, text='Student Age', font=('Bold', 12))
        student_age_label.place(x=5, y=210)

        student_age_entry = Entry(edit_data_frame, font=('Bold', 15), highlightcolor=bg_color,
                                  highlightbackground='gray',
                                  highlightthickness=2)
        student_age_entry.place(x=5, y=235, width=180)
        student_age_entry.bind('<KeyRelease>', lambda e: remove_highlight_warning(entry=student_age_entry))
        student_age_entry.insert(END, get_student_details[0][1])

        student_contact_label = Label(edit_data_frame, text='Phone Number', font=('Bold', 12))
        student_contact_label.place(x=5, y=285)

        student_contact_entry = Entry(edit_data_frame, font=('Bold', 15), highlightcolor=bg_color,
                                      highlightbackground='gray',
                                      highlightthickness=2)
        student_contact_entry.place(x=5, y=310, width=180)
        student_contact_entry.bind('<KeyRelease>', lambda e: remove_highlight_warning(entry=student_contact_entry))
        student_contact_entry.insert(END, get_student_details[0][4])

        student_class_label = Label(edit_data_frame, text='Student Class', font=('Bold', 12))
        student_class_label.place(x=5, y=362)

        select_class_btn = Combobox(edit_data_frame, font=('Bold', 12), state='readonly', values=class_list)
        select_class_btn.place(x=5, y=390, width=180, height=30)
        select_class_btn.bind('<KeyRelease>', lambda e: remove_highlight_warning(entry=select_class_btn))
        select_class_btn.set(get_student_details[0][3])

        student_email_label = Label(edit_data_frame, text='Student Email', font=('Bold', 12))
        student_email_label.place(x=5, y=440)

        student_email_entry = Entry(edit_data_frame, font=('Bold', 15), highlightcolor=bg_color,
                                    highlightbackground='gray',
                                    highlightthickness=2)
        student_email_entry.place(x=5, y=470, width=180)
        student_email_entry.bind('<KeyRelease>', lambda e: remove_highlight_warning(entry=student_email_entry))
        student_email_entry.insert(END, get_student_details[0][5])

        update_data_btn = Button(edit_data_frame, text='Update', font=('Bold', 15),
                                 bg=bg_color, fg=white, bd=0, command=check_inputs)
        update_data_btn.place(x=220, y=470, width=80)

    def delete_account_page():
        def confirm_delete_account():
            confirm = confirmation_box(message='⚠ Are You Sure You Want\nto Delete This Account')
            if confirm:
                connection = sqlite3.connect('students_account_db')
                cursor = connection.cursor()
                cursor.execute(f"""delete from Student_Data where id_number == '{student_id}'""")
                connection.commit()
                connection.close()
                dashboard_frame.destroy()
                welcome_page()
                root.update()
                message_box(message='Your Account Has Bee\nDeleted Successfully')


        delete_account_frame = Frame(pages_frame)
        delete_account_frame.pack(fill='both', expand=True)

        delete_account_label = Label(delete_account_frame, text='⚠ Delete Account', font=('Bold', 15),
                                     fg='red')
        delete_account_label.place(x=30, y=100, width=290)

        delete_account_btn = Button(delete_account_frame, text='DELETE ACCOUNT', font=('Bold', 13),
                                     fg=white, bg='red', command=confirm_delete_account)
        delete_account_btn.place(x=110, y=200)



    pages_frame = Frame(dashboard_frame)
    pages_frame.place(x=122, y=5, width=350, height=550)
    home_page()

    dashboard_frame.pack(pady=5)
    dashboard_frame.pack_propagate(False)
    dashboard_frame.configure(width=480, height=580)


def student_login_page():

    def show_hide_password():
        if password_entry['show'] == '*':
            password_entry.config(show='')
            show_hide_btn.config(image=unlocked_icon)
        else:
            password_entry.config(show='*')
            show_hide_btn.config(image=locked_icon)

    def forward_to_welcome_page():
        student_login_page_frame.destroy()
        root.update()
        welcome_page()

    def forward_to_forget_password_page():
        forgot_password_page()

    def remove_highlight_warning(entry):
        if entry['highlightbackground'] != 'gray':
            if entry.get() != '':
                entry.config(highlightcolor=bg_color, highlightbackground='gray')

    def login_account():
        verify_id_number = check_existing_id(id_number=id_number_entry.get())
        if verify_id_number:
            verify_password = check_valid_password(id_number=id_number_entry.get(), password=password_entry.get())
            if verify_password:
                id_number = id_number_entry.get()
                student_login_page_frame.destroy()
                student_dashboard(student_id=id_number)
                root.update()

            else:
                password_entry.config(highlightcolor='red', highlightbackground='red')
                message_box(message='Password Incorrect!')
        else:
            id_number_entry.config(highlightcolor='red', highlightbackground='red')
            message_box(message='Incorrect Student ID!')

    student_login_page_frame = Frame(root, highlightbackground=bg_color, highlightthickness=3)
    student_login_page_frame.pack(pady=30)
    student_login_page_frame.pack_propagate(False)
    student_login_page_frame.configure(width=400, height=450)

    heading_label = Label(student_login_page_frame, text='Student Login Page',
                            bg=bg_color, fg=white, font=('Bold', 18))
    heading_label.place(x=0, y=0, width=400)

    back_btn = Button(student_login_page_frame, text='←', font=('Bold', 20), fg=bg_color, bd=0, command=forward_to_welcome_page)
    back_btn.place(x=5, y=40)

    student_icon_label = Label(student_login_page_frame, image=login_student_icon)
    student_icon_label.place(x=150, y=40)

    id_number_label = Label(student_login_page_frame, text='Enter Student ID Number', font=('Bold', 15),
                            fg=bg_color)
    id_number_label.place(x=80, y=140)

    id_number_entry = Entry(student_login_page_frame, font=('Bold', 15), justify='center',
                            highlightcolor=bg_color, highlightbackground='gray', highlightthickness=2)
    id_number_entry.place(x=80, y=190)
    id_number_entry.bind('<KeyRelease>', lambda e: remove_highlight_warning(entry=id_number_entry))

    password_label = Label(student_login_page_frame, text='Enter Student Password', font=('Bold', 15),
                            fg=bg_color)
    password_label.place(x=80, y=240)

    password_entry = Entry(student_login_page_frame, font=('Bold', 15), justify='center',
                            highlightcolor=bg_color, highlightbackground='gray', highlightthickness=2,
                            show='*')
    password_entry.place(x=80, y=290)
    password_entry.bind('<KeyRelease>', lambda e: remove_highlight_warning(entry=password_entry))

    show_hide_btn = Button(student_login_page_frame, image=locked_icon, bd=0, command=show_hide_password)
    show_hide_btn.place(x=310, y=280)

    login_btn = Button(student_login_page_frame, text='Login', font=('Bold', 15), bg=bg_color, fg=white, command=login_account)
    login_btn.place(x=95, y=340, width=200, height=40)

    forgot_password_btn = Button(student_login_page_frame, text='⚠\nForgot Password',
                                fg=bg_color, bd=0, command=forward_to_forget_password_page)
    forgot_password_btn.place(x=150, y=390)

def admin_dashboard():

    def switch(indicator, page):
        home_btn_indicator.config(bg='#c3c3c3')
        find_student_btn_indicator.config(bg='#c3c3c3')
        announcement_btn_indicator.config(bg='#c3c3c3')
        indicator.config(bg=bg_color)
        for child in pages_frame.winfo_children():
            child.destroy()
            root.update()
        page()

    def home_page():
        home_page_frame = Frame(pages_frame)

        admin_icon_label = Label(pages_frame, image=login_admin_icon)
        admin_icon_label.image = login_admin_icon
        admin_icon_label.place(x=10, y=10)

        hi_label = Label(pages_frame, text='Hi! Admin', font=('Bold', 15))
        hi_label.place(x=120, y=40)

        class_list_label = Label(pages_frame, text='Number of Students Per Class', font=('Bold', 13),
                                 bg=bg_color, fg=white)
        class_list_label.place(x=20, y=130)

        students_number_label = Label(home_page_frame, text='', font=('Bold', 13), justify='left')
        students_number_label.place(x=20, y=170)

        for i in class_list:
            result = fetch_student_data(f"""select count(*) from Student_Data where class == '{i}'""")
            students_number_label['text'] += f"{i} Class:    {result[0][0]}\n\n"

        home_page_frame.pack(fill='both', expand=True)

    def find_student_page():
        find_student_page_frame = Frame(pages_frame)

        def find_student():

            found_data = ''

            if find_by_option_btn.get() == 'id':
                found_data = fetch_student_data(query=f"""
                select id_number, name, class, gender from Student_Data where id_number ==
                '{search_input.get()}'""")
            elif find_by_option_btn.get() == 'name':
                found_data = fetch_student_data(query=f"""
                select id_number, name, class, gender from Student_Data where name like
                '%{search_input.get()}%'""")
            elif find_by_option_btn.get() == 'class':
                found_data = fetch_student_data(query=f"""
                select id_number, name, class, gender from Student_Data where class ==
                '{search_input.get()}'""")
            elif find_by_option_btn.get() == 'gender':
                found_data = fetch_student_data(query=f"""
                select id_number, name, class, gender from Student_Data where gender ==
                '{search_input.get()}'""")

            if found_data:
                for item in record_table.get_children():
                    record_table.delete(item)
                for details in found_data:
                    record_table.insert(parent='', index='end', values=details)
            else:
                for item in record_table.get_children():
                    record_table.delete(item)

        def generate_student_card():
            selection = record_table.selection()
            selected_id = record_table.item(item=selection, option='values')[0]

            get_student_details = fetch_student_data(f"""
            select name, age, gender, class, phone_number, email from Student_Data where id_number == '{selected_id}'
            """)
            get_student_pic = fetch_student_data(f"""
                select image from Student_Data where id_number == '{selected_id}'
                """)

            student_pic = BytesIO(get_student_pic[0][0])

            student_details = f'''
{selected_id}
{get_student_details[0][0]}
{get_student_details[0][2]}
{get_student_details[0][1]}
{get_student_details[0][3]}
{get_student_details[0][4]}
{get_student_details[0][5]}
            '''
            student_card_img_obj = draw_student_card(student_pic_path=student_pic,
                                                     student_data=student_details)
            student_card_page(student_card_obj=student_card_img_obj, bypass_login_page=True)

        def clear_result():
            find_by_option_btn.set('id')
            search_input.delete(0, END)
            for item in record_table.get_children():
                record_table.delete(item)
            generate_student_card_btn.config(state='disabled')

        search_filter = ['id', 'name', 'class', 'gender']

        find_student_record_label = Label(find_student_page_frame, text='Find Student Record',
                                          font=('Bold', 13), bg=bg_color, fg=white)
        find_student_record_label.place(x=20, y=10, width=300)

        find_by_label = Label(find_student_page_frame, text='Find By', font=('Bold', 13))
        find_by_label.place(x=15, y=50)

        find_by_option_btn = Combobox(find_student_page_frame, font=('Bold', 12), state='readonly',
                                      values=search_filter)
        find_by_option_btn.place(x=80, y=50, width=80)
        find_by_option_btn.set('id')

        search_input = Entry(find_student_page_frame, font=('Bold', 12))
        search_input.place(x=20, y=90)
        search_input.bind('<KeyRelease>', lambda e: find_student())

        record_table_label = Label(find_student_page_frame, font=('Bold', 13), bg=bg_color, fg=white,
                                   text='Record Table')
        record_table_label.place(x=20, y=160, width=300)

        record_table = Treeview(find_student_page_frame)
        record_table.place(x=0, y=200, width=350)
        record_table.bind('<<TreeviewSelect>>', lambda e: generate_student_card_btn.config(state='normal'))

        record_table['columns'] = ('id', 'name', 'class', 'gender')
        record_table.column('#0', stretch=NO, width=0)

        record_table.heading('id', text='ID Number', anchor='w')
        record_table.column('id', width=50, anchor='w')

        record_table.heading('name', text='Name', anchor='w')
        record_table.column('name', width=90, anchor='w')

        record_table.heading('class', text='Class', anchor='w')
        record_table.column('class', width=40, anchor='w')

        record_table.heading('gender', text='Gender', anchor='w')
        record_table.column('gender', width=40, anchor='w')

        generate_student_card_btn = Button(find_student_page_frame, text='Generate Student Card',
                                           font=('Bold', 13), bg=bg_color, fg=white,
                                           state="disabled", command=generate_student_card)
        generate_student_card_btn.place(x=160, y=450)

        clear_btn = Button(find_student_page_frame, text='Clear', font=('Bold', 13),
                           bg=bg_color, fg=white, command=clear_result)
        clear_btn.place(x=10, y=450)

        find_student_page_frame.pack(fill='both', expand=True)

    def announcement_page():

        selected_class = []

        def add_class(name):
            if selected_class.count(name):
                selected_class.remove(name)
            else:
                selected_class.append(name)
            print(selected_class)

        def collect_emails():
            fetched_emails = []
            for _class in selected_class:
                emails = fetch_student_data(f"""select email from Student_Data where class == '{_class}'""")
                for email_address in emails:
                    fetched_emails.append(*email_address)
            thread = threading.Thread(target=send_announcement, args=[fetched_emails])
            thread.start()

        def send_announcement(email_addresses):
            box_frame = Frame(root, highlightbackground=bg_color, highlightthickness=3)

            heading_label = Label(box_frame, text='Sending Email', bg=bg_color, fg=white, font=('Bold', 15))
            heading_label.place(x=0, y=0, width=300)

            sending_label = Label(box_frame, font=('Bold', 12), justify='left')
            sending_label.pack(pady=50)

            box_frame.place(x=100, y=120, width=300, height=200)

            subject = subject_entry.get()
            message = f'<h3 style="white-space: pre-wrap;">{announcement_message.get(0.1, END)}</h3>'
            sent_count = 0
            for email in email_addresses:
                sending_label.config(text=f"Sending To: \n{email}\n\n{sent_count}/{len(email_addresses)}")
                send_email_to_student(email=email, subject=subject, message=message)
                sent_count += 1
                sending_label.config(text=f"Sending To: \n{email}\n\n{sent_count}/{len(email_addresses)}")

            box_frame.destroy()
            message_box(message='Announcement Sent\nSuccesfully')



        announcement_page_frame = Frame(pages_frame)
        announcement_page_frame.pack(fill='both', expand=True)

        subject_label = Label(announcement_page_frame, text='Enter Announcement Subject',
                              font=('Bold', 12))
        subject_label.place(x=10, y=10)

        subject_entry = Entry(announcement_page_frame, font=('Bold', 12))
        subject_entry.place(x=10, y=40, width=210, height=25)

        announcement_message = ScrolledText(announcement_page_frame, font=('Bold', 12))
        announcement_message.place(x=10, y=100, width=300, height=200)

        class_list_label = Label(announcement_page_frame, text='Select Class to Announce',
                                font=('Bold', 12))
        class_list_label.place(x=10, y=320)

        y_position = 350
        for grade in class_list:
            class_check_btn = Checkbutton(announcement_page_frame, text=f'Class {grade}',
                                          command=lambda grade=grade: add_class(name=grade))
            class_check_btn.place(x=10, y=y_position)
            y_position += 25

        send_announcement_btn = Button(announcement_page_frame, text='Send Announcement', font=('Bold', 12),
                                       bg=bg_color, fg=white, command=collect_emails)
        send_announcement_btn.place(x=180, y=520)

    admin_dashboard_frame = Frame(root, highlightbackground=bg_color, highlightthickness=3)
    admin_dashboard_frame.pack(pady=5)
    admin_dashboard_frame.pack_propagate(False)
    admin_dashboard_frame.configure(width=480, height=580)

    options_frame = Frame(admin_dashboard_frame, highlightbackground=bg_color, highlightthickness=2,
                          bg='#c3c3c3')
    options_frame.place(x=0, y=0, width=120, height=575)

    home_btn = Button(options_frame, text='Home', font=('Bold', 15), bd=0, fg=bg_color, bg='#c3c3c3',
                      command=lambda: switch(indicator=home_btn_indicator, page=home_page))
    home_btn.place(x=10, y=50)

    home_btn_indicator = Label(options_frame, text='', bg=bg_color)
    home_btn_indicator.place(x=5, y=48, width=3, height=40)

    find_student_btn = Button(options_frame, text='Find\nStudent', font=('Bold', 15), bd=0, fg=bg_color,
                              bg='#c3c3c3', justify='left',
                              command=lambda: switch(indicator=find_student_btn_indicator, page=find_student_page))
    find_student_btn.place(x=10, y=100)

    find_student_btn_indicator = Label(options_frame, text='', bg='#c3c3c3',)
    find_student_btn_indicator.place(x=5, y=108, width=3, height=40)

    announcement_btn = Button(options_frame, text='Announce-\nMent📢', font=('Bold', 15), bd=0, fg=bg_color,
                              bg='#c3c3c3', justify='left',
                              command=lambda: switch(indicator=announcement_btn_indicator, page=announcement_page))
    announcement_btn.place(x=10, y=170)

    announcement_btn_indicator = Label(options_frame, text='', bg='#c3c3c3')
    announcement_btn_indicator.place(x=5, y=180, width=3, height=40)

    def logout():
        confirm = confirmation_box(message='Do You Want\nto Logout')
        if confirm:
            admin_dashboard_frame.destroy()
            welcome_page()
            root.update()

    logout_btn = Button(options_frame, text='Logout', font=('Bold', 15), bd=0, fg=bg_color,
                              bg='#c3c3c3', command=logout)
    logout_btn.place(x=10, y=240)

    pages_frame = Frame(admin_dashboard_frame)
    pages_frame.place(x=122, y=5, width=350, height=550)
    home_page()

def admin_login_page():

    def show_hide_password():
            if password_entry['show'] == '*':
                password_entry.config(show='')
                show_hide_btn.config(image=unlocked_icon)
            else:
                password_entry.config(show='*')
                show_hide_btn.config(image=locked_icon)

    def forward_to_welcome_page():
        admin_login_page_frame.destroy()
        root.update()
        welcome_page()

    def login_account():
        if username_entry.get() == 'admin':

            if password_entry.get() == 'admin':
                admin_login_page_frame.destroy()
                root.update()
                admin_dashboard()
            else:
                message_box(message='Wrong Password')

        else:
            message_box(message='Wrong Username')


    admin_login_page_frame = Frame(root, highlightbackground=bg_color, highlightthickness=3)
    admin_login_page_frame.pack(pady=30)
    admin_login_page_frame.pack_propagate(False)
    admin_login_page_frame.configure(width=400, height=450)

    heading_label = Label(admin_login_page_frame, text='Admin Login Page',
                                bg=bg_color, fg=white, font=('Bold', 18))
    heading_label.place(x=0, y=0, width=400)

    back_btn = Button(admin_login_page_frame, text='←', font=('Bold', 20), fg=bg_color, bd=0, command=forward_to_welcome_page)
    back_btn.place(x=5, y=40)

    admin_icon_label = Label(admin_login_page_frame, image=login_admin_icon)
    admin_icon_label.place(x=150, y=40)

    username_label = Label(admin_login_page_frame, text='Enter Admin User Name', font=('Bold', 15),
                                fg=bg_color)
    username_label.place(x=80, y=140)

    username_entry = Entry(admin_login_page_frame, font=('Bold', 15), justify='center',
                            highlightcolor=bg_color, highlightbackground='gray', highlightthickness=2)
    username_entry.place(x=80, y=190)

    password_label = Label(admin_login_page_frame, text='Enter Admin Password', font=('Bold', 15),
                            fg=bg_color)
    password_label.place(x=80, y=240)

    password_entry = Entry(admin_login_page_frame, font=('Bold', 15), justify='center',
                            highlightcolor=bg_color, highlightbackground='gray', highlightthickness=2,
                            show='*')
    password_entry.place(x=80, y=290)

    show_hide_btn = Button(admin_login_page_frame, image=locked_icon, bd=0, command=show_hide_password)
    show_hide_btn.place(x=310, y=280)

    login_btn = Button(admin_login_page_frame, text='Login', font=('Bold', 15), bg=bg_color, fg=white,
                       command=login_account)
    login_btn.place(x=95, y=340, width=200, height=40)

    forgot_password_btn = Button(admin_login_page_frame, text='⚠\nForgot Password',
                                fg=bg_color, bd=0)
    forgot_password_btn.place(x=150, y=390)


student_gender = StringVar()
class_list = ['5th', '6th', '7th', '8th', '9th', '10th', '11th', '12th']

def registration_page():

    pic_path = StringVar()
    pic_path.set('')

    def open_pic():
        # open image file path
        path = askopenfilename()
        # Check if any image is open
        if path:
            #If found, display image
            img = ImageTk.PhotoImage(Image.open(path).resize((100,100)))
            pic_path.set(path)

            add_pic_btn.config(image=img)
            add_pic_btn.image = img

    def forward_to_welcome_page():
        ans = confirmation_box(message='Do You Want To Quit The\nRegistration Form?')
        if ans:
            add_account_page_frame.destroy()
            root.update()
            welcome_page()

    def remove_highlight_warning(entry):
        if entry['highlightbackground'] != 'gray':
            if entry.get() != '':
                entry.config(highlightcolor=bg_color, highlightbackground='gray')

    def generate_id_number():
        generate_id = ''
        for r in range(6):
            generate_id += str(random.randint(0, 9))

        if not check_existing_id(id_number=generate_id):
            student_id_entry.config(state='normal')
            student_id_entry.delete(0, END)
            student_id_entry.insert(END, generate_id)
            student_id_entry.config(state='readonly')
        else:
            generate_id_number()

    def check_inavlid_email(email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        match = re.match(pattern=pattern, string=email)
        return match

    def check_input_validation():
        if student_name_entry.get() == '':
            student_name_entry.config(highlightcolor='red', highlightbackground='red')
            student_name_entry.focus()
            message_box(message='Student\'s Full Name is Required')
        elif student_age_entry.get() == '':
            student_age_entry.config(highlightcolor='red', highlightbackground='red')
            student_age_entry.focus()
            message_box(message='Student\'s Age is Required')
        elif student_contact_entry.get() == '':
            student_contact_entry.config(highlightcolor='red', highlightbackground='red')
            student_contact_entry.focus()
            message_box(message='Student\'s Contact is Required')
        elif select_class_btn.get() == '':
            select_class_btn.focus()
            message_box(message='Select Student\'s Class')
        elif student_email_entry.get() == '':
            student_email_entry.config(highlightcolor='red', highlightbackground='red')
            student_email_entry.focus()
            message_box(message='Student\'s Email is Required')
        elif not check_inavlid_email(email=student_email_entry.get().lower()):
            student_email_entry.config(highlightcolor='red', highlightbackground='red')
            student_email_entry.focus()
            message_box(message='Please Enter a Valid Email\nAddress')

        elif account_password_entry.get() == '':
            account_password_entry.config(highlightcolor='red', highlightbackground='red')
            account_password_entry.focus()
            message_box(message='Student\'s Password is Required')
        else:
            pic_data = ''
            if pic_path.get() != '':
                resize_pic = Image.open(pic_path.get()).resize((100,100))
                resize_pic.save('temp_pic.png')

                # Open resized pic in read binary (rb) mode
                read_data = open('temp_pic.png', 'rb')
                pic_data = read_data.read()
                read_data.close()
            else:
                read_data = open('images/add_image.png', 'rb')
                pic_data = read_data.read()
                read_data.close()
                pic_path.set('images/add_image.png')

            add_student_data(id_number=student_id_entry.get(),
                             password=account_password_entry.get(),
                             name=student_name_entry.get(),
                             age=student_age_entry.get(),
                             gender=student_gender.get(),
                             phone_number=student_contact_entry.get(),
                             student_class=select_class_btn.get(),
                             email=student_email_entry.get(),
                             pic_data=pic_data)
            data = f"""
{student_id_entry.get()}
{student_name_entry.get()}
{student_gender.get()}
{student_age_entry.get()}
{select_class_btn.get()}
{student_contact_entry.get()}
{student_email_entry.get()}
"""
            get_student_card = draw_student_card(student_pic_path=pic_path.get(), student_data=data)
            student_card_page(student_card_obj=get_student_card)
            add_account_page_frame.destroy()
            root.update()
            message_box('Your Account has been\nCreated Successfully')

    add_account_page_frame = Frame(root, highlightbackground=bg_color, highlightthickness=3)
    add_account_page_frame.pack(pady=5)
    add_account_page_frame.pack_propagate(False)
    add_account_page_frame.configure(width=480, height=580)

    add_pic_section_frame = Frame(add_account_page_frame, highlightbackground=bg_color, highlightthickness=2)
    add_pic_section_frame.place(x=5, y=5, width=105, height=105)

    add_pic_btn = Button(add_pic_section_frame, image=add_student_icon, bd=0, command=open_pic)
    add_pic_btn.pack()

    student_name_label = Label(add_account_page_frame, text='Enter Student Full Name', font=('Bold', 12))
    student_name_label.place(x=5, y=130)

    student_name_entry = Entry(add_account_page_frame, font=('Bold', 15), highlightcolor=bg_color, highlightbackground='gray',
                            highlightthickness=2)
    student_name_entry.place(x=5, y=160, width=180)
    student_name_entry.bind('<KeyRelease>', lambda e: remove_highlight_warning(entry=student_name_entry))

    student_gender_label = Label(add_account_page_frame, text='Select Student Gender', font=('Bold', 12))
    student_gender_label.place(x=5, y=210)

    male_gender_btn = Radiobutton(add_account_page_frame, text='Male', font=('Bold', 12), variable=student_gender, value='male')
    male_gender_btn.place(x=5, y=235)

    female_gender_btn = Radiobutton(add_account_page_frame, text='Female', font=('Bold', 12), variable=student_gender, value='female')
    female_gender_btn.place(x=75, y=235)

    student_gender.set('male')

    student_age_label = Label(add_account_page_frame, text='Enter Student Age', font=('Bold', 12))
    student_age_label.place(x=5, y=275)

    student_age_entry = Entry(add_account_page_frame, font=('Bold', 15), highlightcolor=bg_color, highlightbackground='gray',
                            highlightthickness=2)
    student_age_entry.place(x=5, y=305, width=180)
    student_age_entry.bind('<KeyRelease>', lambda e: remove_highlight_warning(entry=student_age_entry))

    student_contact_label = Label(add_account_page_frame, text='Enter Phone Number', font=('Bold', 12))
    student_contact_label.place(x=5, y=360)

    student_contact_entry = Entry(add_account_page_frame, font=('Bold', 15), highlightcolor=bg_color, highlightbackground='gray',
                            highlightthickness=2)
    student_contact_entry.place(x=5, y=390, width=180)
    student_contact_entry.bind('<KeyRelease>', lambda e: remove_highlight_warning(entry=student_contact_entry))

    student_class_label = Label(add_account_page_frame, text='Select Student Class', font=('Bold', 12))
    student_class_label.place(x=5, y=445)

    select_class_btn = Combobox(add_account_page_frame, font=('Bold', 12), state='readonly', values=class_list)
    select_class_btn.place(x=5, y=475, width=180, height=30)
    select_class_btn.bind('<KeyRelease>', lambda e: remove_highlight_warning(entry=select_class_btn))

    student_id_lable = Label(add_account_page_frame, text='Student ID Number: ', font=('Bold', 12))
    student_id_lable.place(x=240, y=35)

    student_id_entry = Entry(add_account_page_frame, font=('Bold', 18), bd=0)
    student_id_entry.place(x=380, y=35, width=80)
    student_id_entry.bind('<KeyRelease>', lambda e: remove_highlight_warning(entry=student_id_entry))

    # student_id_entry.config(state='readonly')
    generate_id_number()

    student_id_info_label = Label(add_account_page_frame, text='''Automatically Generated ID Number!
Remember Using This ID Number
to Login to Student Account''', justify='left')
    student_id_info_label.place(x=240, y=65)

    student_email_label = Label(add_account_page_frame, text='Enter Student Email', font=('Bold', 12))
    student_email_label.place(x=240, y=130)

    student_email_entry = Entry(add_account_page_frame, font=('Bold', 15), highlightcolor=bg_color, highlightbackground='gray',
                            highlightthickness=2)
    student_email_entry.place(x=240, y=160, width=180)
    student_email_entry.bind('<KeyRelease>', lambda e: remove_highlight_warning(entry=student_email_entry))

    email_info_label = Label(add_account_page_frame, text='''Via Email Address, Student Can Recover
Account In Case of Forgotten Password
And Will Also Get Notifications''', justify='left')
    email_info_label.place(x=240, y=200)

    account_password_label = Label(add_account_page_frame, text='Create Account Password', font=('Bold', 12))
    account_password_label.place(x=240, y=275)

    account_password_entry = Entry(add_account_page_frame, font=('Bold', 15), highlightcolor=bg_color, highlightbackground='gray',
                            highlightthickness=2)
    account_password_entry.place(x=240, y=305, width=180)
    account_password_entry.bind('<KeyRelease>', lambda e: remove_highlight_warning(entry=account_password_entry))

    password_info_label = Label(add_account_page_frame, text='''Via Student Created Password And
The Provided Student ID Number, 
Student Can Login Into Account''', justify='left')
    password_info_label.place(x=240, y=345)

    home_btn = Button(add_account_page_frame, text='Home', font=('Bold', 15), bg='red', fg=white, bd=0, command=forward_to_welcome_page)
    home_btn.place(x=240, y=420)


init_db()
welcome_page()
if __name__ == "__main__":
    root.mainloop()


