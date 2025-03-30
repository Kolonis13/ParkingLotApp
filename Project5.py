import tkinter as tk
from tkinter import messagebox
import datetime
import json

class ParkingManager:
    TOTAL_SPOTS = 20
    LONG_TERM_SPOTS = 5
    HOURLY_RATE = 2
    MONTHLY_RATE = 50
    PARKING_FILE = "parking_data.json"
    TRANSACTIONS_FILE = "transactions.json"

    def __init__(self):
        self.parking_spots = [None] * self.TOTAL_SPOTS  # Αρχικοποίηση θέσεων στάθμευσης
        self.transactions = []
        self.load_data()

    def load_data(self):
        # Φόρτωση δεδομένων από τα αρχεία
        try:
            with open(self.PARKING_FILE, "r") as f:
                data = json.load(f)
                self.parking_spots = data.get("parking_spots", [None] * self.TOTAL_SPOTS)
        except FileNotFoundError:
            self.parking_spots = [None] * self.TOTAL_SPOTS
        
        try:
            with open(self.TRANSACTIONS_FILE, "r") as f:
                self.transactions = json.load(f)
        except FileNotFoundError:
            self.transactions = []

    def save_data(self):
        # Αποθήκευση δεδομένων
        data = {
            "parking_spots": self.parking_spots
        }
        with open(self.PARKING_FILE, "w") as f:
            json.dump(data, f, indent=4)

        with open(self.TRANSACTIONS_FILE, "w") as f:
            json.dump(self.transactions, f, indent=4)

    def park_car(self, license_plate):
        if license_plate in self.parking_spots:
            return "Το αυτοκίνητο είναι ήδη παρκαρισμένο."

        # Αναζήτηση για μακροχρόνια θέση
        for i in range(self.LONG_TERM_SPOTS):
            if self.parking_spots[i] == license_plate:
                return f"Το αυτοκίνητο είναι παρκαρισμένο στη θέση {i + 1}."

        # Εύρεση κενής θέσης
        for i in range(self.LONG_TERM_SPOTS, self.TOTAL_SPOTS):
            if self.parking_spots[i] is None:
                self.parking_spots[i] = license_plate
                entry_time = datetime.datetime.now().isoformat()
                transaction = {
                    "license_plate": license_plate,
                    "entry_time": entry_time,
                    "exit_time": None,
                    "cost": None
                }
                self.transactions.append(transaction)
                self.save_data()
                return f"Το αυτοκίνητο παρκαρίστηκε στη θέση {i + 1}."
        return "Δεν υπάρχουν διαθέσιμες θέσεις στάθμευσης."

    def exit_car(self, license_plate):
        for i in range(self.LONG_TERM_SPOTS, self.TOTAL_SPOTS):
            if self.parking_spots[i] == license_plate:
                exit_time = datetime.datetime.now()

                # Εύρεση της συναλλαγής για τον υπολογισμό της χρέωσης
                for txn in self.transactions:
                    if txn['license_plate'] == license_plate and txn['exit_time'] is None:
                        entry_time = datetime.datetime.fromisoformat(txn['entry_time'])

                        # Υπολογισμός του χρόνου στάθμευσης σε ώρες
                        duration_hours = (exit_time - entry_time).seconds // 3600
                        if (exit_time - entry_time).seconds % 3600 > 0:  # Αν υπάρχει υπόλοιπος χρόνος
                            duration_hours += 1  

                        # Υπολογισμός κόστους
                        cost = duration_hours * self.HOURLY_RATE
                        txn['exit_time'] = exit_time.isoformat()
                        txn['cost'] = cost
                        self.parking_spots[i] = None  # Απελευθερώνουμε τη θέση
                        self.save_data()  # Αποθηκεύουμε τα δεδομένα

                        # Επιστρέφουμε το μήνυμα με το κόστος
                        return f"Το αυτοκίνητο εξήλθε. Χρέωση: {cost} ευρώ."
                return "Σφάλμα: Δεν βρέθηκε η είσοδος του αυτοκινήτου για υπολογισμό χρέωσης."
        return "Δεν βρέθηκε το αυτοκίνητο για έξοδο."

    # Μακροχρόνιες θέσεις
    def rent_long_term(self, license_plate):
        for i in range(self.LONG_TERM_SPOTS):
            if self.parking_spots[i] is None:
                self.parking_spots[i] = license_plate
                transaction = {
                    "license_plate": license_plate,
                    "entry_time": datetime.datetime.now().isoformat(),
                    "exit_time": None,
                    "cost": self.MONTHLY_RATE
                }
                self.transactions.append(transaction)
                self.save_data()
                return f"Το αυτοκίνητο παρκαρίστηκε στη θέση μακροχρόνιας στάθμευσης {i + 1} με χρέωση 50 ευρώ."
        return "Δεν υπάρχουν διαθέσιμες θέσεις μακροχρόνιας στάθμευσης."

    def daily_report(self):
        total_income = sum([txn['cost'] for txn in self.transactions if txn['cost'] is not None])
        return f"Σύνολο Εισπράξεων: {total_income} ευρώ."

    def list_parked_cars(self):
        return [spot for spot in self.parking_spots if spot]

    def list_free_spots(self):
        return [i + 1 for i in range(self.TOTAL_SPOTS) if self.parking_spots[i] is None]

    def best_customer(self):
        car_counts = {}
        for txn in self.transactions:
            if 'license_plate' in txn:  # Έλεγχος για την ύπαρξη του πεδίου
                car_counts[txn['license_plate']] = car_counts.get(txn['license_plate'], 0) + 1
        if not car_counts:
            return "Δεν υπάρχουν πελάτες ακόμα."
        best_customer = max(car_counts, key=car_counts.get)
        return f"Καλύτερος πελάτης: {best_customer} με {car_counts[best_customer]} σταθμεύσεις."

    def total_income(self):
        long_term_income = sum(1 for spot in self.parking_spots[:self.LONG_TERM_SPOTS] if spot) * self.MONTHLY_RATE
        hourly_income = sum(txn.get('cost', 0) for txn in self.transactions)
        return f"Συνολικές Εισπράξεις: Μακροχρόνιοι: {long_term_income} ευρώ, Ώρας: {hourly_income} ευρώ."

