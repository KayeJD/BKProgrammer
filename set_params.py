
def main(self):
    # self.controller.inst.write('*RST')
    # self.controller.inst.write('*WAI')
    # print(self.controller.inst.query('SYSTem:ERRor?'), end="")
    self.controller.inst.write(f'LIST:RCL 1')
    print(self.controller.inst.query('STAT:QUES:COND?'))

    self.controller.inst.write(f"LIST:SLOWrate {self.slowRate}")
    self.controller.inst.write(f"LIST:RANGe {self.range}")
    self.controller.inst.write(f"LIST:COUNt {self.count}")
    self.controller.inst.write(f"LIST:STEP {self.step}")

    for i in range(1, int(self.step) + 1):
        print(f'Step {i}: ')
        level_inc = (self.range / self.step) * i

        self.controller.inst.write(f"LIST:LEVel {i}, {level_inc:.2f}")
        print(f"LIST:LEVel {i}, {level_inc:.2f}".replace("\n", " "), end="\t")
        self.error_check()

        self.controller.inst.write(f"LIST:SLEW {i}, {self.slew}")
        print(f"LIST:SLEW {i}, {self.slew}".replace("\n", " "), end="\t")
        self.error_check()

        self.controller.inst.write(f"LIST:WIDth {i}, {self.width}")
        print(f"LIST:WIDth {i}, {self.width}".replace("\n", " "), end="\t")
        self.error_check()

        self.controller.inst.query('*OPC?')

    print("\n***DONE writing list to load")

    self.controller.inst.write(f'LIST:SAV 1')

if __name__ == "__main__":
    main()