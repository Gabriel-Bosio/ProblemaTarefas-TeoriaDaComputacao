namespace ProblemaTarefas_TeoriaDaComputacao
{
    public class Maquina
    {
        public Stack<int> Tarefas { get; set; } = new Stack<int>();
        public int TempoEstimado { get; set; } = 0;
        public Maquina()
        {
            Tarefas = new Stack<int>();
            TempoEstimado = 0;
        }

        public void AdicionarTarefa(int t)
        {
            Tarefas.Push(t);
            TempoEstimado += t;
        }

        public int RetiraTarefa()
        {
            int t = Tarefas.Pop();
            TempoEstimado -= t;
            return t;
        }
    }
}
