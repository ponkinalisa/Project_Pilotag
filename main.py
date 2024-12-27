import sys
import sqlite3
import datetime as dt
import maya
from PIL import Image
import os

from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMessageBox, QFileDialog


class ChangeData(QMainWindow):
    def __init__(self):
        self.path = ''
        super().__init__()
        uic.loadUi('UI/change_information.ui', self)

        con = sqlite3.connect('data.sqlite')
        cur = con.cursor()
        self.combo_type.addItems([i[1] for i in cur.execute("""SELECT * FROM Types""")])
        self.status_edit.addItems([i[1] for i in cur.execute("""SELECT * FROM status""")])
        self.gender_edit.addItems([i[1] for i in cur.execute("""SELECT * FROM genders""")])
        con.close()

        self.name.setText(str(ex.label_name.text()[8:]))
        self.birthday.setText(str(ex.label_birthday.text()[15:]))
        self.allergies.setText(str(ex.label_allergies.text()[10:]))
        self.combo_type.setCurrentText(str(ex.label_type.text()[5:]))
        self.description_edit.setText(str(ex.description.text()[16:]))
        self.adres_edit.setText(str(ex.owner_2.text()[16:]))
        self.owner_edit.setText(str(ex.owner.text()[10:]))
        self.weight_edit.setText(str(ex.weigth.text()[5:]))
        self.status_edit.setCurrentText(str(ex.status.text()[8:]))
        self.gender_edit.setCurrentText(str(ex.label_gender.text()[5:]))

        self.save_changes.clicked.connect(self.save)
        self.add_photo.clicked.connect(self.photo)

    def correct_date(self, date):  # функция для проверки корректности даты
        try:
            dt = maya.parse(date).datetime()
            return True
        except Exception:
            return False

    def save(self):
        try:
            date = dt.date.today()
            year = date.year
            month = date.month
            day = date.day
            if self.birthday.text() == '':
                raise ValueError('Ошибка при вводе даты! Ввод даты осуществлен некорректно. '
                                 'Пожалуйста, убедитесь, что дата введена в формате XX.XX.XXXX')
            elif len(self.birthday.text().split('.')) != 3:
                raise ValueError('Ошибка при вводе даты! Ввод даты осуществлен некорректно. '
                                 'Пожалуйста, убедитесь, что дата введена в формате XX.XX.XXXX')
            elif (self.birthday.text().split('.')[0].isdigit() is False or
                  self.birthday.text().split('.')[1].isdigit() is False or
                  self.birthday.text().split('.')[2].isdigit() is False):
                raise ValueError('Ошибка при вводе даты! Ввод даты осуществлен некорректно. '
                                 'Пожалуйста, убедитесь, что в в написании даты отсутствуют опечатки')
            if self.correct_date(self.birthday.text()) == False:
                raise ValueError('Ошибка при вводе даты! Такой даты не существует')
            year1, month1, day1 = tuple([int(i) for i in self.birthday.text().split('.')][::-1])
            if year1 > year:
                raise ValueError('Ошибка при вводе даты! Указана дата, которая более поздняя, чем сегодня.')
            elif year1 >= year and month1 > month:
                raise ValueError('Ошибка при вводе даты! Указана дата, которая более поздняя, чем сегодня.')
            elif year1 >= year and month1 >= month and day1 > day:
                raise ValueError('Ошибка при вводе даты! Животное родилось в будущем?..')
            if self.owner_edit.text() == '':
                raise ValueError('Ошибка при вводе имени! Поле "Сдал ФИО" является обязательным для заполнения')
            if self.adres_edit.text() == '':
                raise ValueError('Ошибка при вводе адреса! Поле "Адрес сдавшего" является обязательным для заполнения')
            id = int(ex.label_id.text()[4:])
            con = sqlite3.connect('data.sqlite')
            cur = con.cursor()
            print(
                f"""UPDATE owners SET fio = '{self.owner_edit.text()}', adres = '{self.adres_edit.text()}', WHERE animal_id = {id}""")
            cur.execute(f"""UPDATE owners SET fio = '{self.owner_edit.text()}', adres = '{self.adres_edit.text()}' WHERE animal_id = {id}""")

            ow_id = cur.execute(f"""SELECT id FROM owners WHERE animal_id = {id}""").fetchone()[0]
            cur.execute(f"""UPDATE animals 
            SET name = '{self.name.text().lower()}', 
            type =(SELECT id FROM Types WHERE name = '{self.combo_type.currentText()}'), 
            birthday = '{self.birthday.text()}', 
            allergies = '{self.allergies.text()}', 
            path = '{self.path}',
            owner_id = {ow_id},
            weigth = '{self.weight_edit.text()}',
            description = '{self.description_edit.text()}',
            status = (SELECT id FROM status WHERE name = '{self.status_edit.currentText()}'),
            gender = (SELECT id FROM genders WHERE name = '{self.gender_edit.currentText()}')
            WHERE id = {id}""")

            con.commit()
            con.close()
            ex.download()

            for i in range(ex.tableWidget.rowCount()):
                if ex.tableWidget.item(i, 0).text() == str(id):
                    ex.tableWidget.setCurrentItem(ex.tableWidget.item(i, 0))
            ex.getting_data()

            QMessageBox.information(self, '', 'Запись Обновлена! Поздравляем!', buttons=QMessageBox.StandardButton.Ok)
            self.close()
        except Exception as e:
            QMessageBox.warning(self, '', '%s' % e, buttons=QMessageBox.StandardButton.Ok)

    def photo(self):
        self.path = QFileDialog.getOpenFileName(self, 'Выбрать картинку', '')[0]
        print(self.path)


