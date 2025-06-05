import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QComboBox, QSpinBox,
    QDateEdit, QPushButton, QTextEdit, QVBoxLayout, QFormLayout,
    QHBoxLayout, QTabWidget, QListWidget, QListWidgetItem, QDialog,
    QDialogButtonBox, QMessageBox
)
from PyQt6.QtCore import QDate, Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QBrush

class ApprovalDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Persetujuan Peminjaman")
        self.setGeometry(200, 200, 400, 200)
        
        layout = QVBoxLayout()
        
        self.message = QLabel("Apakah Anda ingin menyetujui peminjaman ini?")
        layout.addWidget(self.message)
        
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Yes | QDialogButtonBox.StandardButton.No
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
        self.setLayout(layout)

class HistoryItemWidget(QWidget):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Status indicator
        status_color = "#2ecc71" if data["status"] == "Disetujui" else "#e74c3c"
        status_text = QLabel(f"Status: <b style='color:{status_color};'>{data['status']}</b>")
        status_text.setStyleSheet("font-size: 12px;")
        
        # Item details
        details = QLabel(
            f"<b>{data['nama']}</b> - {data['barang']} ({data['jumlah']} buah)<br>"
            f"📅 Pengajuan: {data['timestamp']}<br>"
            f"📥 Pinjam: {data['tgl_pinjam']} | 📤 Kembali: {data['tgl_kembali']}"
        )
        details.setStyleSheet("font-size: 13px;")
        
        layout.addWidget(status_text)
        layout.addWidget(details)
        self.setLayout(layout)

