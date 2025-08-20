# AI-Driven Circuit Generator - Master Code with Graphs
import os
import random
import matplotlib.pyplot as plt
import networkx as nx

GATE_TYPES = ["INVERTER", "NAND", "NOR", "AND", "OR", "XOR", "XNOR"]

# CMOS Gate Class
class CMOSGate:
    def __init__(self, gate_type, width_nmos, width_pmos):
        self.gate_type = gate_type.upper()
        self.width_nmos = width_nmos
        self.width_pmos = width_pmos
        self.area = width_nmos + width_pmos
        self.power = 0.5 * (width_nmos**2 + width_pmos**2) / 100
        self.delay = round((1 / (width_nmos + 0.1)) + (1 / (width_pmos + 0.1)), 4)

    def fitness_score(self):
        return 1 / (self.power * self.delay)

    def generate_netlist(self):
        if self.gate_type == "INVERTER": return self._inverter()
        elif self.gate_type == "NAND": return self._nand()
        elif self.gate_type == "NOR": return self._nor()
        elif self.gate_type == "AND": return self._and()
        elif self.gate_type == "OR": return self._or()
        elif self.gate_type == "XOR": return self._xor()
        elif self.gate_type == "XNOR": return self._xnor()
        else: return "* Unsupported gate type\n.end"

    def _inverter(self):
        return f"""* CMOS Inverter
M1 out in Vdd Vdd PMOS W={self.width_pmos}u L=0.18u
M2 out in 0 0 NMOS W={self.width_nmos}u L=0.18u
Vdd Vdd 0 DC 1.8
Vin in 0 PULSE(0 1.8 0 1n 1n 10n 20n)
Cload out 0 2f
.tran 0.1n 50n
.control
run
plot v(out)
.endc
.end
"""

    def _nand(self):
        return f"""* CMOS NAND
M1 out a Vdd Vdd PMOS W={self.width_pmos}u L=0.18u
M2 out b Vdd Vdd PMOS W={self.width_pmos}u L=0.18u
M3 out b net1 net1 NMOS W={self.width_nmos}u L=0.18u
M4 net1 a 0 0 NMOS W={self.width_nmos}u L=0.18u
Vdd Vdd 0 DC 1.8
Va a 0 PULSE(0 1.8 0 1n 1n 10n 20n)
Vb b 0 PULSE(0 1.8 10n 1n 1n 10n 20n)
Cload out 0 2f
.tran 0.1n 100n
.control
run
plot v(out)
.endc
.end
"""

    def _nor(self):
        return f"""* CMOS NOR
M1 out a Vdd Vdd PMOS W={self.width_pmos}u L=0.18u
M2 out b Vdd Vdd PMOS W={self.width_pmos}u L=0.18u
M3 out a out out NMOS W={self.width_nmos}u L=0.18u
M4 out b 0 0 NMOS W={self.width_nmos}u L=0.18u
Vdd Vdd 0 DC 1.8
Va a 0 PULSE(0 1.8 0 1n 1n 10n 20n)
Vb b 0 PULSE(0 1.8 10n 1n 1n 10n 20n)
Cload out 0 2f
.tran 0.1n 100n
.control
run
plot v(out)
.endc
.end
"""

    def _and(self):
        return self._nand() + self._inverter()

    def _or(self):
        return self._nor() + self._inverter()

    def _xor(self):
        return f"""* CMOS XOR (simplified)
.include "basic_inverter.cir"
X1 a a_inv INVERTER
X2 b b_inv INVERTER
M1 out a b_inv Vdd PMOS W={self.width_pmos}u L=0.18u
M2 out b a_inv Vdd PMOS W={self.width_pmos}u L=0.18u
M3 out a b_inv 0 NMOS W={self.width_nmos}u L=0.18u
M4 out b a_inv 0 NMOS W={self.width_nmos}u L=0.18u
.end
"""

    def _xnor(self):
        return self._xor() + self._inverter()

# Genetic Optimizer
def generate_population(gate_type, size):
    return [CMOSGate(gate_type, random.uniform(1, 5), random.uniform(1, 5)) for _ in range(size)]

