import tkinter as tk
import tkinter.messagebox
from tkinter.font import Font

from simplex import *


# TODO: Handle duplicated variable names.
# TODO: Handle empty variable names and coefficients.
# TODO: Center plus sign between adjacent goal function terms.
# TODO: Align vertically variable entries with goal function entries.
# TODO: Fix content of focused variable name entry being removed when using
#       keyboard shortcut.
# TODO: Restrict coefficient entry values to floating-point numbers.
# TODO: Plot the goal function and constrains if there are exactly 2 vars.
# TODO: Allow to switch between maximization and minimization.
# TODO: Show the result in a label rather than in a popup window.
# TODO: Handle constraints with >= inequality.
class Controls(tk.Frame):

    BASE_PADDING = 16
    INIT_VAR_COUNT = 2
    MAX_VAR_COUNT = 6
    MIN_VAR_COUNT = 2
    INIT_CONSTRAINT_COUNT = 2
    MAX_CONSTRAINT_COUNT = 6
    MIN_CONSTRAINT_COUNT = 2
    VAR_ENTRY_WIDTH = 4

    def __init__(self, master):
        super().__init__(master)

        self.pack(
            padx=self.BASE_PADDING,
            pady=self.BASE_PADDING,
            expand=True,
        )

        self.font = Font(self, size=16)

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
        self.var_entries = []
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
            font=self.font
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
        constraint_minus.pack(side="left", padx=(0.5*self.BASE_PADDING, 0))
        
        constraint_plus = tk.Button(constraint_button_frame, text="+")
        constraint_plus.bind('<Button-1>', self.increment_constraint_count)
        master.bind('<Control-j>', self.increment_constraint_count)
        constraint_plus.pack(side="right", padx=(0.5*self.BASE_PADDING, 0))

        solve_button = tk.Button(master, text="Solve")
        solve_button.bind('<Button-1>', self.solve)
        solve_button.pack(side="bottom", pady=self.BASE_PADDING)


    def decrement_var_count(self, _):
        if len(self.var_entries) <= self.MIN_VAR_COUNT: return

        self.var_entries[-1].grid_forget()
        self.var_entries.pop()

        self.goal_func_terms[-1].grid_forget()
        self.goal_func_terms.pop()

        self.remove_constraint_term()


    def increment_var_count(self, _=None):
        if len(self.var_entries) >= self.MAX_VAR_COUNT: return

        var_name_entry = tk.Entry(
            self,
            width=self.VAR_ENTRY_WIDTH,
            textvariable = self.var_names[len(self.var_entries)],
            font=self.font,
        )
        var_name_entry.grid(
            row=0,
            column=len(self.var_entries)+1,
            padx=(2*self.BASE_PADDING, 0),
            pady=0.5*self.BASE_PADDING,
        )
        self.var_entries.append(var_name_entry)

        term_frame = tk.Frame(self)
        if (len(self.var_entries) > 1):
            term_plus_label = tk.Label(
                term_frame, text="+", font=self.font
            ).pack(side="left")
        term_mul_entry = tk.Entry(
            term_frame,
            width=self.VAR_ENTRY_WIDTH,
            font=self.font,
        ).pack(side="left")
        term_var_label = tk.Label(
            term_frame,
            textvariable=self.var_names[len(self.var_entries)-1],
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
            row=new_id + 2,
            column=0,
        )

        constraint_terms = []
        for _ in range(len(self.var_entries)):
            self.add_constraint_term(constraint_terms, new_id)

        constraint_rhs_frame = tk.Frame(self)
        constraint_rhs_frame.grid(
            row=new_id + 2,
            column=self.MAX_VAR_COUNT+1,
            padx=(2*self.BASE_PADDING, 0),
        )
        constraint_rhs_entry = tk.Entry(
            constraint_rhs_frame,
            width=self.VAR_ENTRY_WIDTH,
            font = self.font,
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
        ).pack(side="left")
        term_var_label = tk.Label(
            term_frame,
            textvariable=self.var_names[len(constraint_terms)],
            font=self.font,
        ).pack(side="right")
        term_frame.grid(
            row=constraint_id + 2,
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
        goal_function = [float(x) for x in self.get_goal_function_coefficients()]
        constraints = [
            [float(x) for x in y] for y in self.get_constraints()
        ]
        solution = perform_simplex(to_tableau(goal_function, constraints))

        tkinter.messagebox.showinfo(
            "Result",
            detail="{}".format(solution),
        )


    def get_goal_function_coefficients(self):
        coefficients = []

        for term in self.goal_func_terms:
            for widget in term.winfo_children():
                if widget.winfo_class() == 'Entry':
                    coefficients.append(widget.get())
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
                        new_row.append(widget.get())
                        break

            for widget in rhs.winfo_children():
                if widget.winfo_class() == 'Entry':
                    new_row.append(widget.get())
                    break

            ret.append(new_row)

        return ret


if __name__ == '__main__':
    root = tk.Tk()
    root.title("Simplex")
    controls = Controls(root)
    root.mainloop()
