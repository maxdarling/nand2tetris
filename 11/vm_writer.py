from jack_constants import VMArithmetic, VMSegment

class VMWriter():
    """Helper class for writing VM instructions during compilation."""

    def __init__(self, outfile: str):
        self.f = open(outfile, 'w')

    def close(self):
        self.f.close()

    def write_push(self, segment: VMSegment, index: int):
        self.f.write(f"push {segment} {index}\n")

    def write_pop(self, segment: VMSegment, index: int):
        self.f.write(f"pop {segment} {index}\n")

    def write_arithmetic(self, operator: VMArithmetic):
        self.f.write(f"{operator}\n")

    def write_label(self, label: str):
        self.f.write(f"label {label}\n")

    def write_goto(self, label: str):
        self.f.write(f"goto {label}\n")

    def write_if(self, label: str):
        self.f.write(f"if-goto {label}\n")

    def write_call(self, name: str, n_args: int):
        self.f.write(f"call {name} {n_args}\n")

    def write_function(self, name: str, n_vars: int):
        self.f.write(f"function {name} {n_vars}\n")

    def write_return(self):
        self.f.write("return\n")
