import gurobipy as gp
from gurobipy import GRB

def min_max_pli(n, jobs1, jobs2, p):
    # Creazione del modello
    model = gp.Model("Solution1")

    M = sum(p)  # Big M (valore molto grande)

    # Variabili di inizio e completamento per ogni job
    s = model.addVars(n, vtype=GRB.CONTINUOUS, name="s")  # Tempo di inizio
    c = model.addVars(n, vtype=GRB.CONTINUOUS, name="c")  # Tempo di completamento

    # Creazione delle variabili di precedenza binarie x[i,j] (x[i,j] = 1 --> job i precede job j)
    x = model.addVars([(i, j) for i in range(n) for j in range(i+1, n)],vtype=GRB.BINARY,name='x')

    # Variabile z per il tempo di completamento massimo
    z = model.addVar(vtype=GRB.CONTINUOUS, name="z")

    # Funzione obiettivo: minimizzare z
    model.setObjective(z, GRB.MINIMIZE)

    # Vincoli sul tempo di completamento
    for i in range(n):
        model.addConstr(c[i] == s[i] + p[i], f"completion_{i}")

    # Vincoli per garantire che z sia maggiore o uguale alla somma dei tempi di completamento per entrambi i giocatori
    model.addConstr(z >= gp.quicksum(c[i] for i in jobs1), "sum_giocatore1")
    model.addConstr(z >= gp.quicksum(c[i] for i in jobs2), "sum_giocatore2")

    # Vincoli di precedenza
    for i in range(n):
        for j in range(i+1, n):
            # Caso 1: i precede j (x[i,j] = 1), allora s[j] >= c[i] - M * (1-x[i,j])
            model.addConstr(s[j] >= c[i] - M * ( 1 - x[i, j]), f"precedenza_{i}_su_{j}")
            # Caso 2: j precede i (x[i,j] = 0), allora s[i] >= c[j] - M * x[i,j]
            model.addConstr(s[i] >= c[j] - M * x[i, j], f"precedenza_{j}_su_{i}")

    # Ottimizzazione del modello
    model.optimize()

    # Stampa dei risultati
    if model.status == GRB.OPTIMAL:
        print("Soluzione ottima trovata:")
        print(f"Valore di z: {z.x}")
        for i in range(n):
            print(f"Job {i}: inizio = {s[i].x}, completamento = {c[i].x}")
        for i in range(n):
            for j in range(i+1, n):
                    print(f"x_{i}_{j} = {x[i, j].x}")

        scheduling = sorted(range(n), key=lambda i: s[i].x)
        print("\nScheduling trovato:")
        for idx, job in enumerate(scheduling):
            print(f"Posizione {idx+1}: Job {job}")
    else:
        print("Non è stata trovata una soluzione ottima.")

min_max_pli(14, [0,1,2,3,4,5,6], [7,8,9,10,11,12,13], [3, 2, 4, 19, 5,23,6,7,12,6,4,7,2,8])