def evolve(pop):
    sorted_pop = sorted(pop, key=lambda x: -x.fitness_score())
    survivors = sorted_pop[:len(pop)//2]
    children = []
    for _ in range(len(pop) - len(survivors)):
        p = random.choice(survivors)
        w_nmos = max(0.1, p.width_nmos + random.uniform(-0.2, 0.2))
        w_pmos = max(0.1, p.width_pmos + random.uniform(-0.2, 0.2))
        children.append(CMOSGate(p.gate_type, w_nmos, w_pmos))
    return survivors + children

# Visualization with image saving
def visualize_gate(gate_type):
    G = nx.DiGraph()
    gate_type = gate_type.upper()

    if gate_type == "INVERTER":
        G.add_edges_from([("Vdd", "PMOS"), ("IN", "PMOS"), ("PMOS", "OUT"),
                          ("IN", "NMOS"), ("NMOS", "GND"), ("NMOS", "OUT")])
    elif gate_type == "NAND":
        G.add_edges_from([("IN1", "PMOS1"), ("IN2", "PMOS2"),
                          ("PMOS1", "OUT"), ("PMOS2", "OUT"),
                          ("IN1", "NMOS2"), ("IN2", "NMOS1"),
                          ("NMOS1", "GND"), ("NMOS2", "NMOS1"), ("NMOS2", "OUT")])
    elif gate_type == "NOR":
        G.add_edges_from([("IN1", "PMOS1"), ("IN2", "PMOS2"),
                          ("PMOS1", "OUT"), ("PMOS2", "OUT"),
                          ("IN1", "NMOS1"), ("IN2", "NMOS2"),
                          ("NMOS1", "GND"), ("NMOS2", "GND"),
                          ("NMOS1", "OUT"), ("NMOS2", "OUT")])
    elif gate_type == "AND":
        G.add_edges_from([("A", "B"), ("B", "NAND_OUT"), ("NAND_OUT", "INV"), ("INV", "AND_OUT")])
    elif gate_type == "OR":
        G.add_edges_from([("A", "B"), ("B", "NOR_OUT"), ("NOR_OUT", "INV"), ("INV", "OR_OUT")])
    elif gate_type == "XOR":
        G.add_edges_from([("A", "NOT_A"), ("B", "NOT_B"),
                          ("NOT_A", "AND1"), ("B", "AND1"),
                          ("NOT_B", "AND2"), ("A", "AND2"),
                          ("AND1", "OR1"), ("AND2", "OR1"),
                          ("OR1", "XOR_OUT")])
    elif gate_type == "XNOR":
        G.add_edges_from([("A", "NOT_A"), ("B", "NOT_B"),
                          ("NOT_A", "AND1"), ("B", "AND1"),
                          ("NOT_B", "AND2"), ("A", "AND2"),
                          ("AND1", "OR1"), ("AND2", "OR1"),
                          ("OR1", "INV"), ("INV", "XNOR_OUT")])
    else:
        G.add_node("Not Visualized")

    pos = nx.spring_layout(G)
    plt.figure(figsize=(6, 5))
    nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=2000, font_size=10)
    plt.title(f"{gate_type} Gate Schematic", fontsize=14)

    os.makedirs("images", exist_ok=True)
    image_path = f"images/{gate_type.lower()}_gate.png"
    plt.savefig(image_path, format='png')
    print(f"✅ Visual saved at: {image_path}")
    plt.close()

# Runner
def run_generator(gate_type):
    print(f"\n🚀 Generating: {gate_type}")
    population = generate_population(gate_type, 10)

    power_list = []
    delay_list = []
    fitness_list = []

    for _ in range(10):
        population = evolve(population)
        best = max(population, key=lambda x: x.fitness_score())
        power_list.append(best.power)
        delay_list.append(best.delay)
        fitness_list.append(best.fitness_score())

    best = max(population, key=lambda x: x.fitness_score())
    print(f"✅ Optimized Specs:\n- NMOS Width: {best.width_nmos:.2f} µm\n- PMOS Width: {best.width_pmos:.2f} µm")
    print(f"- Area: {best.area:.2f}, Power: {best.power:.4f}, Delay: {best.delay:.4f}")

    os.makedirs("netlists", exist_ok=True)
    filename = f"netlists/{gate_type.lower()}_optimized.cir"
    with open(filename, "w") as f:
        f.write(best.generate_netlist())
    print(f"📁 Netlist saved as: {filename}")

    visualize_gate(gate_type)

    # Plot fitness score over generations
    os.makedirs("images", exist_ok=True)
    plt.figure()
    plt.plot(fitness_list, marker='o')
    plt.title(f"{gate_type} - Fitness Score Over Generations")
    plt.xlabel("Generation")
    plt.ylabel("Fitness Score")
    plt.grid(True)
    plt.savefig(f"images/{gate_type.lower()}_fitness_graph.png")
    plt.close()

# Main
if __name__ == "__main__":
    for gate in GATE_TYPES:
        run_generator(gate)
