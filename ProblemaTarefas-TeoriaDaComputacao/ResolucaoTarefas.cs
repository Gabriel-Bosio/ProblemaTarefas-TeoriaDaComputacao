using System.Diagnostics;

namespace ProblemaTarefas_TeoriaDaComputacao
{
    public class ResolucaoTarefas
    {
        public double Tempo { get; private set; }
        public int Iteracoes { get; private set; } = 0;
        public int MakespanInicial { get; private set; }
        public int MakespanFinal { get; private set; }

        private Maquina[] _maquinas = new Maquina[1];

        private Maquina _maquinaMakespan = new Maquina();

        public ResolucaoTarefas(int tarefas, int maquinas)
        {
            Tempo = 0;
            Iteracoes = 0;
            _maquinas = new Maquina[maquinas];
            for(int i = 0; i < maquinas; i++)
                _maquinas[i] = new Maquina();
            _maquinaMakespan = _maquinas[0];

            GerarTarefas(tarefas);
        }

        private void GerarTarefas(int n)
        {
            Random rand = new Random();

            for (int i = 0; i < n; i++)
            {
                int t = rand.Next(1, 100);
                _maquinas[0].AdicionarTarefa(t);
            }
            MakespanInicial = _maquinas[0].Makespan;
        } 

        public void RedefineMaquinaMakespan()
        {
            Maquina? maquinaSpan = null;
            foreach (var maquina in _maquinas)
            {
                if(maquinaSpan == null || maquina.Makespan > maquinaSpan.Makespan)
                    maquinaSpan = maquina;
            }
            _maquinaMakespan = maquinaSpan!;
        }

        public Maquina? RetornarPrimeiroVizinho()
        {
            int i = _maquinas.IndexOf(_maquinaMakespan);
            foreach (var maquina in _maquinas)
            {
                if ( maquina.Makespan + _maquinaMakespan.Tarefas.Peek() < _maquinaMakespan.Makespan)
                    return maquina;
            }
            return null;
        }

        public Maquina? RetornarMelhorVizinho()
        {
            Maquina? melhorVizinho = null;
            foreach (var maquina in _maquinas)
            {
                if (maquina.Makespan + _maquinaMakespan.Tarefas.Peek() < _maquinaMakespan.Makespan)
                    if (melhorVizinho == null || maquina.Makespan < melhorVizinho.Makespan)
                        melhorVizinho = maquina;
            }
            return melhorVizinho;
        }

        public void ExecutaPrimeiraEscolha()
        {
            Stopwatch sw = Stopwatch.StartNew();
            bool continuar = true;

            while (continuar)
            {
                Maquina? primeiraEscolha = RetornarPrimeiroVizinho();

                if (primeiraEscolha != null)
                {
                    int tarefa = _maquinaMakespan.RetiraTarefa();
                    primeiraEscolha!.AdicionarTarefa(tarefa);
                    Iteracoes++;
                    RedefineMaquinaMakespan();
                }
                else
                {
                    continuar = false;
                    MakespanFinal = _maquinaMakespan.Makespan;
                }
            }
            sw.Stop();
            Tempo = sw.Elapsed.TotalMilliseconds;
        }

        public void ExecutaMelhorEscolha()
        {
            Stopwatch sw = Stopwatch.StartNew();
            bool continuar = true;

            while (continuar)
            {
                Maquina? melhorEscolha = RetornarMelhorVizinho();

                if (melhorEscolha != null)
                {
                    int tarefa = _maquinaMakespan.RetiraTarefa();
                    melhorEscolha!.AdicionarTarefa(tarefa);
                    Iteracoes++;
                    RedefineMaquinaMakespan();
                }
                else
                {
                    continuar = false;
                    MakespanFinal = _maquinaMakespan.Makespan;
                }
            }
            sw.Stop();
            Tempo = sw.Elapsed.TotalMilliseconds;
        }
    }
}