class PinjamRTApp(QWidget):
    history_updated = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PinjamRT – Aplikasi Peminjaman Barang RT/RW")
        self.setGeometry(100, 100, 700, 700)
        self.loan_history = []
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Judul Aplikasi
        judul_label = QLabel("📦 PinjamRT – Aplikasi Peminjaman Barang RT/RW")
        judul_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        judul_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        judul_label.setStyleSheet("color: #000000; padding: 10px;")
        main_layout.addWidget(judul_label)

        # Garis pemisah
        separator = QLabel()
        separator.setFrameShape(QLabel.Shape.HLine)
        separator.setStyleSheet("background-color: #cccccc;")
        main_layout.addWidget(separator)

        # Create tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Tab 1: Form Peminjaman
        form_tab = QWidget()
        form_layout = QVBoxLayout(form_tab)
        form_layout.setSpacing(15)
        
        # Form input
        input_form = QFormLayout()
        input_form.setSpacing(15)
        input_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        self.nama_input = QLineEdit()
        self.nama_input.setPlaceholderText("Masukkan nama lengkap")
        
        self.barang_combo = QComboBox()
        self.barang_combo.addItems(["Tenda", "Kursi Plastik", "Sound System", "Peralatan Kerja Bakti", 
                                  "Meja Lipat", "Dispenser", "Tikar", "Panggung Portable"])
        
        self.jumlah_spin = QSpinBox()
        self.jumlah_spin.setRange(1, 50)
        self.jumlah_spin.setValue(1)

        self.tgl_pinjam = QDateEdit()
        self.tgl_pinjam.setDate(QDate.currentDate())
        self.tgl_pinjam.setCalendarPopup(True)
        
        self.tgl_pengembalian = QDateEdit()
        self.tgl_pengembalian.setDate(QDate.currentDate().addDays(1))
        self.tgl_pengembalian.setCalendarPopup(True)

        # Styling input
        input_style = """
            background-color: #ffffff;
            color: #000000;
            padding: 8px;
            border: 1px solid #cccccc;
            border-radius: 4px;
            font-size: 14px;
        """
        self.nama_input.setStyleSheet(input_style)
        self.barang_combo.setStyleSheet(input_style)
        self.jumlah_spin.setStyleSheet(input_style)
        self.tgl_pinjam.setStyleSheet(input_style)
        self.tgl_pengembalian.setStyleSheet(input_style)

        # Add to form
        input_form.addRow("Nama Peminjam:", self.nama_input)
        input_form.addRow("Jenis Barang:", self.barang_combo)
        input_form.addRow("Jumlah Barang:", self.jumlah_spin)
        input_form.addRow("Tanggal Peminjaman:", self.tgl_pinjam)
        input_form.addRow("Tanggal Pengembalian:", self.tgl_pengembalian)
        
        form_layout.addLayout(input_form)
        
        # Tombol Ajukan
        self.ajukan_btn = QPushButton("📬 Ajukan Peminjaman")
        self.ajukan_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 12px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.ajukan_btn.clicked.connect(self.proses_peminjaman)
        form_layout.addWidget(self.ajukan_btn)
        
        # Area Output
        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        self.output_area.setStyleSheet("""
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #cccccc;
            border-radius: 5px;
            padding: 10px;
            font-family: 'Arial';
            font-size: 13px;
        """)
        form_layout.addWidget(QLabel("📋 Detail Pengajuan Terbaru:"))
        form_layout.addWidget(self.output_area)
        
        self.tab_widget.addTab(form_tab, "Form Peminjaman")

        # Tab 2: Persetujuan
        approval_tab = QWidget()
        approval_layout = QVBoxLayout(approval_tab)
        
        # Pending approvals list
        self.pending_list = QListWidget()
        self.pending_list.setStyleSheet("""
            QListWidget {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 5px;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #eeeeee;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
            }
        """)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.approve_btn = QPushButton("✅ Setujui")
        self.approve_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        self.approve_btn.setEnabled(False)
        self.approve_btn.clicked.connect(self.approve_loan)
        
        self.reject_btn = QPushButton("❌ Tolak")
        self.reject_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.reject_btn.setEnabled(False)
        self.reject_btn.clicked.connect(self.reject_loan)
        
        btn_layout.addWidget(self.approve_btn)
        btn_layout.addWidget(self.reject_btn)
        
        approval_layout.addWidget(QLabel("📋 Daftar Pengajuan Menunggu Persetujuan:"))
        approval_layout.addWidget(self.pending_list)
        approval_layout.addLayout(btn_layout)
        
        self.pending_list.itemSelectionChanged.connect(self.update_approval_buttons)
        self.tab_widget.addTab(approval_tab, "Persetujuan")

        # Tab 3: Riwayat Peminjaman
        history_tab = QWidget()
        history_layout = QVBoxLayout(history_tab)
        
        self.history_list = QListWidget()
        self.history_list.setStyleSheet("""
            QListWidget {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 5px;
            }
        """)
        self.history_list.setAlternatingRowColors(True)
        
        history_layout.addWidget(QLabel("📜 Riwayat Peminjaman:"))
        history_layout.addWidget(self.history_list)
        
        # Clear history button
        clear_btn = QPushButton("🧹 Bersihkan Riwayat")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        clear_btn.clicked.connect(self.clear_history)
        history_layout.addWidget(clear_btn)
        
        self.tab_widget.addTab(history_tab, "Riwayat")
        
        # Footer
        nama_label = QLabel("👨‍💻 Dibuat oleh: Kelompok 2 – Raafi', Misscay, Nisfu, Bima")
        nama_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        nama_label.setStyleSheet("color: #666666; font-size: 11px; margin-top: 15px;")
        main_layout.addWidget(nama_label)

        self.setLayout(main_layout)
        self.history_updated.connect(self.update_history_display)

    def proses_peminjaman(self):
        nama = self.nama_input.text().strip()
        barang = self.barang_combo.currentText()
        jumlah = self.jumlah_spin.value()
        tgl_pinjam = self.tgl_pinjam.date().toString("dd/MM/yyyy")
        tgl_kembali = self.tgl_pengembalian.date().toString("dd/MM/yyyy")
        
        # Validasi input
        if not nama:
            QMessageBox.warning(self, "Input Tidak Valid", "Nama peminjam tidak boleh kosong!")
            return
            
        if self.tgl_pengembalian.date() < self.tgl_pinjam.date():
            QMessageBox.warning(self, "Input Tidak Valid", 
                                "Tanggal pengembalian tidak boleh sebelum tanggal peminjaman!")
            return
        
        # Create loan record
        loan_record = {
            "id": len(self.loan_history) + 1,
            "nama": nama,
            "barang": barang,
            "jumlah": jumlah,
            "tgl_pinjam": tgl_pinjam,
            "tgl_kembali": tgl_kembali,
            "status": "Menunggu",
            "timestamp": QDate.currentDate().toString("dd/MM/yyyy")
        }
        
        # Add to pending list
        self.loan_history.append(loan_record)
        self.add_to_pending_list(loan_record)
        
        # Format output
        ringkasan = (
            f"📝 <b>Data Peminjaman</b>\n"
            f"• Nama            : {nama}\n"
            f"• Barang          : {barang}\n"
            f"• Jumlah          : {jumlah}\n"
            f"• Tanggal Pinjam  : {tgl_pinjam}\n"
            f"• Tanggal Kembali : {tgl_kembali}\n"
            f"• Status          : <span style='color:#f39c12;'>Menunggu persetujuan RT</span>\n"
            f"-------------------------------\n"
        )
        self.output_area.setHtml(ringkasan)
        
        # Reset form
        self.nama_input.clear()
        self.jumlah_spin.setValue(1)
        self.tgl_pengembalian.setDate(QDate.currentDate().addDays(1))
        
        QMessageBox.information(self, "Berhasil", "Pengajuan peminjaman berhasil dikirim!")

    def add_to_pending_list(self, loan):
        item = QListWidgetItem(self.pending_list)
        item.setData(Qt.ItemDataRole.UserRole, loan)
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 5, 10, 5)
        
        details = QLabel(
            f"<b>{loan['nama']}</b> - {loan['barang']} ({loan['jumlah']} buah)<br>"
            f"Pinjam: {loan['tgl_pinjam']} | Kembali: {loan['tgl_kembali']}"
        )
        details.setStyleSheet("font-size: 13px;")
        
        layout.addWidget(details)
        widget.setLayout(layout)
        
        item.setSizeHint(widget.sizeHint())
        self.pending_list.addItem(item)
        self.pending_list.setItemWidget(item, widget)

    def update_approval_buttons(self):
        selected = self.pending_list.currentItem() is not None
        self.approve_btn.setEnabled(selected)
        self.reject_btn.setEnabled(selected)

    def approve_loan(self):
        self.process_approval("Disetujui")

    def reject_loan(self):
        self.process_approval("Ditolak")

    def process_approval(self, status):
        selected_item = self.pending_list.currentItem()
        if not selected_item:
            return
            
        loan = selected_item.data(Qt.ItemDataRole.UserRole)
        
        # Show confirmation dialog
        dialog = ApprovalDialog(self)
        result = dialog.exec()
        
        if result == QDialog.DialogCode.Accepted:
            # Update status
            loan["status"] = status
            
            # Remove from pending list
            row = self.pending_list.row(selected_item)
            self.pending_list.takeItem(row)
            
            # Update history
            self.history_updated.emit()
            
            # Show confirmation
            status_color = "#2ecc71" if status == "Disetujui" else "#e74c3c"
            QMessageBox.information(
                self, "Berhasil", 
                f"<span style='color:{status_color}; font-weight:bold;'>Peminjaman {status.lower()}</span>"
            )

    def update_history_display(self):
        self.history_list.clear()
        
        # Sort history by ID (newest first)
        sorted_history = sorted(
            [loan for loan in self.loan_history if loan["status"] != "Menunggu"],
            key=lambda x: x["id"],
            reverse=True
        )
        
        for loan in sorted_history:
            item = QListWidgetItem(self.history_list)
            item_widget = HistoryItemWidget(loan)
            item.setSizeHint(item_widget.sizeHint())
            self.history_list.addItem(item)
            self.history_list.setItemWidget(item, item_widget)
            
            # Set background color based on status
            if loan["status"] == "Disetujui":
                item.setBackground(QBrush(QColor("#e8f5e9")))  # Light green
            else:
                item.setBackground(QBrush(QColor("#ffebee")))  # Light red

    def clear_history(self):
        # Keep only pending loans
        self.loan_history = [loan for loan in self.loan_history if loan["status"] == "Menunggu"]
        
        # Refresh displays
        self.pending_list.clear()
        for loan in self.loan_history:
            self.add_to_pending_list(loan)
        
        self.history_list.clear()
        QMessageBox.information(self, "Berhasil", "Riwayat peminjaman yang sudah selesai telah dibersihkan!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Styling global
    app.setStyleSheet("""
    QWidget {
        color: #000000;
        background-color: #ffffff;
        font-family: 'Segoe UI', Arial;
    }
    QLabel {
        font-size: 13px;
    }
    QFormLayout > QLabel {
        font-weight: bold;
    }
    QLineEdit, QComboBox, QSpinBox, QDateEdit, QTextEdit {
        background-color: #ffffff;
        color: #000000;
        border: 1px solid #cccccc;
        border-radius: 4px;
        padding: 6px;
        font-size: 13px;
    }
    QPushButton {
        background-color: #ffffff;
        color: #000000;
        border: 1px solid #cccccc;
        border-radius: 5px;
        font-weight: bold;
    }
    QListWidget {
        background-color: #ffffff;
        color: #000000;
    }
    QTabWidget::pane {
        border: 1px solid #cccccc;
        border-radius: 5px;
        padding: 5px;
        background-color: #ffffff;
    }
    QTabBar::tab {
        border: 1px solid #cccccc;
        border-bottom: none;
        border-top-left-radius: 5px;
        border-top-right-radius: 5px;
        padding: 8px 15px;
        margin-right: 2px;
        background-color: #ffffff;
        color: #000000;
    }
    QTabBar::tab:selected {
        border-bottom: 2px solid #000000;
        font-weight: bold;
        background-color: #ffffff;
    }
""")

    window = PinjamRTApp()
    window.show()
    sys.exit(app.exec())