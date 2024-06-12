import tkinter as tk

class EntryWithPlaceholder(tk.Entry):
    '''
    Класс для поля ввода с placeholder
    '''
    def __init__(self, master=None, placeholder="PLACEHOLDER", color='grey', show=None):
        super().__init__(master, justify=tk.CENTER)

        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self['fg']

        self.bind("<FocusIn>", self.foc_in)
        self.bind("<FocusOut>", self.foc_out)

        self.put_placeholder()
        self.show = show

    def put_placeholder(self):
        '''
        помещает в поле ввода placeholder
        '''
        self.insert(0, self.placeholder)
        self['fg'] = self.placeholder_color

    def foc_in(self, *args):
        '''
        при получении фокуса
        '''
        if self['fg'] == self.placeholder_color:
            if self.show:
                self.configure(show='*')
            self.delete('0', 'end')
            self['fg'] = self.default_fg_color

    def foc_out(self, *args):
        '''
        при потере фокуса
        '''
        if not self.get():
            self.configure(show='')
            self.put_placeholder()

if __name__ == "__main__": 
    root = tk.Tk() 
    username = EntryWithPlaceholder(root, "username")
    password = EntryWithPlaceholder(root, "password", 'blue')
    username.pack()
    password.pack()  
    root.mainloop()
