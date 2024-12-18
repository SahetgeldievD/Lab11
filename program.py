import tkinter as tk
from tkinter import messagebox, ttk
import matplotlib.pyplot as plt
import numpy as np

def calculate_bezier(points, t):
    n = len(points) - 1
    while len(points) > 1:
        points = [(1 - t) * np.array(points[i]) + t * np.array(points[i + 1]) for i in range(len(points) - 1)]
    return points[0]

def calculate_bezier_steps(points, t_values):
    curve_points = []
    steps = []
    for t in t_values:
        intermediate_steps = [np.array(points)]
        temp_points = points.copy()
        while len(temp_points) > 1:
            temp_points = [(1 - t) * np.array(temp_points[i]) + t * np.array(temp_points[i + 1]) for i in range(len(temp_points) - 1)]
            intermediate_steps.append(temp_points)
        curve_points.append(temp_points[0])
        steps.append(intermediate_steps)
    return np.array(curve_points), steps

def chaikin_subdivide(points, iterations):
    for _ in range(iterations):
        new_points = []
        for i in range(len(points) - 1):
            p0, p1 = np.array(points[i]), np.array(points[i + 1])
            new_points.append(0.75 * p0 + 0.25 * p1)
            new_points.append(0.25 * p0 + 0.75 * p1)
        points = new_points
    return points

def doo_sabin_subdivide(vertices, faces, iterations):
    for _ in range(iterations):
        new_vertices = []
        new_faces = []
        for face in faces:
            face_points = [vertices[v] for v in face]
            face_center = np.mean(face_points, axis=0)
            edge_points = [(np.array(face_points[i]) + np.array(face_points[(i + 1) % len(face)])) / 2 for i in range(len(face))]
            new_faces.append([len(new_vertices) + i for i in range(len(edge_points))])
            new_vertices.extend(edge_points)
            new_vertices.append(face_center)
        vertices = np.array(new_vertices)
        faces = new_faces
    return vertices, faces

def draw_curve():
    try:
        raw_points = entry_points.get()
        points = [tuple(map(float, p.split(','))) for p in raw_points.split(';')]
        t_steps = int(entry_steps.get())
        if t_steps <= 0:
            raise ValueError("Количество шагов должно быть больше нуля.")
        
        selected_curve = combo_curve.get()
        t_values = np.linspace(0, 1, t_steps)
        points = np.array(points)

        if selected_curve == "Кривая Безье":
            curve_points = [calculate_bezier(points, t) for t in t_values]
            curve_points = np.array(curve_points)
            plt.figure(figsize=(8, 6))
            plt.plot(points[:, 0], points[:, 1], 'ro-', label='Контрольные точки')
            plt.plot(curve_points[:, 0], curve_points[:, 1], 'b-', label='Кривая Безье')

        elif selected_curve == "Кубическая кривая Безье":
            curve_points, steps = calculate_bezier_steps(points, t_values)
            plt.figure(figsize=(8, 6))
            plt.plot(points[:, 0], points[:, 1], 'ro-', label='Контрольные точки')
            plt.plot(curve_points[:, 0], curve_points[:, 1], 'b-', label='Кубическая кривая Безье')
            for t_idx, t in enumerate(t_values):
                for step in steps[t_idx]:
                    step = np.array(step)
                    plt.plot(step[:, 0], step[:, 1], 'g--', alpha=0.5)

        elif selected_curve == "Кривая Чайкина":
            iterations = int(entry_steps.get())
            if iterations < 0:
                raise ValueError("Количество итераций должно быть неотрицательным.")
            curve_points = chaikin_subdivide(points, iterations)
            curve_points = np.array(curve_points)
            plt.figure(figsize=(8, 6))
            plt.plot(points[:, 0], points[:, 1], 'ro-', label='Контрольные точки')
            plt.plot(curve_points[:, 0], curve_points[:, 1], 'g-', label='Кривая Чайкина')

        plt.legend()
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.title(selected_curve)
        plt.grid(True)
        plt.show()

    except Exception as e:
        messagebox.showerror("Ошибка", str(e))

def draw_doo_sabin():
    try:
        raw_vertices = entry_vertices.get()
        raw_faces = entry_faces.get()
        vertices = [tuple(map(float, v.split(','))) for v in raw_vertices.split(';')]
        faces = [list(map(int, f.split(','))) for f in raw_faces.split(';')]
        iterations = int(entry_iterations_doo_sabin.get())
        if iterations < 0:
            raise ValueError("Количество итераций должно быть неотрицательным.")

        refined_vertices, refined_faces = doo_sabin_subdivide(vertices, faces, iterations)

        fig = plt.figure(figsize=(8, 6))
        ax = fig.add_subplot(111, projection='3d')

        for face in refined_faces:
            face_points = np.array([refined_vertices[v] for v in face])
            ax.plot_trisurf(face_points[:, 0], face_points[:, 1], face_points[:, 2], alpha=0.5)

        ax.set_title('Поверхность Ду-Сабина')
        plt.show()
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))

root = tk.Tk()
root.title("Генератор кривых и поверхностей")

frame = tk.Frame(root, padx=10, pady=10)
frame.pack()

label_points = tk.Label(frame, text="Контрольные точки:")
label_points.grid(row=0, column=0, sticky="e")
entry_points = tk.Entry(frame, width=50)
entry_points.insert(0, "0,0; 1,3; 3,5; 5,4; 6,2; 7,3; 8,0")
entry_points.grid(row=0, column=1)

label_steps = tk.Label(frame, text="Шаги/итерации:")
label_steps.grid(row=1, column=0, sticky="e")
entry_steps = tk.Entry(frame, width=20)
entry_steps.insert(0, "10")
entry_steps.grid(row=1, column=1, sticky="w")

label_curve = tk.Label(frame, text="Тип кривой:")
label_curve.grid(row=2, column=0, sticky="e")
combo_curve = ttk.Combobox(frame, values=["Кривая Безье", "Кубическая кривая Безье", "Кривая Чайкина"])
combo_curve.set("Кривая Безье")
combo_curve.grid(row=2, column=1, sticky="w")

button_draw = tk.Button(frame, text="Построить", command=draw_curve)
button_draw.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

label_vertices = tk.Label(frame, text="Вершины (x,y,z через ';'):")
label_vertices.grid(row=4, column=0, sticky="e")
entry_vertices = tk.Entry(frame, width=50)
entry_vertices.grid(row=4, column=1)

label_faces = tk.Label(frame, text="Грани (индексы через ';'):")
label_faces.grid(row=5, column=0, sticky="e")
entry_faces = tk.Entry(frame, width=50)
entry_vertices.insert(0, "0,0,0; 1,0,0; 1,1,0; 0,1,0; 0.5,0.5,1")
entry_faces.insert(0, "0,1,2,3; 0,1,4; 1,2,4; 2,3,4; 3,0,4")

entry_faces.grid(row=5, column=1)

label_iterations_doo_sabin = tk.Label(frame, text="Итерации (Ду-Сабин):")
label_iterations_doo_sabin.grid(row=6, column=0, sticky="e")
entry_iterations_doo_sabin = tk.Entry(frame, width=20)
entry_iterations_doo_sabin.insert(0, "2")
entry_iterations_doo_sabin.grid(row=6, column=1, sticky="w")

button_draw_doo_sabin = tk.Button(frame, text="Построить поверхность Ду-Сабина", command=draw_doo_sabin)
button_draw_doo_sabin.grid(row=7, column=0, columnspan=2, padx=5, pady=5)

root.mainloop()