class Illnesses(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('UI/append_illnesses.ui', self)

        self.append_in_illnesses_btn.clicked.connect(self.append)

    def correct_date(self, date):  # функция для проверки корректности даты
        try:
            dt = maya.parse(date).datetime()
            return True
        except Exception:
            return False


    def append(self):
        try:
            date = dt.date.today()
            year = date.year
            month = date.month
            day = date.day
            if self.dateEdit.text() == '':
                raise ValueError('Ошибка при вводе даты! Ввод даты осуществлен некорректно. '
                                 'Пожалуйста, убедитесь, что дата введена в формате XX.XX.XXXX')
            elif len(self.dateEdit.text().split('.')) != 3:
                raise ValueError('Ошибка при вводе даты! Ввод даты осуществлен некорректно. '
                                 'Пожалуйста, убедитесь, что дата введена в формате XX.XX.XXXX')
            elif (self.dateEdit.text().split('.')[0].isdigit() is False or
                self.dateEdit.text().split('.')[1].isdigit() is False or
                self.dateEdit.text().split('.')[2].isdigit() is False):
                raise ValueError('Ошибка при вводе даты! Ввод даты осуществлен некорректно. '
                                 'Пожалуйста, убедитесь, что в в написании даты отсутствуют опечатки')
            if self.correct_date(self.dateEdit.text()) == False:
                raise ValueError('Ошибка при вводе даты! Такой даты не существует')
            year1, month1, day1 = tuple([int(i) for i in self.dateEdit.text().split('.')][::-1])
            if year1 > year:
                raise ValueError('Ошибка при вводе даты! Указана дата, которая более поздняя, чем сегодня. '
                                 'Разве животные болеют по расписанию?')
            elif year1 >= year and month1 > month:
                raise ValueError('Ошибка при вводе даты! Указана дата, которая более поздняя, чем сегодня.'
                                 ' Разве животные болеют по расписанию?')
            elif year1 >= year and month1 >= month and day1 > day:
                raise ValueError('Ошибка при вводе даты! Указана дата, которая более поздняя, чем сегодня. '
                                 'Разве животные болеют по расписанию?')
            ex.w.tableWidget.setRowCount(ex.w.tableWidget.rowCount() + 1)
            ex.w.tableWidget.setItem(ex.w.tableWidget.rowCount() - 1, 0, QTableWidgetItem(str(self.dateEdit.text())))
            ex.w.tableWidget.setItem(ex.w.tableWidget.rowCount() - 1, 1, QTableWidgetItem(str(self.doctor.text())))
            ex.w.tableWidget.setItem(ex.w.tableWidget.rowCount() - 1, 2,
                                     QTableWidgetItem(str(self.textEdit.toPlainText())))
            QMessageBox.information(self, '', 'Запись добавлена! Поздравляем!', buttons=QMessageBox.StandardButton.Ok)
            self.close()
        except Exception as e:
            print('%s' % e)
            QMessageBox.warning(self, '', '%s' % e, buttons=QMessageBox.StandardButton.Ok)

class Illnesses22(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('UI/append_illnesses.ui', self)

        self.append_in_illnesses_btn.clicked.connect(self.append)

    def correct_date(self, date):  # функция для проверки корректности даты
        try:
            dt = maya.parse(date).datetime()
            return True
        except Exception:
            return False


    def append(self):
        try:
            con = sqlite3.connect('data.sqlite')
            cur = con.cursor()
            date = dt.date.today()
            id = int(ex.label_id.text()[4:])
            year = date.year
            month = date.month
            day = date.day
            if self.dateEdit.text() == '':
                raise ValueError('Ошибка при вводе даты! Ввод даты осуществлен некорректно. '
                                 'Пожалуйста, убедитесь, что дата введена в формате XX.XX.XXXX')
            elif len(self.dateEdit.text().split('.')) != 3:
                raise ValueError('Ошибка при вводе даты! Ввод даты осуществлен некорректно. '
                                 'Пожалуйста, убедитесь, что дата введена в формате XX.XX.XXXX')
            elif (self.dateEdit.text().split('.')[0].isdigit() is False or
                self.dateEdit.text().split('.')[1].isdigit() is False or
                self.dateEdit.text().split('.')[2].isdigit() is False):
                raise ValueError('Ошибка при вводе даты! Ввод даты осуществлен некорректно. '
                                 'Пожалуйста, убедитесь, что в в написании даты отсутствуют опечатки')
            if self.correct_date(self.dateEdit.text()) == False:
                raise ValueError('Ошибка при вводе даты! Такой даты не существует')
            year1, month1, day1 = tuple([int(i) for i in self.dateEdit.text().split('.')][::-1])
            if year1 > year:
                raise ValueError('Ошибка при вводе даты! Указана дата, которая более поздняя, чем сегодня. '
                                 'Разве животные болеют по расписанию?')
            elif year1 >= year and month1 > month:
                raise ValueError('Ошибка при вводе даты! Указана дата, которая более поздняя, чем сегодня.'
                                 ' Разве животные болеют по расписанию?')
            elif year1 >= year and month1 >= month and day1 > day:
                raise ValueError('Ошибка при вводе даты! Указана дата, которая более поздняя, чем сегодня. '
                                 'Разве животные болеют по расписанию?')
            ex.tableWidget_2.setRowCount(ex.tableWidget_2.rowCount() + 1)
            ex.tableWidget_2.setItem(ex.tableWidget_2.rowCount() - 1, 0, QTableWidgetItem(str(self.dateEdit.text())))
            ex.tableWidget_2.setItem(ex.tableWidget_2.rowCount() - 1, 1,
                                     QTableWidgetItem(str(self.textEdit.toPlainText())))
            QMessageBox.information(self, '', 'Запись добавлена! Поздравляем!', buttons=QMessageBox.StandardButton.Ok)
            cur.execute(f"""INSERT INTO History(animal_id, date, doctor_fio, description) VALUES({id},
            '{str(self.dateEdit.text())}', '{self.doctor.text()}', '{str(self.textEdit.toPlainText())}')""")
            con.commit()
            con.close()
            ex.getting_data()
            self.close()
        except Exception as e:
            print('%s' % e)
            QMessageBox.warning(self, '', '%s' % e, buttons=QMessageBox.StandardButton.Ok)


class Append(QMainWindow):
    def __init__(self):
         super().__init__()
         uic.loadUi('UI/append.ui', self)
         self.a = None
         self.path = ''

         con = sqlite3.connect('data.sqlite')
         cur = con.cursor()
         self.type_edit.addItems([i[1] for i in cur.execute("""SELECT * FROM Types""")])
         self.gender_edit.addItems([i[1] for i in cur.execute("""SELECT * FROM genders""")])
         self.status_edit.addItems([i[1] for i in cur.execute("""SELECT * FROM status""")])
         con.close()

         self.tableWidget.setColumnCount(3)
         self.tableWidget.setHorizontalHeaderLabels(['Дата', 'Принимающий\n врач\n ФИО', 'Описание'])
         self.tableWidget.setRowCount(0)
         self.tableWidget.horizontalHeader().setDefaultSectionSize(100)
         self.tableWidget.horizontalHeader().setMinimumSectionSize(175)


         self.save.clicked.connect(self.save_result)
         self.new_illness_btn.clicked.connect(self.illnesses)
         self.add_photo.clicked.connect(self.photo)

    def correct_date(self, date):  # функция для проверки корректности даты
        try:
            dt = maya.parse(date).datetime()
            return True
        except Exception:
            return False


    def save_result(self):
        try:
            con = sqlite3.connect('data.sqlite')
            cur = con.cursor()
            date = dt.date.today()
            year = date.year
            month = date.month
            day = date.day
            date = '.'.join([i for i in str(date).split('-')[::-1]])
            names = cur.execute(f"""SELECT id FROM animals WHERE name = '{self.name_edit.text()}'""")
            names = [i[0] for i in names]
            if self.owner_edit.text() == '':
                raise ValueError('Ошибка при вводе имени! Поле для ввода "Сдал ФИО" является обязательным')
            if self.adres_edit.text() == '':
                raise ValueError('Ошибка при вводе адреса! Поле для ввода "Адрес сдавшего" является обязательным')
            if self.birthday_edit.text() == '':
                cur.execute(f"""INSERT INTO animals(name, gender, type, birthday, registration_date, allergies, path, status, weigth, description) 
                            VALUES('{self.name_edit.text().lower()}', (SELECT id FROM genders WHERE name = 
                            '{self.gender_edit.currentText()}'), (SELECT id FROM Types WHERE name = '{self.type_edit.currentText()}'), 
                            NULL, '{date}', '{self.allergies_edit.text()}', '{self.path}', 
                            (SELECT id FROM status WHERE name = '{self.status_edit.currentText()}'), '{self.weight_edit.text()}', '{self.description_edit.text()}')""")
                con.commit()
                con.close()
                self.app_ill()
                ex.download()
                QMessageBox.information(self, '', 'запись добавлена! Поздравляем!',
                                        buttons=QMessageBox.StandardButton.Ok)
                self.close()
                return
            elif len(self.birthday_edit.text().split('.')) != 3:
                raise ValueError('Ошибка при вводе даты! Ввод даты осуществлен некорректно. '
                                 'Пожалуйста, убедитесь, что дата введена в формате XX.XX.XXXX')
            elif (self.birthday_edit.text().split('.')[0].isdigit() is False or
                self.birthday_edit.text().split('.')[1].isdigit() is False or
                self.birthday_edit.text().split('.')[2].isdigit() is False):
                raise ValueError('Ошибка при вводе даты! Ввод даты осуществлен некорректно. '
                                 'Пожалуйста, убедитесь, что в в написании даты отсутствуют опечатки')
            if self.correct_date(self.birthday_edit.text()) == False:
                raise ValueError('Ошибка при вводе даты! Такой даты не существует')
            year1, month1, day1 = tuple([int(i) for i in self.birthday_edit.text().split('.')][::-1])
            if year1 > year:
                raise ValueError('Ошибка при вводе даты! Животное не может родиться позднее, чем быть '
                                 'зарегестрированным')
            elif year1 >= year and month1 > month:
                raise ValueError('Ошибка при вводе даты! Животное не может родиться позднее, чем быть '
                                 'зарегестрированным')
            elif year1 >= year and month1 >= month and day1 > day:
                raise ValueError('Ошибка при вводе даты! Животное не может родиться позднее, чем быть '
                                 'зарегестрированным')
            cur.execute(f"""INSERT INTO animals(name, gender, type, birthday, registration_date, allergies, path, status, weigth, description) 
            VALUES('{self.name_edit.text().lower()}', (SELECT id FROM genders WHERE name = 
            '{self.gender_edit.currentText()}'), (SELECT id FROM Types WHERE name = '{self.type_edit.currentText()}'), 
            '{self.birthday_edit.text()}', '{date}', '{self.allergies_edit.text()}', '{self.path}', 
            (SELECT id FROM status WHERE name = '{self.status_edit.currentText()}'), '{self.weight_edit.text()}', '{self.description_edit.text()}')""")
            QMessageBox.information(self, '', 'запись добавлена! Поздравляем!', buttons=QMessageBox.StandardButton.Ok)
            con.commit()
            con.close()
            self.app_ill()
            ex.download()
        except Exception as e:
            QMessageBox.warning(self, '', '%s' % e, buttons=QMessageBox.StandardButton.Ok)


    def app_ill(self):
        con = sqlite3.connect('data.sqlite')
        cur = con.cursor()
        id = cur.execute(f"""SELECT MAX(id) FROM animals""").fetchone()
        id = id[0]
        print(0)
        cur.execute(f"""INSERT INTO owners(animal_id, FIO, adres) VALUES({id}, '{self.owner_edit.text()}', 
        '{self.adres_edit.text()}')""")
        print(0)
        for i in range(self.tableWidget.rowCount()):
            cur.execute(f"""INSERT INTO history(animal_id, date, doctor_fio, description) VALUES({id}, 
                        '{self.tableWidget.item(i, 0).text()}', '{self.tableWidget.item(i, 1).text()}', 
                        '{self.tableWidget.item(i, 2).text()}')""")
        ow_id = cur.execute(f"""SELECT MAX(id) FROM owners""").fetchone()[0]
        cur.execute(f"""UPDATE animals SET owner_id = {ow_id} WHERE id = {id}""")
        con.commit()
        con.close()


    def illnesses(self):
        try:
            if self.a is None:
                self.a = Illnesses()
            self.a.show()
        except Exception as e:
            print('%s' % e)

    def photo(self):
        self.path = QFileDialog.getOpenFileName(self, 'Выбрать картинку', '')[0]
        QMessageBox.information(self, '', 'Фото добавлено! Поздравляем!', buttons=QMessageBox.StandardButton.Ok)



class Project(QMainWindow):
    def __init__(self):
        self.path = ''
        self.start = False
        self.w = None
        self.e = None # self.w == self.widget
        self.widget = None # another widget
        super().__init__()
        uic.loadUi('UI/project.ui', self)
        con = sqlite3.connect('data.sqlite')
        cur = con.cursor()
        self.combo_sorting.addItems([i[1] for i in cur.execute("""SELECT * FROM Types""")])
        con.close()

        self.tableWidget_2.setColumnCount(3)
        self.tableWidget_2.setHorizontalHeaderLabels(['Дата', 'Принимающий\n врач\n ФИО', 'Описание'])
        self.tableWidget_2.setRowCount(0)
        self.tableWidget_2.horizontalHeader().setDefaultSectionSize(100)
        self.tableWidget_2.horizontalHeader().setMinimumSectionSize(175)
        self.tabWidget.setCurrentWidget(self.tab)

        self.bownload_button.clicked.connect(self.download)
        self.combo_sorting.currentTextChanged.connect(self.sorting_type)
        self.append_button.clicked.connect(self.append)
        self.delete_button.clicked.connect(self.delete)
        self.get_data.clicked.connect(self.getting_data)
        self.radioButton.toggled.connect(self.update)
        self.change_data_button.clicked.connect(self.change_individual_data)
        self.add_illness.clicked.connect(self.add_ill)
        self.delete_illness.clicked.connect(self.del_ill)
        self.save_for_printing.clicked.connect(self.save_for_print)
        self.get_photo.clicked.connect(self.photo)

        self.download()

    def download(self):
        try:
            if self.start is False:
                self.start = True
            con = sqlite3.connect('data.sqlite')
            cur = con.cursor()
            genders = [i[1] for i in cur.execute("""SELECT * FROM genders""")]
            types = [i[1] for i in cur.execute("""SELECT * FROM Types""")]
            status = [i[1] for i in cur.execute("""SELECT * FROM status""")]
            names = [i[1] for i in cur.execute("""SELECT * FROM owners""")]
            owner = [i[0] for i in cur.execute("""SELECT * FROM owners""")]
            text = self.combo_sorting.currentText()
            if text == 'Все' and self.search.text() == '':
                data = cur.execute("""SELECT * FROM animals""")
            elif text == 'Все' and self.search.text() != '':
                data = cur.execute(f"""SELECT * FROM animals WHERE name = '{self.search.text().lower()}'""").fetchall()
            elif self.search.text() != '':
                data = cur.execute(
                    f"""SELECT * FROM animals WHERE type =(SELECT id FROM Types WHERE name = '{text.lower()}') AND 
                    name = '{self.search.text().lower()}'""").fetchall()
            else:
                data = cur.execute(f"""SELECT * FROM animals WHERE type =(SELECT id FROM Types WHERE name = 
                '{text.lower()}')""").fetchall()
            self.tableWidget.setColumnCount(10)
            self.tableWidget.setHorizontalHeaderLabels(
                ['ID', 'ИМЯ', 'СТАТУС', 'ФИО \n СДАВШЕГО', 'ПОЛ', 'ВИД', 'ДАТА \n РОЖДЕНИЯ', 'ДАТА \n РЕГИСТРАЦИИ',
                 'АЛЛЕРГИИ', 'ВЕС'])
            self.tableWidget.setRowCount(0)
            if self.radioButton.isChecked() == True:
                data = sorted([i for i in list(data)], key=lambda x: (int(str(x[6]).split('.')[2]),
                                                                      int(str(x[6]).split('.')[1]),
                                                                      int(str(x[6]).split('.')[0])))
            for i, row in enumerate(data):
                self.tableWidget.setRowCount(
                    self.tableWidget.rowCount() + 1)
                for j, elem in enumerate(row):
                    if j >= 10:
                        break
                    if j == 4 and elem is not None:
                        elem = genders[int(elem)]
                    elif j == 5 and elem is not None:
                        elem = types[int(elem)]
                    elif j == 2 and elem is not None:
                        elem = status[int(elem)]
                    elif j == 3 and elem is not None:
                        elem = names[owner.index(elem)]
                    if elem is None or elem == '':
                        elem = 'нет'
                    self.tableWidget.setItem(
                        i, j, QTableWidgetItem(str(elem)))
            con.close()
        except Exception as e:
            print('%s' % e)

    def sorting_type(self):
        try:
            text = self.combo_sorting.currentText()
            if text == 'Все':
                self.download()
            elif self.start:
                con = sqlite3.connect('data.sqlite')
                cur = con.cursor()
                if self.search.text() != '':
                    data = cur.execute(f"""SELECT * FROM animals WHERE type =(SELECT id FROM Types WHERE name = 
                    '{text.lower()}') AND name = '{self.search.text().lower()}'""").fetchall()
                else:
                    data = cur.execute(f"""SELECT * FROM animals WHERE type =(SELECT id FROM Types WHERE name = 
                    '{text.lower()}')""").fetchall()
                genders = [i[1] for i in cur.execute("""SELECT * FROM genders""")]
                types = [i[1] for i in cur.execute("""SELECT * FROM Types""")]
                status = [i[1] for i in cur.execute("""SELECT * FROM status""")]
                names = [i[1] for i in cur.execute("""SELECT * FROM owners""")]
                owner = [i[0] for i in cur.execute("""SELECT * FROM owners""")]
                self.tableWidget.setColumnCount(10)
                self.tableWidget.setHorizontalHeaderLabels(
                    ['ID', 'ИМЯ', 'СТАТУС', 'ФИО \n СДАВШЕГО', 'ПОЛ', 'ВИД', 'ДАТА \n РОЖДЕНИЯ', 'ДАТА \n РЕГИСТРАЦИИ',
                     'АЛЛЕРГИИ', 'ВЕС'])
                self.tableWidget.setRowCount(0)
                if self.radioButton.isChecked() == True:
                    data = sorted([i for i in list(data)], key=lambda x: (int(str(x[6]).split('.')[2]),
                                                                          int(str(x[6]).split('.')[1]),
                                                                          int(str(x[6]).split('.')[0])))
                for i, row in enumerate(data):
                    self.tableWidget.setRowCount(
                        self.tableWidget.rowCount() + 1)
                    for j, elem in enumerate(row):
                        if j >= 10:
                            break
                        if j == 4 and elem is not None:
                            elem = genders[int(elem)]
                        elif j == 5 and elem is not None:
                            elem = types[int(elem)]
                        elif j == 2 and elem is not None:
                            elem = status[int(elem)]
                        elif j == 3 and elem is not None:
                            elem = names[owner.index(elem)]
                        if elem is None or elem == '':
                            elem = 'нет'
                        self.tableWidget.setItem(
                            i, j, QTableWidgetItem(str(elem)))
                con.close()
        except Exception as e:
            print('%s' % e)

    def append(self):
        try:
            if self.w is None:
                self.w = Append()
            self.w.show()
        except Exception as e:
            print('%s' % e)

    def delete(self):
        try:
            con = sqlite3.connect('data.sqlite')
            cur = con.cursor()
            rows = list(set([i.row() for i in self.tableWidget.selectedItems()]))
            ids = [self.tableWidget.item(i, 0).text() for i in rows]
            names = [self.tableWidget.item(i, 1).text() for i in rows]
            valid = QMessageBox.question(
                self, '', "Действительно удалить из списка животных с кличками " + ", ".join(names),
                buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if valid == QMessageBox.StandardButton.No:
                con.close()
                return
            cur.execute("DELETE FROM animals WHERE id IN (" + ", ".join(
                '?' * len(ids)) + ")", ids)
            con.commit()
            con.close()
            valid = QMessageBox.information(self, '', "Записи были успешно удалены.",
                                            buttons=QMessageBox.StandardButton.Ok)
            self.download()
        except Exception as e:
            print('%s' % e)

    def getting_data(self):
        try:
            con = sqlite3.connect('data.sqlite')
            cur = con.cursor()
            row = sorted(list(set([i.row() for i in self.tableWidget.selectedItems()])))[0]
            self.label_name.setText(f'Кличка: {self.tableWidget.item(row, 1).text()}')
            self.cur_id = int(self.tableWidget.item(row, 0).text())
            self.label_id.setText(f'ID: {self.tableWidget.item(row, 0).text()}')
            self.label_type.setText(f'Вид: {self.tableWidget.item(row, 5).text()}')
            self.label_birthday.setText(f'Дата рождения: {self.tableWidget.item(row, 6).text()}')
            self.label_registration_date.setText(f'Дата регистрации: {self.tableWidget.item(row, 7).text()}')
            self.label_allergies.setText(f'Аллергии: {self.tableWidget.item(row, 8).text()}')
            self.label_gender.setText(f'Пол: {self.tableWidget.item(row, 4).text()}')
            self.status.setText(f'Статус: {self.tableWidget.item(row, 2).text()}')
            self.owner.setText(f'Сдал ФИО: {self.tableWidget.item(row, 3).text()}')
            self.weigth.setText(f'Вес: {self.tableWidget.item(row, 9).text()}')
            desc = cur.execute(f"""SELECT description FROM animals WHERE id = 
                                   {int(self.tableWidget.item(row, 0).text())}""").fetchone()[0]
            if desc is None:
                desc = 'нет'
            adres = cur.execute(f"""SELECT adres FROM owners WHERE animal_id = 
                                   {self.tableWidget.item(row, 0).text()}""").fetchone()[0]
            if adres is None:
                adres = 'нет'
            self.description.setText(f'Особые приметы: {desc}')
            self.owner_2.setText(f'Адрес сдавшего: {adres}')


            self.tableWidget_2.setColumnCount(3)
            self.tableWidget_2.setHorizontalHeaderLabels(['Дата', 'Принимающий\n врач\n ФИО', 'Описание'])
            self.tableWidget_2.setRowCount(0)
            data = cur.execute(f"""SELECT date, doctor_fio, description FROM History WHERE animal_id = 
                                   {self.tableWidget.item(row, 0).text()}""")
            for i, row in enumerate(data):
                self.tableWidget_2.setRowCount(
                    self.tableWidget_2.rowCount() + 1)
                for j, elem in enumerate(row):
                    if elem is None:
                        elem = ''
                    self.tableWidget_2.setItem(
                        i, j, QTableWidgetItem(str(elem)))
            con.close()
            self.tabWidget.setCurrentWidget(self.tab_2)
        except Exception as e:
            print('%s' % e)

    def update(self):
        self.download()

    def change_individual_data(self):
        try:
            if self.widget is None:
                self.widget = ChangeData()
            self.widget.show()
        except Exception as e:
            print('%s' % e)

    def add_ill(self):
        try:
            if self.e is None:
                self.e = Illnesses22()
            self.e.show()
        except Exception as e:
            print('%s' % e)

    def del_ill(self):
        try:
            con = sqlite3.connect('data.sqlite')
            cur = con.cursor()
            rows = list(set([i.row() for i in self.tableWidget_2.selectedItems()]))
            dates = [self.tableWidget_2.item(i, 0).text() for i in rows]
            descriptions = [self.tableWidget_2.item(i, 2).text() for i in rows]
            d = dates + descriptions
            valid = QMessageBox.question(
                self, '', "Вы действительно желаете удалить из списка выбранные элементы?",
                buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            id = int(self.label_id.text()[4:])
            if valid == QMessageBox.StandardButton.Yes:
                cur.execute(f"""DELETE FROM History WHERE animal_id = {id} AND date IN (""" + ", ".join(
                    '?' * len(dates)) + ") AND description IN (" + ", ".join(
                    '?' * len(descriptions)) + ")", d)
                valid = QMessageBox.information(self, '', "Записи были успешно удалены.",
                                                buttons=QMessageBox.StandardButton.Ok)
                con.commit()
                self.getting_data()
            con.close()
        except Exception as e:
            print('%s' % e)

    def save_for_print(self):
        date = dt.datetime.now()
        year = str(date.year)
        month = str(date.month)
        day = str(date.day)
        hour = str(date.hour)
        minute = str(date.minute)
        second = str(date.second)
        date = ''.join([year, month, day, hour, minute, second])
        print(date)
        fname = date + '.txt'
        with open(fname, 'w', encoding='UTF-8') as f:
            f.write(self.label_name.text() + '\n')
            f.write(self.label_id.text() + '\n')
            f.write(self.label_type.text() + '\n')
            f.write(self.label_gender.text() + '\n')
            f.write(self.status.text() + '\n')
            f.write(self.label_birthday.text() + '\n')
            f.write(self.label_registration_date.text() + '\n')
            f.write(self.weigth.text() + '\n')
            f.write(self.owner.text() + '\n')
            f.write(self.owner_2.text() + '\n')
            f.write(self.description.text() + '\n')
            f.write(self.label_allergies.text() + '\n')
            f.write('Информация о заболеваниях:\n')
            if self.tableWidget_2.rowCount() == 0:
                f.write('Информация о заболеваниях отсутствует.')
            for i in range(self.tableWidget_2.rowCount()):
                s = (f'Дата: {self.tableWidget_2.item(i, 0).text()}\nЛечащий врач: '
                     f'{self.tableWidget_2.item(i, 1).text()}\nОписание заболевния: '
                     f'{self.tableWidget_2.item(i, 2).text()}\n')
                f.write(s)
        valid = QMessageBox.information(self, '', f"Данные сохранены на устройство в файл с именем {fname}. "
                                                  f"Файл находится в папке программы",
                                        buttons=QMessageBox.StandardButton.Ok)
        f.close()

    def photo(self):
        try:
            con = sqlite3.connect('data.sqlite')
            cur = con.cursor()
            self.path = cur.execute(f"""SELECT path FROM animals WHERE id = {self.cur_id}""").fetchone()[0]
            con.close()
            if self.path is None or self.path == '':
                valid = QMessageBox.information(self, '', f"Нет фото", buttons=QMessageBox.StandardButton.Ok)
                return
            if not os.path.exists(self.path):
                valid = QMessageBox.information(self, '', f"Что-то пошло не так. Возможно, путь фото изменился. "
                                                          f"Попробуйте изменить фото",
                                                buttons=QMessageBox.StandardButton.Ok)
                return
            img = Image.open(fr'{self.path}')
            img.show()
        except Exception as e:
            valid = QMessageBox.information(self, '', f"Нет фото", buttons=QMessageBox.StandardButton.Ok)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Project()
    ex.show()
    sys.exit(app.exec())