import tkinter as tk
import tkinter.messagebox
import tkinter.font

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (
        FigureCanvasTkAgg,
        NavigationToolbar2Tk
)

from simplex import *


# TODO: Add plot's axes labels based on the currently set var names.
# TODO: Colorize the constraints' functions with different colors.
# TODO: Add solution's space colorization.
# TODO: Add a diagram legend.
class Plot(tk.Frame):

    def __init__(self, master):
        super().__init__(master)

        self.pack(side="top", expand=True)

        fig = plt.Figure(dpi=100)
        self.ax = fig.add_subplot()

        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.draw()

        toolbar = NavigationToolbar2Tk(self.canvas, self, pack_toolbar=False)
        toolbar.update()

        self.canvas.get_tk_widget().pack(
            side=tkinter.TOP,
            fill=tkinter.BOTH,
            expand=True,
            pady=0,
        )
        toolbar.pack(side=tkinter.TOP, fill=tkinter.X)


    def plot(self, goal_function, constraints, solution):
        assert len(goal_function) == 2
        assert len(solution[0]) == 2

        self.ax.clear()

        # Plot goal function
        point = solution[0]
        if goal_function[0] != 0 and goal_function[1] != 0:
            a = -goal_function[1] / goal_function[0]
            b = point[1] - a*point[0]
            xs = [0, -b/a]
            ys = [a*x + b for x in xs]
            self.ax.plot(xs, ys)
        elif goal_function[0] == 0:
            self.ax.axhline(point[1])
        else:
            self.ax.axvline(point[0])

        # Plot constraints' lines
        constraints_data = []
        for constraint in constraints:
            if constraint[1] != 0:
                a = -constraint[0] / constraint[1]
                b = constraint[2] / constraint[1]
                constraints_data.append((a, b))
                self.ax.axline((0, b), (1, a+b), linestyle='--')
            elif constraint[0] != 0:
                b = constraint[2] / constraint[0]
                constraints_data.append((0, b))
                self.ax.axvline(b, linestyle='--')

        # Draw the solution's point
        self.ax.plot(solution[0][0], solution[0][1], marker='o', color='red')

        self.ax.set_xlim(0)
        self.ax.set_ylim(0)

        self.canvas.draw()


