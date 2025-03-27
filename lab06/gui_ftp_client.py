import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext, simpledialog
import socket
import os


class FTPClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("FTP Client")
        self.root.geometry("800x600")

        # Переменные для ввода
        self.host_var = tk.StringVar(value="127.0.0.1")
        self.port_var = tk.StringVar(value="21")
        self.user_var = tk.StringVar(value="TestUser")
        self.pass_var = tk.StringVar(value="12345")
        self.file_content_var = tk.StringVar()

        # Сокеты
        self.control_socket = None
        self.data_socket = None

        # GUI
        self.setup_ui()

    def setup_ui(self):
        # Фрейм для подключения
        connect_frame = ttk.LabelFrame(self.root, text="Подключение", padding=10)
        connect_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(connect_frame, text="Сервер:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(connect_frame, textvariable=self.host_var, width=20).grid(row=0, column=1)

        ttk.Label(connect_frame, text="Порт:").grid(row=0, column=2, sticky=tk.W)
        ttk.Entry(connect_frame, textvariable=self.port_var, width=5).grid(row=0, column=3)

        ttk.Label(connect_frame, text="Пользователь:").grid(row=1, column=0, sticky=tk.W)
        ttk.Entry(connect_frame, textvariable=self.user_var).grid(row=1, column=1)

        ttk.Label(connect_frame, text="Пароль:").grid(row=1, column=2, sticky=tk.W)
        ttk.Entry(connect_frame, textvariable=self.pass_var, show="*").grid(row=1, column=3)

        ttk.Button(connect_frame, text="Подключиться", command=self.connect).grid(row=2, column=0, columnspan=4, pady=5)

        # Фрейм для файлов
        files_frame = ttk.LabelFrame(self.root, text="Файлы", padding=10)
        files_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.file_tree = ttk.Treeview(files_frame, columns=("Name", "Size"), show="headings")
        self.file_tree.heading("Name", text="Имя")
        self.file_tree.heading("Size", text="Размер")
        self.file_tree.pack(fill=tk.BOTH, expand=True)

        # Фрейм для CRUD-операций
        crud_frame = ttk.Frame(self.root)
        crud_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(crud_frame, text="Создать", command=self.create_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(crud_frame, text="Просмотреть", command=self.retrieve_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(crud_frame, text="Обновить", command=self.update_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(crud_frame, text="Удалить", command=self.delete_file).pack(side=tk.LEFT, padx=2)

        # Фрейм для содержимого файла
        content_frame = ttk.LabelFrame(self.root, text="Содержимое файла", padding=10)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.content_text = scrolledtext.ScrolledText(content_frame, wrap=tk.WORD)
        self.content_text.pack(fill=tk.BOTH, expand=True)

    def connect(self):
        try:
            self.control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.control_socket.connect((self.host_var.get(), int(self.port_var.get())))
            response = self._get_response()
            if not response.startswith("220"):
                raise Exception("Ошибка подключения")

            self._send_command(f"USER {self.user_var.get()}")
            response = self._get_response()
            if not response.startswith("331"):
                raise Exception("Ошибка пользователя")

            self._send_command(f"PASS {self.pass_var.get()}")
            response = self._get_response()
            if not response.startswith("230"):
                raise Exception("Ошибка пароля")

            self.list_files()
            messagebox.showinfo("Успех", "Подключение установлено!")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def list_files(self):
        try:
            self._setup_data_connection()
            self._send_command("LIST")
            response = self._get_response()

            data = self._receive_data()
            self.data_socket.close()
            self._get_response()

            self.file_tree.delete(*self.file_tree.get_children())
            for line in data.decode("utf-8").split("\n"):
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 9:
                        name = " ".join(parts[8:])
                        size = parts[4]
                        self.file_tree.insert("", tk.END, values=(name, size))
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def create_file(self):
        try:
            filename = simpledialog.askstring("Создать файл", "Введите имя файла:")
            if not filename:
                return

            content = self.content_text.get("1.0", tk.END).strip()
            if not content:
                content = " "

            self._setup_data_connection()
            self._send_command(f"STOR {filename}")
            response = self._get_response()

            self.data_socket.sendall(content.encode("utf-8"))
            self.data_socket.close()
            self._get_response()

            self.list_files()
            messagebox.showinfo("Успех", "Файл создан!")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def retrieve_file(self):
        try:
            selected = self.file_tree.selection()
            if not selected:
                messagebox.showwarning("Ошибка", "Файл не выбран")
                return

            filename = self.file_tree.item(selected[0])["values"][0]

            self._setup_data_connection()
            self._send_command(f"RETR {filename}")
            response = self._get_response()

            data = self._receive_data()
            self.data_socket.close()
            self._get_response()

            self.content_text.delete("1.0", tk.END)
            self.content_text.insert(tk.END, data.decode("utf-8"))
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def update_file(self):
        self.retrieve_file()

    def delete_file(self):
        try:
            selected = self.file_tree.selection()
            if not selected:
                messagebox.showwarning("Ошибка", "Файл не выбран")
                return

            filename = self.file_tree.item(selected[0])["values"][0]
            self._send_command(f"DELE {filename}")
            response = self._get_response()

            if response.startswith("250"):
                self.list_files()
                messagebox.showinfo("Успех", "Файл удален!")
            else:
                raise Exception("Ошибка удаления")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _setup_data_connection(self):
        self._send_command("PASV")
        response = self._get_response()

        if not response.startswith("227"):
            raise Exception("Ошибка PASV")

        parts = response.split("(")[1].split(")")[0].split(",")
        ip = ".".join(parts[:4])
        port = int(parts[4]) * 256 + int(parts[5])

        self.data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.data_socket.connect((ip, port))

    def _send_command(self, command):
        self.control_socket.sendall(f"{command}\r\n".encode("utf-8"))

    def _get_response(self):
        response = b""
        while True:
            part = self.control_socket.recv(1024)
            response += part
            if len(part) < 1024 or part[-2:] == b"\r\n":
                break
        return response.decode("utf-8").strip()

    def _receive_data(self):
        data = b""
        while True:
            part = self.data_socket.recv(4096)
            if not part:
                break
            data += part
        return data


if __name__ == "__main__":
    root = tk.Tk()
    app = FTPClientGUI(root)
    root.mainloop()