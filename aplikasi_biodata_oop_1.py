import tkinter as tk
from tkinter import messagebox
import datetime
import logging

# Setup logging
logging.basicConfig(
    filename='aplikasi_biodata.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Membuat kelas utama aplikasi yang mewarisi dari tk.Tk
class AplikasiBiodata(tk.Tk):
    # Metode __init__ adalah constructor yang akan dijalankan saat objek dibuat
    def __init__(self):
        super().__init__()
        self.title("Aplikasi Biodata Mahasiswa")
        self.geometry("600x700")
        self.resizable(True, True)

        # Database user sederhana (dalam aplikasi nyata, ini akan di database)
        self.users_db = {
            "admin": "123",
            "user1": "password1",
            "mahasiswa": "123456",
            "syaif(12345)": "123" # User baru untuk testing
        }

        # Status login
        self.current_user = None

        # Atribut untuk manajemen frame
        self.frame_aktif = None

        # --- Variabel Kontrol Tkinter ---
        self.var_nama = tk.StringVar()
        self.var_nim = tk.StringVar()
        self.var_jurusan = tk.StringVar()
        self.var_jk = tk.StringVar(value="Pria")
        self.var_setuju = tk.IntVar()

        # Aktifkan trace untuk validasi real-time
        self.var_nama.trace_add("write", self.validate_form)
        self.var_nim.trace_add("write", self.validate_form)
        self.var_jurusan.trace_add("write", self.validate_form)

        # Buat tampilan
        self._buat_tampilan_login()
        self._buat_tampilan_biodata()

        # Tampilkan frame login di awal
        self._pindah_ke(self.frame_login)

        # Log aplikasi start
        logging.info("Aplikasi dimulai")

    def _pindah_ke(self, frame_tujuan):
        """Menghapus frame yang sedang aktif dan menampilkan frame tujuan."""
        if self.frame_aktif is not None:
            self.frame_aktif.pack_forget()
        self.frame_aktif = frame_tujuan
        self.frame_aktif.pack(fill=tk.BOTH, expand=True)

    def _buat_tampilan_login(self):
        """Membuat dan menyusun widget untuk tampilan Login."""
        self.frame_login = tk.Frame(self, bg="#ffe8cc", padx=20, pady=20)
        
        # Frame tengah untuk form login
        form_login = tk.Frame(self.frame_login, bg="#ffffff", padx=40, pady=40, relief=tk.RAISED, bd=1)
        form_login.place(relx=0.5, rely=0.4, anchor=tk.CENTER)

        tk.Label(form_login, text="LOGIN", font=("Segoe UI", 20, "bold"), bg="#ffffff", fg="#333333").pack(pady=(0, 25))
        
        frame_user = tk.Frame(form_login, bg="#ffffff")
        frame_user.pack(fill="x", pady=(0, 15))
        tk.Label(frame_user, text="Username", bg="#ffffff", font=("Segoe UI", 11), fg="#555555").pack(anchor="w", pady=(0, 5))
        self.entry_username = tk.Entry(frame_user, font=("Segoe UI", 12), width=28, relief=tk.SOLID, bd=1)
        self.entry_username.pack(fill="x", ipady=4)
        
        frame_pass_container = tk.Frame(form_login, bg="#ffffff")
        frame_pass_container.pack(fill="x", pady=(0, 5))
        tk.Label(frame_pass_container, text="Password", bg="#ffffff", font=("Segoe UI", 11), fg="#555555").pack(anchor="w", pady=(0, 5))
        
        frame_pass = tk.Frame(frame_pass_container, bg="#ffffff", relief=tk.SOLID, bd=1)
        frame_pass.pack(fill="x")
        self.entry_password = tk.Entry(frame_pass, show="*", font=("Segoe UI", 12), relief=tk.FLAT, bd=0)
        self.entry_password.pack(side=tk.LEFT, expand=True, fill="x", padx=(5, 0), ipady=4)
        self.btn_show_pass = tk.Button(frame_pass, text="👁", command=self._toggle_password, bg="#ffffff", relief=tk.FLAT, bd=0, cursor="hand2")
        self.btn_show_pass.pack(side=tk.RIGHT, padx=5)

        self.var_remember = tk.IntVar()
        self.chk_remember = tk.Checkbutton(form_login, text="Remember Me", variable=self.var_remember, bg="#ffffff", font=("Segoe UI", 10), fg="#555555")
        self.chk_remember.pack(anchor="w", pady=(5, 20))
        
        btn_login = tk.Button(form_login, text="Login", font=("Segoe UI", 12, "bold"), command=self._coba_login, bg="#0d6efd", fg="white", relief=tk.FLAT, cursor="hand2")
        btn_login.pack(fill="x", ipady=5)
        
        self._load_remembered_username()

    def _toggle_password(self):
        """Toggle show/hide password."""
        if self.entry_password.cget('show') == '*':
            self.entry_password.config(show='')
            self.btn_show_pass.config(text='🔒')
        else:
            self.entry_password.config(show='*')
            self.btn_show_pass.config(text='👁')

    def _load_remembered_username(self):
        """Memuat username dari file jika Remember Me diaktifkan sebelumnya."""
        import os
        if os.path.exists("remember_me.txt"):
            with open("remember_me.txt", "r") as f:
                username = f.read().strip()
                if username:
                    self.entry_username.insert(0, username)
                    self.var_remember.set(1)

    def _coba_login(self):
        """Method untuk memproses attempt login dengan logging"""
        username = self.entry_username.get().strip()
        password = self.entry_password.get()

        # Log attempt login
        logging.info(f"Login attempt for username: {username}")

        # Validasi input kosong
        if not username or not password:
            logging.warning(f"Empty credentials attempt for username: {username}")
            messagebox.showwarning("Login Gagal", "Username dan Password tidak boleh kosong.")
            self.entry_username.focus_set()
            return

        # Validasi panjang minimum
        if len(username) < 3:
            logging.warning(f"Username too short: {username}")
            messagebox.showwarning("Login Gagal", "Username minimal 3 karakter.")
            self.entry_username.focus_set()
            return

        # Cek kredensial di database
        if username in self.users_db and self.users_db[username] == password:
            self.current_user = username
            
            # Handle remember me
            import os
            if hasattr(self, 'var_remember'):
                if self.var_remember.get() == 1:
                    with open("remember_me.txt", "w") as f:
                        f.write(username)
                else:
                    if os.path.exists("remember_me.txt"):
                        os.remove("remember_me.txt")
                        
            logging.info(f"Successful login for user: {username}")
            messagebox.showinfo("Login Berhasil", f"Selamat Datang, {username}!")
            self._reset_form_biodata()
            self._update_title_with_user()
            self._pindah_ke(self.frame_biodata)
            
            if not (hasattr(self, 'var_remember') and self.var_remember.get() == 1):
                self.entry_username.delete(0, tk.END)
            self.entry_password.delete(0, tk.END)
        else:
            logging.warning(f"Failed login attempt for username: {username}")
            messagebox.showerror("Login Gagal", "Username atau Password salah.")
            self.entry_password.delete(0, tk.END)
            self.entry_username.focus_set()

    def _logout(self):
        """Method untuk logout dengan logging"""
        if messagebox.askyesno("Logout", f"Apakah {self.current_user} yakin ingin logout?"):
            logging.info(f"User logout: {self.current_user}")
            # Reset status user
            self.current_user = None
            # Update title
            self._update_title_with_user()
            # Bersihkan field login
            self.entry_username.delete(0, tk.END)
            self.entry_password.delete(0, tk.END)
            
            # Reload remember me jika ada
            if hasattr(self, '_load_remembered_username'):
                self._load_remembered_username()
                
            # Reset form biodata
            self._reset_form_biodata()
            # Kembali ke halaman login
            self._pindah_ke(self.frame_login)
            # Focus ke username field
            self.entry_username.focus_set()

    def _buat_tampilan_biodata(self):
        """Membuat dan menyusun widget untuk tampilan utama Biodata."""
        self.frame_biodata = tk.Frame(self, bg="orange")
        
        self.main_frame = tk.Frame(master=self.frame_biodata, padx=30, pady=30, bg="antique white", relief=tk.RAISED, bd=1)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.main_frame.columnconfigure(1, weight=1)

        # Header dengan tombol logout
        header_frame = tk.Frame(master=self.main_frame, bg="antique white")
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        header_frame.columnconfigure(0, weight=1)

        tk.Label(
            master=header_frame, 
            text="FORM BIODATA MAHASISWA", 
            font=("Segoe UI", 18, "bold"), bg="antique white", fg="#333333"
        ).grid(row=0, column=0, sticky="w")

        btn_logout = tk.Button(
            master=header_frame,
            text="Logout",
            font=("Segoe UI", 10, "bold"),
            bg="#dc3545", fg="white",
            relief=tk.FLAT,
            command=self._logout, cursor="hand2", padx=15, pady=5
        )
        btn_logout.grid(row=0, column=1, sticky="e")

        # Frame khusus untuk input dengan border
        self.frame_input = tk.Frame(
            master=self.main_frame, 
            bg="#fff4e6", relief=tk.GROOVE, bd=2
        )
        self.frame_input.grid(row=1, column=0, columnspan=2, pady=10, sticky="ew")
        self.frame_input.columnconfigure(1, weight=1)

        label_font = ("Segoe UI", 11)
        input_font = ("Segoe UI", 11)

        # Input Nama
        self.label_nama = tk.Label(master=self.frame_input, text="Nama Lengkap", font=label_font, bg="#fff4e6", fg="#555555")
        self.label_nama.grid(row=0, column=0, sticky="W", pady=10, padx=(0, 20))
        self.entry_nama = tk.Entry(master=self.frame_input, font=input_font, textvariable=self.var_nama, relief=tk.SOLID, bd=1)
        self.entry_nama.grid(row=0, column=1, pady=10, sticky="ew", ipady=4)

        # Input NIM
        self.label_nim = tk.Label(master=self.frame_input, text="NIM", font=label_font, bg="#fff4e6", fg="#555555")
        self.label_nim.grid(row=1, column=0, sticky="W", pady=10, padx=(0, 20))
        self.entry_nim = tk.Entry(master=self.frame_input, font=input_font, textvariable=self.var_nim, relief=tk.SOLID, bd=1)
        self.entry_nim.grid(row=1, column=1, pady=10, sticky="ew", ipady=4)

        # Input Jurusan
        self.label_jurusan = tk.Label(master=self.frame_input, text="Jurusan", font=label_font, bg="#fff4e6", fg="#555555")
        self.label_jurusan.grid(row=2, column=0, sticky="W", pady=10, padx=(0, 20))
        self.entry_jurusan = tk.Entry(master=self.frame_input, font=input_font, textvariable=self.var_jurusan, relief=tk.SOLID, bd=1)
        self.entry_jurusan.grid(row=2, column=1, pady=10, sticky="ew", ipady=4)

        # Input alamat dengan Text widget
        self.label_alamat = tk.Label(master=self.frame_input, text="Alamat", font=label_font, bg="#fff4e6", fg="#555555")
        self.label_alamat.grid(row=3, column=0, sticky="NW", pady=10, padx=(0, 20))

        self.frame_alamat = tk.Frame(master=self.frame_input, relief=tk.SOLID, borderwidth=1, bg="#ffffff")
        self.scrollbar_alamat = tk.Scrollbar(master=self.frame_alamat)
        self.scrollbar_alamat.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_alamat = tk.Text(master=self.frame_alamat, height=4, font=input_font, relief=tk.FLAT)
        self.text_alamat.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar_alamat.config(command=self.text_alamat.yview)
        self.text_alamat.config(yscrollcommand=self.scrollbar_alamat.set)
        self.frame_alamat.grid(row=3, column=1, pady=10, sticky="ew")

        # Jenis kelamin
        self.label_jk = tk.Label(master=self.frame_input, text="Jenis Kelamin", font=label_font, bg="#fff4e6", fg="#555555")
        self.label_jk.grid(row=4, column=0, sticky="W", pady=10, padx=(0, 20))

        self.frame_jk = tk.Frame(master=self.frame_input, bg="#fff4e6")
        self.frame_jk.grid(row=4, column=1, sticky="W", pady=10)

        self.radio_pria = tk.Radiobutton(master=self.frame_jk, text="Pria", variable=self.var_jk, value="Pria", bg="#fff4e6", font=input_font)
        self.radio_pria.pack(side=tk.LEFT, padx=(0, 20))
        self.radio_wanita = tk.Radiobutton(master=self.frame_jk, text="Wanita", variable=self.var_jk, value="Wanita", bg="#fff4e6", font=input_font)
        self.radio_wanita.pack(side=tk.LEFT)

        # Checkbox persetujuan
        self.check_setuju = tk.Checkbutton(
            master=self.frame_input,
            text="Saya menyetujui pengumpulan data ini.",
            variable=self.var_setuju,
            font=("Segoe UI", 10),
            bg="#fff4e6", fg="#555555",
            command=self.validate_form
        )
        self.check_setuju.grid(row=5, column=0, columnspan=2, pady=(15, 5), sticky="W")

        # Frame untuk tombol
        frame_tombol = tk.Frame(master=self.main_frame, bg="antique white")
        frame_tombol.grid(row=6, column=0, columnspan=2, pady=25, sticky="EW")
        frame_tombol.columnconfigure(0, weight=1)
        frame_tombol.columnconfigure(1, weight=1)

        # Tombol submit
        self.btn_submit = tk.Button(
            master=frame_tombol, 
            text="Submit Biodata", 
            font=("Segoe UI", 12, "bold"),
            command=self.submit_data,
            state=tk.DISABLED,
            bg="#d6d6d6", fg="white", relief=tk.FLAT, cursor="hand2"
        )
        self.btn_submit.grid(row=0, column=0, sticky="EW", padx=(0, 10), ipady=5)

        # Tombol reset
        self.btn_reset = tk.Button(
            master=frame_tombol, 
            text="Reset Form", 
            font=("Segoe UI", 12, "bold"),
            command=self._reset_form_biodata,
            bg="#6c757d", fg="white", relief=tk.FLAT, cursor="hand2"
        )
        self.btn_reset.grid(row=0, column=1, sticky="EW", padx=(10, 0), ipady=5)

        self.btn_submit.bind("<Enter>", self.on_enter)
        self.btn_submit.bind("<Leave>", self.on_leave)
        self.btn_reset.bind("<Enter>", lambda e: self.btn_reset.config(bg="#5a6268"))
        self.btn_reset.bind("<Leave>", lambda e: self.btn_reset.config(bg="#6c757d"))
        btn_logout.bind("<Enter>", lambda e: btn_logout.config(bg="#c82333"))
        btn_logout.bind("<Leave>", lambda e: btn_logout.config(bg="#dc3545"))
        self.entry_nama.bind("<Return>", self.submit_shortcut)
        self.entry_nim.bind("<Return>", self.submit_shortcut)
        self.entry_jurusan.bind("<Return>", self.submit_shortcut)
        self.text_alamat.bind("<Return>", self.submit_shortcut)

        # Label hasil
        self.label_hasil = tk.Label(master=self.main_frame, text="", font=("Segoe UI", 11, "italic"), justify=tk.LEFT, bg="antique white", fg="#28a745")
        self.label_hasil.grid(row=7, column=0, columnspan=2, sticky="W")

        # Membuat menu
        self._buat_menu()

    def submit_data(self):
        """Submit data biodata dengan validasi lengkap"""
        try:
            # Cek checkbox
            if self.var_setuju.get() == 0:
                messagebox.showwarning("Peringatan", "Anda harus menyetujui pengumpulan data!")
                return

            # Ambil data dari form
            nama = self.entry_nama.get().strip()
            nim = self.entry_nim.get().strip()
            jurusan = self.entry_jurusan.get().strip()
            alamat = self.text_alamat.get("1.0", tk.END).strip()
            jenis_kelamin = self.var_jk.get()

            # Validasi field kosong
            if not nama or not nim or not jurusan:
                messagebox.showwarning("Input Kosong", "Nama, NIM, dan Jurusan harus diisi!")
                return

            # Validasi format NIM (harus angka dan minimal 8 digit)
            if not nim.isdigit() or len(nim) < 8:
                messagebox.showwarning("Format NIM Salah", "NIM harus berupa angka minimal 8 digit!")
                self.entry_nim.focus_set()
                return

            # Validasi nama (tidak boleh hanya angka)
            if nama.isdigit():
                messagebox.showwarning("Format Nama Salah", "Nama tidak boleh hanya berupa angka!")
                self.entry_nama.focus_set()
                return

            # Tampilkan hasil
            hasil = f"Nama: {nama}\nNIM: {nim}\nJurusan: {jurusan}\nAlamat: {alamat}\nJenis Kelamin: {jenis_kelamin}"
            messagebox.showinfo("Data Tersimpan", hasil)

            # Tampilkan hasil di label dengan info user
            hasil_lengkap = f"BIODATA TERSIMPAN:\nDiinput oleh: {self.current_user}\n\n{hasil}"
            self.label_hasil.config(text=hasil_lengkap)

            # Log successful data submission
            logging.info(f"Data submitted by user: {self.current_user} - NIM: {nim}")

        except Exception as e:
            logging.error(f"Error in submit_data by {self.current_user}: {str(e)}")
            messagebox.showerror("Error", f"Terjadi kesalahan saat memproses data:\n{str(e)}")

    def validate_form(self, *args):
        nama_valid = self.var_nama.get().strip() != ""
        nim_valid = self.var_nim.get().strip() != ""
        jurusan_valid = self.var_jurusan.get().strip() != ""
        setuju_valid = self.var_setuju.get() == 1

        if nama_valid and nim_valid and jurusan_valid and setuju_valid:
            self.btn_submit.config(state=tk.NORMAL, bg="#0d6efd")
        else:
            self.btn_submit.config(state=tk.DISABLED, bg="#d6d6d6")

    def on_enter(self, event):
        if self.btn_submit['state'] == tk.NORMAL:
            self.btn_submit.config(bg="#0b5ed7")

    def on_leave(self, event):
        if self.btn_submit['state'] == tk.NORMAL:
            self.btn_submit.config(bg="#0d6efd")

    def submit_shortcut(self, event=None):
        if self.btn_submit['state'] == tk.NORMAL:
            self.submit_data()

    def _reset_form_biodata(self):
        """Reset semua field di form biodata"""
        self.var_nama.set("")
        self.var_nim.set("")
        self.var_jurusan.set("")
        self.text_alamat.delete("1.0", tk.END)
        self.var_jk.set("Pria")
        self.var_setuju.set(0)
        self.label_hasil.config(text="")

    def _buat_menu(self):
        """Membuat menu bar untuk aplikasi"""
        menu_bar = tk.Menu(master=self)
        self.config(menu=menu_bar)

        file_menu = tk.Menu(master=menu_bar, tearoff=0)
        file_menu.add_command(label="Logout", command=self._logout)
        file_menu.add_separator()
        file_menu.add_command(label="Keluar", command=self.keluar_aplikasi)

        menu_bar.add_cascade(label="File", menu=file_menu)

    def _hapus_menu(self):
        """Menghapus menu bar dari window."""
        empty_menu = tk.Menu(self)
        self.config(menu=empty_menu)

    def _update_title_with_user(self):
        """Update judul window dengan nama user yang login"""
        if self.current_user:
            self.title(f"Aplikasi Biodata Mahasiswa - User: {self.current_user}")
        else:
            self.title("Aplikasi Biodata Mahasiswa")

    #menyimpan hasil file
    def _buat_menu(self):
        """Membuat menu bar untuk aplikasi"""
        menu_bar = tk.Menu(master=self)
        self.config(menu=menu_bar)

        file_menu = tk.Menu(master=menu_bar, tearoff=0)
        file_menu.add_command(label="Simpan Hasil", command=self.simpan_hasil)
        file_menu.add_separator()
        file_menu.add_command(label="Logout", command=self._logout)
        file_menu.add_separator()
        file_menu.add_command(label="Keluar", command=self.keluar_aplikasi)

        menu_bar.add_cascade(label="File", menu=file_menu)

    def simpan_hasil(self):
        """Simpan hasil biodata ke file dengan error handling"""
        try:
            hasil_tersimpan = self.label_hasil.cget("text")

            if not hasil_tersimpan or "BIODATA TERSIMPAN" not in hasil_tersimpan:
                messagebox.showwarning("Peringatan", "Tidak ada data untuk disimpan. Mohon submit terlebih dahulu.")
                return

            # Buat nama file dengan timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"biodata_{self.current_user}_{timestamp}.txt"

            with open(filename, "w", encoding="utf-8") as file:
                file.write(f"Data disimpan oleh: {self.current_user}\n")
                file.write(f"Waktu penyimpanan: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                file.write("-" * 50 + "\n")
                file.write(hasil_tersimpan)

            messagebox.showinfo("Info", f"Data berhasil disimpan ke file '{filename}'.")

        except PermissionError:
            messagebox.showerror("Error", "Tidak memiliki izin untuk menyimpan file di lokasi ini.")
        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan saat menyimpan file:\n{str(e)}")

    def keluar_aplikasi(self):
        """Keluar dari aplikasi dengan konfirmasi"""
        if messagebox.askokcancel("Keluar", "Apakah Anda yakin ingin keluar dari aplikasi?"):
            logging.info(f"Application closed by user: {self.current_user}")
            self.destroy()

# Blok berikut hanya akan dieksekusi jika file ini dijalankan secara langsung
if __name__ == "__main__":
    app = AplikasiBiodata()
    app.mainloop()
    app.mainloop()