class ParkingApp:
    def __init__(self, root):
        self.manager = ParkingManager()
        self.root = root
        self.root.title("Parking Volos")

        # Δημιουργία κουμπιών επιλογών
        tk.Button(root, text="1. Εισερχόμενο Αυτοκίνητο", command=self.park_car_window).pack(fill='x')
        tk.Button(root, text="2. Εξερχόμενο Αυτοκίνητο", command=self.exit_car_window).pack(fill='x')
        tk.Button(root, text="3. Ενοικίαση Μακροχρόνιας Θέσης", command=self.rent_long_term_window).pack(fill='x')
        tk.Button(root, text="4. Ταμείο Ημέρας", command=self.show_daily_report).pack(fill='x')
        tk.Button(root, text="5. Προβολή Θέσεων Στάθμευσης", command=self.show_parking_spots).pack(fill='x')
        tk.Button(root, text="6. Λίστα Παρκαρισμένων Αυτοκινήτων", command=self.show_parked_cars).pack(fill='x')
        tk.Button(root, text="7. Λίστα Ελεύθερων Θέσεων", command=self.show_free_spots).pack(fill='x')
        tk.Button(root, text="8. Καλύτερος Πελάτης", command=self.show_best_customer).pack(fill='x')
        tk.Button(root, text="9. Συνολικές Εισπράξεις", command=self.show_total_income).pack(fill='x')

    def park_car_window(self):
        def park():
            license_plate = entry_license_plate.get()
            message = self.manager.park_car(license_plate)
            messagebox.showinfo("Πληροφορία", message)

        window = tk.Toplevel(self.root)
        window.title("Εισερχόμενο Αυτοκίνητο")
        tk.Label(window, text="Αρ. Κυκλοφορίας:").pack()
        entry_license_plate = tk.Entry(window)
        entry_license_plate.pack()
        tk.Button(window, text="Καταχώρηση", command=park).pack()

    def exit_car_window(self):
        def exit_car():
            license_plate = entry_license_plate.get()
            message = self.manager.exit_car(license_plate)
            messagebox.showinfo("Πληροφορία", message)

        window = tk.Toplevel(self.root)
        window.title("Εξερχόμενο Αυτοκίνητο")
        tk.Label(window, text="Αρ. Κυκλοφορίας:").pack()
        entry_license_plate = tk.Entry(window)
        entry_license_plate.pack()
        tk.Button(window, text="Καταχώρηση", command=exit_car).pack()

    def rent_long_term_window(self):
        def rent():
            license_plate = entry_license_plate.get()
            message = self.manager.rent_long_term(license_plate)
            messagebox.showinfo("Πληροφορία", message)

        window = tk.Toplevel(self.root)
        window.title("Ενοικίαση Μακροχρόνιας Θέσης")
        tk.Label(window, text="Αρ. Κυκλοφορίας:").pack()
        entry_license_plate = tk.Entry(window)
        entry_license_plate.pack()
        tk.Button(window, text="Καταχώρηση", command=rent).pack()

    def show_daily_report(self):
        report = self.manager.daily_report()
        messagebox.showinfo("Ταμείο Ημέρας", report)

    def show_parking_spots(self):
        window = tk.Toplevel(self.root)
        window.title("Προβολή Θέσεων Στάθμευσης")

        for i, spot in enumerate(self.manager.parking_spots):
            color = "green" if spot is None else ("blue" if i < self.manager.LONG_TERM_SPOTS else "red")
            text = f"Θέση {i + 1}: {spot if spot else 'Κενή'}"
            label = tk.Label(window, text=text, bg=color, width=30)
            label.pack()

    def show_parked_cars(self):
        parked_cars = self.manager.list_parked_cars()
        message = "\n".join(parked_cars) if parked_cars else "Δεν υπάρχουν παρκαρισμένα αυτοκίνητα."
        messagebox.showinfo("Παρκαρισμένα Αυτοκίνητα", message)

    def show_free_spots(self):
        free_spots = self.manager.list_free_spots()
        message = ", ".join(map(str, free_spots)) if free_spots else "Δεν υπάρχουν ελεύθερες θέσεις."
        messagebox.showinfo("Ελεύθερες Θέσεις", message)

    def show_best_customer(self):
        best_customer = self.manager.best_customer()
        messagebox.showinfo("Καλύτερος Πελάτης", best_customer)

    def show_total_income(self):
        total_income = self.manager.total_income()
        messagebox.showinfo("Συνολικές Εισπράξεις", total_income)

if __name__ == "__main__":
    root = tk.Tk()
    app = ParkingApp(root)
    root.mainloop()
