using System.Diagnostics;
using System.Security;

namespace ProblemaTarefas_TeoriaDaComputacao
{
    public class ResolucaoTarefas
    {
        public double Tempo { get; private set; }
        public int Iteracoes { get; private set; } = 0;
        public int MakespanInicial { get; private set; }
        public int MakespanFinal { get; private set; }
        public double parametroAlpha { get; set; }

        private Maquina[] _maquinas = new Maquina[1];

        private Maquina _maquinaMakespan = new Maquina();

        public ResolucaoTarefas(int tarefas, int maquinas, double alpha = 0)
        {
            Tempo = 0;
            Iteracoes = 0;
            _maquinas = new Maquina[maquinas];
            for(int i = 0; i < maquinas; i++)
                _maquinas[i] = new Maquina();
            _maquinaMakespan = _maquinas[0];
            parametroAlpha = alpha;

            GerarTarefas(tarefas);
        }

        // Gera n tarefas de tempo aleatório na maquina inicial
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

        public void ExecutaPrimeiraEscolha()
        {
            Stopwatch sw = Stopwatch.StartNew();
            bool continuar = true;

            while (continuar)
            {
                Maquina? primeiraEscolha = RetornarPrimeiroVizinho(); //Seleciona sempre primeiro vizinho elegível encontrado

                if (primeiraEscolha != null)
                {
                    int tarefa = _maquinaMakespan.RetiraTarefa();
                    primeiraEscolha!.AdicionarTarefa(tarefa);
                    RedefineMaquinaMakespan();
                }
                else // Finaliza se não houver vizinho elegível
                {
                    continuar = false;
                    MakespanFinal = _maquinaMakespan.Makespan;
                }
                Iteracoes++;
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
                Maquina melhorEscolha = RetornarMelhorVizinho(); // Seleciona vizinho com menor makespan

                if (MaquinaElegivel(melhorEscolha))
                {
                    int tarefa = _maquinaMakespan.RetiraTarefa();
                    melhorEscolha!.AdicionarTarefa(tarefa);
                    RedefineMaquinaMakespan();
                }
                else
                {
                    continuar = false;
                    MakespanFinal = _maquinaMakespan.Makespan;
                }
                Iteracoes++;
            }
            sw.Stop();
            Tempo = sw.Elapsed.TotalMilliseconds;
        }

        public void ExecutaBuscaMonotonaRandomizada()
        {
            Stopwatch sw = Stopwatch.StartNew();
            Random rand = new Random();
            bool continuar = true;

            int nIteracoesSemMelhora = 0;

            while (continuar)
            {
                Maquina vizinho;
                if (rand.NextDouble() < parametroAlpha)
                    vizinho = RetornarVizinhoAleatorio(rand); // Vizinho aleatório
                else
                    vizinho = RetornarMelhorVizinho(); // Melhor melhora

                if (MaquinaElegivel(vizinho))
                {
                    int tarefa = _maquinaMakespan.RetiraTarefa();
                    vizinho!.AdicionarTarefa(tarefa);
                    RedefineMaquinaMakespan();
                    nIteracoesSemMelhora = 0;
                }
                else
                {
                    nIteracoesSemMelhora++;
                    if (nIteracoesSemMelhora >= 1000) // Critério de parada: 1000 iterações sem melhoria
                    {
                        continuar = false;
                        MakespanFinal = _maquinaMakespan.Makespan;
                    }
                }
                Iteracoes++;
            }
            sw.Stop();
            Tempo = sw.Elapsed.TotalMilliseconds;
        }

        private bool MaquinaElegivel(Maquina maquina) // Verifica se a máquina pode receber a tarefa do makespan sem aumentar o makespan geral
        {
            if (maquina.Makespan + _maquinaMakespan.Tarefas.Peek() < _maquinaMakespan.Makespan)
                return true;
            return false;
        }

        private void RedefineMaquinaMakespan() // Define a máquina com maior makespan
        {
            Maquina? maquinaSpan = null;
            foreach (var maquina in _maquinas)
            {
                if(maquinaSpan == null || maquina.Makespan > maquinaSpan.Makespan)
                    maquinaSpan = maquina;
            }
            _maquinaMakespan = maquinaSpan!;
        }

        private Maquina? RetornarPrimeiroVizinho() // Retorna o primeiro vizinho elegível encontrado
        {
            int i = _maquinas.IndexOf(_maquinaMakespan);
            foreach (var maquina in _maquinas)
            {
                if (MaquinaElegivel(maquina)) // Realiza a verificação de elegibilidade antecipadamente para não encerrar de forma precosse
                    return maquina;
            }
            return null;
        }

        private Maquina RetornarMelhorVizinho()
        {
            Maquina? melhorVizinho = null;
            foreach (var maquina in _maquinas)
            {
                if (maquina != _maquinaMakespan && (melhorVizinho == null || maquina.Makespan < melhorVizinho.Makespan))
                    melhorVizinho = maquina;
            }
            return melhorVizinho!; // Vizinho com menor makespan
        }

        private Maquina RetornarVizinhoAleatorio(Random rand) // Retorna aleatoriamente qualquer máquina que não seja a máquina do makespan
        {
            int indexSpan = _maquinas.IndexOf(_maquinaMakespan);

            int indexRand = rand.Next(0, _maquinas.Length - 1); // TAM - 1 para returar posição da maquina de Makespan

            if(indexRand >= indexSpan) // Incrementa caso o índice for acima da máquina do makespan
                indexRand++;

            return _maquinas[indexRand];
        }

        
    }
}
