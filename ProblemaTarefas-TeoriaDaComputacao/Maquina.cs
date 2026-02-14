namespace ProblemaTarefas_TeoriaDaComputacao
{
    public class Maquina
    {
        public Stack<int> Tarefas { get; set; } = new Stack<int>();
        public int Makespan { get; set; } = 0;
        public Maquina()
        {
            Tarefas = new Stack<int>();
            Makespan = 0;
        }

        public void AdicionarTarefa(int t)
        {
            Tarefas.Push(t);
            Makespan += t;
        }

        public int RetiraTarefa()
        {
            int t = Tarefas.Pop();
            Makespan -= t;
            return t;
        }
    }
}
