import tkinter as tk
import serial
import time

PORT = "COM4"   # change if your Uno uses a different COM port
BAUD = 115200
SERVO_STEP = 30

class MotorControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RF Servo + DC Motor Control")
        self.root.geometry("580x540")

        self.ser = serial.Serial(PORT, BAUD, timeout=0.1)
        time.sleep(2)

        self.servo_enabled = True
        self.servo_angle = 90
        self.dc_state = "STOP"

        title = tk.Label(root, text="Laptop → Uno RF → Nano Servo + DC Motor Control",
                         font=("Arial", 15, "bold"))
        title.pack(pady=8)

        self.status_label = tk.Label(root, text="Ready", font=("Arial", 11))
        self.status_label.pack(pady=5)

        servo_frame = tk.LabelFrame(root, text="Servo Control", padx=10, pady=10)
        servo_frame.pack(fill="x", padx=12, pady=8)

        self.servo_big = tk.Label(
            servo_frame, text=f"{self.servo_angle}°",
            font=("Arial", 28, "bold"), fg="navy"
        )
        self.servo_big.pack(pady=6)

        move_frame = tk.Frame(servo_frame)
        move_frame.pack(pady=6)

        tk.Button(move_frame, text="LEFT -30°", width=14, height=2,
                  command=self.servo_left, bg="lightblue").grid(row=0, column=0, padx=10)
        tk.Button(move_frame, text="RIGHT +30°", width=14, height=2,
                  command=self.servo_right, bg="lightblue").grid(row=0, column=1, padx=10)

        ctrl_frame = tk.Frame(servo_frame)
        ctrl_frame.pack(pady=8)

        tk.Button(ctrl_frame, text="SERVO ON", width=12, bg="lightgreen",
                  command=self.servo_on).grid(row=0, column=0, padx=8)
        tk.Button(ctrl_frame, text="SERVO OFF", width=12, bg="tomato",
                  command=self.servo_off).grid(row=0, column=1, padx=8)
        tk.Button(ctrl_frame, text="CENTER", width=12,
                  command=self.servo_center).grid(row=0, column=2, padx=8)

        dc_frame = tk.LabelFrame(root, text="DC Motor Control", padx=10, pady=10)
        dc_frame.pack(fill="x", padx=12, pady=8)

        self.dc_label = tk.Label(
            dc_frame, text=f"DC Motor: {self.dc_state}",
            font=("Arial", 16, "bold")
        )
        self.dc_label.pack(pady=8)

        dc_btn_frame = tk.Frame(dc_frame)
        dc_btn_frame.pack(pady=10)

        tk.Button(dc_btn_frame, text="FORWARD", width=14, height=2,
                  command=self.dc_forward, bg="lightgreen").grid(row=0, column=0, padx=10)
        tk.Button(dc_btn_frame, text="STOP", width=14, height=2,
                  command=self.dc_stop, bg="lightgray").grid(row=0, column=1, padx=10)
        tk.Button(dc_btn_frame, text="BACKWARD", width=14, height=2,
                  command=self.dc_backward, bg="lightsalmon").grid(row=0, column=2, padx=10)

        info_label = tk.Label(
            root,
            text="Servo moves in 30° steps. DC motor supports forward / stop / backward.",
            font=("Arial", 10)
        )
        info_label.pack(pady=6)

        root.protocol("WM_DELETE_WINDOW", self.close_app)

    def send_command(self, cmd):
        self.ser.write((cmd + "\n").encode("utf-8"))
        self.status_label.config(text=f"Sent: {cmd}")
        print("Sent:", cmd)
        time.sleep(0.12)

    def servo_on(self):
        self.servo_enabled = True
        self.send_command(f"SERVO,ON,{self.servo_angle}")
        self.servo_big.config(text=f"{self.servo_angle}°")

    def servo_off(self):
        self.servo_enabled = False
        self.send_command(f"SERVO,OFF,{self.servo_angle}")
        self.servo_big.config(text=f"{self.servo_angle}°")

    def servo_center(self):
        self.servo_angle = 90
        state = "ON" if self.servo_enabled else "OFF"
        self.send_command(f"SERVO,{state},{self.servo_angle}")
        self.servo_big.config(text=f"{self.servo_angle}°")

    def servo_left(self):
        self.servo_angle = max(0, self.servo_angle - SERVO_STEP)
        state = "ON" if self.servo_enabled else "OFF"
        self.send_command(f"SERVO,{state},{self.servo_angle}")
        self.servo_big.config(text=f"{self.servo_angle}°")

    def servo_right(self):
        self.servo_angle = min(180, self.servo_angle + SERVO_STEP)
        state = "ON" if self.servo_enabled else "OFF"
        self.send_command(f"SERVO,{state},{self.servo_angle}")
        self.servo_big.config(text=f"{self.servo_angle}°")

    def dc_forward(self):
        self.dc_state = "FORWARD"
        self.send_command("DC,FORWARD,0")
        self.dc_label.config(text=f"DC Motor: {self.dc_state}")

    def dc_stop(self):
        self.dc_state = "STOP"
        self.send_command("DC,STOP,0")
        self.dc_label.config(text=f"DC Motor: {self.dc_state}")

    def dc_backward(self):
        self.dc_state = "BACKWARD"
        self.send_command("DC,BACKWARD,0")
        self.dc_label.config(text=f"DC Motor: {self.dc_state}")

    def close_app(self):
        try:
            self.ser.close()
        except:
            pass
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MotorControlApp(root)
    root.mainloop()