# TODO: Center plus sign between adjacent goal function terms.
# TODO: Fix content of focused variable name entry being removed when using
#       keyboard shortcut.
# TODO: Allow to switch between maximization and minimization.
# TODO: Handle constraints with >= inequality.
class Controls(tk.Frame):

    BASE_PADDING = 16
    INIT_VAR_COUNT = 2
    MAX_VAR_COUNT = 4
    MIN_VAR_COUNT = 2
    INIT_CONSTRAINT_COUNT = 2
    MAX_CONSTRAINT_COUNT = 4
    MIN_CONSTRAINT_COUNT = 2
    VAR_ENTRY_WIDTH = 4
    MAX_VAR_NAME_LEN = 3

    def __init__(self, master, plot):
        super().__init__(master)
        self.plot = plot

        self.pack(
            padx=self.BASE_PADDING,
            pady=self.BASE_PADDING,
            expand=True,
        )

        self.font = tkinter.font.Font(self, size=16)

        vars_label = tk.Label(self, text="Variables:", font=self.font)
        vars_label.grid(row=0, column=0)

        self.var_names = [
            tk.StringVar(master, "x{}".format(i+1))
                for i in range(self.MAX_VAR_COUNT)
        ]
        self.inequalities = [
            tk.StringVar(master, "<=") for i in range(self.MAX_VAR_COUNT)
        ]
        self.constraints = []
        self.var_entry_frames = []
        self.goal_func_terms = []
        for i in range(self.INIT_VAR_COUNT):
            self.increment_var_count()
        for i in range(self.INIT_CONSTRAINT_COUNT):
            self.increment_constraint_count()

        var_button_frame = tk.Frame(self)
        var_button_frame.grid(
            row=0,
            column=self.MAX_VAR_COUNT+1,
            padx=(2*self.BASE_PADDING, 0),
        )

        vars_minus = tk.Button(var_button_frame, text="-")
        vars_minus.bind('<Button-1>', self.decrement_var_count)
        master.bind('<Control-h>', self.decrement_var_count)
        vars_minus.pack(side="left", padx=(0.5*self.BASE_PADDING, 0))
        
        vars_plus = tk.Button(var_button_frame, text="+")
        vars_plus.bind('<Button-1>', self.increment_var_count)
        master.bind('<Control-l>', self.increment_var_count)
        vars_plus.pack(side="right", padx=(0.5*self.BASE_PADDING, 0))

        goal_func_label = tk.Label(
            self,
            text="Goal function:",
            font=self.font,
        )
        goal_func_label.grid(row=1, column=0)

        max_or_min_label = tk.Label(self, text="→ max", font=self.font)
        max_or_min_label.grid(
            row=1,
            column=self.MAX_VAR_COUNT+1,
            padx=(2*self.BASE_PADDING, 0),
        )

        constraint_button_frame = tk.Frame(self)
        constraint_button_frame.grid(
            row=2+self.MAX_CONSTRAINT_COUNT+1,
            column=0,
            padx=(2*self.BASE_PADDING, 0),
        )

        constraint_minus = tk.Button(constraint_button_frame, text="-")
        constraint_minus.bind('<Button-1>', self.decrement_constraint_count)
        master.bind('<Control-k>', self.decrement_constraint_count)
        constraint_minus.pack(
            side="left",
            padx=(0.5*self.BASE_PADDING, 0),
            pady=0.5*self.BASE_PADDING,
        )
        
        constraint_plus = tk.Button(constraint_button_frame, text="+")
        constraint_plus.bind('<Button-1>', self.increment_constraint_count)
        master.bind('<Control-j>', self.increment_constraint_count)
        constraint_plus.pack(
            side="right",
            padx=(0.5*self.BASE_PADDING, 0),
            pady=0.5*self.BASE_PADDING,
        )

        solve_frame = tk.Frame(master)
        solve_frame.pack(side="bottom", pady=self.BASE_PADDING)

        solve_button = tk.Button(solve_frame, text="Solve", font=self.font)
        solve_button.bind('<Button-1>', self.solve)
        solve_button.grid(row=0, column=0, pady=self.BASE_PADDING)

        tk.Label(
            solve_frame,
            text="Solution:",
            font=self.font
        ).grid(
            row=0, column=1,
            padx=(2*self.BASE_PADDING, 0.5*self.BASE_PADDING),
            pady=self.BASE_PADDING
        )

        self.solution = tk.StringVar(master, "")

        solution_label = tk.Label(
            solve_frame,
            textvariable = self.solution,
            font=self.font,
        ).grid(
            row=0, column=2,
            pady=self.BASE_PADDING,
        )


    def decrement_var_count(self, _):
        if len(self.var_entry_frames) <= self.MIN_VAR_COUNT: return

        self.var_entry_frames[-1].grid_forget()
        self.var_entry_frames.pop()

        self.goal_func_terms[-1].grid_forget()
        self.goal_func_terms.pop()

        self.remove_constraint_term()


    def increment_var_count(self, _=None):
        if len(self.var_entry_frames) >= self.MAX_VAR_COUNT: return

        var_name_entry_frame = tk.Frame(self)
        if len(self.var_entry_frames) >= 1:
            # For alignment purposes only.
            tk.Label(
                var_name_entry_frame, width=1, font=self.font,
            ).pack(side="left")

        var_name_entry = tk.Entry(
            var_name_entry_frame,
            width=self.VAR_ENTRY_WIDTH,
            textvariable=self.var_names[len(self.var_entry_frames)],
            font=self.font,
            validate="key",
        )
        var_name_entry['validatecommand'] = (
            var_name_entry.register(self._validate_identifier_input), "%P"
        )
        var_name_entry.pack(side="left")

        # For alignment purposes only.
        tk.Label(
            var_name_entry_frame,
            width=self.MAX_VAR_NAME_LEN,
            font=self.font,
        ).pack(side="right")

        var_name_entry_frame.grid(
            row=0,
            column=len(self.var_entry_frames)+1,
            padx=(2*self.BASE_PADDING, 0),
            pady=0.5*self.BASE_PADDING,
        )
        self.var_entry_frames.append(var_name_entry_frame)

        term_frame = tk.Frame(self)
        if (len(self.var_entry_frames) > 1):
            term_plus_label = tk.Label(
                term_frame, text="+", font=self.font,
            ).pack(side="left")
        term_mul_entry = tk.Entry(
            term_frame,
            width=self.VAR_ENTRY_WIDTH,
            font=self.font,
            validate="key",
        )
        term_mul_entry['validatecommand'] = (
            term_mul_entry.register(self._validate_coefficient_input), "%P"
        )
        term_mul_entry.pack(side="left")
        term_var_label = tk.Label(
            term_frame,
            textvariable=self.var_names[len(self.var_entry_frames)-1],
            width=self.MAX_VAR_NAME_LEN,
            font=self.font,
        ).pack(side="right")
        term_frame.grid(
            row=1,
            column=len(self.goal_func_terms)+1,
            padx=(2*self.BASE_PADDING, 0),
            pady=0.5*self.BASE_PADDING,
        )
        self.goal_func_terms.append(term_frame)

        # If this method was called from the constructor, do not add
        # constraint terms.
        if len(self.constraints) == 0: return

        for i, constraint in enumerate(self.constraints):
            _, terms, _ = constraint
            self.add_constraint_term(terms, i+1)


    def decrement_constraint_count(self, event=None):
        if len(self.constraints) <= self.MIN_CONSTRAINT_COUNT: return

        label, terms, rhs = self.constraints.pop()
        label.grid_forget()
        rhs.grid_forget()
        for term in terms:
            term.grid_forget()


    def increment_constraint_count(self, event=None):
        if len(self.constraints) >= self.MAX_CONSTRAINT_COUNT: return

        new_id = len(self.constraints) + 1

        constraint_label = tk.Label(
            self,
            text="Constraint {}:".format(new_id),
            font=self.font,
        )
        constraint_label.grid(
            row=new_id+2,
            column=0,
        )

        constraint_terms = []
        for _ in range(len(self.var_entry_frames)):
            self.add_constraint_term(constraint_terms, new_id)

        constraint_rhs_frame = tk.Frame(self)
        constraint_rhs_frame.grid(
            row=new_id+2,
            column=self.MAX_VAR_COUNT+1,
            padx=(2*self.BASE_PADDING, 0),
        )
        constraint_rhs_entry = tk.Entry(
            constraint_rhs_frame,
            width=self.VAR_ENTRY_WIDTH,
            font=self.font,
            validate="key",
        )
        constraint_rhs_entry['validatecommand'] = (
            constraint_rhs_entry.register(self._validate_coefficient_input),
            "%P",
        )
        constraint_rhs_entry.insert(0, "0")
        constraint_rhs_entry.pack(
            side="right",
            padx=(0.5*self.BASE_PADDING, 0),
        )
        constraint_rhs_inequality_menu = tk.OptionMenu(
            constraint_rhs_frame,
            self.inequalities[new_id-1],
            "<=",
        ).pack(
            side="left",
            padx=(0.5*self.BASE_PADDING, 0),
        )

        self.constraints.append(
            (constraint_label, constraint_terms, constraint_rhs_frame)
        )


    def add_constraint_term(self, constraint_terms, constraint_id):
        term_frame = tk.Frame(self)
        if len(constraint_terms) > 0:
            term_plus_label = tk.Label(
                term_frame, text="+", font=self.font
            ).pack(side="left")
        term_mul_entry = tk.Entry(
            term_frame,
            width=self.VAR_ENTRY_WIDTH,
            font=self.font,
            validate="key",
        )
        term_mul_entry['validatecommand'] = (
            term_mul_entry.register(self._validate_coefficient_input), "%P"
        )
        term_mul_entry.pack(side="left")
        term_var_label = tk.Label(
            term_frame,
            textvariable=self.var_names[len(constraint_terms)],
            width=self.MAX_VAR_NAME_LEN,
            font=self.font,
        ).pack(side="right")
        term_frame.grid(
            row=constraint_id+2,
            column=len(constraint_terms)+1,
            padx=(2*self.BASE_PADDING, 0),
            pady=0.5*self.BASE_PADDING,
        )
        constraint_terms.append(term_frame)


    def remove_constraint_term(self):
        for constraint in self.constraints:
            _, terms, _ = constraint
            terms.pop().grid_forget()


    def solve(self, event=None):
        goal_function = self.get_goal_function_coefficients()
        constraints = [
            [float(x) if x != "-" else -1.0 for x in y]
                for y in self.get_constraints()
        ]
        solution = perform_simplex(to_tableau(goal_function, constraints))

        if len(goal_function) == 2:
            self.plot(goal_function, constraints, solution)

        self.solution.set(
            "("
            + ", ".join(str(x) for x in solution[0])
            + ")"
            + " = "
            + str(solution[1])
        )


    def get_goal_function_coefficients(self):
        coefficients = []

        for term in self.goal_func_terms:
            for widget in term.winfo_children():
                if widget.winfo_class() == 'Entry':
                    coefficients.append(
                        self._coefficient_str_to_float(widget.get())
                    )
                    break

        return coefficients


    def get_constraints(self):
        ret = []

        for constraint in self.constraints:
            new_row = []
            _, term_frames, rhs = constraint

            for term_frame in term_frames:
                for widget in term_frame.winfo_children():
                    if widget.winfo_class() == 'Entry':
                        new_row.append(
                            self._coefficient_str_to_float(widget.get())
                        )
                        break

            for widget in rhs.winfo_children():
                if widget.winfo_class() == 'Entry':
                    new_row.append(
                        self._coefficient_str_to_float(widget.get())
                    )
                    break

            ret.append(new_row)

        return ret


    def _coefficient_str_to_float(self, val):
        if val == "":
            return 1.0
        elif val == "-":
            return -1.0
        else:
            return float(val)


    def _validate_identifier_input(self, input):
        if input == "":
            return True
        if input[0].isnumeric():
            return False
        if not input.isalnum():
            return False
        if len(input) > self.MAX_VAR_NAME_LEN:
            return False
        return True


    def _validate_coefficient_input(self, input):
        if input == "" or input == "-":
            return True

        try:
            float(input)
        except ValueError:
            return False

        return True


if __name__ == '__main__':
    root = tk.Tk()
    root.title("Simplex")
    plot = Plot(root)
    controls = Controls(root, plot.plot)
    root.mainloop()
