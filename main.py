import tkinter as ttk

from CRMStarterApp import CRMStarterApp
from utility_function import basis_handle_errors


@basis_handle_errors(text='PackageGeneratorApp')
def main():
    root = ttk.Tk()
    CRMStarterApp(root)
    # root.iconbitmap('icons/icon.ico')
    root.mainloop()


if __name__ == "__main__":
    main()
