import npyscreen


class App(npyscreen.NPSApp):
    def main(self):
        form = npyscreen.FormBaseNew(name='EKOiE')
        form.add_widget(npyscreen.TitleSelectOne, name='Track number', values=[1, 2, 3, 4, 5])
        form.edit()


if __name__ == '__main__':
    app = App()
    app.run()
